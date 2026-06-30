# Feature: AI Summary Rewrite Availability Hardening

**Feature ID:** RF-011
**Status:** Specification
**Priority:** High
**Target Release:** Phase 1.3 Reliability
**Source Documentation:** `specs/intake/ai-summary-rewrite-availability-hardening-intake.md`, `specs/intake/ai-summary-rewrite-availability-hardening-brief.md`, `specs/intake/processed_intake_requests.json` (INTAKE-2026-06-30-003)

---

## Overview

This feature hardens AI rewrite availability for recommendation summaries so configured environments reliably use provider-backed rewrite instead of unintentionally falling back to deterministic output. It adds runtime readiness checks, failure classification, and operational diagnostics while preserving safe fallback behavior for true degraded conditions.

The objective is to increase rewrite success rate, reduce avoidable fallback frequency, and improve trust in AI-assisted run outputs without breaking existing summary contracts.

---

## User Stories

### US-11.1: Validate rewrite readiness before summary generation

**As a** platform maintainer  
**I want to** validate rewrite provider prerequisites at startup or preflight  
**So that** misconfiguration is detected before users hit fallback behavior

**Acceptance Criteria:**
- ✅ Required rewrite configuration surfaces are validated (endpoint, model/deployment, auth/credentials, timeout settings).
- ✅ Validation distinguishes hard-fail vs warning-level issues for optional vs required paths.
- ✅ Validation output is actionable and points to exact missing/malformed settings.
- ✅ Health/readiness diagnostics expose rewrite availability state.

**Technical Details:**
- Primary backend surfaces: `scripts/pallet_coach/api/app.py`, `scripts/pallet_coach/ai/azure_responses.py`.
- Validation should reuse centralized configuration loading rules and avoid duplicating env parsing.

---

### US-11.2: Classify and trace rewrite unavailability causes

**As an** operations engineer  
**I want to** see explicit machine-readable failure classes for rewrite unavailability  
**So that** I can quickly diagnose and fix root causes

**Acceptance Criteria:**
- ✅ Rewrite failures are classified into explicit categories (config_missing, auth_error, endpoint_unreachable, deployment_mismatch, timeout, provider_error).
- ✅ Each fallback event emits reason code and context in run logs/traces.
- ✅ Trace metadata is queryable by endpoint, run_id, and failure class.
- ✅ Diagnostic verbosity remains safe and avoids leaking secrets.

**Technical Details:**
- Extend existing trace payload structure without breaking readers.
- Use stable reason-code enums for downstream analytics and alerting.

---

### US-11.3: Reduce unintended fallback in configured environments

**As a** product owner  
**I want to** minimize deterministic fallback occurrences where rewrite should work  
**So that** users consistently receive AI-enhanced summaries

**Acceptance Criteria:**
- ✅ Rewrite success rate target is measurable and reported per environment.
- ✅ Fallback rate baseline is captured and regression monitored after changes.
- ✅ Timeout and retry policy is tuned to avoid premature fallback while bounded for responsiveness.
- ✅ Deterministic fallback remains available as controlled safety path under real degradation.

**Technical Details:**
- Keep response contracts unchanged (`SummaryResponse`, `SummaryUiResponse`).
- Tune retry/timeout policy with explicit environment-safe defaults.

---

### US-11.4: Improve user-visible summary mode transparency

**As a** planning user  
**I want to** understand whether my summary was AI-rewritten or deterministic fallback  
**So that** I can interpret output confidence correctly

**Acceptance Criteria:**
- ✅ UI clearly distinguishes rewrite success vs fallback mode for each run summary.
- ✅ Messaging is concise and non-alarming when fallback is expected.
- ✅ Per-run summary mode state is persisted or derivable from run artifacts/traces.
- ✅ UI behavior does not block existing run workflow actions.

**Technical Details:**
- Primary UI surfaces: `UI/pallet_coach_ui/src/pages/Run.tsx`, `UI/pallet_coach_ui/src/components/SummaryPanel.tsx`.
- Reuse existing summary status rendering patterns where possible.

---

## Dependencies

### Prerequisites
- RF-002 API Layer and Run Management
- RF-004 AI Integrations and Traceability
- RF-005 React UI Home and Run Experience
- RF-010 AI Summary Latency Optimization

### Related Features
- RF-007 Testing, Evaluation, and Quality Gates
- RF-008 Deployment, Security, and Operational Readiness

---

## Technical Architecture

### Components Involved
- `scripts/pallet_coach/api/app.py` (summary endpoint orchestration and diagnostics)
- `scripts/pallet_coach/ai/azure_responses.py` (provider readiness and error classification)
- `scripts/pallet_coach/ai/tracing.py` (reason-coded trace events)
- `UI/pallet_coach_ui/src/pages/Run.tsx` (summary mode visibility)
- `UI/pallet_coach_ui/src/components/SummaryPanel.tsx` (status display)

### Data Flow
1. User requests summary generation.
2. Backend validates rewrite readiness and attempts provider rewrite.
3. If rewrite succeeds, AI summary mode is recorded and returned.
4. If rewrite fails, failure class is recorded and deterministic fallback returned.
5. UI displays resulting summary mode and traceable status.

### APIs & Integrations
- `POST /api/summary`
- `POST /api/summary_ui`
- Azure OpenAI rewrite path via existing provider integration

---

## Non-Functional Requirements

### Reliability
- Rewrite availability should meet agreed success-rate target in configured environments.

### Observability
- Fallback events must include stable reason codes and searchable metadata.

### Security
- Diagnostics must avoid sensitive credential leakage.

### Maintainability
- Rewrite availability checks should be centralized and testable.

---

## Test Coverage

### Unit/Component Tests Required
- Rewrite readiness validator behavior for valid/invalid config states.
- Failure classification mapping from provider/runtime errors to reason codes.

### Integration Tests Required
- Summary endpoint behavior for rewrite success path.
- Summary endpoint behavior for classified fallback paths.
- Trace/log payload validation for reason-code completeness.

### UI Tests Required
- Run page status rendering for rewrite success vs fallback mode.
- Non-blocking behavior while displaying summary mode status.

---

## Traceability

**Source Documents:**
- `specs/intake/ai-summary-rewrite-availability-hardening-intake.md`
- `specs/intake/ai-summary-rewrite-availability-hardening-brief.md`
- `specs/intake/processed_intake_requests.json` (`id`: `INTAKE-2026-06-30-003`)
- `specs/intake/INDEX.md` (entry dated 2026-06-30)

**Lifecycle Gate:**
- Intake complete and feature extraction complete.
- Next gate: technical implementation planning.

---

## Open Questions

- Which environment currently contributes most to fallback frequency (local, Docker local, hosted)?
- What rewrite success-rate and fallback-rate targets should be used as release gates?
- Should rewrite/fallback mode also be included in exported run artifacts for downstream audit?

---

**Last Updated:** 2026-06-30
**Author:** Engineering Lead-equivalent extraction