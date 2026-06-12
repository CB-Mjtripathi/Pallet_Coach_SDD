# Implementation Plan: Core Solver Engine
**Feature ID:** RF-001  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** FROM SCRATCH

---

## Executive Summary

**Feature:** Core Solver Engine  
**Status:** Not Implemented  
**Implementation Approach:** FROM SCRATCH  
**Estimated Complexity:** High  
**Risk Level:** Medium

**Summary:**
The workspace currently contains requirement and feature documentation but no backend or frontend implementation code. RF-001 must be implemented from scratch by creating the full `scripts/pallet_coach/` Python package structure for contracts parsing, deterministic solver logic, stacking policy analysis, and recommendation orchestration. The implementation must preserve strict mathematical determinism, exact contract field names, and tolerance semantics, and must be accompanied by unit tests and evaluation fixtures.

---

## Table of Contents
1. Feature Analysis
2. Implementation Status
3. Impact Analysis
4. Development Plan
5. Testing Strategy
6. Developer Checklist

---

## Feature Analysis

### Feature Overview
- **Feature ID:** RF-001
- **Feature Name:** Core Solver Engine
- **Priority:** Critical
- **Complexity:** High

### Scope Summary
RF-001 implements deterministic single-layer pallet layout enumeration for single-SKU, upright-only cases with optional 90-degree rotation and optional interlock variants. It applies overhang and underhang tolerance rules, computes required per-solution metrics, filters to tolerance-pass candidates, and ranks results deterministically.

The feature also includes contract validation defaults and stacking policy analysis support needed for downstream outputs. The recommender interface provides a stable entry point for API and artifact layers.

### Key Requirements
1. Enumerate all distinct feasible grid patterns `(nx, ny, rotation)` under tolerance rules.
2. Support `rotation_deg` values `0` and `90` only when `allow_rotation_90=true`.
3. Keep `case.height_mm` upright (no tilt/tipping orientation handling in Step 1).
4. Generate optional interlock variants labeled with `_interlock` when enabled.
5. Apply exact overhang and underhang formulas and anchoring semantics.
6. Apply default tolerance values when omitted.
7. Honor `auto_underhang` behavior for winning pattern selection semantics.
8. Rank by `cases_per_layer` descending, then `area_fill_efficiency_pct` descending.
9. Return `status="impossible"` with approved reason codes when no feasible layouts exist.
10. Compute all mandatory metrics, including `inner_axis_segments_mm`.
11. Expose `recommend(req, max_options=25)` delegating into `solver.solve()`.

### User Stories Summary
- **US-1.1:** Enumerate feasible grid patterns with optional rotation/interlock and no overlap.
- **US-1.2:** Enforce tolerance and anchoring rules consistently with defaults and auto-underhang behavior.
- **US-1.3:** Return deterministic ranked recommendations with complete metric payload and impossible handling.

### Technical Specifications
- **APIs Required:** Internal Python module API only (`recommend`, `solve`, `parse_contract`, stacking analysis helpers).
- **Data Models:** Canonical request dataclasses/dicts for pallet, case, stack, tolerances, constraints; solution and metrics models.
- **Integrations:** No external API for RF-001 itself.
- **Performance:** Solver branch must support `/api/solve` 10-second target for typical MVP input volume.

### Dependencies
- **Prerequisites:** None in code (feature is foundational).
- **Integration Points:** RF-002 API, RF-003 diagrams/artifacts, RF-007 tests/eval harness.

### Complexity Assessment
- **Estimated Complexity:** High
- **Reasoning:**
  - Number of user stories: 3
  - Number of modules involved: 4 primary modules + shared model helpers
  - External integrations: 0
  - Data model complexity: Moderate to high (nested structures and strict schemas)
  - UI complexity: None in this feature
  - Algorithmic correctness constraints are strict and sensitive to rounding/deterministic ordering

---

## Implementation Status

## Search Results Analysis

### Files Found

#### Backend Services
- No `scripts/**/*.py` implementation files found.
- No `scripts/pallet_coach/` package found.

#### UI Components
- No `UI/` implementation tree found.

#### Data Models
- No backend model or schema files found.

### Summary of Findings
- **Total implementation files for RF-001 found:** 0
- **Highly relevant implementation files:** 0
- **Partially relevant implementation files:** 0
- **Documentation-only references found:** Yes (`requirement.md`, `specs/features/*.md`)

