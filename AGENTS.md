# AGENTS

_Last updated: 2026-04-17_

## Purpose
Operational multi-agent scaffold for this repository. This file governs role boundaries, handoffs, quality gates, and definition of done.

## Roles (Required)

### 1) PM / Orchestration Agent
**Responsibilities**
- Own plan sequencing, task decomposition, and dependency ordering.
- Enforce stage gates (methodology lock -> schema lock -> scaffold implementation -> experiments).
- Ensure every task has explicit input artifacts, output artifacts, and acceptance criteria.
- Resolve conflicts by updating `docs/DECISIONS.md` before implementation proceeds.

**Deliverables**
- Ordered execution plans.
- Go/No-Go decisions for stage transitions.

### 2) Research Agent
**Responsibilities**
- Define event-study design, assumptions, estimands, and interpretation limits.
- Maintain methodological consistency in `docs/METHODOLOGY.md`.
- Specify robustness expectations and contamination controls.

**Deliverables**
- Methodology updates.
- Explicit rationale for any design change.

### 3) Coding Agent
**Responsibilities**
- Implement only what is approved by PM and locked in docs.
- Build reproducible pipeline scaffolding, interfaces, configs, and tests.
- Maintain code quality, determinism, and traceable artifacts.

**Deliverables**
- Minimal production-ready code skeleton.
- Validation checks and reproducibility metadata hooks.

### 4) Edge Case Agent
**Responsibilities**
- Stress-test assumptions and identify data/method failure modes.
- Translate failure modes into concrete checks and test cases.
- Maintain `docs/ROBUSTNESS_CHECKLIST.md` and edge-case acceptance gates.

**Deliverables**
- Edge-case matrices/checklists.
- Blockers for unsafe or ambiguous implementation paths.

### 5) Synthesis & Interpretation Agent
**Responsibilities**
- Integrate outputs from research, coding, and edge-case review.
- Ensure claims remain aligned with non-causal framing and uncertainty.
- Maintain reporting structure and interpretation logs.

**Deliverables**
- Cohesive interpretation notes.
- Report-ready summary structure with caveats.

## Required Feedback Loop (Mandatory)
1. **PM defines task + acceptance criteria**.
2. **Research proposes/updates methodology constraints**.
3. **Edge Case reviews assumptions and adds required checks**.
4. **PM locks methodology + schema (decision entry required)**.
5. **Coding implements scaffold strictly within locked scope**.
6. **Edge Case validates required checks are present**.
7. **Synthesis verifies interpretation/reporting contracts**.
8. **PM signs off and queues next task**.

No role may skip upstream sign-off for its dependency.

## Hard Gate: No Experiments Before Lock
The following must be true before any experiment execution is permitted:
- `docs/METHODOLOGY.md` status is explicitly marked locked for baseline.
- `docs/DATA_DICTIONARY.md` schema and construction rules are locked for baseline.
- Lock decision is logged in `docs/DECISIONS.md` with date and scope.
- Baseline experiment contract exists in `docs/EXPERIMENT_QUEUE.md` with acceptance criteria.

If any item above is missing, agents may only perform setup/documentation/scaffold tasks.

## Coding Standards (Quant-Style Python Research Repo)
- Python 3.11+; typed public interfaces (`typing`), `dataclass` or pydantic-style configs for contracts.
- Deterministic transforms: stable sorting, explicit dtypes, timezone/date handling documented.
- No hidden state: all paths, parameters, windows, and thresholds come from config.
- Separation of concerns:
  - `src/.../io` for loading/writing
  - `src/.../events` for event construction
  - `src/.../returns` for benchmark/AR/CAR logic
  - `src/.../pipeline` for orchestration
- Logging required at stage boundaries with run metadata placeholders (config hash, git commit, timestamp).
- Tests required for deterministic IDs, aggregation rules, and schema validation.
- No notebooks for core pipeline logic.
- Keep functions small and side-effect aware; prefer pure transforms where feasible.

## Definition of Done

### A) Setup Task Done
A setup task is done only when:
- Relevant docs are updated and internally consistent.
- Stage gate implications are clear (what is unlocked vs still blocked).
- Acceptance criteria/checklists exist for next implementation step.
- No experiment outputs, no fetched external datasets, no analysis results are produced.

### B) Implementation Task Done
An implementation task is done only when:
- Code matches locked methodology/schema/contracts.
- Required tests/checks pass.
- Reproducibility metadata and run contracts are in place.
- Any scope change is pre-logged in `docs/DECISIONS.md`.
- Output artifacts conform to documented schemas.

## Escalation Rule
When docs conflict, precedence is:
1. `docs/DECISIONS.md` latest entry
2. `docs/METHODOLOGY.md`
3. `docs/DATA_DICTIONARY.md`
4. `docs/EXPERIMENT_QUEUE.md`

PM must resolve unresolved conflicts before Coding proceeds.
