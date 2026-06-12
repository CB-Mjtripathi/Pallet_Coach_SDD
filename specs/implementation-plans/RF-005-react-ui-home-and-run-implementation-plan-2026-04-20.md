# Implementation Plan: React UI Home and Run Experience
**Feature ID:** RF-005  
**Generated:** 2026-04-20  
**Agent:** Tech Lead v1.0  
**Approach:** ENHANCEMENT / REFINEMENT

---

## Executive Summary

**Feature:** React UI Home and Run Experience  
**Status:** Fully Implemented (with refinement opportunities)  
**Implementation Approach:** Enhancement / Refinement  
**Estimated Complexity:** Medium  
**Risk Level:** Medium

**Summary:**
RF-005 is fully implemented in the current codebase across routing, Home submit workflow, Run results workflow, and shared shell/help affordances. The current request context and recent UI parity updates indicate a refinement phase rather than net-new feature development. This plan documents current coverage, preservation boundaries, and targeted enhancements to maintain behavior while improving visual/layout consistency.

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
**Feature ID:** RF-005  
**Feature Name:** React UI Home and Run Experience  
**Priority:** Critical  
**Complexity:** Medium

## Scope Summary
RF-005 defines the complete user-facing React workflow for collecting pallet inputs on Home and reviewing optimization outputs on Run. It includes API orchestration, artifact and summary presentation, diagram actions, table-based decision support, bundle export, and run log visibility.

## Key Requirements
1. Home route supports sectioned input flow with validation and canonical unit normalization.
2. Submit sequence is solve first, then summary generation, then route transition to run view.
3. Run route loads bundle and logs, renders summary/diagrams/options/stacking/input cards.
4. Diagram generation and summary regeneration actions remain available.
5. AppShell and HelpPanel deliver robust navigation and onboarding affordances.

## User Stories Summary
- **US-5.1:** Configure inputs and submit optimization request from Home.
- **US-5.2:** Inspect and compare run outputs on Run.
- **US-5.3:** Navigate with AppShell and HelpPanel affordances.

## Technical Specifications
- **APIs Required:** `/api/solve`, `/api/summary_ui`, `/api/diagram`, `/api/runs/{run_id}`, `/api/runs/{run_id}/logs`, `/output/{run_id}/{filename}`
- **Data Models:** `SolvePayload`, `SolveResponse`, `Bundle`
- **Integrations:** React Router, React Markdown, JSZip/FileSaver, Vite proxy/API fetch layer
- **Performance:** non-blocking loading states for summary/diagram actions

## Dependencies
- **Prerequisites:** RF-002, RF-003, RF-004
- **Related Features:** RF-006 (design system), RF-009 (isometric diagram support surfaced on Run)

## Complexity Assessment
**Estimated Complexity:** Medium  
**Reasoning:**
- Number of user stories: 3
- Number of modules involved: 10+
- External integrations: moderate (API + artifact serving + markdown + zip export)
- Data model complexity: moderate
- UI complexity: moderate-high

---

## Components Required (RF-005)

### Backend Services
- [x] Existing API consumption only (frontend calls backend endpoints)
- [x] Existing service modification not required for RF-005 baseline
- [ ] New agent/LLM integration not required (already handled by backend RF-004)
- [x] Frontend workflow orchestration logic implemented

### Data Layer
- [x] Existing bundle/log/artifact models consumed
- [ ] No new DB schema required

### API Integration
- [x] Solve endpoint integration
- [x] Summary UI endpoint integration
- [x] Diagram endpoint integration
- [x] Run and logs retrieval integration

### UI Components
- [x] Home page
- [x] Run page
- [x] Diagram carousel and data tables
- [x] Help panel and app shell
- [x] File export/download workflow

### Business Logic
- [x] Validation and normalization
- [x] Submit sequencing and warning handoff
- [x] State management for run actions and loading states

---

## Implementation Status

## Search Results Analysis

### Files Found

#### UI Routes and Shell
- `UI/pallet_coach_ui/src/routes.tsx`
  - Defines `/` and `/runs/:runId`
  - Match Level: Exact
- `UI/pallet_coach_ui/src/components/AppShell.tsx`
  - Sticky shell/header and help trigger
  - Match Level: Exact
