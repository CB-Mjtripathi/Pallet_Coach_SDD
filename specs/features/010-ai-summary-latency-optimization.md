# Feature: AI Summary Latency Optimization

**Feature ID:** RF-010
**Status:** Implemented
**Priority:** High
**Target Release:** Phase 1.2 Enhancement
**Source Documentation:** `specs/intake/ai-summary-latency-optimization-intake.md`, `specs/intake/ai-summary-latency-optimization-brief.md`, `specs/intake/processed_intake_requests.json` (INTAKE-2026-06-29-002)

---

## Overview

This feature reduces actual and perceived latency for AI summary experiences used in run review workflows. The scope covers backend path optimization (`/api/summary` and `/api/summary_ui`), safe reuse of previously generated summaries when inputs are unchanged, timeout/fallback tuning to reduce tail latency, and user-facing loading behavior improvements.

The objective is to replace subjective "faster" expectations with measurable service targets and release gates while preserving summary quality, safety behavior, and reliability.

---

## User Stories

### US-10.1: Establish measurable baseline and latency budget

**As a** product owner  
**I want to** define and approve AI Summary latency budgets using baseline measurements  
**So that** optimization work can be planned and validated objectively

**Acceptance Criteria:**
- ✅ Baseline latency is measured for `/api/summary_ui` and `/api/summary` across representative payload profiles (small, medium, large).
- ✅ Stage-level timings are captured for at least: request parse, bundle minimization/context prep, model call, response parse, artifact write, and response serialization.
- ✅ Approved latency budgets are documented for p50 and p95 per endpoint profile.
- ✅ Success criteria include explicit comparison against baseline (e.g., reduction percentage and absolute target thresholds).

**Technical Details:**
- Primary backend surface: `scripts/pallet_coach/api/app.py` summary endpoints.
- Primary AI call path: `scripts/pallet_coach/ai/azure_responses.py`.
- Trace persistence remains compatible with existing AI trace artifacts.

---

### US-10.2: Optimize backend summary pipeline critical path

**As a** platform engineer  
**I want to** reduce avoidable work in the summary pipeline  
**So that** end-to-end summary responses complete within budget

**Acceptance Criteria:**
- ✅ Dominant latency contributors identified in US-10.1 are reduced through targeted changes in the critical path.
- ✅ Repeated synchronous work in summary generation is eliminated or moved off the request path when safe.
- ✅ Payload preparation and serialization overhead is reduced without changing contract compatibility.
- ✅ p95 latency for both summary endpoints meets approved budget in production-like test scenarios.

**Technical Details:**
- Candidate optimization points include repeated context preparation in `build_minimized_bundle(...)`, prompt construction overhead, and synchronous file IO in summary response path.
- No API contract changes to existing `SummaryResponse` and `SummaryUiResponse` schemas.

---

### US-10.3: Add safe summary reuse, timeout tuning, and responsive fallback

**As an** operations user  
**I want to** receive fast responses for repeat requests and resilient behavior under model slowness  
**So that** my workflow is not blocked by avoidable or extreme latency

**Acceptance Criteria:**
- ✅ Identical (or policy-approved near-identical) summary requests can reuse valid existing artifacts when freshness rules allow.
- ✅ Timeout and retry policy is tuned to reduce avoidable tail latency while protecting reliability.
- ✅ When upstream AI latency/failure exceeds policy, fallback behavior responds quickly and remains user-understandable.
- ✅ Error rate does not regress materially against baseline after optimization.

**Technical Details:**
- Reuse policy must remain transparent and auditable in run artifacts/logs.
- Fallback behavior must preserve current safety posture and avoid fabricated values.

---

### US-10.4: Improve perceived speed in Run UI summary experience

**As a** planner reviewing run output  
**I want to** see clear progress and non-blocking summary behavior  
**So that** I can continue using the app while summary generation completes

**Acceptance Criteria:**
- ✅ Run page summary flow remains non-blocking and clearly communicates loading/progress state.
- ✅ First useful user feedback appears within agreed UI responsiveness budget for summary actions.
- ✅ Existing regenerate behavior remains available and does not introduce duplicate in-flight calls for the same run.
- ✅ UX behavior is validated for both first-load summary generation and cached/reused summary retrieval paths.

**Technical Details:**
- UI surfaces: `UI/pallet_coach_ui/src/pages/Run.tsx`, `UI/pallet_coach_ui/src/components/SummaryPanel.tsx`, and API client summary calls in `UI/pallet_coach_ui/src/api/endpoints.ts`.

---

### US-10.5: Add observability and performance regression gates

**As a** support and reliability stakeholder  
**I want to** monitor AI summary latency continuously  
**So that** regressions are detected quickly after release

