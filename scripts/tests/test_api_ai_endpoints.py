from __future__ import annotations

import base64
import importlib
from pathlib import Path

from fastapi.testclient import TestClient

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
    response = client.post("/api/solve", json=_solve_request())
    assert response.status_code == 200
    body = response.json()
    return body["run_id"], Path(body["out_dir"])


def test_summary_endpoint_writes_artifact_and_updates_bundle(monkeypatch):
    run_id, run_dir = _create_run()

    def _fake_summary(bundle: dict, style: str = "detailed"):
        assert bundle["run_id"] == run_id
        return "# AI Summary\n\nHello", {"provider": "azure_openai", "model": "fake"}

    monkeypatch.setattr(app_module, "generate_summary_markdown", _fake_summary)

    response = client.post("/api/summary", json={"run_id": run_id, "style": "detailed"})
    assert response.status_code == 200

    summary_path = run_dir / "recommendation_summary.md"
    assert summary_path.exists()
    assert "AI Summary" in summary_path.read_text(encoding="utf-8")

    bundle = client.get(f"/api/runs/{run_id}").json()
    assert bundle["artifacts"]["recommendation_summary"]["path"] == "recommendation_summary.md"
    assert bundle["ai_assist"]["summary_generated"] is True


def test_summary_ui_endpoint_supports_force(monkeypatch):
    run_id, run_dir = _create_run()

    existing = run_dir / "summary_ui.md"
    existing.write_text("cached", encoding="utf-8")

    calls = {"count": 0}

    def _fake_summary_ui(summary_markdown: str, bundle: dict, style: str = "detailed"):
        calls["count"] += 1
        return "fresh ui summary", {"provider": "azure_openai", "model": "fake"}

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

    def _boom(bundle: dict, style: str = "detailed"):
        raise RuntimeError("provider down")

    monkeypatch.setattr(app_module, "generate_summary_markdown", _boom)

    response = client.post("/api/summary", json={"run_id": run_id, "style": "detailed"})
    assert response.status_code == 502
