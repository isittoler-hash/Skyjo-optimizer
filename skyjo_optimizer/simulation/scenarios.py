from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameSituation:
    """Defines a testing context that changes the value of strategy behaviors.

    Values are normalized to roughly ``0..1`` and interpreted by the evaluator.
    """

    name: str
    volatility: float
    deck_richness: float
    opponent_aggression: float
    endgame_pressure: float


DEFAULT_SITUATIONS = [
    GameSituation(
        name="balanced",
        volatility=0.5,
        deck_richness=0.5,
        opponent_aggression=0.5,
        endgame_pressure=0.5,
    ),
    GameSituation(
        name="high_volatility",
        volatility=0.9,
        deck_richness=0.4,
        opponent_aggression=0.7,
        endgame_pressure=0.8,
    ),
    GameSituation(
        name="control_table",
        volatility=0.3,
        deck_richness=0.6,
        opponent_aggression=0.2,
        endgame_pressure=0.4,
    ),
    GameSituation(
        name="scarce_deck",
        volatility=0.4,
        deck_richness=0.2,
        opponent_aggression=0.6,
        endgame_pressure=0.7,
    ),
]
