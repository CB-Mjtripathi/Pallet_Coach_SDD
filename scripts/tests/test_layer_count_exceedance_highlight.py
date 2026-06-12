from pallet_coach.contracts import parse_request
from pallet_coach.stacking import compute_stacking_analysis


def test_warning_emitted_when_current_stack_height_exceeds_2000():
    req = parse_request(
        {
            "request": {
                "pallet": {"type": "euro", "length_mm": 1200, "width_mm": 800},
                "case": {"length_mm": 300, "width_mm": 200, "height_mm": 300},
                "stack": {"layer_count": 8},
                "constraints": {},
            }
        }
    )
    stacking = compute_stacking_analysis(req, cases_per_layer=8)
    assert any("exceeds 2000 mm" in warning for warning in stacking.warnings)


def test_weight_warning_emitted_when_weight_is_binding():
    req = parse_request(
        {
            "request": {
                "pallet": {"type": "industrial", "length_mm": 1200, "width_mm": 1000},
                "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150, "weight_kg": 10},
                "stack": {"layer_count": 4},
                "constraints": {"max_pallet_weight_kg": 200},
            }
        }
    )
    stacking = compute_stacking_analysis(req, cases_per_layer=10)
    assert any("more restrictive" in warning for warning in stacking.warnings)
