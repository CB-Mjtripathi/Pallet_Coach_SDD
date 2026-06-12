import type { Bundle } from "../api/types";
import { Card } from "./ui/Card";

interface StackingTableProps {
  bundle: Bundle;
}

export function StackingTable({ bundle }: StackingTableProps): JSX.Element {
  const s = bundle.stacking;
  const caseHeightMm = bundle.request.case.height_mm;
  const recMax = s.recommended_layers_range.max;
  const recMaxHeight = s.pallet_height_mm + recMax * caseHeightMm;
  const weightCeiling = s.weight_ceiling_layers_conservative ?? s.weight_ceiling_layers ?? null;

  return (
    <Card className="overflow-hidden animate-in animate-delay-4">
      <table className="data-table w-full border-collapse bg-[rgb(var(--panel2))] text-sm">
        <tbody>
          <Row label="Max stack height" value={`${s.max_stack_height_mm} mm`} />
          <Row label="Pallet height" value={`${s.pallet_height_mm} mm`} />
          <Row label="Current stack height" value={`${s.current_stack_height_mm} mm`} />
          <Row label="Headroom" value={`${s.headroom_mm} mm`} />
          <Row label="Current Layers" value={`${s.current_layers}`} />
          <Row label="Max layers at cap" value={`${s.max_layers_at_max_height}`} />
          <Row label="Addable layers" value={`${s.addable_layers_to_max_height}`} />
          <Row label="Weight ceiling (layers)" value={weightCeiling === null ? "n/a" : `${weightCeiling}`} />
          <Row label="Recommended range" value={`${s.recommended_layers_range.min}..${s.recommended_layers_range.max} layers`} />
          <Row label="Height at recommended max" value={`${recMaxHeight} mm`} />
        </tbody>
      </table>
    </Card>
  );
}

function Row({ label, value }: { label: string; value: string }): JSX.Element {
  return (
    <tr className="data-table-row border-b border-[rgb(var(--line))]">
      <td className="px-4 py-3 text-[rgb(var(--muted))]">{label}</td>
      <td className="table-num px-4 py-3 text-right">{value}</td>
    </tr>
  );
}
