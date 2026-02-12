from __future__ import annotations

import json
import subprocess
import sys

from skyjo_optimizer.ml.evolution import EvolutionConfig
from skyjo_optimizer.ml.experiment import run_experiment
from skyjo_optimizer.simulation.scenarios import DEFAULT_SITUATIONS


def test_experiment_writes_structured_artifacts(tmp_path) -> None:
    report = run_experiment(
        situations=DEFAULT_SITUATIONS[:1],
        config=EvolutionConfig(population_size=6, generations=2, elite_count=2, rounds_per_eval=10, seed=3),
    )

    run_dir = report.write_artifacts(tmp_path)
    assert (run_dir / "report.json").exists()
    assert (run_dir / "tournament_summary.csv").exists()

    payload = json.loads((run_dir / "report.json").read_text())
    assert payload["metadata"]["seed_bank_id"]
    assert payload["metadata"]["run_timestamp_utc"]


def test_cli_baseline_command_writes_json(tmp_path) -> None:
    output = tmp_path / "baseline.json"
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "skyjo_optimizer.cli",
            "baseline",
            "--rounds",
            "6",
            "--seed",
            "4",
            "--output",
            str(output),
        ]
    )

    payload = json.loads(output.read_text())
    assert payload["rounds"] == 6
    assert payload["seed"] == 4
    assert "heuristic" in payload["mean_score_by_agent"]
