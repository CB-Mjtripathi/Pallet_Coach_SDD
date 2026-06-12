from __future__ import annotations

from math import ceil

from .models import (
    EdgeClearance,
    FootprintBBox,
    InnerAxisSegments,
    Placement,
    Solution,
    SolutionMetrics,
    SolveRequestNormalized,
    SolverReason,
    SolverResult,
)
from .overhang_underhang import calculate_case_hang_metrics, compute_layout_underhang_ratio


def _rotation_options(req: SolveRequestNormalized) -> list[int]:
    return [0, 90] if req.constraints.allow_rotation_90 else [0]


def _grid_counts(pallet_dim_mm: int, case_dim_mm: int, max_overhang_mm: int) -> range:
    upper = max(0, ceil((pallet_dim_mm + max_overhang_mm) / case_dim_mm))
    return range(1, upper + 1)


def _build_grid_layout(
    nx: int,
    ny: int,
    case_dim_x: float,
    case_dim_y: float,
    rotation_deg: int,
    interlock: bool = False,
    row_offset_mm: float = 0.0,
) -> list[Placement]:
    layout: list[Placement] = []
    for row in range(ny):
        x_offset = row_offset_mm if interlock and row % 2 == 1 else 0.0
        for col in range(nx):
            layout.append(
                Placement(
                    x_mm=x_offset + col * case_dim_x,
                    y_mm=row * case_dim_y,
                    rotation_deg=rotation_deg,
                    dim_x_mm=case_dim_x,
                    dim_y_mm=case_dim_y,
                )
            )
    return layout


def _candidate_axis_positions(limit_mm: int, segment_lengths_mm: list[int]) -> list[float]:
    positions = {0.0}
    changed = True
    while changed:
        next_positions = set(positions)
        for base in positions:
            for length in segment_lengths_mm:
                candidate = base + float(length)
                if candidate <= limit_mm:
                    next_positions.add(candidate)
        changed = len(next_positions) != len(positions)
        positions = next_positions
    return sorted(positions)


def _candidate_mixed_placements(req: SolveRequestNormalized) -> list[Placement]:
    dims_by_rotation = [
        (
            req.case.length_mm if rotation == 0 else req.case.width_mm,
            req.case.width_mm if rotation == 0 else req.case.length_mm,
            rotation,
        )
        for rotation in _rotation_options(req)
    ]
    candidate_x = _candidate_axis_positions(
        req.pallet.length_mm,
        [int(dim_x) for dim_x, _, _ in dims_by_rotation],
    )
    candidate_y = _candidate_axis_positions(
        req.pallet.width_mm,
        [int(dim_y) for _, dim_y, _ in dims_by_rotation],
    )

    placements: list[Placement] = []
    seen: set[tuple[float, float, int]] = set()
    for x_mm in candidate_x:
        for y_mm in candidate_y:
            for dim_x_mm, dim_y_mm, rotation_deg in dims_by_rotation:
                if x_mm + dim_x_mm > req.pallet.length_mm or y_mm + dim_y_mm > req.pallet.width_mm:
                    continue
                signature = (x_mm, y_mm, rotation_deg)
                if signature in seen:
                    continue
                seen.add(signature)
                placements.append(
                    Placement(
                        x_mm=x_mm,
                        y_mm=y_mm,
                        rotation_deg=rotation_deg,
                        dim_x_mm=dim_x_mm,
                        dim_y_mm=dim_y_mm,
                    )
                )
    return placements


def _best_mixed_layout(
    req: SolveRequestNormalized,
    min_cases_to_beat: int,
    max_candidate_positions: int = 256,
) -> list[Placement] | None:
    candidates = _candidate_mixed_placements(req)
    if not candidates or len(candidates) > max_candidate_positions:
        return None

    conflicts: list[set[int]] = [set() for _ in range(len(candidates))]
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            if _boxes_overlap(candidates[i], candidates[j]):
                conflicts[i].add(j)
                conflicts[j].add(i)

    best_indices: tuple[int, ...] = ()
    best_count = max(0, min_cases_to_beat)

    def search(chosen: tuple[int, ...], remaining: frozenset[int]) -> None:
        nonlocal best_count, best_indices
        if len(chosen) + len(remaining) <= best_count:
            return
        if not remaining:
            if len(chosen) > best_count:
                best_count = len(chosen)
                best_indices = chosen
            return

        pivot = max(remaining, key=lambda idx: len(conflicts[idx] & remaining))
        search(chosen + (pivot,), remaining - {pivot} - conflicts[pivot])
        search(chosen, remaining - {pivot})

    search((), frozenset(range(len(candidates))))
    if not best_indices:
        return None

    layout = [candidates[idx] for idx in best_indices]
    return sorted(layout, key=lambda placement: (placement.y_mm, placement.x_mm, placement.rotation_deg))


def _boxes_overlap(a: Placement, b: Placement) -> bool:
    ax2, ay2 = a.x_mm + a.dim_x_mm, a.y_mm + a.dim_y_mm
    bx2, by2 = b.x_mm + b.dim_x_mm, b.y_mm + b.dim_y_mm
    return not (ax2 <= b.x_mm or bx2 <= a.x_mm or ay2 <= b.y_mm or by2 <= a.y_mm)


