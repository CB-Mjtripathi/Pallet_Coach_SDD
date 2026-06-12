import { Button } from "./ui/Button";
import { Card } from "./ui/Card";

interface DiagramCarouselProps {
  runId: string;
  activeTab: "flat" | "3d" | "isometric";
  onChangeTab: (tab: "flat" | "3d" | "isometric") => void;
  onGenerate: (view: "flat" | "3d") => void;
  loadingView: "flat" | "3d" | null;
}

export function DiagramCarousel({
  runId,
  activeTab,
  onChangeTab,
  onGenerate,
  loadingView,
}: DiagramCarouselProps): JSX.Element {
  const deterministicFile =
    activeTab === "flat"
      ? "comparison_flat.png"
      : activeTab === "3d"
        ? "comparison_3d.png"
        : "isometric_exploded_3d.png";
  const canGenerateAi = activeTab !== "isometric";

  return (
    <Card className="p-5 animate-in animate-delay-2">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex gap-2">
          <Button variant={activeTab === "flat" ? "primary" : "secondary"} onClick={() => onChangeTab("flat")}>
            Flat comparison
          </Button>
          <Button variant={activeTab === "3d" ? "primary" : "secondary"} onClick={() => onChangeTab("3d")}>
            3D view
          </Button>
          <Button
            variant={activeTab === "isometric" ? "primary" : "secondary"}
            onClick={() => onChangeTab("isometric")}
          >
            Isometric exploded
          </Button>
        </div>
        <Button onClick={() => onGenerate(activeTab === "flat" ? "flat" : "3d")} disabled={loadingView !== null || !canGenerateAi}>
          {loadingView === activeTab ? "Generating" : "Generate AI diagram"}
        </Button>
      </div>
      <img
        src={`/output/${runId}/${deterministicFile}`}
        alt={`Deterministic ${activeTab} diagram`}
        className="w-full rounded-sm border border-[rgb(var(--line))]"
      />
    </Card>
  );
}
