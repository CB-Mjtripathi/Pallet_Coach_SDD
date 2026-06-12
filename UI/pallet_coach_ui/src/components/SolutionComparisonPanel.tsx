import type { Bundle, WeightUnit } from "../api/types";
import { convertWeight, formatPatternLabel } from "../lib/formatters";
import { Card } from "./ui/Card";

interface SolutionComparisonPanelProps {
  bundle: Bundle;
  weightUnit: WeightUnit;
}

export function SolutionComparisonPanel({ bundle, weightUnit }: SolutionComparisonPanelProps): JSX.Element | null {
  const solutions = bundle.recommender.solutions;
  if (!solutions || solutions.length < 2) {
    return null;
  }

  const best = solutions[0];
  const runnerUp = solutions[1];

  const isMixedBest = best.solution_id === "mixed_irregular_opt";
  const isGridRunnerUp = runnerUp.solution_id.startsWith("grid_");

  if (!isMixedBest || !isGridRunnerUp) {
    return null;
  }

  const bestMetrics = best.metrics;
  const runnerUpMetrics = runnerUp.metrics;

  const casesDiff = bestMetrics.cases_per_layer - runnerUpMetrics.cases_per_layer;
  const efficiencyDiff = bestMetrics.area_fill_efficiency_pct - runnerUpMetrics.area_fill_efficiency_pct;

  return (
    <Card className="overflow-hidden animate-in">
      <div className="bg-gradient-to-r from-[rgb(var(--accent))] to-[rgb(var(--accent-dim))] px-5 py-4">
        <h3 className="text-sm font-semibold text-white">Mixed-Pattern Optimization</h3>
        <p className="mt-1 text-xs text-white/80">
          The mixed-orientation layout outperforms traditional grid patterns on your case geometry.
        </p>
      </div>

      <div className="grid grid-cols-2 divide-x divide-[rgb(var(--line))]">
        {/* Best Solution (Mixed) */}
        <div className="bg-[rgb(var(--panel))] px-5 py-4">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[rgb(var(--success))]">
              <span className="text-xs font-bold text-white">✓</span>
            </div>
            <h4 className="text-sm font-semibold">New: {formatPatternLabel(best.solution_id)}</h4>
          </div>
          <table className="w-full text-xs">
            <tbody>
              <tr className="border-b border-[rgb(var(--line))]">
                <td className="py-1 text-[rgb(var(--muted))]">Cases / layer</td>
                <td className="py-1 text-right font-semibold">{bestMetrics.cases_per_layer}</td>
              </tr>
              <tr className="border-b border-[rgb(var(--line))]">
                <td className="py-1 text-[rgb(var(--muted))]">Total cases</td>
                <td className="py-1 text-right font-semibold">{bestMetrics.total_cases}</td>
              </tr>
              <tr className="border-b border-[rgb(var(--line))]">
                <td className="py-1 text-[rgb(var(--muted))]">Area fill %</td>
                <td className="py-1 text-right font-semibold">{bestMetrics.area_fill_efficiency_pct.toFixed(1)}%</td>
              </tr>
              <tr>
                <td className="py-1 text-[rgb(var(--muted))]">Height (mm)</td>
                <td className="py-1 text-right font-semibold">{bestMetrics.total_height_mm}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Runner-Up Solution (Grid) */}
        <div className="bg-[rgb(var(--panel2))] px-5 py-4">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[rgb(var(--muted))]">
              <span className="text-xs font-bold text-white">2</span>
            </div>
            <h4 className="text-sm font-semibold">Previous: {formatPatternLabel(runnerUp.solution_id)}</h4>
          </div>
          <table className="w-full text-xs">
            <tbody>
              <tr className="border-b border-[rgb(var(--line))]">
                <td className="py-1 text-[rgb(var(--muted))]">Cases / layer</td>
                <td className="py-1 text-right font-semibold">{runnerUpMetrics.cases_per_layer}</td>
              </tr>
              <tr className="border-b border-[rgb(var(--line))]">
                <td className="py-1 text-[rgb(var(--muted))]">Total cases</td>
                <td className="py-1 text-right font-semibold">{runnerUpMetrics.total_cases}</td>
              </tr>
              <tr className="border-b border-[rgb(var(--line))]">
                <td className="py-1 text-[rgb(var(--muted))]">Area fill %</td>
                <td className="py-1 text-right font-semibold">{runnerUpMetrics.area_fill_efficiency_pct.toFixed(1)}%</td>
              </tr>
              <tr>
                <td className="py-1 text-[rgb(var(--muted))]">Height (mm)</td>
                <td className="py-1 text-right font-semibold">{runnerUpMetrics.total_height_mm}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="border-t border-[rgb(var(--line))] bg-[rgb(var(--panel))] px-5 py-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-[rgb(var(--muted))]">Cases improvement</p>
            <p className="text-lg font-bold text-[rgb(var(--success))]">
              +{casesDiff} <span className="text-xs text-[rgb(var(--muted))]">per layer</span>
            </p>
          </div>
          <div>
            <p className="text-xs text-[rgb(var(--muted))]">Efficiency gain</p>
            <p className="text-lg font-bold text-[rgb(var(--success))]">
              +{efficiencyDiff.toFixed(1)}% <span className="text-xs text-[rgb(var(--muted))]">fill</span>
            </p>
          </div>
        </div>
        <p className="mt-3 text-xs leading-relaxed text-[rgb(var(--muted))]">
          The mixed-orientation layout combines rotated and non-rotated cases in a single layer, achieving higher packing density than
          traditional grid patterns. This is computed by searching all feasible placement positions within tolerance rules.
        </p>
      </div>
    </Card>
  );
}
