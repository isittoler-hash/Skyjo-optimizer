# Skyjo Optimizer Setup

This repository is prepared to build a **code-driven, iterative optimizer** for the card game **Skyjo**.

## What this setup includes

- A rules and assumptions brief for Skyjo.
- A project strategy for simulation-first optimization.
- A recommended language/framework stack.
- A testing and iteration roadmap.

## Recommended implementation stack

- **Language:** Python 3.12+
- **Core libs:** NumPy (state arrays), Numba (hot-loop acceleration), pandas (analysis)
- **Testing:** pytest + hypothesis
- **Experiment tracking:** lightweight CSV/Parquet logs (later upgrade to MLflow/W&B if needed)

See details in:

- [`docs/skyjo-rules.md`](docs/skyjo-rules.md)
- [`docs/technical-approach.md`](docs/technical-approach.md)
- [`docs/iteration-plan.md`](docs/iteration-plan.md)
