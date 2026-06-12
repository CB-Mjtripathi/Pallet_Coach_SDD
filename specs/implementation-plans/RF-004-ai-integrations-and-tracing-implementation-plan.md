# Implementation Plan: AI Integrations and Traceability
**Feature ID:** RF-004  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Modification + New Components)

---

## Executive Summary

**Feature:** AI Integrations and Traceability  
**Status:** Partially Implemented  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** High  
**Risk Level:** High

**Summary:**
RF-004 requires optional AI augmentation for summaries and diagrams while preserving deterministic RF-001 to RF-003 outputs as authoritative. The current codebase has endpoint contracts and stubs for `/api/summary`, `/api/summary_ui`, and `/api/diagram`, but no provider clients, prompt template rendering, or AI trace logging. This plan introduces provider modules, prompt template utilities, trace redaction/writing, and API orchestration updates with non-fatal AI failure behavior.

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
**Feature ID:** RF-004  
**Feature Name:** AI Integrations and Traceability  
**Priority:** High  
**Complexity:** High

### Scope Summary
RF-004 adds three optional AI capabilities: AI markdown summary generation (`/api/summary`), UI-focused summary rewrite (`/api/summary_ui`), and AI diagram generation (`/api/diagram`). It also enforces mandatory per-call AI trace logging with best-effort secret redaction and provider metadata capture.

The feature is additive. Deterministic solver outputs and RF-003 artifacts must remain the source of truth and must continue to be generated even if AI providers fail or are unavailable.

### Key Requirements
1. Implement Azure Responses integration in `scripts/pallet_coach/ai/azure_responses.py` using environment-configured endpoint/model/timeout.
2. Implement bundle minimization policy for summary calls: include request + status + stacking + top 5 solutions; exclude raw placement arrays.
3. Implement summary endpoints:
   - `/api/summary`: produce deterministic-to-AI summary markdown artifact.
   - `/api/summary_ui`: produce UI-friendly rewrite using dedicated system prompt and `force` behavior.
4. Implement Google AI Studio image generation in `scripts/pallet_coach/ai/google_ai_studio.py`:
   - `view=flat` -> `diagram_flat.png`
   - `view=3d` -> `diagram_3d.png`
5. Implement prompt template rendering from `scripts/pallet_coach/prompts/*.md` with `{{var}}` substitution.
6. Implement trace logging to `ai_traces/ai_calls.jsonl` for every AI call with secret redaction.
7. Update `bundle.json` artifact pointers and `ai_assist` flags only after successful writes.
8. Ensure AI failures are surfaced in API responses without breaking deterministic run data.

### User Stories Summary
- **US-4.1:** AI summaries generated from minimized bundle context.
- **US-4.2:** AI diagrams generated from rendered prompt artifacts.
- **US-4.3:** Safe, redacted AI call traceability for debugging/evaluation.

### Technical Specifications
- **APIs Required:** `POST /api/summary`, `POST /api/summary_ui`, `POST /api/diagram`
- **Data Models:** Existing `SummaryRequest/Response`, `SummaryUiRequest/Response`, `DiagramRequest/Response`
- **Integrations:** Azure OpenAI Responses API, Google AI Studio image model
- **Performance:** Respect provider timeouts (`AZURE_OAI_TIMEOUT_S` default 60, `GOOGLE_AI_TIMEOUT_S` default 120)

### Dependencies
- **Prerequisites:** RF-002 run resolution; RF-003 prompt artifacts and bundle conventions
- **Integration Points:** RF-005 run page actions for regenerate summary and AI diagram generation

### Complexity Assessment
**Estimated Complexity:** High  
**Reasoning:**
- Number of user stories: 3
- Number of modules involved: 6 to 9
- External integrations: 2 provider APIs
- Data model complexity: moderate
- UI complexity impact: medium (API behavior consumed by UI)
- Security/compliance complexity: high (trace redaction and secret handling)

---

## Implementation Status

### Search Results Analysis

#### Backend / API
- **File:** `scripts/pallet_coach/api/app.py`
  - **Relevance:** High
  - **Functions Found:** `/api/summary`, `/api/summary_ui`, `/api/diagram`
  - **Functionality:** Endpoints exist as `501 Not implemented` stubs
  - **Match Level:** Partial shell only

