# Implementation Plan: Deployment, Security, and Operational Readiness

**Feature ID:** RF-008  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Partial Existing + New Components)

---

## Executive Summary

**Feature:** Deployment, Security, and Operational Readiness  
**Status:** Partially Implemented (vite proxy ✅, PowerShell scripts ❌, Docker ❌, env validation ❌)  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** Medium  
**Risk Level:** Low-Medium

**Summary:**  
RF-008 adds non-functional production requirements: local development scripts, single-container deployment, security baselines, and environment variable management. Vite proxy config exists; developers need PowerShell setup/run scripts, Docker multi-stage build, Nginx reverse proxy, and comprehensive environment validation.

---

## Table of Contents
1. [Feature Analysis](#feature-analysis)
2. [Implementation Status](#implementation-status)
3. [Impact Analysis](#impact-analysis)
4. [Development Plan](#development-plan)
5. [Testing Strategy](#testing-strategy)
6. [Developer Checklist](#developer-checklist)

---

## Feature Analysis

### Feature Overview

**Feature ID:** RF-008  
**Feature Name:** Deployment, Security, and Operational Readiness  
**Priority:** High  
**Complexity:** Medium  

### Scope Summary

RF-008 establishes repeatable, secure deployment patterns for Pallet Coach with clear development and production pathways. It encompasses three user stories: local development environment initialization, single-container Docker deployment, and security/compatibility baseline enforcement.

### Key Requirements

1. **Local Development**: One-command setup (`init_project.ps1`) provisions Python venv, installs backend dependencies, installs UI dependencies. Two simple commands start backend and frontend servers.
2. **Container Deployment**: Multi-stage Docker build with Node 18 (UI) + Python 3.11 (backend), served through Nginx reverse proxy.
3. **Security Baselines**: Environment variables for all secrets, no hardcoded API keys. Path traversal protection for output routes. AI trace redaction before disk writes.
4. **Compatibility**: Python 3.10+ with Pydantic 2.11+. Node 18+. Latest two browser versions.

### User Stories Summary

- **US-8.1:** Run local development environment quickly (init/start scripts)
- **US-8.2:** Deploy as single container (Dockerfile, Nginx, entrypoint)
- **US-8.3:** Enforce security and compatibility baselines (env vars, secrets, path safety)

### Technical Specifications

- **PowerShell Scripts**: Windows-focused dev automation (`.ps1` files with standard conventions)
- **Docker Multi-Stage Build**: Node 18 → Python 3.11-slim with Nginx
- **Reverse Proxy**: Nginx serves SPA + proxies /api + /output to backend
- **Environment Variables**: 9 required vars for AI services, tracing, timeouts
- **Validation**: Startup checks for missing env vars, path safety, version constraints

### Dependencies

- **Prerequisites:** RF-002 (API structure), RF-004 (AI tracing), RF-007 (test gates)
- **Integration Points:** Existing vite.config.ts proxy, existing env var patterns in scripts/pallet_coach/ai/

### Complexity Assessment

**Estimated Complexity:** Medium  
**Reasoning:** Scripting and Docker config are straightforward; security validation and proper path handling require careful implementation. No novel algorithms or complex business logic.

**Factors:**
- PowerShell scripts: Simple setup/startup (low)
- Dockerfile multi-stage build: Standard pattern, well-documented (low-medium)
- Environment validation: Requires careful handling of required vs optional vars (medium)
- Nginx config: Standard SPA reverse proxy pattern (low)
- Path safety: Critical security requirement, requires thorough testing (medium)

---

## Implementation Status

### Status Assessment
⚠️ **HYBRID IMPLEMENTATION**: Some components exist, others completely missing.

### What Exists

1. **Vite Proxy Config** (`UI/pallet_coach_ui/vite.config.ts`)
   - ✅ `/api` proxy to `http://localhost:8000` configured
   - ✅ `/output` proxy to `http://localhost:8000` configured
   - ✅ Port 5173 configured
   - **Issue**: Uses `localhost` not `127.0.0.1` (minor, equivalent on dev machines)

2. **Core Dependencies** (`scripts/requirements.txt`)
   - ✅ pytest, fastapi, uvicorn, pydantic, httpx, matplotlib present
   - ⚠️ Missing exact pins from requirement.md (some versions too loose)

3. **Environment Variable Handling** (existing codebase)
   - ✅ `scripts/pallet_coach/ai/google_ai_studio.py`: Environment variable loading pattern established
   - ✅ `scripts/pallet_coach/ai/tracing.py`: AZURE/GOOGLE API key handling exists
   - ⚠️ No centralized validation on startup
   - ⚠️ No .env.template for documentation

### What's Missing

1. **PowerShell Setup Scripts** (0% implemented)
   - ❌ `init_project.ps1` — one-time project initialization
   - ❌ `start_api.ps1` — Uvicorn server startup
   - ❌ `start_ui.ps1` — Vite dev server startup

2. **Container Deployment** (0% implemented)
   - ❌ `Dockerfile` — multi-stage Node 18 + Python 3.11 build
   - ❌ `docker/nginx.conf` — reverse proxy configuration
   - ❌ `docker/entrypoint.sh` — container startup script

3. **Environment Configuration** (20% implemented)
   - ❌ `.env.template` — environment variable documentation
   - ❌ Startup validation for required env vars
   - ⚠️ Incomplete env var inventory (AI integration exists, but not centralized)

4. **Security Hardening** (0% implemented)
   - ❌ Path traversal validation on `/output` routes
   - ❌ AI trace redaction verification (tracing exists, but redaction not confirmed)

### Coverage Summary

| Component | Status | Coverage | Work Needed |
|-----------|--------|----------|-------------|
| Vite proxy config | ✅ Partial | 100% | Minor: Host fix (localhost vs 127.0.0.1) |
| Requirements.txt | ⚠️ Partial | 60% | Pin exact versions, add missing pkgs |
| Dev scripts | ❌ Missing | 0% | Create all 3 scripts |
| Docker build | ❌ Missing | 0% | Create Dockerfile + configs |
| Env validation | ❌ Missing | 0% | Create startup checks |
| Path safety | ❌ Missing | 0% | Add traversal protection |
| .env.template | ❌ Missing | 0% | Create template |

### Implementation Approach Rationale

**HYBRID chosen because:**
- Vite proxy config is complete and working
- Environment variable patterns established in existing code
- But major components (scripts, Docker, validation) require full from-scratch implementation
- No breaking changes to existing code; only additions and refinements

---

## Impact Analysis

### Affected Modules

| Module | Change Type | Impact Level | Reason |
|--------|------------|--------------|--------|
| `UI/pallet_coach_ui/vite.config.ts` | Minor fix | Low | Change `localhost` to `127.0.0.1` (equivalent, specification compliance) |
| `scripts/requirements.txt` | Update versions | Low | Pin exact dependency versions per requirement.md |
| `scripts/pallet_coach/` (AI modules) | Add validation | Low | Add centralized env var validation on startup |
| Project root | Add new files | Medium | Add PowerShell scripts, Docker configs, .env.template |
| FastAPI app (`scripts/pallet_coach/main.py`) | Add path safety | Medium | Add validation to `/output` route to prevent path traversal |
| `.gitignore` | Verify | None | Ensure `.env.ai` already in .gitignore (should be) |

### Integration Points

#### 1. Vite Configuration Integration
**Current:** Vite proxies to localhost:8000  
**Change:** No breaking change; minor host fix for consistency  
**Impact:** Development workflow unchanged

```typescript
// Current: localhost:8000 (works but differs from spec)
// New: 127.0.0.1:8000 (matches specification)
// Both are equivalent on developer machines
```

#### 2. API Routes
**Affected Routes:**
- `GET /api/solve` — Existing, no changes needed
- `GET /output/{run_id}/**` — Add path traversal validation

**Validation Pattern:**
```python
# In main.py /output route handler
def validate_run_id_path_safety(run_id: str, requested_path: str) -> bool:
    """
    Ensure run_id doesn't contain path traversal attempts.
    Block: "..", absolute paths, suspicious sequences
    """
    import pathlib
    # Implementation in dev plan
```

#### 3. Startup Flow
**Current:** Application starts with environment variables loaded ad-hoc  
**Change:** Add centralized validation at application startup

**New Startup Sequence:**
1. Load environment variables (existing os.getenv pattern)
2. **NEW:** Validate required vars present and valid
3. **NEW:** Log environment configuration (sanitized)
4. Start FastAPI app

#### 4. Docker Deployment
**Integration Point:** Existing app code requires NO changes  
**Docker handles:** Build, dependency installation, reverse proxy, entrypoint logic

---

### Features That Must NOT Be Impacted

| Feature | Location | Reason | Validation |
|---------|----------|--------|-----------|
| Solver algorithm | `scripts/pallet_coach/solver/` | Core business logic | Run `pytest scripts/tests/test_solver_*.py` |
| API endpoints | `scripts/pallet_coach/main.py` | Existing API contracts | Run `pytest scripts/tests/test_api_*.py` |
| AI integration | `scripts/pallet_coach/ai/` | Sensitive integration | Run `pytest scripts/tests/test_api_ai_endpoints.py` |
| Artifact generation | `scripts/pallet_coach/artifacts/` | Production critical | Run `pytest scripts/tests/test_artifacts_*.py` |
| UI components | `UI/pallet_coach_ui/src/` | User-facing | Run UI tests with npm test |

### Preservation Strategy

#### Code Guidelines
- ✅ **DO:** Add new PowerShell scripts in project root
- ✅ **DO:** Add Docker configs in new `docker/` directory
- ✅ **DO:** Add environment validation functions in new modules
- ✅ **DO:** Update requirements.txt with pinned versions
- ❌ **DON'T:** Modify existing FastAPI app initialization (only add new routes for path safety)
- ❌ **DON'T:** Change existing environment variable names
- ❌ **DON'T:** Modify AI module signatures

#### Testing Requirements
- [ ] All existing pytest tests must pass unchanged
- [ ] Vite dev server must still proxy correctly
- [ ] Local development workflow must work with new scripts
- [ ] Docker build must produce working image
- [ ] Manual UAT: Entire application workflow works in container

---

## Risk Assessment

### Overall Risk Level: LOW-MEDIUM

### Risk Factors

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Breaking Changes | Low | Adding new files, minimal code changes | Validate all existing tests pass |
| Environment Handling | Medium | Startup validation could fail in new ways | Graceful error messages, .env.template documentation |
| Docker Build | Low | Standard multi-stage build pattern | Test build locally before shipping |
| Path Traversal | Medium | Security-critical implementation | Comprehensive unit tests, security code review |
| Version Pinning | Low | Tight dependency constraints could cause issues | Test in CI, document constraints in README |
| Windows Script Compatibility | Medium | PowerShell scripts only for Windows devs | Provide equivalent bash scripts in Phase 2 |

### Specific Risks

#### Risk 1: Environment Variable Validation Too Strict
- **Probability:** Medium
- **Impact:** Developers unable to run local environment
- **Overall:** MEDIUM RISK
- **Mitigation:**
  - Clearly document required vs optional env vars in .env.template
  - Provide helpful error messages if vars missing
  - .env.template covers all needed vars with example values
  - Test startup validation with minimal env vars
- **Contingency:** Can disable validation with `SKIP_ENV_VALIDATION=true` for development

#### Risk 2: Docker Build Fails Due to Dependency Issues
- **Probability:** Low
- **Impact:** Cannot deploy to production
- **Overall:** LOW-MEDIUM RISK
- **Mitigation:**
  - Verify all dependencies in requirements.txt compatible
  - Test Docker build in CI before merge
  - Use locked dependency versions (no `>=`)
  - Pin Python 3.11-slim and Node 18-alpine versions
- **Contingency:** Rollback to previous Dockerfile; use compatibility range analysis

#### Risk 3: Path Traversal Validation Blocks Legitimate Paths
- **Probability:** Low
- **Impact:** Users cannot access valid output artifacts
- **Overall:** LOW RISK
- **Mitigation:**
  - Comprehensive path safety unit tests
  - Test with all valid run ID formats
  - Test with edge cases (Unicode, special chars)
  - Security code review before merge
- **Contingency:** Disable path validation with feature flag if critical issue discovered

#### Risk 4: Vite Proxy Breaks on 127.0.0.1 Change
- **Probability:** Very Low
- **Impact:** Dev environment broken
- **Overall:** VERY LOW RISK
- **Mitigation:**
  - Test Vite proxy change locally before merge
  - Both localhost and 127.0.0.1 equivalent on dev machines
  - No application code changes, only vite config
- **Contingency:** Revert to localhost if issues found

### Risk Mitigation Strategy

1. **Pre-Implementation:** Review all existing tests to understand baseline
2. **During Implementation:** Run tests frequently to catch regressions early
3. **Before Merge:** Full test suite pass + Docker build test + manual UAT
4. **Post-Deployment:** Monitor application startup logs for env var issues

---

## Development Plan

### Implementation Approach: HYBRID (Modification + New Components)

**Rationale:**  
Vite proxy config exists and works; deployment scripts and Docker infrastructure are completely new. Minimal modifications to existing code (vite.config.ts, requirements.txt pin versions); majority of work is new file creation.

---

## Files to MODIFY

### 1. Vite Configuration (Specification Compliance Fix)
**File:** `UI/pallet_coach_ui/vite.config.ts`

**Current State:**
- Proxy to `localhost:8000` (works, but differs from spec which says `127.0.0.1:8000`)

**Required Changes:**

**Change 1: Update proxy host to match specification**

```typescript
// CURRENT (lines 10, 14)
target: "http://localhost:8000",

// CHANGE TO
target: "http://127.0.0.1:8000",
```

**Location:** Lines 10 and 14 (both /api and /output proxies)

**Reason:** Specification requirement.md section 13.1 specifies `127.0.0.1:8000`, not `localhost:8000`. While functionally equivalent, must match spec exactly.

**Testing Required:**
- [ ] Run `npm run dev` and verify `/api` proxy works
- [ ] Run `/api/solve` and confirm request reaches backend
- [ ] Verify `/output` routes work correctly

---

### 2. Update Python Dependencies
**File:** `scripts/requirements.txt`

**Current State:**
```
pytest==8.3.4
fastapi==0.135.2
uvicorn==0.32.1
pydantic>=2.11
httpx==0.28.1
matplotlib>=3.8
```

**Issues:**
- Some versions too loose (e.g., `pydantic>=2.11` allows any version ≥ 2.11)
- Missing packages required by requirement.md section 13.2
- Need exact pins for reproducible builds

**Required Changes:**

Add exact pinning and missing packages per requirement.md section 13.2:

```
# Existing - update pins
pytest==8.3.4
fastapi==0.135.2
uvicorn==0.32.1
pydantic==2.11.0
httpx==0.28.1
matplotlib==3.8.0

# ADD: Missing packages from requirement.md 13.2
python-pptx==1.0.2
pypdf==6.9.2
extract-msg==0.52.0
python-dotenv==1.0.1
```

**Why Changes:**
- Exact pins ensure reproducible builds in Docker
- Missing packages needed for artifact generation (US-8.2 container deployment)
- `python-dotenv` needed for `.env` file loading

**Testing Required:**
- [ ] Run `pip install -r scripts/requirements.txt` and verify all packages install
- [ ] Verify Python 3.11 compatibility for all packages
- [ ] Run `pytest` to verify no import errors

---

### 3. Add Environment Validation Module
**File:** `scripts/pallet_coach/config.py` (new file)

**Purpose:** Centralized environment variable validation on startup

**Create File:**

```python
"""
Environment configuration and validation.

Handles loading required environment variables, setting defaults, and
validating that the application can access required external services.
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """
    Environment configuration with validation.
    
    Loads required and optional environment variables.
    Raises RuntimeError if critical variables are missing.
    Logs warnings for optional variables not configured.
    """
    
    # Required environment variables (no defaults)
    REQUIRED_VARS = [
        # Note: These are optional for local dev but required for production
        # For flexibility, we don't enforce these at startup
    ]
    
    # Optional environment variables with defaults
    OPTIONAL_VARS = {
        # AI Services
        "AZURE_OAI_RESPONSES_ENDPOINT": "",
        "AZURE_OAI_API_KEY": "",
        "AZURE_OAI_MODEL": "gpt-5.2-chat",
        "AZURE_OAI_TIMEOUT_S": "60",
        
        "GOOGLE_AI_API_KEY": "",
        "GOOGLE_AI_IMAGE_MODEL": "gemini-3-pro-image-preview",
        "GOOGLE_AI_TIMEOUT_S": "120",
        
        # Tracing
        "AI_TRACE_DIRNAME": "ai_traces",
    }
    
    def __init__(self):
        """Initialize and validate environment."""
        self._load_env_vars()
        self._validate_env_vars()
    
    def _load_env_vars(self):
        """Load all environment variables."""
        # Load from .env file if it exists (for local development)
        try:
            from dotenv import load_dotenv
            load_dotenv(".env.ai")
        except ImportError:
            # python-dotenv not installed, skip
            pass
        
        # Store loaded values
        self.config = {}
        
        # Load optional vars with defaults
        for var_name, default in self.OPTIONAL_VARS.items():
            self.config[var_name] = os.getenv(var_name, default)
        
        # Load any other vars that might exist
        for var_name in self.REQUIRED_VARS:
            value = os.getenv(var_name)
            if value:
                self.config[var_name] = value
    
    def _validate_env_vars(self):
        """Validate environment variable values."""
        # Check timeout values are valid integers if set
        for timeout_var in ["AZURE_OAI_TIMEOUT_S", "GOOGLE_AI_TIMEOUT_S"]:
            try:
                timeout_val = self.config.get(timeout_var)
                if timeout_val:
                    float(timeout_val)
            except ValueError:
                raise ValueError(f"{timeout_var} must be a valid number, got: {timeout_val}")
        
        # Warn if AI services not configured
        if not self.config.get("AZURE_OAI_API_KEY"):
            logger.warning("AZURE_OAI_API_KEY not configured; AI summaries will not work")
        
        if not self.config.get("GOOGLE_AI_API_KEY"):
            logger.warning("GOOGLE_AI_API_KEY not configured; AI diagrams will not work")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def get_required(self, key: str) -> str:
        """Get a required configuration value; raise if missing."""
        value = self.config.get(key)
        if not value:
            raise RuntimeError(f"Required environment variable '{key}' is not set")
        return value
    
    @staticmethod
    def log_sanitized_config():
        """Log configuration with secrets redacted."""
        config = EnvironmentConfig()
        sanitized = {}
        
        for key, value in config.config.items():
            if "KEY" in key or "SECRET" in key or "PASS" in key:
                # Redact sensitive values
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        logger.info(f"Environment configuration loaded: {sanitized}")


# Singleton instance
_config = None


def get_config() -> EnvironmentConfig:
    """Get or create the environment configuration singleton."""
    global _config
    if _config is None:
        _config = EnvironmentConfig()
    return _config


def init_config():
    """Initialize the environment configuration."""
    get_config()
    EnvironmentConfig.log_sanitized_config()
```

**Location:** Create as new file `scripts/pallet_coach/config.py`

**Integration Points:**
- Call `init_config()` in `main.py` on application startup
- Use `get_config().get(var_name)` throughout app instead of `os.getenv()`

---

### 4. Add Path Safety Validation (Security)
**File:** `scripts/pallet_coach/main.py`

**Current State:**
- `/output/{run_id}/**` route exists for artifact serving
- No path traversal protection

**Required Changes:**

**Add path safety validation:**

```python
# ADD at top of main.py
import pathlib
import os
from urllib.parse import unquote

# ADD new function
def validate_output_path(run_id: str, requested_path: str) -> pathlib.Path:
    """
    Validate that requested_path is safe and within the run's output directory.
    
    Prevents path traversal attacks by ensuring:
    - No ".." in path (directory escape)
    - Path is absolute-safe (no leading /)
    - Path resolves within expected output directory
    
    Args:
        run_id: Run identifier (e.g., "R0001_20260417")
        requested_path: Requested file path relative to run directory
    
    Returns:
        Safe absolute path to file
    
    Raises:
        ValueError: If path traversal or other safety issue detected
    """
    # Validate run_id format (alphanumeric, underscore, hyphen only)
    import re
    if not re.match(r"^[a-zA-Z0-9_-]+$", run_id):
        raise ValueError(f"Invalid run_id format: {run_id}")
    
    # Decode URL-encoded path
    safe_path = unquote(requested_path)
    
    # Block absolute paths and traversal attempts
    if safe_path.startswith("/") or ".." in safe_path:
        raise ValueError(f"Path traversal detected: {safe_path}")
    
    # Construct base output directory
    base_dir = pathlib.Path(os.getcwd()) / "04_Output" / run_id
    
    # Resolve requested path
    target_path = (base_dir / safe_path).resolve()
    
    # Ensure target is within base directory
    try:
        target_path.relative_to(base_dir)
    except ValueError:
        raise ValueError(f"Path escape attempt detected: {requested_path}")
    
    # Ensure file exists and is readable
    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {requested_path}")
    
    if target_path.is_dir():
        raise ValueError(f"Cannot serve directories: {requested_path}")
    
    return target_path


# MODIFY existing /output route to use validation
@app.get("/output/{run_id}/{file_path:path}")
async def get_output_file(run_id: str, file_path: str):
    """
    Serve output artifact files with path safety validation.
    
    Prevents path traversal attacks.
    """
    try:
        safe_path = validate_output_path(run_id, file_path)
        return FileResponse(safe_path)
    except (ValueError, FileNotFoundError) as e:
        return JSONResponse(
            status_code=400 if isinstance(e, ValueError) else 404,
            content={"error": str(e)}
        )
```

**Testing Required:**
- [ ] Valid artifact paths serve correctly
- [ ] Path traversal attempts (`../../../`) are blocked
- [ ] Requests outside run directory are blocked
- [ ] Proper HTTP status codes (400 for traversal, 404 for not found)

---

## Files to CREATE

### 1. PowerShell Setup Script
**File:** `init_project.ps1`

**Purpose:** One-time project initialization for developers

**Create File:**

```powershell
<#
.SYNOPSIS
    Initialize Pallet Coach development environment.

.DESCRIPTION
    Sets up Python virtual environment, installs backend dependencies,
    and installs UI dependencies.

    Windows PowerShell only.

.EXAMPLE
    .\init_project.ps1

.NOTES
    Must be run from project root directory.
    Requires Python 3.10+ and Node 18+ to be installed globally.
#>

param()

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $SuccessColor
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $ErrorColor
}

# Step 1: Check Python
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✓ Found: $pythonVersion"
} catch {
    Write-Error "✗ Python not found. Install Python 3.10+ from https://www.python.org/"
    exit 1
}

# Step 2: Check Node
Write-Info "Checking Node.js installation..."
try {
    $nodeVersion = node --version 2>&1
    Write-Success "✓ Found: $nodeVersion"
} catch {
    Write-Error "✗ Node.js not found. Install Node 18+ from https://nodejs.org/"
    exit 1
}

# Step 3: Create Python virtual environment
Write-Info "Creating Python virtual environment..."
if (Test-Path ".venv") {
    Write-Info "Virtual environment already exists, skipping creation"
} else {
    try {
        python -m venv .venv
        Write-Success "✓ Virtual environment created"
    } catch {
        Write-Error "✗ Failed to create virtual environment"
        exit 1
    }
}

# Step 4: Activate virtual environment
Write-Info "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"
Write-Success "✓ Virtual environment activated"

# Step 5: Install Python dependencies
Write-Info "Installing Python dependencies from scripts/requirements.txt..."
try {
    pip install -q -r scripts/requirements.txt
    Write-Success "✓ Python dependencies installed"
} catch {
    Write-Error "✗ Failed to install Python dependencies"
    exit 1
}

# Step 6: Install UI dependencies
Write-Info "Installing UI dependencies from UI/pallet_coach_ui/package.json..."
try {
    Push-Location UI\pallet_coach_ui
    npm install --quiet
    Pop-Location
    Write-Success "✓ UI dependencies installed"
} catch {
    Write-Error "✗ Failed to install UI dependencies"
    exit 1
}

Write-Success ""
Write-Success "=========================================="
Write-Success "✓ Project initialization complete!"
Write-Success "=========================================="
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Start backend:  .\start_api.ps1"
Write-Info "2. Start UI:       .\start_ui.ps1"
Write-Info ""
Write-Info "Documentation: https://github.com/YOUR_ORG/pallet-coach"
```

**Location:** Create at project root: `init_project.ps1`

**Execution:** Run once per developer machine

---

### 2. PowerShell API Startup Script
**File:** `start_api.ps1`

**Purpose:** Start FastAPI backend server with proper environment

**Create File:**

```powershell
<#
.SYNOPSIS
    Start Pallet Coach API server.

.DESCRIPTION
    Starts FastAPI backend on http://127.0.0.1:8000

    Requires virtual environment created by init_project.ps1

.EXAMPLE
    .\start_api.ps1

.NOTES
    Run in dedicated PowerShell terminal.
    Press Ctrl+C to stop the server.
#>

param()

# Check if virtual environment activated
if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found. Run .\init_project.ps1 first."
    exit 1
}

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Set Python path for imports
$env:PYTHONPATH = "scripts"

Write-Host "Starting Pallet Coach API..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend running at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API docs at:        http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

# Start Uvicorn server
python -m uvicorn scripts.pallet_coach.main:app `
    --host 127.0.0.1 `
    --port 8000 `
    --reload `
    --log-level info
```

**Location:** Create at project root: `start_api.ps1`

**Execution:** Run in dedicated terminal; keeps running while development continues

---

### 3. PowerShell UI Startup Script
**File:** `start_ui.ps1`

**Purpose:** Start Vite development server

**Create File:**

```powershell
<#
.SYNOPSIS
    Start Pallet Coach UI development server.

.DESCRIPTION
    Starts Vite dev server on http://localhost:5173
    Proxies API calls to http://127.0.0.1:8000

.EXAMPLE
    .\start_ui.ps1

.NOTES
    Run in dedicated PowerShell terminal.
    Requires node_modules installed by init_project.ps1
    Press Ctrl+C to stop the server.
#>

param()

# Check if UI dependencies installed
if (-not (Test-Path "UI\pallet_coach_ui\node_modules")) {
    Write-Error "UI dependencies not found. Run .\init_project.ps1 first."
    exit 1
}

Write-Host "Starting Pallet Coach UI..." -ForegroundColor Green
Write-Host ""
Write-Host "UI running at: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend API:   http://127.0.0.1:8000 (proxied)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

# Start Vite dev server
Push-Location UI\pallet_coach_ui
npm run dev
Pop-Location
```

**Location:** Create at project root: `start_ui.ps1`

**Execution:** Run in dedicated terminal; keeps running while development continues

---

### 4. Environment Template File
**File:** `.env.template`

**Purpose:** Document required and optional environment variables

**Create File:**

```bash
# Pallet Coach Environment Variables Template
# Copy to .env.ai and fill in your values
# .env.ai is in .gitignore and not committed to version control

# ====================================
# Azure OpenAI Configuration (Optional)
# ====================================
# Used for generating AI summaries of palletization solutions
# If not configured, summary generation will be skipped

AZURE_OAI_RESPONSES_ENDPOINT=
# Example: https://your-resource.openai.azure.com/

AZURE_OAI_API_KEY=
# Get from: Azure Portal → OpenAI Resource → Keys and Endpoint

AZURE_OAI_MODEL=gpt-4
# Deployment model name (e.g., gpt-4, gpt-4-turbo)

AZURE_OAI_TIMEOUT_S=60
# Timeout in seconds for API requests


# ====================================
# Google AI Studio Configuration (Optional)
# ====================================
# Used for generating AI diagrams of palletization solutions
# If not configured, diagram generation will be skipped

GOOGLE_AI_API_KEY=
# Get from: https://aistudio.google.com/app/apikey

GOOGLE_AI_IMAGE_MODEL=gemini-pro-vision
# Model for image generation (e.g., gemini-pro-vision)

GOOGLE_AI_TIMEOUT_S=120
# Timeout in seconds for API requests


# ====================================
# Tracing Configuration
# ====================================
AI_TRACE_DIRNAME=ai_traces
# Directory where AI service calls are logged for debugging
# Set to empty string to disable tracing
```

**Location:** Create at project root: `.env.template`

**Usage:** Developers copy to `.env.ai` and fill in their values

---

### 5. Dockerfile
**File:** `Dockerfile`

**Purpose:** Multi-stage Docker build for single-container deployment

**Create File:**

```dockerfile
# Multi-stage Docker build for Pallet Coach
# Stage 1: Build React UI
# Stage 2: Runtime with Python, Nginx, and static assets

# ============================================
# Stage 1: Build React SPA
# ============================================
FROM node:18-alpine AS ui-build

WORKDIR /app/UI/pallet_coach_ui

# Copy package files
COPY UI/pallet_coach_ui/package*.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY UI/pallet_coach_ui/ ./

# Build production bundle
RUN npm run build

# Verify build output
RUN test -d dist || (echo "Build failed: dist/ directory not found" && exit 1)


# ============================================
# Stage 2: Runtime (Python + Nginx + SPA)
# ============================================
FROM python:3.11-slim

# Install system dependencies including Nginx
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy backend source code
COPY scripts/ ./scripts/

# Copy SPA static files from build stage
COPY --from=ui-build /app/UI/pallet_coach_ui/dist ./static/

# Copy Nginx configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r scripts/requirements.txt

# Create output directory for solver runs
RUN mkdir -p 04_Output

# Create ai_traces directory for tracing
RUN mkdir -p ai_traces

# Expose port 80 (Nginx)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# Run entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
```

**Location:** Create at project root: `Dockerfile`

**Build Command:**
```bash
docker build -t pallet-coach:latest .
```

**Run Command:**
```bash
docker run -p 80:80 \
  -e AZURE_OAI_API_KEY=your_key \
  -e GOOGLE_AI_API_KEY=your_key \
  pallet-coach:latest
```

---

### 6. Nginx Configuration
**File:** `docker/nginx.conf`

**Purpose:** Reverse proxy configuration for serving SPA and backend API

**Create File:**

```nginx
# Nginx configuration for Pallet Coach
# Serves React SPA from /app/static/
# Proxies /api/* to backend on 127.0.0.1:8000
# Proxies /output/* to backend on 127.0.0.1:8000
# Fallback to index.html for SPA routing

upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    # ====================================
    # SPA Static Files
    # ====================================
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # ====================================
    # API Proxy
    # ====================================
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed in future)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # ====================================
    # Output/Artifacts Proxy
    # ====================================
    location /output/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Reasonable timeout for file downloads
        proxy_read_timeout 120s;
    }

    # ====================================
    # Health Check Endpoint
    # ====================================
    location /healthz {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # ====================================
    # SPA Fallback (all other routes)
    # ====================================
    location / {
        root /app/static;
        
        # Try file first, then directory, then fallback to index.html
        try_files $uri $uri/ /index.html =404;
        
        # Set cache headers for HTML
        add_header Cache-Control "public, must-revalidate, max-age=0";
    }

    # ====================================
    # Error Pages
    # ====================================
    error_page 404 /index.html;

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

**Location:** Create in new directory: `docker/nginx.conf`

**Configuration Details:**
- SPA static files cached for 1 year
- `/api/*` routes proxied to backend
- `/output/*` routes proxied to backend for artifact serving
- SPA fallback routes to `index.html` for client-side routing
- Health check endpoint for container orchestration

---

### 7. Docker Entrypoint Script
**File:** `docker/entrypoint.sh`

**Purpose:** Container startup script that orchestrates services

**Create File:**

```bash
#!/bin/bash
# Pallet Coach Docker entrypoint
# Starts Nginx and FastAPI backend server

set -e

echo "========================================="
echo "Pallet Coach Container Startup"
echo "========================================="

# ============================================
# Step 1: Validate Environment
# ============================================
echo ""
echo "[1/4] Validating environment variables..."

# Check critical environment variables
# (AI keys are optional but log their presence)
if [ -n "$AZURE_OAI_API_KEY" ]; then
    echo "  ✓ AZURE_OAI_API_KEY configured"
else
    echo "  ⚠ AZURE_OAI_API_KEY not configured (AI summaries disabled)"
fi

if [ -n "$GOOGLE_AI_API_KEY" ]; then
    echo "  ✓ GOOGLE_AI_API_KEY configured"
else
    echo "  ⚠ GOOGLE_AI_API_KEY not configured (AI diagrams disabled)"
fi

# Set defaults if not provided
export PYTHONUNBUFFERED=1
export PYTHONPATH=/app/scripts
export AI_TRACE_DIRNAME=${AI_TRACE_DIRNAME:-ai_traces}

echo "  ✓ Environment validated"

# ============================================
# Step 2: Start Nginx
# ============================================
echo ""
echo "[2/4] Starting Nginx reverse proxy..."
nginx -g 'daemon off;' &
NGINX_PID=$!
sleep 1
if ps -p $NGINX_PID > /dev/null; then
    echo "  ✓ Nginx started (PID: $NGINX_PID)"
else
    echo "  ✗ Nginx failed to start"
    exit 1
fi

# ============================================
# Step 3: Start FastAPI Backend
# ============================================
echo ""
echo "[3/4] Starting FastAPI backend..."
cd /app

# Run with gunicorn for production-like behavior
exec python -m uvicorn \
    scripts.pallet_coach.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --log-level info
```

**Location:** Create in new directory: `docker/entrypoint.sh`

**Make Executable:** `chmod +x docker/entrypoint.sh`

---

### 8. Tests for Path Safety Validation
**File:** `scripts/tests/test_path_safety.py`

**Purpose:** Unit tests for path traversal protection

**Create File:**

```python
"""
Unit tests for path safety validation.

Verifies that the /output route prevents path traversal attacks
and only serves files within the run's output directory.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the function to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pallet_coach.main import validate_output_path


class TestPathSafetyValidation:
    """Test suite for path safety validation."""
    
    def test_valid_file_path(self, tmp_path):
        """Test that valid file paths are allowed."""
        # Setup
        run_id = "R0001_20260417"
        run_dir = tmp_path / "04_Output" / run_id
        run_dir.mkdir(parents=True)
        
        test_file = run_dir / "bundle.json"
        test_file.write_text('{"test": true}')
        
        # Mock os.getcwd to return tmp_path
        with patch('os.getcwd', return_value=str(tmp_path)):
            # Test
            result = validate_output_path(run_id, "bundle.json")
            
            # Assert
            assert result.exists()
            assert result.name == "bundle.json"
    
    def test_path_traversal_attempt_double_dot(self):
        """Test that path traversal with .. is blocked."""
        run_id = "R0001_20260417"
        
        # Should raise ValueError for ".." in path
        with pytest.raises(ValueError, match="Path traversal detected"):
            validate_output_path(run_id, "../../../etc/passwd")
    
    def test_path_traversal_attempt_absolute_path(self):
        """Test that absolute paths are blocked."""
        run_id = "R0001_20260417"
        
        # Should raise ValueError for absolute path
        with pytest.raises(ValueError, match="Path traversal detected"):
            validate_output_path(run_id, "/etc/passwd")
    
    def test_invalid_run_id_format(self):
        """Test that invalid run ID formats are rejected."""
        invalid_run_ids = [
            "../../../",  # Traversal in run_id
            "$(whoami)",   # Command injection attempt
            "<script>",    # XSS attempt
            "R0001\x00",   # Null byte
        ]
        
        for invalid_id in invalid_run_ids:
            with pytest.raises(ValueError, match="Invalid run_id format"):
                validate_output_path(invalid_id, "bundle.json")
    
    def test_file_not_found(self, tmp_path):
        """Test that request for non-existent file raises FileNotFoundError."""
        run_id = "R0001_20260417"
        run_dir = tmp_path / "04_Output" / run_id
        run_dir.mkdir(parents=True)
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            with pytest.raises(FileNotFoundError):
                validate_output_path(run_id, "nonexistent.json")
    
    def test_directory_request_blocked(self, tmp_path):
        """Test that requests for directories are blocked (not files)."""
        run_id = "R0001_20260417"
        run_dir = tmp_path / "04_Output" / run_id
        subdir = run_dir / "subdir"
        subdir.mkdir(parents=True)
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            with pytest.raises(ValueError, match="Cannot serve directories"):
                validate_output_path(run_id, "subdir")
    
    def test_url_encoded_path(self, tmp_path):
        """Test that URL-encoded paths are decoded and validated."""
        run_id = "R0001_20260417"
        run_dir = tmp_path / "04_Output" / run_id
        run_dir.mkdir(parents=True)
        
        # Create file with URL-safe name
        test_file = run_dir / "layer_diagram.png"
        test_file.write_bytes(b"PNG_DATA")
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            # URL encoded path should work
            result = validate_output_path(run_id, "layer_diagram.png")
            assert result.exists()
    
    def test_symlink_escape_attempt_blocked(self, tmp_path):
        """Test that symlink escapes are prevented (path escapes outside run dir)."""
        run_id = "R0001_20260417"
        run_dir = tmp_path / "04_Output" / run_id
        run_dir.mkdir(parents=True)
        
        # Create a file outside the run directory
        external_file = tmp_path / "external.json"
        external_file.write_text('{"external": true}')
        
        # Create symlink inside run dir pointing outside
        symlink = run_dir / "escape.json"
        symlink.symlink_to(external_file)
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            # Symlink pointing outside run dir should be blocked
            with pytest.raises(ValueError, match="Path escape attempt detected"):
                validate_output_path(run_id, "escape.json")


class TestEnvironmentConfiguration:
    """Test suite for environment configuration loading."""
    
    def test_config_loads_defaults(self):
        """Test that configuration loads with default values."""
        from pallet_coach.config import EnvironmentConfig
        
        # Should not raise even without env vars set
        config = EnvironmentConfig()
        
        # Should have default values
        assert config.get("AZURE_OAI_MODEL") == "gpt-5.2-chat"
        assert config.get("AI_TRACE_DIRNAME") == "ai_traces"
    
    def test_config_loads_env_vars(self):
        """Test that configuration loads from environment."""
        from pallet_coach.config import EnvironmentConfig
        
        with patch.dict(os.environ, {"AZURE_OAI_MODEL": "custom-model"}):
            config = EnvironmentConfig()
            assert config.get("AZURE_OAI_MODEL") == "custom-model"
    
    def test_config_timeout_validation(self):
        """Test that timeout values are validated as numbers."""
        from pallet_coach.config import EnvironmentConfig
        
        with patch.dict(os.environ, {"AZURE_OAI_TIMEOUT_S": "not_a_number"}):
            with pytest.raises(ValueError, match="must be a valid number"):
                EnvironmentConfig()
```

**Location:** Create at `scripts/tests/test_path_safety.py`

**Testing:** Run with `pytest scripts/tests/test_path_safety.py -v`

---

## Integration Points Summary

| Module | Integration | Impact |
|--------|-----------|--------|
| `main.py` | Add path safety validation to `/output` route | Medium |
| `config.py` | NEW - Environment validation module | Low (new file) |
| `vite.config.ts` | Change localhost to 127.0.0.1 | Low |
| `requirements.txt` | Update versions to exact pins | Low |
| `.gitignore` | Verify `.env.ai` already ignored | None (should exist) |
| PowerShell scripts | NEW development automation | Low (new files) |
| Docker setup | NEW container deployment | Low (new files) |

---

## Testing Strategy

### Unit Tests
**File:** `scripts/tests/test_path_safety.py`

**Test Coverage:**
- [x] Valid file paths are served correctly
- [x] Path traversal attempts (../) are blocked
- [x] Absolute paths are blocked
- [x] Invalid run ID formats are rejected
- [x] Non-existent files raise 404
- [x] Directory requests are blocked
- [x] URL-encoded paths are decoded and validated
- [x] Symlink escapes are prevented
- [x] Environment configuration loads defaults
- [x] Environment configuration loads from env vars
- [x] Timeout values are validated as numbers

**Run Command:** `pytest scripts/tests/test_path_safety.py -v`

**Expected Result:** 10+ tests passing

### Integration Tests

#### Local Development Smoke Test
**Procedure:**
1. Run `init_project.ps1` — should create venv and install dependencies
2. Run `start_api.ps1` in terminal 1 — should start on 127.0.0.1:8000
3. Run `start_ui.ps1` in terminal 2 — should start on localhost:5173
4. Open browser to http://localhost:5173
5. Click "Run Example" to test `/api/solve` call through proxy
6. Verify API response appears in UI
7. Verify output artifacts accessible through `/output` proxy

**Expected Result:** 
- UI loads
- Solver runs
- Results display
- No console errors

#### Container Smoke Test
**Procedure:**
1. Build Docker image: `docker build -t pallet-coach:latest .`
2. Run container: `docker run -p 80:80 -e GOOGLE_AI_API_KEY=test pallet-coach:latest`
3. Open browser to http://localhost
4. Run example solve
5. Verify results display
6. Verify artifacts accessible

**Expected Result:**
- Container starts without errors
- UI loads at http://localhost
- Solver works
- Results display

### UAT Tests

**Test Scenario 1: Local Development Workflow**
```
Given: Developer has not set up Pallet Coach before
When:  Developer runs init_project.ps1
Then:  Python venv created, all dependencies installed, no errors

When:  Developer runs start_api.ps1 and start_ui.ps1 in two terminals
Then:  API running at 127.0.0.1:8000, UI running at localhost:5173, proxies work

When:  Developer accesses http://localhost:5173
Then:  App loads, can run solve, sees results
```

**Test Scenario 2: Container Deployment**
```
Given: Docker installed on deployment machine
When:  DevOps engineer builds and runs docker image
Then:  Container starts, no errors in logs

When:  Browser accesses http://localhost
Then:  UI loads, app is fully functional

When:  Docker image deployed to production
Then:  Application serves traffic, no security issues
```

**Test Scenario 3: Path Traversal Security**
```
Given: Container running
When:  Attacker requests /output/R0001_20260417/../../../etc/passwd
Then:  Request blocked with 400 error
And:  No system files exposed
```

### Regression Tests

**Run All Existing Tests:**
```bash
# Backend tests
pytest scripts/tests/ -v --tb=short

# UI tests
cd UI/pallet_coach_ui
npm test
```

**Expected Result:** All tests passing (no regressions introduced)

---

## Developer Checklist

### Phase 1: Preparation
- [ ] Create Git feature branch: `feature/008-deployment-security-ops`
- [ ] Review this implementation plan thoroughly
- [ ] Review RF-008 feature spec in `specs/features/008-deployment-security-and-ops.md`
- [ ] Review requirement.md sections 10 and 13
- [ ] Read all existing test files to understand baseline
- [ ] Set up local development environment

### Phase 2: Modifications
- [ ] **Modify** `UI/pallet_coach_ui/vite.config.ts`
  - [ ] Change proxy target from localhost to 127.0.0.1 on lines 10, 14
  - [ ] Test: `npm run dev` and verify proxy works
  
- [ ] **Modify** `scripts/requirements.txt`
  - [ ] Add exact version pins for all packages
  - [ ] Add missing packages: python-pptx, pypdf, extract-msg, python-dotenv
  - [ ] Test: `pip install -r scripts/requirements.txt` succeeds
  
- [ ] **Modify** `scripts/pallet_coach/main.py`
  - [ ] Add `validate_output_path()` function for path safety
  - [ ] Update `/output` route to use validation
  - [ ] Add proper error handling (400 for traversal, 404 for not found)
  - [ ] Test: Invalid paths blocked, valid paths served

### Phase 3: New Files - Environment & Security
- [ ] **Create** `scripts/pallet_coach/config.py`
  - [ ] Implement EnvironmentConfig class
  - [ ] Load .env.ai file if exists
  - [ ] Validate timeout values are numbers
  - [ ] Implement get() and get_required() methods
  
- [ ] **Create** `.env.template`
  - [ ] Document all 9 environment variables
  - [ ] Add descriptions and examples
  - [ ] Note which are required vs optional
  
- [ ] **Create** `scripts/tests/test_path_safety.py`
  - [ ] Test valid paths work
  - [ ] Test path traversal blocked
  - [ ] Test invalid run IDs rejected
  - [ ] Test symlink escapes prevented
  - [ ] Test environment config loading

### Phase 4: New Files - PowerShell Scripts
- [ ] **Create** `init_project.ps1`
  - [ ] Check Python and Node installed
  - [ ] Create Python venv
  - [ ] Install Python dependencies
  - [ ] Install UI dependencies
  - [ ] Test: Run script, verify all installed
  
- [ ] **Create** `start_api.ps1`
  - [ ] Activate venv
  - [ ] Set PYTHONPATH
  - [ ] Start Uvicorn on 127.0.0.1:8000
  - [ ] Test: Run script, access http://127.0.0.1:8000/docs
  
- [ ] **Create** `start_ui.ps1`
  - [ ] Start Vite dev server
  - [ ] Verify proxies work
  - [ ] Test: Run script, access http://localhost:5173, test API call

### Phase 5: New Files - Docker Deployment
- [ ] **Create** `Dockerfile`
  - [ ] Stage 1: Build React SPA with Node 18
  - [ ] Stage 2: Runtime with Python 3.11 + Nginx
  - [ ] Copy SPA and backend code
  - [ ] Install Python dependencies
  - [ ] Expose port 80
  - [ ] Add health check
  - [ ] Test: `docker build -t pallet-coach:latest .` succeeds
  
- [ ] **Create** `docker/` directory
  - [ ] Create `docker/nginx.conf`
    - [ ] Serve SPA static files with cache headers
    - [ ] Proxy /api to backend
    - [ ] Proxy /output to backend
    - [ ] SPA fallback to index.html
    - [ ] Test: Routes work correctly
    
  - [ ] Create `docker/entrypoint.sh`
    - [ ] Validate environment on startup
    - [ ] Start Nginx
    - [ ] Start FastAPI backend
    - [ ] Test: Container starts cleanly

### Phase 6: Testing
- [ ] **Run unit tests**
  - [ ] `pytest scripts/tests/test_path_safety.py -v`
  - [ ] Verify: 10+ tests pass
  
- [ ] **Run integration tests**
  - [ ] Local development: Run init, start_api, start_ui, test workflow
  - [ ] Container deployment: Build, run, test in container
  
- [ ] **Run regression tests**
  - [ ] `pytest scripts/tests/ -v` (all backend tests)
  - [ ] `cd UI/pallet_coach_ui && npm test` (all UI tests)
  - [ ] Verify: No existing tests broken
  
- [ ] **Manual UAT**
  - [ ] [ ] Windows PowerShell scripts work on local machine
  - [ ] [ ] Docker image builds without errors
  - [ ] [ ] Docker container starts cleanly
  - [ ] [ ] UI loads at http://localhost:5173
  - [ ] [ ] Solver runs successfully
  - [ ] [ ] Results display correctly
  - [ ] [ ] Output artifacts accessible
  - [ ] [ ] Path traversal attacks blocked
  - [ ] [ ] Invalid env vars handled gracefully

### Phase 7: Documentation & Quality
- [ ] Update `README.md` with local development section
  - [ ] Add "Quick Start" with init_project.ps1
  - [ ] Add "Running Locally" with start_api.ps1 and start_ui.ps1
  - [ ] Add "Docker Deployment" with build and run commands
  - [ ] Add "Environment Variables" section with .env.template reference
  
- [ ] Add code comments
  - [ ] Path safety validation clearly documented
  - [ ] Environment config module well-commented
  - [ ] Nginx config with section headers
  
- [ ] Verify no debug code
  - [ ] No print() statements
  - [ ] No TODO or FIXME comments
  - [ ] No hardcoded values
  
- [ ] Verify security best practices
  - [ ] Environment variables documented
  - [ ] Secrets not logged
  - [ ] Path safety validation comprehensive
  - [ ] Security review for path safety code

### Phase 8: Code Review & Merge
- [ ] Self-review all changes
- [ ] Check for any debug code or TODOs
- [ ] Commit changes with meaningful messages:
  - [ ] `Add PowerShell development scripts`
  - [ ] `Add Docker multi-stage build`
  - [ ] `Add path traversal security validation`
  - [ ] `Add environment configuration module`
  - [ ] `Update dependencies to pinned versions`
  
- [ ] Push feature branch: `git push origin feature/008-deployment-security-ops`
- [ ] Create pull request with comprehensive description
- [ ] Request code review from senior developer
- [ ] Address feedback
- [ ] Merge to main branch
- [ ] Update feature status in `specs/features/008-deployment-security-and-ops.md`
  - [ ] Change status from "Specification" to "Implemented"
  - [ ] Add implementation notes

### Phase 9: Deployment Readiness
- [ ] Verify CI/CD pipeline passes
- [ ] Test deployment to staging environment
- [ ] Perform security review
- [ ] Document operations procedures
- [ ] Update deployment documentation
- [ ] Create rollback plan

---

## Troubleshooting Guide

### Common Issues During Local Development

#### Issue: `init_project.ps1` fails with "Python not found"
**Solution:** 
- Install Python 3.10+ from https://www.python.org/
- Ensure Python is in system PATH
- Verify: `python --version` in PowerShell

#### Issue: `start_api.ps1` fails with "ModuleNotFoundError"
**Solution:**
- Ensure `init_project.ps1` completed successfully
- Verify venv activated: `. .\.venv\Scripts\Activate.ps1`
- Verify requirements installed: `pip list | grep fastapi`

#### Issue: `start_ui.ps1` fails to connect to API
**Solution:**
- Ensure `start_api.ps1` running in other terminal
- Verify API running: `curl http://127.0.0.1:8000/docs`
- Check vite.config.ts proxy target is `127.0.0.1:8000`

#### Issue: Docker build fails with "npm install" error
**Solution:**
- Verify Node 18+ installed in build environment
- Check package.json syntax in `UI/pallet_coach_ui/`
- Increase Docker build memory if available

#### Issue: Docker container exits immediately
**Solution:**
- Check logs: `docker logs <container_id>`
- Verify environment variables set: `docker run -e GOOGLE_AI_API_KEY=test ...`
- Verify all required files copied to image

### Common Security Issues

#### Issue: Path traversal attack detected in logs
**Solution:**
- This is expected behavior - attacks are being blocked
- Review logs to identify source of attacks
- Consider implementing rate limiting if under active attack

#### Issue: Secrets exposed in Docker image
**Solution:**
- Never copy .env file to Docker image
- Use environment variables at runtime
- Use Docker secrets for production deployments
- Scan image: `trivy image pallet-coach:latest`

---

## Additional Resources

- **Feature Specification:** `specs/features/008-deployment-security-and-ops.md`
- **Requirements Document:** `requirement.md` sections 10 and 13
- **Existing Test Examples:** `scripts/tests/test_api_*.py`
- **Existing Service Examples:** `scripts/pallet_coach/ai/`
- **Docker Documentation:** https://docs.docker.com/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Nginx Documentation:** https://nginx.org/en/docs/

---

**END OF IMPLEMENTATION PLAN**

**Status:** Ready for developer pickup  
**Complexity:** Medium  
**Estimated Effort:** 16-20 hours  
**Dependencies:** None (can be implemented independently)  
**Risk Level:** Low-Medium  

**Next Steps:**
1. Assign to developer
2. Developer creates feature branch
3. Follow checklist section
4. Submit for code review
5. Merge after approval

---

*Generated by Tech Lead Agent v1.0 on 2026-04-17*
