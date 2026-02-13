# Open PR merge plan

Date: 2026-02-13
Repository: `isittoler-hash/Skyjo-optimizer`

## Open pull requests reviewed

1. **#12 — Add pipeline CLI command with manifest output**
   - Branch: `codex/add-cli-command-for-benchmarks-and-manifest` -> `main`
   - Files changed:
     - `skyjo_optimizer/cli.py`
     - `tests/test_cli_and_artifacts.py`
   - Scope summary:
     - Adds a `pipeline` CLI command that runs baseline tournament, optimization, holdout scoring, artifact verification, and writes `manifest.json`.

2. **#11 — Add consolidated artifacts report-summary CLI and reporting module**
   - Branch: `codex/add-module-to-consolidate-report.json-to-csv` -> `main`
   - Files changed:
     - `skyjo_optimizer/cli.py`
     - `skyjo_optimizer/ml/__init__.py`
     - `skyjo_optimizer/ml/reporting.py`
     - `tests/test_cli_and_artifacts.py`
     - `tests/test_reporting.py`
   - Scope summary:
     - Adds `report-summary` CLI command and a reporting module to aggregate `artifacts/*/report.json` into a CSV.

## Mergeability and conflict assessment

- Both PRs currently report non-mergeable/dirty status against `main`.
- Both PRs modify the same high-conflict files:
  - `skyjo_optimizer/cli.py`
  - `tests/test_cli_and_artifacts.py`
- Risk profile:
  - **High** risk of textual conflicts in CLI parser setup and command dispatch logic.
  - **Medium** risk of semantic conflicts if test assumptions overlap around artifact layout and command outputs.

## Proposed merge sequence

1. **Merge #12 first (pipeline command).**
   - Rationale: It introduces an end-to-end workflow and additional artifact files (`baseline.json`, `holdout_score.json`, `verify.json`, `manifest.json`) that can then be consumed or referenced by follow-up reporting tooling.

2. **Rebase/refresh #11 on top of post-#12 `main`, then merge #11.**
   - Resolve conflicts in `cli.py` by preserving both subcommands:
     - `pipeline`
     - `report-summary`
   - Resolve conflicts in `tests/test_cli_and_artifacts.py` by keeping both feature test sets.

## Concrete conflict-resolution checklist

1. In `skyjo_optimizer/cli.py`:
   - Keep all imports needed by both PRs.
   - Register both subparsers (`pipeline` and `report-summary`).
   - Keep both command handlers in `main()` and ensure each returns proper exit code.
   - Preserve helper functions added by #12 (`_current_commit_hash`, `_verify_pipeline_artifacts`) and #11 reporting calls (`summarize_reports`, `write_summary_csv`).

2. In `tests/test_cli_and_artifacts.py`:
   - Keep pipeline tests and report-summary-adjacent tests.
   - Ensure temp-directory artifact expectations do not assume mutually exclusive file sets.

3. Ensure #11 reporting exports remain intact:
   - `skyjo_optimizer/ml/__init__.py` exports reporting symbols.
   - `skyjo_optimizer/ml/reporting.py` and `tests/test_reporting.py` are unchanged except conflict adjustments.

## Validation plan before final merge

Run, in order:

1. `pytest tests/test_cli_and_artifacts.py tests/test_reporting.py`
2. `pytest` (full suite)
3. Manual smoke checks:
   - `python -m skyjo_optimizer.cli pipeline --output-root <tmpdir>`
   - `python -m skyjo_optimizer.cli report-summary --artifacts-root <tmpdir> --output <tmpdir>/summary.csv`

## Rollback / safety notes

- If the combined CLI changes become too conflict-heavy, split merge into two commits during conflict resolution:
  1. Parser/dispatch reconciliation in `cli.py`
  2. Test reconciliation and fixture/output-path updates
- If needed, ship #12 first and gate #11 behind a quick follow-up PR that only reconciles conflicts and preserves original behavior.