- **File:** `scripts/pallet_coach/api/models.py`
  - **Relevance:** Medium
  - **Models Found:** `SummaryRequest/Response`, `SummaryUiRequest/Response`, `DiagramRequest/Response`
  - **Functionality:** Contract classes exist
  - **Match Level:** Partial contract only

#### RF-003 Primitives Relevant to RF-004
- **File:** `scripts/pallet_coach/artifacts.py`
  - **Relevance:** Medium
  - **Functions Found:** `write_image_prompts(...)`, `update_bundle_artifacts(...)`
  - **Functionality:** Deterministic prompt artifact writing and artifact pointer updates
  - **Match Level:** Supporting dependency

- **File:** `scripts/pallet_coach/api/app.py`
  - **Relevance:** Medium
  - **Functionality:** Writes `image_prompt_flat.md` and `image_prompt_3d.md` during solve
  - **Match Level:** Supporting dependency

#### Missing RF-004 Core Components
- `scripts/pallet_coach/ai/azure_responses.py` (missing)
- `scripts/pallet_coach/ai/google_ai_studio.py` (missing)
- `scripts/pallet_coach/prompt_templates.py` (missing)
- `scripts/pallet_coach/prompts/*.md` system/template files (missing)
- AI trace writer/redaction utility (missing)
- Endpoint business logic for summary/diagram generation (missing)
- Endpoint test coverage for RF-004 behaviors (missing)

### Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|-------------------------|-----|
| US-4.1 | Partial | Endpoint/model stubs exist | Missing Azure client, minimized bundle assembly, prompt rendering, summary file write, artifact pointer/flag updates |
| US-4.2 | Partial | Endpoint/model stubs + prompt files written in solve | Missing Google client integration, image write flow, bundle pointer/flag updates |
| US-4.3 | Not Implemented | None | Missing `ai_traces/ai_calls.jsonl`, secret redaction, metadata logging |

### Coverage Summary
- **Implemented:** 0 / 3 full user stories (0%)
- **Partially Implemented:** 2 / 3
- **Not Implemented:** 1 / 3

### Recommendation
**Primary Approach:** HYBRID  
**Reasoning:** Endpoint contracts and run/bundle primitives already exist, but all provider, prompt, and trace execution logic must be created.

### Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Azure summary generation | `/api/summary`, `/api/summary_ui` functional | endpoint stubs only | Missing |
| Bundle minimization (top 5, no placements) | minimized context before LLM call | none | Missing |
| Google AI diagram generation | `/api/diagram` writes `diagram_flat.png`/`diagram_3d.png` | endpoint stub only | Missing |
| Prompt template rendering | `prompts/*.md` with `{{var}}` replacement | none | Missing |
| AI trace logging with redaction | JSONL with secret redaction | none | Missing |

---

## Impact Analysis

### Affected Modules

#### API Orchestration
- **File:** `scripts/pallet_coach/api/app.py`
  - **Change Type:** Modification
  - **Impact Level:** High
  - **Reason:** Replace RF-002 stubs with full RF-004 endpoint logic and error policy.

#### API Models
- **File:** `scripts/pallet_coach/api/models.py`
  - **Change Type:** Potential Modification
  - **Impact Level:** Medium
  - **Reason:** Confirm response models match final payloads; add fields if required.

#### New AI Provider Layer
- **File:** `scripts/pallet_coach/ai/__init__.py`
  - **Change Type:** New File
  - **Impact Level:** Low

- **File:** `scripts/pallet_coach/ai/azure_responses.py`
  - **Change Type:** New File
  - **Impact Level:** High

- **File:** `scripts/pallet_coach/ai/google_ai_studio.py`
  - **Change Type:** New File
  - **Impact Level:** High

#### New Prompt/Template Layer
- **File:** `scripts/pallet_coach/prompt_templates.py`
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `scripts/pallet_coach/prompts/azure_summary_system.md`
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `scripts/pallet_coach/prompts/azure_summary_ui_system.md`
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `scripts/pallet_coach/prompts/image_prompt_flat_template.md`
  - **Change Type:** New File
  - **Impact Level:** Low

- **File:** `scripts/pallet_coach/prompts/image_prompt_3d_template.md`
  - **Change Type:** New File
  - **Impact Level:** Low

#### New Trace Utility
- **File:** `scripts/pallet_coach/ai/tracing.py` (recommended)
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** Consolidate JSONL trace append and key redaction.

