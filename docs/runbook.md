# Runbook

This runbook covers the exact command sequence to go from a clean machine to generated optimizer artifacts.

## 1) Set up Python environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## 2) Validate the repository

```bash
make test
```

## 3) Produce a baseline benchmark artifact

```bash
make baseline
```

This writes `artifacts/baseline.json`.

## 4) Run optimization and generate experiment artifacts

```bash
make optimize
```

This prints the timestamped output directory and writes artifacts under `artifacts/` (including `report.json` and `tournament_summary.csv`).

## 5) Full one-shot verification flow

```bash
make verify
```

`make verify` runs tests, baseline, and optimization in sequence.
