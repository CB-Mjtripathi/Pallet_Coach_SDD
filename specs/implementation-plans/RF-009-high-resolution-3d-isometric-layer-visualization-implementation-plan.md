# Implementation Plan: High-Resolution 3D Isometric Layer Visualization
**Feature ID:** RF-009  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Modification + New Components)

---

## Executive Summary

**Feature:** High-Resolution 3D Isometric Layer Visualization  
**Status:** Partially Implemented  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** Medium-High  
**Risk Level:** Medium

**Summary:**  
The codebase already supports deterministic 3D rendering (`comparison_3d.png`, `onpallet_3d.png`) and Run-page diagram viewing, but RF-009 requires higher-resolution isometric output, exploded layer separation, and JSON hide/show UX behavior. The recommended approach is to extend existing rendering and UI components without breaking current artifacts and API contracts.

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
- Feature ID: RF-009
- Feature Name: High-Resolution 3D Isometric Layer Visualization
- Priority: High
- Complexity: Medium-High

### Scope Summary
RF-009 improves interpretability of pallet stacking visuals by adding a high-resolution isometric exploded-layer diagram while preserving deterministic solver geometry. It also requires Run UI to provide a default-collapsed JSON details experience with an explicit show/hide control.

### Key Requirements
1. High-resolution 3D isometric rendering with stable camera and wooden pallet base.
2. Exploded layer separation for clear layer boundaries.
3. Layer ordering preserved and mixed carton sizes represented correctly.
4. JSON details hidden by default, user-toggleable in Run UI.

### User Stories Summary
- US-9.1: High-resolution isometric pallet visualization.
- US-9.2: Exploded-view layer separation.
- US-9.3: JSON hide/show in Run experience.

### Technical Specifications
- APIs Required: No new external APIs required.
- Data Models: Existing bundle and solution structures; add new artifact key/path.
- Integrations: Existing solve pipeline and Run UI diagram carousel.
- Performance: Maintain acceptable solve-to-artifact latency while increasing image fidelity.

### Dependencies
- Prerequisites: RF-003, RF-005, RF-006
- Related: RF-007 for new tests and quality gates

### Complexity Assessment
**Estimated Complexity:** Medium-High  
**Reasoning:** Existing 3D primitives are present, but introducing exploded-layer semantics and high-resolution output while preserving backward compatibility for artifacts/UI/tests requires careful refactoring and additional test coverage.

Factors:
- User stories: 3
- Modules involved: ~8
- External integrations: 0 new
- Data model complexity: moderate (artifact map extension)
- UI complexity: moderate

---

## Implementation Status

## Search Results Analysis

### Files Found

#### Backend Services
- File: `scripts/pallet_coach/diagram.py`
  - Relevance: High
  - Functions Found: `render_comparison_3d_png`, `render_onpallet_3d_png`, `_draw_3d_layout`
  - Functionality: Deterministic 3D rendering with layered stacks and fixed camera for on-pallet view.
  - Match Level: Partial

- File: `scripts/pallet_coach/artifacts.py`
  - Relevance: Medium
  - Functionality: Generates image prompts and bundle artifact metadata updates.
  - Match Level: Partial (no hi-res exploded artifact contract)

- File: `scripts/pallet_coach/api/app.py`
  - Relevance: Medium
  - Functionality: Solve pipeline writes deterministic artifacts and exposes run bundle/output.
  - Match Level: Partial (artifact list extension needed)

