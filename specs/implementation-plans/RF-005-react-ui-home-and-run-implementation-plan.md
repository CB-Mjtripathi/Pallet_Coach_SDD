# Implementation Plan: React UI Home and Run Experience
**Feature ID:** RF-005  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** FROM SCRATCH (UI) + Minor Integration Alignment

---

## Executive Summary

**Feature:** React UI Home and Run Experience  
**Status:** Not Implemented  
**Implementation Approach:** FROM SCRATCH  
**Estimated Complexity:** Very High  
**Risk Level:** High

**Summary:**
RF-005 defines the full product UI for Step 1 MVP and currently has no implementation in the repository. The backend API and run artifact pipeline (RF-002 to RF-004) are available and can be consumed directly, so the main effort is creating a new React + TypeScript + Vite + Tailwind application in `UI/pallet_coach_ui` and implementing Home and Run workflows exactly as specified. The plan below maps each required section, endpoint interaction, formatter, and UX behavior to concrete files and tests.

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
**Feature ID:** RF-005  
**Feature Name:** React UI Home and Run Experience  
**Priority:** Critical  
**Complexity:** Very High

### Scope Summary
RF-005 introduces the complete web frontend with two routes (`/` and `/runs/:runId`) and required workflows for submitting canonical solve requests, visualizing deterministic and optional AI artifacts, and exporting run outputs. It also requires app-shell UX affordances and interoperability with RF-004 AI actions.

### Key Requirements
1. Build React + TypeScript (strict) app using Vite and Tailwind.
2. Implement Home route form in exact required order with unit toggles, validation, normalization, and submit sequencing.
3. Implement Run route with bundle loading, optional AI summary panel, diagram carousel with AI triggers, options table mapping, stacking table, input summary, export ZIP, and logs panel.
4. Implement AppShell sticky header and HelpPanel drawer behavior with keyboard and backdrop close.
5. Preserve backend contract field names and endpoint payloads.

### User Stories Summary
- **US-5.1:** Home page captures and validates request inputs, normalizes units, and submits solve flow.
- **US-5.2:** Run page renders bundle-derived insights, diagrams, AI actions, and export/log utilities.
- **US-5.3:** AppShell and HelpPanel provide discoverability, status context, and accessibility behaviors.

### Technical Specifications
- **APIs Required:**
  - `POST /api/solve`
  - `POST /api/summary_ui`
  - `POST /api/diagram`
  - `GET /api/runs/{run_id}`
  - `GET /api/runs/{run_id}/logs`
  - `GET /output/{run_id}/{filename}` (+ HEAD checks)
- **Frontend Stack:** React 18+, TypeScript strict, Vite 7+, Tailwind 3+, React Router, React Markdown, Remark GFM, JSZip, File Saver.
- **Normalization Rules:** `inch->mm` rounding; `lbs->kg` rounding to 3 decimals.
- **Validation:** positive integers for dimensions/layers; positive finite for optional weights.

### Dependencies
- **Prerequisites:** RF-002 API, RF-003 deterministic artifacts, RF-004 optional AI endpoints.
- **Related Features:** RF-006 design-system specification consumed as styling baseline.

### Complexity Assessment
**Estimated Complexity:** Very High  
**Reasoning:**
- Number of user stories: 3 (broad and UI-heavy)
- Number of new modules/components: 15+
- External integrations: 6 backend endpoints + router state handoff
- Data model complexity: moderate (bundle shape, formatters, derived fields)
- UI complexity: high (forms, tables, tabs, markdown, async actions, export)

---

## Implementation Status

### Search Results Analysis

#### UI Code Presence
- No `UI/` frontend project found.
- No `*.tsx`, `*.ts`, `*.jsx`, `*.js`, `*.css`, or `*.html` application files found in the workspace.

#### Backend Readiness (for integration)
- `scripts/pallet_coach/api/app.py` provides solve/run/log/output routes and RF-004 AI endpoints.
- `scripts/pallet_coach/api/models.py` defines request/response contracts.
- RF-003 artifact generation is available and validated.

