# Feature: React UI Home and Run Experience

**Feature ID:** RF-005
**Status:** Implemented
**Priority:** Critical
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Section 8, Sections 9 and 11)

---

## Overview

This feature defines the complete user-facing web application experience for Pallet Coach using React + TypeScript + Vite + Tailwind. It includes the Home input workflow and Run results workflow with artifact viewing, AI summary rendering, diagram generation triggers, options comparison, stacking analysis, and bundle export.

The UI enforces unit normalization, input validation, submit sequencing, and transparent presentation of deterministic + optional AI outputs.

---

## User Stories

### US-5.1: Submit pallet optimization request from Home page

**As a** logistics engineer  
**I want to** configure case, pallet, and stack inputs with unit toggles  
**So that** I can run optimization from one guided form

**Acceptance Criteria:**
- ✅ Home route (`/`) implements sectioned form in required order.
- ✅ Unit toggles support `mm|inch` and `kg|lbs` with defaults `mm`, `kg`.
- ✅ Case dimensions and layers are validated as positive integers.
- ✅ Optional weight fields are validated as positive finite numbers.
- ✅ UI normalizes units before POST (`inch→mm`, `lbs→kg`) and posts canonical request.
- ✅ UI sends `auto_underhang=true` and zeroed tolerance fields as specified.
- ✅ Submit triggers `/api/solve`, then fire-and-forget `/api/summary_ui`, then navigates to `/runs/:runId`.

**Technical Details:**
- Route component: `Home`
- Validation helpers: `parsePositiveInt`, `parseFiniteNumber`
- Presets: Euro and Industrial in Step 1

---

### US-5.2: Review and compare run outputs on Run page

**As an** operations manager  
**I want to** inspect ranked options, stack guidance, and diagrams  
**So that** I can choose adoption range and communicate change impact

**Acceptance Criteria:**
- ✅ Run route (`/runs/:runId`) loads `bundle.json` via `/api/runs/:runId`.
- ✅ AI summary panel appears when `summary_ui.md` exists and supports regenerate.
- ✅ Diagram carousel supports Flat comparison and 3D view tabs.
- ✅ Each tab has AI diagram generation trigger via `/api/diagram` with selected `view`.
- ✅ Options table shows top 5 solutions with required column mappings.
- ✅ Stacking table displays all required fields and derived recommended-max height.
- ✅ Input summary card reflects original request.
- ✅ Download bundle action zips artifacts with `jszip` + `file-saver`.
- ✅ Collapsible logs panel reads `/api/runs/:runId/logs`.

**Technical Details:**
- Route component: `Run`
- Markdown rendering: `react-markdown` + `remark-gfm`
- Artifact image existence checks via HEAD requests

---

### US-5.3: Provide robust app shell and help affordances

**As a** supply chain analyst  
**I want to** navigate and understand the tool quickly  
**So that** I can onboard without external documentation

**Acceptance Criteria:**
- ✅ AppShell contains sticky header and MVP badge elements as specified.
- ✅ Help button opens right-side HelpPanel drawer with focus management.
- ✅ Help panel closes via backdrop click, Escape, or close button.

**Technical Details:**
- Components: `AppShell`, `HelpPanel`
- Accessibility: focus trapping and keyboard close behavior

---

## Dependencies

### Prerequisites
- RF-002 API endpoints
- RF-003 artifact persistence conventions
- RF-004 optional AI endpoints

### Related Features
- RF-006 visual design system and CSS tokens

---

## Technical Architecture

### Components Involved
- React Router routes: `/` and `/runs/:runId`
- Form/state management components
- Results, table, carousel, and markdown rendering components
- Export utility for bundle ZIP

### Data Flow
1. User enters input data and passes validation.
2. UI normalizes to canonical mm/kg request shape.
3. Submit to solve endpoint and route to run page.
4. Run page fetches bundle, resolves available artifacts, renders sections.
5. Optional AI actions mutate artifacts and trigger reload.

