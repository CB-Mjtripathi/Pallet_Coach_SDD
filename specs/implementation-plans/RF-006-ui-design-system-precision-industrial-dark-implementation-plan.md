# Implementation Plan: UI Design System - Precision Industrial Dark
**Feature ID:** RF-006  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Refinement + Componentization)

---

## Executive Summary

**Feature:** UI Design System - Precision Industrial Dark  
**Status:** Partially Implemented  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** High  
**Risk Level:** Medium

**Summary:**
RF-006 design tokens and some visual foundations were introduced during RF-005 UI delivery, but the design system is not yet fully compliant with the canonical style contract. The current UI uses partial global styles and utility classes, while missing explicit component contracts, several animation definitions, and dedicated design-system tests required by RF-006. This plan focuses on converting the existing style baseline into a fully reusable, testable, and exact-match design system.

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
**Complexity:** High

### Scope Summary
RF-006 defines canonical visual tokens and style behavior for all core UI primitives and route-level composition. It requires exact palette, typography, motion, and layout constants; reusable component style contracts; and validation coverage for visual-system integrity.

### Key Requirements
1. Enforce root token values and tokenized color usage exactly as specified.
2. Maintain global scan-line overlay and gradient text utility.
3. Enforce typography rules for body, headings, labels, and mono metric fields.
4. Implement canonical contracts for Card, Button variants, TextInput, SelectInput, Field, Toggle, and tables.
5. Define and use required animations (`fadeInUp`, `slideInRight`, `fadeIn`, pulse) and stagger classes.
6. Preserve AppShell and HelpPanel z-index and interaction contracts.
7. Add tests for token presence and core class-contract fidelity.

### User Stories Summary
- **US-6.1:** Apply canonical global visual tokens.
- **US-6.2:** Enforce typography and component style contracts.
- **US-6.3:** Deliver motion and layout behavior.

### Technical Specifications
- **Core files:** global stylesheet, tailwind config, shared components.
- **Fonts:** IBM Plex Sans + JetBrains Mono from Google Fonts CDN with graceful fallback.
- **Component coverage:** AppShell, HelpPanel, and all shared primitives used by Home/Run pages.

### Dependencies
- **Prerequisites:** RF-005 route/component structure.
- **Related features:** RF-004 markdown rendering in prose panel.

### Complexity Assessment
**Estimated Complexity:** High  
**Reasoning:**
- Number of user stories: 3
- Number of modules involved: 8 to 14
- External integrations: Google Fonts CDN only
- Data model complexity: low
- UI complexity: high (exact style contracts + reusable primitives + motion)

---

## Implementation Status

### Search Results Analysis

#### Global Styles and Tailwind
- **File:** `UI/pallet_coach_ui/src/styles/global.css`
  - **Relevance:** High
  - **What exists:** canonical token values, scan-line overlay, gradient text, basic card/button/input classes, fade-in-up animation and stagger classes.
  - **Gap level:** Partial

- **File:** `UI/pallet_coach_ui/tailwind.config.ts`
  - **Relevance:** Medium
  - **What exists:** typography plugin enabled, fade-in-up and pulse-slow animation extension.
  - **Gap level:** Partial

#### Core Layout Components
- **File:** `UI/pallet_coach_ui/src/components/AppShell.tsx`
  - **Relevance:** High
  - **What exists:** sticky header, status indicator, MVP badge, help trigger, max-width/padding constants.
  - **Gap level:** Partial (needs strict class-contract alignment and reusable primitive adoption)

