import type { WeightUnit } from "../api/types";

export function formatPatternLabel(solutionId: string): string {
  let label = solutionId;
  
  if (label === "mixed_irregular_opt") {
    return "Mixed Irregular (Optimized)";
  }
  
  if (label.startsWith("grid_")) {
    label = label.slice(5);
  }

  const interlock = label.endsWith("_interlock");
  if (interlock) {
    label = label.slice(0, -"_interlock".length);
  }

  const rotationMatch = label.match(/_rot(\d+)$/);
  if (rotationMatch) {
    const angle = rotationMatch[1];
    label = `${label.replace(/_rot\d+$/, "")} ${angle} deg`;
  }

  return label;
}

export function formatInterlock(interlock: boolean): string {
  return interlock ? "Interlock" : "Normal";
}

export function convertWeight(valueKg: number | null | undefined, unit: WeightUnit): string {
  if (valueKg === null || valueKg === undefined) {
    return "n/a";
  }
  if (unit === "lbs") {
    return `${(valueKg / 0.453592).toFixed(1)} lbs`;
  }
  return `${valueKg.toFixed(1)} kg`;
}
