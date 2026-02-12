from skyjo_optimizer.agents.heuristic import HeuristicStrategy
from skyjo_optimizer.ml.evolution import EvolutionConfig, EvolutionOptimizer
from skyjo_optimizer.simulation.scenarios import DEFAULT_SITUATIONS, GameSituation


def test_optimize_returns_valid_strategy() -> None:
    optimizer = EvolutionOptimizer(
        EvolutionConfig(
            population_size=12,
            generations=6,
            elite_count=4,
            rounds_per_eval=30,
            seed=13,
        )
    )

    result = optimizer.optimize(DEFAULT_SITUATIONS[:3])

    assert -200 < result.aggregate_fitness < 0
    assert set(result.scenario_scores) == {s.name for s in DEFAULT_SITUATIONS[:3]}
    assert 0 <= result.strategy.risk_tolerance <= 1


def test_select_best_for_specific_situation_prefers_risk_aligned_policy() -> None:
    optimizer = EvolutionOptimizer(EvolutionConfig(seed=3))
    situation = GameSituation(
        name="spiky",
        volatility=0.9,
        deck_richness=0.5,
        opponent_aggression=0.5,
        endgame_pressure=0.5,
    )

    conservative = HeuristicStrategy(0.1, 0.3, 0.5, 0.4)
    aligned = HeuristicStrategy(0.9, 0.3, 0.5, 0.4)

    best = optimizer.select_best_for_situation([conservative, aligned], situation, rounds=220)

    assert best.strategy == aligned
