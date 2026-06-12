import { useEffect, useRef } from "react";
import { Button } from "./ui/Button";

interface HelpPanelProps {
  open: boolean;
  onClose: () => void;
}

export function HelpPanel({ open, onClose }: HelpPanelProps): JSX.Element | null {
  const panelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }
    panelRef.current?.focus();

    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <>
      <button
        className="fixed inset-0 z-[60] bg-black/40 backdrop-enter"
        onClick={onClose}
        aria-label="Close help panel backdrop"
      />
      <div
        ref={panelRef}
        tabIndex={-1}
        className="fixed right-0 top-0 z-[70] h-full w-full max-w-md border-l border-[rgb(var(--line))] bg-[rgb(var(--panel))] help-panel-enter"
      >
        <div className="flex items-center justify-between border-b border-[rgb(var(--line))] px-5 py-4">
          <div>
            <div className="text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))]">Assistant</div>
            <h2 className="mt-2 text-lg">How to Use</h2>
          </div>
          <Button onClick={onClose} aria-label="Close help panel">
            x
          </Button>
        </div>
        <div className="h-[calc(100%-73px)] overflow-y-auto px-5 py-5 text-sm text-[rgb(var(--muted))]">
          <section className="animate-in mb-6">
            <h3 className="mb-2 text-xs uppercase tracking-[0.15em] text-[rgb(var(--accent))]">Welcome</h3>
            <p className="leading-relaxed">
              Pallet Coach calculates the optimal arrangement of cases on a pallet, maximizing space efficiency while
              respecting your geometry and stacking constraints.
            </p>
          </section>

          <div className="mb-6 h-px bg-[rgb(var(--line))]" />

          <section className="animate-in animate-delay-1 mb-6">
            <h3 className="mb-3 text-xs uppercase tracking-[0.15em] text-[rgb(var(--accent))]">How to Use</h3>
            <ol className="space-y-3">
              <li className="flex gap-3">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[rgba(var(--accent),0.3)] text-xs text-[rgb(var(--accent))]">
                  1
                </span>
                <span>Enter case dimensions, pallet preset, layers, and any optional constraints on the home screen.</span>
              </li>
              <li className="flex gap-3">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[rgba(var(--accent),0.3)] text-xs text-[rgb(var(--accent))]">
                  2
                </span>
                <span>Run the solver to generate ranked layout options, stacking guidance, and deterministic diagrams.</span>
              </li>
              <li className="flex gap-3">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[rgba(var(--accent),0.3)] text-xs text-[rgb(var(--accent))]">
                  3
                </span>
                <span>Review the run page for 3D visuals, recommendation summary, artifact downloads, and raw JSON.</span>
              </li>
            </ol>
          </section>

          <div className="mb-6 h-px bg-[rgb(var(--line))]" />

          <section className="animate-in animate-delay-2 mb-6">
            <h3 className="mb-3 text-xs uppercase tracking-[0.15em] text-[rgb(var(--accent))]">Reading Results</h3>
            <div className="space-y-3 leading-relaxed">
              <p>Use the options table to compare cases per layer, total cases, fill efficiency, and stack height.</p>
              <p>Use the stacking guidance to validate layer ranges, headroom, and weight ceilings before execution.</p>
            </div>
          </section>

          <div className="mb-6 h-px bg-[rgb(var(--line))]" />

          <section className="animate-in animate-delay-3">
            <h3 className="mb-3 text-xs uppercase tracking-[0.15em] text-[rgb(var(--accent))]">Tips</h3>
            <ul className="space-y-2 leading-relaxed">
              <li>Try both flat and 3D views to assess footprint clarity versus layer interpretation.</li>
              <li>Use interlock only when it improves stability without hurting cases per layer.</li>
              <li>Export the bundle when you need traceable artifacts for review or handoff.</li>
            </ul>
          </section>
        </div>
      </div>
    </>
  );
}
