export type WeightUnit = "kg" | "lbs";
export type DimUnit = "mm" | "inch";

export interface SolvePayload {
  request: {
    request_id?: string;
    meta: {
      dim_unit: DimUnit;
      weight_unit: WeightUnit;
      sku_code?: string;
      sku_description?: string;
    };
    pallet: {
      type: "euro" | "industrial" | "custom";
      length_mm: number;
      width_mm: number;
    };
    case: {
      length_mm: number;
      width_mm: number;
      height_mm: number;
      weight_kg?: number;
    };
    stack: {
      layer_count: number;
    };
    tolerances: {
      max_overhang_l_mm: number;
      max_overhang_w_mm: number;
      max_underhang_l_mm: number;
      max_underhang_w_mm: number;
    };
    constraints: {
      allow_rotation_90: boolean;
      allow_interlock: boolean;
      auto_underhang: boolean;
      max_pallet_weight_kg?: number;
    };
  };
  max_solutions: number;
  include_timestamp: boolean;
}

export interface SolveResponse {
  run_id: string;
  out_dir: string;
  solver_status: string;
  artifacts: Record<string, { path: string }>;
}

export interface Bundle {
  run_id: string;
  request: SolvePayload["request"];
  recommender: {
    status: string;
    reasons: Array<{ code: string; message: string }>;
    solutions: Array<{
      solution_id: string;
      layout: Array<{
        x_mm: number;
        y_mm: number;
        rotation_deg: number;
        dim_x_mm: number;
        dim_y_mm: number;
      }>;
      metrics: {
        cases_per_layer: number;
        total_cases: number;
        total_height_mm: number;
        total_weight_kg?: number | null;
        area_fill_efficiency_pct: number;
        interlock: boolean;
      };
    }>;
  };
  stacking: {
    max_stack_height_mm: number;
    pallet_height_mm: number;
    current_stack_height_mm: number;
    headroom_mm: number;
    current_layers: number;
    max_layers_at_max_height: number;
    addable_layers_to_max_height: number;
    weight_ceiling_layers?: number | null;
    weight_ceiling_layers_conservative?: number | null;
    recommended_layers_range: { min: number; max: number };
  };
  artifacts: Record<string, { path: string }>;
}
