from __future__ import annotations

import os
from typing import Any

import httpx

from ..config import load_env_ai


def evaluate_rewrite_readiness() -> dict[str, Any]:
    """Evaluate whether AI rewrite path is configured for provider calls."""
    load_env_ai()

    required = [
        "AZURE_OAI_RESPONSES_ENDPOINT",
        "AZURE_OAI_API_KEY",
        "AZURE_OAI_MODEL",
    ]

    missing = [name for name in required if not str(os.getenv(name, "")).strip()]
    if missing:
        return {
            "status": "fail",
            "reason_code": "config_missing",
            "message": f"Missing required rewrite config: {', '.join(missing)}",
        }

    endpoint = str(os.getenv("AZURE_OAI_RESPONSES_ENDPOINT", "")).strip()
    if not endpoint.startswith("http"):
        return {
            "status": "fail",
            "reason_code": "config_missing",
            "message": "AZURE_OAI_RESPONSES_ENDPOINT must be an absolute URL",
        }

    timeout_raw = str(os.getenv("AZURE_OAI_TIMEOUT_S", "")).strip()
    if timeout_raw:
        try:
            float(timeout_raw)
        except ValueError:
            return {
                "status": "fail",
                "reason_code": "config_missing",
                "message": f"Invalid numeric timeout for AZURE_OAI_TIMEOUT_S: {timeout_raw}",
            }

    return {
        "status": "pass",
        "reason_code": "ready",
        "message": "Rewrite readiness checks passed",
    }


def classify_rewrite_exception(exc: Exception) -> str:
    """Map provider/runtime exceptions to stable RF-011 reason codes."""
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        return "timeout"

    if isinstance(exc, httpx.TransportError):
        return "endpoint_unreachable"

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code in {401, 403}:
            return "auth_error"
        if status_code in {404, 400}:
            return "deployment_mismatch"
        if status_code == 408:
            return "timeout"
        return "provider_error"

    text = str(exc).lower()
    if "missing required environment variable" in text:
        return "config_missing"
    if "api key" in text or "unauthorized" in text or "forbidden" in text:
        return "auth_error"
    if "name resolution" in text or "connection refused" in text or "could not resolve" in text:
        return "endpoint_unreachable"
    if "deployment" in text and ("mismatch" in text or "not found" in text):
        return "deployment_mismatch"
    if "timeout" in text or "budget" in text:
        return "timeout"

    return "provider_error"
