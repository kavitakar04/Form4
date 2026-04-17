# EXPERIMENT_QUEUE

_Last updated: 2026-04-17_

## Baseline Experiment Contract (E1)
**Name:** Filing-date event study for clean sell events.

### Objective
Estimate average abnormal return response around filing date for baseline clean sell sample.

### Inputs (required)
- Locked `METHODOLOGY.md` v1.x.
- `sell_events_processed` with `clean_sell_flag = true`.
- Trading return data and market benchmark aligned to event panel.
- Config specifying event windows and sample period.

### Outputs (required)
- Table: AR/CAR by event window with standard errors and confidence intervals.
- Table: sample counts and attrition by filter step.
- Figure: mean CAR path over event time.
- Log: run metadata (config hash, timestamp, git commit).

### Acceptance Criteria (go/no-go)
1. Reproducibility: rerun with same config reproduces identical tables/figures.
2. Data integrity: no duplicate `event_id`, no broken joins in event-return panel.
3. Method compliance: event definition and windows match `METHODOLOGY.md`.
4. Edge-case review completed against `ROBUSTNESS_CHECKLIST.md` minimum set.
5. Interpretation note entered in `RESULTS_LOG.md` with limits and non-causal framing.

## Planned Follow-On (Not Yet Approved)
- E2: Transaction-date timing decomposition.
- E3: Benchmark robustness (market model / factor variants).
- E4: Subsample heterogeneity (insider role, sell intensity, firm size).
