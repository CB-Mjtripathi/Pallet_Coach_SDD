import { useEffect, useState } from "react";
import type { Bundle } from "../api/types";
import { Card } from "./ui/Card";

interface OverhangUnderhangRow {
  caseId: string;
  left: number;
  right: number;
  front: number;
  back: number;
  ohLeft: number;
  ohRight: number;
  ohFront: number;
  ohBack: number;
  overhangRatioPct: number;
  underhangImpactPct: number;
  valid: string;
}

interface OverhangUnderhangTableProps {
  bundle: Bundle;
  runId: string;
}

export function OverhangUnderhangPanel({ bundle, runId }: OverhangUnderhangTableProps): JSX.Element {
  const [rows, setRows] = useState<OverhangUnderhangRow[]>([]);
  const [totals, setTotals] = useState<{
    totalOverhangArea: number;
    layoutUnderhangRatio: number;
    palletUtilization: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTable() {
      try {
        // Defensive: check if bundle and artifacts exist
        if (!bundle?.artifacts) {
          setError("Bundle artifacts not available");
          setLoading(false);
          return;
        }

        const artifactPath = bundle.artifacts.overhang_underhang_table?.path;
        if (!artifactPath) {
          setError("Overhang/underhang table artifact not generated");
          setLoading(false);
          return;
        }

        const response = await fetch(`/output/${runId}/${artifactPath}`);
        if (!response.ok) {
          setError(`Failed to load table: ${response.status} ${response.statusText}`);
          setLoading(false);
          return;
        }

        const markdown = await response.text();
        if (!markdown || markdown.trim().length === 0) {
          setError("Table artifact is empty");
          setLoading(false);
          return;
        }

        const parsed = parseMarkdownTable(markdown);
        if (parsed.rows.length === 0 && !parsed.totals) {
          setError("No table data could be parsed");
          setLoading(false);
          return;
        }

        setRows(parsed.rows);
        setTotals(parsed.totals);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error loading table");
        setLoading(false);
      }
    }

    loadTable();
  }, [bundle, runId]);

  function getRowColor(row: OverhangUnderhangRow): string {
    if (row.valid === "no") return "bg-[rgb(220,38,38,0.1)]";
    if (row.overhangRatioPct > 5) return "bg-[rgb(220,38,38,0.08)]";
    if (row.overhangRatioPct > 1) return "bg-[rgb(245,158,11,0.08)]";
    if (row.underhangImpactPct > 20) return "bg-[rgb(245,158,11,0.05)]";
    return "";
  }

  function getStatusBadge(row: OverhangUnderhangRow): JSX.Element {
    if (row.valid === "no") {
      return <span className="inline-block rounded px-2 py-1 text-xs font-semibold bg-[rgb(220,38,38)] text-white">Outside</span>;
    }
    if (row.overhangRatioPct > 5) {
      return <span className="inline-block rounded px-2 py-1 text-xs font-semibold bg-[rgb(220,38,38)] text-white">Fail</span>;
    }
    if (row.overhangRatioPct > 1) {
      return <span className="inline-block rounded px-2 py-1 text-xs font-semibold bg-[rgb(245,158,11)] text-black">Warn</span>;
    }
    return <span className="inline-block rounded px-2 py-1 text-xs font-semibold bg-[rgb(34,197,94)] text-white">Pass</span>;
  }

  if (loading) {
    return (
      <Card className="animate-in">
        <div className="p-5 text-sm text-[rgb(var(--muted))]">Loading overhang/underhang table...</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="animate-in">
        <div className="p-5">
          <div className="text-sm font-semibold text-[rgb(var(--muted))]">Overhang & Underhang Analysis</div>
          <div className="mt-2 text-sm text-[rgb(var(--muted))]">{error}</div>
        </div>
      </Card>
    );
  }

  if (rows.length === 0) {
    return (
      <Card className="animate-in">
        <div className="p-5">
          <div className="text-sm font-semibold text-[rgb(var(--muted))]">Overhang & Underhang Analysis</div>
          <div className="mt-2 text-sm text-[rgb(var(--muted))]">No placement data available for analysis.</div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden animate-in">
      <div className="p-5 border-b border-[rgb(var(--line))]">
        <h2 className="text-sm uppercase tracking-[0.18em] text-[rgb(var(--muted))]">Overhang & Underhang Analysis</h2>
        <p className="mt-2 text-xs text-[rgb(var(--muted))]">
          Per-case placement validation: red = outside or exceeds limit, yellow = warning, green = pass.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="data-table w-full border-collapse text-sm">
          <thead className="bg-[rgb(var(--panel2))]">
            <tr className="border-b border-[rgb(var(--line))]">
              <th className="px-3 py-3 text-left text-xs font-semibold text-[rgb(var(--muted))]">Case</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-[rgb(var(--muted))]">Left</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-[rgb(var(--muted))]">Right</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-[rgb(var(--muted))]">Front</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-[rgb(var(--muted))]">Back</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-[rgb(var(--muted))]">OH Ratio %</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-[rgb(var(--muted))]">UH Impact %</th>
              <th className="px-3 py-3 text-center text-xs font-semibold text-[rgb(var(--muted))]">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr
                key={idx}
                className={`data-table-row border-b border-[rgb(var(--line))] transition-colors ${getRowColor(row)}`}
              >
                <td className="px-3 py-2 text-sm font-medium">{row.caseId}</td>
                <td className="px-3 py-2 text-right text-sm">{row.left.toFixed(1)}</td>
                <td className="px-3 py-2 text-right text-sm">{row.right.toFixed(1)}</td>
                <td className="px-3 py-2 text-right text-sm">{row.front.toFixed(1)}</td>
                <td className="px-3 py-2 text-right text-sm">{row.back.toFixed(1)}</td>
                <td className={`px-3 py-2 text-right text-sm font-semibold ${
                  row.overhangRatioPct > 5 ? 'text-[rgb(220,38,38)]' : 
                  row.overhangRatioPct > 1 ? 'text-[rgb(245,158,11)]' : 
                  'text-[rgb(34,197,94)]'
                }`}>
                  {row.overhangRatioPct.toFixed(2)}%
                </td>
                <td className={`px-3 py-2 text-right text-sm ${
                  row.underhangImpactPct > 20 ? 'text-[rgb(245,158,11)]' : 'text-[rgb(var(--text))]'
                }`}>
                  {row.underhangImpactPct.toFixed(2)}%
                </td>
                <td className="px-3 py-2 text-center">{getStatusBadge(row)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totals && (
        <div className="border-t border-[rgb(var(--line))] bg-[rgb(var(--panel2))] p-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <div className="text-xs text-[rgb(var(--muted))]">Total Overhang Area</div>
              <div className="mt-1 text-sm font-semibold">{totals.totalOverhangArea.toFixed(2)} mm²</div>
            </div>
            <div>
              <div className="text-xs text-[rgb(var(--muted))]">Layout Underhang Ratio</div>
              <div className="mt-1 text-sm font-semibold">{(totals.layoutUnderhangRatio * 100).toFixed(2)}%</div>
            </div>
            <div>
              <div className="text-xs text-[rgb(var(--muted))]">Pallet Utilization</div>
              <div className="mt-1 text-sm font-semibold text-[rgb(34,197,94)]">{(totals.palletUtilization * 100).toFixed(2)}%</div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}

function parseMarkdownTable(markdown: string): {
  rows: OverhangUnderhangRow[];
  totals: { totalOverhangArea: number; layoutUnderhangRatio: number; palletUtilization: number } | null;
} {
  const lines = markdown.split("\n");
  const rows: OverhangUnderhangRow[] = [];
  let totals: { totalOverhangArea: number; layoutUnderhangRatio: number; palletUtilization: number } | null = null;

  let inTable = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.startsWith("| Case |")) {
      inTable = true;
      continue;
    }

    if (inTable && line.startsWith("|")) {
      if (line.includes("---")) continue;

      const cells = line.split("|").map((c) => c.trim()).filter((c) => c.length > 0);
      if (cells.length >= 8) {
        rows.push({
          caseId: cells[0],
          left: parseFloat(cells[1]) || 0,
          right: parseFloat(cells[2]) || 0,
          front: parseFloat(cells[3]) || 0,
          back: parseFloat(cells[4]) || 0,
          ohLeft: parseFloat(cells[5]) || 0,
          ohRight: parseFloat(cells[6]) || 0,
          ohFront: parseFloat(cells[7]) || 0,
          ohBack: parseFloat(cells[8]) || 0,
          overhangRatioPct: parseFloat(cells[9]) || 0,
          underhangImpactPct: parseFloat(cells[10]) || 0,
          valid: cells[11] === "yes" ? "yes" : "no",
        });
      }
    }

    if (line.includes("Total overhang area")) {
      const match = line.match(/(\d+\.?\d*)\s*mm²/);
      if (match && !totals) {
        totals = { totalOverhangArea: parseFloat(match[1]) || 0, layoutUnderhangRatio: 0, palletUtilization: 0 };
      }
    }

    if (line.includes("Layout underhang ratio")) {
      const match = line.match(/(\d+\.?\d*)%/);
      if (match && totals) {
        totals.layoutUnderhangRatio = parseFloat(match[1]) / 100 || 0;
      }
    }

    if (line.includes("Pallet utilization")) {
      const match = line.match(/(\d+\.?\d*)%/);
      if (match && totals) {
        totals.palletUtilization = parseFloat(match[1]) / 100 || 0;
      }
    }
  }

  return { rows, totals };
}
