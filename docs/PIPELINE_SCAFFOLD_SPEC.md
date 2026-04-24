# PIPELINE_SCAFFOLD_SPEC

_Last updated: 2026-04-17_
_Status: Setup-only specification (no data logic implemented)_

## Goal
Define the initial codebase skeleton and interfaces required before any ingestion, event construction, or experiment runs.

## Planned Directory Skeleton
```text
src/form4_research/
  __init__.py
  config/
    schema.py
  io/
    interfaces.py
  events/
    interfaces.py
  returns/
    interfaces.py
  pipeline/
    run_baseline.py
  validation/
    checks.py

configs/
  baseline.yaml

tests/
  test_event_id_determinism.py
  test_schema_contracts.py
  test_pipeline_contract.py
```

## Interface Contracts (Setup Only)
- `config/schema.py`: typed config objects + validation for windows/dates.
- `io/interfaces.py`: load/save protocol definitions (no external calls yet).
- `events/interfaces.py`: event construction function signatures + expected DataFrame schema.
- `returns/interfaces.py`: abnormal-return/CAR function signatures + expected schema.
- `pipeline/run_baseline.py`: CLI entrypoint wiring with dry-run mode.
- `validation/checks.py`: schema and determinism check stubs.

## Non-Goals
- No ingestion from SEC or market sources.
- No parsing logic.
- No experiment execution.
- No notebook creation.

## Acceptance Criteria
- Skeleton imports resolve.
- CLI dry-run prints stage plan only.
- Tests exist for interface and schema contracts (may initially validate placeholders).
