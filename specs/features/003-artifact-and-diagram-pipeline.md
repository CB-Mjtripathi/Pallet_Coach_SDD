# Feature: Artifact Pipeline and Diagram Rendering

**Feature ID:** RF-003
**Status:** Implemented
**Priority:** High
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Sections 6, 9.3, 10)

---

## Overview

This feature defines deterministic run artifacts, bundle schema persistence, and all required native diagram outputs for run consumption and compliance traceability. Every solve call writes a complete run package under `04_Output/<run_id>/`.

It includes rendering standards for top-down and 3D diagrams using Matplotlib Agg backend and fixed color palette semantics.

---

## User Stories

### US-3.1: Persist complete run bundles

**As a** supply chain analyst  
**I want to** receive a consistent run directory with all mandatory files  
**So that** every recommendation is auditable and exportable

**Acceptance Criteria:**
- ✅ Every successful solve writes mandatory artifacts listed in requirement.md section 6.1.
- ✅ `bundle.json` includes request, recommender, stacking, artifacts, AI assist, and provenance blocks.
- ✅ Run log is append-only and timestamped.
- ✅ Run IDs follow `R{n:04d}_{YYYYMMDD}` with daily monotonic increment.

**Technical Details:**
- Bundle schema must match requirement.md section 9.3
- Artifact keys and filenames must remain stable for UI compatibility

---

### US-3.2: Render deterministic non-AI diagrams

**As an** operations manager  
**I want to** view clear visual before/after placement diagrams  
**So that** I can compare current and recommended palletization quickly

**Acceptance Criteria:**
- ✅ `render_layer_png(...)` outputs top-down layer with labels and dimension lines.
- ✅ `render_comparison_flat_png(...)` outputs BEFORE vs AFTER side-by-side.
- ✅ `render_comparison_3d_png(...)` outputs BEFORE vs AFTER 3D comparison.
- ✅ `render_onpallet_3d_png(...)` outputs single isometric stacked pallet image.
- ✅ All outputs are PNG at >=150 dpi and generated with Matplotlib Agg backend.

**Technical Details:**
- Module: `scripts/pallet_coach/diagram.py`
- Must use exact color tokens in requirement.md section 6.2

---

### US-3.3: Infer baseline grid for BEFORE panel

**As a** logistics engineer  
**I want to** compare recommendation against inferred baseline layout  
**So that** the improvement narrative is grounded even without explicit baseline coordinates

**Acceptance Criteria:**
- ✅ If `baseline_cases_per_layer` exists, infer plausible `(nx, ny)` using aspect ratio.
- ✅ Candidate factor pairs are scored by footprint plausibility and grid balance.
- ✅ Inferred baseline is used only for BEFORE panel rendering and never injected as solver output.

**Technical Details:**
- Baseline inference utility scoped to diagram subsystem only

---

## Dependencies

### Prerequisites
- RF-001 solver metrics (`inner_axis_segments_mm`, edge clearance, interlock)
- RF-002 API solve orchestration

### Related Features
- RF-004 AI diagrams append to artifact set
- RF-005 run page consumes all diagram assets

---

## Technical Architecture

### Components Involved
- `diagram.py`: renderers and baseline inference
- Bundle writer utilities for artifact indexing
- Run log writer

### Data Flow
1. Solve result selected and mapped to best recommendation.
2. Mandatory diagrams rendered and stored in run directory.
3. Summary markdown and prompt files generated.
4. Bundle artifact pointers updated atomically.

### APIs & Integrations
- Invoked by `POST /api/solve` pipeline and `POST /api/diagram` for AI diagrams

---

## Non-Functional Requirements

### Performance
- Each diagram should complete within 3 seconds target.

### Security
- Only write files inside active run directory.

### Scalability
- Renderer design should support future async worker offload.

---

## Implementation Notes

- Use fixed axis orientation and coordinate conventions from business rules.
- Render tolerance zones with explicit ok/warn/fail color mapping.

---

## Test Coverage

### Unit Tests Required
- Artifact file presence checks after solve
- Color/status mapping tests for tolerance zone overlays
- Baseline inferred grid selection tests

### UAT Tests Required
- Human-readable diagram comparison for representative scenarios
- A4 print-readability check at generated DPI

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 6 (artifact pipeline and rendering)
- Attached: `requirement.md` section 9.3 (`bundle.json` schema)

**Related ADRs:**
- None yet

**Implementation Files:**
- `scripts/pallet_coach/diagram.py`
- `scripts/pallet_coach/*` bundle writer modules

---

## Open Questions

- Whether PNG compression tuning should prioritize file size or maximum visual fidelity by default.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Delivery Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** specs/implementation-plans/RF-003-artifact-and-diagram-pipeline-implementation-plan.md

### Files Created
- scripts/pallet_coach/diagram.py
- scripts/pallet_coach/artifacts.py
- scripts/tests/test_artifact_pipeline.py
- scripts/tests/test_diagram_rendering.py

### Files Modified
- scripts/pallet_coach/api/app.py
- scripts/requirements.txt

### Validation Results
- Unit/integration tests: 21 passed, 0 failed
- Eval harness: 4 passed, 0 failed

### Outcome
- Mandatory RF-003 deterministic artifacts are generated during `/api/solve`.
- Native diagram pipeline is implemented with Matplotlib Agg and print-targeted DPI.
- Baseline inferred grid logic is implemented for BEFORE comparison rendering only.
