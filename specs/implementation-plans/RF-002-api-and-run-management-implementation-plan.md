# Implementation Plan: API Layer and Run Management
**Feature ID:** RF-002  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Modification + New Components)

---

## Executive Summary

**Feature:** API Layer and Run Management  
**Status:** Partially Implemented  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** High  
**Risk Level:** Medium

**Summary:**
RF-002 API capabilities are not implemented yet, but RF-001 primitives now exist and should be reused. The plan is to add a full FastAPI app, typed API models, run directory manager, safe path resolution, static output serving, and solve/run/log endpoints while preserving RF-001 contracts and deterministic solver outputs.

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
**Feature ID:** RF-002  
**Feature Name:** API Layer and Run Management  
**Priority:** Critical  
**Complexity:** High

## Scope Summary
RF-002 provides a production-oriented FastAPI interface for health checks, solve requests, run retrieval, log retrieval, optional AI action stubs, and static artifact serving. It must also allocate run directories in `04_Output`, enforce run ID format and safe run-path resolution, and return strongly-typed responses.

This feature orchestrates RF-001 outputs into persisted run bundles that the UI and downstream services can consume.

## Key Requirements
1. Provide endpoints: `/health`, `/api/solve`, `/api/runs/{run_id}`, `/api/runs/{run_id}/logs`, `/api/summary`, `/api/summary_ui`, `/api/diagram`, `/output/{run_id}/{filename}`.
2. Return HTTP 422 for invalid solver request contracts with `ContractError` details.
3. Return HTTP 404 when run ID does not exist.
4. Mount `/output` static route to repository `04_Output` path.
5. Mitigate run ID path traversal via safe path validation.
6. Generate run IDs as `R{n:04d}_{YYYYMMDD}` with daily monotonic counters.
7. Accept `/api/solve` parameters `max_solutions` (1..250 default 25) and `include_timestamp` (default true).
8. Persist `bundle.json` and `run_log.txt` minimum artifacts at solve-time.
9. Return typed `SolveResponse` including best metrics and artifact pointers.
10. Keep `/api` prefixing for API endpoints.

## User Stories Summary
- **US-2.1:** Solve via API with contract validation, run creation, typed response.
- **US-2.2:** Retrieve run bundles and run logs safely.
- **US-2.3:** Serve output artifacts from safe static routes.

## Technical Specifications
- **APIs Required:** FastAPI endpoints listed above.
- **Data Models:** Pydantic API models for solve, summary, summary_ui, and diagram requests/responses.
- **Integrations:** RF-001 recommender and contracts parser; filesystem output root `04_Output`.
- **Performance:** Typical `/api/solve` request path should remain within 10 seconds target once RF-003 diagrams are in place.

## Dependencies
- **Prerequisites:** RF-001 solver/recommender (implemented).
- **Integration Points:** RF-003 artifact renderer; RF-004 AI endpoints; RF-005 UI run page.

## Complexity Assessment
**Estimated Complexity:** High  
**Reasoning:**
- Number of user stories: 3
- Number of modules involved: 4 to 6 new modules
- External integrations: internal filesystem + future AI handlers
- Data model complexity: moderate
- UI complexity: none directly, but strict contract compatibility with UI is required

---

## Implementation Status

## Search Results Analysis

### Files Found

#### Backend Services
- `scripts/pallet_coach/contracts.py`  
  - **Relevance:** Medium  
  - **Functions Found:** `parse_request`, validation helpers  
  - **Functionality:** Canonical request validation and default handling  
  - **Match Level:** Partial prerequisite

- `scripts/pallet_coach/recommender.py`  
  - **Relevance:** High  
  - **Functions Found:** `recommend`  
  - **Functionality:** Orchestrates parse -> solve -> stacking  
  - **Match Level:** Partial prerequisite

- `scripts/pallet_coach/solver.py`, `scripts/pallet_coach/stacking.py`, `scripts/pallet_coach/models.py`  
  - **Relevance:** Medium  
  - **Functionality:** Core computation and data models  
  - **Match Level:** Supporting prerequisite

#### API Components
- No `scripts/pallet_coach/api/` directory or FastAPI app found.
- No Pydantic endpoint request/response models found.
- No run-manager or output path-safety utility found.