**Acceptance Criteria:**
- ✅ Endpoint and stage latency metrics are emitted with dimensions sufficient for trend analysis (operation, endpoint, outcome, payload profile).
- ✅ AI traces include enough metadata to distinguish cache/reuse, normal generation, and fallback paths.
- ✅ Automated tests cover summary endpoint behavior for standard, reused, and fallback scenarios.
- ✅ A repeatable performance check is documented for release verification.

**Technical Details:**
- Build on existing trace framework and endpoint tests under `scripts/tests/test_ai_tracing.py` and `scripts/tests/test_api_ai_endpoints.py`.

---

## Dependencies

### Prerequisites
- RF-002 API Layer and Run Management
- RF-004 AI Integrations and Traceability
- RF-005 React UI Home and Run Experience

### Related Features
- RF-007 Testing, Evaluation, and Quality Gates
- RF-008 Deployment, Security, and Operational Readiness

---

## Technical Architecture

### Components Involved
- `scripts/pallet_coach/api/app.py` (summary endpoint orchestration)
- `scripts/pallet_coach/ai/azure_responses.py` (provider call path and payload preparation)
- `scripts/pallet_coach/ai/tracing.py` (latency and execution trace capture)
- `UI/pallet_coach_ui/src/pages/Run.tsx` (summary trigger and loading behavior)
- `UI/pallet_coach_ui/src/components/SummaryPanel.tsx` (summary rendering state)

### Data Flow
1. User requests summary from Run workflow.
2. API resolves run context and determines reuse vs regenerate path.
3. Summary pipeline prepares minimized context and invokes AI provider when needed.
4. Summary artifact and trace metadata are persisted.
5. UI receives summary or fallback response and updates state without blocking broader run view interactions.

### APIs & Integrations
- `POST /api/summary`
- `POST /api/summary_ui`
- Azure OpenAI Responses API (existing integration)

---

## Non-Functional Requirements

### Performance
- Endpoint p50 and p95 targets must be explicitly documented and approved before implementation sign-off.
- Tail-latency reduction must be demonstrated in representative concurrent usage tests, not only single-request runs.

### Reliability
- Optimization changes must not materially increase AI summary endpoint error rate.

### Observability
- Latency and outcome telemetry must support regression detection per release.

### Maintainability
- Optimizations should be implemented as clear pipeline stages and policies, not one-off hardcoded shortcuts.

---

## Implementation Slices For Downstream Planning

1. Baseline + budgets + stage instrumentation.
2. Backend critical-path optimization in summary generation flow.
3. Reuse/caching policy + timeout/retry/fallback tuning.
4. Run UI responsiveness improvements and duplicate-call safeguards.
5. Test, benchmark, and rollout gates.

---

## Test Coverage

### Unit/Component Tests Required
- Summary pipeline stage timing and metadata coverage.
- Reuse eligibility logic tests (cache hit/miss and freshness boundary).
- Timeout/fallback behavior tests with deterministic provider failure simulation.

### Integration Tests Required
- `/api/summary` and `/api/summary_ui` latency-path behavior under normal and degraded provider conditions.
- End-to-end UI flow test ensuring non-blocking summary UX and stable regeneration behavior.

### Performance Validation Required
- Baseline vs post-change comparison report for p50/p95 by payload profile.
- Concurrency test results showing sustained improvements under representative load.

---

## Traceability

**Source Documents:**
- `specs/intake/ai-summary-latency-optimization-intake.md`
- `specs/intake/ai-summary-latency-optimization-brief.md`
- `specs/intake/processed_intake_requests.json` (`id`: `INTAKE-2026-06-29-002`)
- `specs/intake/INDEX.md` (entry dated 2026-06-29)

**Lifecycle Gate:**
- Intake -> Engineering documentation complete with RF-010.
- Next gate required: architecture/technical implementation planning.

**Related ADRs:**
- None yet (to be produced during architecture stage if caching/timeout policies alter operational behavior).

---

## Open Questions

- What production p95 and p99 targets are approved for `/api/summary_ui` and `/api/summary`?
- Should release scope prioritize first-load latency, repeat-load latency, or balanced improvement across both?
- Are any bounded quality/freshness trade-offs acceptable to hit strict latency targets?

---

**Last Updated:** 2026-06-29
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-06-29  
**Implementation Plan:** `specs/implementation-plans/RF-010-ai-summary-latency-optimization-implementation-plan.md`

Delivered scope highlights:
- Stage timing instrumentation and enriched summary trace dimensions.
- Policy-driven summary reuse with freshness checks and auditable reason codes.
- Timeout/retry/fallback classification for summary generation paths.
- Run page in-flight summary dedup and responsive non-blocking status messaging.
- Added backend, tracing, UI, and perf-helper test coverage for RF-010 paths.
