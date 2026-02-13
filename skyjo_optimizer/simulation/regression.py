from __future__ import annotations

from dataclasses import dataclass

from skyjo_optimizer.simulation.baseline import RandomAgent, SimpleHeuristicAgent, run_tournament


@dataclass(frozen=True)
class RegressionCheckResult:
    deterministic_replay_ok: bool
    heuristic_beats_random: bool
    heuristic_mean_score: float
    random_mean_score: float
    heuristic_win_rate: float
    random_win_rate: float


def run_regression_checks(*, rounds: int = 60, seed: int = 11) -> RegressionCheckResult:
    agents = [SimpleHeuristicAgent("heuristic"), RandomAgent("random")]

    first = run_tournament(agents, rounds=rounds, seed=seed)
    second = run_tournament(agents, rounds=rounds, seed=seed)

    deterministic_replay_ok = first == second
    heuristic_beats_random = (
        first.mean_score_by_agent["heuristic"] < first.mean_score_by_agent["random"]
        and first.win_rate_by_agent["heuristic"] > first.win_rate_by_agent["random"]
    )

    return RegressionCheckResult(
        deterministic_replay_ok=deterministic_replay_ok,
        heuristic_beats_random=heuristic_beats_random,
        heuristic_mean_score=first.mean_score_by_agent["heuristic"],
        random_mean_score=first.mean_score_by_agent["random"],
        heuristic_win_rate=first.win_rate_by_agent["heuristic"],
        random_win_rate=first.win_rate_by_agent["random"],
    )
