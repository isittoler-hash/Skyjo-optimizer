from __future__ import annotations

import argparse
import json
import platform
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from skyjo_optimizer.ml import EvolutionConfig, run_experiment
from skyjo_optimizer.simulation.evaluator import evaluate_strategy
from skyjo_optimizer.simulation.scenarios import DEFAULT_SITUATIONS
from skyjo_optimizer.simulation import RandomAgent, SimpleHeuristicAgent, run_tournament


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skyjo optimizer command line tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    baseline = subparsers.add_parser("baseline", help="run baseline tournament")
    baseline.add_argument("--rounds", type=int, default=24)
    baseline.add_argument("--seed", type=int, default=7)
    baseline.add_argument("--output", type=Path, default=None)

    optimize = subparsers.add_parser("optimize", help="run evolutionary optimization experiment")
    optimize.add_argument("--population-size", type=int, default=24)
    optimize.add_argument("--generations", type=int, default=20)
    optimize.add_argument("--elite-count", type=int, default=6)
    optimize.add_argument("--rounds-per-eval", type=int, default=120)
    optimize.add_argument("--seed", type=int, default=7)
    optimize.add_argument("--output-root", type=Path, default=Path("artifacts"))

    pipeline = subparsers.add_parser("pipeline", help="run baseline, optimization, holdout scoring, and verification")
    pipeline.add_argument("--population-size", type=int, default=24)
    pipeline.add_argument("--generations", type=int, default=20)
    pipeline.add_argument("--elite-count", type=int, default=6)
    pipeline.add_argument("--rounds-per-eval", type=int, default=120)
    pipeline.add_argument("--baseline-rounds", type=int, default=24)
    pipeline.add_argument("--holdout-rounds", type=int, default=120)
    pipeline.add_argument("--seed", type=int, default=7)
    pipeline.add_argument("--output-root", type=Path, default=Path("artifacts"))

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "baseline":
        result = run_tournament(
            [SimpleHeuristicAgent("heuristic"), RandomAgent("random_a"), RandomAgent("random_b")],
            rounds=args.rounds,
            seed=args.seed,
        )
        payload = {
            "rounds": args.rounds,
            "seed": args.seed,
            "mean_score_by_agent": result.mean_score_by_agent,
            "median_score_by_agent": result.median_score_by_agent,
            "tail95_score_by_agent": result.tail95_score_by_agent,
            "win_rate_by_agent": result.win_rate_by_agent,
            "win_rate_matrix": result.win_rate_matrix,
        }
        output = json.dumps(payload, indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n")
        else:
            print(output)
        return 0

    if args.command == "optimize":
        config = EvolutionConfig(
            population_size=args.population_size,
            generations=args.generations,
            elite_count=args.elite_count,
            rounds_per_eval=args.rounds_per_eval,
            seed=args.seed,
        )
        report = run_experiment(config=config)
        path = report.write_artifacts(args.output_root)
        print(path)
        return 0

    if args.command == "pipeline":
        baseline_result = run_tournament(
            [SimpleHeuristicAgent("heuristic"), RandomAgent("random_a"), RandomAgent("random_b")],
            rounds=args.baseline_rounds,
            seed=args.seed,
        )
        baseline_payload = {
            "rounds": args.baseline_rounds,
            "seed": args.seed,
            "mean_score_by_agent": baseline_result.mean_score_by_agent,
            "median_score_by_agent": baseline_result.median_score_by_agent,
            "tail95_score_by_agent": baseline_result.tail95_score_by_agent,
            "win_rate_by_agent": baseline_result.win_rate_by_agent,
            "win_rate_matrix": baseline_result.win_rate_matrix,
        }

        holdout_situation = DEFAULT_SITUATIONS[-1]
        training_situations = [s for s in DEFAULT_SITUATIONS if s.name != holdout_situation.name]

        config = EvolutionConfig(
            population_size=args.population_size,
            generations=args.generations,
            elite_count=args.elite_count,
            rounds_per_eval=args.rounds_per_eval,
            seed=args.seed,
        )
        report = run_experiment(
            situations=training_situations,
            config=config,
            holdout_situation=holdout_situation,
            tournament_rounds=args.baseline_rounds,
        )
        run_dir = report.write_artifacts(args.output_root)

        holdout_result = evaluate_strategy(
            report.optimized.strategy,
            holdout_situation,
            rounds=args.holdout_rounds,
            seed=args.seed + 30_000,
        )
        holdout_payload = {
            "scenario": holdout_situation.name,
            "rounds": args.holdout_rounds,
            "seed": args.seed + 30_000,
            "fitness": holdout_result.fitness,
            "mean_score": holdout_result.mean_score,
        }

        baseline_path = run_dir / "baseline.json"
        baseline_path.write_text(json.dumps(baseline_payload, indent=2, sort_keys=True) + "\n")
        holdout_path = run_dir / "holdout_score.json"
        holdout_path.write_text(json.dumps(holdout_payload, indent=2, sort_keys=True) + "\n")

        verify_payload = _verify_pipeline_artifacts(run_dir)
        verify_path = run_dir / "verify.json"
        verify_path.write_text(json.dumps(verify_payload, indent=2, sort_keys=True) + "\n")

        manifest_payload = {
            "git_hash": _current_commit_hash(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version(),
            "timestamp_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "command_args": sys.argv,
            "artifacts": {
                "run_dir": str(run_dir),
                "report_json": str(run_dir / "report.json"),
                "tournament_summary_csv": str(run_dir / "tournament_summary.csv"),
                "baseline_json": str(baseline_path),
                "holdout_score_json": str(holdout_path),
                "verify_json": str(verify_path),
            },
        }
        manifest_path = run_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n")

        print(run_dir)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


def _current_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _verify_pipeline_artifacts(run_dir: Path) -> dict[str, object]:
    required = [
        run_dir / "report.json",
        run_dir / "tournament_summary.csv",
        run_dir / "baseline.json",
        run_dir / "holdout_score.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    return {
        "ok": not missing,
        "checked_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "missing": missing,
    }


if __name__ == "__main__":
    raise SystemExit(main())
