import { describe, expect, it } from "vitest";
import * as fs from "node:fs";
import * as path from "node:path";

const cssPath = path.resolve(__dirname, "global.css");
const cssText = fs.readFileSync(cssPath, "utf-8");

describe("RF-006 theme tokens", () => {
  it("defines canonical root token values", () => {
    expect(cssText).toContain("--bg: 10 12 14");
    expect(cssText).toContain("--panel: 14 16 18");
    expect(cssText).toContain("--panel2: 18 20 24");
    expect(cssText).toContain("--line: 38 42 48");
    expect(cssText).toContain("--text: 235 239 244");
    expect(cssText).toContain("--muted: 155 165 178");
    expect(cssText).toContain("--accent: 80 220 255");
    expect(cssText).toContain("--danger: 255 108 108");
    expect(cssText).toContain("--shadow: 0 0 0");
  });

  it("includes required global motion and overlay contracts", () => {
    expect(cssText).toContain("body::before");
    expect(cssText).toContain("@keyframes fadeInUp");
    expect(cssText).toContain("@keyframes fadeIn");
    expect(cssText).toContain("@keyframes slideInRight");
    expect(cssText).toContain(".help-panel-enter");
    expect(cssText).toContain(".backdrop-enter");
    expect(cssText).toContain(".animate-delay-4");
  });
});
