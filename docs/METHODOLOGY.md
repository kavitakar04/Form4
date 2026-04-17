# METHODOLOGY

_Last updated: 2026-04-17_
_Status: Draft v1.1 (baseline constraints defined; final lock pending schema decisions)_

## 1) Research Question
What is the short-horizon stock-price reaction to economically meaningful insider sell disclosures reported on SEC Form 4?

## 2) Outcome Definition (Baseline)
- Event-time abnormal return: `AR_{i,t} = R_{i,t} - E[R_{i,t}|benchmark]`
- Window-level CAR: sum of AR over predefined event windows.

## 3) Event Timing
- **Primary (baseline):** event date = filing date.
- **Secondary (future robustness):** transaction-date timing decomposition.

## 4) Unit of Analysis (Baseline)
One filing-level event per issuer per filing date per filing ID, aggregated from qualifying sell line items.

## 5) Inclusion / Exclusion Principles
### Include
- Common-equity related sells with clear economic disposition semantics.
- Events with valid identifiers and pricing coverage for required windows.

### Exclude
- Derivative conversions/exercises without clear open-market sell intent.
- Mechanical/non-discretionary dispositions with ambiguous signal.
- Events missing required identifiers for deterministic pricing joins.

## 6) Expected Return Benchmark
- **Baseline:** market-adjusted return with broad market proxy.
- **Planned robustness:** market-model and factor variants (post-baseline).

## 7) Event Windows (Baseline Set)
- Primary: `[0, +1]`
- Supporting: `[-1, +1]`, `[0, +2]`, `[-2, +2]`

(Trading-day indexing; day 0 is filing date.)

## 8) Estimation Window (for robustness models)
Use a pre-event estimation period with a contamination buffer near day 0. Exact bounds must be defined in config before robustness runs.

## 9) Confounds to Track
- Earnings announcements near window.
- Major firm-specific news/corporate actions.
- Overlapping insider events.
- Market stress days.

## 10) Inference Requirement
Inference must acknowledge event-time/cross-sectional dependence (robust/clustered approach). Final baseline choice must be logged in `docs/DECISIONS.md`.

## 11) Interpretation Limits
- Baseline estimates are associational, not inherently causal.
- Filing-date design identifies disclosure reaction, not leakage by itself.
- Report effect sizes in bps with uncertainty intervals.

## 12) Change Control
Changes to event definitions, benchmarks, windows, or outcomes require a decision log update before implementation/acceptance.

## 13) Baseline Lock Checklist
Baseline methodology is considered locked only when:
- [ ] Inclusion/exclusion semantics are mapped 1:1 to fields in `docs/DATA_DICTIONARY.md`.
- [ ] Inference approach for baseline reporting is chosen.
- [ ] Any unresolved ambiguity is documented with explicit fallback handling.
- [ ] Lock decision is recorded in `docs/DECISIONS.md`.
