# Technical Setup: Language and Framework Selection

## Selected language: Python

Python is the best fit for this phase because it enables:

- Fast iteration speed for game logic changes.
- Strong data-science ecosystem for simulation analytics.
- Easy progression from baseline heuristics to RL-style agents.

## Framework/library choices

### 1. State engine

- **NumPy** for compact board/deck state representation.
- **Numba** to JIT-accelerate tight simulation loops.

Why: gives most of the speed benefit needed for Monte Carlo rollouts while keeping code readable.

### 2. Testing

- **pytest** for deterministic unit/integration tests.
- **hypothesis** for property-based tests (great for game invariants).

### 3. Data and analysis

- **pandas** for result aggregation.
- Optional later: **polars** for very large experiment logs.

### 4. CLI and orchestration

- **Typer** for command-line experiment entrypoints.
- Config files via **TOML** to keep experiment variants reproducible.

## Proposed package layout

```text
skyjo_optimizer/
  engine/
    rules.py           # legal actions, turn transitions
    state.py           # board/deck/player state
    scoring.py         # scoring and end conditions
    config.py          # ruleset toggles
  agents/
    random_agent.py
    heuristic_v1.py
    mcts_agent.py      # optional later
  simulation/
    run_match.py
    run_tournament.py
    metrics.py
  experiments/
    baselines.py
    ablations.py
  tests/
    test_rules.py
    test_scoring.py
    test_invariants.py
```

## Why not start with RL frameworks immediately?

Starting directly with heavy RL stacks (e.g., SB3/RLlib) tends to hide rule bugs and slows early learning cycles. A clean simulator + strong baselines first gives:

- Trustworthy environment dynamics.
- Faster debugging.
- Better benchmark signals before policy learning.

## Performance target for phase 1

Goal: reach at least **100k+ simulated turns/minute** on local CPU for baseline agents.

That throughput is enough for robust A/B comparison of heuristics.
