from __future__ import annotations

import json

from skyjo_optimizer.ml.evolution import EvolutionConfig
from skyjo_optimizer.ml.experiment import run_experiment
from skyjo_optimizer.simulation.scenarios import DEFAULT_SITUATIONS, GameSituation


def test_run_experiment_returns_expected_shapes() -> None:
    report = run_experiment(
        situations=DEFAULT_SITUATIONS[:2],
        config=EvolutionConfig(
            population_size=10,
            generations=4,
            elite_count=3,
            rounds_per_eval=25,
            seed=17,
        ),
    )

    assert len(report.optimized.scenario_scores) == 2
    assert len(report.benchmark.scenario_scores) == 2
    assert report.metadata.seed == 17
    assert len(report.metadata.ruleset_config_hash) == 64


def test_run_experiment_holdout_and_serialization(tmp_path) -> None:
    holdout = GameSituation(
        name="holdout",
        volatility=0.7,
        deck_richness=0.3,
        opponent_aggression=0.8,
        endgame_pressure=0.6,
    )
    report = run_experiment(
        situations=DEFAULT_SITUATIONS[:1],
        holdout_situation=holdout,
        config=EvolutionConfig(population_size=8, generations=3, elite_count=2, rounds_per_eval=20, seed=5),
    )

    output = report.write_json(tmp_path / "report.json")
    payload = json.loads(output.read_text())

    assert report.holdout_score is not None
    assert payload["metadata"]["ruleset_config_hash"] == report.metadata.ruleset_config_hash
    assert payload["optimized"]["scenario_scores"]
