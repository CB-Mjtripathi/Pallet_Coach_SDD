# Implementation Plan: Artifact Pipeline and Diagram Rendering
**Feature ID:** RF-003  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Modification + New Components)

---

## Executive Summary

**Feature:** Artifact Pipeline and Diagram Rendering  
**Status:** Partially Implemented  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** High  
**Risk Level:** Medium

**Summary:**
RF-003 has partial groundwork in place through RF-002 (`run_id` allocation, run folder creation, `bundle.json` and `run_log.txt` persistence). The missing scope is deterministic generation of mandatory non-AI artifacts and Matplotlib-native diagram rendering, including baseline inferred grid logic for BEFORE comparisons. This plan adds new rendering and artifact modules and extends `/api/solve` orchestration while preserving RF-001 deterministic solver behavior and RF-002 path-security guarantees.

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

## Feature Overview
**Feature ID:** RF-003  
**Feature Name:** Artifact Pipeline and Diagram Rendering  
**Priority:** High  
**Complexity:** High

## Scope Summary
RF-003 requires every successful solve to emit a complete deterministic artifact set into `04_Output/<run_id>/`, with stable filenames and bundle pointers. It also requires four non-AI renderer functions in `scripts/pallet_coach/diagram.py` producing print-quality PNGs (>=150 dpi) and implementing mandatory visual semantics (case labels, dimension lines, tolerance coloring).

This feature must additionally infer baseline `(nx, ny)` from `baseline_cases_per_layer` for BEFORE comparisons, using scored factor-pair selection, while ensuring the inferred baseline is never treated as solver output.

## Key Requirements
1. Persist mandatory artifacts for each successful `/api/solve`: `bundle.json`, `run_log.txt`, `recommendation_summary.md`, `layer_diagram.png`, `comparison_flat.png`, `comparison_3d.png`, `onpallet_3d.png`, `image_prompt_flat.md`, `image_prompt_3d.md`.
2. Keep run ID semantics already implemented in RF-002 (`R{n:04d}_{YYYYMMDD}`).
3. Add deterministic `recommendation_summary.md` generation from solver outputs.
4. Implement `render_layer_png`, `render_comparison_flat_png`, `render_comparison_3d_png`, `render_onpallet_3d_png` in `scripts/pallet_coach/diagram.py`.
5. Use Matplotlib `Agg` backend and emit PNGs at >=150 dpi.
6. Render labels, dimension lines from `inner_axis_segments_mm`, and edge-clearance zones with tolerance statuses.
7. Implement baseline inferred grid scoring for BEFORE panel when `baseline_cases_per_layer` is provided.
8. Keep bundle artifact pointers consistent and atomically updated.

## User Stories Summary
- **US-3.1:** Persist complete run bundles and mandatory artifacts for auditability.
- **US-3.2:** Render deterministic non-AI diagrams for before/after understanding.
- **US-3.3:** Infer baseline grid for BEFORE panel without polluting solver outputs.

## Technical Specifications
- **APIs Required:** `/api/solve` orchestration extension from RF-002.
- **Data Models:** Reuse RF-001 solution/metrics schema; add internal artifact metadata helpers.
- **Integrations:** RF-001 recommender outputs, RF-002 run store paths and bundle writes.
- **Performance:** Diagram generation target <=3 seconds each on typical inputs.

## Dependencies
- **Prerequisites:** RF-001 solver metrics (`inner_axis_segments_mm`, edge clearances, interlock), RF-002 API/run store.
- **Integration Points:** RF-004 optional AI diagram augmentations, RF-005 run page artifact display.

## Complexity Assessment
**Estimated Complexity:** High  
**Reasoning:**
- Number of user stories: 3
- Number of modules involved: 4 to 6
- External integrations: none for native rendering
- Data model complexity: moderate
- UI complexity: indirect (artifact contract consumed by UI)
- Visualization and geometry fidelity requirements are strict

---

## Implementation Status

## Search Results Analysis

### Files Found

#### Backend/Run Pipeline
- `scripts/pallet_coach/api/app.py`  
  - **Relevance:** High  
  - **Functions Found:** `/api/solve`, bundle/log writing orchestration  
  - **Functionality:** Creates run dir, writes `bundle.json` and log, exposes artifact pointer keys  
  - **Match Level:** Partial

