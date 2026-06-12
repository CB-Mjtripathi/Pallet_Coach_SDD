from __future__ import annotations

from math import isfinite
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

PALETTE = {
    "pallet_fill": "#FFFFFF",
    "pallet_border": "#333333",
    "case_fill": "#90CAF9",
    "case_border": "#1A1A1A",
    "case_top": "#1E88E5",
    "interlock_a": "#1E88E5",
    "interlock_b": "#1565C0",
    "tolerance_ok": "#4CAF50",
    "tolerance_warn": "#FFC107",
    "tolerance_fail": "#F44336",
    "underhang_zone": "#90CAF9",
    "overhang_zone": "#FFCC80",
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "background": "#FFFFFF",
    "grid_line": "#CCCCCC",
    "dimension_line": "#333333",
}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _layer_base_z(layer_index: int, case_height_mm: int, exploded_gap_mm: int = 0, pallet_height_mm: int = 10) -> float:
    return float(pallet_height_mm + layer_index * (case_height_mm + exploded_gap_mm))


def _extract_dims(request: dict[str, Any]) -> tuple[int, int, int, int]:
    pallet = request.get("pallet", {})
    case = request.get("case", {})
    return (
        _safe_int(pallet.get("length_mm"), 1200),
        _safe_int(pallet.get("width_mm"), 800),
        _safe_int(case.get("length_mm"), 300),
        _safe_int(case.get("width_mm"), 200),
    )


def _edge_status(clearance_mm: float, max_underhang_mm: float, max_overhang_mm: float) -> str:
    if clearance_mm < 0:
        overhang = abs(clearance_mm)
        if overhang > max_overhang_mm:
            return "fail"
        if overhang >= 0.8 * max_overhang_mm and max_overhang_mm > 0:
            return "warn"
        return "ok"

    if clearance_mm > max_underhang_mm:
        return "fail"
    if clearance_mm >= 0.8 * max_underhang_mm and max_underhang_mm > 0:
        return "warn"
    return "ok"


def _status_color(status: str) -> str:
    if status == "fail":
        return PALETTE["tolerance_fail"]
    if status == "warn":
        return PALETTE["tolerance_warn"]
    return PALETTE["tolerance_ok"]


def _draw_dimension_text(ax: Any, x_segments: list[float], y_segments: list[float], pallet_l: int, pallet_w: int) -> None:
    x_text = "x segments (mm): " + ", ".join(str(int(v)) for v in x_segments) if x_segments else "x segments (mm): n/a"
    y_text = "y segments (mm): " + ", ".join(str(int(v)) for v in y_segments) if y_segments else "y segments (mm): n/a"

    ax.text(0, -0.12 * pallet_w, x_text, fontsize=8, color=PALETTE["text_secondary"])
    ax.text(0, -0.18 * pallet_w, y_text, fontsize=8, color=PALETTE["text_secondary"])


def _draw_topdown(ax: Any, layout: list[dict[str, Any]], request: dict[str, Any], metrics: dict[str, Any] | None, title: str) -> None:
    pallet_l, pallet_w, case_l, case_w = _extract_dims(request)

    ax.set_facecolor(PALETTE["background"])
    ax.add_patch(
        Rectangle(
            (0, 0),
            pallet_l,
            pallet_w,
            facecolor=PALETTE["pallet_fill"],
            edgecolor=PALETTE["pallet_border"],
            linewidth=1.4,
        )
    )

    tolerances = request.get("tolerances", {})
    edge = (metrics or {}).get("edge_clearance_mm", {})
    left = float(edge.get("left_mm", 0.0))
    right = float(edge.get("right_mm", 0.0))
    bottom = float(edge.get("bottom_mm", 0.0))
    top = float(edge.get("top_mm", 0.0))

    status_left = _edge_status(left, float(tolerances.get("max_underhang_l_mm", 0)), float(tolerances.get("max_overhang_l_mm", 0)))
    status_right = _edge_status(right, float(tolerances.get("max_underhang_l_mm", 0)), float(tolerances.get("max_overhang_l_mm", 0)))
    status_bottom = _edge_status(bottom, float(tolerances.get("max_underhang_w_mm", 0)), float(tolerances.get("max_overhang_w_mm", 0)))
    status_top = _edge_status(top, float(tolerances.get("max_underhang_w_mm", 0)), float(tolerances.get("max_overhang_w_mm", 0)))

    band_x = max(case_l, case_w) * 0.12
    band_y = max(case_l, case_w) * 0.12

    ax.add_patch(Rectangle((-band_x, 0), band_x, pallet_w, facecolor=_status_color(status_left), alpha=0.2, edgecolor="none"))
    ax.add_patch(Rectangle((pallet_l, 0), band_x, pallet_w, facecolor=_status_color(status_right), alpha=0.2, edgecolor="none"))
    ax.add_patch(Rectangle((0, -band_y), pallet_l, band_y, facecolor=_status_color(status_bottom), alpha=0.2, edgecolor="none"))
    ax.add_patch(Rectangle((0, pallet_w), pallet_l, band_y, facecolor=_status_color(status_top), alpha=0.2, edgecolor="none"))

    for idx, item in enumerate(layout, start=1):
        x = float(item.get("x_mm", 0.0))
        y = float(item.get("y_mm", 0.0))
        dx = float(item.get("dim_x_mm", case_l))
        dy = float(item.get("dim_y_mm", case_w))
        rot = _safe_int(item.get("rotation_deg"), 0)

        ax.add_patch(
            Rectangle(
                (x, y),
                dx,
                dy,
                facecolor=PALETTE["case_fill"],
                edgecolor=PALETTE["case_border"],
                linewidth=1.0,
            )
        )
        ax.text(
            x + dx / 2.0,
            y + dy / 2.0,
            f"{idx} ({rot}deg)",
            ha="center",
            va="center",
            fontsize=7,
            color=PALETTE["text_primary"],
        )

    segments = (metrics or {}).get("inner_axis_segments_mm", {})
    x_segments = [float(v) for v in segments.get("x_segments_mm", []) if isfinite(float(v))]
    y_segments = [float(v) for v in segments.get("y_segments_mm", []) if isfinite(float(v))]

    _draw_dimension_text(ax, x_segments, y_segments, pallet_l, pallet_w)

    ax.set_xlim(-0.2 * max(case_l, case_w), pallet_l + 0.2 * max(case_l, case_w))
    ax.set_ylim(-0.24 * max(case_l, case_w), pallet_w + 0.2 * max(case_l, case_w))
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", linewidth=0.5, color=PALETTE["grid_line"], alpha=0.5)
    ax.set_title(title, fontsize=11, color=PALETTE["text_primary"])
    ax.set_xlabel("Length (mm)")
    ax.set_ylabel("Width (mm)")


