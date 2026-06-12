from pallet_coach.contracts import parse_request
from pallet_coach.solver import solve


def test_zero_overhang_exact_fit_returns_feasible_solution():
    req = parse_request(
        {
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
                "constraints": {"allow_rotation_90": True, "allow_interlock": False},
            }
        }
    )
    result = solve(req)
    assert result.status == "ok"
    assert result.solutions
    assert result.solutions[0].metrics.cases_per_layer >= 16


def test_small_underhang_anchor_rule_passes_when_one_side_within_limit():
    req = parse_request(
        {
            "request": {
                "pallet": {"type": "industrial", "length_mm": 1200, "width_mm": 1000},
                "case": {"length_mm": 290, "width_mm": 200, "height_mm": 150},
                "stack": {"layer_count": 8},
                "tolerances": {
                    "max_overhang_l_mm": 0,
                    "max_overhang_w_mm": 0,
                    "max_underhang_l_mm": 0,
                    "max_underhang_w_mm": 0,
                },
                "constraints": {"allow_rotation_90": True, "allow_interlock": False},
            }
        }
    )
    result = solve(req)
    assert result.status == "ok"
    assert any(s.metrics.tolerance_pass for s in result.solutions)


def test_rotation_required_case_appears_when_allow_rotation_true():
    req = parse_request(
        {
            "request": {
                "pallet": {"type": "custom", "length_mm": 400, "width_mm": 500},
                "case": {"length_mm": 500, "width_mm": 300, "height_mm": 100},
                "stack": {"layer_count": 2},
                "tolerances": {
                    "max_overhang_l_mm": 0,
                    "max_overhang_w_mm": 0,
                    "max_underhang_l_mm": 20,
                    "max_underhang_w_mm": 20,
                },
                "constraints": {"allow_rotation_90": True, "allow_interlock": False},
            }
        }
    )
    result = solve(req)
    assert result.status == "ok"
    assert any(s.solution_id.endswith("rot90") for s in result.solutions)


def test_no_feasible_pattern_returns_impossible_reason_code():
    req = parse_request(
        {
            "request": {
                "pallet": {"type": "euro", "length_mm": 300, "width_mm": 200},
                "case": {"length_mm": 500, "width_mm": 500, "height_mm": 100},
                "stack": {"layer_count": 2},
                "tolerances": {
                    "max_overhang_l_mm": 0,
                    "max_overhang_w_mm": 0,
                    "max_underhang_l_mm": 20,
                    "max_underhang_w_mm": 20,
                },
                "constraints": {"allow_rotation_90": True, "allow_interlock": False},
            }
        }
    )
    result = solve(req)
    assert result.status == "impossible"
    assert result.reasons
    assert result.reasons[0].code in {
        "NO_FEASIBLE_PATTERN",
        "CASE_LARGER_THAN_PALLET_WITH_TOLERANCE",
    }


def test_mixed_layout_beats_simple_grid_for_410x280_on_euro_pallet():
    req = parse_request(
        {
            "request": {
                "pallet": {"type": "euro", "length_mm": 1200, "width_mm": 800},
                "case": {"length_mm": 410, "width_mm": 280, "height_mm": 160},
                "stack": {"layer_count": 8},
                "tolerances": {
                    "max_overhang_l_mm": 0,
                    "max_overhang_w_mm": 0,
                    "max_underhang_l_mm": 0,
                    "max_underhang_w_mm": 0,
                },
                "constraints": {"allow_rotation_90": True, "allow_interlock": False, "auto_underhang": True},
            }
        }
    )

    result = solve(req)

    assert result.status == "ok"
    assert result.solutions[0].solution_id == "mixed_irregular_opt"
    assert result.solutions[0].metrics.cases_per_layer == 6
    assert result.solutions[0].metrics.area_fill_efficiency_pct == 71.75
