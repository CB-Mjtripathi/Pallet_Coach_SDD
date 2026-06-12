# Implementation Plan: RF-006 Reference UI Parity
**Feature ID:** RF-006  
**Generated:** 2026-04-20  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Modification + Validation)

---

## Executive Summary

**Feature:** UI Design System - Precision Industrial Dark (reference parity alignment)  
**Status:** Partially Implemented for parity target  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** Medium  
**Risk Level:** Medium

**Summary:**
RF-006 core design-system contracts already exist, but the latest requirement asks for visual and layout parity with the reference repository UI. Current implementation is close in theme and components, with specific differences in section hierarchy, shell composition, and run-page information architecture. This plan focuses on controlled UI modifications while preserving existing business behavior, API contracts, and test stability.

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
**Feature ID:** RF-006  
**Feature Name:** UI Design System - Precision Industrial Dark  
**Priority:** High  
**Complexity:** Medium

### Scope Summary
The scope is parity-oriented UI refinement: align page-level layout, shell/header treatment, and content ordering to the reference product while retaining this codebase's functional behavior and endpoint wiring. Styling must continue to use tokenized CSS and shared UI primitives.

### Key Requirements
1. Match reference-level visual direction (industrial dark, typography, motion cadence).
2. Align AppShell and HelpPanel composition with reference interaction patterns.
3. Align Home route section hierarchy, hero structure, and CTA semantics.
4. Align Run route hierarchy (run metadata, summary workspace, diagrams, tables, actions, details).
5. Preserve existing functional behavior: solve flow, summary generation, diagram generation, artifact rendering, logs, and JSON details.

### User Stories Summary
- **US-6.1:** Canonical global tokens and visual utilities remain enforced.
- **US-6.2:** Typography and primitive contracts remain consistent across all route pages.
- **US-6.3:** Motion and layering support clear hierarchy and responsiveness.

### Technical Specifications
- **Primary UI files:**
  - `UI/pallet_coach_ui/src/styles/global.css`
  - `UI/pallet_coach_ui/src/components/AppShell.tsx`
  - `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
  - `UI/pallet_coach_ui/src/pages/Home.tsx`
  - `UI/pallet_coach_ui/src/pages/Run.tsx`
- **Test files impacted:**
  - `UI/pallet_coach_ui/src/pages/Home.test.tsx`
  - `UI/pallet_coach_ui/src/pages/Run.test.tsx`

### Dependencies
- **Prerequisites:** RF-005 React UI Home and Run Experience.
- **Related:** RF-009 diagram enhancements and tab behavior in Run page.

### Complexity Assessment
**Estimated Complexity:** Medium  
**Reasoning:**
- Number of user stories: 3
- Modules involved: 7
- External integrations: none new
- Data model complexity: low
- UI complexity: medium-high (parity and non-regression constraints)

---

## Implementation Status

### Search Results Analysis

#### High Relevance Findings
- `UI/pallet_coach_ui/src/styles/global.css`
  - Strong token base and animation classes present.
  - Needed parity refinements: additional hero/layout utilities and motion constants.
- `UI/pallet_coach_ui/src/components/AppShell.tsx`
  - Existing sticky shell present.
  - Needed parity refinements: reference-like branding, status language, composition.
- `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
  - Existing drawer and close behavior present.
  - Needed parity refinements: sectioned instructional content and hierarchy.
- `UI/pallet_coach_ui/src/pages/Home.tsx`
  - Existing form workflow present.
  - Needed parity refinements: hero-first layout, CTA wording, section rhythm.
- `UI/pallet_coach_ui/src/pages/Run.tsx`
  - Existing results workflow present.
  - Needed parity refinements: run hero/meta tiles and side workspace composition.

### Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-6.1 | Partial | Tokenized global CSS exists | Reference parity utilities and surface treatments |
| US-6.2 | Partial | Shared primitives and typography exist | Route-level hierarchy not fully reference-aligned |
| US-6.3 | Partial | Animations and delays exist | Motion application and section pacing need parity pass |

