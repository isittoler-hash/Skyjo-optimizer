# Skyjo Optimizer Setup

This repository now includes a first executable baseline for **multi-situation strategy testing** and **evolutionary strategy selection**.

## What is implemented

- `GameSituation` profiles to represent different table conditions.
- A parameterized `HeuristicStrategy` policy vector.
- A deterministic evaluator that scores strategies under each situation.
- An evolutionary optimizer that mutates strategy weights and keeps elites.
- A selector that picks the best strategy for a specific situation.

## Quick start

```bash
python -m pytest
```

## Code map

```text
skyjo_optimizer/
  agents/heuristic.py          # strategy parameters
  simulation/scenarios.py      # game situations (test contexts)
  simulation/evaluator.py      # deterministic strategy scoring
  ml/evolution.py              # evolutionary optimization + selection
tests/
  test_evolution.py
```

## Notes

The evaluator is currently a synthetic proxy objective until full Skyjo state-transition rules are implemented.
It is deterministic and seeded so comparisons are reproducible between runs.

See the planning docs for full simulator roadmap:

- [`docs/skyjo-rules.md`](docs/skyjo-rules.md)
- [`docs/technical-approach.md`](docs/technical-approach.md)
- [`docs/iteration-plan.md`](docs/iteration-plan.md)
