import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { formatApiError } from "../api/client";
import { artifactExists, getBundle, getLogs, postDiagram, postSummaryUi } from "../api/endpoints";
import type { Bundle, WeightUnit } from "../api/types";
import { DiagramCarousel } from "../components/DiagramCarousel";
import { InputSummaryCard } from "../components/InputSummaryCard";
import { LogsPanel } from "../components/LogsPanel";
import { OptionsTable } from "../components/OptionsTable";
import { OverhangUnderhangPanel } from "../components/OverhangUnderhangPanel";
import { PalletDigitalTwin3D } from "../components/PalletDigitalTwin3D";
import { SolutionComparisonPanel } from "../components/SolutionComparisonPanel";
import { StackingTable } from "../components/StackingTable";
import { SummaryPanel } from "../components/SummaryPanel";
import { Button } from "../components/ui/Button";
import { SelectInput } from "../components/ui/SelectInput";
import { downloadRunBundleZip } from "../lib/exportZip";

interface RouterState {
  summaryWarning?: string;
  summaryPending?: boolean;
}

export function Run(): JSX.Element {
  const { runId = "" } = useParams();
  const location = useLocation();
  const state = (location.state ?? {}) as RouterState;

  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [logs, setLogs] = useState("");
  const [summaryMarkdown, setSummaryMarkdown] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"flat" | "3d" | "isometric">("flat");
  const [weightUnit, setWeightUnit] = useState<WeightUnit>("kg");
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingView, setLoadingView] = useState<"flat" | "3d" | null>(null);
  const [showJsonDetails, setShowJsonDetails] = useState(false);
  const [warning, setWarning] = useState<string | null>(state.summaryWarning ?? null);
  const [bundleError, setBundleError] = useState<string | null>(null);
  const [summaryPending, setSummaryPending] = useState(Boolean(state.summaryPending));

  async function refreshData(): Promise<void> {
    setBundleError(null);
    const bundlePromise = getBundle(runId);
    const logsPromise = getLogs(runId).catch(() => "");

    const data = await bundlePromise;
    setBundle(data);
    setLogs(await logsPromise);

    const summaryPath = data.artifacts?.summary_ui?.path ?? null;
    if (summaryPath) {
      try {
        const summaryOk = await artifactExists(runId, summaryPath);
        if (summaryOk) {
          const response = await fetch(`/output/${runId}/${summaryPath}`);
          setSummaryMarkdown(await response.text());
        } else {
          setSummaryMarkdown("");
        }
      } catch (err) {
        setSummaryMarkdown("");
        setWarning(err instanceof Error ? err.message : "Failed to load summary artifact");
      }
    } else {
      setSummaryMarkdown("");
    }
  }

  useEffect(() => {
    if (!runId) {
      return;
    }
    refreshData().catch((err: Error) => {
      setBundleError(formatApiError(err, "Failed to load run data"));
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  useEffect(() => {
    if (!runId || !bundle || !summaryPending || summaryMarkdown) {
      return;
    }

    let cancelled = false;
    setSummaryPending(false);
    setLoadingSummary(true);

    postSummaryUi(runId, false)
      .then((response) => {
        if (!cancelled) {
          setSummaryMarkdown(response.summary_markdown);
          setWarning(null);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setWarning(formatApiError(err, "Failed to generate summary"));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingSummary(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [bundle, runId, summaryMarkdown, summaryPending]);

  async function onRegenerateSummary(): Promise<void> {
    setLoadingSummary(true);
    try {
      const response = await postSummaryUi(runId, true);
      setSummaryMarkdown(response.summary_markdown);
      setWarning(null);
    } catch (err) {
      setWarning(formatApiError(err, "Failed to regenerate summary"));
    } finally {
      setLoadingSummary(false);
    }
  }

  async function onGenerateDiagram(view: "flat" | "3d"): Promise<void> {
    setLoadingView(view);
    try {
      await postDiagram(runId, view);
      await refreshData();
    } catch (err) {
      setWarning(formatApiError(err, "Failed to generate AI diagram"));
    } finally {
      setLoadingView(null);
    }
  }

  if (!runId) {
    return <p className="text-sm text-[rgb(var(--muted))]">Missing run id.</p>;
  }

  if (!bundle) {
    if (bundleError) {
      return (
        <div className="space-y-4">
          <p className="text-sm font-semibold text-[rgb(var(--danger))]">Failed to load run data</p>
          <p className="text-sm text-[rgb(var(--muted))]">{bundleError}</p>
          <p className="text-sm text-[rgb(var(--muted))]">Make sure the API server is running on port 8000, then refresh the page.</p>
          <Link to="/" className="text-sm text-[rgb(var(--accent))]">← Back to Home</Link>
        </div>
      );
    }
    return <p className="text-sm text-[rgb(var(--muted))]">Loading run data...</p>;
  }

  const status = bundle.recommender?.status ?? "unknown";
  const topSolution = bundle.recommender.solutions[0];

  return (
    <div className="space-y-6">
      <header className="animate-in">
        <div className="flex items-start justify-between gap-6">
          <div>
            <div className="summary-kicker">Run</div>
            <h1 className="mt-3 text-4xl leading-[1.05] tracking-tight">{bundle.run_id}</h1>
            <p className="mt-3 max-w-2xl text-sm text-[rgb(var(--muted))]">
              Review the best recommendation, compare diagrams, and inspect solver output artifacts for this run.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <SelectInput className="w-32" value={weightUnit} onChange={(e) => setWeightUnit(e.target.value as WeightUnit)}>
              <option value="kg">kg</option>
              <option value="lbs">lbs</option>
            </SelectInput>
            <Button variant="primary" onClick={() => downloadRunBundleZip(runId, bundle)}>
              Download bundle
            </Button>
          </div>
        </div>

        <div className="run-meta-grid mt-6">
          <div className="metric-tile">
            <div className="metric-label">Status</div>
            <div className="metric-value">{status}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">Best cases / layer</div>
            <div className="metric-value">{topSolution?.metrics.cases_per_layer ?? "-"}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">Top fill %</div>
            <div className="metric-value">
              {typeof topSolution?.metrics.area_fill_efficiency_pct === "number"
                ? topSolution.metrics.area_fill_efficiency_pct.toFixed(1)
                : "-"}
            </div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">Recommended layers</div>
            <div className="metric-value">
              {bundle.stacking.recommended_layers_range.min}..{bundle.stacking.recommended_layers_range.max}
            </div>
          </div>
        </div>
      </header>

      {warning ? <p className="text-sm text-[rgb(var(--danger))]">{warning}</p> : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
        <div>
          {summaryMarkdown ? (
            <SummaryPanel markdown={summaryMarkdown} loading={loadingSummary} onRegenerate={onRegenerateSummary} />
          ) : (
            <section className="card p-5 animate-in animate-delay-1">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm uppercase tracking-[0.18em] text-[rgb(var(--muted))]">AI Summary</h2>
                <Button variant="primary" onClick={onRegenerateSummary} disabled={loadingSummary}>
                  {loadingSummary ? "Regenerating" : "Generate"}
                </Button>
              </div>
              <p className="text-sm text-[rgb(var(--muted))]">No UI summary artifact is available for this run yet.</p>
            </section>
          )}
        </div>
        <div className="space-y-6">
          <section className="card p-5 animate-in animate-delay-2">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))]">Navigation</h2>
              <Link to="/" className="text-sm text-[rgb(var(--accent))]">
                Back to Home
              </Link>
            </div>
            <p className="text-sm text-[rgb(var(--muted))]">
              Switch diagram views, validate stack guidance, and export the artifact bundle from this run workspace.
            </p>
          </section>
          <InputSummaryCard bundle={bundle} />
        </div>
      </div>

      <DiagramCarousel
        runId={runId}
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        onGenerate={onGenerateDiagram}
        loadingView={loadingView}
      />

      <PalletDigitalTwin3D bundle={bundle} />

      <SolutionComparisonPanel bundle={bundle} weightUnit={weightUnit} />

      <OverhangUnderhangPanel bundle={bundle} runId={runId} />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
        <div>
          <OptionsTable bundle={bundle} weightUnit={weightUnit} />
        </div>
        <div className="space-y-6">
          <StackingTable bundle={bundle} />
          <section className="card p-5 animate-in animate-delay-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-xs uppercase tracking-[0.16em] text-[rgb(var(--muted))]">Actions</h3>
            </div>
            <div className="grid gap-3">
              <Button variant="secondary" onClick={onRegenerateSummary} disabled={loadingSummary}>
                {loadingSummary ? "Regenerating summary" : "Regenerate summary"}
              </Button>
              <Button variant="secondary" onClick={() => onGenerateDiagram("flat")} disabled={loadingView !== null}>
                {loadingView === "flat" ? "Generating flat" : "Generate flat AI diagram"}
              </Button>
              <Button variant="secondary" onClick={() => onGenerateDiagram("3d")} disabled={loadingView !== null}>
                {loadingView === "3d" ? "Generating 3D" : "Generate 3D AI diagram"}
              </Button>
            </div>
          </section>
        </div>
      </div>

      <section className="card p-5">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-xs uppercase tracking-[0.16em] text-[rgb(var(--muted))]">Run JSON Details</h3>
          <Button variant="secondary" onClick={() => setShowJsonDetails((prev) => !prev)}>
            {showJsonDetails ? "Hide JSON" : "Show JSON"}
          </Button>
        </div>
        {showJsonDetails ? (
          <pre className="max-h-[480px] overflow-auto rounded-sm border border-[rgb(var(--line))] bg-[rgb(var(--panel))] p-3 text-xs text-[rgb(var(--text))]">
            {JSON.stringify(bundle, null, 2)}
          </pre>
        ) : null}
      </section>

      <LogsPanel logs={logs} />
    </div>
  );
}
