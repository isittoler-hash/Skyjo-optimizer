from __future__ import annotations

import random
from collections import Counter

from skyjo_optimizer.engine import (
    RulesConfig,
    apply_action,
    card_location_counts,
    initialize_round,
    is_round_over,
    legal_actions,
)


def test_round_initialization_conserves_card_multiset() -> None:
    rules = RulesConfig()
    state = initialize_round(rules, player_count=4, seed=11)

    expected = Counter()
    for value, count in rules.deck_composition.items():
        expected[value] = count

    observed = Counter(state.cards[card_id].value for card_id in card_location_counts(state).elements())
    assert observed == expected


def test_card_identity_unique_across_locations_during_playout() -> None:
    state = initialize_round(RulesConfig(), player_count=3, seed=21)
    rng = random.Random(21)

    for _ in range(120):
        counts = card_location_counts(state)
        assert set(counts.values()) == {1}

        actions = legal_actions(state)
        action = rng.choice(actions)
        state = apply_action(state, action)
        if is_round_over(state):
            break


def test_legal_actions_are_applyable() -> None:
    state = initialize_round(RulesConfig(), player_count=4, seed=7)

    for action in legal_actions(state):
        next_state = apply_action(state, action)
        assert next_state.turn_count == state.turn_count + 1


def test_random_playout_terminates_in_finite_steps() -> None:
    state = initialize_round(RulesConfig(), player_count=4, seed=99)
    rng = random.Random(99)

    for _ in range(1000):
        if is_round_over(state):
            break
        state = apply_action(state, rng.choice(legal_actions(state)))
    else:
        raise AssertionError("round did not terminate in finite steps")

    assert is_round_over(state)
