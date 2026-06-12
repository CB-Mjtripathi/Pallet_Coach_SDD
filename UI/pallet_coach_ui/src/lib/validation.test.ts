import { describe, expect, it } from "vitest";
import { parseFiniteNumber, parsePositiveInt } from "./validation";

describe("validation helpers", () => {
  it("parsePositiveInt accepts positive integers", () => {
    expect(parsePositiveInt("8")).toBe(8);
    expect(parsePositiveInt("0")).toBeNull();
    expect(parsePositiveInt("2.5")).toBeNull();
    expect(parsePositiveInt("-1")).toBeNull();
  });

  it("parseFiniteNumber accepts positive finite numbers", () => {
    expect(parseFiniteNumber("2.5")).toBe(2.5);
    expect(parseFiniteNumber("0")).toBeNull();
    expect(parseFiniteNumber("foo")).toBeNull();
    expect(parseFiniteNumber("-1")).toBeNull();
  });
});