### Coverage Summary
- **Implemented:** 0 / 3 fully for parity objective
- **Partially Implemented:** 3 / 3
- **Not Implemented:** 0 / 3

### Recommendation
**Primary Approach:** HYBRID (Modification + Validation)

**Reasoning:**
Core functionality and design tokens already exist. Work should focus on controlled structural/UI refactor, not new architecture.

### Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Reference-like shell and identity band | Header hierarchy and status presentation | `AppShell.tsx` | Partial |
| Reference-like Help panel sequencing | Welcome/how-to/results/tips blocks | `HelpPanel.tsx` | Partial |
| Home layout parity | Hero-first and sectioned form flow | `Home.tsx` | Partial |
| Run layout parity | Hero/meta + two-column workspace | `Run.tsx` | Partial |
| Non-regression behavior | Existing API calls and interactions preserved | `Home.tsx`, `Run.tsx`, `endpoints.ts` | Partial |

---

## Impact Analysis

### Affected Modules

1. **Global styling**
- **File:** `UI/pallet_coach_ui/src/styles/global.css`
- **Change Type:** Modification
- **Impact Level:** Medium
- **Reason:** Add parity utility classes and refine visual surfaces.

2. **App shell and help overlay**
- **Files:** `UI/pallet_coach_ui/src/components/AppShell.tsx`, `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
- **Change Type:** Modification
- **Impact Level:** Medium
- **Reason:** Align top-level composition and support content.

3. **Route pages**
- **Files:** `UI/pallet_coach_ui/src/pages/Home.tsx`, `UI/pallet_coach_ui/src/pages/Run.tsx`
- **Change Type:** Modification
- **Impact Level:** High
- **Reason:** Main parity target for section hierarchy and layout rhythm.

4. **Route tests**
- **Files:** `UI/pallet_coach_ui/src/pages/Home.test.tsx`, `UI/pallet_coach_ui/src/pages/Run.test.tsx`
- **Change Type:** Modification
- **Impact Level:** Medium
- **Reason:** Text labels/structure changes require test alignment.

### Integration Points

#### Internal Dependencies
- RF-005 Home/Run behavior must remain intact.
- RF-009 isometric tab behavior must remain available and unchanged.

#### External Dependencies
- No new runtime dependency is required.

### Features That Must NOT Be Impacted

1. **Solve submission contract**
- **Location:** `UI/pallet_coach_ui/src/pages/Home.tsx`, `UI/pallet_coach_ui/src/lib/normalization.ts`
- **Preserve:** canonical payload shape and validation behavior.

2. **Run artifacts and actions**
- **Location:** `UI/pallet_coach_ui/src/pages/Run.tsx`, `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
- **Preserve:** summary/diagram actions, tabs, and bundle download.

3. **API endpoint wiring**
- **Location:** `UI/pallet_coach_ui/src/api/endpoints.ts`
- **Preserve:** endpoint paths and request contracts.

### Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Layout regression | Medium | Structural move may hide content paths | Validate all core sections after refactor |
| Action regression | Medium | Repositioned controls may break handlers | Keep handler wiring unchanged; add test assertions |
| Mobile responsiveness | Medium | New hero/meta blocks can overflow | Test at narrow viewport and adjust CSS grid |
| Snapshot/text brittleness | Low | Test selectors tied to labels | Update tests to role-based resilient queries |

---

## Development Plan

## Implementation Approach: HYBRID (Modification + Validation)

### Rationale
Implementation already exists and is functional. The requirement is parity in layout/look, so modifications should target composition and styling without altering core data flow.

### Files to MODIFY

### 1. Global style parity pass
**File:** `UI/pallet_coach_ui/src/styles/global.css`

