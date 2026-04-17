# PIPELINE

_Last updated: 2026-04-17_

## Baseline event-return build step (implemented)

Command:

```bash
python -m form4_pipeline.run_event_returns \
  --events data/processed/sell_events_processed.csv \
  --market data/processed/market_benchmark_prepared.csv \
  --config config/baseline_event_windows.json \
  --output-dir data/processed \
  --run-tag baseline_event_returns
```

### Inputs
- `sell_events_processed` rows where `clean_sell_flag = true`.
- Prepared issuer-level trading returns joined with benchmark returns.
- Locked baseline window config (`[-1,+1]`, `[-2,+2]`, `[0,+1]`, `[0,+2]`).

### Outputs
- `data/processed/event_returns_processed.csv`: event-by-trading-day panel with event-time offsets and abnormal returns.
- `data/processed/event_cars_processed.csv`: event-level CAR by configured window.
- `data/processed/event_returns_manifest.json`: deterministic metadata manifest with row counts and run metadata.

### Alignment rule implemented
- Event day 0 is the first trading date on or after filing `event_date`.
- Event-time offsets are defined in trading days around day 0.
