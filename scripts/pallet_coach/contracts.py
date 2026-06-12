from __future__ import annotations

from typing import Any

from .errors import ContractError
from .models import (
    CaseInput,
    ConstraintInput,
    PalletInput,
    SolveRequestNormalized,
    StackInput,
    ToleranceInput,
)

DEFAULT_TOLERANCES = {
    "max_overhang_l_mm": 0,
    "max_overhang_w_mm": 0,
    "max_underhang_l_mm": 20,
    "max_underhang_w_mm": 20,
}


def _as_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise ContractError(f"{field_name} must be numeric", {"field": field_name})
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{field_name} must be numeric", {"field": field_name}) from exc


def validate_positive_int(field_name: str, value: Any, min_value: int = 1) -> int:
    number = _as_number(value, field_name)
    if int(number) != number:
        raise ContractError(f"{field_name} must be an integer", {"field": field_name})
    as_int = int(number)
    if as_int < min_value:
        raise ContractError(
            f"{field_name} must be >= {min_value}",
            {"field": field_name, "min": min_value},
        )
    return as_int


def _read_required(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ContractError(f"Missing required field: {key}", {"field": key})
    return mapping[key]


def parse_request(payload: dict[str, Any]) -> SolveRequestNormalized:
    req = payload.get("request", payload)
    if not isinstance(req, dict):
        raise ContractError("request must be an object", {"field": "request"})

    pallet_raw = _read_required(req, "pallet")
    case_raw = _read_required(req, "case")
    stack_raw = _read_required(req, "stack")

    if not isinstance(pallet_raw, dict) or not isinstance(case_raw, dict) or not isinstance(stack_raw, dict):
        raise ContractError("pallet, case, and stack must be objects")

    pallet = PalletInput(
        type=str(_read_required(pallet_raw, "type")).lower(),
        length_mm=validate_positive_int("pallet.length_mm", _read_required(pallet_raw, "length_mm")),
        width_mm=validate_positive_int("pallet.width_mm", _read_required(pallet_raw, "width_mm")),
    )

    weight = case_raw.get("weight_kg")
    case = CaseInput(
        length_mm=validate_positive_int("case.length_mm", _read_required(case_raw, "length_mm")),
        width_mm=validate_positive_int("case.width_mm", _read_required(case_raw, "width_mm")),
        height_mm=validate_positive_int("case.height_mm", _read_required(case_raw, "height_mm")),
        weight_kg=None if weight is None else float(_as_number(weight, "case.weight_kg")),
    )

    stack = StackInput(
        layer_count=validate_positive_int("stack.layer_count", _read_required(stack_raw, "layer_count"))
    )

    tolerance_raw = req.get("tolerances", {})
    if not isinstance(tolerance_raw, dict):
        raise ContractError("tolerances must be an object", {"field": "tolerances"})

    merged_tolerance = {**DEFAULT_TOLERANCES, **tolerance_raw}
    tolerances = ToleranceInput(
        max_overhang_l_mm=validate_positive_int(
            "tolerances.max_overhang_l_mm",
            merged_tolerance["max_overhang_l_mm"],
            min_value=0,
        ),
        max_overhang_w_mm=validate_positive_int(
            "tolerances.max_overhang_w_mm",
            merged_tolerance["max_overhang_w_mm"],
            min_value=0,
        ),
        max_underhang_l_mm=validate_positive_int(
            "tolerances.max_underhang_l_mm",
            merged_tolerance["max_underhang_l_mm"],
            min_value=0,
        ),
        max_underhang_w_mm=validate_positive_int(
            "tolerances.max_underhang_w_mm",
            merged_tolerance["max_underhang_w_mm"],
            min_value=0,
        ),
    )

    constraints_raw = req.get("constraints", {})
    if not isinstance(constraints_raw, dict):
        raise ContractError("constraints must be an object", {"field": "constraints"})

    max_pallet_weight_kg = constraints_raw.get("max_pallet_weight_kg")
    max_overhang_percent = constraints_raw.get("max_overhang_percent")
    min_underhang_percent = constraints_raw.get("min_underhang_percent")
    constraints = ConstraintInput(
        allow_rotation_90=bool(constraints_raw.get("allow_rotation_90", True)),
        allow_interlock=bool(constraints_raw.get("allow_interlock", False)),
        auto_underhang=bool(constraints_raw.get("auto_underhang", False)),
        max_pallet_weight_kg=(
            None
            if max_pallet_weight_kg is None
            else float(_as_number(max_pallet_weight_kg, "constraints.max_pallet_weight_kg"))
        ),
        max_overhang_percent=(
            None
            if max_overhang_percent is None
            else float(_as_number(max_overhang_percent, "constraints.max_overhang_percent"))
        ),
        min_underhang_percent=(
            None
            if min_underhang_percent is None
            else float(_as_number(min_underhang_percent, "constraints.min_underhang_percent"))
        ),
    )

    return SolveRequestNormalized(
        request_id=req.get("request_id"),
        meta=req.get("meta", {}),
        pallet=pallet,
        case=case,
        stack=stack,
        tolerances=tolerances,
        constraints=constraints,
    )
