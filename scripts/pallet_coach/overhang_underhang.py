from __future__ import annotations

from dataclasses import dataclass

from .models import Placement


@dataclass(frozen=True)
class CaseHangMetrics:
    left_mm: float
    right_mm: float
    front_mm: float
    back_mm: float
    overhang_left_mm: float
    overhang_right_mm: float
    overhang_front_mm: float
    overhang_back_mm: float
    overlap_length_mm: float
    overlap_width_mm: float
    occupied_area_mm2: float
    case_area_mm2: float
    overhang_area_mm2: float
    overhang_ratio: float
    underhang_impact_ratio: float
    is_inside_pallet: bool


@dataclass(frozen=True)
class CaseHangValidation:
    is_valid: bool
    reason: str | None
    metrics: CaseHangMetrics


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def calculate_case_hang_metrics(
    pallet_length_mm: float,
    pallet_width_mm: float,
    case_length_mm: float,
    case_width_mm: float,
    position_x_mm: float,
    position_y_mm: float,
) -> CaseHangMetrics:
    left = float(position_x_mm)
    right = float(position_x_mm + case_length_mm)
    front = float(position_y_mm)
    back = float(position_y_mm + case_width_mm)

    overhang_left = max(0.0, 0.0 - left)
    overhang_right = max(0.0, right - float(pallet_length_mm))
    overhang_front = max(0.0, 0.0 - front)
    overhang_back = max(0.0, back - float(pallet_width_mm))

    overlap_length = max(0.0, min(right, float(pallet_length_mm)) - max(left, 0.0))
    overlap_width = max(0.0, min(back, float(pallet_width_mm)) - max(front, 0.0))
    occupied_area = overlap_length * overlap_width

    case_area = max(1.0, float(case_length_mm * case_width_mm))
    overhang_area = max(0.0, case_area - occupied_area)
    overhang_ratio = _clamp(overhang_area / case_area, 0.0, 1.0)

    pallet_area = max(1.0, float(pallet_length_mm * pallet_width_mm))
    underhang_impact_ratio = _clamp(1.0 - (occupied_area / pallet_area), 0.0, 1.0)

    return CaseHangMetrics(
        left_mm=left,
        right_mm=right,
        front_mm=front,
        back_mm=back,
        overhang_left_mm=overhang_left,
        overhang_right_mm=overhang_right,
        overhang_front_mm=overhang_front,
        overhang_back_mm=overhang_back,
        overlap_length_mm=overlap_length,
        overlap_width_mm=overlap_width,
        occupied_area_mm2=occupied_area,
        case_area_mm2=case_area,
        overhang_area_mm2=overhang_area,
        overhang_ratio=overhang_ratio,
        underhang_impact_ratio=underhang_impact_ratio,
        is_inside_pallet=overlap_length > 0 and overlap_width > 0,
    )


def validate_case_hang(
    metrics: CaseHangMetrics,
    max_overhang_percent: float,
    support_ok: bool = True,
) -> CaseHangValidation:
    max_overhang_ratio = max(0.0, float(max_overhang_percent)) / 100.0

    if metrics.overlap_length_mm <= 0.0 or metrics.overlap_width_mm <= 0.0:
        return CaseHangValidation(
            is_valid=False,
            reason="CASE_OUTSIDE_PALLET",
            metrics=metrics,
        )

    if metrics.overhang_ratio > max_overhang_ratio:
        return CaseHangValidation(
            is_valid=False,
            reason="OVERHANG_RATIO_EXCEEDED",
            metrics=metrics,
        )

    if not support_ok:
        return CaseHangValidation(
            is_valid=False,
            reason="SUPPORT_CHECK_FAILED",
            metrics=metrics,
        )

    return CaseHangValidation(is_valid=True, reason=None, metrics=metrics)


def compute_layout_underhang_ratio(
    pallet_length_mm: float,
    pallet_width_mm: float,
    layout: list[Placement],
) -> float:
    pallet_area = max(1.0, float(pallet_length_mm * pallet_width_mm))
    occupied_area = 0.0
    for p in layout:
        m = calculate_case_hang_metrics(
            pallet_length_mm,
            pallet_width_mm,
            p.dim_x_mm,
            p.dim_y_mm,
            p.x_mm,
            p.y_mm,
        )
        occupied_area += m.occupied_area_mm2

    underhang_area = max(0.0, pallet_area - occupied_area)
    return _clamp(underhang_area / pallet_area, 0.0, 1.0)
