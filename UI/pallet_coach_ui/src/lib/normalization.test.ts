import { describe, expect, it } from "vitest";
import { buildSolvePayload, type HomeFormState } from "./normalization";

const baseState: HomeFormState = {
  dimUnit: "mm",
  weightUnit: "kg",
  skuCode: "10263",
  skuDescription: "SKU test",
  caseLength: "300",
  caseWidth: "200",
  caseHeight: "150",
  caseWeight: "2.2",
  preset: "euro_1200x800",
  layers: "8",
  allowInterlock: false,
  maxPalletWeight: "1000",
};

describe("buildSolvePayload", () => {
  it("normalizes inch to mm and lbs to kg", () => {
    const payload = buildSolvePayload({
      ...baseState,
      dimUnit: "inch",
      weightUnit: "lbs",
      caseLength: "10",
      caseWidth: "8",
      caseHeight: "6",
      caseWeight: "5",
      maxPalletWeight: "100",
    });

    expect(payload.request.case.length_mm).toBe(254);
    expect(payload.request.case.width_mm).toBe(203);
    expect(payload.request.case.height_mm).toBe(152);
    expect(payload.request.case.weight_kg).toBeCloseTo(2.268, 3);
    expect(payload.request.constraints.max_pallet_weight_kg).toBeCloseTo(45.359, 3);
  });

  it("always sends auto_underhang true and zero tolerances", () => {
    const payload = buildSolvePayload(baseState);
    expect(payload.request.constraints.auto_underhang).toBe(true);
    expect(payload.request.tolerances).toEqual({
      max_overhang_l_mm: 0,
      max_overhang_w_mm: 0,
      max_underhang_l_mm: 0,
      max_underhang_w_mm: 0,
    });
  });
});
