from __future__ import annotations

import json
from pathlib import Path
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


def test_cli_pipeline_command_writes_manifest_and_artifacts(tmp_path) -> None:
    output = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "skyjo_optimizer.cli",
            "pipeline",
            "--population-size",
            "6",
            "--generations",
            "2",
            "--elite-count",
            "2",
            "--rounds-per-eval",
            "8",
            "--baseline-rounds",
            "4",
            "--holdout-rounds",
            "5",
            "--seed",
            "9",
            "--output-root",
            str(tmp_path),
        ],
        text=True,
    ).strip()

    run_dir = Path(output)
    assert run_dir.exists()
    assert (run_dir / "report.json").exists()
    assert (run_dir / "tournament_summary.csv").exists()
    assert (run_dir / "baseline.json").exists()
    assert (run_dir / "holdout_score.json").exists()
    assert (run_dir / "verify.json").exists()
    assert (run_dir / "manifest.json").exists()

    verify_payload = json.loads((run_dir / "verify.json").read_text())
    assert verify_payload["ok"] is True

    manifest_payload = json.loads((run_dir / "manifest.json").read_text())
    assert manifest_payload["git_hash"]
    assert manifest_payload["hostname"]
    assert manifest_payload["python_version"]
    assert manifest_payload["command_args"]
    assert manifest_payload["artifacts"]["report_json"]
