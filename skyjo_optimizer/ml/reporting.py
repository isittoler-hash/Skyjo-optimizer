from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReportSummaryRow:
    run_timestamp_utc: str
    seed: int
    aggregate_fitness: float
    holdout_score: float | None
    aggregate_fitness_delta_vs_benchmark: float
    benchmark_mean_delta_vs_random_a: float | None
    benchmark_mean_delta_vs_random_b: float | None
    benchmark_win_rate_delta_vs_random_a: float | None
    benchmark_win_rate_delta_vs_random_b: float | None

    def to_dict(self) -> dict[str, str | int | float]:
        row: dict[str, str | int | float] = {
            "run_timestamp_utc": self.run_timestamp_utc,
            "seed": self.seed,
            "aggregate_fitness": self.aggregate_fitness,
            "holdout_score": "" if self.holdout_score is None else self.holdout_score,
            "aggregate_fitness_delta_vs_benchmark": self.aggregate_fitness_delta_vs_benchmark,
            "benchmark_mean_delta_vs_random_a": ""
            if self.benchmark_mean_delta_vs_random_a is None
            else self.benchmark_mean_delta_vs_random_a,
            "benchmark_mean_delta_vs_random_b": ""
            if self.benchmark_mean_delta_vs_random_b is None
            else self.benchmark_mean_delta_vs_random_b,
            "benchmark_win_rate_delta_vs_random_a": ""
            if self.benchmark_win_rate_delta_vs_random_a is None
            else self.benchmark_win_rate_delta_vs_random_a,
            "benchmark_win_rate_delta_vs_random_b": ""
            if self.benchmark_win_rate_delta_vs_random_b is None
            else self.benchmark_win_rate_delta_vs_random_b,
        }
        return row


def summarize_reports(artifacts_root: str | Path) -> list[ReportSummaryRow]:
    rows: list[ReportSummaryRow] = []
    for report_path in sorted(Path(artifacts_root).glob("*/report.json")):
        payload = json.loads(report_path.read_text())
        metadata = payload["metadata"]
        optimized = payload["optimized"]
        benchmark = payload["benchmark"]
        tournament = payload.get("tournament_benchmark", {})
        means = tournament.get("mean_score_by_agent", {})
        win_rates = tournament.get("win_rate_by_agent", {})

        heuristic_mean = _agent_metric(means, "heuristic")
        heuristic_win_rate = _agent_metric(win_rates, "heuristic")

        rows.append(
            ReportSummaryRow(
                run_timestamp_utc=metadata["run_timestamp_utc"],
                seed=int(metadata["seed"]),
                aggregate_fitness=float(optimized["aggregate_fitness"]),
                holdout_score=None if payload.get("holdout_score") is None else float(payload["holdout_score"]),
                aggregate_fitness_delta_vs_benchmark=float(optimized["aggregate_fitness"])
                - float(benchmark["aggregate_fitness"]),
                benchmark_mean_delta_vs_random_a=None
                if heuristic_mean is None
                else _delta(heuristic_mean, _agent_metric(means, "random_a")),
                benchmark_mean_delta_vs_random_b=None
                if heuristic_mean is None
                else _delta(heuristic_mean, _agent_metric(means, "random_b")),
                benchmark_win_rate_delta_vs_random_a=None
                if heuristic_win_rate is None
                else _delta(heuristic_win_rate, _agent_metric(win_rates, "random_a")),
                benchmark_win_rate_delta_vs_random_b=None
                if heuristic_win_rate is None
                else _delta(heuristic_win_rate, _agent_metric(win_rates, "random_b")),
            )
        )

    return sorted(rows, key=lambda row: row.run_timestamp_utc)


def write_summary_csv(rows: list[ReportSummaryRow], destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(ReportSummaryRow.__annotations__.keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row.to_dict() for row in rows)

    return path


def _agent_metric(values: dict[str, object], agent_name: str) -> float | None:
    value = values.get(agent_name)
    return float(value) if value is not None else None


def _delta(left: float, right: float | None) -> float | None:
    if right is None:
        return None
    return left - right
