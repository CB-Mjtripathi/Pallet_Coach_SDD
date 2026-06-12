# Feature: High-Resolution 3D Isometric Layer Visualization

**Feature ID:** RF-009
**Status:** Implemented
**Priority:** High
**Target Release:** Phase 1.1 Enhancement
**Source Documentation:** User request (2026-04-17): "I can not see 3d stack and layering for pallet. Create a high-resolution 3D isometric diagram of pallet stacking and carton optimization."

---

## Overview

This feature upgrades pallet visualization clarity by adding a high-resolution 3D isometric rendering mode with exploded layer separation and mixed carton size support. The intent is to make stack structure, layer boundaries, and optimization outcomes immediately understandable in operational and stakeholder reviews.

It also introduces a UI affordance to hide or reveal raw JSON output so users can focus on visuals first while still retaining full technical transparency for debugging and audit workflows.

---

## User Stories

### US-9.1: Render high-resolution 3D isometric pallet stack

**As a** logistics planner  
**I want to** see a high-resolution 3D isometric pallet diagram  
**So that** I can clearly interpret stacking and placement outcomes

**Acceptance Criteria:**
- ✅ Rendered view is true isometric perspective with stable camera angle.
- ✅ Output image resolution supports high-clarity review (target >= 1920x1080 equivalent).
- ✅ A standard wooden pallet is always visible as the base reference.
- ✅ Cartons are rendered as 3D solids with visible edges and depth cues.

**Technical Details:**
- Extend existing diagram renderer in `scripts/pallet_coach/diagram.py`.
- Add explicit output mode for high-resolution isometric rendering.
- Persist output under run artifacts with stable filename key.

---

### US-9.2: Visualize layer boundaries with exploded view separation

**As an** operations analyst  
**I want to** see each layer slightly separated in exploded view  
**So that** I can distinguish layer composition and stacking sequence

**Acceptance Criteria:**
- ✅ Each layer is vertically offset by a configurable exploded gap.
- ✅ Separation is sufficient to visually distinguish all layers.
- ✅ Layer order (bottom to top) remains correct and consistent with solver output.
- ✅ Mixed carton sizes are represented correctly within and across layers.

**Technical Details:**
- Introduce exploded-layer render routine with deterministic offset policy.
- Keep cartesian coordinates traceable to original layout plus visual offset only.
- Ensure offset is presentational and does not alter optimization metrics.

---

### US-9.3: Hide/show JSON details from Run experience

**As a** business user  
**I want to** hide raw JSON by default and reveal it on demand  
**So that** I can review visuals without technical clutter

**Acceptance Criteria:**
- ✅ Add a show/hide control near JSON output sections in Run UI.
- ✅ Default state keeps JSON collapsed/hidden.
- ✅ Toggle state updates instantly without page reload.
- ✅ JSON remains available for technical review when expanded.

**Technical Details:**
- Update Run page and related components under `UI/pallet_coach_ui/src/pages/Run.tsx` and/or JSON display components.
- Reuse existing design system controls from RF-006.

---

## Dependencies

### Prerequisites
- RF-003 Artifact Pipeline and Diagram Rendering
- RF-005 React UI Home and Run Experience
- RF-006 UI Design System - Precision Industrial Dark

### Related Features
- RF-007 Testing, Evaluation, and Quality Gates (new visual regression and rendering tests)

---

## Technical Architecture

### Components Involved
- `scripts/pallet_coach/diagram.py` (high-resolution isometric + exploded rendering)
- `scripts/pallet_coach/artifacts.py` (artifact registration for new diagram output)
- `UI/pallet_coach_ui/src/pages/Run.tsx` (JSON show/hide interaction)

### Data Flow
1. Solve endpoint produces deterministic layout and stacking outputs.
2. Diagram pipeline generates high-resolution isometric exploded-layer image.
3. Artifact metadata is written into `bundle.json`.
4. Run UI loads image artifacts and keeps JSON collapsed unless user expands.

### APIs & Integrations
- Existing solve and output artifact routes remain primary integration points.
- No new external APIs required.

---

## Non-Functional Requirements

### Performance
- High-resolution diagram generation should remain within practical run-time target for Step 1 cases.

### Security
- Artifact path and run path safety controls from RF-008 remain mandatory.

### Scalability
- Rendering mode should be parameterized for future quality tiers (standard/high/print).

---

## Implementation Notes

- Favor deterministic camera settings and color mapping for repeatability across runs.
- Use clear layer labeling and optional legend to support mixed carton sizes.
- Keep JSON toggle behavior accessible via keyboard and screen readers.

---

## Test Coverage

### Unit Tests Required
- Diagram renderer test for high-resolution output dimensions.
- Exploded-layer separation validation test.
- JSON show/hide state logic test in Run UI.

### UAT Tests Required
- Manual readability check of 3D isometric exploded output on typical run cases.
- Verify hidden-by-default JSON and reliable toggle behavior.

---

## Traceability

**Source Documents:**
- User request (2026-04-17) in Engineering Lead run input

**Related ADRs:**
- None yet

**Implementation Files:**
- `scripts/pallet_coach/diagram.py`
- `scripts/pallet_coach/artifacts.py`
- `UI/pallet_coach_ui/src/pages/Run.tsx`

---

## Open Questions

- Should exploded-layer gap be user-configurable in the UI or fixed by design token?
- Should the high-resolution artifact be generated on solve by default or on-demand?

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** `specs/implementation-plans/RF-009-high-resolution-3d-isometric-layer-visualization-implementation-plan.md`

### Files Modified
- `scripts/pallet_coach/diagram.py`
- `scripts/pallet_coach/api/app.py`
- `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
- `UI/pallet_coach_ui/src/pages/Run.tsx`
- `scripts/tests/test_diagram_rendering.py`
- `scripts/tests/test_artifact_pipeline.py`
- `UI/pallet_coach_ui/src/pages/Run.test.tsx`

### Validation Evidence
- Backend tests: `39 passed, 2 warnings`
- Eval harness: `6 passed, 0 failed` (`--include-sample-parity`)
- Frontend tests: `15 passed`
- Frontend build: successful

### Acceptance Criteria Coverage
- High-resolution isometric exploded 3D deterministic artifact added: `isometric_exploded_3d.png`
- Layer separation implemented via deterministic exploded gap policy in renderer
- Wooden pallet base retained and stable isometric camera settings used
- Run UI supports JSON show/hide with default hidden state
- Existing flat and 3D diagram flows preserved without regression
