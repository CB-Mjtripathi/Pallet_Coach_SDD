# Feature: AI Integrations and Traceability

**Feature ID:** RF-004
**Status:** Implemented
**Priority:** High
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Section 7, Sections 5.1 and 6.1 optional artifacts)

---

## Overview

This feature specifies optional generative AI augmentation for summaries and diagrams. It includes Azure OpenAI Responses integration for textual outputs, Google AI Studio integration for generated diagrams, prompt template rendering, and required AI call tracing with secret redaction.

The AI layer is explicitly additive: solver and non-AI artifacts remain deterministic and authoritative.

---

## User Stories

### US-4.1: Generate AI summaries from minimized bundle context

**As an** operations manager  
**I want to** receive a polished, stakeholder-friendly markdown summary  
**So that** recommendation outcomes are easier to communicate

**Acceptance Criteria:**
- ✅ `/api/summary` uses Azure Responses endpoint with full configured URL and API version.
- ✅ `/api/summary_ui` uses dedicated UI rewrite system prompt.
- ✅ AI input includes only minimized bundle context: top 5 solutions, request, status, stacking, and excludes raw placements arrays.
- ✅ Summary files are saved to run directory and artifact pointers updated.

**Technical Details:**
- Module: `scripts/pallet_coach/ai/azure_responses.py`
- Required env vars: `AZURE_OAI_RESPONSES_ENDPOINT`, `AZURE_OAI_API_KEY`, `AZURE_OAI_MODEL`, `AZURE_OAI_TIMEOUT_S`

---

### US-4.2: Generate AI diagrams from rendered prompts

**As a** supply chain analyst  
**I want to** produce high-level AI visualizations for flat and 3D views  
**So that** external audiences can consume polished visuals

**Acceptance Criteria:**
- ✅ `/api/diagram` reads rendered prompt file selected by `view` (`flat` or `3d`).
- ✅ Google AI call writes binary image to `diagram_flat.png` or `diagram_3d.png`.
- ✅ `bundle.json` artifact pointers are updated after image write.
- ✅ Request timeouts follow configured defaults.

**Technical Details:**
- Module: `scripts/pallet_coach/ai/google_ai_studio.py`
- Required env vars: `GOOGLE_AI_API_KEY`, `GOOGLE_AI_IMAGE_MODEL`, `GOOGLE_AI_TIMEOUT_S`

---

### US-4.3: Preserve AI operation trace with secret redaction

**As an** AI/CoE developer  
**I want to** inspect prompt/response metadata safely  
**So that** I can debug and evaluate AI behavior without leaking credentials

**Acceptance Criteria:**
- ✅ Every AI call appends one JSONL line to `ai_traces/ai_calls.jsonl`.
- ✅ Trace writing redacts values matching `AZURE_OAI_API_KEY` and `GOOGLE_AI_API_KEY`.
- ✅ Trace should include timestamp, endpoint/model, token counts when available, latency, run_id.

**Technical Details:**
- Tracing path controlled by `AI_TRACE_DIRNAME` (default `ai_traces`)
- Best-effort metadata capture for provider differences

---

## Dependencies

### Prerequisites
- RF-002 API endpoints and run resolution
- RF-003 prompt file and artifact storage conventions

### Related Features
- RF-005 Run page AI panel and regenerate actions

---

## Technical Architecture

### Components Involved
- `azure_responses.py`
- `google_ai_studio.py`
- `prompt_templates.py`
- `scripts/pallet_coach/prompts/*.md`

### Data Flow
1. Read run bundle and select reduced context.
2. Render system/user prompts from templates.
3. Execute provider call with timeout and model settings.
4. Persist output artifact and update bundle pointers.
5. Append redacted trace event.

### APIs & Integrations
- `POST /api/summary`
- `POST /api/summary_ui`
- `POST /api/diagram`

---

## Non-Functional Requirements

### Performance
- Azure calls may run up to configured 60-second timeout.
- Google calls may run up to configured 120-second timeout.

### Security
- Secrets must never be hardcoded or persisted in clear text traces.

### Scalability
- Future migration to async job queue recommended for resilience and UX.

---

## Implementation Notes

- Preserve explicit UI summary prompt constraints (traffic-light emojis and no invented numbers).
- Keep AI outputs optional; core flow must not fail hard on AI errors.

---

## Test Coverage

### Unit Tests Required
- Prompt rendering variable substitution tests
- Trace redaction tests
- Bundle minimization policy tests

### UAT Tests Required
- Summary generation and regenerate workflow from run page
- Diagram generation for both `flat` and `3d`

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 7 (AI integrations)
- Attached: `requirement.md` section 5.1 (API endpoints)
- Attached: `requirement.md` section 6.1 (optional AI artifacts)

**Related ADRs:**
- None yet

**Implementation Files:**
- `scripts/pallet_coach/ai/azure_responses.py`
- `scripts/pallet_coach/ai/google_ai_studio.py`
- `scripts/pallet_coach/prompt_templates.py`
- `scripts/pallet_coach/prompts/azure_summary_system.md`
- `scripts/pallet_coach/prompts/azure_summary_ui_system.md`
- `scripts/pallet_coach/prompts/image_prompt_flat_template.md`
- `scripts/pallet_coach/prompts/image_prompt_3d_template.md`

---

## Open Questions

- None. Provider-specific defaults are specified.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Delivery Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** specs/implementation-plans/RF-004-ai-integrations-and-tracing-implementation-plan.md

### Files Created
- scripts/pallet_coach/ai/__init__.py
- scripts/pallet_coach/ai/azure_responses.py
- scripts/pallet_coach/ai/google_ai_studio.py
- scripts/pallet_coach/ai/tracing.py
- scripts/pallet_coach/prompt_templates.py
- scripts/pallet_coach/prompts/azure_summary_system.md
- scripts/pallet_coach/prompts/azure_summary_ui_system.md
- scripts/pallet_coach/prompts/image_prompt_flat_template.md
- scripts/pallet_coach/prompts/image_prompt_3d_template.md
- scripts/tests/test_prompt_templates.py
- scripts/tests/test_ai_tracing.py
- scripts/tests/test_api_ai_endpoints.py

### Files Modified
- scripts/pallet_coach/api/app.py

### Validation Results
- Unit/integration tests: 29 passed, 0 failed
- Eval harness: 4 passed, 0 failed

### Outcome
- RF-004 endpoints are implemented: `/api/summary`, `/api/summary_ui`, `/api/diagram`.
- AI trace JSONL capture with secret redaction is implemented.
- Bundle minimization policy is enforced for summary generation input.
