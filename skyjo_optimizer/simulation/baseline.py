from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random
from statistics import mean, median

from skyjo_optimizer.engine import Action, RoundState, RulesConfig, apply_action, initialize_round, is_round_over, legal_actions


@dataclass(frozen=True)
class RoundResult:
    scores_by_agent: dict[str, int]
    winner_names: tuple[str, ...]
    turns: int


@dataclass(frozen=True)
class TournamentResult:
    rounds: tuple[RoundResult, ...]
    mean_score_by_agent: dict[str, float]
    median_score_by_agent: dict[str, float]
    tail95_score_by_agent: dict[str, float]
    win_rate_by_agent: dict[str, float]
    win_rate_matrix: dict[str, dict[str, float]]


class BaselineAgent(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def choose_action(self, state: RoundState, actions: list[Action], rng: Random) -> Action:
        """Choose one legal action from the current state."""


class RandomAgent(BaselineAgent):
    def choose_action(self, state: RoundState, actions: list[Action], rng: Random) -> Action:
        return rng.choice(actions)


class SimpleHeuristicAgent(BaselineAgent):
    """Simple value-seeking baseline.

    Strategy:
    - If discard top card is low, swap it into a hidden slot first.
    - Otherwise prefer flipping hidden cards to reduce uncertainty.
    - If all cards are revealed, replace the current highest-value card.
    """

    def choose_action(self, state: RoundState, actions: list[Action], rng: Random) -> Action:
        player = state.players[state.active_player]
        values = [state.cards[card_id].value for card_id in player.slots]
        discard_top = state.cards[state.discard_pile[-1]].value

        hidden_slots = [idx for idx in range(len(player.slots)) if idx not in player.face_up]
        if discard_top <= 2:
            if hidden_slots:
                preferred_slot = hidden_slots[0]
            else:
                preferred_slot = max(range(len(values)), key=lambda idx: values[idx])
            for action in actions:
                if action.kind == "take_discard_swap" and action.slot_index == preferred_slot:
                    return action

        if hidden_slots:
            flip_slot = hidden_slots[0]
            for action in actions:
                if action.kind == "draw_discard_flip" and action.slot_index == flip_slot:
                    return action

        highest_slot = max(range(len(values)), key=lambda idx: values[idx])
        for action in actions:
            if action.kind == "draw_swap" and action.slot_index == highest_slot:
                return action

        return rng.choice(actions)


def run_round(
    agents: list[BaselineAgent],
    *,
    seed: int,
    rules: RulesConfig | None = None,
    max_turns: int = 1000,
) -> RoundResult:
    if len(agents) < 2:
        raise ValueError("at least two agents are required")

    config = rules or RulesConfig()
    state = initialize_round(config, player_count=len(agents), seed=seed)
    rng = Random(seed)

    for _ in range(max_turns):
        if is_round_over(state):
            break
        action = agents[state.active_player].choose_action(state, legal_actions(state), rng)
        state = apply_action(state, action)
    else:
        raise RuntimeError("round exceeded max_turns without termination")

    scores = {
        agent.name: _score_player(state, idx)
        for idx, agent in enumerate(agents)
    }
    best_score = min(scores.values())
    winners = tuple(sorted(name for name, score in scores.items() if score == best_score))

    return RoundResult(scores_by_agent=scores, winner_names=winners, turns=state.turn_count)


def run_tournament(
    agents: list[BaselineAgent],
    *,
    rounds: int,
    seed: int,
    rules: RulesConfig | None = None,
) -> TournamentResult:
    if rounds <= 0:
        raise ValueError("rounds must be positive")

    per_agent_scores: dict[str, list[int]] = {agent.name: [] for agent in agents}
    wins: dict[str, float] = {agent.name: 0.0 for agent in agents}
    matrix_counts: dict[str, dict[str, float]] = {
        agent.name: {other.name: 0.0 for other in agents if other.name != agent.name}
        for agent in agents
    }

    round_results: list[RoundResult] = []
    for round_index in range(rounds):
        seating = _rotate_agents(agents, round_index)
        result = run_round(seating, seed=seed + round_index * 13, rules=rules)
        round_results.append(result)

        for name, score in result.scores_by_agent.items():
            per_agent_scores[name].append(score)

        share = 1.0 / len(result.winner_names)
        for winner in result.winner_names:
            wins[winner] += share
        for a_name in wins:
            for b_name in matrix_counts[a_name]:
                if result.scores_by_agent[a_name] < result.scores_by_agent[b_name]:
                    matrix_counts[a_name][b_name] += 1.0
                elif result.scores_by_agent[a_name] == result.scores_by_agent[b_name]:
                    matrix_counts[a_name][b_name] += 0.5

    mean_scores = {name: mean(scores) for name, scores in per_agent_scores.items()}
    median_scores = {name: median(scores) for name, scores in per_agent_scores.items()}
    tail95_scores = {
        name: _percentile(scores, 0.95)
        for name, scores in per_agent_scores.items()
    }
    win_rates = {name: value / rounds for name, value in wins.items()}
    matrix = {
        a_name: {b_name: value / rounds for b_name, value in row.items()}
        for a_name, row in matrix_counts.items()
    }

    return TournamentResult(
        rounds=tuple(round_results),
        mean_score_by_agent=mean_scores,
        median_score_by_agent=median_scores,
        tail95_score_by_agent=tail95_scores,
        win_rate_by_agent=win_rates,
        win_rate_matrix=matrix,
    )


def _rotate_agents(agents: list[BaselineAgent], shift: int) -> list[BaselineAgent]:
    offset = shift % len(agents)
    return agents[offset:] + agents[:offset]


def _score_player(state: RoundState, player_index: int) -> int:
    player = state.players[player_index]
    return sum(state.cards[card_id].value for card_id in player.slots)


def _percentile(values: list[int], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])

    target = (len(ordered) - 1) * q
    low = int(target)
    high = min(low + 1, len(ordered) - 1)
    weight = target - low
    return ordered[low] * (1 - weight) + ordered[high] * weight
