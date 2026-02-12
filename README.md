# Skyjo Optimizer Setup

This repository now includes a first executable baseline for **multi-situation strategy testing** and **evolutionary strategy selection**.

## What is implemented

- `GameSituation` profiles to represent different table conditions.
- A parameterized `HeuristicStrategy` policy vector.
- A deterministic evaluator that scores strategies under each situation.
- A seeded baseline simulator with random and simple heuristic agents for round-robin play.
- An evolutionary optimizer that mutates strategy weights and keeps elites.
- A selector that picks the best strategy for a specific situation.
- An experiment runner that records metadata + benchmark comparisons and can write JSON reports.
- A first-pass engine skeleton with rules configuration and round-level invariant checks.

## Quick start

```bash
python -m pytest
```

## Code map

```text
skyjo_optimizer/
  engine/config.py             # configurable ruleset + disputed-rule toggles
  engine/state.py              # round state, legal actions, turn transitions
  agents/heuristic.py          # strategy parameters
  simulation/scenarios.py      # game situations (test contexts)
  simulation/evaluator.py      # deterministic strategy scoring
  simulation/baseline.py       # seeded round/tournament runner + baseline agents
  ml/evolution.py              # evolutionary optimization + selection
  ml/experiment.py             # experiment metadata + report generation
tests/
  test_evolution.py
  test_engine_invariants.py
```

## Notes

The optimizer evaluator remains a synthetic proxy objective for fast iterations.
Alongside it, the baseline simulator now runs full round-state transitions with deterministic seeds so head-to-head comparisons are reproducible between runs.

See the planning docs for full simulator roadmap:

- [`docs/skyjo-rules.md`](docs/skyjo-rules.md)
- [`docs/technical-approach.md`](docs/technical-approach.md)
- [`docs/iteration-plan.md`](docs/iteration-plan.md)
