import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Button } from "./Button";
import { Card } from "./Card";
import { Field } from "./Field";
import { SelectInput } from "./SelectInput";
import { TextInput } from "./TextInput";
import { Toggle } from "./Toggle";

describe("RF-006 primitive contracts", () => {
  it("applies canonical base classes to primitives", () => {
    render(
      <>
        <Card>card body</Card>
        <Field label="Length">
          <TextInput aria-label="Length" defaultValue="120" />
        </Field>
        <Field label="Preset">
          <SelectInput aria-label="Preset" defaultValue="euro">
            <option value="euro">Euro</option>
          </SelectInput>
        </Field>
      </>
    );

    const card = screen.getByText("card body").closest("section");
    expect(card?.className).toContain("card");

    const input = screen.getByLabelText("Length");
    expect(input.className).toContain("text-input");

    const select = screen.getByLabelText("Preset");
    expect(select.className).toContain("select-input");
  });

  it("supports button variants and toggle interaction", () => {
    const onToggle = vi.fn();

    render(
      <>
        <Button variant="primary">Run</Button>
        <Button variant="ghost">Ghost</Button>
        <Toggle checked={false} onChange={onToggle} label="Enabled" id="allow-interlock" />
      </>
    );

    const runButton = screen.getByRole("button", { name: "Run" });
    expect(runButton.className).toContain("btn");
    expect(runButton.className).toContain("btn-primary");

    const ghostButton = screen.getByRole("button", { name: "Ghost" });
    expect(ghostButton.className).toContain("btn-ghost");

    fireEvent.click(screen.getByLabelText("Enabled"));
    expect(onToggle).toHaveBeenCalledWith(true);
  });
});
