import pytest

from pallet_coach.contracts import parse_request
from pallet_coach.errors import ContractError


def test_contract_rejects_missing_required_field():
    payload = {
        "request": {
            "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150},
            "stack": {"layer_count": 8},
        }
    }

    with pytest.raises(ContractError) as exc:
        parse_request(payload)

    assert "Missing required field: pallet" in str(exc.value)


def test_contract_rejects_non_integer_dimensions():
    payload = {
        "request": {
            "pallet": {"type": "euro", "length_mm": 1200.5, "width_mm": 800},
            "case": {"length_mm": 300, "width_mm": 200, "height_mm": 150},
            "stack": {"layer_count": 8},
        }
    }

    with pytest.raises(ContractError) as exc:
        parse_request(payload)

    assert "must be an integer" in str(exc.value)
