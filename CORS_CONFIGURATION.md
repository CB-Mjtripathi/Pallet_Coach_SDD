# CORS Configuration & Cross-Origin Error Resolution

## Problem

When running the Pallet Coach application locally with separate services:
- **Frontend (React UI)**: http://127.0.0.1:5173 (port 5173)
- **Backend (FastAPI)**: http://127.0.0.1:8000 (port 8000)

The browser would block API requests with error: `{"detail":"Not Found"}` due to missing CORS headers.

## Root Cause

Cross-Origin Resource Sharing (CORS) restrictions require:
1. The API to explicitly allow requests from different origins
2. Proper headers in API responses to indicate allowed origins, methods, and headers

**Without CORS middleware**, the API returns 404 for cross-origin requests, which appears as `{"detail":"Not Found"}` in the browser.

---

## Solution Implemented

### 1. **Backend API (FastAPI) - CORS Middleware**

**File**: `scripts/pallet_coach/api/app.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Development: UI local host
        "http://127.0.0.1:5173",      # Development: UI loopback
        "http://localhost:3000",      # Alternative dev port
        "http://127.0.0.1:3000",      # Alternative dev port loopback
    ],
    allow_credentials=True,
    allow_methods=["*"],             # Allow all HTTP methods
    allow_headers=["*"],             # Allow all request headers
)
```

**What it does:**
- Allows requests from specified UI origins
- Sets CORS response headers to permit cross-origin requests
- Enables requests with credentials (cookies, auth headers)

### 2. **Frontend Dev Server Proxy (Vite)**

**File**: `UI/pallet_coach_ui/vite.config.ts`

```typescript
server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/output": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
}
```

**What it does:**
- During development, Vite acts as a proxy
- Requests to `/api/*` are forwarded to the API server
- This avoids CORS issues when making API calls from the UI

### 3. **Enhanced Error Handling (Frontend)**

**File**: `UI/pallet_coach_ui/src/api/client.ts`

Improved error messages to distinguish between:
- Network connectivity errors
- API response errors
- CORS/connection issues

**File**: `UI/pallet_coach_ui/src/pages/Home.tsx`

Added helpful error messages that guide users to:
- Check if API server is running
- Verify API configuration
- Understand the actual error from the API

---

## Development Setup

### Starting the Application

1. **Initialize dependencies** (first time only):
   ```powershell
   .\init_project.ps1
   ```

2. **Start the API server** (Terminal 1):
   ```powershell
   .\start_api.ps1
   ```
   - Runs on: http://127.0.0.1:8000
   - With CORS middleware enabled

3. **Start the UI dev server** (Terminal 2):
   ```powershell
   .\start_ui.ps1
   ```
   - Runs on: http://127.0.0.1:5173
   - Proxies `/api` and `/output` to the API

4. **Access the UI**:
   - Open browser to: http://127.0.0.1:5173

---

## Production Configuration

For production deployment, **restrict CORS origins**:

```python
allow_origins=[
    "https://your-domain.com",          # Your production domain
    "https://www.your-domain.com",      # With www
],
allow_credentials=True,
allow_methods=["GET", "POST"],          # Only required methods
allow_headers=["Content-Type"],         # Only required headers
```

⚠️ **Never use** `allow_origins=["*"]` with `allow_credentials=True` in production.

---

## Testing the Fix

1. Fill in the form on the UI with sample data:
   - Case Length: 410 mm
   - Case Width: 280 mm
   - Case Height: 160 mm
   - Layers: 8

2. Click **"Get Started"**

3. Expected result:
   - ✅ Form submits successfully
   - ✅ Redirected to results page with pallet patterns
   - ✅ No "Not Found" error

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Network error: Unable to connect to API" | Ensure API is running: `.\start_api.ps1` on port 8000 |
| "Connection refused" | Check firewall, ensure port 8000 is not blocked |
| CORS error in browser console | Verify CORS middleware is loaded (check app startup logs) |
| "Cannot POST /api/solve" | Check API routes are registered (visit http://127.0.0.1:8000/docs) |

---

## Files Modified for CORS Fix

1. ✅ `scripts/pallet_coach/api/app.py` - Added CORSMiddleware
2. ✅ `UI/pallet_coach_ui/vite.config.ts` - Proxy configuration (already correct)
3. ✅ `UI/pallet_coach_ui/src/api/client.ts` - Enhanced error handling
4. ✅ `UI/pallet_coach_ui/src/pages/Home.tsx` - Better error messages

---

## References

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [Vite Proxy Configuration](https://vitejs.dev/config/server-options.html#server-proxy)
- [MDN CORS Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

**Last Updated**: 2026-06-12  
**Status**: ✅ CORS properly configured for development and ready for production adjustments