- `scripts/pallet_coach/api/run_store.py`  
  - **Relevance:** High  
  - **Functions Found:** run ID allocator, run dir create/resolve, bundle write, log append/tail  
  - **Functionality:** Core run persistence utilities  
  - **Match Level:** Partial prerequisite

- `scripts/pallet_coach/recommender.py`  
  - **Relevance:** Medium  
  - **Functionality:** Deterministic recommendation payload  
  - **Match Level:** Supporting prerequisite

#### Diagram/Artifact Generation
- No `scripts/pallet_coach/diagram.py` found.
- No baseline inferred grid utility found.
- No deterministic `recommendation_summary.md` generator found.
- No actual PNG emission currently in `/api/solve` path.

### Summary of Findings
- **Total relevant files found:** 3 primary + RF-001 dependencies
- **Highly relevant files:** 2 (`api/app.py`, `api/run_store.py`)
- **Partially relevant files:** 1 (`recommender.py`)
- **Missing core RF-003 files:** diagram module and artifact generation utilities

## Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-3.1 | Partial | Run folder + `bundle.json` + `run_log.txt` exist in `/api/solve` | Missing mandatory summary/diagram/prompt artifact creation and comprehensive artifact pointer sync |
| US-3.2 | Not Implemented | None | Missing `diagram.py` renderers and PNG generation |
| US-3.3 | Not Implemented | None | Missing baseline inferred grid scoring utility for BEFORE panel |

### Coverage Summary
- **Implemented:** 0 / 3 full user stories (0%)
- **Partially Implemented:** 1 / 3
- **Not Implemented:** 2 / 3

### Recommendation
**Primary Approach:** HYBRID  
**Reasoning:** Extend existing API run orchestration and run-store primitives while creating missing rendering and artifact modules from scratch.

## Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Mandatory run folder + run_id format | `04_Output/<run_id>` and daily monotonic IDs | `api/run_store.py` | Exists |
| Mandatory artifact set generated | summary + diagrams + prompt markdowns | `api/app.py` only has pointer placeholders | Missing |
| Native diagram rendering functions | 4 renderer functions in `diagram.py` | None | Missing |
| Baseline inferred grid logic | scored factor-pair `(nx, ny)` inference | None | Missing |
| Bundle pointers updated for artifacts | stable schema in `bundle.json` | partial pointer dictionary only | Partial |

---

## Impact Analysis

## Affected Modules

### API Orchestration
- **File:** `scripts/pallet_coach/api/app.py`
  - **Change Type:** Modification
  - **Impact Level:** High
  - **Reason:** `/api/solve` must generate and persist all deterministic artifacts.

### Run Store / Artifact Utilities
- **File:** `scripts/pallet_coach/api/run_store.py`
  - **Change Type:** Modification (or extension via new helper module)
  - **Impact Level:** Medium
  - **Reason:** Add artifact write helpers and safe file update patterns.

- **File:** `scripts/pallet_coach/artifacts.py` (new recommended)
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Encapsulate summary markdown generation, prompt file writing, and bundle pointer updates.

### Diagram Rendering
- **File:** `scripts/pallet_coach/diagram.py`
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Implement four mandatory renderers and baseline inference logic.

### Dependencies
- **File:** `scripts/requirements.txt`
  - **Change Type:** Modification
  - **Impact Level:** Medium
  - **Reason:** Ensure Matplotlib dependency present (`matplotlib>=3.8`).

### Tests
- **File:** `scripts/tests/test_artifact_pipeline.py` (new)
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Validate mandatory file creation and bundle pointer consistency.

- **File:** `scripts/tests/test_diagram_rendering.py` (new)
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Validate PNG generation, size/resolution, and baseline inference behavior.

## Integration Points

### Internal Dependencies
- **Depends On:** RF-001 Core Solver Engine
  - **Integration Point:** Use top solution layout + metrics to render diagrams and build summary
  - **Data Flow:** recommender solutions -> diagram renderer and summary writer -> artifact files
  - **Impact:** High

- **Depends On:** RF-002 API Layer and Run Management
  - **Integration Point:** run directory allocation and path-safe writes
  - **Data Flow:** run_id/run_dir -> artifact writes -> bundle update -> API response
  - **Impact:** High

### External Dependencies
- **Matplotlib (Agg backend)** for native deterministic diagram rendering.

