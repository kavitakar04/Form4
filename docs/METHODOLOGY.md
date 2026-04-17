# METHODOLOGY

_Last updated: 2026-04-17_
_Status: Draft v1.0 (intended to constrain baseline implementation)_

## 1) Research Question
What is the short-horizon stock-price reaction to **economically meaningful insider sell disclosures** reported on SEC Form 4?

## 2) Impact Definition (Primary)
Impact is defined as **abnormal return (AR)** and cumulative abnormal return (CAR) around an event date.

- Event-time abnormal return: \(AR_{i,t} = R_{i,t} - E[R_{i,t}|\text{benchmark}]\)
- Window CAR: sum of ARs over predefined windows.

## 3) Event Timing Strategy
### Primary timing (locked)
- **Event date = filing date** (Form 4 disclosure date).

### Secondary timing (planned robustness)
- **Transaction date** analysis to decompose anticipation vs disclosure effects.

## 4) Unit of Analysis (Baseline)
**Event-level filing observation** per issuer per filing date, constructed from one or more qualifying sell line items in that filing.

Rationale:
- Aligns with public disclosure timing.
- Avoids overweighting filings with many small line items.

## 5) Sample Inclusion / Exclusion Principles
### Include (baseline)
- Common-equity related insider sell disclosures with clear economic disposition semantics.
- Issuers with valid price history spanning estimation and event windows.

### Exclude (baseline)
- Transactions flagged as derivative conversions/exercises without clear open-market sell intent.
- Purely mechanical/non-discretionary dispositions where economic signal is ambiguous.
- Events with missing or invalid security/issuer identifiers needed for pricing joins.

## 6) Benchmark for Expected Returns (Baseline)
Baseline expected-return model: **market-adjusted return** (broad market proxy).

Planned robustness (not baseline):
- Market model estimated on pre-event window.
- Size/value/momentum factor variants.

## 7) Event Windows (Baseline Set)
- Primary: [0, +1]
- Supporting: [-1, +1], [0, +2], [-2, +2]

Where day 0 is filing date in trading-day time.

## 8) Estimation Window
For model-based robustness (e.g., market model), use pre-event estimation period excluding contamination buffer near event date. Exact bounds to be locked in config before running baseline.

## 9) Confounds and Contamination Controls
Must document and monitor:
- Earnings announcements near event windows.
- Major firm-specific news and corporate actions.
- Overlapping insider filings and repeated-event clustering.
- Market-wide stress days that can dominate idiosyncratic reaction.

## 10) Inference and Dependence
Use inference that acknowledges cross-sectional/event-time dependence (e.g., clustered or robust standard errors). Final method selection must be logged before baseline result acceptance.

## 11) Interpretation Limits
- Estimated effects are **associational**, not necessarily causal.
- Filing-date results capture disclosure reaction; they do not separately identify information leakage unless secondary timing tests support it.
- Magnitude interpretation must report economic units (bps) and uncertainty intervals.

## 12) Change Control
Any change to:
- Event definition
- Return benchmark
- Outcome variables
- Window definitions

must be recorded in `docs/DECISIONS.md` before new experiments are accepted.
