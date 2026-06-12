from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REDACTED = "***REDACTED***"


def redact_secrets(value: Any, secrets: list[str]) -> Any:
    filtered = [s for s in secrets if s]
    if not filtered:
        return value

    if isinstance(value, str):
        text = value
        for secret in filtered:
            text = text.replace(secret, REDACTED)
        return text

    if isinstance(value, list):
        return [redact_secrets(v, filtered) for v in value]

    if isinstance(value, dict):
        return {k: redact_secrets(v, filtered) for k, v in value.items()}

    return value


def append_ai_trace(run_dir: Path, event: dict[str, Any], trace_dirname: str | None = None) -> Path:
    trace_dirname = trace_dirname or os.getenv("AI_TRACE_DIRNAME", "ai_traces")
    trace_dir = run_dir / trace_dirname
    trace_dir.mkdir(parents=True, exist_ok=True)

    secrets = [
        os.getenv("AZURE_OAI_API_KEY", ""),
        os.getenv("GOOGLE_AI_API_KEY", ""),
    ]

    payload = dict(event)
    payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    payload = redact_secrets(payload, secrets)

    path = trace_dir / "ai_calls.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path
