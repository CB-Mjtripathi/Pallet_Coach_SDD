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


def test_append_ai_trace_preserves_latency_dimensions(tmp_path):
    event = {
        "provider": "azure_openai",
        "operation": "summary_ui",
        "endpoint": "/api/summary_ui",
        "payload_profile": "medium",
        "outcome": "reused_artifact",
        "reason_code": "identical_fingerprint",
        "stage_timings_ms": {
            "parse_ms": 1,
            "context_prep_ms": 12,
            "provider_ms": 0,
            "artifact_read_ms": 2,
            "serialize_ms": 0,
            "total_ms": 20,
        },
    }

    trace_path = append_ai_trace(tmp_path, event)
    payload = json.loads(trace_path.read_text(encoding="utf-8").splitlines()[-1])

    assert payload["endpoint"] == "/api/summary_ui"
    assert payload["payload_profile"] == "medium"
    assert payload["outcome"] == "reused_artifact"
    assert payload["stage_timings_ms"]["total_ms"] == 20
