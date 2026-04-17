# DATA_DICTIONARY

_Last updated: 2026-04-17_
_Status: Draft v1.0_

## Purpose
Define canonical datasets and event schema required before baseline event-study implementation.

## Dataset Layers
- `data/raw/`: source files as ingested, immutable.
- `data/interim/`: parsed and normalized transactional records.
- `data/processed/`: analysis-ready event-level and return-join datasets.

## Core Tables

## 1) `form4_transactions_interim`
Line-item transactional records parsed from Form 4.

Minimum fields:
- `filing_id` (string): unique filing identifier.
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

## 2) `sell_events_processed`
Event-level filing observations (baseline unit of analysis).

Minimum fields:
- `event_id` (string): deterministic hash of issuer + filing_date + filing_id.
- `issuer_cik` (string)
- `issuer_ticker` (string)
- `filing_id` (string)
- `event_date` (date): filing date.
- `sell_txn_count` (int): number of qualifying sell line items in filing.
- `sell_shares_total` (float)
- `sell_notional_total` (float, nullable)
- `sell_intensity_metric` (float, nullable)
- `clean_sell_flag` (bool): passes baseline inclusion filters.
- `exclusion_reason` (string, nullable)

## 3) `event_returns_processed`
Trading-day return panel around each event.

Minimum fields:
- `event_id` (string)
- `trade_date` (date)
- `event_time` (int): trading day offset from event date.
- `raw_return` (float)
- `benchmark_return` (float)
- `abnormal_return` (float)

## Event Construction Rules (Draft)
1. Start from `form4_transactions_interim`.
2. Retain candidate sell rows using transaction semantics rules in methodology.
3. Aggregate candidate rows to one filing-level event (`sell_events_processed`).
4. Mark `clean_sell_flag = true` only if inclusion criteria pass and no hard exclusion applies.

## Required Quality Checks
- Uniqueness: `event_id` unique in `sell_events_processed`.
- Determinism: identical inputs produce identical `event_id` and aggregate values.
- Traceability: each event maps back to originating `filing_id` and transaction rows.
- Missingness logs: null rates reported for price/notional-critical fields.

## Open Schema Decisions to Lock Before Baseline
- Canonical rule for ticker resolution when filing ticker is missing.
- Exact handling of amended filings.
- Thresholds for minimum notional/shares to classify as economically meaningful sell events.
