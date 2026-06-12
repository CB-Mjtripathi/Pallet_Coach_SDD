import { describe, expect, it } from "vitest";
import { convertWeight, formatInterlock, formatPatternLabel } from "./formatters";

describe("formatters", () => {
  it("formats pattern labels", () => {
    expect(formatPatternLabel("grid_4x3_rot90_interlock")).toBe("4x3 90 deg");
    expect(formatPatternLabel("grid_4x3_rot0")).toBe("4x3 0 deg");
  });

  it("formats interlock", () => {
    expect(formatInterlock(true)).toBe("Interlock");
    expect(formatInterlock(false)).toBe("Normal");
  });

  it("converts weights", () => {
    expect(convertWeight(10, "kg")).toBe("10.0 kg");
    expect(convertWeight(10, "lbs")).toContain("lbs");
  });
});
