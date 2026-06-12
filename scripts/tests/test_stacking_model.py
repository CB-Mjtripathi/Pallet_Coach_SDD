from pallet_coach.contracts import parse_request
from pallet_coach.stacking import compute_stacking_analysis


def _req(case_weight=None, max_weight=None):
    request = {
        "request": {
            "pallet": {"type": "euro", "length_mm": 1200, "width_mm": 800},
            "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150},
            "stack": {"layer_count": 8},
            "constraints": {"allow_rotation_90": True, "allow_interlock": False},
        }
    }
    if case_weight is not None:
        request["request"]["case"]["weight_kg"] = case_weight
    if max_weight is not None:
        request["request"]["constraints"]["max_pallet_weight_kg"] = max_weight
    return parse_request(request)


def test_height_ceiling_computation_matches_formula():
    req = _req()
    stacking = compute_stacking_analysis(req, cases_per_layer=12)
    assert stacking.height_ceiling_layers == 12


def test_weight_ceiling_computation_matches_formula():
    req = _req(case_weight=2.0, max_weight=300)
    stacking = compute_stacking_analysis(req, cases_per_layer=10)
    assert stacking.weight_ceiling_layers == 13


def test_effective_ceiling_uses_min_of_height_and_weight():
    req = _req(case_weight=5.0, max_weight=250)
    stacking = compute_stacking_analysis(req, cases_per_layer=10)
    assert stacking.height_ceiling_layers == 12
    assert stacking.weight_ceiling_layers == 4
    assert stacking.effective_ceiling_layers == 4


def test_optional_weight_fields_are_none_when_missing():
    req = _req()
    stacking = compute_stacking_analysis(req, cases_per_layer=10)
    assert stacking.weight_ceiling_layers is None


def test_recommended_range_caps_at_plus_three_and_effective_ceiling():
    req = _req(case_weight=5.0, max_weight=250)
    stacking = compute_stacking_analysis(req, cases_per_layer=10)
    assert stacking.recommended_layers_range.min == 4
    assert stacking.recommended_layers_range.max == 4
