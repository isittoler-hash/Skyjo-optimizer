from __future__ import annotations

import csv

from skyjo_optimizer.ml.evolution import EvolutionConfig
from skyjo_optimizer.ml.experiment import run_experiment
from skyjo_optimizer.ml.reporting import summarize_reports, write_summary_csv


def test_reporting_summary_and_csv(tmp_path) -> None:
    report = run_experiment(
        config=EvolutionConfig(population_size=6, generations=2, elite_count=2, rounds_per_eval=10, seed=23)
    )
    report.write_artifacts(tmp_path)

    rows = summarize_reports(tmp_path)
    assert len(rows) == 1
    assert rows[0]["seed"] == 23

    output = write_summary_csv(rows, tmp_path / "summary.csv")
    with output.open() as handle:
        parsed = list(csv.DictReader(handle))

    assert len(parsed) == 1
    assert parsed[0]["seed"] == "23"
    assert parsed[0]["run_dir"]
