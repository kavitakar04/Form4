# EXPERIMENT_QUEUE

_Last updated: 2026-04-17_
_Status: Defined, execution blocked until methodology + schema lock_

## Stage Gate (Applies to all experiments)
Do not run experiments until:
- Methodology lock recorded.
- Data schema lock recorded.
- Pipeline scaffold + validation checks exist.

## Baseline Experiment Contract (E1)
**Name:** Filing-date event study for clean sell events.

### Objective
Estimate average abnormal return response around filing date for baseline clean-sell sample.

### Inputs (required)
- Locked `docs/METHODOLOGY.md`.
- Locked `docs/DATA_DICTIONARY.md`.
- `sell_events_processed` with `clean_sell_flag = true`.
- Event-aligned return and benchmark data.
- Config declaring sample period and event windows.

### Outputs (required)
- AR/CAR summary table by window (SE/CI included).
- Sample attrition table by filter step.
- Mean CAR path figure over event time.
- Run metadata log (config hash, timestamp, git commit).

### Acceptance Criteria (Go/No-Go)
1. Reproducibility: identical outputs on rerun with identical config.
2. Data integrity: no duplicate `event_id`; no broken event-return joins.
3. Method compliance: windows/events match locked methodology.
4. Edge-case minimum checks satisfied (`docs/ROBUSTNESS_CHECKLIST.md`).
5. Interpretation note appended to `docs/RESULTS_LOG.md` with non-causal framing.

## Planned Follow-On (Not approved)
- E2: Transaction-date timing decomposition.
- E3: Benchmark robustness (market model / factor variants).
- E4: Subsample heterogeneity (role, intensity, size).
