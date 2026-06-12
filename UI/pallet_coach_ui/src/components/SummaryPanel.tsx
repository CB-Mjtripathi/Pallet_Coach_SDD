import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "./ui/Button";
import { Card } from "./ui/Card";

interface SummaryPanelProps {
  markdown: string;
  loading: boolean;
  onRegenerate: () => void;
}

export function SummaryPanel({ markdown, loading, onRegenerate }: SummaryPanelProps): JSX.Element {
  return (
    <Card className="p-5 animate-in animate-delay-1">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm uppercase tracking-[0.18em] text-[rgb(var(--muted))]">AI Summary</h2>
        <Button variant="primary" onClick={onRegenerate} disabled={loading}>
          {loading ? "Regenerating" : "Regenerate"}
        </Button>
      </div>
      <div className="prose prose-invert max-w-none text-sm">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </Card>
  );
}