### Implementation Status: Not Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-5.1 | Not Implemented | None | Full Home form route, validation, normalization, submit flow missing |
| US-5.2 | Not Implemented | None | Full Run route, data presentation, AI actions, export/log panels missing |
| US-5.3 | Not Implemented | None | AppShell and HelpPanel components missing |

### Coverage Summary
- **Implemented:** 0 / 3 user stories
- **Partially Implemented:** 0
- **Not Implemented:** 3

### Recommendation
**Primary Approach:** FROM SCRATCH  
**Reasoning:** UI codebase does not exist; build a new frontend application and integrate with existing backend APIs.

### Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Home route form workflow | Section order + validation + normalization + submit chain | None | Missing |
| Run route rendering | Bundle fetch, tables, diagrams, AI actions, logs | None | Missing |
| App shell/help drawer | Sticky shell + drawer interactions | None | Missing |
| Bundle export | ZIP download with artifacts | None | Missing |
| AI action wiring | `/api/summary_ui`, `/api/diagram` call flows | Backend endpoints exist; UI absent | Missing |

---

## Impact Analysis

### Affected Modules

#### New Frontend Workspace
- **Folder:** `UI/pallet_coach_ui/`
  - **Change Type:** New Project
  - **Impact Level:** High
  - **Reason:** Entire RF-005 scope delivered here.

#### Backend API Compatibility
- **File:** `scripts/pallet_coach/api/app.py`
  - **Change Type:** Optional Minor Alignment
  - **Impact Level:** Low to Medium
  - **Reason:** Only if UI contract mismatches discovered during implementation.

#### Documentation and Integration
- **Files:** root README or UI README (new)
  - **Change Type:** New/Modified
  - **Impact Level:** Low
  - **Reason:** Developer run instructions and proxy configuration.

### Integration Points

#### Internal Dependencies
- **Depends On RF-002:** run retrieval and logs endpoints.
- **Depends On RF-003:** deterministic artifact filenames and bundle schema.
- **Depends On RF-004:** optional AI regenerate and AI diagram endpoints.

#### External Dependencies
- npm packages:
  - `react`, `react-dom`, `typescript`, `vite`
  - `tailwindcss`, `postcss`, `autoprefixer`, `@tailwindcss/typography`
  - `react-router-dom`
  - `react-markdown`, `remark-gfm`
  - `jszip`, `file-saver`
- Browser APIs: `fetch`, `Blob`, `URL.createObjectURL`

### Features That Must NOT Be Impacted

1. **RF-001 Solver correctness**
   - Preserve backend request schema and do not introduce contract drift.
2. **RF-002/RF-003 run and artifact guarantees**
   - Do not rely on mutable filenames; consume stable artifact keys.
3. **RF-004 optional AI behavior**
   - Frontend must handle AI errors as non-blocking warnings where specified.

### Risk Assessment

### Overall Risk Level: High

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Scope Breadth | High | Entire UI from zero baseline | staged component delivery with smoke checks |
| Contract Coupling | Medium | UI mappings tied to bundle schema | typed API client and contract tests |
| Async UX Flows | High | multi-step submit/regenerate/generate flows | explicit loading/error states per action |
| Test Coverage Gap | High | no existing frontend tests | add unit + component + flow tests early |
| Dependency Setup | Medium | new Node toolchain in repo | pin versions and include setup docs |

#### Specific Risk 1: Run-page field mismatch with backend bundle
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** add mapping layer (`src/lib/mappers.ts`) with safe fallbacks; test against sample bundle fixture.

#### Specific Risk 2: Non-blocking summary handoff not preserved
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** implement `POST /api/summary_ui` as try/catch fire-and-forget and pass warning in router state.

#### Specific Risk 3: Bundle ZIP export fails on mixed artifact availability
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** use artifact existence checks and skip missing files gracefully.

---

## Development Plan