#### UI Components
- File: `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
  - Relevance: High
  - Functionality: Displays deterministic flat/3d artifacts and triggers optional AI diagrams.
  - Match Level: Partial (no dedicated hi-res exploded artifact tab)

- File: `UI/pallet_coach_ui/src/pages/Run.tsx`
  - Relevance: High
  - Functionality: Loads run bundle, renders summary, diagrams, tables, logs.
  - Match Level: Partial (no JSON details panel/toggle)

#### Tests
- File: `scripts/tests/test_diagram_rendering.py`
  - Relevance: High
  - Functionality: Validates PNG creation and 150 dpi minimum for existing renderers.
  - Match Level: Partial

- File: `scripts/tests/test_artifact_pipeline.py`
  - Relevance: High
  - Functionality: Validates mandatory artifact files and bundle pointers.
  - Match Level: Partial

- File: `UI/pallet_coach_ui/src/pages/Run.test.tsx`
  - Relevance: Medium
  - Functionality: Baseline Run page render behavior test.
  - Match Level: Partial

### Summary of Findings
- Total highly relevant files: 7
- Existing 3D rendering: present
- Existing exploded-layer support: absent
- Existing JSON hide/show control: absent

## Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-9.1 | Partial | `scripts/pallet_coach/diagram.py` 3D rendering exists | No dedicated hi-res exploded isometric artifact mode/contract |
| US-9.2 | Not Implemented | Layer stacking drawn contiguous by case height | No exploded vertical gap policy |
| US-9.3 | Not Implemented | Run page has no raw JSON panel/toggle | Need hidden-by-default JSON details section |

### Coverage Summary
- Implemented: 0 / 3
- Partially Implemented: 1 / 3
- Not Implemented: 2 / 3

### Recommendation
**Primary Approach:** HYBRID  
**Reasoning:** Strong baseline rendering and Run page framework exists, but key RF-009 capabilities require extending existing modules and adding targeted UI + tests.

---

## Impact Analysis

## Affected Modules

### Services Layer
- File: `scripts/pallet_coach/diagram.py`
  - Change Type: Modification
  - Impact Level: High
  - Reason: Core rendering logic for hi-res isometric exploded output.

- File: `scripts/pallet_coach/artifacts.py`
  - Change Type: Modification
  - Impact Level: Medium
  - Reason: Artifact registration/prompt alignment for new diagram type.

### API Layer
- File: `scripts/pallet_coach/api/app.py`
  - Change Type: Modification
  - Impact Level: Medium
  - Reason: Include new deterministic artifact key/path in solve outputs.

### UI Layer
- File: `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
  - Change Type: Modification
  - Impact Level: Medium
  - Reason: Add high-resolution exploded-view selection/display.

- File: `UI/pallet_coach_ui/src/pages/Run.tsx`
  - Change Type: Modification
  - Impact Level: Medium
  - Reason: Add JSON show/hide control and default-collapsed panel.

### Test Layer
- File: `scripts/tests/test_diagram_rendering.py`
  - Change Type: Modification
  - Impact Level: Medium

- File: `scripts/tests/test_artifact_pipeline.py`
  - Change Type: Modification
  - Impact Level: Medium

- File: `UI/pallet_coach_ui/src/pages/Run.test.tsx`
  - Change Type: Modification
  - Impact Level: Low-Medium

## Integration Points

### Internal Dependencies
- New feature depends on RF-003 rendering and artifact conventions.
- Run UI integration depends on RF-005 page/component structure.
- UI controls should reuse RF-006 primitives (`Button`, `Card`, etc.).

### Data Flow
1. Solve returns best solution + stack metadata.
2. Diagram renderer generates current artifacts plus new hi-res exploded artifact.
3. API bundle metadata includes new artifact path.
4. Run page loads and renders new visual option.
5. JSON details remain collapsed unless user explicitly expands.

## Features That Must NOT Be Impacted

1. RF-003 deterministic artifact generation
   - Location: `scripts/pallet_coach/diagram.py`, `scripts/pallet_coach/api/app.py`
   - Preserve: Existing `comparison_flat.png`, `comparison_3d.png`, `onpallet_3d.png`
   - Validation: Run `pytest scripts/tests/test_diagram_rendering.py -q` and `pytest scripts/tests/test_artifact_pipeline.py -q`