def _has_overlap(layout: list[Placement]) -> bool:
    for i in range(len(layout)):
        for j in range(i + 1, len(layout)):
            if _boxes_overlap(layout[i], layout[j]):
                return True
    return False


def _compute_footprint_bbox(layout: list[Placement]) -> FootprintBBox:
    min_x = min(p.x_mm for p in layout)
    min_y = min(p.y_mm for p in layout)
    max_x = max(p.x_mm + p.dim_x_mm for p in layout)
    max_y = max(p.y_mm + p.dim_y_mm for p in layout)
    return FootprintBBox(min_x_mm=min_x, min_y_mm=min_y, max_x_mm=max_x, max_y_mm=max_y)


def _compute_edge_clearance(req: SolveRequestNormalized, bbox: FootprintBBox) -> EdgeClearance:
    return EdgeClearance(
        left_mm=bbox.min_x_mm,
        right_mm=req.pallet.length_mm - bbox.max_x_mm,
        bottom_mm=bbox.min_y_mm,
        top_mm=req.pallet.width_mm - bbox.max_y_mm,
    )


def _evaluate_tolerance(req: SolveRequestNormalized, clearance: EdgeClearance, layout: list[Placement]) -> bool:
    left_overhang = max(0.0, -clearance.left_mm)
    right_overhang = max(0.0, -clearance.right_mm)
    bottom_overhang = max(0.0, -clearance.bottom_mm)
    top_overhang = max(0.0, -clearance.top_mm)

    overhang_l_pass = (
        left_overhang <= req.tolerances.max_overhang_l_mm
        and right_overhang <= req.tolerances.max_overhang_l_mm
    )
    overhang_w_pass = (
        bottom_overhang <= req.tolerances.max_overhang_w_mm
        and top_overhang <= req.tolerances.max_overhang_w_mm
    )

    if req.constraints.auto_underhang:
        underhang_l_pass = True
        underhang_w_pass = True
    else:
        underhang_l_pass = min(clearance.left_mm, clearance.right_mm) <= req.tolerances.max_underhang_l_mm
        underhang_w_pass = min(clearance.bottom_mm, clearance.top_mm) <= req.tolerances.max_underhang_w_mm

    ratio_pass = True
    if req.constraints.max_overhang_percent is not None:
        max_ratio = max(0.0, float(req.constraints.max_overhang_percent)) / 100.0
        for placement in layout:
            metrics = calculate_case_hang_metrics(
                pallet_length_mm=req.pallet.length_mm,
                pallet_width_mm=req.pallet.width_mm,
                case_length_mm=placement.dim_x_mm,
                case_width_mm=placement.dim_y_mm,
                position_x_mm=placement.x_mm,
                position_y_mm=placement.y_mm,
            )
            if metrics.overhang_ratio > max_ratio:
                ratio_pass = False
                break

    underhang_ratio_pass = True
    if req.constraints.min_underhang_percent is not None:
        min_ratio = max(0.0, float(req.constraints.min_underhang_percent)) / 100.0
        layout_underhang_ratio = compute_layout_underhang_ratio(
            req.pallet.length_mm,
            req.pallet.width_mm,
            layout,
        )
        underhang_ratio_pass = layout_underhang_ratio >= min_ratio

    return overhang_l_pass and overhang_w_pass and underhang_l_pass and underhang_w_pass and ratio_pass and underhang_ratio_pass


def _inner_axis_segments(layout: list[Placement]) -> InnerAxisSegments:
    x_edges = sorted({p.x_mm for p in layout} | {p.x_mm + p.dim_x_mm for p in layout})
    y_edges = sorted({p.y_mm for p in layout} | {p.y_mm + p.dim_y_mm for p in layout})
    x_segments = [round(x_edges[i + 1] - x_edges[i], 6) for i in range(len(x_edges) - 1)]
    y_segments = [round(y_edges[i + 1] - y_edges[i], 6) for i in range(len(y_edges) - 1)]
    return InnerAxisSegments(x_segments_mm=x_segments, y_segments_mm=y_segments)


def _compute_metrics(
    req: SolveRequestNormalized,
    layout: list[Placement],
    tolerance_pass: bool,
    interlock: bool,
) -> SolutionMetrics:
    cases_per_layer = len(layout)
    total_cases = cases_per_layer * req.stack.layer_count
    total_height_mm = 144 + req.stack.layer_count * req.case.height_mm
    total_weight_kg = None
    if req.case.weight_kg is not None:
        total_weight_kg = cases_per_layer * req.stack.layer_count * req.case.weight_kg

    bbox = _compute_footprint_bbox(layout)
    clearance = _compute_edge_clearance(req, bbox)
    efficiency = 100.0 * (
        cases_per_layer * req.case.length_mm * req.case.width_mm
    ) / (req.pallet.length_mm * req.pallet.width_mm)

    return SolutionMetrics(
        cases_per_layer=cases_per_layer,
        total_cases=total_cases,
        total_height_mm=total_height_mm,
        total_weight_kg=round(total_weight_kg, 3) if total_weight_kg is not None else None,
        area_fill_efficiency_pct=round(efficiency, 6),
        footprint_bbox_mm=bbox,
        edge_clearance_mm=clearance,
        tolerance_pass=tolerance_pass,
        inner_axis_segments_mm=_inner_axis_segments(layout),
        interlock=interlock,
    )


