from __future__ import annotations

import base64
import os
import time
from typing import Any

import httpx

from ..config import load_env_ai


def _required_env(name: str) -> str:
    load_env_ai()
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _find_image_b64(data: Any) -> str | None:
    if isinstance(data, dict):
        inline_data = data.get("inlineData")
        if isinstance(inline_data, dict):
            b64 = inline_data.get("data")
            mime = inline_data.get("mimeType", "")
            if isinstance(b64, str) and b64 and "image" in str(mime):
                return b64

        for value in data.values():
            found = _find_image_b64(value)
            if found:
                return found

    if isinstance(data, list):
        for item in data:
            found = _find_image_b64(item)
            if found:
                return found

    return None


def generate_diagram_image(prompt_text: str, view: str) -> tuple[bytes, dict[str, Any]]:
    api_key = _required_env("GOOGLE_AI_API_KEY")
    model = os.getenv("GOOGLE_AI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    timeout_s = float(os.getenv("GOOGLE_AI_TIMEOUT_S", "120"))

    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Generate a polished {view} diagram as PNG."},
                    {"text": prompt_text},
                ]
            }
        ]
    }

    started = time.perf_counter()
    response = httpx.post(endpoint, json=payload, timeout=timeout_s)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    response.raise_for_status()

    body = response.json()
    image_b64 = _find_image_b64(body)
    if not image_b64:
        raise RuntimeError("Google AI Studio response did not include image bytes")

    image_bytes = base64.b64decode(image_b64)
    metadata = {
        "provider": "google_ai_studio",
        "endpoint": endpoint,
        "model": model,
        "latency_ms": elapsed_ms,
    }
    return image_bytes, metadata
