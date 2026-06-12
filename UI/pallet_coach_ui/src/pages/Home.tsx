import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { postSolve } from "../api/endpoints";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Field } from "../components/ui/Field";
import { SelectInput } from "../components/ui/SelectInput";
import { TextInput } from "../components/ui/TextInput";
import { Toggle } from "../components/ui/Toggle";
import type { HomeFormState } from "../lib/normalization";
import { buildSolvePayload } from "../lib/normalization";
import { PALLET_PRESETS } from "../lib/palletPresets";
import { parseFiniteNumber, parsePositiveInt } from "../lib/validation";

const initialState: HomeFormState = {
  dimUnit: "mm",
  weightUnit: "kg",
  skuCode: "",
  skuDescription: "",
  caseLength: "",
  caseWidth: "",
  caseHeight: "",
  caseWeight: "",
  preset: "euro_1200x800",
  layers: "8",
  allowInterlock: false,
  maxPalletWeight: "",
};

export function Home(): JSX.Element {
  const navigate = useNavigate();
  const [form, setForm] = useState<HomeFormState>(initialState);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validation = useMemo(() => {
    const caseLength = parsePositiveInt(form.caseLength);
    const caseWidth = parsePositiveInt(form.caseWidth);
    const caseHeight = parsePositiveInt(form.caseHeight);
    const layers = parsePositiveInt(form.layers);
    const caseWeight = form.caseWeight.trim() ? parseFiniteNumber(form.caseWeight) : 1;
    const maxPalletWeight = form.maxPalletWeight.trim() ? parseFiniteNumber(form.maxPalletWeight) : 1;

    return {
      valid:
        caseLength !== null &&
        caseWidth !== null &&
        caseHeight !== null &&
        layers !== null &&
        caseWeight !== null &&
        maxPalletWeight !== null,
    };
  }, [form]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!validation.valid || submitting) {
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const payload = buildSolvePayload(form);
      const solve = await postSolve(payload);
      navigate(`/runs/${solve.run_id}`, {
        state: { summaryPending: true },
      });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to submit solve request";
      // Check for common issues
      if (errorMsg.includes("Network error") || errorMsg.includes("Unable to connect")) {
        setError("⚠️ Connection Error: Ensure the API server is running (python start_api.ps1)");
      } else if (errorMsg.includes("Not Found")) {
        setError("⚠️ API Error: The request endpoint was not found. Check API configuration.");
      } else {
        setError(errorMsg);
      }
    } finally {
      setSubmitting(false);
    }
  }

  function update<K extends keyof HomeFormState>(key: K, value: HomeFormState[K]): void {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div className="mx-auto max-w-3xl">
      <section className="hero-grid animate-in mb-10 overflow-hidden border border-[rgb(var(--line))] bg-[rgba(var(--panel),0.55)] px-6 py-8">
        <div className="relative z-10 text-center">
          <div className="status-pill animate-in animate-delay-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[rgb(var(--accent))]" />
            Online
          </div>
          <div className="animate-in animate-delay-2 mt-4 text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))]">
            Pallet optimization
          </div>
          <h1 className="animate-in animate-delay-2 mt-4 text-5xl leading-[1.0] tracking-tight gradient-text">Recommender</h1>
          <p className="animate-in animate-delay-3 mx-auto mt-6 max-w-md text-sm text-[rgb(var(--muted))]">
            Enter case dimensions, pallet specs, and constraints. The solver returns ranked options, deterministic
            diagrams, and a run-ready recommendation summary.
          </p>
          {error ? <p className="mx-auto mt-5 max-w-lg text-sm text-[rgb(var(--danger))]">{error}</p> : null}
        </div>
      </section>

      <Card as="form" className="space-y-6 p-6 animate-in animate-delay-4" onSubmit={onSubmit}>
        <section className="grid gap-4 sm:grid-cols-2">
          <Field label="Dimension unit">
            <SelectInput
              value={form.dimUnit}
              onChange={(e) => update("dimUnit", e.target.value as HomeFormState["dimUnit"])}
            >
              <option value="mm">mm</option>
              <option value="inch">inch</option>
            </SelectInput>
          </Field>
          <Field label="Weight unit">
            <SelectInput
              value={form.weightUnit}
              onChange={(e) => update("weightUnit", e.target.value as HomeFormState["weightUnit"])}
            >
              <option value="kg">kg</option>
              <option value="lbs">lbs</option>
            </SelectInput>
          </Field>
        </section>

        <section className="grid gap-4 border-t border-[rgb(var(--line))] pt-6 sm:grid-cols-2">
          <Field label="SKU code">
            <TextInput value={form.skuCode} onChange={(e) => update("skuCode", e.target.value)} placeholder="e.g., SKU-001" />
          </Field>
          <Field label="SKU description">
            <TextInput value={form.skuDescription} onChange={(e) => update("skuDescription", e.target.value)} placeholder="e.g., 24-pack carton" />
          </Field>
        </section>

        <section className="border-t border-[rgb(var(--line))] pt-6">
          <h2 className="mb-3 text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))]">Case</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Length" required>
              <TextInput value={form.caseLength} onChange={(e) => update("caseLength", e.target.value)} placeholder="e.g., 410" inputMode="decimal" />
            </Field>
            <Field label="Width" required>
              <TextInput value={form.caseWidth} onChange={(e) => update("caseWidth", e.target.value)} placeholder="e.g., 280" inputMode="decimal" />
            </Field>
            <Field label="Height" required>
              <TextInput value={form.caseHeight} onChange={(e) => update("caseHeight", e.target.value)} placeholder="e.g., 160" inputMode="decimal" />
            </Field>
          </div>
        </section>

        <section className="grid gap-4 border-t border-[rgb(var(--line))] pt-6 sm:grid-cols-2">
          <Field label="Case weight">
            <TextInput value={form.caseWeight} onChange={(e) => update("caseWeight", e.target.value)} placeholder="e.g., 18.0" inputMode="decimal" />
          </Field>
          <Field label="Pallet preset" required>
            <SelectInput
              value={form.preset}
              onChange={(e) => update("preset", e.target.value as HomeFormState["preset"])}
            >
              {Object.entries(PALLET_PRESETS).map(([key, preset]) => (
                <option key={key} value={key}>
                  {preset.label}
                </option>
              ))}
            </SelectInput>
          </Field>
        </section>

        <section className="grid gap-4 border-t border-[rgb(var(--line))] pt-6 sm:grid-cols-2">
          <Field label="Layers" required>
            <TextInput value={form.layers} onChange={(e) => update("layers", e.target.value)} placeholder="e.g., 8" inputMode="decimal" />
          </Field>
        </section>

        <section className="grid gap-4 border-t border-[rgb(var(--line))] pt-6 sm:grid-cols-2">
          <Field label="Allow interlock">
            <Toggle checked={form.allowInterlock} onChange={(checked) => update("allowInterlock", checked)} label="Enabled" />
          </Field>
          <Field label="Max pallet weight">
            <TextInput value={form.maxPalletWeight} onChange={(e) => update("maxPalletWeight", e.target.value)} placeholder="e.g., 1000" inputMode="decimal" />
          </Field>
        </section>

        <div className="flex justify-end">
          <Button variant="primary" type="submit" disabled={!validation.valid || submitting}>
            {submitting ? "Solving..." : "Get Started"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
