# Feature: UI Design System - Precision Industrial Dark

**Feature ID:** RF-006
**Status:** Implemented
**Priority:** High
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Section 11, Section 8.5-8.6)

---

## Overview

This feature specifies the canonical visual language for Pallet Coach under the "Precision Industrial Dark" theme. It defines exact color tokens, typography, layout constants, animations, and component-level styling behavior.

The design system is mandatory and must be reproduced exactly to ensure consistency with stakeholder expectations and functional readability in logistics workflows.

---

## User Stories

### US-6.1: Apply canonical global visual tokens

**As an** operations stakeholder  
**I want to** see a consistent industrial interface across all pages  
**So that** the application feels trustworthy and production-ready

**Acceptance Criteria:**
- ✅ Root CSS variables match required RGB token values exactly.
- ✅ Color usage follows `rgb(var(--token))` or `rgba(var(--token), opacity)`.
- ✅ Global scan-line overlay pseudo-element is implemented.
- ✅ Gradient-text utility and status badge visuals are implemented.

**Technical Details:**
- Global styles in app-level stylesheet
- No substitution of canonical palette values

---

### US-6.2: Enforce typography and component style contracts

**As a** supply chain analyst  
**I want to** read data-dense screens quickly  
**So that** I can make decisions with minimal cognitive load

**Acceptance Criteria:**
- ✅ IBM Plex Sans and JetBrains Mono loaded from Google Fonts with graceful fallback.
- ✅ Heading/body/label tracking and weight rules are implemented.
- ✅ Card, button, input, toggle, and table component styles match required specs.
- ✅ Numeric table cells use mono/accent style treatment.

**Technical Details:**
- Tailwind utility composition with reusable component classes
- Typography plugin enabled for markdown prose areas

---

### US-6.3: Deliver motion and layout behavior

**As a** user  
**I want to** perceive meaningful transitions and clear hierarchy  
**So that** the app feels responsive without distracting animation noise

**Acceptance Criteria:**
- ✅ `fadeInUp`, `slideInRight`, `fadeIn`, and pulse animations are defined.
- ✅ Stagger delay classes (`animate-delay-1` to `animate-delay-4`) are available.
- ✅ Home/Run pages obey max width and spacing constants.
- ✅ AppShell and HelpPanel z-index layering contracts are preserved.

**Technical Details:**
- Utility classes in global CSS and Tailwind config as needed

---

## Dependencies

### Prerequisites
- RF-005 UI route and component structure

### Related Features
- RF-004 markdown summaries rendered inside prose-themed panel

---

## Technical Architecture

### Components Involved
- Global stylesheet and Tailwind config
- Shared UI components (`Card`, `Button`, `Field`, `TextInput`, `SelectInput`, `Toggle`)

### Data Flow
1. Theme tokens initialize at app load.
2. Shared components apply consistent utility class contracts.
3. Route pages compose shared components and animation classes.

### APIs & Integrations
- Google Fonts CDN for IBM Plex Sans and JetBrains Mono

---

## Non-Functional Requirements

### Performance
- Styling and animations must remain lightweight and avoid layout thrash.

### Security
- No runtime remote script dependencies beyond font CDN.

### Scalability
- Tokenized system should support future themes via variable overrides.

---

## Implementation Notes

- Avoid arbitrary style divergence from required values.
- Keep component APIs simple and reusable for future feature growth.

---

## Test Coverage

### Unit Tests Required
- Snapshot checks for class contracts on core UI primitives
- Theme token presence test in global styles

### UAT Tests Required
- Visual QA pass against canonical color/typography/motion specs
- Responsive checks on desktop and mobile widths

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 11 (design system)
- Attached: `requirement.md` sections 8.5 and 8.6 (AppShell and HelpPanel)

**Related ADRs:**
- None yet

**Implementation Files:**
- `UI/pallet_coach_ui/src/styles/global.css`
- `UI/pallet_coach_ui/tailwind.config.ts`
- `UI/pallet_coach_ui/src/components/*`

---

## Open Questions

- None. The visual spec is explicit and complete.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** `specs/implementation-plans/RF-006-ui-design-system-precision-industrial-dark-implementation-plan.md`

### Files Created
- `UI/pallet_coach_ui/src/components/ui/Card.tsx`
- `UI/pallet_coach_ui/src/components/ui/Button.tsx`
- `UI/pallet_coach_ui/src/components/ui/Field.tsx`
- `UI/pallet_coach_ui/src/components/ui/TextInput.tsx`
- `UI/pallet_coach_ui/src/components/ui/SelectInput.tsx`
- `UI/pallet_coach_ui/src/components/ui/Toggle.tsx`
- `UI/pallet_coach_ui/src/components/ui/contracts.test.tsx`
- `UI/pallet_coach_ui/src/styles/themeTokens.test.ts`
- `UI/pallet_coach_ui/src/vite-env.d.ts`

### Files Modified
- `UI/pallet_coach_ui/src/styles/global.css`
- `UI/pallet_coach_ui/tailwind.config.ts`
- `UI/pallet_coach_ui/src/pages/Home.tsx`
- `UI/pallet_coach_ui/src/pages/Run.tsx`
- `UI/pallet_coach_ui/src/components/AppShell.tsx`
- `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
- `UI/pallet_coach_ui/src/components/SummaryPanel.tsx`
- `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
- `UI/pallet_coach_ui/src/components/OptionsTable.tsx`
- `UI/pallet_coach_ui/src/components/StackingTable.tsx`
- `UI/pallet_coach_ui/src/components/InputSummaryCard.tsx`
- `UI/pallet_coach_ui/src/components/LogsPanel.tsx`

### Validation Results
- ✅ `cd UI/pallet_coach_ui ; npm run test` (14 passed)
- ✅ `cd UI/pallet_coach_ui ; npm run build` (success)
- ✅ `c:/python314/python.exe -m pytest scripts/tests -q` (29 passed)
- ✅ `$env:PYTHONPATH="scripts"; c:/python314/python.exe eval/run_eval.py` (4 passed, 0 failed)

### Acceptance Criteria Coverage
- ✅ US-6.1 global token and overlay contracts enforced with tests.
- ✅ US-6.2 primitive component contracts implemented and adopted across Home/Run/shared components.
- ✅ US-6.3 motion and layout behavior completed (`fadeInUp`, `slideInRight`, `fadeIn`, stagger delays, HelpPanel transitions).
