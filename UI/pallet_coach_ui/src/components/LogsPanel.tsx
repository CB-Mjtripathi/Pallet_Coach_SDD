import { Card } from "./ui/Card";

interface LogsPanelProps {
  logs: string;
}

export function LogsPanel({ logs }: LogsPanelProps): JSX.Element {
  return (
    <Card as="details" className="p-5 text-sm">
      <summary className="cursor-pointer text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))]">Run Logs</summary>
      <pre className="mt-3 max-h-80 overflow-auto rounded-sm border border-[rgb(var(--line))] bg-[rgb(var(--panel2))] p-3 text-xs text-[rgb(var(--text))]">
        {logs || "No logs available."}
      </pre>
    </Card>
  );
}
