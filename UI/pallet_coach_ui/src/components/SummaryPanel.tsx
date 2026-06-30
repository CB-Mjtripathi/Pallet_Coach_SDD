import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "./ui/Button";
import { Card } from "./ui/Card";

interface SummaryPanelProps {
  markdown: string;
  loading: boolean;
  statusMessage?: string | null;
  mode?: "rewrite_success" | "deterministic_fallback" | null;
  onRegenerate: () => void;
}

export function SummaryPanel({ markdown, loading, statusMessage, mode, onRegenerate }: SummaryPanelProps): JSX.Element {
  const modeLabel = mode === "deterministic_fallback" ? "Mode: Deterministic fallback" : mode === "rewrite_success" ? "Mode: AI rewrite" : null;

  return (
    <Card className="p-5 animate-in animate-delay-1">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm uppercase tracking-[0.18em] text-[rgb(var(--muted))]">AI Summary</h2>
        <Button variant="primary" onClick={onRegenerate} disabled={loading}>
          {loading ? "Regenerating" : "Regenerate"}
        </Button>
      </div>
      {modeLabel ? <p className="mb-2 text-xs text-[rgb(var(--muted))]">{modeLabel}</p> : null}
      {statusMessage ? <p className="mb-2 text-xs text-[rgb(var(--muted))]">{statusMessage}</p> : null}
      <div className="prose prose-invert max-w-none text-sm">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </Card>
  );
}