#### Dependencies
- **File:** `scripts/requirements.txt`
  - **Change Type:** Modification
  - **Impact Level:** Medium
  - **Reason:** Add HTTP client dependency if needed (`requests` or use stdlib `urllib` if preferred).

#### Tests
- **File:** `scripts/tests/test_ai_tracing.py` (new)
  - **Change Type:** New File
  - **Impact Level:** High

- **File:** `scripts/tests/test_prompt_templates.py` (new)
  - **Change Type:** New File
  - **Impact Level:** Medium

- **File:** `scripts/tests/test_api_ai_endpoints.py` (new)
  - **Change Type:** New File
  - **Impact Level:** High

- **File:** `scripts/tests/test_api_app.py`
  - **Change Type:** Modification (optional)
  - **Impact Level:** Medium

### Integration Points

#### Internal Dependencies
- **Depends On:** RF-002 API/run-store
  - **Integration Point:** `resolve_run_dir_safe`, bundle read/write, run logs
  - **Data Flow:** endpoint -> run dir -> artifact write -> bundle update
  - **Impact:** High

- **Depends On:** RF-003 artifact outputs
  - **Integration Point:** pre-rendered `image_prompt_flat.md`/`image_prompt_3d.md`
  - **Data Flow:** run dir prompt files -> Google AI call -> PNG artifact
  - **Impact:** High

#### External Dependencies
- **Azure OpenAI Responses API**
  - Endpoint provided via `AZURE_OAI_RESPONSES_ENDPOINT`
  - Auth header with `AZURE_OAI_API_KEY`

- **Google AI Studio image generation API**
  - Key from `GOOGLE_AI_API_KEY`
  - Model from `GOOGLE_AI_IMAGE_MODEL`

### Features That Must NOT Be Impacted

1. **RF-001 deterministic solver and ranking semantics**
   - **Location:** `scripts/pallet_coach/solver.py`
   - **Preserve Reason:** AI layer must be optional augmentation only.
   - **Validation:** Existing solver tests + eval harness unchanged.

2. **RF-002 run path security and endpoint stability**
   - **Location:** `scripts/pallet_coach/api/run_store.py`, `scripts/pallet_coach/api/app.py`
   - **Preserve Reason:** Security-critical file access guarantees.
   - **Validation:** Existing API/run-store tests remain green.

3. **RF-003 deterministic artifact pipeline**
   - **Location:** `scripts/pallet_coach/diagram.py`, `scripts/pallet_coach/artifacts.py`, solve flow
   - **Preserve Reason:** RF-004 failures must not block deterministic outputs.
   - **Validation:** RF-003 artifact tests remain green.

### Risk Assessment

### Overall Risk Level: High

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| External Dependencies | High | Two provider APIs with variable schemas/failures | isolate provider adapters and add robust fallback/error mapping |
| Security / Secrets | High | Trace logging could leak keys | centralized redaction utility; never log raw headers |
| Integration Points | Medium | Endpoint changes in central API module | keep helper modules thin and endpoint orchestration explicit |
| Data Model Changes | Medium | Bundle pointer/flag drift risk | bundle schema assertions in tests |
| Test Coverage Gap | High | No current AI endpoint tests | add endpoint + unit tests with mocked providers |
| Feature Coupling | Medium | UI depends on endpoint response semantics | preserve response contracts and add compatibility tests |

#### Specific Risk 1: Secret leakage in traces
- **Probability:** Medium
- **Impact:** Critical
- **Mitigation:** Redact both exact secret values and secret-like key names before append.
- **Contingency:** disable trace payload body fields with config toggle if redaction uncertainties appear.

#### Specific Risk 2: AI provider outage blocks user flows
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** return controlled non-200/4xx or clear error body per endpoint, keep deterministic artifacts intact.
- **Contingency:** fallback to deterministic summary for `/api/summary` when AI unavailable.

#### Specific Risk 3: Minimized bundle policy violated
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** dedicated minimization function with explicit test asserting layout arrays removed.
- **Contingency:** scrubper pass before provider submission.

---

## Development Plan

## Implementation Approach: HYBRID (Modification + New Components)

### Rationale
The API surface and run artifact structure already exist, but RF-004 capabilities (providers, templates, tracing, endpoint execution logic) are absent. Implement missing components and wire to existing run lifecycle.

### Strategy Summary
- **New Components:** 9 to 11
- **Modified Components:** 2 to 4
- **Unchanged Components:** RF-001/RF-003 deterministic compute and diagram generation logic