#### Tests
- No API endpoint tests currently present.

### Summary of Findings
- **Total relevant files found:** 6
- **Highly relevant files:** 1 (`recommender.py`)
- **Partially relevant files:** 5
- **Missing core RF-002 implementation files:** all API-layer modules and tests

## Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|------------------------|-----|
| US-2.1 | Partial | `scripts/pallet_coach/recommender.py` | Missing FastAPI endpoint, run creation, typed response, artifact persistence |
| US-2.2 | Not Implemented | None | Missing run lookup, bundle read, log tail route, 404 behavior |
| US-2.3 | Not Implemented | None | Missing static `/output` mount and safe run file serving |

### Coverage Summary
- **Implemented:** 0 / 3 full user stories (0%)
- **Partially Implemented:** 1 / 3
- **Not Implemented:** 2 / 3

### Recommendation
**Primary Approach:** HYBRID  
**Reasoning:** Reuse RF-001 recommender/contracts as core execution engine, then implement full API and run-management surface from scratch.

## Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| `/api/solve` with contract-aware errors | 422 on invalid contract | `contracts.parse_request` and `ContractError` | Partial |
| Run directory allocation and run ID format | `R{n:04d}_{YYYYMMDD}` | None | Missing |
| `GET /api/runs/{run_id}` | returns parsed bundle | None | Missing |
| `GET /api/runs/{run_id}/logs` | returns tail text | None | Missing |
| `/output` static mount + safe path handling | child-of-output root check | None | Missing |
| Typed API models | SolveRequest/SolveResponse/etc | None | Missing |

---

## Impact Analysis

## Affected Modules

### Services Layer
- **File:** `scripts/pallet_coach/recommender.py`
  - **Change Type:** Optional modification (light)
  - **Impact Level:** Medium
  - **Reason:** Ensure returned structure is serialization-friendly for API response and bundle writing.

### API Layer (new)
- **File:** `scripts/pallet_coach/api/app.py`
  - **Change Type:** New file
  - **Impact Level:** High
  - **Reason:** Core FastAPI route implementation.

- **File:** `scripts/pallet_coach/api/models.py`
  - **Change Type:** New file
  - **Impact Level:** High
  - **Reason:** Typed request/response contracts.

- **File:** `scripts/pallet_coach/api/run_store.py`
  - **Change Type:** New file
  - **Impact Level:** High
  - **Reason:** Run ID generation, safe run path resolution, bundle/log writing.

- **File:** `scripts/pallet_coach/api/__init__.py`
  - **Change Type:** New file
  - **Impact Level:** Low

### Tests
- **File:** `scripts/tests/test_api_app.py`
  - **Change Type:** New file
  - **Impact Level:** High
  - **Reason:** Endpoint and error mapping validation.

- **File:** `scripts/tests/test_run_store.py`
  - **Change Type:** New file
  - **Impact Level:** Medium
  - **Reason:** run ID format and path traversal protections.

### Dependencies
- **File:** `scripts/requirements.txt`
  - **Change Type:** Modify
  - **Impact Level:** Medium
  - **Reason:** Add FastAPI, Uvicorn, Pydantic and HTTP test client support.

## Integration Points

### Internal Dependencies
- **Depends On:** RF-001 Core Solver Engine
  - **Integration Point:** `recommender.recommend()` invoked by `/api/solve`
  - **Data Flow:** canonical request in -> recommender payload out -> bundle persisted and response returned
  - **Impact:** High

### External Dependencies
- **FastAPI framework** for endpoint layer
- **Pydantic v2** for typed API models
- **Starlette StaticFiles** for `/output` serving

### Data Flow
1. Receive `SolveRequest` payload.
2. Validate max_solutions range and request shape.
3. Create run directory and log file.
4. Execute recommender.
5. Persist `bundle.json` and deterministic summary/log artifact placeholders.
6. Return `SolveResponse`.
7. Expose bundle/log/static retrieval endpoints.

## Features That Must NOT Be Impacted

1. **RF-001 deterministic solver behavior**
   - **Location:** `scripts/pallet_coach/solver.py`
   - **Why Preserve:** Foundational correctness for all ranking results
   - **Validation:** Run RF-001 test suite and eval harness unchanged

