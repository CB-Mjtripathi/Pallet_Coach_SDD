from __future__ import annotations

import json
from math import pi, sin
from pathlib import Path
from typing import Any

from .models import Placement
from .overhang_underhang import calculate_case_hang_metrics, compute_layout_underhang_ratio


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt_number(value: Any, decimals: int = 1) -> str:
    if value is None:
        return "n/a"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{num:.{decimals}f}"


def write_recommendation_summary(run_dir: Path, bundle: dict[str, Any]) -> Path:
    recommender = bundle.get("recommender", {})
    solutions = recommender.get("solutions", [])
    top = solutions[0] if solutions else None
    top_metrics = (top or {}).get("metrics", {})
    top_solution_id = (top or {}).get("solution_id", "unknown")

    lines = [
        "# Pallet Coach Recommendation Summary",
        "",
        f"Run ID: {bundle.get('run_id', 'unknown')}",
        f"Status: {recommender.get('status', 'unknown')}",
        "",
        "## Top Solution",
        f"- Pattern: {top_solution_id}",
        f"- Cases per layer: {top_metrics.get('cases_per_layer', 'n/a')}",
        f"- Total cases: {top_metrics.get('total_cases', 'n/a')}",
        f"- Area fill efficiency (%): {top_metrics.get('area_fill_efficiency_pct', 'n/a')}",
        f"- Total height (mm): {top_metrics.get('total_height_mm', 'n/a')}",
        "",
    ]

    if len(solutions) > 1:
        runner_up = solutions[1]
        runner_metrics = (runner_up or {}).get("metrics", {})
        runner_id = (runner_up or {}).get("solution_id", "unknown")
        cases_diff = _safe_float(top_metrics.get("cases_per_layer")) - _safe_float(
            runner_metrics.get("cases_per_layer")
        )
        eff_diff = _safe_float(top_metrics.get("area_fill_efficiency_pct")) - _safe_float(
            runner_metrics.get("area_fill_efficiency_pct")
        )
        lines.extend([
            "## Comparison with Runner-Up",
            f"- Runner-up pattern: {runner_id}",
            f"- Cases/layer improvement: +{_fmt_number(cases_diff, 0)}",
            f"- Efficiency improvement: +{_fmt_number(eff_diff, 1)}%",
            "",
        ])

    reasons = recommender.get("reasons", [])
    if reasons:
        lines.append("## Reasons")
        for reason in reasons:
            lines.append(f"- {reason.get('code', 'UNKNOWN')}: {reason.get('message', '')}")
        lines.append("")

    stacking = bundle.get("stacking", {})
    lines.extend(
        [
            "## Stacking",
            f"- Current layers: {stacking.get('current_layers', 'n/a')}",
            f"- Effective ceiling layers: {stacking.get('effective_ceiling_layers', 'n/a')}",
            f"- Addable layers to max height: {stacking.get('addable_layers_to_max_height', 'n/a')}",
            "",
            "## Warnings",
        ]
    )

    warnings = stacking.get("warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    content = "\n".join(lines) + "\n"
    path = run_dir / "recommendation_summary.md"
    path.write_text(content, encoding="utf-8")
    return path


def write_image_prompts(run_dir: Path, bundle: dict[str, Any]) -> tuple[Path, Path]:
    run_id = bundle.get("run_id", "unknown")
    status = bundle.get("recommender", {}).get("status", "unknown")
    request = bundle.get("request", {})

    flat_prompt = "\n".join(
        [
            "# Flat Diagram Prompt",
            "",
            f"Run ID: {run_id}",
            f"Status: {status}",
            "Task: Render a side-by-side BEFORE vs AFTER flat palletization diagram.",
            "Input request payload:",
            f"{request}",
            "",
            "Notes:",
            "- BEFORE uses inferred baseline grid when baseline_cases_per_layer exists.",
            "- AFTER uses best deterministic solver layout.",
        ]
    ) + "\n"

    prompt_3d = "\n".join(
        [
            "# 3D Diagram Prompt",
            "",
            f"Run ID: {run_id}",
            f"Status: {status}",
            "Task: Render isometric pallet stack diagrams for before/after comparison.",
            "Input request payload:",
            f"{request}",
            "",
            "Notes:",
            "- Use layer count and case dimensions from request.",
            "- Preserve deterministic solver geometry and metric context.",
        ]
    ) + "\n"

    flat_path = run_dir / "image_prompt_flat.md"
    p3d_path = run_dir / "image_prompt_3d.md"
    flat_path.write_text(flat_prompt, encoding="utf-8")
    p3d_path.write_text(prompt_3d, encoding="utf-8")
    return flat_path, p3d_path


def write_printable_loading_sheet(run_dir: Path, bundle: dict[str, Any]) -> Path:
    """Generate a clean printable loading sheet for floor operators using the best solution."""
    recommender = bundle.get("recommender", {})
    solutions = recommender.get("solutions", [])
    top = solutions[0] if solutions else None
    
    if not top:
        return run_dir / "loading_sheet.md"
    
    layout = top.get("layout", [])
    metrics = top.get("metrics", {})
    request = bundle.get("request", {})
    pallet = request.get("pallet", {})
    case_info = request.get("case", {})
    stack = request.get("stack", {})
    
    lines = [
        "# Pallet Loading Sheet",
        "",
        "## Pallet Information",
        f"- Pallet type: {pallet.get('type', 'unknown')}",
        f"- Dimensions: {pallet.get('length_mm')} mm × {pallet.get('width_mm')} mm",
        "",
        "## Case Information",
        f"- Dimensions: {case_info.get('length_mm')} mm × {case_info.get('width_mm')} mm × {case_info.get('height_mm')} mm",
        f"- Weight: {case_info.get('weight_kg', 'n/a')} kg",
        "",
        "## Solution Plan",
        f"- Pattern: {top.get('solution_id', 'unknown')}",
        f"- Cases per layer: {metrics.get('cases_per_layer', 'n/a')}",
        f"- Layer count: {stack.get('layer_count', 'n/a')}",
        f"- Total cases: {metrics.get('total_cases', 'n/a')}",
        f"- Area fill efficiency: {metrics.get('area_fill_efficiency_pct', 'n/a')}%",
        f"- Total height: {metrics.get('total_height_mm', 'n/a')} mm",
        "",
        "## Layer Layout",
        "",
        "| Case ID | X (mm) | Y (mm) | Rotation | Footprint |",
        "|---------|--------|--------|----------|-----------|",
    ]
    
    for idx, placement in enumerate(layout, 1):
        x = placement.get("x_mm", 0)
        y = placement.get("y_mm", 0)
        rot = placement.get("rotation_deg", 0)
        dim_x = placement.get("dim_x_mm", 0)
        dim_y = placement.get("dim_y_mm", 0)
        rot_label = "R" if rot == 90 else "N"
        lines.append(f"| C{idx:02d} | {x:.0f} | {y:.0f} | {rot}° ({rot_label}) | {dim_x:.0f} × {dim_y:.0f} |")
    
    lines.extend([
        "",
        "## Key",
        "- N = Non-rotated (standard orientation)",
        "- R = Rotated 90 degrees",
        "- All dimensions in millimeters (mm)",
        "",
        "## Floor Operator Notes",
        "1. Place pallet on floor with origin (0,0) at bottom-left corner.",
        "2. Position cases according to the X and Y coordinates in the table above.",
        "3. Respect rotation requirements for each case.",
        "4. Ensure no cases extend beyond pallet boundaries.",
        "5. Repeat for each layer using the same placement pattern.",
        "",
    ])
    
    content = "\n".join(lines) + "\n"
    path = run_dir / "loading_sheet.md"
    path.write_text(content, encoding="utf-8")
    return path


def write_overhang_underhang_table(run_dir: Path, bundle: dict[str, Any]) -> Path:
    recommender = bundle.get("recommender", {})
    solutions = recommender.get("solutions", [])
    top = solutions[0] if solutions else None
    request = bundle.get("request", {})
    pallet = request.get("pallet", {})

    path = run_dir / "overhang_underhang_table.md"
    if not top:
        path.write_text("# Overhang and Underhang Table\n\nNo solution available.\n", encoding="utf-8")
        return path

    pallet_l = float(pallet.get("length_mm", 0.0))
    pallet_w = float(pallet.get("width_mm", 0.0))
    layout = top.get("layout", [])

    lines = [
        "# Overhang and Underhang Table",
        "",
        f"Run ID: {bundle.get('run_id', 'unknown')}",
        f"Solution: {top.get('solution_id', 'unknown')}",
        "",
        "| Case | Left | Right | Front | Back | OH Left | OH Right | OH Front | OH Back | Overhang Ratio % | Underhang Impact % | Valid |",
        "|------|------|-------|-------|------|---------|----------|----------|---------|------------------|--------------------|-------|",
    ]

    total_overhang_area = 0.0
    for idx, placement in enumerate(layout, 1):
        metrics = calculate_case_hang_metrics(
            pallet_length_mm=pallet_l,
            pallet_width_mm=pallet_w,
            case_length_mm=float(placement.get("dim_x_mm", 0.0)),
            case_width_mm=float(placement.get("dim_y_mm", 0.0)),
            position_x_mm=float(placement.get("x_mm", 0.0)),
            position_y_mm=float(placement.get("y_mm", 0.0)),
        )
        total_overhang_area += metrics.overhang_area_mm2
        is_valid = "yes" if metrics.is_inside_pallet else "no"
        lines.append(
            "| "
            f"C{idx:02d} | {metrics.left_mm:.1f} | {metrics.right_mm:.1f} | {metrics.front_mm:.1f} | {metrics.back_mm:.1f} | "
            f"{metrics.overhang_left_mm:.1f} | {metrics.overhang_right_mm:.1f} | {metrics.overhang_front_mm:.1f} | {metrics.overhang_back_mm:.1f} | "
            f"{metrics.overhang_ratio * 100.0:.2f} | {metrics.underhang_impact_ratio * 100.0:.2f} | {is_valid} |"
        )

    normalized_layout = [
        Placement(
            x_mm=float(p.get("x_mm", 0.0)),
            y_mm=float(p.get("y_mm", 0.0)),
            rotation_deg=int(p.get("rotation_deg", 0)),
            dim_x_mm=float(p.get("dim_x_mm", 0.0)),
            dim_y_mm=float(p.get("dim_y_mm", 0.0)),
        )
        for p in layout
    ]
    layout_underhang_ratio = compute_layout_underhang_ratio(pallet_l, pallet_w, normalized_layout)

    lines.extend(
        [
            "",
            "## Totals",
            f"- Total overhang area (mm2): {total_overhang_area:.2f}",
            f"- Layout underhang ratio (%): {layout_underhang_ratio * 100.0:.2f}",
            f"- Pallet utilization (%): {(1.0 - layout_underhang_ratio) * 100.0:.2f}",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _build_stack_boxes(solution: dict[str, Any], layer_count: int, case_height_mm: int) -> list[dict[str, float]]:
    layout = solution.get("layout", [])
    boxes: list[dict[str, float]] = []
    for layer in range(max(1, int(layer_count))):
        for item in layout:
            boxes.append(
                {
                    "x": float(item.get("x_mm", 0.0)),
                    "y": float(item.get("y_mm", 0.0)),
                    "dx": float(item.get("dim_x_mm", 0.0)),
                    "dy": float(item.get("dim_y_mm", 0.0)),
                    "z": float(layer * case_height_mm),
                }
            )
    return boxes


def _solution_stability(bundle: dict[str, Any], solution: dict[str, Any], friction_mu: float = 0.38) -> dict[str, Any]:
    request = bundle.get("request", {})
    pallet = request.get("pallet", {})
    case = request.get("case", {})
    stack = request.get("stack", {})

    pallet_l = float(pallet.get("length_mm", 1200))
    pallet_w = float(pallet.get("width_mm", 800))
    case_h = int(case.get("height_mm", 150))
    layer_count = int(stack.get("layer_count", 1))

    boxes = _build_stack_boxes(solution, layer_count, case_h)
    if not boxes:
        return {
            "solution_id": solution.get("solution_id", "unknown"),
            "stability_index": 0,
            "center_of_gravity": {"x_mm": 0.0, "y_mm": 0.0, "z_mm": 0.0},
            "profiles": {},
        }

    cx = sum(b["x"] + b["dx"] / 2.0 for b in boxes) / len(boxes)
    cy = sum(b["y"] + b["dy"] / 2.0 for b in boxes) / len(boxes)
    cz = sum(b["z"] + case_h / 2.0 for b in boxes) / len(boxes)

    center_shift = ((cx - pallet_l / 2.0) ** 2 + (cy - pallet_w / 2.0) ** 2) ** 0.5
    shift_norm = center_shift / max(1.0, min(pallet_l, pallet_w) * 0.5)
    stack_height = max(1.0, float(layer_count * case_h))
    height_norm = cz / stack_height

    profiles = {
        "idle": {"base_g": 0.05, "vibration_g": 0.05, "frequency_hz": 1.2},
        "city": {"base_g": 0.22, "vibration_g": 0.12, "frequency_hz": 2.1},
        "highway": {"base_g": 0.35, "vibration_g": 0.16, "frequency_hz": 2.9},
        "hard_brake": {"base_g": 0.62, "vibration_g": 0.24, "frequency_hz": 3.6},
    }

    report_profiles: dict[str, Any] = {}
    for name, cfg in profiles.items():
        max_slip_mm = 0.0
        overhang_events = 0
        collision_events = 0

        sim_steps = 72
        for step in range(sim_steps):
            t = step / 24.0
            accel_g = cfg["base_g"] + cfg["vibration_g"] * sin(2.0 * pi * cfg["frequency_hz"] * t)
            slip_ratio = max(0.0, (abs(accel_g) - friction_mu) / max(0.01, friction_mu))
            base_shift = slip_ratio * (18.0 + 42.0 * height_norm)
            max_slip_mm = max(max_slip_mm, base_shift)

            shifted: list[tuple[float, float, float, float]] = []
            for b in boxes:
                layer_factor = 1.0 + (b["z"] / max(1.0, stack_height)) * 0.6
                px = b["x"] / max(1.0, pallet_l)
                differential = 1.0 + 0.12 * px
                shift_x = base_shift * layer_factor * differential
                x1 = b["x"] + shift_x
                y1 = b["y"]
                x2 = x1 + b["dx"]
                y2 = y1 + b["dy"]
                shifted.append((x1, y1, x2, y2))

                if x1 < 0 or y1 < 0 or x2 > pallet_l or y2 > pallet_w:
                    overhang_events += 1

            for i in range(len(shifted)):
                ax1, ay1, ax2, ay2 = shifted[i]
                for j in range(i + 1, len(shifted)):
                    bx1, by1, bx2, by2 = shifted[j]
                    if not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1):
                        collision_events += 1

        risk_score = shift_norm * 50.0 + (max_slip_mm / 120.0) * 60.0 + min(35.0, overhang_events / 45.0)
        stability_index = max(0, min(100, int(round(100.0 - risk_score))))

        report_profiles[name] = {
            "max_slip_mm": round(max_slip_mm, 3),
            "overhang_events": overhang_events,
            "collision_events": collision_events,
            "stability_index": stability_index,
            "assumptions": {
                "friction_mu": friction_mu,
                "base_accel_g": cfg["base_g"],
                "vibration_accel_g": cfg["vibration_g"],
                "frequency_hz": cfg["frequency_hz"],
                "time_step_s": round(1.0 / 24.0, 6),
                "steps": sim_steps,
            },
        }

    aggregate_index = int(round(sum(v["stability_index"] for v in report_profiles.values()) / len(report_profiles)))

    return {
        "solution_id": solution.get("solution_id", "unknown"),
        "stability_index": aggregate_index,
        "center_of_gravity": {
            "x_mm": round(cx, 3),
            "y_mm": round(cy, 3),
            "z_mm": round(cz, 3),
            "lateral_shift_mm": round(center_shift, 3),
        },
        "profiles": report_profiles,
    }


def write_3d_stability_report(run_dir: Path, bundle: dict[str, Any]) -> tuple[Path, Path]:
    recommender = bundle.get("recommender", {})
    solutions = recommender.get("solutions", [])

    top = solutions[0] if solutions else {}
    baseline = next((s for s in solutions if str(s.get("solution_id", "")).startswith("grid_")), top)

    payload = {
        "run_id": bundle.get("run_id", "unknown"),
        "generated_at": bundle.get("created_at"),
        "request": {
            "pallet": bundle.get("request", {}).get("pallet", {}),
            "case": bundle.get("request", {}).get("case", {}),
            "stack": bundle.get("request", {}).get("stack", {}),
        },
        "analysis": {
            "after": _solution_stability(bundle, top),
            "before": _solution_stability(bundle, baseline),
        },
    }

    after = payload["analysis"]["after"]
    before = payload["analysis"]["before"]
    improvement = after["stability_index"] - before["stability_index"]

    lines = [
        "# 3D Stability Report",
        "",
        f"Run ID: {payload['run_id']}",
        "",
        "## Summary",
        f"- Before solution: {before['solution_id']} (index {before['stability_index']}/100)",
        f"- After solution: {after['solution_id']} (index {after['stability_index']}/100)",
        f"- Stability delta: {improvement:+d}",
        "",
        "## Physics Assumptions",
        "- Time-step vibration and slip model with Coulomb friction approximation.",
        "- Slip occurs when |acceleration_g| exceeds friction coefficient (mu).",
        "- Differential layer displacement increases with stack height.",
        "",
        "## Truck Profile Results (After)",
    ]

    for name, data in after["profiles"].items():
        lines.append(
            f"- {name}: index={data['stability_index']}, max_slip_mm={data['max_slip_mm']}, "
            f"overhang_events={data['overhang_events']}, collision_events={data['collision_events']}"
        )

    lines.append("")

    md_path = run_dir / "stability_report_3d.md"
    json_path = run_dir / "stability_report_3d.json"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return md_path, json_path


def update_bundle_artifacts(bundle: dict[str, Any], artifact_map: dict[str, str]) -> dict[str, Any]:
    artifacts = dict(bundle.get("artifacts", {}))
    for key, filename in artifact_map.items():
        artifacts[key] = {"path": filename}
    bundle["artifacts"] = artifacts
    return bundle