**Required changes:**
1. Add/standardize motion tokens (`--ease-out-expo`, duration tokens).
2. Add hero and run workspace utility classes (`hero-grid`, `run-meta-grid`, `metric-*`).
3. Refine background atmosphere and card surfaces to reference style direction.
4. Keep existing token names/values and utility compatibility.

### 2. App shell parity
**File:** `UI/pallet_coach_ui/src/components/AppShell.tsx`

**Required changes:**
1. Align left brand cluster (identity + product title hierarchy).
2. Align right-side status/step treatment.
3. Preserve help trigger and page container contracts.

### 3. Help panel parity
**File:** `UI/pallet_coach_ui/src/components/HelpPanel.tsx`

**Required changes:**
1. Add structured sections: Welcome, How to Use, Reading Results, Tips.
2. Preserve close methods (Escape/backdrop/button).
3. Keep existing focus behavior and z-index layering.

### 4. Home page parity
**File:** `UI/pallet_coach_ui/src/pages/Home.tsx`

**Required changes:**
1. Introduce hero-first section with status badge and title treatment.
2. Keep form data model and submit logic unchanged.
3. Update CTA phrasing and placeholders for parity readability.

### 5. Run page parity
**File:** `UI/pallet_coach_ui/src/pages/Run.tsx`

**Required changes:**
1. Add run hero with metadata tiles.
2. Shift to two-column information workspace for summary + contextual panels.
3. Preserve diagram carousel, options table, stacking table, logs, and JSON toggle behavior.
4. Keep action handlers unchanged for summary and diagram generation.

### 6. Test alignment
**Files:** `UI/pallet_coach_ui/src/pages/Home.test.tsx`, `UI/pallet_coach_ui/src/pages/Run.test.tsx`

**Required changes:**
1. Update expected button labels and structural text assertions.
2. Keep behavior-focused checks (navigation, JSON toggle, run render).

---

## Testing Strategy

### Unit and Route Tests
- Run: `cd UI/pallet_coach_ui && npm test -- --run`
- Validate all existing tests pass after parity changes.

### Build Validation
- Run: `cd UI/pallet_coach_ui && npm run build`
- Ensure TypeScript and Vite build pass with no errors.

### Runtime Validation
- Start dev server with explicit host:
  - `npm run dev -- --host 127.0.0.1 --port 5173`
- Verify:
  - Home page renders hero + sectioned form.
  - Run page renders hero/meta, summary workspace, diagrams, tables, JSON toggle, logs.

### Regression Validation
- Confirm solve submission still routes to `/runs/:runId`.
- Confirm summary regenerate and diagram generation actions still call backend endpoints.
- Confirm isometric tab remains available.

---

## Developer Checklist

### Planning and Safety
- [ ] Review RF-006 and RF-005 specs.
- [ ] Preserve existing API contracts and request shapes.

### Implementation
- [ ] Update global CSS parity utilities and motion tokens.
- [ ] Refactor AppShell structure to reference parity.
- [ ] Refactor HelpPanel section flow and content hierarchy.
- [ ] Refactor Home hero + form presentation while preserving state/submit logic.
- [ ] Refactor Run composition while preserving all handlers and data rendering.
- [ ] Update route tests for label/structure changes.

### Validation
- [ ] Run frontend test suite and confirm pass.
- [ ] Run frontend build and confirm pass.
- [ ] Run dev server on explicit host/port and verify local access.
- [ ] Validate key workflows manually (Home submit, Run actions, JSON toggle, logs).

### Completion
- [ ] Mark RF-006 parity update complete in delivery notes.
- [ ] Attach validation outputs to implementation-complete artifact.

---

## Implementation Status Snapshot (Current)

The following parity work has already been applied in this repository as of 2026-04-20:
- AppShell, HelpPanel, Home, Run, and global CSS were refit toward reference layout/look.
- Route tests were updated and passing.
- Frontend build is passing.

This plan remains the canonical guidance and audit trail for the parity change set.

---

**END OF IMPLEMENTATION PLAN**