2. **Contract parsing defaults and validation semantics**
   - **Location:** `scripts/pallet_coach/contracts.py`
   - **Why Preserve:** UI/request compatibility and error behavior
   - **Validation:** Existing contract tests + new API 422 mapping tests

## Preservation Strategy
- Add API-layer code in new modules instead of rewriting RF-001 internals.
- Keep existing function signatures in RF-001 modules.
- Treat recommender payload as source of truth for bundle persistence.

## Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Code Complexity | Medium | Multi-endpoint orchestration and filesystem IO | isolate run-store utility and keep app thin |
| Integration Points | Medium | API depends on strict RF-001 schemas | strong serialization tests and fixture-based checks |
| Data Model Changes | Medium | Contract drift can break UI | lock response models and add test snapshots |
| External Dependencies | Low | Standard FastAPI stack only | pin versions and smoke test app startup |
| Test Coverage Gap | High | No API tests currently exist | add endpoint tests and run-store unit tests |
| Feature Coupling | Medium | API drives downstream UI and artifact features | include end-to-end solve-route integration test |

### Specific Risks

#### Risk 1: Path Traversal in run_id and filename
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Resolve candidate path with `Path.resolve()`
  - Verify candidate is child of output root before access
  - Reject traversal attempts with HTTP 404/400
- **Contingency:** Add explicit exploit tests and block release until green

#### Risk 2: Incorrect Run ID Sequencing Under Concurrency
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Use filesystem lock or atomic create on ID allocation
  - Scan existing run directories for date-scoped max index
- **Contingency:** fallback retry loop on collision

#### Risk 3: ContractError not mapped to HTTP 422
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** explicit exception handler and endpoint-level guard
- **Contingency:** add regression test asserting response code + details shape

---

## Development Plan

## Implementation Approach: HYBRID (Modification + New Components)

### Rationale
RF-001 internals exist and should be reused. RF-002 API layer and run-storage components are missing, so implementation combines new API files with minimal integration updates to current recommender outputs.

### Strategy Summary
- **New Components:** 6
  - `api/app.py`, `api/models.py`, `api/run_store.py`, `api/__init__.py`, API tests, run-store tests
- **Modified Components:** 2
  - `scripts/requirements.txt`, optional small serialization-safe adjustments in `recommender.py`
- **Unchanged Components:** RF-001 solver/stacking/contracts logic

## Files to CREATE

### 1. API Models
**File:** `scripts/pallet_coach/api/models.py`

Create Pydantic v2 models:
- `SolveRequest`
- `SolveResponse`
- `SummaryRequest`
- `SummaryResponse`
- `SummaryUiRequest`
- `SummaryUiResponse`
- `DiagramRequest`
- `DiagramResponse`

Validation rules:
- `max_solutions` constrained `ge=1, le=250` default 25
- `include_timestamp` default true
- `style` enum: `short|detailed`
- `view` enum: `flat|3d`

### 2. Run Store Utility
**File:** `scripts/pallet_coach/api/run_store.py`

Required functions:
1. `get_output_root() -> Path`
2. `ensure_output_root() -> Path`
3. `allocate_run_id(now_utc: datetime | None = None) -> str`
4. `create_run_dir(run_id: str) -> Path`
5. `resolve_run_dir_safe(run_id: str) -> Path`
6. `write_bundle(run_dir: Path, bundle: dict) -> Path`
7. `append_run_log(run_dir: Path, message: str) -> Path`
8. `tail_run_log(run_dir: Path, n_lines: int = 200) -> str`
9. `archive_loose_root_files()` optional startup housekeeping

### 3. FastAPI App
**File:** `scripts/pallet_coach/api/app.py`

Implement:
- `app = FastAPI(...)`
- Startup hook: ensure output root + optional archive loose files
- Static mount: `/output` -> output root
- Routes:
  - `GET /health`
  - `POST /api/solve`
  - `GET /api/runs/{run_id}`
  - `GET /api/runs/{run_id}/logs`
  - `POST /api/summary` (stub returning 501 until RF-004)
  - `POST /api/summary_ui` (stub returning 501 until RF-004)
  - `POST /api/diagram` (stub returning 501 until RF-004)

`/api/solve` behavior:
1. allocate run ID + create run dir
2. call `recommend()`
3. build `bundle.json` minimum schema block
4. write `bundle.json` and `run_log.txt`
5. return `SolveResponse`

