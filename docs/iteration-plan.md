# Iterative Testing and Optimization Plan


## Current implementation status

- ✅ Phase 0: rule-lock + invariant tests are in place.
- 🟡 Phase 1: deterministic seeded simulation runner and baseline agents are now implemented; next work is expanding benchmark reporting and integrating these metrics into experiment logging.

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

## Estimated completion timeline

Assuming focused part-time iteration (about 6-8 hours/week):

- Phase 1 completion (benchmark reporting + experiment integration): **done** in this iteration.
- Phase 2 completion (heuristic optimization loop hardening + holdout analysis): **~1-2 weeks**.
- Phase 3 completion (optional search-based agent prototype): **~1 week** after Phase 2.
- Phase 4 completion (optional learning-based extension with benchmark gates): **~2-3 weeks** after Phase 3.

Projected total to reach a robust non-optional baseline (through Phase 2): **~2 weeks**.
Projected total including optional Phases 3-4: **~5-7 weeks**.