- `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
  - Right drawer, Escape/backdrop close, focus behavior
  - Match Level: Exact

#### Home Workflow
- `UI/pallet_coach_ui/src/pages/Home.tsx`
  - `postSolve` + `postSummaryUi` + route navigate flow
  - Match Level: Exact
- `UI/pallet_coach_ui/src/lib/normalization.ts`
  - Canonical payload mapping and unit conversion logic
  - Match Level: Exact
- `UI/pallet_coach_ui/src/lib/validation.ts`
  - Positive number validation helpers
  - Match Level: Exact

#### Run Workflow
- `UI/pallet_coach_ui/src/pages/Run.tsx`
  - Bundle/log loading, summary panel, diagram carousel, options/stacking/input cards, JSON toggle, log panel
  - Match Level: Exact
- `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
  - Flat/3D/isometric tab behavior and generation action
  - Match Level: Exact
- `UI/pallet_coach_ui/src/lib/exportZip.ts`
  - Bundle ZIP export path
  - Match Level: Exact

#### API Endpoints Layer
- `UI/pallet_coach_ui/src/api/endpoints.ts`
  - solve/summary/diagram/run/log/artifact presence checks
  - Match Level: Exact

#### Tests
- `UI/pallet_coach_ui/src/pages/Home.test.tsx`
- `UI/pallet_coach_ui/src/pages/Run.test.tsx`
  - Match Level: Partial-to-exact coverage (key workflows present)

### Summary of Findings
- **Total highly relevant files:** 12+
- **Implementation state:** Feature behavior present end-to-end
- **Primary gap type:** refinement/documentation/tests breadth, not core feature absence

## Implementation Status: Fully Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-5.1 | Implemented | Home route validation, solve/summary sequence, navigate to run | Minor UX copy/layout refinements only |
| US-5.2 | Implemented | Run route data load, summary, diagrams, tables, logs, export | Expand regression tests for edge cases |
| US-5.3 | Implemented | AppShell and HelpPanel interactions | Continue accessibility hardening and parity tuning |

### Coverage Summary
- **Implemented:** 3 / 3 user stories (100%)
- **Partially Implemented:** 0
- **Not Implemented:** 0

### Recommendation
**Primary Approach:** ENHANCEMENT / REFINEMENT

**Reasoning:**
No missing RF-005 capability blocks were found. Work should focus on visual/layout consistency, non-regression, and hardening tests.

---

## Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Home submit workflow | Solve -> summary -> navigate | `src/pages/Home.tsx`, `src/lib/normalization.ts` | Implemented |
| Run bundle and logs rendering | Load run and logs, render sections | `src/pages/Run.tsx`, `src/api/endpoints.ts` | Implemented |
| Diagram interactions | Flat/3D generation triggers + tabs | `src/components/DiagramCarousel.tsx`, `src/pages/Run.tsx` | Implemented |
| Summary handling | Show UI summary and regenerate | `src/components/SummaryPanel.tsx`, `src/pages/Run.tsx` | Implemented |
| Shell/help affordance | Sticky shell + closable help drawer | `src/components/AppShell.tsx`, `src/components/HelpPanel.tsx` | Implemented |
| Bundle export | Download all artifacts | `src/lib/exportZip.ts`, `src/pages/Run.tsx` | Implemented |

### Gap Analysis
**What Exists:**
- Complete RF-005 functional flow
- Route and endpoint wiring
- Core unit/route tests

**What’s Missing / Recommended:**
- Broader tests around failure paths and warning propagation
- Additional UX/accessibility checks for keyboard and screen-reader semantics
- Documentation update reflecting recent parity-oriented layout refinements

---

## Impact Analysis

## Affected Modules (Enhancement Scope)

### UI Layer
- `UI/pallet_coach_ui/src/pages/Home.tsx`
  - **Change Type:** Modification
  - **Impact Level:** Medium
- `UI/pallet_coach_ui/src/pages/Run.tsx`
  - **Change Type:** Modification
  - **Impact Level:** High
- `UI/pallet_coach_ui/src/components/AppShell.tsx`
  - **Change Type:** Modification
  - **Impact Level:** Medium
