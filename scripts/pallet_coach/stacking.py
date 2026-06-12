from __future__ import annotations

from math import floor

from .models import RecommendedRange, SolveRequestNormalized, StackingAnalysis

MAX_STACK_HEIGHT_MM = 2000
PALLET_HEIGHT_MM_DEFAULT = 144
PALLET_TARE_KG = {"euro": 25, "industrial": 30, "custom": 25}


def _recommended_range(current_layers: int, effective_ceiling_layers: int) -> RecommendedRange:
    rec_min = min(current_layers + 1, effective_ceiling_layers)
    rec_max = min(current_layers + 3, effective_ceiling_layers)
    return RecommendedRange(min=rec_min, max=max(rec_min, rec_max))


def compute_stacking_analysis(req: SolveRequestNormalized, cases_per_layer: int) -> StackingAnalysis:
    pallet_height_mm = PALLET_HEIGHT_MM_DEFAULT
    max_stack_height_mm = MAX_STACK_HEIGHT_MM

    current_layers = req.stack.layer_count
    current_stack_height_mm = pallet_height_mm + current_layers * req.case.height_mm
    headroom_mm = max_stack_height_mm - current_stack_height_mm

    available_load_height = max_stack_height_mm - pallet_height_mm
    height_ceiling_layers = floor(available_load_height / req.case.height_mm)

    weight_ceiling_layers: int | None = None
    if req.case.weight_kg is not None and req.constraints.max_pallet_weight_kg is not None and cases_per_layer > 0:
        pallet_tare = PALLET_TARE_KG.get(req.pallet.type, PALLET_TARE_KG["custom"])
        numerator = req.constraints.max_pallet_weight_kg - pallet_tare
        denominator = cases_per_layer * req.case.weight_kg
        if denominator > 0:
            weight_ceiling_layers = floor(numerator / denominator)

    effective_ceiling_layers = height_ceiling_layers
    if weight_ceiling_layers is not None:
        effective_ceiling_layers = min(height_ceiling_layers, weight_ceiling_layers)

    warnings: list[str] = []
    if current_stack_height_mm > MAX_STACK_HEIGHT_MM:
        warnings.append("Current stack height exceeds 2000 mm policy limit.")
    if weight_ceiling_layers is not None and weight_ceiling_layers < height_ceiling_layers:
        warnings.append("Weight ceiling is more restrictive than height ceiling.")

    addable_layers = max(0, effective_ceiling_layers - current_layers)
    return StackingAnalysis(
        current_layers=current_layers,
        max_stack_height_mm=max_stack_height_mm,
        pallet_height_mm=pallet_height_mm,
        current_stack_height_mm=current_stack_height_mm,
        headroom_mm=headroom_mm,
        height_ceiling_layers=height_ceiling_layers,
        weight_ceiling_layers=weight_ceiling_layers,
        effective_ceiling_layers=effective_ceiling_layers,
        recommended_layers_range=_recommended_range(current_layers, effective_ceiling_layers),
        max_layers_at_max_height=height_ceiling_layers,
        addable_layers_to_max_height=addable_layers,
        warnings=warnings,
        assumptions={"pallet_height_mm": pallet_height_mm, "max_stack_height_mm": max_stack_height_mm},
    )
