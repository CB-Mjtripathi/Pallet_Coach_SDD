from __future__ import annotations

import base64
import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from pallet_coach.api.run_store import allocate_run_id, create_run_dir, write_bundle
from pallet_coach.artifacts import write_image_prompts
from pallet_coach.api.app import app


app_module = importlib.import_module("pallet_coach.api.app")

client = TestClient(app)


def _solve_request() -> dict:
    return {
        "request": {
            "pallet": {"type": "euro", "length_mm": 1200, "width_mm": 800},
            "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150},
            "stack": {"layer_count": 8},
            "tolerances": {
                "max_overhang_l_mm": 0,
                "max_overhang_w_mm": 0,
                "max_underhang_l_mm": 20,
                "max_underhang_w_mm": 20,
            },
            "constraints": {
                "allow_rotation_90": True,
                "allow_interlock": False,
                "auto_underhang": False,
            },
        },
        "max_solutions": 25,
        "include_timestamp": True,
    }


def _create_run() -> tuple[str, Path]:
    run_id = allocate_run_id()
    run_dir = create_run_dir(run_id)

    bundle = {
        "run_id": run_id,
        "request": _solve_request()["request"],
        "recommender": {
            "status": "ok",
            "reasons": [],
            "solutions": [],
        },
        "stacking": {},
        "artifacts": {},
        "ai_assist": {
            "summary_generated": False,
            "summary_ui_generated": False,
            "diagram_flat_generated": False,
            "diagram_3d_generated": False,
        },
    }

    write_bundle(run_dir, bundle)
    write_image_prompts(run_dir, bundle)
    return run_id, run_dir


