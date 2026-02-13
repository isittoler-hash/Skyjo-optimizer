from __future__ import annotations

import argparse
import json
from pathlib import Path

from skyjo_optimizer.ml import EvolutionConfig, run_experiment
from skyjo_optimizer.simulation import RandomAgent, SimpleHeuristicAgent, run_regression_checks, run_tournament


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

    verify = subparsers.add_parser("verify", help="run deterministic replay and benchmark regression checks")
    verify.add_argument("--rounds", type=int, default=60)
    verify.add_argument("--seed", type=int, default=11)

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

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
