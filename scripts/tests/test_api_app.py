from __future__ import annotations

from fastapi.testclient import TestClient

from pallet_coach.api.app import app


client = TestClient(app)


def _valid_request() -> dict:
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


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_solve_contract_returns_422():
    payload = _valid_request()
    del payload["request"]["pallet"]
    response = client.post("/api/solve", json=payload)
    assert response.status_code == 422


def test_valid_solve_creates_run_and_bundle_and_output_accessible():
    response = client.post("/api/solve", json=_valid_request())
    assert response.status_code == 200

    body = response.json()
    run_id = body["run_id"]
    assert body["solver_status"] in {"ok", "impossible"}

    bundle_response = client.get(f"/api/runs/{run_id}")
    assert bundle_response.status_code == 200
    assert bundle_response.json()["run_id"] == run_id

    logs_response = client.get(f"/api/runs/{run_id}/logs")
    assert logs_response.status_code == 200
    assert "Solve" in logs_response.text

    output_response = client.get(f"/output/{run_id}/bundle.json")
    assert output_response.status_code == 200


def test_missing_run_returns_404():
    response = client.get("/api/runs/R9999_20990101")
    assert response.status_code == 404


def test_output_route_blocks_path_traversal():
    response = client.post("/api/solve", json=_valid_request())
    assert response.status_code == 200
    run_id = response.json()["run_id"]

    # Use encoded traversal so the route still matches and input validation can reject it.
    attack = client.get(f"/output/{run_id}/..%2Fbundle.json")
    assert attack.status_code == 404
