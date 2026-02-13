from __future__ import annotations

import csv
import json

from skyjo_optimizer.ml.reporting import summarize_reports, write_summary_csv


def test_summarize_reports_collects_and_computes_deltas(tmp_path) -> None:
    run_dir = tmp_path / "20250101_run"
    run_dir.mkdir(parents=True)
    payload = {
        "metadata": {
            "run_timestamp_utc": "2025-01-01T00:00:00+00:00",
            "seed": 11,
        },
        "optimized": {"aggregate_fitness": 12.5},
        "benchmark": {"aggregate_fitness": 10.0},
        "holdout_score": 8.75,
        "tournament_benchmark": {
            "mean_score_by_agent": {"heuristic": 41.0, "random_a": 46.0, "random_b": 50.0},
            "win_rate_by_agent": {"heuristic": 0.7, "random_a": 0.2, "random_b": 0.1},
        },
    }
    (run_dir / "report.json").write_text(json.dumps(payload))

    rows = summarize_reports(tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row.seed == 11
    assert row.aggregate_fitness_delta_vs_benchmark == 2.5
    assert row.benchmark_mean_delta_vs_random_a == -5.0
    assert row.benchmark_win_rate_delta_vs_random_b == 0.6


def test_write_summary_csv_writes_expected_columns(tmp_path) -> None:
    run_dir = tmp_path / "20250101_run"
    run_dir.mkdir(parents=True)
    payload = {
        "metadata": {
            "run_timestamp_utc": "2025-01-01T00:00:00+00:00",
            "seed": 3,
        },
        "optimized": {"aggregate_fitness": 2.0},
        "benchmark": {"aggregate_fitness": 1.0},
        "holdout_score": None,
        "tournament_benchmark": {
            "mean_score_by_agent": {"heuristic": 10.0, "random_a": 11.0, "random_b": 12.0},
            "win_rate_by_agent": {"heuristic": 0.5, "random_a": 0.3, "random_b": 0.2},
        },
    }
    (run_dir / "report.json").write_text(json.dumps(payload))

    output = write_summary_csv(summarize_reports(tmp_path), tmp_path / "summary.csv")

    with output.open() as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames
        row = next(reader)

    assert headers is not None
    assert "seed" in headers
    assert "aggregate_fitness" in headers
    assert "holdout_score" in headers
    assert "benchmark_mean_delta_vs_random_a" in headers
    assert row["holdout_score"] == ""
