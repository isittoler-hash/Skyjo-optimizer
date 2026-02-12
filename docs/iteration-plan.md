# Iterative Testing and Optimization Plan

## Phase 0: Rule-lock and invariants

Deliverables:
- Formalized rules config (including disputed-rule toggles).
- Invariant tests that must always hold.

Required invariants:
- Card conservation: total card multiset is constant.
- No duplicate card identity in multiple locations.
- Legal-action generator never outputs impossible moves.
- Round termination always reaches scoring in finite steps.

## Phase 1: Baseline simulator

Deliverables:
- Deterministic seeded simulation runner.
- Baseline agents:
  - Random policy.
  - Simple heuristic policy (value-seeking + basic column logic).

Evaluation:
- Win rate matrix in round-robin tournaments.
- Mean/median round score.
- Variance and tail risk (95th percentile bad rounds).

## Phase 2: Heuristic optimization loop

Process:
1. Define a parameterized heuristic family.
2. Run tournament batch with fixed seeds.
3. Rank by multi-metric objective (win rate primary, score secondary).
4. Keep top variants; mutate parameters.
5. Repeat.

Guardrails:
- Hold-out seed sets to reduce overfitting.
- Keep one frozen benchmark agent throughout all runs.

## Phase 3: Search-based agent (optional)

Introduce Monte Carlo lookahead under partial observability:
- Belief sampling over hidden cards.
- Rollouts using tuned heuristic policy.
- Action chosen by expected value + risk adjustment.

## Phase 4: Learning-based extensions (optional)

Only after simulator and baselines are stable:
- Contextual bandit policy improvement for local decisions.
- RL policy training with strict benchmark gating.

## Experiment logging standard

Each run should persist:
- Git commit hash.
- Ruleset config hash.
- Agent version + parameters.
- RNG seed set.
- Full metric outputs.

## Initial definition of success

- Heuristic agent significantly outperforms random baseline.
- Results are reproducible under reruns.
- Rule-variant sensitivity is measured and reported.