def infer_baseline_grid(baseline_cases_per_layer: int, case_length_mm: int, case_width_mm: int) -> tuple[int, int]:
    n = max(1, int(baseline_cases_per_layer))
    c_l = max(1.0, float(case_length_mm))
    c_w = max(1.0, float(case_width_mm))

    candidates: list[tuple[float, int, int, float]] = []
    for nx in range(1, n + 1):
        if n % nx != 0:
            continue
        ny = n // nx
        balance_penalty = abs(nx - ny) / max(nx, ny)
        area_score = n * c_l * c_w
        # Primary score combines implied area usage (constant for a given n) and grid balance.
        # Tie-break uses axis preference from case aspect ratio to keep orientation deterministic.
        aspect_pref = (nx / ny) * (c_l / c_w)
        score = (1.0 - balance_penalty) + area_score * 0.0
        candidates.append((score, nx, ny, aspect_pref))

    if not candidates:
        return (n, 1)

    candidates.sort(key=lambda row: (row[0], row[3], row[1]), reverse=True)
    _, nx_best, ny_best, _ = candidates[0]
    return (nx_best, ny_best)


def _baseline_layout(request: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pallet_l, pallet_w, case_l, case_w = _extract_dims(request)
    baseline_count = _safe_int(request.get("baseline_cases_per_layer"), 0)
    if baseline_count <= 0:
        baseline_count = 1

    nx, ny = infer_baseline_grid(baseline_count, case_l, case_w)
    layout: list[dict[str, Any]] = []
    for row in range(ny):
        for col in range(nx):
            layout.append(
                {
                    "x_mm": col * case_l,
                    "y_mm": row * case_w,
                    "rotation_deg": 0,
                    "dim_x_mm": case_l,
                    "dim_y_mm": case_w,
                }
            )

    metrics = {
        "inner_axis_segments_mm": {
            "x_segments_mm": [case_l] * nx,
            "y_segments_mm": [case_w] * ny,
        },
        "edge_clearance_mm": {
            "left_mm": 0,
            "right_mm": pallet_l - nx * case_l,
            "bottom_mm": 0,
            "top_mm": pallet_w - ny * case_w,
        },
    }
    return layout, metrics


def _save(fig: Any, out_path: Path, dpi: int = 150, tight: bool = True) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if tight:
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=PALETTE["background"])
    else:
        fig.savefig(out_path, dpi=dpi, facecolor=PALETTE["background"])
    plt.close(fig)
    return out_path


def render_layer_png(run_dir: Path, solution: dict[str, Any] | None, request: dict[str, Any], out_name: str = "layer_diagram.png") -> Path:
    fig, ax = plt.subplots(figsize=(10, 7))
    layout = (solution or {}).get("layout", [])
    metrics = (solution or {}).get("metrics", {})
    title = "Layer Diagram"
    if not layout:
        title = "Layer Diagram (No feasible layout)"
    _draw_topdown(ax, layout, request, metrics, title)
    return _save(fig, run_dir / out_name)


