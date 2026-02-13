from __future__ import annotations

import argparse
import json
from pathlib import Path

from skyjo_optimizer.ml import EvolutionConfig, run_experiment, summarize_reports, write_summary_csv
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

    report_summary = subparsers.add_parser(
        "report-summary",
        help="consolidate artifacts/*/report.json files into a CSV summary",
    )
    report_summary.add_argument("--artifacts-root", type=Path, default=Path("artifacts"))
    report_summary.add_argument("--output", type=Path, default=Path("artifacts/summary.csv"))

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

    if args.command == "report-summary":
        rows = summarize_reports(args.artifacts_root)
        output = write_summary_csv(rows, args.output)
        print(output)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
