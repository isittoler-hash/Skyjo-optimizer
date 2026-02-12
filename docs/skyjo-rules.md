# Skyjo Rules Research Summary

> Note: Skyjo has minor house-rule differences. This document encodes a practical baseline for building a simulator. Any disputed rule should be represented as a configurable option in code.

## Round structure

1. Each player gets **12 cards** laid out in a **3 x 4 grid**, initially face-down.
2. Each player flips **2 of their 12 cards** face-up.
3. One card is placed face-up to start the discard pile; the rest form the draw pile.
4. Play proceeds clockwise.

## Turn actions (baseline)

On a turn, the active player may:

1. **Take the top discard card**, then swap it with one card in their grid (face-up or face-down), discarding the replaced card.
2. **Or draw top card from draw pile** and:
   - swap it with one grid card (discarding replaced card), or
   - discard the drawn card immediately and instead flip one face-down grid card face-up.

## Column-clearing rule

If all 3 cards in a vertical column are face-up and have equal value, that column is removed from play (effectively contributes 0 points).

## End of round

A round end is triggered when one player has all cards face-up.

Baseline simulator policy:
- The triggering player finishes their turn.
- All other players receive one final turn.
- Then scoring is computed.

## Scoring

- A player’s round score is the sum of remaining grid cards (after removed columns are gone).
- Lower is better.

### Common penalty rule (recommended default)

If the round-ending player does **not** have the **strictly lowest** score, their score is doubled for that round.

Because this rule differs by table/edition, implement it as a switch:
- `ender_penalty_mode = "strict_lowest_required"` (default)
- `ender_penalty_mode = "off"`

## Deck composition (recommended baseline model)

Use the commonly cited distribution:

- `-2`: 5 cards
- `-1`: 10 cards
- `0`: 15 cards
- `1..12`: 10 cards each value

Total = 150 cards.

If another edition differs, keep deck composition configurable.

## Match end

Play rounds until at least one player reaches or exceeds target points (commonly 100). Winner is lowest total score.

## Strategy implications for optimization

- Information asymmetry is core: unknown face-down cards drive risk.
- Discard-pile value and future board flexibility both matter.
- Column completion has high tactical leverage.
- End-round timing creates a race/tempo layer.