def render_comparison_flat_png(
    run_dir: Path,
    best_solution: dict[str, Any] | None,
    request: dict[str, Any],
    baseline_cases_per_layer: int | None = None,
    out_name: str = "comparison_flat.png",
) -> Path:
    if baseline_cases_per_layer is not None:
        request = {**request, "baseline_cases_per_layer": baseline_cases_per_layer}

    before_layout, before_metrics = _baseline_layout(request)
    after_layout = (best_solution or {}).get("layout", [])
    after_metrics = (best_solution or {}).get("metrics", {})

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    _draw_topdown(axes[0], before_layout, request, before_metrics, "BEFORE (Inferred Baseline)")
    _draw_topdown(axes[1], after_layout, request, after_metrics, "AFTER (Best Solution)")

    return _save(fig, run_dir / out_name)


def _draw_3d_layout(
    ax: Any,
    layout: list[dict[str, Any]],
    request: dict[str, Any],
    layer_count: int,
    title: str,
    exploded_gap_mm: int = 0,
    isometric_mode: bool = False,
) -> None:
    pallet_l, pallet_w, _, _ = _extract_dims(request)
    case_h = _safe_int(request.get("case", {}).get("height_mm"), 150)
    # Add a small visual inset so adjacent cuboids do not z-fight in 3D raster output.
    render_inset_mm = 0.8

    ax.bar3d(0, 0, 0, pallet_l, pallet_w, 10, color=PALETTE["pallet_fill"], edgecolor=PALETTE["pallet_border"], alpha=0.95)

    colors = [PALETTE["interlock_a"], PALETTE["interlock_b"]]
    for layer in range(max(1, layer_count)):
        for item in layout:
            x = float(item.get("x_mm", 0.0))
            y = float(item.get("y_mm", 0.0))
            dx = float(item.get("dim_x_mm", 1.0))
            dy = float(item.get("dim_y_mm", 1.0))
            z = _layer_base_z(layer, case_h, exploded_gap_mm=exploded_gap_mm)
            x_draw = x + render_inset_mm / 2.0
            y_draw = y + render_inset_mm / 2.0
            dx_draw = max(0.2, dx - render_inset_mm)
            dy_draw = max(0.2, dy - render_inset_mm)
            ax.bar3d(
                x_draw,
                y_draw,
                z,
                dx_draw,
                dy_draw,
                case_h,
                color=colors[layer % 2],
                edgecolor=PALETTE["case_border"],
                shade=True,
                alpha=0.95,
            )

    ax.set_title(title, fontsize=11, color=PALETTE["text_primary"])
    ax.set_xlabel("Length (mm)")
    ax.set_ylabel("Width (mm)")
    ax.set_zlabel("Height (mm)")
    ax.set_xlim(0, pallet_l)
    ax.set_ylim(0, pallet_w)
    max_z = _layer_base_z(max(0, layer_count - 1), case_h, exploded_gap_mm=exploded_gap_mm) + case_h + 10
    ax.set_zlim(0, max_z)
    if isometric_mode:
        ax.view_init(elev=30, azim=-45)


def render_comparison_3d_png(
    run_dir: Path,
    best_solution: dict[str, Any] | None,
    request: dict[str, Any],
    baseline_cases_per_layer: int | None = None,
    out_name: str = "comparison_3d.png",
) -> Path:
    if baseline_cases_per_layer is not None:
        request = {**request, "baseline_cases_per_layer": baseline_cases_per_layer}

    before_layout, _ = _baseline_layout(request)
    after_layout = (best_solution or {}).get("layout", [])
    layers = _safe_int(request.get("stack", {}).get("layer_count"), 1)

    fig = plt.figure(figsize=(15, 7))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    _draw_3d_layout(ax1, before_layout, request, layers, "BEFORE (Inferred Baseline)")
    _draw_3d_layout(ax2, after_layout, request, layers, "AFTER (Best Solution)")

    return _save(fig, run_dir / out_name)


def render_onpallet_3d_png(
    run_dir: Path,
    best_solution: dict[str, Any] | None,
    request: dict[str, Any],
    out_name: str = "onpallet_3d.png",
) -> Path:
    layout = (best_solution or {}).get("layout", [])
    layers = _safe_int(request.get("stack", {}).get("layer_count"), 1)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    _draw_3d_layout(ax, layout, request, layers, "On-Pallet 3D View")
    ax.view_init(elev=22, azim=-58)

    return _save(fig, run_dir / out_name)


def render_isometric_exploded_3d_png(
    run_dir: Path,
    best_solution: dict[str, Any] | None,
    request: dict[str, Any],
    out_name: str = "isometric_exploded_3d.png",
    exploded_gap_mm: int = 40,
) -> Path:
    layout = (best_solution or {}).get("layout", [])
    layers = _safe_int(request.get("stack", {}).get("layer_count"), 1)

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    _draw_3d_layout(
        ax,
        layout,
        request,
        layers,
        "Isometric Exploded Layer View",
        exploded_gap_mm=exploded_gap_mm,
        isometric_mode=True,
    )

    # Preserve full canvas size for high-resolution contract checks.
    return _save(fig, run_dir / out_name, dpi=160, tight=False)
