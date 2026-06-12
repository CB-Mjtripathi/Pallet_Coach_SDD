from __future__ import annotations

from pallet_coach.models import Placement
from pallet_coach.overhang_underhang import (
    calculate_case_hang_metrics,
    compute_layout_underhang_ratio,
    validate_case_hang,
)


def test_case_hang_metrics_no_overhang_inside_pallet():
    metrics = calculate_case_hang_metrics(
        pallet_length_mm=1200,
        pallet_width_mm=800,
        case_length_mm=400,
        case_width_mm=300,
        position_x_mm=100,
        position_y_mm=50,
    )

    assert metrics.overhang_area_mm2 == 0
    assert metrics.overhang_ratio == 0
    assert metrics.is_inside_pallet is True


def test_case_hang_metrics_partial_overlap_has_overhang():
    metrics = calculate_case_hang_metrics(
        pallet_length_mm=1200,
        pallet_width_mm=800,
        case_length_mm=400,
        case_width_mm=300,
        position_x_mm=1000,
        position_y_mm=600,
    )

    assert metrics.overhang_right_mm > 0
    assert metrics.overhang_back_mm > 0
    assert metrics.overhang_ratio > 0


def test_validate_case_hang_rejects_overhang_ratio_exceeded():
    metrics = calculate_case_hang_metrics(
        pallet_length_mm=100,
        pallet_width_mm=100,
        case_length_mm=100,
        case_width_mm=100,
        position_x_mm=50,
        position_y_mm=0,
    )

    validation = validate_case_hang(metrics, max_overhang_percent=10.0)

    assert validation.is_valid is False
    assert validation.reason == "OVERHANG_RATIO_EXCEEDED"


def test_compute_layout_underhang_ratio():
    layout = [
        Placement(x_mm=0, y_mm=0, rotation_deg=0, dim_x_mm=600, dim_y_mm=800),
    ]

    ratio = compute_layout_underhang_ratio(
        pallet_length_mm=1200,
        pallet_width_mm=800,
        layout=layout,
    )

    assert ratio == 0.5
