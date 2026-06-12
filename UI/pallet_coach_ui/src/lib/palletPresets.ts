export type PresetKey = "industrial_1200x1000" | "euro_1200x800";

export const PALLET_PRESETS: Record<
  PresetKey,
  { label: string; type: "industrial" | "euro"; length_mm: number; width_mm: number }
> = {
  industrial_1200x1000: {
    label: "Industrial 1200x1000",
    type: "industrial",
    length_mm: 1200,
    width_mm: 1000,
  },
  euro_1200x800: {
    label: "Euro 1200x800",
    type: "euro",
    length_mm: 1200,
    width_mm: 800,
  },
};