### Data Flow
1. `/api/solve` obtains recommendation payload.
2. Select best solution and gather required metrics.
3. Generate deterministic summary markdown and prompt markdown files.
4. Render four native PNG diagrams to run directory.
5. Update `bundle.json` artifact pointers and append run log events.

## Features That Must NOT Be Impacted

1. **RF-001 ranking and tolerance semantics**
   - **Location:** `scripts/pallet_coach/solver.py`
   - **Why Preserve:** Diagram outputs depend on solver truth; no solver behavior drift allowed.
   - **Validation:** Existing RF-001 tests and eval harness remain green.

2. **RF-002 path traversal protections and run directory safety**
   - **Location:** `scripts/pallet_coach/api/run_store.py` and `scripts/pallet_coach/api/app.py`
   - **Why Preserve:** Security-critical behavior.
   - **Validation:** Existing API/run_store tests remain green.

## Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Code Complexity | Medium | Multi-artifact generation pipeline | isolate in `artifacts.py` and keep app orchestration thin |
| Integration Points | Medium | Tightly coupled with API solve flow | add end-to-end solve artifact tests |
| Data Model Changes | Medium | bundle schema drift could break UI | schema-aware tests against required keys |
| External Dependencies | Low | Matplotlib only | pin compatible version and use Agg backend |
| Test Coverage Gap | High | no current artifact-generation tests | add targeted artifact and rendering tests |
| Feature Coupling | Medium | diagram data depends on solver metrics | preserve RF-001 interfaces and add compatibility tests |

### Specific Risks

#### Risk 1: Diagram render performance exceeds target
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Use simple geometry primitives and avoid unnecessary redraw passes.
  - Reuse figure settings and close figures promptly.
- **Contingency:** degrade comparison detail level under high-load scenarios.

#### Risk 2: Bundle artifact pointers diverge from files on disk
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Generate files first, then atomically update bundle pointers.
  - Add test asserting pointer/file existence parity.
- **Contingency:** recovery task to rebuild pointer map from run directory.

#### Risk 3: Baseline inference picks unrealistic pair
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Use explicit scoring combining footprint plausibility and grid balance.
  - Add edge-case tests for multiple factor pairs.
- **Contingency:** fallback to closest square-ish factor pair.

---

## Development Plan

## Implementation Approach: HYBRID (Modification + New Components)

### Rationale
RF-002 already handles run allocation, bundle persistence, and secure paths. RF-003 requires adding missing deterministic artifact generation and diagram rendering while reusing the existing solve orchestration shell.

### Strategy Summary
- **New Components:** 4
  - `diagram.py`, `artifacts.py`, artifact tests, diagram tests
- **Modified Components:** 3
  - `api/app.py`, `api/run_store.py` (helper extension optional), `requirements.txt`
- **Unchanged Components:** RF-001 solver/contracts/stacking/recommender semantics

## Files to CREATE

### 1. Diagram Renderer
**File:** `scripts/pallet_coach/diagram.py`

Implement:
- `render_layer_png(run_dir, solution, request, out_name="layer_diagram.png")`
- `render_comparison_flat_png(run_dir, best_solution, request, baseline_cases_per_layer=None, out_name="comparison_flat.png")`
- `render_comparison_3d_png(run_dir, best_solution, request, baseline_cases_per_layer=None, out_name="comparison_3d.png")`
- `render_onpallet_3d_png(run_dir, best_solution, request, out_name="onpallet_3d.png")`

Mandatory renderer constraints:
- set backend `matplotlib.use("Agg")`
- output PNG with `dpi >= 150`
- case rectangle labels with index + rotation
- dimension lines based on `inner_axis_segments_mm`
- tolerance zone colors from required palette

Add helper:
- `infer_baseline_grid(baseline_cases_per_layer, case_length_mm, case_width_mm) -> tuple[int, int]`
  - enumerate factor pairs
  - score by implied footprint plausibility + grid balance
  - return best pair

### 2. Artifact Writer Helpers
**File:** `scripts/pallet_coach/artifacts.py`

Implement:
- `write_recommendation_summary(run_dir, bundle) -> Path`
- `write_image_prompts(run_dir, bundle) -> tuple[Path, Path]`
- `update_bundle_artifacts(bundle, artifact_map) -> dict`

Summary requirements:
- deterministic markdown
- includes solver status, top option metrics, and stacking highlights
- no AI model usage in this feature

