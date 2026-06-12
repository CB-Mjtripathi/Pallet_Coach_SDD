from __future__ import annotations

import json

from pallet_coach.ai.tracing import REDACTED, append_ai_trace


def test_append_ai_trace_creates_jsonl_and_redacts_secrets(tmp_path, monkeypatch):
    monkeypatch.setenv("AZURE_OAI_API_KEY", "azure-secret")
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "google-secret")

    event = {
        "provider": "azure_openai",
        "prompt": "token=azure-secret and key=google-secret",
        "nested": {"raw": "google-secret"},
    }

    trace_path = append_ai_trace(tmp_path, event)
    assert trace_path.exists()

    lines = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["provider"] == "azure_openai"
    assert payload["prompt"].count(REDACTED) == 2
    assert payload["nested"]["raw"] == REDACTED
    assert "timestamp" in payload