## Implementation Status: Not Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-1.1 | Not Implemented | None | Full solver engine required |
| US-1.2 | Not Implemented | None | Full tolerance/contract logic required |
| US-1.3 | Not Implemented | None | Full recommender/status handling required |

### Coverage Summary
- **Implemented:** 0 / 3 user stories (0%)
- **Partially Implemented:** 0
- **Not Implemented:** 3

### Recommendation
- **Primary Approach:** FROM SCRATCH
- **Reasoning:** No code artifacts exist for solver, contracts, stacking, or recommender modules.

## Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|---------------------|---------------|--------|
| Enumerate feasible layouts | Distinct `(nx, ny, rotation)` candidates | None | Missing |
| Enforce tolerance semantics | Per-side overhang + anchored underhang | None | Missing |
| Deterministic ranking | `cases_per_layer`, then `efficiency` | None | Missing |
| Impossible response handling | Approved reason codes | None | Missing |
| Metric computation block | Full section 3.6 metrics | None | Missing |
| Recommender entrypoint | `recommend(req, max_options=25)` | None | Missing |

---

## Impact Analysis

## Affected Modules

### Services Layer
- **File:** `scripts/pallet_coach/contracts.py`
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Contract validation, defaults, type safety, reason-code alignment.

- **File:** `scripts/pallet_coach/solver.py`
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Core enumeration, tolerance checks, metrics, ranking.

- **File:** `scripts/pallet_coach/stacking.py`
  - **Change Type:** New File
  - **Impact Level:** Medium
  - **Reason:** Height/weight ceilings and recommendation range computations required by outputs.

- **File:** `scripts/pallet_coach/recommender.py`
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Stable orchestration API for downstream features.

### Data Models
- **File:** `scripts/pallet_coach/models.py`
  - **Change Type:** New File
  - **Impact Level:** Medium
  - **Reason:** Shared dataclasses/typed dicts to prevent schema drift.

### Package Setup
- **File:** `scripts/pallet_coach/__init__.py`
  - **Change Type:** New File
  - **Impact Level:** Low

- **File:** `scripts/pallet_coach/errors.py`
  - **Change Type:** New File
  - **Impact Level:** Low
  - **Reason:** `ContractError` and typed domain exceptions.

### Testing
- **File:** `scripts/tests/test_solver_centered_strict_tolerances.py`
  - **Change Type:** New File
  - **Impact Level:** High

- **File:** `scripts/tests/test_stacking_model.py`
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `scripts/tests/test_layer_count_exceedance_highlight.py`
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `eval/run_eval.py`
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `eval/test_cases.json`
  - **Change Type:** New File
  - **Impact Level:** Medium

## Integration Points

### Internal Dependencies
- RF-001 outputs become direct input for RF-002 `/api/solve` response and `bundle.json` construction.
- RF-003 depends on layout coordinates, `inner_axis_segments_mm`, and `edge_clearance_mm` fields.
- RF-005 expects solution metrics and stacking fields for options and stacking tables.

### Data Flow
1. Contract parser validates and normalizes canonical request.
2. Solver enumerates layouts and computes metric payloads.
3. Recommender filters/ranks and returns top-N or impossible payload.
4. Stacking module computes layer policy and warnings for bundle block.

## Features That Must NOT Be Impacted

Current repository has no runtime implementation; therefore preservation target is schema and requirement compatibility:
1. Requirement semantics in `requirement.md` must remain unchanged in implementation behavior.
2. Field names and bundle paths declared in `specs/features/*.md` must be preserved exactly.
3. Future RF-002..RF-008 modules must be able to consume outputs without contract translation layer.

## Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Code Complexity | Medium | Multiple metric and tolerance formulas with strict semantics | Centralize formulas; add unit tests per formula |
| Integration Points | Medium | Downstream features depend on exact field names | Define typed models and golden tests |
| Data Model Changes | Medium | Early schema drift can cascade into UI/API regressions | Lock schema in tests and sample fixtures |
| External Dependencies | Low | No provider calls in RF-001 | Keep pure Python logic isolated |
| Test Coverage Gap | High | Zero tests currently exist | Implement mandatory test set before feature sign-off |
| Feature Coupling | Medium | RF-001 is foundational | Stable public interfaces, avoid premature refactor |

### Specific Risks

#### Risk 1: Tolerance Semantics Implemented Incorrectly
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Encode formulas exactly once in helper functions.
  - Add targeted tests for side-specific overhang and anchored underhang behavior.
  - Add impossible-case fixtures for edge values.