- `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
  - **Change Type:** Modification
  - **Impact Level:** Medium

### Styling and Primitives
- `UI/pallet_coach_ui/src/styles/global.css`
  - **Change Type:** Modification
  - **Impact Level:** Medium

### Tests
- `UI/pallet_coach_ui/src/pages/Home.test.tsx`
- `UI/pallet_coach_ui/src/pages/Run.test.tsx`
  - **Change Type:** Modification
  - **Impact Level:** Medium

## Features That Must NOT Be Impacted

1. **Canonical payload contract and solve workflow**
- Preserve `postSolve` payload shape and normalization behavior.

2. **Run actions and artifact retrieval**
- Preserve summary regenerate, diagram generation, bundle export, and logs retrieval.

3. **RF-009 visualization tab availability**
- Preserve isometric exploded option in run diagram experience.

## Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| UI regression | Medium | Layout updates may displace controls | Keep behavior handlers untouched; validate with tests |
| Action breakage | Medium | Refactors may disconnect event handlers | Route tests + manual run smoke checks |
| Test coverage gap | Medium | Existing tests cover core happy path only | Add warning/failure path assertions |
| Accessibility drift | Low-Medium | Styling changes can affect keyboard/focus flow | Validate HelpPanel and key controls manually |

### Specific Risks

#### Risk 1: Run page composition changes hide key controls
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** enforce explicit sections and role-based test assertions for key buttons.

#### Risk 2: Home CTA text changes break brittle tests
- **Probability:** High
- **Impact:** Low
- **Mitigation:** prefer role + semantic expectations and update tests alongside UI copy changes.

---

## Development Plan

## Implementation Approach: ENHANCEMENT / REFINEMENT

### Rationale
RF-005 requirements are functionally satisfied; refinement work should preserve APIs and behavior while improving consistency and resilience.

### Files to MODIFY (if continuing refinement)

1. `UI/pallet_coach_ui/src/pages/Home.tsx`
- Keep request normalization and submit orchestration intact.
- Refine section composition and messaging only.

2. `UI/pallet_coach_ui/src/pages/Run.tsx`
- Preserve data loading/actions.
- Refine section hierarchy and readability.

3. `UI/pallet_coach_ui/src/components/AppShell.tsx`
- Maintain sticky shell/help behavior.
- Refine visual hierarchy and status indicators.

4. `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
- Maintain close/focus behavior.
- Improve instructional sequencing content.

5. `UI/pallet_coach_ui/src/styles/global.css`
- Tune visual consistency and animation pacing.

6. `UI/pallet_coach_ui/src/pages/Home.test.tsx`
7. `UI/pallet_coach_ui/src/pages/Run.test.tsx`
- Expand behavior assertions and keep selectors robust.

### Files to CREATE (optional hardening)

1. `UI/pallet_coach_ui/src/pages/Run.actions.test.tsx`
- Validate summary regenerate and diagram generation failure/success handling.

2. `UI/pallet_coach_ui/src/components/HelpPanel.a11y.test.tsx`
- Validate keyboard close and focus expectations.

---

## Testing Strategy

### Required Validation
1. `cd UI/pallet_coach_ui && npm test -- --run`
2. `cd UI/pallet_coach_ui && npm run build`
3. Manual UI smoke test:
- Home submit flow to run route
- Run summary regenerate
- Run diagram generation action
- JSON show/hide toggle
- Bundle download trigger

### Regression Guardrails
- No changes to endpoint URLs or payload keys.
- Maintain existing route paths (`/`, `/runs/:runId`).
- Keep isometric diagram tab visible and functioning.

---

## Developer Checklist

### Preparation
- [ ] Review RF-005 feature spec.
- [ ] Review current Home/Run/AppShell/HelpPanel implementation.

### Refinement Implementation
- [ ] Preserve business behavior in Home submit flow.
- [ ] Preserve all Run actions and data rendering.
- [ ] Apply visual/layout improvements only where required.
- [ ] Ensure HelpPanel keyboard and backdrop close behavior remains intact.

### Testing
- [ ] Run frontend tests and fix regressions.
- [ ] Run frontend build.
- [ ] Perform manual smoke test for Home->Run workflow and run actions.

### Completion
- [ ] Update implementation notes if refinements were shipped.
- [ ] Ensure no regressions in RF-006 and RF-009-linked UI behaviors.

---

## Current Assessment Outcome (2026-04-20)

RF-005 is fully implemented and operational. Any new work should be tracked as refinement/hardening tasks under enhancement scope rather than as missing feature implementation.

---

**END OF IMPLEMENTATION PLAN**
