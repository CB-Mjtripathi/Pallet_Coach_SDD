from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from pallet_coach.api.app import app
from pallet_coach.artifacts import write_recommendation_summary


client = TestClient(app)


MANDATORY_FILES = [
    "bundle.json",
    "run_log.txt",
    "recommendation_summary.md",
    "stability_report_3d.md",
    "stability_report_3d.json",
    "overhang_underhang_table.md",
    "layer_diagram.png",
    "comparison_flat.png",
    "comparison_3d.png",
    "onpallet_3d.png",
    "isometric_exploded_3d.png",
    "image_prompt_flat.md",
    "image_prompt_3d.md",
]


def _valid_request() -> dict:
    return {
        "request": {
            "pallet": {"type": "euro", "length_mm": 1200, "width_mm": 800},
            "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150},
            "stack": {"layer_count": 8},
            "baseline_cases_per_layer": 9,
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


def test_solve_writes_mandatory_rf003_artifacts_and_pointers():
    response = client.post("/api/solve", json=_valid_request())
    assert response.status_code == 200

    body = response.json()
    run_dir = Path(body["out_dir"])

    for name in MANDATORY_FILES:
        assert (run_dir / name).exists(), f"Expected artifact missing: {name}"

    bundle_response = client.get(f"/api/runs/{body['run_id']}")
    assert bundle_response.status_code == 200
    bundle = bundle_response.json()

    for key in [
        "run_log",
        "recommendation_summary",
        "layer_diagram",
        "comparison_flat",
        "comparison_3d",
        "onpallet_3d",
        "isometric_exploded_3d",
        "stability_report_3d",
        "stability_report_3d_md",
        "overhang_underhang_table",
        "image_prompt_flat",
        "image_prompt_3d",
    ]:
        artifact_path = bundle["artifacts"][key]["path"]
        assert (run_dir / artifact_path).exists(), f"Bundle pointer missing target file for key={key}"


def test_run_log_contains_artifact_generation_events():
    response = client.post("/api/solve", json=_valid_request())
    assert response.status_code == 200
    run_id = response.json()["run_id"]

    logs = client.get(f"/api/runs/{run_id}/logs")
    assert logs.status_code == 200
    assert "Generating deterministic artifacts" in logs.text
    assert "Deterministic artifacts generated" in logs.text


def test_recommendation_summary_handles_none_runner_metrics(tmp_path: Path):
    bundle = {
        "run_id": "RTEST_20260421",
        "recommender": {
            "status": "ok",
            "solutions": [
                {
                    "solution_id": "mixed_irregular_opt",
                    "metrics": {
                        "cases_per_layer": 6,
                        "total_cases": 48,
                        "area_fill_efficiency_pct": 71.75,
                        "total_height_mm": 1424,
                    },
                },
                {
                    "solution_id": "grid_rot90",
                    "metrics": {
                        "cases_per_layer": None,
                        "area_fill_efficiency_pct": None,
                    },
                },
            ],
            "reasons": [],
        },
        "stacking": {"warnings": []},
    }

    path = write_recommendation_summary(tmp_path, bundle)

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "Comparison with Runner-Up" in text
    assert "Efficiency improvement" in text