def _read_trace_events(run_dir: Path) -> list[dict]:
    trace_path = run_dir / "ai_traces" / "ai_calls.jsonl"
    if not trace_path.exists():
        return []
    return [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_summary_endpoint_writes_artifact_and_updates_bundle(monkeypatch):
    run_id, run_dir = _create_run()

    def _fake_summary(bundle: dict, style: str = "detailed", endpoint_budget_ms: int | None = None):
        assert bundle["run_id"] == run_id
        assert endpoint_budget_ms is not None
        return "# AI Summary\n\nHello", {"provider": "azure_openai", "model": "fake", "timings_ms": {"provider_ms": 10}}

    monkeypatch.setattr(app_module, "generate_summary_markdown", _fake_summary)

    response = client.post("/api/summary", json={"run_id": run_id, "style": "detailed"})
    assert response.status_code == 200

    summary_path = run_dir / "recommendation_summary.md"
    assert summary_path.exists()
    assert "AI Summary" in summary_path.read_text(encoding="utf-8")

    bundle = client.get(f"/api/runs/{run_id}").json()
    assert bundle["artifacts"]["recommendation_summary"]["path"] == "recommendation_summary.md"
    assert bundle["ai_assist"]["summary_generated"] is True

    events = _read_trace_events(run_dir)
    assert events
    summary_event = events[-1]
    assert summary_event["operation"] == "summary"
    assert summary_event["outcome"] == "generation"
    assert "stage_timings_ms" in summary_event
    assert "payload_profile" in summary_event


def test_summary_ui_endpoint_supports_force(monkeypatch):
    run_id, run_dir = _create_run()
    bundle_data = app_module._load_bundle_or_404(run_dir)

    existing = run_dir / "summary_ui.md"
    existing.write_text("cached", encoding="utf-8")
    (run_dir / "recommendation_summary.md").write_text("source", encoding="utf-8")

    source_summary_hash = app_module._sha256_text("source")
    minimized_hash = app_module._sha256_text(
        json.dumps(app_module.build_minimized_bundle(bundle_data), sort_keys=True, ensure_ascii=False)
    )
    fingerprint = app_module._sha256_text(
        json.dumps(
            {
                "run_id": run_id,
                "mode": "summary_ui",
                "style": "detailed",
                "source_summary_hash": source_summary_hash,
                "minimized_hash": minimized_hash,
            },
            sort_keys=True,
        )
    )
    near_fields_hash = app_module._sha256_text(
        json.dumps(
            {
                "run_id": run_id,
                "mode": "summary_ui",
                "style": "detailed",
                "source_summary_hash": source_summary_hash,
            },
            sort_keys=True,
        )
    )

    (run_dir / "summary_ui.meta.json").write_text(
        json.dumps(
            {
                "created_at": app_module._iso_now(),
                "fingerprint": fingerprint,
                "near_fields_hash": near_fields_hash,
                "style": "detailed",
                "mode": "summary_ui",
                "source_summary_hash": source_summary_hash,
            }
        ),
        encoding="utf-8",
    )

    calls = {"count": 0}

    def _fake_summary_ui(
        summary_markdown: str,
        bundle: dict,
        style: str = "detailed",
        endpoint_budget_ms: int | None = None,
    ):
        calls["count"] += 1
        assert endpoint_budget_ms is not None
        return "fresh ui summary", {"provider": "azure_openai", "model": "fake", "timings_ms": {"provider_ms": 10}}

    monkeypatch.setattr(app_module, "generate_summary_ui_markdown", _fake_summary_ui)

    first = client.post("/api/summary_ui", json={"run_id": run_id, "style": "detailed", "force": False})
    assert first.status_code == 200
    assert first.json()["summary_markdown"] == "cached"
    assert calls["count"] == 0

    second = client.post("/api/summary_ui", json={"run_id": run_id, "style": "detailed", "force": True})
    assert second.status_code == 200
    assert second.json()["summary_markdown"] == "fresh ui summary"
    assert calls["count"] == 1

    bundle = client.get(f"/api/runs/{run_id}").json()
    assert bundle["artifacts"]["summary_ui"]["path"] == "summary_ui.md"
    assert bundle["ai_assist"]["summary_ui_generated"] is True


def test_diagram_endpoint_writes_flat_and_3d_artifacts(monkeypatch):
    run_id, run_dir = _create_run()

    png_bytes = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=")

    def _fake_diagram(prompt_text: str, view: str):
        assert prompt_text
        return png_bytes, {"provider": "google_ai_studio", "model": "fake"}

    monkeypatch.setattr(app_module, "generate_diagram_image", _fake_diagram)

    flat = client.post("/api/diagram", json={"run_id": run_id, "view": "flat"})
    three_d = client.post("/api/diagram", json={"run_id": run_id, "view": "3d"})

    assert flat.status_code == 200
    assert three_d.status_code == 200

    assert (run_dir / "diagram_flat.png").exists()
    assert (run_dir / "diagram_3d.png").exists()

    bundle = client.get(f"/api/runs/{run_id}").json()
    assert bundle["artifacts"]["diagram_flat"]["path"] == "diagram_flat.png"
    assert bundle["artifacts"]["diagram_3d"]["path"] == "diagram_3d.png"
    assert bundle["ai_assist"]["diagram_flat_generated"] is True
    assert bundle["ai_assist"]["diagram_3d_generated"] is True


def test_summary_endpoint_returns_502_when_provider_fails(monkeypatch):
    run_id, _ = _create_run()

    def _boom(bundle: dict, style: str = "detailed", endpoint_budget_ms: int | None = None):
        raise RuntimeError("provider down")

    monkeypatch.setattr(app_module, "generate_summary_markdown", _boom)

    response = client.post("/api/summary", json={"run_id": run_id, "style": "detailed"})
    assert response.status_code == 502


def test_summary_ui_endpoint_fallback_timeout_outcome(monkeypatch):
    run_id, run_dir = _create_run()
    (run_dir / "recommendation_summary.md").write_text("source", encoding="utf-8")

    def _boom(*args, **kwargs):
        raise TimeoutError("provider timeout")

    monkeypatch.setattr(app_module, "generate_summary_ui_markdown", _boom)

    response = client.post("/api/summary_ui", json={"run_id": run_id, "style": "detailed", "force": True})
    assert response.status_code == 200
    assert "AI rewrite unavailable" in response.json()["summary_markdown"]

    events = _read_trace_events(run_dir)
    assert events
    event = events[-1]
    assert event["operation"] == "summary_ui"
    assert event["outcome"] == "fallback_timeout"
    assert event["reason_code"] == "provider_timeout"
    assert "stage_timings_ms" in event
