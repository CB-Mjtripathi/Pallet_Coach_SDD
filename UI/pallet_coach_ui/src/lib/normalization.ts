import type { DimUnit, SolvePayload, WeightUnit } from "../api/types";
import type { PresetKey } from "./palletPresets";
import { PALLET_PRESETS } from "./palletPresets";

export interface HomeFormState {
  dimUnit: DimUnit;
  weightUnit: WeightUnit;
  skuCode: string;
  skuDescription: string;
  caseLength: string;
  caseWidth: string;
  caseHeight: string;
  caseWeight: string;
  preset: PresetKey;
  layers: string;
  allowInterlock: boolean;
  maxPalletWeight: string;
}

function toMm(value: number, unit: DimUnit): number {
  if (unit === "inch") {
    return Math.round(value * 25.4);
  }
  return Math.round(value);
}

function toKg(value: number, unit: WeightUnit): number {
  if (unit === "lbs") {
    return Math.round(value * 0.453592 * 1000) / 1000;
  }
  return Math.round(value * 1000) / 1000;
}

export function buildSolvePayload(form: HomeFormState): SolvePayload {
  const preset = PALLET_PRESETS[form.preset];
  const caseLengthNum = Number(form.caseLength);
  const caseWidthNum = Number(form.caseWidth);
  const caseHeightNum = Number(form.caseHeight);
  const layerCountNum = Number(form.layers);

  const payload: SolvePayload = {
    request: {
      meta: {
        dim_unit: form.dimUnit,
        weight_unit: form.weightUnit,
        sku_code: form.skuCode || undefined,
        sku_description: form.skuDescription || undefined,
      },
      pallet: {
        type: preset.type,
        length_mm: preset.length_mm,
        width_mm: preset.width_mm,
      },
      case: {
        length_mm: toMm(caseLengthNum, form.dimUnit),
        width_mm: toMm(caseWidthNum, form.dimUnit),
        height_mm: toMm(caseHeightNum, form.dimUnit),
      },
      stack: {
        layer_count: Math.round(layerCountNum),
      },
      tolerances: {
        max_overhang_l_mm: 0,
        max_overhang_w_mm: 0,
        max_underhang_l_mm: 0,
        max_underhang_w_mm: 0,
      },
      constraints: {
        allow_rotation_90: true,
        allow_interlock: form.allowInterlock,
        auto_underhang: true,
      },
    },
    max_solutions: 10,
    include_timestamp: true,
  };

  if (form.caseWeight.trim()) {
    payload.request.case.weight_kg = toKg(Number(form.caseWeight), form.weightUnit);
  }

  if (form.maxPalletWeight.trim()) {
    payload.request.constraints.max_pallet_weight_kg = toKg(Number(form.maxPalletWeight), form.weightUnit);
  }

  return payload;
}
