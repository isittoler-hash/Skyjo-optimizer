from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from dataclasses import asdict, dataclass
from pathlib import Path

from skyjo_optimizer.simulation import RandomAgent, SimpleHeuristicAgent, run_tournament
from skyjo_optimizer.agents.heuristic import HeuristicStrategy
from skyjo_optimizer.ml.evolution import EvolutionConfig, EvolutionOptimizer, StrategyPerformance
from skyjo_optimizer.simulation.evaluator import EvaluationResult, evaluate_strategy
from skyjo_optimizer.simulation.scenarios import DEFAULT_SITUATIONS, GameSituation


@dataclass(frozen=True)
class ExperimentMetadata:
    git_commit_hash: str
    ruleset_config_hash: str
    run_timestamp_utc: str
    seed_bank_id: str
    optimizer_config: EvolutionConfig
    seed: int


@dataclass(frozen=True)
class ExperimentReport:
    metadata: ExperimentMetadata
    optimized: StrategyPerformance
    benchmark: StrategyPerformance
    tournament_benchmark: dict[str, object]
    holdout_score: float | None

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["metadata"]["optimizer_config"] = asdict(self.metadata.optimizer_config)
        return data

    def write_json(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n")
        return destination

    def write_artifacts(self, root: str | Path = "artifacts") -> Path:
        run_id = f"{self.metadata.run_timestamp_utc.replace(':', '').replace('-', '')}_{self.metadata.git_commit_hash[:7]}"
        run_dir = Path(root) / run_id
        self.write_json(run_dir / "report.json")
        _write_tournament_csv(self.tournament_benchmark, run_dir / "tournament_summary.csv")
        return run_dir


def run_experiment(
    situations: list[GameSituation] | None = None,
    *,
    config: EvolutionConfig | None = None,
    holdout_situation: GameSituation | None = None,
    benchmark_strategy: HeuristicStrategy | None = None,
    tournament_rounds: int = 24,
) -> ExperimentReport:
    scenarios = situations or DEFAULT_SITUATIONS
    optimizer = EvolutionOptimizer(config)
    optimized = optimizer.optimize(scenarios)

    benchmark = benchmark_strategy or HeuristicStrategy(0.5, 0.5, 0.5, 0.5)
    benchmark_perf = _score_static_strategy(
        benchmark,
        scenarios,
        rounds=optimizer.config.rounds_per_eval,
        seed=optimizer.config.seed,
    )
    tournament_benchmark = _run_baseline_tournament_benchmark(
        seed=optimizer.config.seed,
        rounds=tournament_rounds,
    )

    holdout_score = None
    if holdout_situation is not None:
        result = evaluate_strategy(
            optimized.strategy,
            holdout_situation,
            rounds=optimizer.config.rounds_per_eval,
            seed=optimizer.config.seed + 10_000,
        )
        holdout_score = result.fitness

    metadata = ExperimentMetadata(
        git_commit_hash=_current_commit_hash(),
        ruleset_config_hash=_ruleset_hash(scenarios),
        run_timestamp_utc=datetime.now(UTC).isoformat(timespec="seconds"),
        seed_bank_id=_seed_bank_id(optimizer.config.seed),
        optimizer_config=optimizer.config,
        seed=optimizer.config.seed,
    )

    return ExperimentReport(
        metadata=metadata,
        optimized=optimized,
        benchmark=benchmark_perf,
        tournament_benchmark=tournament_benchmark,
        holdout_score=holdout_score,
    )


def _run_baseline_tournament_benchmark(*, seed: int, rounds: int) -> dict[str, object]:
    result = run_tournament(
        [
            SimpleHeuristicAgent("heuristic"),
            RandomAgent("random_a"),
            RandomAgent("random_b"),
        ],
        rounds=rounds,
        seed=seed + 20_000,
    )

    return {
        "rounds": rounds,
        "seed": seed + 20_000,
        "mean_score_by_agent": result.mean_score_by_agent,
        "median_score_by_agent": result.median_score_by_agent,
        "tail95_score_by_agent": result.tail95_score_by_agent,
        "win_rate_by_agent": result.win_rate_by_agent,
        "win_rate_matrix": result.win_rate_matrix,
    }


def _score_static_strategy(
    strategy: HeuristicStrategy,
    situations: list[GameSituation],
    rounds: int,
    seed: int,
) -> StrategyPerformance:
    scores: dict[str, float] = {}
    total = 0.0

    for index, scenario in enumerate(situations):
        result: EvaluationResult = evaluate_strategy(
            strategy,
            scenario,
            rounds=rounds,
            seed=seed + index * 37,
        )
        scores[scenario.name] = result.fitness
        total += result.fitness

    return StrategyPerformance(
        strategy=strategy,
        scenario_scores=scores,
        aggregate_fitness=total / len(situations),
    )


def _ruleset_hash(situations: list[GameSituation]) -> str:
    payload = [asdict(s) for s in sorted(situations, key=lambda item: item.name)]
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _current_commit_hash() -> str:
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return output
    except Exception:
        return "unknown"


def _seed_bank_id(seed: int) -> str:
    payload = f"seed-bank::{seed}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def _write_tournament_csv(tournament: dict[str, object], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    means: dict[str, float] = tournament["mean_score_by_agent"]  # type: ignore[assignment]
    medians: dict[str, float] = tournament["median_score_by_agent"]  # type: ignore[assignment]
    tails: dict[str, float] = tournament["tail95_score_by_agent"]  # type: ignore[assignment]
    wins: dict[str, float] = tournament["win_rate_by_agent"]  # type: ignore[assignment]

    rows = ["agent,mean_score,median_score,tail95_score,win_rate"]
    for agent_name in sorted(means):
        rows.append(
            f"{agent_name},{means[agent_name]:.6f},{medians[agent_name]:.6f},{tails[agent_name]:.6f},{wins[agent_name]:.6f}"
        )
    destination.write_text("\n".join(rows) + "\n")
