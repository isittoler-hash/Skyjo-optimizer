from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


DEFAULT_DECK_COMPOSITION: dict[int, int] = {
    -2: 5,
    -1: 10,
    0: 15,
    **{value: 10 for value in range(1, 13)},
}


@dataclass(frozen=True)
class RulesConfig:
    """Configurable Skyjo rule switches and constants."""

    cards_per_player: int = 12
    starting_face_up_cards: int = 2
    target_match_score: int = 100
    ender_penalty_mode: str = "strict_lowest_required"
    deck_composition: Mapping[int, int] = field(default_factory=lambda: DEFAULT_DECK_COMPOSITION.copy())

    def validate(self) -> None:
        if self.cards_per_player <= 0:
            raise ValueError("cards_per_player must be positive")
        if self.starting_face_up_cards < 0:
            raise ValueError("starting_face_up_cards must be non-negative")
        if self.starting_face_up_cards > self.cards_per_player:
            raise ValueError("starting_face_up_cards cannot exceed cards_per_player")
        if self.ender_penalty_mode not in {"strict_lowest_required", "off"}:
            raise ValueError("ender_penalty_mode must be 'strict_lowest_required' or 'off'")
        if not self.deck_composition:
            raise ValueError("deck_composition must not be empty")
        if any(count <= 0 for count in self.deck_composition.values()):
            raise ValueError("all deck composition counts must be positive")

    @property
    def total_cards(self) -> int:
        return sum(self.deck_composition.values())