## Implementation Approach: FROM SCRATCH (UI) + Minor Integration Alignment

### Rationale
No UI code currently exists. Build a new frontend project under `UI/pallet_coach_ui` and wire it to existing backend endpoints.

### Strategy Summary
- **New Components:** 15 to 20
- **Modified Components:** 0 to 2 (only if backend alignment becomes necessary)
- **Unchanged Components:** RF-001 to RF-004 backend core logic

## Files to CREATE

### 1. Project Scaffold
- `UI/pallet_coach_ui/package.json`
- `UI/pallet_coach_ui/tsconfig.json`
- `UI/pallet_coach_ui/vite.config.ts`
- `UI/pallet_coach_ui/index.html`
- `UI/pallet_coach_ui/postcss.config.js`
- `UI/pallet_coach_ui/tailwind.config.ts`
- `UI/pallet_coach_ui/src/main.tsx`
- `UI/pallet_coach_ui/src/App.tsx`
- `UI/pallet_coach_ui/src/styles/global.css`

### 2. Routing and Layout
- `UI/pallet_coach_ui/src/routes.tsx`
- `UI/pallet_coach_ui/src/components/AppShell.tsx`
- `UI/pallet_coach_ui/src/components/HelpPanel.tsx`

### 3. Home Route and Form Modules
- `UI/pallet_coach_ui/src/pages/Home.tsx`
- `UI/pallet_coach_ui/src/lib/validation.ts`
  - `parsePositiveInt`, `parseFiniteNumber`
- `UI/pallet_coach_ui/src/lib/normalization.ts`
  - unit conversion helpers and canonical request builder
- `UI/pallet_coach_ui/src/lib/palletPresets.ts`

### 4. Run Route and Data Components
- `UI/pallet_coach_ui/src/pages/Run.tsx`
- `UI/pallet_coach_ui/src/components/SummaryPanel.tsx`
- `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
- `UI/pallet_coach_ui/src/components/OptionsTable.tsx`
- `UI/pallet_coach_ui/src/components/StackingTable.tsx`
- `UI/pallet_coach_ui/src/components/InputSummaryCard.tsx`
- `UI/pallet_coach_ui/src/components/LogsPanel.tsx`

### 5. API and Utility Layer
- `UI/pallet_coach_ui/src/api/client.ts`
- `UI/pallet_coach_ui/src/api/types.ts`
- `UI/pallet_coach_ui/src/api/endpoints.ts`
- `UI/pallet_coach_ui/src/lib/formatters.ts`
  - pattern label parsing (`grid_*_rot*` handling)
- `UI/pallet_coach_ui/src/lib/exportZip.ts`
  - JSZip + FileSaver helper for run artifact export

### 6. Tests
- `UI/pallet_coach_ui/src/lib/normalization.test.ts`
- `UI/pallet_coach_ui/src/lib/validation.test.ts`
- `UI/pallet_coach_ui/src/lib/formatters.test.ts`
- `UI/pallet_coach_ui/src/pages/Home.test.tsx`
- `UI/pallet_coach_ui/src/pages/Run.test.tsx`

### 7. Frontend Docs
- `UI/pallet_coach_ui/README.md`
  - local setup, backend URL/proxy, build and test commands.

## Files to MODIFY (Conditional)

### 1. Backend Alignment (only if required)
- `scripts/pallet_coach/api/models.py` and/or `scripts/pallet_coach/api/app.py`
  - Only if strict UI contract requires small compatibility field aliases.
  - Prefer frontend mapping/fallback instead of backend mutation.

---

## Integration Strategy

### API Base URL and Proxy
- Configure Vite dev proxy to backend (default `http://localhost:8000`), preserving relative `/api` and `/output` paths.

### Home Submit Sequence
1. Validate fields in real time.
2. Build canonical payload with normalization and fixed tolerances + `auto_underhang=true`.
3. `POST /api/solve` and await response.
4. Fire-and-forget `POST /api/summary_ui` using returned run id; capture warning if it fails.
5. Navigate to `/runs/:runId` with warning in router state.

