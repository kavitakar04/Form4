# PROJECT_STATE

_Last updated: 2026-04-17_

## Objective (Locked)
Build a reproducible event-study pipeline to estimate stock-market reaction to SEC Form 4 sell disclosures.

- Primary timing: filing date.
- Secondary timing (later): transaction date.
- Primary outcome: abnormal return (AR) and CAR.

## Current Stage
**Stage 0 — Methodology and schema lock (in progress, experiments blocked).**

## Completion Snapshot
### Complete
- Governance docs exist and are now coordinated under a repo-root `AGENTS.md`.
- Baseline objective, timing, and unit-of-analysis direction are documented.
- Baseline experiment contract exists with go/no-go acceptance criteria.

### Not Complete (Blocking Experiments)
- Methodology is not yet explicitly marked **Locked for Baseline**.
- Data dictionary open decisions are not yet explicitly resolved/locked.
- Pipeline scaffold and codebase structure are not yet implemented.

## Active Guardrails
1. No experiments before methodology + schema are locked and logged in `docs/DECISIONS.md`.
2. Any change to event definition/benchmark/outcomes/windows must be logged before implementation.
3. Reproducibility must be config-driven and artifact-traceable.

## Next 3 Implementation-Prep Tasks (Ordered)
1. **Pipeline/codebase skeleton**: create package layout, CLI entrypoints, config contracts, and test skeletons only (no ingestion/analysis execution).
2. **Schema lock task**: resolve open data dictionary decisions (ticker resolution, amended filing handling, economic-meaningful thresholds) and record lock in `docs/DECISIONS.md`.
3. **Execution contract task**: add runbook + stage-gate checklists for baseline E1 readiness (inputs/outputs/validation/repro metadata), still without running experiments.

## Key Risks (Still Active)
- Event contamination near filing windows.
- Sell-semantic ambiguity (derivative/mechanical dispositions).
- Timing ambiguity around after-hours filings.
- Dependence from clustered/repeated events.