Prompt files:
- `image_prompt_flat.md`
- `image_prompt_3d.md`
- include deterministic run context placeholders for RF-004 reuse

### 3. Tests
**File:** `scripts/tests/test_artifact_pipeline.py`

Cases:
1. `/api/solve` creates all mandatory artifact files.
2. Bundle artifact pointers reference existing files.
3. Run log contains artifact-generation events.

**File:** `scripts/tests/test_diagram_rendering.py`

Cases:
1. Each renderer emits PNG file and non-zero bytes.
2. PNG metadata/resolution meets >=150 dpi target.
3. baseline inference returns expected `(nx, ny)` for known factor scenarios.

## Files to MODIFY

### 1. API Solve Orchestration
**File:** `scripts/pallet_coach/api/app.py`

Required changes:
- After recommender call, invoke deterministic artifact generation flow.
- Write missing mandatory files:
  - `recommendation_summary.md`
  - `layer_diagram.png`
  - `comparison_flat.png`
  - `comparison_3d.png`
  - `onpallet_3d.png`
  - `image_prompt_flat.md`
  - `image_prompt_3d.md`
- Update `bundle["artifacts"]` entries only after file creation.
- Append run log entries for each major artifact stage.

### 2. Run Store Helper Extension (optional)
**File:** `scripts/pallet_coach/api/run_store.py`

Add optional helper(s):
- `write_text_artifact(run_dir, filename, content)`
- `artifact_exists(run_dir, filename)`

### 3. Dependency Manifest
**File:** `scripts/requirements.txt`

Ensure presence of:
- `matplotlib>=3.8`

---

## Testing Strategy

### Unit and Integration Tests
1. Existing RF-001 tests must remain green.
2. Existing RF-002 API/run-store tests must remain green.
3. New artifact and diagram tests validate file creation and renderer behavior.

### UAT Scenarios
1. Call `/api/solve`, confirm all mandatory artifact files appear in run directory.
2. Open `/output/{run_id}/{filename}` for generated PNG and markdown files.
3. Verify comparison outputs are present for runs with/without `baseline_cases_per_layer`.

### Validation Commands
- `c:/python314/python.exe -m pytest scripts/tests -q`
- `c:/python314/python.exe eval/run_eval.py`

---

## Developer Checklist

### Preparation
- [ ] Review RF-003 feature spec and this plan
- [ ] Confirm RF-001 and RF-002 test baselines are green

### Implementation
- [ ] Create `scripts/pallet_coach/diagram.py`
- [ ] Create `scripts/pallet_coach/artifacts.py`
- [ ] Extend `/api/solve` in `scripts/pallet_coach/api/app.py` to generate mandatory artifacts
- [ ] Ensure bundle artifact pointer map is consistent with files on disk
- [ ] Ensure Matplotlib Agg backend and dpi >=150 in all PNG renderers
- [ ] Ensure baseline inferred grid utility is deterministic and isolated to comparison rendering

### Testing
- [ ] Create `scripts/tests/test_artifact_pipeline.py`
- [ ] Create `scripts/tests/test_diagram_rendering.py`
- [ ] Run full test suite and confirm no regressions
- [ ] Run eval harness and confirm unchanged RF-001 behavior

### Validation
- [ ] Verify required files in each solve run directory
- [ ] Verify output route serves generated artifacts
- [ ] Verify run logs capture artifact generation lifecycle

### Completion
- [ ] Update RF-003 status to Implemented after delivery
- [ ] Create implementation-complete report for RF-003

---

## Troubleshooting Guide

**Issue:** Matplotlib backend error in headless environment  
**Fix:** set backend to `Agg` before pyplot imports in `diagram.py`.

**Issue:** PNG exists but unreadable or empty  
**Fix:** ensure figure `savefig(..., dpi=150)` and `plt.close(fig)` after writes.

**Issue:** Artifact pointers present but files missing  
**Fix:** update bundle pointers only after verifying file write success.

---

## Additional Resources

- Feature specification: `specs/features/003-artifact-and-diagram-pipeline.md`
- Implemented prerequisites:
  - `specs/features/001-core-solver-engine.md`
  - `specs/features/002-api-and-run-management.md`
- Source requirement sections: `requirement.md` sections 6.1, 6.2, 6.3, 9.3

---

**END OF IMPLEMENTATION PLAN**
