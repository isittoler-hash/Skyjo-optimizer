from __future__ import annotations

import json
import subprocess
import sys

from skyjo_optimizer.engine import RulesConfig, initialize_round
from skyjo_optimizer.simulation import run_regression_checks
from skyjo_optimizer.simulation.baseline import _score_player


def test_column_clearing_excludes_matching_revealed_column() -> None:
    state = initialize_round(RulesConfig(), player_count=2, seed=9)

    player = state.players[0]
    value_to_ids: dict[int, list[int]] = {}
    for card in state.cards.values():
        value_to_ids.setdefault(card.value, []).append(card.card_id)

    matching_value = next(value for value, ids in value_to_ids.items() if len(ids) >= 3)
    forced_slots = list(player.slots)
    forced_slots[0], forced_slots[4], forced_slots[8] = value_to_ids[matching_value][:3]

    state = state.__class__(
        rules=state.rules,
        cards=state.cards,
        players=(
            player.__class__(slots=tuple(forced_slots), face_up=frozenset({0, 4, 8, *player.face_up})),
            state.players[1],
        ),
        draw_pile=state.draw_pile,
        discard_pile=state.discard_pile,
        active_player=state.active_player,
        turn_count=state.turn_count,
        final_turns_remaining=state.final_turns_remaining,
        round_ender=state.round_ender,
    )

    score = _score_player(state, 0)
    raw = sum(state.cards[c].value for c in forced_slots)
    assert score == raw - matching_value * 3


def test_regression_checks_pass() -> None:
    result = run_regression_checks(rounds=20, seed=5)
    assert result.deterministic_replay_ok is True
    assert result.heuristic_beats_random is True


def test_cli_verify_command() -> None:
    output = subprocess.check_output(
        [sys.executable, "-m", "skyjo_optimizer.cli", "verify", "--rounds", "20", "--seed", "5"],
        text=True,
    )
    payload = json.loads(output)
    assert payload["deterministic_replay_ok"] is True
