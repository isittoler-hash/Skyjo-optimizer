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


def test_cli_baseline_config_parsing_and_cli_override(tmp_path) -> None:
    output = tmp_path / "baseline_config.json"
    config = tmp_path / "baseline.toml"
    config.write_text(
        f"""
rounds = 8
seed = 13
output = "{output}"
""".strip()
        + "\n"
    )

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "skyjo_optimizer.cli",
            "baseline",
            "--config",
            str(config),
            "--seed",
            "99",
        ]
    )

    payload = json.loads(output.read_text())
    assert payload["rounds"] == 8
    assert payload["seed"] == 99
    assert payload["resolved_config"]["rounds"] == 8
    assert payload["resolved_config"]["seed"] == 99


def test_cli_optimize_config_parsing_and_resolved_config_persisted(tmp_path) -> None:
    config = tmp_path / "optimize.toml"
    config.write_text(
        f"""
population_size = 6
generations = 2
elite_count = 2
rounds_per_eval = 8
seed = 17
output_root = "{tmp_path}"
""".strip()
        + "\n"
    )

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "skyjo_optimizer.cli",
            "optimize",
            "--config",
            str(config),
            "--generations",
            "3",
        ]
    )

    run_dirs = [path for path in tmp_path.iterdir() if path.is_dir()]
    assert run_dirs

    payload = json.loads((run_dirs[0] / "report.json").read_text())
    assert payload["metadata"]["resolved_config"]["population_size"] == 6
    assert payload["metadata"]["resolved_config"]["generations"] == 3
    assert payload["metadata"]["resolved_config"]["output_root"] == str(tmp_path)
