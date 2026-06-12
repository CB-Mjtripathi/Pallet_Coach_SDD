import type { Bundle, WeightUnit } from "../api/types";
import { convertWeight, formatInterlock, formatPatternLabel } from "../lib/formatters";
import { Card } from "./ui/Card";

interface OptionsTableProps {
  bundle: Bundle;
  weightUnit: WeightUnit;
}

export function OptionsTable({ bundle, weightUnit }: OptionsTableProps): JSX.Element {
  const solutions = bundle.recommender.solutions.slice(0, 5);

  return (
    <Card className="overflow-hidden animate-in animate-delay-3">
      <table className="data-table w-full border-collapse bg-[rgb(var(--panel2))]">
        <thead className="data-table-head border-b border-[rgb(var(--line))] bg-[rgba(var(--panel),0.5)] text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">
          <tr>
            <th className="px-4 py-3 text-left">Rank</th>
            <th className="px-4 py-3 text-left">Pattern</th>
            <th className="px-4 py-3 text-left">Interlock</th>
            <th className="px-4 py-3 text-right">Cases/Layer</th>
            <th className="px-4 py-3 text-right">Total Layers</th>
            <th className="px-4 py-3 text-right">Total Cases</th>
            <th className="px-4 py-3 text-right">Total Weight</th>
            <th className="px-4 py-3 text-right">Eff %</th>
            <th className="px-4 py-3 text-right">Total Height</th>
          </tr>
        </thead>
        <tbody>
          {solutions.map((solution, index) => {
            const metrics = solution.metrics;
            const totalLayers = Math.round(metrics.total_cases / Math.max(1, metrics.cases_per_layer));
            return (
              <tr key={solution.solution_id} className="data-table-row border-b border-[rgb(var(--line))] text-sm">
                <td className="px-4 py-3">{index + 1}</td>
                <td className="px-4 py-3">{formatPatternLabel(solution.solution_id)}</td>
                <td className="px-4 py-3">{formatInterlock(metrics.interlock)}</td>
                <td className="table-num px-4 py-3 text-right">{metrics.cases_per_layer}</td>
                <td className="table-num px-4 py-3 text-right">{totalLayers}</td>
                <td className="table-num px-4 py-3 text-right">{metrics.total_cases}</td>
                <td className="table-num px-4 py-3 text-right">
                  {convertWeight(metrics.total_weight_kg ?? null, weightUnit)}
                </td>
                <td className="table-num px-4 py-3 text-right">{metrics.area_fill_efficiency_pct.toFixed(1)}</td>
                <td className="table-num px-4 py-3 text-right">{metrics.total_height_mm} mm</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </Card>
  );
}