2. RF-005 Run page baseline UX
   - Location: `UI/pallet_coach_ui/src/pages/Run.tsx`
   - Preserve: Existing summary/diagram/options/logs rendering and flow
   - Validation: `npm test` + manual run page smoke test

3. RF-007 quality gates
   - Location: test and eval pipeline
   - Preserve: All current tests/eval must continue passing
   - Validation: full `pytest scripts/tests -q` and eval harness

## Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Code Complexity | Medium | 3D rendering refactor may affect existing visuals | Isolate new renderer path and keep old outputs intact |
| Integration Points | Medium | New artifact key impacts UI loading logic | Add fallback behavior and artifact existence checks |
| Data Model Changes | Low-Medium | Bundle artifact map extension only | Backward-compatible optional key |
| External Dependencies | Low | No new external API | Keep dependency surface unchanged |
| Test Coverage Gap | Medium | New visual behavior requires assertions | Add deterministic tests for size/view/gap semantics |
| Feature Coupling | Medium | Diagram and UI tightly coupled on artifact names | Use explicit constants/types and update both sides together |

### Specific Risks

#### Risk 1: Existing 3D artifacts regress
- Probability: Medium
- Impact: High
- Mitigation: Keep existing render functions stable; add new function for RF-009 output.
- Contingency: Revert new renderer binding while keeping optional artifact generation behind flag.

#### Risk 2: High-resolution rendering increases runtime too much
- Probability: Medium
- Impact: Medium
- Mitigation: Use bounded DPI/figure size; benchmark representative cases.
- Contingency: Introduce quality tier fallback (standard/high).

#### Risk 3: JSON panel introduces noisy UX
- Probability: Low
- Impact: Medium
- Mitigation: Default collapsed state, concise label, no impact on existing sections.
- Contingency: Feature flag to disable JSON panel if product feedback requires.

---

## Development Plan
## Implementation Approach: HYBRID (Modification + New Components)

## Files to MODIFY

### 1) Diagram Renderer Enhancements
**File:** `scripts/pallet_coach/diagram.py`

#### Change 1: Add explicit hi-res exploded isometric renderer
- Add new function, e.g. `render_isometric_exploded_3d_png(...)`.
- Behavior:
  - Isometric camera: fixed deterministic `view_init` values.
  - High resolution target: at least 1920x1080 equivalent (e.g., larger figsize and/or higher dpi).
  - Wooden pallet visual style distinct from cartons.
  - Layer exploded gap parameter (default constant, deterministic).

#### Change 2: Extend 3D layout helper
- Update `_draw_3d_layout` to support optional `exploded_gap_mm` and `isometric_mode`.
- Preserve current behavior when `exploded_gap_mm=0`.

#### Change 3: Mixed carton compatibility
- Ensure per-item dimensions (`dim_x_mm`, `dim_y_mm`) remain source-of-truth.
- Keep compatibility with current single-size inputs.

### 2) Artifact Metadata and Prompt Updates
**File:** `scripts/pallet_coach/artifacts.py`
- Extend artifact map conventions to include new deterministic artifact key, for example:
  - `isometric_exploded_3d`: `isometric_exploded_3d.png`
- Extend prompts with optional guidance for exploded-layer interpretability.

### 3) Solve Pipeline Artifact Wiring
**File:** `scripts/pallet_coach/api/app.py`
- Update `_build_artifacts()` to include new artifact key/path.
- In `solve_endpoint()`, render and write new artifact.
- Keep existing solve response fields backward-compatible.