## Files to CREATE

### 1. AI Package Init
**File:** `scripts/pallet_coach/ai/__init__.py`

Purpose:
- Define package boundary for provider/tracing utilities.

### 2. Azure Responses Client
**File:** `scripts/pallet_coach/ai/azure_responses.py`

Implement:
- `build_minimized_bundle(bundle: dict[str, Any]) -> dict[str, Any]`
  - keep request, recommender status/reasons/top5 solutions (without `layout`), stacking
- `generate_summary_markdown(...) -> tuple[str, dict[str, Any]]`
- `generate_summary_ui_markdown(...) -> tuple[str, dict[str, Any]]`

Behavior:
- Read env vars: `AZURE_OAI_RESPONSES_ENDPOINT`, `AZURE_OAI_API_KEY`, `AZURE_OAI_MODEL`, `AZURE_OAI_TIMEOUT_S`
- Use system prompt files via `prompt_templates.py`
- Return markdown + trace metadata (latency, token usage when available)

### 3. Google AI Studio Client
**File:** `scripts/pallet_coach/ai/google_ai_studio.py`

Implement:
- `generate_diagram_image(prompt_text: str, view: str) -> tuple[bytes, dict[str, Any]]`

Behavior:
- Read env vars: `GOOGLE_AI_API_KEY`, `GOOGLE_AI_IMAGE_MODEL`, `GOOGLE_AI_TIMEOUT_S`
- Accept rendered prompt content from run directory files
- Return PNG bytes + trace metadata

### 4. AI Tracing Utility
**File:** `scripts/pallet_coach/ai/tracing.py`

Implement:
- `redact_secrets(value: Any, secrets: list[str]) -> Any`
- `append_ai_trace(run_dir: Path, event: dict[str, Any], trace_dirname: str = "ai_traces") -> Path`

Behavior:
- Append one JSON object per line to `ai_traces/ai_calls.jsonl`
- Redact values matching configured keys (`AZURE_OAI_API_KEY`, `GOOGLE_AI_API_KEY`)
- Include: timestamp, provider, endpoint/model, run_id, latency_ms, tokens when available

### 5. Prompt Template Renderer
**File:** `scripts/pallet_coach/prompt_templates.py`

Implement:
- `load_prompt_template(name: str) -> str`
- `render_prompt_template(name: str, variables: dict[str, Any]) -> str`

Behavior:
- Resolve templates from `scripts/pallet_coach/prompts/`
- Support simple `{{var}}` substitution

### 6. Prompt Files
**File:** `scripts/pallet_coach/prompts/azure_summary_system.md`
- Include deterministic summary generation instruction set.

**File:** `scripts/pallet_coach/prompts/azure_summary_ui_system.md`
- Must include requirement constraints:
  - only use numbers present in input
  - preserve meaning
  - scannable markdown
  - include required fields when present
  - impossible-case guidance
  - traffic-light emojis

**File:** `scripts/pallet_coach/prompts/image_prompt_flat_template.md`
**File:** `scripts/pallet_coach/prompts/image_prompt_3d_template.md`
- Include placeholders for run/request/solution context and style constraints.

### 7. Tests
**File:** `scripts/tests/test_prompt_templates.py`

Test cases:
1. Template loading from prompt directory.
2. `{{var}}` substitution renders expected text.
3. Missing variable behavior is explicit and deterministic.

**File:** `scripts/tests/test_ai_tracing.py`

Test cases:
1. Trace file path creation and JSONL append behavior.
2. Secret redaction for Azure/Google keys.
3. Metadata fields present in trace records.

**File:** `scripts/tests/test_api_ai_endpoints.py`

Test cases (with provider mocks):
1. `/api/summary` writes summary artifact and updates bundle pointer.
2. `/api/summary_ui` writes `summary_ui.md`, updates bundle, supports `force`.
3. `/api/diagram` for both views writes output image and updates bundle pointers.
4. AI provider failure handling is controlled and does not corrupt bundle.

## Files to MODIFY

### 1. API AI Endpoints
**File:** `scripts/pallet_coach/api/app.py`

