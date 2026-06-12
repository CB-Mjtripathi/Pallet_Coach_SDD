# Feature: Deployment, Security, and Operational Readiness

**Feature ID:** RF-008
**Status:** Implemented
**Priority:** High
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Sections 10 and 13)

---

## Overview

This feature defines non-functional production requirements for performance, security, compatibility, and deployment topology. It includes local development scripts, single-container deployment architecture, dependency baselines, environment variables, and operational recommendations.

The goal is repeatable, secure deployment of Pallet Coach with clear paths for future multi-user scaling.

---

## User Stories

### US-8.1: Run local development environment quickly

**As a** developer  
**I want to** initialize and run UI + API locally with standard scripts  
**So that** I can iterate safely with minimal setup friction

**Acceptance Criteria:**
- ✅ `init_project.ps1` provisions Python venv, installs backend deps, installs UI deps.
- ✅ `start_api.ps1` runs Uvicorn at `http://127.0.0.1:8000`.
- ✅ `start_ui.ps1` runs Vite at `http://localhost:5173`.
- ✅ Vite proxy forwards `/api` and `/output` to backend.

**Technical Details:**
- Scripted setup for Windows-focused workflow

---

### US-8.2: Deploy as single container

**As a** DevOps engineer  
**I want to** deploy one image that serves SPA and API routes  
**So that** runtime operations stay simple for MVP rollout

**Acceptance Criteria:**
- ✅ Multi-stage Dockerfile builds UI in Node 18 and backend in Python 3.11 slim.
- ✅ Nginx serves SPA static files and proxies `/api` + `/output` to backend.
- ✅ SPA fallback serves `index.html` for non-asset routes.

**Technical Details:**
- Nginx and entrypoint as specified in requirement.md section 13.3

---

### US-8.3: Enforce security and compatibility baselines

**As a** platform owner  
**I want to** enforce secure secret handling and platform compatibility  
**So that** the system is safe and maintainable in production

**Acceptance Criteria:**
- ✅ API keys are loaded from environment variables or `env.ai` only.
- ✅ `env.ai` is in `.gitignore`.
- ✅ AI traces redact secret values before disk writes.
- ✅ Path traversal mitigation exists for run ID paths.
- ✅ Backend supports Python 3.10+ with Pydantic 2.11+.
- ✅ Frontend supports Node 18+ and latest two browser versions.

**Technical Details:**
- Environment variable inventory exactly matches requirement.md section 13.4

---

## Dependencies

### Prerequisites
- RF-002 API and static route structure
- RF-004 secure AI tracing
- RF-007 test gates for deployment readiness

### Related Features
- All functional features rely on environment and runtime readiness

---

## Technical Architecture

### Components Involved
- PowerShell setup/run scripts
- `scripts/requirements.txt`
- Dockerfile
- Nginx config and entrypoint

### Data Flow
1. Build UI static assets.
2. Install backend dependencies.
3. Start backend and reverse-proxy through Nginx.
4. Serve SPA, API, and output artifacts from one endpoint.

### APIs & Integrations
- Azure OpenAI and Google AI services configured entirely by environment variables

---

## Non-Functional Requirements

### Performance
- Solve path target <= 10 seconds for typical Step 1 inputs.

### Security
- Secret isolation, redaction, and path safety are mandatory.

### Scalability
- Planned migration paths: DB/object storage, async jobs, structured logging, metrics, readiness probes.

---

## Implementation Notes

- Keep requirements pinned/compatible for reproducible builds.
- Add auth/rate limiting before external multi-user exposure.

---

## Test Coverage

### Unit Tests Required
- Config loading tests for missing/invalid env vars
- Path safety tests on output route and run resolution

### UAT Tests Required
- Local script-based startup smoke test
- Container smoke test for SPA route, API route, and output serving

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 10 (non-functional requirements)
- Attached: `requirement.md` section 13 (deployment and infrastructure)

**Related ADRs:**
- None yet

**Implementation Files:**
- `init_project.ps1`
- `start_api.ps1`
- `start_ui.ps1`
- `scripts/requirements.txt`
- `Dockerfile`
- `docker/nginx.conf`
- `docker/entrypoint.sh`

---

## Open Questions

- Decide initial auth strategy and rate-limiting stack for post-MVP external exposure.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** `specs/implementation-plans/RF-008-deployment-security-and-ops-implementation-plan.md`

### Files Created
- `init_project.ps1`
- `start_api.ps1`
- `start_ui.ps1`
- `Dockerfile`
- `docker/nginx.conf`
- `docker/entrypoint.sh`
- `.env.template`
- `.gitignore`
- `scripts/pallet_coach/config.py`
- `scripts/tests/test_rf008_deployment_ops.py`

### Files Modified
- `scripts/requirements.txt`
- `UI/pallet_coach_ui/vite.config.ts`
- `UI/pallet_coach_ui/package.json`
- `scripts/pallet_coach/api/app.py`
- `scripts/pallet_coach/ai/azure_responses.py`
- `scripts/pallet_coach/ai/google_ai_studio.py`
- `scripts/pallet_coach/ai/tracing.py`
- `scripts/tests/test_api_app.py`

### Validation Evidence
- Backend tests: `37 passed`
- Eval harness: `6 passed, 0 failed` (`--include-sample-parity`)
- Frontend tests: `14 passed`
- Frontend build: successful

### Acceptance Criteria Coverage
- Local development scripts implemented (`init_project.ps1`, `start_api.ps1`, `start_ui.ps1`)
- Vite proxy forwards `/api` and `/output` to `127.0.0.1:8000`
- Single-container deployment assets implemented (`Dockerfile`, `docker/nginx.conf`, `docker/entrypoint.sh`)
- Environment keys supported via process env and `env.ai`; `env.ai` ignored by git
- AI trace redaction preserved with configurable trace directory
- Path traversal mitigation remains enforced for run paths and output serving
- Dependency and compatibility baseline updated (Python deps and Node/browser metadata)
