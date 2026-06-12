from __future__ import annotations

from pathlib import Path

from PIL import Image

from pallet_coach.diagram import (
    _layer_base_z,
    infer_baseline_grid,
    render_comparison_3d_png,
    render_comparison_flat_png,
    render_isometric_exploded_3d_png,
    render_layer_png,
    render_onpallet_3d_png,
)


def _request() -> dict:
    return {
        "pallet": {"type": "euro", "length_mm": 1200, "width_mm": 800},
        "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150},
        "stack": {"layer_count": 8},
        "baseline_cases_per_layer": 12,
        "tolerances": {
            "max_overhang_l_mm": 0,
            "max_overhang_w_mm": 0,
            "max_underhang_l_mm": 20,
            "max_underhang_w_mm": 20,
        },
    }


def _solution() -> dict:
    return {
        "solution_id": "grid_4x3_rot0",
        "layout": [
            {"x_mm": 0, "y_mm": 0, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 300, "y_mm": 0, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 600, "y_mm": 0, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 900, "y_mm": 0, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 0, "y_mm": 200, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 300, "y_mm": 200, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 600, "y_mm": 200, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 900, "y_mm": 200, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 0, "y_mm": 400, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 300, "y_mm": 400, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 600, "y_mm": 400, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
            {"x_mm": 900, "y_mm": 400, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200},
        ],
        "metrics": {
            "inner_axis_segments_mm": {
                "x_segments_mm": [300, 300, 300, 300],
                "y_segments_mm": [200, 200, 200],
            },
            "edge_clearance_mm": {"left_mm": 0, "right_mm": 0, "bottom_mm": 100, "top_mm": 100},
        },
    }


def _assert_png(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 0
    with Image.open(path) as img:
        assert img.format == "PNG"
        dpi = img.info.get("dpi", (0, 0))
        assert dpi[0] >= 149
        assert dpi[1] >= 149


def test_renderers_emit_nonempty_png_with_print_dpi(tmp_path):
    req = _request()
    sol = _solution()

    layer = render_layer_png(tmp_path, sol, req)
    flat = render_comparison_flat_png(tmp_path, sol, req)
    cmp_3d = render_comparison_3d_png(tmp_path, sol, req)
    onpallet = render_onpallet_3d_png(tmp_path, sol, req)
    iso = render_isometric_exploded_3d_png(tmp_path, sol, req)

    _assert_png(layer)
    _assert_png(flat)
    _assert_png(cmp_3d)
    _assert_png(onpallet)
    _assert_png(iso)


def test_render_isometric_exploded_has_high_resolution_profile(tmp_path):
    req = _request()
    sol = _solution()

    path = render_isometric_exploded_3d_png(tmp_path, sol, req)
    with Image.open(path) as img:
        width, height = img.size
        assert width >= 1920
        assert height >= 1080


def test_layer_base_z_respects_exploded_gap_mm():
    case_h = 150
    no_gap_step = _layer_base_z(1, case_h, exploded_gap_mm=0) - _layer_base_z(0, case_h, exploded_gap_mm=0)
    gap_step = _layer_base_z(1, case_h, exploded_gap_mm=40) - _layer_base_z(0, case_h, exploded_gap_mm=40)

    assert no_gap_step == 150
    assert gap_step == 190


def test_infer_baseline_grid_prefers_balanced_factor_pair():
    nx, ny = infer_baseline_grid(12, 300, 200)
    assert nx * ny == 12
    assert (nx, ny) == (4, 3)