Exception mapping:
- `ContractError` -> HTTP 422 with details
- missing run -> HTTP 404

### 4. API Package Marker
**File:** `scripts/pallet_coach/api/__init__.py`

Export app object for Uvicorn import path.

### 5. Tests
**File:** `scripts/tests/test_api_app.py`

Test cases:
1. health returns `{"status": "ok"}`
2. invalid solve contract returns 422
3. valid solve creates run and bundle + expected response keys
4. missing run ID returns 404 for bundle endpoint
5. log endpoint returns plain text tail

**File:** `scripts/tests/test_run_store.py`

Test cases:
1. run ID format `R{n:04d}_{YYYYMMDD}`
2. daily increment behavior
3. safe run path allows valid IDs
4. traversal attempts are rejected

## Files to MODIFY

### 1. Dependencies
**File:** `scripts/requirements.txt`

Add:
- `fastapi==0.135.2`
- `uvicorn==0.32.1`
- `pydantic>=2.11`
- `httpx==0.28.1`

### 2. Recommender (if needed)
**File:** `scripts/pallet_coach/recommender.py`

Potential adjustments:
- Ensure return payload is JSON-serializable with primitive values.
- Preserve status/reasons/solutions keys to match bundle expectations.

---

## Testing Strategy

### Unit and Integration Tests
1. `scripts/tests/test_run_store.py`
   - run allocation and path safety
2. `scripts/tests/test_api_app.py`
   - endpoint behavior and status code mapping
3. Existing RF-001 tests
   - ensure no regression in solver stack

### UAT Scenarios
1. Submit solve payload to `/api/solve`, then open `/api/runs/{run_id}` and `/api/runs/{run_id}/logs`.
2. Verify `/output/{run_id}/bundle.json` is accessible.
3. Verify invalid run IDs and traversal patterns are rejected.

### Validation Commands
- `c:/python314/python.exe -m pytest scripts/tests -q`
- `c:/python314/python.exe -m uvicorn pallet_coach.api.app:app --app-dir scripts --host 127.0.0.1 --port 8000`

---

## Developer Checklist

### Setup
- [ ] Review RF-002 feature specification
- [ ] Review this implementation plan
- [ ] Ensure Python environment configured

### Implementation
- [ ] Create `scripts/pallet_coach/api/models.py`
- [ ] Create `scripts/pallet_coach/api/run_store.py`
- [ ] Create `scripts/pallet_coach/api/app.py`
- [ ] Create `scripts/pallet_coach/api/__init__.py`
- [ ] Update `scripts/requirements.txt` with FastAPI stack
- [ ] Ensure `/api` prefix and `/output` static mount
- [ ] Implement run ID allocation and safe run resolution
- [ ] Implement 422 mapping for `ContractError`
- [ ] Implement 404 mapping for missing run IDs

### Testing
- [ ] Create `scripts/tests/test_run_store.py`
- [ ] Create `scripts/tests/test_api_app.py`
- [ ] Run full test suite and confirm no RF-001 regressions
- [ ] Run local API smoke test for solve and run retrieval endpoints

### Validation
- [ ] Verify generated run IDs follow required format
- [ ] Verify `bundle.json` is created in each run directory
- [ ] Verify logs endpoint returns tail text
- [ ] Verify path traversal attempts are blocked

### Completion
- [ ] Update RF-002 status to In Development or Implemented after code delivery
- [ ] Produce implementation-complete report

---

## Troubleshooting Guide

**Issue:** `ModuleNotFoundError` for FastAPI modules  
**Fix:** install updated `scripts/requirements.txt` and verify interpreter path.

**Issue:** Static files route not serving bundle  
**Fix:** verify output root exists and FastAPI static mount path matches repo root `04_Output`.

**Issue:** run path safety false positives  
**Fix:** normalize run ID and compare `resolved_path.is_relative_to(output_root)` equivalent logic.

---

## Additional Resources

- Feature specification: `specs/features/002-api-and-run-management.md`
- Implemented dependency feature: `specs/features/001-core-solver-engine.md`
- Source requirement sections: `requirement.md` sections 5, 6.1, 9.2, 9.3, 10.2

---

**END OF IMPLEMENTATION PLAN**