def _rank_solutions(solutions: list[Solution]) -> list[Solution]:
    return sorted(
        solutions,
        key=lambda s: (
            -s.metrics.cases_per_layer,
            -s.metrics.area_fill_efficiency_pct,
            s.solution_id,
        ),
    )


def _case_larger_than_pallet_with_tolerance(req: SolveRequestNormalized) -> bool:
    can_fit_any = False
    for rotation in _rotation_options(req):
        dim_x = req.case.length_mm if rotation == 0 else req.case.width_mm
        dim_y = req.case.width_mm if rotation == 0 else req.case.length_mm
        fits_x = dim_x <= req.pallet.length_mm + req.tolerances.max_overhang_l_mm
        fits_y = dim_y <= req.pallet.width_mm + req.tolerances.max_overhang_w_mm
        can_fit_any = can_fit_any or (fits_x and fits_y)
    return not can_fit_any


def solve(req: SolveRequestNormalized, max_options: int = 25) -> SolverResult:
    if req.stack.layer_count < 1:
        return SolverResult(
            status="impossible",
            reasons=[
                SolverReason(
                    code="LAYER_COUNT_INVALID",
                    message="Layer count must be >= 1.",
                )
            ],
            solutions=[],
        )

    capped_max_options = max(1, min(int(max_options), 250))
    candidates: list[Solution] = []

    for rotation in _rotation_options(req):
        case_dim_x = req.case.length_mm if rotation == 0 else req.case.width_mm
        case_dim_y = req.case.width_mm if rotation == 0 else req.case.length_mm

        nx_range = _grid_counts(req.pallet.length_mm, case_dim_x, req.tolerances.max_overhang_l_mm)
        ny_range = _grid_counts(req.pallet.width_mm, case_dim_y, req.tolerances.max_overhang_w_mm)

        for nx in nx_range:
            for ny in ny_range:
                layout = _build_grid_layout(nx, ny, case_dim_x, case_dim_y, rotation)
                if _has_overlap(layout):
                    continue
                clearance = _compute_edge_clearance(req, _compute_footprint_bbox(layout))
                tolerance_pass = _evaluate_tolerance(req, clearance, layout)
                metrics = _compute_metrics(req, layout, tolerance_pass, interlock=False)
                candidates.append(
                    Solution(
                        solution_id=f"grid_{nx}x{ny}_rot{rotation}",
                        layout=layout,
                        metrics=metrics,
                    )
                )

                if req.constraints.allow_interlock:
                    interlock_layout = _build_grid_layout(
                        nx,
                        ny,
                        case_dim_x,
                        case_dim_y,
                        rotation,
                        interlock=True,
                        row_offset_mm=req.case.width_mm / 2.0,
                    )
                    if _has_overlap(interlock_layout):
                        continue
                    interlock_clearance = _compute_edge_clearance(req, _compute_footprint_bbox(interlock_layout))
                    interlock_pass = _evaluate_tolerance(req, interlock_clearance, interlock_layout)
                    interlock_metrics = _compute_metrics(
                        req,
                        interlock_layout,
                        interlock_pass,
                        interlock=True,
                    )
                    candidates.append(
                        Solution(
                            solution_id=f"grid_{nx}x{ny}_rot{rotation}_interlock",
                            layout=interlock_layout,
                            metrics=interlock_metrics,
                        )
                    )

    passing = [c for c in candidates if c.metrics.tolerance_pass]

    top_grid_cases = max((solution.metrics.cases_per_layer for solution in passing), default=0)
    mixed_layout = _best_mixed_layout(req, min_cases_to_beat=top_grid_cases)
    if mixed_layout is not None:
        mixed_clearance = _compute_edge_clearance(req, _compute_footprint_bbox(mixed_layout))
        mixed_pass = _evaluate_tolerance(req, mixed_clearance, mixed_layout)
        mixed_metrics = _compute_metrics(req, mixed_layout, mixed_pass, interlock=False)
        candidates.append(
            Solution(
                solution_id="mixed_irregular_opt",
                layout=mixed_layout,
                metrics=mixed_metrics,
            )
        )
        if mixed_metrics.tolerance_pass:
            passing.append(candidates[-1])

    ranked = _rank_solutions(passing)

    if not ranked:
        if _case_larger_than_pallet_with_tolerance(req):
            reason = SolverReason(
                code="CASE_LARGER_THAN_PALLET_WITH_TOLERANCE",
                message="Case is larger than pallet dimensions under current tolerance limits.",
            )
        else:
            reason = SolverReason(
                code="NO_FEASIBLE_PATTERN",
                message="No placements satisfy the tolerance constraints.",
            )
        return SolverResult(status="impossible", reasons=[reason], solutions=[])

    return SolverResult(status="ok", reasons=[], solutions=ranked[:capped_max_options])
