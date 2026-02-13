from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random

from skyjo_optimizer.engine.config import RulesConfig


@dataclass(frozen=True)
class Card:
    card_id: int
    value: int


@dataclass(frozen=True)
class PlayerState:
    slots: tuple[int, ...]
    face_up: frozenset[int]


@dataclass(frozen=True)
class RoundState:
    rules: RulesConfig
    cards: dict[int, Card]
    players: tuple[PlayerState, ...]
    draw_pile: tuple[int, ...]
    discard_pile: tuple[int, ...]
    active_player: int
    turn_count: int
    final_turns_remaining: int | None
    round_ender: int | None


@dataclass(frozen=True)
class Action:
    kind: str
    slot_index: int


def build_deck(rules: RulesConfig) -> list[Card]:
    rules.validate()
    deck: list[Card] = []
    next_id = 0
    for value, count in sorted(rules.deck_composition.items()):
        for _ in range(count):
            deck.append(Card(card_id=next_id, value=value))
            next_id += 1
    return deck


def initialize_round(rules: RulesConfig, player_count: int, seed: int) -> RoundState:
    if player_count < 2:
        raise ValueError("player_count must be at least 2")

    deck = build_deck(rules)
    if len(deck) < player_count * rules.cards_per_player + 1:
        raise ValueError("deck too small for requested number of players")

    rng = Random(seed)
    card_ids = [card.card_id for card in deck]
    rng.shuffle(card_ids)

    players: list[PlayerState] = []
    cursor = 0
    for _ in range(player_count):
        slots = tuple(card_ids[cursor : cursor + rules.cards_per_player])
        cursor += rules.cards_per_player

        face_up_indices = set(rng.sample(range(rules.cards_per_player), rules.starting_face_up_cards))
        players.append(PlayerState(slots=slots, face_up=frozenset(face_up_indices)))

    discard_pile = (card_ids[cursor],)
    cursor += 1
    draw_pile = tuple(card_ids[cursor:])
    cards_by_id = {card.card_id: card for card in deck}

    return RoundState(
        rules=rules,
        cards=cards_by_id,
        players=tuple(players),
        draw_pile=draw_pile,
        discard_pile=discard_pile,
        active_player=0,
        turn_count=0,
        final_turns_remaining=None,
        round_ender=None,
    )


def legal_actions(state: RoundState) -> list[Action]:
    player = state.players[state.active_player]
    actions: list[Action] = []
    for slot_index in range(len(player.slots)):
        actions.append(Action(kind="take_discard_swap", slot_index=slot_index))
        actions.append(Action(kind="draw_swap", slot_index=slot_index))
        if slot_index not in player.face_up:
            actions.append(Action(kind="draw_discard_flip", slot_index=slot_index))
    return actions


def apply_action(state: RoundState, action: Action) -> RoundState:
    if action not in legal_actions(state):
        raise ValueError("illegal action")

    players = [
        PlayerState(slots=tuple(player.slots), face_up=frozenset(player.face_up))
        for player in state.players
    ]
    draw_pile = list(state.draw_pile)
    discard_pile = list(state.discard_pile)
    player = players[state.active_player]

    slot_cards = list(player.slots)
    face_up = set(player.face_up)

    if action.kind == "take_discard_swap":
        incoming = discard_pile.pop()
        outgoing = slot_cards[action.slot_index]
        slot_cards[action.slot_index] = incoming
        discard_pile.append(outgoing)
        face_up.add(action.slot_index)
    elif action.kind == "draw_swap":
        incoming, draw_pile, discard_pile = _draw_card(draw_pile, discard_pile)
        outgoing = slot_cards[action.slot_index]
        slot_cards[action.slot_index] = incoming
        discard_pile.append(outgoing)
        face_up.add(action.slot_index)
    elif action.kind == "draw_discard_flip":
        _, draw_pile, discard_pile = _draw_card(draw_pile, discard_pile)
        face_up.add(action.slot_index)
    else:
        raise ValueError(f"unknown action kind: {action.kind}")

    players[state.active_player] = PlayerState(slots=tuple(slot_cards), face_up=frozenset(face_up))

    next_state = RoundState(
        rules=state.rules,
        cards=state.cards,
        players=tuple(players),
        draw_pile=tuple(draw_pile),
        discard_pile=tuple(discard_pile),
        active_player=state.active_player,
        turn_count=state.turn_count,
        final_turns_remaining=state.final_turns_remaining,
        round_ender=state.round_ender,
    )
    return _advance_turn(next_state)


def _draw_card(draw_pile: list[int], discard_pile: list[int]) -> tuple[int, list[int], list[int]]:
    if not draw_pile:
        if len(discard_pile) <= 1:
            raise RuntimeError("no cards available to draw")
        top_discard = discard_pile.pop()
        draw_pile[:] = discard_pile
        discard_pile[:] = [top_discard]

    card_id = draw_pile.pop()
    return card_id, draw_pile, discard_pile


def _advance_turn(state: RoundState) -> RoundState:
    players = state.players
    final_turns_remaining = state.final_turns_remaining
    round_ender = state.round_ender

    if final_turns_remaining is None:
        for index, player in enumerate(players):
            if len(player.face_up) == len(player.slots):
                round_ender = index
                final_turns_remaining = len(players) - 1
                break
    elif final_turns_remaining > 0:
        final_turns_remaining -= 1

    return RoundState(
        rules=state.rules,
        cards=state.cards,
        players=players,
        draw_pile=state.draw_pile,
        discard_pile=state.discard_pile,
        active_player=(state.active_player + 1) % len(players),
        turn_count=state.turn_count + 1,
        final_turns_remaining=final_turns_remaining,
        round_ender=round_ender,
    )


def is_round_over(state: RoundState) -> bool:
    return state.final_turns_remaining == 0


def card_location_counts(state: RoundState) -> Counter[int]:
    counts: Counter[int] = Counter(state.draw_pile)
    counts.update(state.discard_pile)
    for player in state.players:
        counts.update(player.slots)
    return counts
