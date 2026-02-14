from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tomllib

from skyjo_optimizer.ml import EvolutionConfig, run_experiment, summarize_reports, write_summary_csv
from skyjo_optimizer.simulation import RandomAgent, SimpleHeuristicAgent, run_regression_checks, run_tournament
from skyjo_optimizer.simulation.scenarios import DEFAULT_SITUATIONS


BASELINE_DEFAULTS: dict[str, object] = {
    "rounds": 24,
    "seed": 7,
    "output": None,
}

OPTIMIZE_DEFAULTS: dict[str, object] = {
    "population_size": 24,
    "generations": 20,
    "elite_count": 6,
    "rounds_per_eval": 120,
    "seed": 7,
    "output_root": Path("artifacts"),
}


PIPELINE_DEFAULTS: dict[str, object] = {
    "rounds": 24,
    "seed": 7,
    "population_size": 24,
    "generations": 20,
    "elite_count": 6,
    "rounds_per_eval": 120,
    "output_root": Path("artifacts"),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skyjo optimizer command line tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    baseline = subparsers.add_parser("baseline", help="run baseline tournament")
    baseline.add_argument("--config", type=Path, default=None)
    baseline.add_argument("--rounds", type=int, default=None)
    baseline.add_argument("--seed", type=int, default=None)
    baseline.add_argument("--output", type=Path, default=None)

    optimize = subparsers.add_parser("optimize", help="run evolutionary optimization experiment")
    optimize.add_argument("--config", type=Path, default=None)
    optimize.add_argument("--population-size", type=int, default=None)
    optimize.add_argument("--generations", type=int, default=None)
    optimize.add_argument("--elite-count", type=int, default=None)
    optimize.add_argument("--rounds-per-eval", type=int, default=None)
    optimize.add_argument("--seed", type=int, default=None)
    optimize.add_argument("--output-root", type=Path, default=None)

    verify = subparsers.add_parser("verify", help="run deterministic replay and benchmark regression checks")
    verify.add_argument("--rounds", type=int, default=60)
    verify.add_argument("--seed", type=int, default=11)

    pipeline = subparsers.add_parser("pipeline", help="run testable end-to-end pipeline and write a manifest")
    pipeline.add_argument("--config", type=Path, default=None)
    pipeline.add_argument("--rounds", type=int, default=None)
    pipeline.add_argument("--seed", type=int, default=None)
    pipeline.add_argument("--population-size", type=int, default=None)
    pipeline.add_argument("--generations", type=int, default=None)
    pipeline.add_argument("--elite-count", type=int, default=None)
    pipeline.add_argument("--rounds-per-eval", type=int, default=None)
    pipeline.add_argument("--output-root", type=Path, default=None)

    report_summary = subparsers.add_parser("report-summary", help="summarize artifacts/*/report.json into a CSV")
    report_summary.add_argument("--artifacts-root", type=Path, default=Path("artifacts"))
    report_summary.add_argument("--output", type=Path, required=True)

    return parser


def _resolve_command_config(args: argparse.Namespace, defaults: dict[str, object]) -> dict[str, object]:
    file_values = _load_config_for_command(args.config, args.command)
    resolved: dict[str, object] = {}
    for key, default in defaults.items():
        cli_value = getattr(args, key)
        raw_value = cli_value if cli_value is not None else file_values.get(key, default)
        resolved[key] = _coerce_value(key, raw_value)
    return resolved


def _load_config_for_command(path: Path | None, command: str) -> dict[str, object]:
    if path is None:
        return {}

    payload = tomllib.loads(path.read_text())
    section = payload.get(command)
    if isinstance(section, dict):
        return section
    return payload


def _coerce_value(key: str, value: object) -> object:
    if key in {"output", "output_root", "artifacts_root"} and value is not None:
        return Path(value)
    return value


def _serialize_resolved_config(config: dict[str, object]) -> dict[str, object]:
    serialized: dict[str, object] = {}
    for key, value in config.items():
        if isinstance(value, Path):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized


def _current_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _verify_pipeline_artifacts(root: Path, run_dir: Path) -> dict[str, bool]:
    checks = {
        "baseline": (root / "baseline.json").exists(),
        "verify": (root / "verify.json").exists(),
        "holdout_score": (root / "holdout_score.json").exists(),
        "manifest": (root / "manifest.json").exists(),
        "report": (run_dir / "report.json").exists(),
        "tournament_summary": (run_dir / "tournament_summary.csv").exists(),
    }
    return checks


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "baseline":
        resolved = _resolve_command_config(args, BASELINE_DEFAULTS)
        rounds = int(resolved["rounds"])
        seed = int(resolved["seed"])
        output_path = resolved["output"]

        result = run_tournament(
            [SimpleHeuristicAgent("heuristic"), RandomAgent("random_a"), RandomAgent("random_b")],
            rounds=rounds,
            seed=seed,
        )
        payload = {
            "rounds": rounds,
            "seed": seed,
            "mean_score_by_agent": result.mean_score_by_agent,
            "median_score_by_agent": result.median_score_by_agent,
            "tail95_score_by_agent": result.tail95_score_by_agent,
            "win_rate_by_agent": result.win_rate_by_agent,
            "win_rate_matrix": result.win_rate_matrix,
            "resolved_config": _serialize_resolved_config(resolved),
        }
        output = json.dumps(payload, indent=2, sort_keys=True)
        if isinstance(output_path, Path):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output + "\n")
        else:
            print(output)
        return 0

    if args.command == "verify":
        result = run_regression_checks(rounds=args.rounds, seed=args.seed)
        payload = {
            "rounds": args.rounds,
            "seed": args.seed,
            "deterministic_replay_ok": result.deterministic_replay_ok,
            "heuristic_beats_random": result.heuristic_beats_random,
            "heuristic_mean_score": result.heuristic_mean_score,
            "random_mean_score": result.random_mean_score,
            "heuristic_win_rate": result.heuristic_win_rate,
            "random_win_rate": result.random_win_rate,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if result.deterministic_replay_ok and result.heuristic_beats_random else 1

    if args.command == "optimize":
        resolved = _resolve_command_config(args, OPTIMIZE_DEFAULTS)
        config = EvolutionConfig(
            population_size=int(resolved["population_size"]),
            generations=int(resolved["generations"]),
            elite_count=int(resolved["elite_count"]),
            rounds_per_eval=int(resolved["rounds_per_eval"]),
            seed=int(resolved["seed"]),
        )
        report = run_experiment(config=config, resolved_config=_serialize_resolved_config(resolved))
        output_root = resolved["output_root"]
        path = report.write_artifacts(output_root if isinstance(output_root, Path) else Path("artifacts"))
        print(path)
        return 0

    if args.command == "pipeline":
        resolved = _resolve_command_config(args, PIPELINE_DEFAULTS)
        output_root = resolved["output_root"]
        root = output_root if isinstance(output_root, Path) else Path("artifacts")
        root.mkdir(parents=True, exist_ok=True)

        baseline_payload = {
            "rounds": int(resolved["rounds"]),
            "seed": int(resolved["seed"]),
        }
        baseline_result = run_tournament(
            [SimpleHeuristicAgent("heuristic"), RandomAgent("random_a"), RandomAgent("random_b")],
            rounds=baseline_payload["rounds"],
            seed=baseline_payload["seed"],
        )
        baseline_payload.update(
            {
                "mean_score_by_agent": baseline_result.mean_score_by_agent,
                "median_score_by_agent": baseline_result.median_score_by_agent,
                "tail95_score_by_agent": baseline_result.tail95_score_by_agent,
                "win_rate_by_agent": baseline_result.win_rate_by_agent,
                "win_rate_matrix": baseline_result.win_rate_matrix,
            }
        )
        (root / "baseline.json").write_text(json.dumps(baseline_payload, indent=2, sort_keys=True) + "\n")

        config = EvolutionConfig(
            population_size=int(resolved["population_size"]),
            generations=int(resolved["generations"]),
            elite_count=int(resolved["elite_count"]),
            rounds_per_eval=int(resolved["rounds_per_eval"]),
            seed=int(resolved["seed"]),
        )
        train_situations = DEFAULT_SITUATIONS[:-1] if len(DEFAULT_SITUATIONS) > 1 else DEFAULT_SITUATIONS
        holdout = DEFAULT_SITUATIONS[-1]
        report = run_experiment(
            situations=train_situations,
            holdout_situation=holdout,
            config=config,
            resolved_config=_serialize_resolved_config(resolved),
        )
        run_dir = report.write_artifacts(root)
        (root / "holdout_score.json").write_text(json.dumps({"holdout_score": report.holdout_score}, indent=2) + "\n")

        verify = run_regression_checks(rounds=int(resolved["rounds"]), seed=int(resolved["seed"]))
        verify_payload = {
            "rounds": int(resolved["rounds"]),
            "seed": int(resolved["seed"]),
            "deterministic_replay_ok": verify.deterministic_replay_ok,
            "heuristic_beats_random": verify.heuristic_beats_random,
            "heuristic_mean_score": verify.heuristic_mean_score,
            "random_mean_score": verify.random_mean_score,
        }
        (root / "verify.json").write_text(json.dumps(verify_payload, indent=2, sort_keys=True) + "\n")

        manifest = {
            "git_commit_hash": _current_commit_hash(),
            "resolved_config": _serialize_resolved_config(resolved),
            "run_dir": str(run_dir),
            "artifacts": _verify_pipeline_artifacts(root, run_dir),
        }
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(root / "manifest.json")
        return 0

    if args.command == "report-summary":
        rows = summarize_reports(args.artifacts_root)
        destination = write_summary_csv(rows, args.output)
        print(destination)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