### 4) Run Page Visual Selector and JSON Toggle
**File:** `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
- Add third deterministic option/tab for hi-res exploded isometric view.
- Keep existing flat and 3d options unchanged.

**File:** `UI/pallet_coach_ui/src/pages/Run.tsx`
- Add JSON details panel with show/hide control.
- Default collapsed state.
- Suggested implementation:
  - local state `showJsonDetails` default false
  - toggle button/expander
  - render JSON payload from bundle when expanded

### 5) API Type Update (if needed)
**File:** `UI/pallet_coach_ui/src/api/types.ts`
- If strict typing needed for artifact key consumption, add optional typed key for new artifact.

## Files to CREATE

### 1) Optional dedicated constants module (recommended)
**File:** `scripts/pallet_coach/rendering_constants.py` (optional)
- Hold constants for isometric angles, default exploded gap, high-res DPI profile.
- Reduces hardcoded values and improves testability.

---

## Testing Strategy

### Backend Unit/Integration

**Modify:** `scripts/tests/test_diagram_rendering.py`
- Add tests:
  1. `test_render_isometric_exploded_png_exists_and_is_png`
  2. `test_render_isometric_exploded_png_has_high_resolution`
  3. `test_exploded_gap_applies_vertical_layer_offset`

**Modify:** `scripts/tests/test_artifact_pipeline.py`
- Add new mandatory artifact pointer check for hi-res exploded output.

### Frontend Unit/UI

**Modify:** `UI/pallet_coach_ui/src/pages/Run.test.tsx`
- Add tests:
  1. JSON panel hidden by default.
  2. Toggle reveals JSON and hides again.
  3. New diagram selection renders expected image path.

### Regression
- Backend:
  - `pytest scripts/tests -q`
  - `PYTHONPATH=scripts python eval/run_eval.py --include-sample-parity`
- Frontend:
  - `npm test`
  - `npm run build`

### Manual UAT
1. Run solve with 6-10 layers.
2. Verify exploded layer separation and readability in new diagram option.
3. Confirm pallet base is visible and stable camera angle is maintained.
4. Verify JSON is hidden by default and toggles instantly.

---

## Developer Checklist

### Preparation
- [ ] Review RF-009 feature spec
- [ ] Review current `diagram.py` and Run UI components
- [ ] Confirm artifact naming conventions used by API/UI

### Modification Phase
- [ ] Modify `scripts/pallet_coach/diagram.py`
  - [ ] Add high-resolution isometric exploded renderer
  - [ ] Add exploded gap support
  - [ ] Preserve existing render function behavior
- [ ] Modify `scripts/pallet_coach/artifacts.py`
  - [ ] Add artifact mapping/prompt context
- [ ] Modify `scripts/pallet_coach/api/app.py`
  - [ ] Register and write new artifact in solve path
- [ ] Modify `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
  - [ ] Add new deterministic view selector
- [ ] Modify `UI/pallet_coach_ui/src/pages/Run.tsx`
  - [ ] Add JSON hide/show control, default hidden

### Testing Phase
- [ ] Update backend diagram tests
- [ ] Update artifact pipeline tests
- [ ] Update Run page tests
- [ ] Run all backend tests and eval harness
- [ ] Run frontend tests and build

### Validation Phase
- [ ] Confirm no regressions in existing diagrams and run flow
- [ ] Confirm RF-009 acceptance criteria coverage
- [ ] Document implementation notes and update feature status when done

---

## Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|---------------------|---------------|--------|
| High-resolution isometric stack | >=1920x1080 equivalent, stable camera, pallet base | `scripts/pallet_coach/diagram.py` current 3D functions | ⚠️ Partial |
| Exploded layered separation | Visible vertical gaps per layer | `scripts/pallet_coach/diagram.py` contiguous z stacking | ❌ Missing |
| JSON hide/show in Run | Hidden by default, toggle display | `UI/pallet_coach_ui/src/pages/Run.tsx` no JSON panel | ❌ Missing |
| Artifact persistence for new view | Stable artifact path/key in bundle | `scripts/pallet_coach/api/app.py` artifact map | ❌ Missing |

---

## Final Recommendation

Proceed with HYBRID implementation by extending current deterministic rendering and Run UI. Do not replace existing diagram modes; add RF-009 as an additive capability with dedicated tests and backward-compatible artifact handling.

---

END OF IMPLEMENTATION PLAN