- **Contingency:** Freeze API integration until formula test suite passes.

#### Risk 2: Non-Deterministic Ranking Output
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Explicit stable sort tuple and tie-breaking fallback by deterministic key.
  - Avoid set/dict iteration order in candidate generation outputs.
- **Contingency:** Add snapshot regression tests for sorted `solution_id` order.

#### Risk 3: Missing Mandatory Metrics Causes Downstream Failures
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Define strict `SolutionMetrics` model and constructor with completeness checks.
  - Validate keys before response emission.
- **Contingency:** Fail fast with explicit error and add schema conformance tests.

---

## Development Plan

## Implementation Approach: FROM SCRATCH

### Rationale
RF-001 has zero implementation footprint in the current repository. The fastest safe path is to create the canonical `scripts/pallet_coach` package with strict contracts and tests, matching requirement formulas and output schemas.

### Strategy Summary
- **New Components:** 13
  - Package/module files, tests, eval harness, sample fixtures
- **Modified Components:** 0
- **Unchanged Components:** All existing docs and agent files

## Files to CREATE

### 1. Core Package and Models

#### File: `scripts/pallet_coach/__init__.py`
Purpose: package export surface.

#### File: `scripts/pallet_coach/errors.py`
Purpose: domain errors (`ContractError`, `SolverError`).

Suggested structure:
- `class ContractError(ValueError):` include optional `details` dict.
- `class SolverError(RuntimeError):` optional reason code.

#### File: `scripts/pallet_coach/models.py`
Purpose: typed request/response and metric dataclasses.

Minimum dataclasses/typed structures:
- `PalletInput(type, length_mm, width_mm)`
- `CaseInput(length_mm, width_mm, height_mm, weight_kg=None)`
- `StackInput(layer_count)`
- `ToleranceInput(max_overhang_l_mm, max_overhang_w_mm, max_underhang_l_mm, max_underhang_w_mm)`
- `ConstraintInput(allow_rotation_90, allow_interlock, auto_underhang, max_pallet_weight_kg=None)`
- `SolveRequestNormalized(...)`
- `Placement(x_mm, y_mm, rotation_deg, dim_x_mm, dim_y_mm)`
- `EdgeClearance(left_mm, right_mm, bottom_mm, top_mm)`
- `SolutionMetrics(...)`
- `Solution(solution_id, layout, metrics)`
- `SolverResult(status, reasons, solutions)`
- `StackingAnalysis(...)`

### 2. Contract Parsing

#### File: `scripts/pallet_coach/contracts.py`
Purpose: validate and normalize incoming request contract.

Implement:
- `DEFAULT_TOLERANCES` constants:
  - `max_overhang_l_mm=0`
  - `max_overhang_w_mm=0`
  - `max_underhang_l_mm=20`
  - `max_underhang_w_mm=20`
- `parse_request(payload: dict) -> SolveRequestNormalized`
- `validate_positive_int(field_name, value, min_value=1)`
- Raise `ContractError` with field-specific details.

Validation minimums:
- pallet length/width >= 1
- case length/width/height >= 1
- stack.layer_count >= 1
- constraints and tolerance object defaults applied when absent

### 3. Stacking Policy Module

#### File: `scripts/pallet_coach/stacking.py`
Purpose: compute stacking guidance block and warnings.

Implement:
- Constants:
  - `MAX_STACK_HEIGHT_MM = 2000`
  - `PALLET_HEIGHT_MM_DEFAULT = 144`
  - `PALLET_TARE_KG = {"euro": 25, "industrial": 30, "custom": 25}`
- `compute_stacking_analysis(req: SolveRequestNormalized, cases_per_layer: int) -> StackingAnalysis`

Required formulas:
- `available_load_height = max_stack_height_mm - pallet_height_mm`
- `height_ceiling_layers = floor(available_load_height / case.height_mm)`
- If weight data present:
  - `weight_ceiling_layers = floor((max_pallet_weight_kg - pallet_tare_kg) / (cases_per_layer * case.weight_kg))`
- `effective_ceiling_layers = min(height_ceiling_layers, weight_ceiling_layers)` when both exist
- `recommended_layers_range = [current_layers + 1 .. min(current_layers + 3, effective_ceiling)]`
- `current_stack_height_mm = pallet_height_mm + current_layers * case.height_mm`
- `headroom_mm = max_stack_height_mm - current_stack_height_mm`

