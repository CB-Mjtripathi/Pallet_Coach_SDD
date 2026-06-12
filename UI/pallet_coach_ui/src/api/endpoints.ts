import { apiFetch, apiText } from "./client";
import type { Bundle, SolvePayload, SolveResponse } from "./types";

export function postSolve(payload: SolvePayload): Promise<SolveResponse> {
  return apiFetch<SolveResponse>("/api/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function postSummaryUi(runId: string, force = false): Promise<{ summary_markdown: string }> {
  return apiFetch<{ summary_markdown: string }>("/api/summary_ui", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, style: "detailed", force }),
  });
}

export function postDiagram(runId: string, view: "flat" | "3d"): Promise<{ diagram_path: string }> {
  return apiFetch<{ diagram_path: string }>("/api/diagram", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, view }),
  });
}

export function getBundle(runId: string): Promise<Bundle> {
  return apiFetch<Bundle>(`/api/runs/${runId}`);
}

export function getLogs(runId: string): Promise<string> {
  return apiText(`/api/runs/${runId}/logs`);
}

export async function artifactExists(runId: string, filename: string): Promise<boolean> {
  const response = await fetch(`/output/${runId}/${filename}`, { method: "HEAD" });
  return response.ok;
}

export async function downloadArtifact(runId: string, filename: string): Promise<Blob> {
  const response = await fetch(`/output/${runId}/${filename}`);
  if (!response.ok) {
    throw new Error(`Failed to download ${filename}`);
  }
  return response.blob();
}
