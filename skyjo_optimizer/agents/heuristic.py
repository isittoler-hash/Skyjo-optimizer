from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeuristicStrategy:
    """Parameterized Skyjo-style strategy weights.

    Lower estimated score is better; the evaluator converts this to fitness.
    """

    risk_tolerance: float
    reveal_priority: float
    column_focus: float
    discard_aggression: float

    def clipped(self) -> "HeuristicStrategy":
        def c(value: float) -> float:
            return max(0.0, min(1.0, value))

        return HeuristicStrategy(
            risk_tolerance=c(self.risk_tolerance),
            reveal_priority=c(self.reveal_priority),
            column_focus=c(self.column_focus),
            discard_aggression=c(self.discard_aggression),
        )
