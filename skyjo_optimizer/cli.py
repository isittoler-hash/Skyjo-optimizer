from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib

from skyjo_optimizer.ml import EvolutionConfig, run_experiment
from skyjo_optimizer.simulation import RandomAgent, SimpleHeuristicAgent, run_tournament


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
    if key in {"output", "output_root"} and value is not None:
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

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