Required changes:
- Replace 501 stubs for `/api/summary`, `/api/summary_ui`, `/api/diagram` with RF-004 logic.
- Resolve run dir and load bundle.
- Call provider utilities and tracing utility.
- Persist artifacts:
  - `/api/summary` -> `recommendation_summary.md` (or dedicated AI summary path if design chooses)
  - `/api/summary_ui` -> `summary_ui.md`
  - `/api/diagram?view=flat` -> `diagram_flat.png`
  - `/api/diagram?view=3d` -> `diagram_3d.png`
- Update `bundle["artifacts"]` and `bundle["ai_assist"]` flags after successful writes.
- Append run log entries for AI start/success/failure events.

### 2. API Models (if needed)
**File:** `scripts/pallet_coach/api/models.py`

Potential changes:
- Ensure response models align with actual endpoint payloads.
- Add explicit error fields only if required by endpoint behavior.

### 3. Requirements Manifest
**File:** `scripts/requirements.txt`

Potential update:
- Add HTTP provider package if not using stdlib HTTP client.

---

## Testing Strategy

### Unit and Integration Tests
1. Existing RF-001 to RF-003 tests remain green.
2. New prompt/template/tracing tests validate RF-004 internals.
3. Endpoint tests with mocks validate behavior without external API dependency.

### UAT Scenarios
1. Trigger `/api/summary` for a known run and verify summary artifact + bundle update.
2. Trigger `/api/summary_ui` and verify rewrite artifact and `summary_ui_generated=true`.
3. Trigger `/api/diagram` for `flat` and `3d` and verify image files and pointers.
4. Validate `ai_traces/ai_calls.jsonl` entries are appended and secrets redacted.
5. Validate deterministic run artifacts are still available when AI calls fail.

### Validation Commands
- `c:/python314/python.exe -m pytest scripts/tests -q`
- `c:/python314/python.exe eval/run_eval.py`

---

## Developer Checklist

### Preparation
- [ ] Review RF-004 feature specification
- [ ] Review this implementation plan
- [ ] Confirm RF-001 to RF-003 test baseline is green

### Implementation
- [ ] Create `scripts/pallet_coach/ai/__init__.py`
- [ ] Create `scripts/pallet_coach/ai/azure_responses.py`
- [ ] Create `scripts/pallet_coach/ai/google_ai_studio.py`
- [ ] Create `scripts/pallet_coach/ai/tracing.py`
- [ ] Create `scripts/pallet_coach/prompt_templates.py`
- [ ] Create prompt files under `scripts/pallet_coach/prompts/`
- [ ] Implement minimized bundle policy (no raw placements)
- [ ] Implement `/api/summary` endpoint logic
- [ ] Implement `/api/summary_ui` endpoint logic (`force` support)
- [ ] Implement `/api/diagram` endpoint logic for `flat` and `3d`
- [ ] Update bundle artifact pointers and `ai_assist` flags only after successful writes
- [ ] Append run log entries for AI operations

### Testing
- [ ] Create `scripts/tests/test_prompt_templates.py`
- [ ] Create `scripts/tests/test_ai_tracing.py`
- [ ] Create `scripts/tests/test_api_ai_endpoints.py`
- [ ] Run full test suite (`scripts/tests`)
- [ ] Run eval harness and confirm no solver regressions

### Validation
- [ ] Verify AI trace file path and JSONL append semantics
- [ ] Verify secret redaction behavior for both provider API keys
- [ ] Verify `/output/{run_id}/{filename}` serves generated AI artifacts
- [ ] Verify deterministic artifacts remain available when AI calls fail

### Completion
- [ ] Update RF-004 feature status to Implemented after delivery
- [ ] Create RF-004 implementation complete report

---

## Troubleshooting Guide

**Issue:** Provider credentials missing at runtime  
**Fix:** Return clear 4xx/5xx API error with actionable message; do not mutate bundle state.

**Issue:** Provider response format changed  
**Fix:** Parse defensively and log best-effort metadata in trace event.

**Issue:** Redaction misses embedded secret values  
**Fix:** Apply recursive deep redaction over strings, dicts, lists before trace append.

**Issue:** `/api/summary_ui` repeatedly overwrites content unexpectedly  
**Fix:** Gate write behavior with `force` and artifact existence checks.

---

## Additional Resources

- Feature specification: `specs/features/004-ai-integrations-and-tracing.md`
- Requirement source: `requirement.md` section 7
- Existing API shell: `scripts/pallet_coach/api/app.py`
- Existing run artifact conventions: RF-003 modules and tests

---

**END OF IMPLEMENTATION PLAN**