### APIs & Integrations
- `POST /api/solve`
- `POST /api/summary_ui`
- `POST /api/diagram`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/logs`
- `GET /output/{run_id}/{filename}`

---

## Non-Functional Requirements

### Performance
- UI interactions should remain responsive while backend processes.
- Loading states required for summary/diagram generation actions.

### Security
- No secrets in frontend bundle.
- API failures surfaced as safe, user-readable non-blocking warnings where appropriate.

### Scalability
- Componentized architecture for easy extension to additional pallet presets and Phase 2 capabilities.

---

## Implementation Notes

- Keep strict TypeScript mode enabled.
- Preserve canonical field names expected by backend contracts.

---

## Test Coverage

### Unit Tests Required
- Input normalization tests (`inch→mm`, `lbs→kg`)
- Validation state tests for submit-disable behavior
- Table mapping formatters for pattern label parsing

### UAT Tests Required
- Full Home→Run flow including summary warning handoff in router state
- AI regenerate and AI diagram flows
- Download bundle integrity check

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 8 (React UI)
- Attached: `requirement.md` section 9.1 (canonical request)
- Attached: `requirement.md` section 11 (design rules consumed by RF-006)

**Related ADRs:**
- None yet

**Implementation Files:**
- `UI/pallet_coach_ui/src/pages/Home.tsx`
- `UI/pallet_coach_ui/src/pages/Run.tsx`
- `UI/pallet_coach_ui/src/components/AppShell.tsx`
- `UI/pallet_coach_ui/src/components/HelpPanel.tsx`

---

## Open Questions

- None. Section ordering and field behavior are explicit in requirements.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Delivery Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** specs/implementation-plans/RF-005-react-ui-home-and-run-implementation-plan.md

### Files Created
- UI/pallet_coach_ui/package.json
- UI/pallet_coach_ui/index.html
- UI/pallet_coach_ui/vite.config.ts
- UI/pallet_coach_ui/tailwind.config.ts
- UI/pallet_coach_ui/postcss.config.js
- UI/pallet_coach_ui/tsconfig.json
- UI/pallet_coach_ui/tsconfig.app.json
- UI/pallet_coach_ui/tsconfig.node.json
- UI/pallet_coach_ui/src/main.tsx
- UI/pallet_coach_ui/src/App.tsx
- UI/pallet_coach_ui/src/routes.tsx
- UI/pallet_coach_ui/src/styles/global.css
- UI/pallet_coach_ui/src/components/AppShell.tsx
- UI/pallet_coach_ui/src/components/HelpPanel.tsx
- UI/pallet_coach_ui/src/components/SummaryPanel.tsx
- UI/pallet_coach_ui/src/components/DiagramCarousel.tsx
- UI/pallet_coach_ui/src/components/OptionsTable.tsx
- UI/pallet_coach_ui/src/components/StackingTable.tsx
- UI/pallet_coach_ui/src/components/InputSummaryCard.tsx
- UI/pallet_coach_ui/src/components/LogsPanel.tsx
- UI/pallet_coach_ui/src/pages/Home.tsx
- UI/pallet_coach_ui/src/pages/Run.tsx
- UI/pallet_coach_ui/src/api/client.ts
- UI/pallet_coach_ui/src/api/endpoints.ts
- UI/pallet_coach_ui/src/api/types.ts
- UI/pallet_coach_ui/src/lib/validation.ts
- UI/pallet_coach_ui/src/lib/normalization.ts
- UI/pallet_coach_ui/src/lib/palletPresets.ts
- UI/pallet_coach_ui/src/lib/formatters.ts
- UI/pallet_coach_ui/src/lib/exportZip.ts
- UI/pallet_coach_ui/src/lib/normalization.test.ts
- UI/pallet_coach_ui/src/lib/validation.test.ts
- UI/pallet_coach_ui/src/lib/formatters.test.ts
- UI/pallet_coach_ui/src/pages/Home.test.tsx
- UI/pallet_coach_ui/src/pages/Run.test.tsx
- UI/pallet_coach_ui/src/test/setup.ts
- UI/pallet_coach_ui/src/README.md

### Validation Results
- Frontend tests: 10 passed, 0 failed
- Frontend build: successful
- Backend tests: 29 passed, 0 failed
- Eval harness: 4 passed, 0 failed

### Outcome
- RF-005 Home and Run routes are implemented in a new React + TypeScript + Vite UI app.
- Required request normalization, validation, and route flow sequencing are implemented.
- Run page tables, diagrams, logs panel, summary panel, and bundle export are implemented.