Warning logic:
- height exceed warning when current stack height > 2000
- weight-restrictive warning when weight ceiling < height ceiling

### 4. Solver Module

#### File: `scripts/pallet_coach/solver.py`
Purpose: enumerate feasible layouts and compute deterministic ranking payloads.

Implement public entrypoint:
- `solve(req: SolveRequestNormalized, max_options: int = 25) -> SolverResult`

Internal helpers:
- `_rotation_options(req)` returns `[0]` or `[0, 90]`
- `_grid_counts(pallet_dim_mm, case_dim_mm, max_overhang_mm)` candidate count generator
- `_build_grid_layout(nx, ny, case_dim_x, case_dim_y, rotation_deg, interlock=False)`
- `_compute_footprint_bbox(layout)`
- `_compute_edge_clearance(pallet, bbox)`
- `_evaluate_tolerance(clearance, tolerances, auto_underhang)`
- `_inner_axis_segments(layout)`
- `_compute_metrics(layout, req, layer_count, interlock)`
- `_rank_solutions(solutions)`

Core requirements implementation notes:
- Enumerate `(nx, ny, rotation)` candidates; include interlock when enabled.
- Keep upright-only (height never rotates).
- Detect no overlap (grid generation should inherently prevent overlap; still validate).
- Filter to `tolerance_pass=true` before ranking.
- `solution_id` patterns:
  - Normal: `grid_{nx}x{ny}_rot{rotation}`
  - Interlock: `grid_{nx}x{ny}_rot{rotation}_interlock`
- Enforce max options: default 25, upstream hard cap 250.
- If none feasible, return:
  - `status="impossible"`
  - approved reason codes.

Mandatory metrics fields per solution:
- `cases_per_layer`
- `total_cases`
- `total_height_mm`
- `total_weight_kg` when case weight exists
- `area_fill_efficiency_pct`
- `footprint_bbox_mm`
- `edge_clearance_mm`
- `tolerance_pass`
- `inner_axis_segments_mm`
- `interlock`

### 5. Recommender Module

#### File: `scripts/pallet_coach/recommender.py`
Purpose: stable feature entrypoint for downstream API layer.

Implement:
- `recommend(req: dict, max_options: int = 25) -> dict`

Behavior:
1. Normalize request using `contracts.parse_request`.
2. Invoke `solver.solve`.
3. Compute stacking analysis using top solution `cases_per_layer` if available.
4. Return dict aligned for bundle serialization.

### 6. Tests and Evaluation Assets

#### File: `scripts/tests/test_solver_centered_strict_tolerances.py`
Must validate:
- feasible outputs under zero-overhang and small-underhang constraints
- expected ranking order for known case/pallet combinations

#### File: `scripts/tests/test_stacking_model.py`
Must validate:
- all stacking formulas and warnings
- no-weight paths return optional fields as null/None

#### File: `scripts/tests/test_layer_count_exceedance_highlight.py`
Must validate:
- warning behavior when current layers exceed height ceiling

#### File: `eval/test_cases.json`
Must include minimum cases:
- perfect-fit
- underhang-tolerance-bound
- impossible
- rotation-required

#### File: `eval/run_eval.py`
Must:
- iterate test cases
- call recommender or solver
- compare expected metrics and statuses
- emit pass/fail and diff summary

#### File: `samples/R1_perfect_fit/bundle.json`
#### File: `samples/R13_underhang_tolerance/bundle.json`
Purpose: baseline parity references for later validation.

### 7. Packaging and Dependency Support

#### File: `scripts/requirements.txt`
Include required dependencies for RF-001 scope:
- `pytest==8.3.4`
- optional additional typing/test tools if desired

#### File: `scripts/tests/__init__.py`
Optional package marker for test discovery consistency.

## Suggested Implementation Sequence

1. Create `errors.py`, `models.py`, `contracts.py`.
2. Create `stacking.py` with tested formulas first.
3. Implement `solver.py` candidate generation and metrics.
4. Implement `recommender.py` orchestration.
5. Add mandatory tests.
6. Add eval harness and sample fixtures.
7. Run tests and lock deterministic ordering snapshots.

## Pseudocode Outline for Deterministic Ranking

- Build candidate list in deterministic nested loop order:
  - for rotation in sorted(rotations)
  - for nx in range(1..max_nx)
  - for ny in range(1..max_ny)
