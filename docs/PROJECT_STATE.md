# PROJECT_STATE

_Last updated: 2026-04-17_

## Objective (Locked)
Build a reproducible research pipeline to estimate stock-market reaction to **SEC Form 4 sell disclosures**, with:
- Primary event timing: **filing date**.
- Secondary timing analysis: **transaction date**.
- Primary outcome: **abnormal return**.

## Current Stage
**Stage 0 — Study design hardening (in progress).**

### What is complete
- High-level research objective and role model are defined in project brief.
- Core sequencing rule is defined: methodology before experiments.

### What is not yet complete
- No prior docs were present in repository at project start; no existing methodology constraints were codified in repo files.
- Event definitions and filtering logic are not yet encoded in a data dictionary/schema.
- Experiment interface (inputs, outputs, acceptance gates) is not yet fully specified.

## Scope Guardrails (Active)
1. No coding experiments until methodology and schemas are locked.
2. Any change to event definition/benchmark/outcomes must first update `docs/METHODOLOGY.md` and be logged in `docs/DECISIONS.md`.
3. All accepted logic must be reproducible from config and saved outputs.

## Immediate Priorities (Ordered)
1. Finalize methodology document sections required to constrain baseline event study.
2. Finalize event/data dictionary with inclusion-exclusion semantics.
3. Finalize experiment contract and acceptance criteria before implementation.

## Risks and Open Questions
- **Event contamination risk:** same-day confounding corporate or macro events may bias estimated reaction.
- **Transaction ambiguity risk:** derivative-related or non-economic dispositions may be misclassified as sells.
- **Timing risk:** after-hours filings can blur t=0 return measurement.
- **Overlap risk:** clustered insider events and repeated filings can induce dependence.

## Next 3 Setup Tasks (Approved Queue)
1. Draft a complete `docs/METHODOLOGY.md` v1.0 with locked baseline choices and explicit interpretation limits.
2. Draft `docs/DATA_DICTIONARY.md` v1.0 defining event-level unit of analysis and transaction-to-event aggregation rules.
3. Draft `docs/EXPERIMENT_QUEUE.md` v1.0 with baseline experiment contract, required diagnostics, and go/no-go acceptance checks.
