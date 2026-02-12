# Skyjo Optimizer Detailed Execution Plan

## 1) Objective and success criteria

### Objective
Build a reproducible strategy-optimization pipeline that can:
1. Simulate Skyjo rounds/matches under configurable rules.
2. Benchmark multiple agents fairly.
3. Improve heuristic policies through automated search.
4. Produce audit-ready experiment reports.

### Definition of success
- Core rule engine validates key invariants under repeated randomized testing.
- Baseline heuristic beats random by a statistically meaningful margin on hold-out seeds.
- Optimization loop shows consistent improvement across at least 3 independent reruns.
- Every report includes versioned metadata (commit hash, seed set, ruleset signature, params).

---

## 2) Scope and assumptions

### In scope
- Rule-consistent simulation of core gameplay loop.
- Deterministic experiment orchestration (seed-driven).
- Heuristic-agent parameterization and evolutionary tuning.
- Metrics and experiment artifact generation.

### Out of scope (for now)
- Production UI.
- Distributed training cluster orchestration.
- Heavy RL frameworks before simulator validation.

### Assumptions
- Python remains primary implementation language.
- Early iterations prioritize correctness + reproducibility over raw speed.
- Rule variants can be represented through configuration toggles.

---

## 3) Workstreams

## WS-A: Rules and state engine hardening

### Goals
- Encode legal move generation, turn transitions, reveal/draw/swap mechanics, and scoring.
- Enforce game invariants at each transition boundary.

### Tasks
1. **State model completion**
   - Define immutable/controlled-mutation structures for deck, discard, player grids, hidden/revealed flags.
   - Add serialization helpers for snapshots used in tests and debugging.
2. **Rules implementation**
   - Implement legal-action enumeration for each turn context.
   - Implement transition reducer that applies actions and returns next state.
3. **Scoring and termination**
   - Encode round-end triggers and score computation.
   - Include configurable toggles for disputed rule variants.
4. **Invariant validation layer**
   - Build reusable assertions for card conservation, uniqueness, and valid ownership/location.

### Deliverables
- Rule engine modules + deterministic transition tests.
- Invariant test suite (unit + property-based).

### Exit criteria
- 0 failing invariant tests over large randomized test batches.
- Round simulation reaches terminal state for all tested seeds.

---

## WS-B: Baseline agents and tournament framework

### Goals
- Establish trustworthy baseline performance reference points.
- Create repeatable multi-agent match/tournament harness.

### Tasks
1. **Agent interface**
   - Standardize agent API (`observe -> choose_action`).
   - Add validation to reject illegal actions.
2. **Baseline agents**
   - Implement random policy baseline.
   - Expand heuristic policy with explicit parameters and interpretable weights.
3. **Tournament runner**
   - Run round-robin matches across seed sets and rule variants.
   - Capture per-round and aggregate metrics.
4. **Metrics pack**
   - Win rate, mean score, median score, variance, and tail-risk quantiles.

### Deliverables
- Deterministic tournament runner.
- Baseline benchmark report template.

### Exit criteria
- Baseline runs are bitwise-reproducible given fixed seeds.
- Heuristic outperforms random on predefined benchmark suite.

---

## WS-C: Evolutionary optimization loop

### Goals
- Improve heuristic parameter vectors automatically while preventing overfitting.

### Tasks
1. **Search-space definition**
   - Enumerate tunable parameters, bounds, priors, and mutation scales.
2. **Objective function**
   - Primary objective: win rate.
   - Secondary tie-breakers: score and risk-adjusted metrics.
3. **Optimization loop improvements**
   - Elite retention, mutation schedule, and optional crossover.
   - Early-stop criteria for stalled progress.
4. **Generalization checks**
   - Train/validation seed split.
   - Periodic hold-out evaluation with frozen benchmark opponents.

### Deliverables
- Configurable optimizer driver.
- Comparison reports across generations.

### Exit criteria
- Improvement over generation-0 baseline on hold-out suite.
- Similar trends across at least 3 independent optimizer runs.

---

## WS-D: Experiment management and reproducibility

### Goals
- Ensure each experiment is traceable, comparable, and rerunnable.

### Tasks
1. **Experiment schema**
   - Store run metadata: commit hash, timestamp, ruleset hash, seed bank ID, agent params, metrics.
2. **Artifact output**
   - JSON and optional CSV summaries.
   - Structured folder naming conventions for easy diffing.
3. **CLI orchestration**
   - Add clear entrypoints for baseline runs, optimization runs, and report generation.
4. **Regression protection**
   - Add benchmark gates in CI for core metrics and deterministic replay checks.

### Deliverables
- Experiment manifest schema.
- Runnable command set for repeated studies.

### Exit criteria
- Independent rerun reproduces metrics within expected deterministic tolerance.
- Regression checks catch intentional seeded degradations.

---

## 4) Milestone schedule (suggested)

### Milestone 1 (Week 1)
- Complete core state/rules/scoring implementation.
- Add invariant/property tests.

### Milestone 2 (Week 2)
- Ship random + heuristic agents on tournament harness.
- Generate baseline benchmark report.

### Milestone 3 (Week 3)
- Integrate upgraded evolutionary loop with hold-out validation.
- Produce first optimization trend report.

### Milestone 4 (Week 4)
- Finalize reproducibility tooling + report CLI.
- Add CI benchmark gating and deterministic replay checks.

---

## 5) Risk register and mitigations

1. **Risk: Rule ambiguity causes invalid comparisons**
   - Mitigation: central rule-config object + explicit variant labels in every report.
2. **Risk: Overfitting to specific seed sets/opponents**
   - Mitigation: rotating seed banks, hold-out suite, frozen benchmark agents.
3. **Risk: Slow simulation throughput blocks optimization iterations**
   - Mitigation: profile hotspots, cache repeated computations, optionally add Numba after correctness lock.
4. **Risk: Hidden nondeterminism in code path**
   - Mitigation: seed plumbing audit + deterministic replay test in CI.

---

## 6) Execution checklist

- [ ] Finalize rule/config specification with documented toggles.
- [ ] Implement and validate transition engine.
- [ ] Build invariant + property-based test harness.
- [ ] Ship baseline agent interface and two baseline agents.
- [ ] Implement deterministic tournament runner and metrics aggregation.
- [ ] Define optimization config schema and search space.
- [ ] Run first optimization experiment batch and inspect convergence.
- [ ] Add hold-out generalization evaluation.
- [ ] Implement experiment manifest + artifact writer.
- [ ] Add CLI commands for full reproducible workflow.
- [ ] Add CI checks for invariants, deterministic replay, and benchmark regression.

---

## 7) Immediate next actions

1. Convert existing evaluator/scenario abstractions into a formal, rule-driven round engine.
2. Add high-priority invariant tests (card conservation, no duplicate card identity, legal-action validity).
3. Define benchmark seed bank and frozen baseline opponent set.
4. Produce first baseline report and use it as optimization reference.
