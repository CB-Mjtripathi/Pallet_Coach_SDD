import { useState } from "react";
import { Link } from "react-router-dom";
import { HelpPanel } from "./HelpPanel";
import { Button } from "./ui/Button";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps): JSX.Element {
  const [helpOpen, setHelpOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[rgb(var(--bg))] text-[rgb(var(--text))]">
      <header className="sticky top-0 z-50 border-b border-[rgb(var(--line))] bg-[rgba(var(--panel),0.88)] backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-3 no-underline">
              <div className="relative flex h-9 w-9 items-center justify-center border border-[rgba(var(--accent),0.35)] bg-[rgba(var(--accent),0.08)]">
                <span className="absolute inset-1 border border-[rgba(var(--accent),0.18)]" />
                <span className="h-2 w-2 rounded-full bg-[rgb(var(--accent))]" />
              </div>
              <div>
                <div className="text-[0.68rem] uppercase tracking-[0.22em] text-[rgb(var(--muted))]">Carlsberg GBS</div>
                <div className="font-mono text-sm tracking-[0.18em] text-[rgb(var(--accent))]">Pallet Coach</div>
              </div>
            </Link>
            <Button className="h-9 w-9 rounded-full p-0" onClick={() => setHelpOpen(true)} aria-label="Open help panel">
              ?
            </Button>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))] md:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              Online
            </div>
            <span className="badge px-3 py-1 text-xs uppercase tracking-[0.18em]">Step 1 MVP</span>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl px-6 py-10">{children}</main>
      <HelpPanel open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}