- compute metrics
- keep only `tolerance_pass`
- stable sort key:
  - `(-cases_per_layer, -area_fill_efficiency_pct, solution_id)`

This ensures deterministic output across Python runs.

---

## Testing Strategy

## Unit Tests

### scripts/tests/test_solver_centered_strict_tolerances.py
Required test cases:
1. `test_zero_overhang_exact_fit_returns_feasible_solution`
2. `test_small_underhang_anchor_rule_passes_when_one_side_within_limit`
3. `test_rotation_required_case_appears_when_allow_rotation_true`
4. `test_no_feasible_pattern_returns_impossible_reason_code`

### scripts/tests/test_stacking_model.py
Required test cases:
1. `test_height_ceiling_computation_matches_formula`
2. `test_weight_ceiling_computation_matches_formula`
3. `test_effective_ceiling_uses_min_of_height_and_weight`
4. `test_optional_weight_fields_are_none_when_missing`
5. `test_recommended_range_caps_at_plus_three_and_effective_ceiling`

### scripts/tests/test_layer_count_exceedance_highlight.py
Required test cases:
1. `test_warning_emitted_when_current_stack_height_exceeds_2000`
2. `test_weight_warning_emitted_when_weight_is_binding`

## UAT / Scenario Tests

1. Perfect fit scenario: validate top option matches expected full utilization pattern.
2. Underhang-bound scenario: validate anchored-axis rule behavior.
3. Impossible scenario: validate reason code and empty solutions.
4. Rotation-required scenario: validate optimal layout requires `rot90` candidate.

## Quality Gates

- All RF-001 unit tests pass.
- Deterministic order snapshot stable across repeated runs.
- No missing mandatory metric fields.
- Eval harness reports pass on baseline scenarios.

---

## Developer Checklist

### Setup
- [ ] Create feature branch: `feature/rf-001-core-solver-engine`
- [ ] Create `scripts/pallet_coach/` package structure
- [ ] Create `scripts/tests/`, `eval/`, and `samples/` folders

### Implementation
- [ ] Create `scripts/pallet_coach/errors.py`
- [ ] Create `scripts/pallet_coach/models.py`
- [ ] Create `scripts/pallet_coach/contracts.py`
- [ ] Implement defaults and validation guards
- [ ] Create `scripts/pallet_coach/stacking.py`
- [ ] Implement all stacking formulas and warnings
- [ ] Create `scripts/pallet_coach/solver.py`
- [ ] Implement candidate enumeration for rotation and optional interlock
- [ ] Implement tolerance checks and edge clearance logic
- [ ] Implement full metrics block including `inner_axis_segments_mm`
- [ ] Implement deterministic ranking and impossible handling
- [ ] Create `scripts/pallet_coach/recommender.py`
- [ ] Expose `recommend(req, max_options=25)` and solver delegation

### Testing
- [ ] Create mandatory unit tests in `scripts/tests/`
- [ ] Add evaluation harness and test cases in `eval/`
- [ ] Add sample bundle references in `samples/`
- [ ] Run `pytest` and ensure all pass
- [ ] Run evaluation script and verify expected outcomes

### Validation
- [ ] Confirm all RF-001 acceptance criteria map to tests
- [ ] Verify field names match requirement contracts exactly
- [ ] Verify deterministic output order across repeated executions
- [ ] Verify impossible reason-code coverage

### Completion
- [ ] Self-review for requirement parity
- [ ] Open PR with traceability matrix (requirements to code/tests)
- [ ] Mark RF-001 feature status as In Development or Implemented after merge

---

## Troubleshooting Guide

### Common Issues

**Issue:** Slightly inconsistent ranking order between runs  
**Fix:** Ensure explicit tertiary sort key (`solution_id`) and deterministic loop order.

**Issue:** Underhang behavior appears counterintuitive  
**Fix:** Recheck anchored-axis rule uses `min(side_a, side_b)` not both sides.

**Issue:** Unexpected impossible responses  
**Fix:** Inspect tolerance defaults and `auto_underhang` override behavior in normalized request.

**Issue:** Missing metric fields in downstream bundle generation  
**Fix:** Validate `SolutionMetrics` constructor and serialization completeness before returning.

---

## Additional Resources

- Feature specification: `specs/features/001-core-solver-engine.md`
- Source requirements: `requirement.md` sections 3, 4, 9, 12
- Related features: RF-002, RF-003, RF-007

---

**END OF IMPLEMENTATION PLAN**
