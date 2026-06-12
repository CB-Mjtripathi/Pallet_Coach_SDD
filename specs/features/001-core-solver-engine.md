# Feature: Core Solver Engine

**Feature ID:** RF-001
**Status:** Implemented
**Priority:** Critical
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Sections 1, 3, 4, 9, 10, 12)

---

## Overview

This feature defines the deterministic pallet pattern solver that is the computational core of Pallet Coach. It covers geometric enumeration, tolerance validation, ranking, impossible-case handling, and mandatory metric generation for every candidate solution.

The solver is constrained to Step 1 MVP semantics: single SKU, upright-only case placement, grid patterns as first-class outputs, optional interlock generation, and deterministic ranking that is reproducible across identical inputs.

---

## User Stories

### US-1.1: Enumerate feasible pallet patterns

**As a** logistics engineer  
**I want to** enumerate all feasible grid layouts for a case and pallet geometry  
**So that** I can identify the highest-throughput case-per-layer arrangement

**Acceptance Criteria:**
- ✅ Solver enumerates all distinct `(nx, ny, rotation)` combinations within tolerance semantics.
- ✅ `rotation_deg` includes `0` and `90` only when `allow_rotation_90=true`.
- ✅ All placements are upright-only with `case.height_mm` fixed as vertical.
- ✅ No output layout contains overlapping case rectangles.
- ✅ If `allow_interlock=true`, interlock variants are produced and labeled with `_interlock`.

**Technical Details:**
- Module: `scripts/pallet_coach/solver.py`
- Core policy: grid-only in Step 1, with optional experimental interlock branch
- Coordinates: origin at bottom-left, x along pallet length, y along pallet width
- Internal unit: mm only

---

### US-1.2: Enforce tolerance and anchoring rules

**As a** supply chain analyst  
**I want to** validate overhang/underhang consistently  
**So that** accepted patterns match site compliance logic

**Acceptance Criteria:**
- ✅ Per-side overhang checks are applied using left/right and top/bottom formulas.
- ✅ Underhang anchoring checks apply `min(side_a, side_b)` per axis.
- ✅ Default tolerances are used when fields are omitted.
- ✅ `auto_underhang=true` overrides explicit underhang fields for the selected winning pattern.
- ✅ Only `tolerance_pass=true` solutions are included in ranked output.

**Technical Details:**
- Tolerance formulas exactly as defined in requirement.md section 3.3
- Computed fields include `edge_clearance_mm` and `tolerance_pass`

---

### US-1.3: Return deterministic ranked recommendations

**As an** operations manager  
**I want to** receive a deterministic ranking of valid options  
**So that** decisions are transparent and reproducible

**Acceptance Criteria:**
- ✅ Ranking is by `cases_per_layer` desc, then `area_fill_efficiency_pct` desc.
- ✅ Returns `status="ok"` with ranked options when feasible.
- ✅ Returns `status="impossible"` with reason codes when no feasible patterns exist.
- ✅ Supports default max output 25 and hard API cap 250.
- ✅ Computes all mandatory metrics in requirement.md section 3.6.

**Technical Details:**
- Entry point: `scripts/pallet_coach/recommender.py` via `recommend(req, max_options=25)`
- Solver delegation: recommender calls `solver.solve()`
- Impossible reason codes: `NO_FEASIBLE_PATTERN`, `CASE_LARGER_THAN_PALLET_WITH_TOLERANCE`, `LAYER_COUNT_INVALID`

---

## Dependencies

### Prerequisites
- Contract parsing and validation (`scripts/pallet_coach/contracts.py`)
- Stacking policy logic (`scripts/pallet_coach/stacking.py`)

### Related Features
- RF-002 API & run management consumes solver outputs
- RF-003 artifact pipeline renders diagrams from solver layouts
- RF-007 test harness validates solver correctness

---

## Technical Architecture

### Components Involved
- `contracts.py`: strict input validation and defaults
- `solver.py`: geometric enumeration and metric computation
- `recommender.py`: public recommendation API surface
- `stacking.py`: policy-based height/weight layer analysis

### Data Flow
1. Parse and validate canonical request.
2. Enumerate candidate layouts for allowed rotations/interlock mode.
3. Compute metrics and tolerance pass/fail for each layout.
4. Filter to passing solutions and rank deterministically.
5. Return `ok` or `impossible` payload.

### APIs & Integrations
- Internal integration via Python function calls only for this feature.

---

## Non-Functional Requirements

### Performance
- `/api/solve` path including solver branch must satisfy 10-second typical target.

### Security
- Deterministic pure-compute path with no secret access.

### Scalability
- Solver algorithm should remain modular for Phase 2 expansion (non-grid and mixed SKU).

---

## Implementation Notes

- Keep solver deterministic: avoid non-deterministic iteration order when sorting equivalent candidates.
- Preserve exact field names in contracts and bundle schema for downstream compatibility.

---

## Test Coverage

### Unit Tests Required
- `test_solver_centered_strict_tolerances.py`
- Impossible-case reason code validation
- Rotation-required case with `allow_rotation_90=true`

### UAT Tests Required
- Perfect-fit pallet/case scenario
- Underhang-bound scenario using anchoring rules

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 3 (Business rules and domain logic)
- Attached: `requirement.md` section 4 (Backend solver requirements)
- Attached: `requirement.md` section 9 (Data contracts)
- Attached: `requirement.md` section 12 (Testing)

**Related ADRs:**
- None yet (to be created during architecture implementation)

**Implementation Files:**
- `scripts/pallet_coach/contracts.py`
- `scripts/pallet_coach/solver.py`
- `scripts/pallet_coach/recommender.py`
- `scripts/pallet_coach/stacking.py`

---

## Open Questions

- None. Requirements are explicit for Step 1 MVP.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** specs/implementation-plans/RF-001-core-solver-engine-implementation-plan.md

**Files Created:**
- scripts/pallet_coach/__init__.py
- scripts/pallet_coach/errors.py
- scripts/pallet_coach/models.py
- scripts/pallet_coach/contracts.py
- scripts/pallet_coach/stacking.py
- scripts/pallet_coach/solver.py
- scripts/pallet_coach/recommender.py
- scripts/tests/__init__.py
- scripts/tests/test_solver_centered_strict_tolerances.py
- scripts/tests/test_stacking_model.py
- scripts/tests/test_layer_count_exceedance_highlight.py
- scripts/requirements.txt
- eval/test_cases.json
- eval/run_eval.py
- samples/R1_perfect_fit/bundle.json
- samples/R13_underhang_tolerance/bundle.json

**Validation:**
- Unit tests: 11 passed
- Evaluation harness: 4 passed
- Total checks: 15 passed, 0 failed