### Run Data Loading and Actions
1. Load bundle via `GET /api/runs/:runId`.
2. Probe image artifacts using HEAD requests on `/output/:runId/:filename`.
3. Trigger AI summary regenerate and AI diagram generation with loading/error states.
4. Reload relevant sections after successful AI actions.

### Data Mapping Rules
- Top 5 options from `bundle.recommender.solutions.slice(0,5)`.
- Pattern format:
  - strip `grid_`
  - strip `_interlock` suffix
  - map `_rot{n}` to `{n} deg`
- Total layers: `round(total_cases / cases_per_layer)`.
- Weight conversion displayed in selected unit.
- Derived recommended-max height: `pallet_height_mm + recommended_max * case_height_mm`.

---

## Testing Strategy

### Unit and Component Tests
1. Normalization tests for inch/lbs conversions and canonical payload shape.
2. Validation tests for submit-disable logic and field parsing helpers.
3. Formatter tests for pattern labels and table display values.
4. Home route tests for submit sequence and warning handoff behavior.
5. Run route tests for bundle rendering, AI action triggers, and fallback states.

### UAT Scenarios
1. Home submit with valid data -> run page navigation and initial artifacts visible.
2. Home submit with invalid required fields -> submit disabled.
3. Run page regenerate summary -> summary panel refreshes.
4. Run page generate AI diagram for both tabs -> image refreshes.
5. Download bundle -> ZIP contains expected available artifact files.
6. Logs panel loads and displays run log text.

### Validation Commands (Frontend)
- `npm install`
- `npm run dev`
- `npm run test`
- `npm run build`

### Validation Commands (Backend regression)
- `c:/python314/python.exe -m pytest scripts/tests -q`
- `c:/python314/python.exe eval/run_eval.py`

---

## Developer Checklist

### Preparation
- [ ] Create frontend workspace at `UI/pallet_coach_ui`
- [ ] Initialize React + TS + Vite + Tailwind stack
- [ ] Configure router and API base/proxy

### Implementation
- [ ] Implement AppShell and HelpPanel behavior
- [ ] Implement Home route form sections in required order
- [ ] Implement validation and normalization utilities
- [ ] Implement solve submit flow + summary_ui warning handoff
- [ ] Implement Run route data loading and section ordering
- [ ] Implement summary panel with markdown rendering and regenerate
- [ ] Implement diagram tabs and AI diagram triggers
- [ ] Implement options and stacking tables with required mappings
- [ ] Implement input summary card and logs panel
- [ ] Implement ZIP export utility

### Testing
- [ ] Add frontend unit/component tests
- [ ] Validate all acceptance criteria workflows
- [ ] Run frontend build and test commands
- [ ] Re-run backend tests to confirm no regressions

### Validation and Completion
- [ ] Confirm strict TypeScript mode passes
- [ ] Confirm responsive behavior on desktop/mobile
- [ ] Update RF-005 feature status after implementation
- [ ] Create RF-005 implementation-complete report

---

## Troubleshooting Guide

**Issue:** CORS/proxy failures in dev  
**Fix:** set Vite proxy for `/api` and `/output`; ensure backend runs on expected host/port.

**Issue:** Missing artifact image on run page  
**Fix:** probe artifact existence via HEAD and render fallback placeholders.

**Issue:** Bundle field shape drift  
**Fix:** centralize mapping in typed adapter functions and default safely.

**Issue:** AI action failures blocking UX  
**Fix:** keep non-blocking warning pattern and independent loading/error state per action.

---

## Additional Resources

- Feature specification: `specs/features/005-react-ui-home-and-run.md`
- Requirements source: `requirement.md` sections 8, 9, 11
- Related design system feature: `specs/features/006-ui-design-system-precision-industrial-dark.md`
- Backend API entrypoint: `scripts/pallet_coach/api/app.py`

---

**END OF IMPLEMENTATION PLAN**
