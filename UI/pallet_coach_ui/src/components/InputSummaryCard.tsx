import type { Bundle } from "../api/types";
import { Card } from "./ui/Card";

interface InputSummaryCardProps {
  bundle: Bundle;
}

export function InputSummaryCard({ bundle }: InputSummaryCardProps): JSX.Element {
  const req = bundle.request;
  return (
    <Card className="p-5 text-sm">
      <h3 className="mb-3 text-xs uppercase tracking-[0.16em] text-[rgb(var(--muted))]">Input Summary</h3>
      <div className="grid gap-2 sm:grid-cols-2">
        <Info label="Pallet" value={`${req.pallet.type} (${req.pallet.length_mm}x${req.pallet.width_mm} mm)`} />
        <Info label="Case" value={`${req.case.length_mm}x${req.case.width_mm}x${req.case.height_mm} mm`} />
        <Info label="Layers" value={`${req.stack.layer_count}`} />
        <Info
          label="Tolerances"
          value={`${req.tolerances.max_overhang_l_mm}/${req.tolerances.max_overhang_w_mm}/${req.tolerances.max_underhang_l_mm}/${req.tolerances.max_underhang_w_mm}`}
        />
      </div>
    </Card>
  );
}

function Info({ label, value }: { label: string; value: string }): JSX.Element {
  return (
    <div>
      <div className="text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">{label}</div>
      <div className="table-num">{value}</div>
    </div>
  );
}
