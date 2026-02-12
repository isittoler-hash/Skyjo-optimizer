from __future__ import annotations

import random
from dataclasses import dataclass

from skyjo_optimizer.agents.heuristic import HeuristicStrategy
from skyjo_optimizer.simulation.scenarios import GameSituation


@dataclass(frozen=True)
class EvaluationResult:
    scenario: str
    mean_score: float
    variance: float
    fitness: float


def _single_round_score(
    strategy: HeuristicStrategy,
    situation: GameSituation,
    rng: random.Random,
) -> float:
    """Synthetic score model used until full game engine is available.

    Lower is better and loosely mirrors Skyjo trade-offs.
    """

    noise = rng.gauss(0.0, 4.0)

    base_score = 35.0
    risk_effect = (situation.volatility * 18 - 9) * strategy.risk_tolerance
    reveal_effect = -12 * situation.endgame_pressure * strategy.reveal_priority
    column_effect = -10 * situation.deck_richness * strategy.column_focus
    discard_effect = -8 * situation.opponent_aggression * strategy.discard_aggression

    mismatch_penalty = 14 * abs(strategy.risk_tolerance - situation.volatility)
    balance_bonus = -6 * (
        strategy.reveal_priority + strategy.column_focus + strategy.discard_aggression
    ) / 3

    return (
        base_score
        + risk_effect
        + reveal_effect
        + column_effect
        + discard_effect
        + mismatch_penalty
        + balance_bonus
        + noise
    )


def evaluate_strategy(
    strategy: HeuristicStrategy,
    situation: GameSituation,
    rounds: int,
    seed: int,
) -> EvaluationResult:
    rng = random.Random(seed)
    samples = [_single_round_score(strategy, situation, rng) for _ in range(rounds)]
    mean = sum(samples) / len(samples)
    variance = sum((x - mean) ** 2 for x in samples) / len(samples)
    # Maximize fitness: lower score and lower variance are preferred.
    fitness = -mean - 0.05 * variance
    return EvaluationResult(
        scenario=situation.name,
        mean_score=mean,
        variance=variance,
        fitness=fitness,
    )