- **File:** `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
  - **Relevance:** High
  - **What exists:** right drawer, backdrop close, Escape close, focus-on-open.
  - **Gap level:** Partial (animation classes referenced but not fully defined in global stylesheet)

#### Missing Design-System Assets
- No dedicated primitive component files (Card, Button, Field, TextInput, SelectInput, Toggle).
- No explicit theme-token unit tests.
- No class-contract snapshot tests for core primitives.

### Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-6.1 | Partial | Tokens, scan-line, gradient utility exist in global CSS | Missing explicit token tests and full tokenized usage consistency checks |
| US-6.2 | Partial | Fonts + some class contracts implemented | Missing reusable primitive component library and strict contract parity |
| US-6.3 | Partial | fadeInUp and stagger classes exist; shell layering mostly present | Missing full motion set (`slideInRight`, `fadeIn`) and formal layout contract validation |

### Coverage Summary
- **Implemented:** 0 / 3 full user stories
- **Partially Implemented:** 3 / 3
- **Not Implemented:** 0 / 3

### Recommendation
**Primary Approach:** HYBRID  
**Reasoning:** retain and refine existing RF-005 style foundation, then add missing primitive abstractions, animation definitions, and RF-006 specific tests.

### Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Root token exactness | canonical token values | global.css root vars present | Partial (needs tests and consistency pass) |
| Typography contract | heading/body/label/mono rules | global.css + component usage partial | Partial |
| Primitive style contracts | card/button/input/select/field/toggle/table | class usage spread across pages/components | Missing structured primitive layer |
| Motion contract | fadeInUp/slideInRight/fadeIn/pulse + delays | fadeInUp + delays + pulse partial | Partial |
| Design-system tests | token presence and class snapshots | no dedicated RF-006 tests | Missing |

---

## Impact Analysis

### Affected Modules

#### Global Styling
- **File:** `UI/pallet_coach_ui/src/styles/global.css`
  - **Change Type:** Modification
  - **Impact Level:** High
  - **Reason:** canonical definitions and missing animation contracts must be completed.

#### Tailwind Configuration
- **File:** `UI/pallet_coach_ui/tailwind.config.ts`
  - **Change Type:** Modification
  - **Impact Level:** Medium
  - **Reason:** ensure utility parity and stable class generation.

#### New Shared Primitive Layer
- **Files to add:**
  - `UI/pallet_coach_ui/src/components/ui/Card.tsx`
  - `UI/pallet_coach_ui/src/components/ui/Button.tsx`
  - `UI/pallet_coach_ui/src/components/ui/Field.tsx`
  - `UI/pallet_coach_ui/src/components/ui/TextInput.tsx`
  - `UI/pallet_coach_ui/src/components/ui/SelectInput.tsx`
  - `UI/pallet_coach_ui/src/components/ui/Toggle.tsx`
  - **Change Type:** New
  - **Impact Level:** High
  - **Reason:** centralize and enforce RF-006 style contracts.

#### Existing Component Consumption
- **Files likely to modify:**
  - `UI/pallet_coach_ui/src/components/AppShell.tsx`
  - `UI/pallet_coach_ui/src/components/HelpPanel.tsx`
  - `UI/pallet_coach_ui/src/components/SummaryPanel.tsx`
  - `UI/pallet_coach_ui/src/components/DiagramCarousel.tsx`
  - `UI/pallet_coach_ui/src/components/OptionsTable.tsx`
  - `UI/pallet_coach_ui/src/components/StackingTable.tsx`
  - `UI/pallet_coach_ui/src/pages/Home.tsx`
  - `UI/pallet_coach_ui/src/pages/Run.tsx`
  - **Change Type:** Modification
  - **Impact Level:** Medium
  - **Reason:** swap ad hoc class usage to shared primitives.

#### Test Layer
- **Files to add:**
  - `UI/pallet_coach_ui/src/styles/themeTokens.test.ts`
  - `UI/pallet_coach_ui/src/components/ui/contracts.test.tsx`
  - **Change Type:** New
  - **Impact Level:** High
  - **Reason:** RF-006 explicit unit coverage requirements.

### Integration Points

#### Internal Dependencies
- **Depends On:** RF-005 pages/components
  - **Integration Point:** shared primitive adoption without behavioral drift.

- **Related To:** RF-004 markdown panel
  - **Integration Point:** prose rendering classes and typography plugin usage.

#### External Dependencies
- Google Fonts CDN (already in use).
- No additional runtime dependencies required.

### Features That Must NOT Be Impacted

1. **RF-005 functional workflows**
   - Home submit and Run data actions must remain behaviorally identical.

2. **RF-004 optional AI interactions**
   - Summary regenerate and diagram generation controls must keep existing action flow.

3. **Backend API contract assumptions**
   - Visual-system refactor must not alter request/response payload semantics.

### Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Visual Regression | High | wide class refactor can alter appearance | create primitives and migrate incrementally with visual QA checklist |
| Behavioral Drift | Medium | replacing controls can break interactions | preserve prop contracts and add interaction smoke tests |
| Test Coverage Gap | Medium | style assertions can be brittle | test key contract tokens/classes only |
| Scope Coupling | Medium | RF-005 and RF-006 overlap | isolate RF-006 changes to styling and primitive layer |

#### Specific Risk 1: accidental layout/spacing regressions
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** enforce layout constants in primitive wrappers and route containers.

#### Specific Risk 2: missing animation/keyframe classes used by HelpPanel
- **Probability:** High
- **Impact:** Low to Medium
- **Mitigation:** define `slideInRight`/`fadeIn` keyframes and matching utility classes centrally.

#### Specific Risk 3: inconsistent token usage outside primitives
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** component migration + lint/style review pass.

---

## Development Plan

## Implementation Approach: HYBRID (Refinement + Componentization)

### Rationale
RF-005 created usable styling foundations. RF-006 should consolidate those into canonical primitives, close specification gaps, and add tests.

### Strategy Summary
- **New Components:** 8 to 10 (primitive library + tests)
- **Modified Components:** 8 to 12 (existing pages/components)
- **Unchanged Components:** API and backend layers

## Files to CREATE

### 1. Primitive Components
- `UI/pallet_coach_ui/src/components/ui/Card.tsx`
- `UI/pallet_coach_ui/src/components/ui/Button.tsx`
- `UI/pallet_coach_ui/src/components/ui/Field.tsx`
- `UI/pallet_coach_ui/src/components/ui/TextInput.tsx`
- `UI/pallet_coach_ui/src/components/ui/SelectInput.tsx`
- `UI/pallet_coach_ui/src/components/ui/Toggle.tsx`

Goals:
- encode canonical class contracts as reusable components.
- support button variants (`primary`, `secondary`, `ghost`).

### 2. RF-006 Test Files
- `UI/pallet_coach_ui/src/styles/themeTokens.test.ts`
- `UI/pallet_coach_ui/src/components/ui/contracts.test.tsx`

Goals:
- assert token values exist and are exact.
- snapshot/assert critical class contracts for primitives.

## Files to MODIFY

### 1. Global CSS
- `UI/pallet_coach_ui/src/styles/global.css`

Required updates:
- add missing animation keyframes/classes:
  - `slideInRight`, `fadeIn`
  - `.help-panel-enter`, `.backdrop-enter`
- ensure button active-scale and glow behavior contract completeness.
- ensure label/field helper styles align to canonical spec.

### 2. Tailwind Config
- `UI/pallet_coach_ui/tailwind.config.ts`

Required updates:
- include any missing animation utility extension if needed.
- preserve typography plugin config.

### 3. Existing Component Usage
- migrate existing components/pages to primitive components where applicable.
- preserve existing functional behavior and API interactions.

---

## Testing Strategy

### Unit Tests
1. Theme token presence and exact value test.
2. Primitive component class contract tests.
3. Interaction sanity tests for Toggle/Button states.

### UAT / Visual QA
1. Desktop and mobile responsive pass for Home and Run pages.
2. Verify animation behavior for page entry and HelpPanel transitions.
3. Verify typography consistency across headings, labels, prose summary, and numeric cells.

### Validation Commands
- `cd UI/pallet_coach_ui ; npm run test`
- `cd UI/pallet_coach_ui ; npm run build`
- `c:/python314/python.exe -m pytest scripts/tests -q`
- `$env:PYTHONPATH="scripts"; c:/python314/python.exe eval/run_eval.py`

---

## Developer Checklist

### Preparation
- [ ] Review RF-006 feature specification and requirement section 11
- [ ] Inventory current class contracts and identify deltas

### Implementation
- [ ] Create reusable UI primitive components
- [ ] Complete missing animation contracts in global styles
- [ ] Align Card/Button/Input/Field/Toggle/Table contracts to canonical rules
- [ ] Refactor Home/Run/AppShell/HelpPanel to use primitives

### Testing
- [ ] Add token contract tests
- [ ] Add primitive class-contract tests
- [ ] Run frontend tests and build
- [ ] Run backend regression tests

### Validation
- [ ] Perform visual QA pass against RF-006 acceptance criteria
- [ ] Confirm no RF-005 behavioral regressions

### Completion
- [ ] Update RF-006 status to Implemented after delivery
- [ ] Create RF-006 implementation complete report

---

## Additional Resources

- Feature specification: `specs/features/006-ui-design-system-precision-industrial-dark.md`
- Requirement source: `requirement.md` section 11
- Existing UI baseline: `UI/pallet_coach_ui/src/styles/global.css`, `UI/pallet_coach_ui/src/components/*`

---

**END OF IMPLEMENTATION PLAN**
