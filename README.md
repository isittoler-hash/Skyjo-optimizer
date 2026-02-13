# Skyjo Optimizer Setup

This repository includes a reproducible **strategy-optimization pipeline** for Skyjo with:

- A deterministic round engine with configurable rule toggles.
- Baseline tournament simulation and benchmark metrics.
- Evolutionary heuristic optimization with train/holdout seed splits.
- Experiment reports with metadata and artifact writing.
- CLI entrypoints for baseline benchmarking, optimization runs, and deterministic regression checks.

## Quick start

```bash
python -m pytest
python -m skyjo_optimizer.cli baseline --rounds 24 --seed 7
python -m skyjo_optimizer.cli optimize --population-size 24 --generations 20 --seed 7
python -m skyjo_optimizer.cli verify --rounds 60 --seed 11
```

## Artifact layout

Optimization runs write timestamped folders under `artifacts/` containing:

- `report.json` with run metadata, optimized strategy metrics, holdout score, and tournament benchmark.
- `tournament_summary.csv` with per-agent aggregate metrics.

## Code map

```text
skyjo_optimizer/
  engine/config.py             # configurable ruleset + disputed-rule toggles
  engine/state.py              # round state, legal actions, turn transitions
  agents/heuristic.py          # strategy parameters
  simulation/scenarios.py      # game situations (test contexts)
  simulation/evaluator.py      # deterministic strategy scoring
  simulation/baseline.py       # seeded round/tournament runner + baseline agents
  ml/evolution.py              # evolutionary optimization with holdout checks
  ml/experiment.py             # experiment metadata + artifact generation
  cli.py                       # CLI entrypoints for baseline and optimization
```

## Production release planning

For a step-by-step workflow to move the project to a production-ready release, see:

- `docs/production-release-workflow.md`
