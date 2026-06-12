# Feature: API Layer and Run Management

**Feature ID:** RF-002
**Status:** Implemented
**Priority:** Critical
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Sections 5, 6.1, 9, 10)

---

## Overview

This feature defines the FastAPI surface for solve, run retrieval, logging, AI endpoints, and static artifact delivery. It also formalizes secure run directory resolution, run identifier generation, and response contracts.

The API serves as the orchestration layer between user input, deterministic solver execution, artifact generation, and optional AI augmentation while enforcing contract validation and HTTP semantics.

---

## User Stories

### US-2.1: Solve pallet request via API

**As a** logistics engineer  
**I want to** submit one canonical payload to `/api/solve`  
**So that** I get a complete run with recommendation outputs and artifacts

**Acceptance Criteria:**
- ✅ `POST /api/solve` validates request and returns HTTP 422 on contract errors.
- ✅ Valid solve creates a unique run directory under `04_Output/<run_id>/`.
- ✅ Response follows `SolveResponse` schema including `run_id`, `out_dir`, `solver_status`, and artifacts.
- ✅ Supports `max_solutions` range 1-250 with default 25.
- ✅ Supports `include_timestamp` with default true.

**Technical Details:**
- App module: `scripts/pallet_coach/api/app.py`
- Models module: `scripts/pallet_coach/api/models.py`
- Contract parser raises `ContractError` for invalid payloads

---

### US-2.2: Access run bundle and logs

**As a** supply chain analyst  
**I want to** retrieve generated run data and execution logs  
**So that** I can audit and compare decisions

**Acceptance Criteria:**
- ✅ `GET /api/runs/{run_id}` returns parsed `bundle.json`.
- ✅ `GET /api/runs/{run_id}/logs` returns last N lines in plain text.
- ✅ Missing run IDs return HTTP 404.
- ✅ Run path resolution mitigates path traversal and confirms child path under `04_Output`.

**Technical Details:**
- Safe path normalization and parent check are mandatory
- Log endpoint reads tail from run log file only

---

### US-2.3: Serve generated output artifacts

**As an** operations manager  
**I want to** view run artifacts directly in browser  
**So that** I can review diagrams and summaries without manual file handling

**Acceptance Criteria:**
- ✅ `/output` static route is mounted to repo-root `04_Output/`.
- ✅ `GET /output/{run_id}/{filename}` serves only files inside valid run directory.
- ✅ Dev proxy forwards both `/api` and `/output` paths to backend.

**Technical Details:**
- FastAPI StaticFiles mount on `/output`
- Vite proxy entries in UI config

---

## Dependencies

### Prerequisites
- RF-001 solver and recommender
- RF-003 artifact writer and renderer

### Related Features
- RF-004 AI endpoints (`/api/summary`, `/api/summary_ui`, `/api/diagram`)
- RF-008 deployment routing via Nginx and single-container runtime

---

## Technical Architecture

### Components Involved
- `api/app.py`: route definitions and orchestration
- `api/models.py`: request/response schemas
- Output manager: run ID allocation and filesystem organization

### Data Flow
1. Receive typed request via FastAPI.
2. Validate and parse canonical contract.
3. Execute recommender and write required artifacts.
4. Return typed response for UI navigation.
5. Serve persisted run data via `/api/runs` and `/output`.

### APIs & Integrations
- `GET /health`
- `POST /api/solve`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/logs`
- `POST /api/summary`
- `POST /api/summary_ui`
- `POST /api/diagram`
- `GET /output/{run_id}/{filename}`

---

## Non-Functional Requirements

### Performance
- Typical solve response including diagrams must complete within 10 seconds.

### Security
- Path traversal protection on all run ID driven endpoints.
- No hardcoded secrets.

### Scalability
- Prepare eventual migration from filesystem to DB + object storage for multi-user workloads.

---

## Implementation Notes

- Preserve API route prefixing under `/api`.
- Optional startup routine should archive loose root files in `04_Output/`.

---

## Test Coverage

### Unit Tests Required
- Endpoint validation and HTTP 422 mapping for `ContractError`
- Run ID not found handling (HTTP 404)
- Path traversal attack test cases

### UAT Tests Required
- End-to-end solve request from UI form to run page
- Artifact access via `/output/:runId/:filename`

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 5 (API layer)
- Attached: `requirement.md` section 6.1 (run directory structure)
- Attached: `requirement.md` section 9 (contracts)
- Attached: `requirement.md` section 10.2 (security)

**Related ADRs:**
- None yet

**Implementation Files:**
- `scripts/pallet_coach/api/app.py`
- `scripts/pallet_coach/api/models.py`

---

## Open Questions

- Should log tail default line count be fixed (e.g., 200) or query-param configurable.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** specs/implementation-plans/RF-002-api-and-run-management-implementation-plan.md

**Files Created:**
- scripts/pallet_coach/api/__init__.py
- scripts/pallet_coach/api/models.py
- scripts/pallet_coach/api/run_store.py
- scripts/pallet_coach/api/app.py
- scripts/tests/test_api_app.py
- scripts/tests/test_run_store.py

**Files Modified:**
- scripts/requirements.txt

**Validation:**
- scripts/tests: 17 passed, 0 failed
- eval harness: 4 passed, 0 failed
- total checks: 21 passed, 0 failed
