# DATA_DICTIONARY

_Last updated: 2026-04-17_
_Status: Draft v1.1 (schema defined; lock pending open decisions)_

## Purpose
Define canonical datasets and baseline schema contracts required before implementation and experiments.

## Dataset Layers
- `data/raw/`: immutable source snapshots.
- `data/interim/`: parsed/normalized transaction-level records.
- `data/processed/`: analysis-ready event-level and event-return records.

## Core Tables

### 1) `form4_transactions_interim`
Minimum fields:
- `filing_id` (string)
- `issuer_cik` (string)
- `issuer_ticker` (string, nullable)
- `reporting_owner_id` (string, nullable)
- `filing_date` (date)
- `transaction_date` (date, nullable)
- `security_title` (string)
- `transaction_code` (string)
- `shares` (float)
- `price_per_share` (float, nullable)
- `ownership_nature` (string, nullable)
- `is_derivative` (bool)
- `raw_disposition_flag` (string, nullable)
- `is_amendment` (bool, required for amendment policy)

### 2) `sell_events_processed`
Minimum fields:
- `event_id` (string; deterministic hash of issuer + filing_date + filing_id)
- `issuer_cik` (string)
- `issuer_ticker` (string)
- `filing_id` (string)
- `event_date` (date; filing date)
- `sell_txn_count` (int)
- `sell_shares_total` (float)
- `sell_notional_total` (float, nullable)
- `sell_intensity_metric` (float, nullable)
- `clean_sell_flag` (bool)
- `exclusion_reason` (string, nullable)

### 3) `event_returns_processed`
Minimum fields:
- `event_id` (string)
- `trade_date` (date)
- `event_time` (int; trading-day offset)
- `raw_return` (float)
- `benchmark_return` (float)
- `abnormal_return` (float)

## Event Construction Rules
1. Start from `form4_transactions_interim`.
2. Identify candidate sell rows using locked methodology semantics.
3. Aggregate to filing-level event in `sell_events_processed`.
4. Set `clean_sell_flag = true` only when all inclusion checks pass and no hard exclusion applies.

## Required Quality Checks
- Uniqueness: `event_id` unique in `sell_events_processed`.
- Determinism: identical inputs -> identical IDs/aggregates.
- Traceability: each event maps back to transaction rows.
- Missingness logging for key fields (price/notional/identifier).

## Open Decisions (Must Lock Before Implementation)
- Canonical ticker resolution when filing ticker is missing.
- Amendment handling policy (`is_amendment`).
- Thresholds (if any) for economically meaningful sell-event classification.

## Schema Lock Checklist
Schema is considered locked only when:
- [ ] Open decisions above are resolved in this file.
- [ ] Field-level nullability is finalized for baseline pipeline.
- [ ] Event ID recipe is frozen and testable.
- [ ] Lock decision is recorded in `docs/DECISIONS.md`.
