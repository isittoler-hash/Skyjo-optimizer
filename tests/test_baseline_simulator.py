from __future__ import annotations

from skyjo_optimizer.simulation import RandomAgent, SimpleHeuristicAgent, run_round, run_tournament


def test_run_round_is_deterministic_for_fixed_seed() -> None:
    agents = [SimpleHeuristicAgent("heuristic"), RandomAgent("random"), RandomAgent("random_2")]

    first = run_round(agents, seed=42)
    second = run_round(agents, seed=42)

    assert first == second


def test_tournament_produces_expected_metrics_shapes() -> None:
    agents = [SimpleHeuristicAgent("heuristic"), RandomAgent("random"), RandomAgent("random_2")]
    result = run_tournament(agents, rounds=8, seed=5)

    assert len(result.rounds) == 8
    assert set(result.mean_score_by_agent) == {agent.name for agent in agents}
    assert set(result.median_score_by_agent) == {agent.name for agent in agents}
    assert set(result.tail95_score_by_agent) == {agent.name for agent in agents}
    assert abs(sum(result.win_rate_by_agent.values()) - 1.0) < 1e-9

    for row_name, row in result.win_rate_matrix.items():
        assert row_name not in row
        assert set(row) == {agent.name for agent in agents if agent.name != row_name}
        for value in row.values():
            assert 0.0 <= value <= 1.0


def test_simple_heuristic_outperforms_random_in_head_to_head() -> None:
    agents = [SimpleHeuristicAgent("heuristic"), RandomAgent("random")]
    result = run_tournament(agents, rounds=60, seed=11)

    assert result.mean_score_by_agent["heuristic"] < result.mean_score_by_agent["random"]
    assert result.win_rate_by_agent["heuristic"] > result.win_rate_by_agent["random"]
