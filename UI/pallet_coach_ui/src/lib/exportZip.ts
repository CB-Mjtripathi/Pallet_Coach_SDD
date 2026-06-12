import JSZip from "jszip";
import { saveAs } from "file-saver";
import type { Bundle } from "../api/types";
import { downloadArtifact } from "../api/endpoints";

export async function downloadRunBundleZip(runId: string, bundle: Bundle): Promise<void> {
  const zip = new JSZip();
  const artifacts = Object.values(bundle.artifacts).map((entry) => entry.path);

  for (const artifact of artifacts) {
    try {
      const blob = await downloadArtifact(runId, artifact);
      zip.file(artifact, blob);
    } catch {
      // Skip missing artifacts so export still succeeds with available files.
    }
  }

  const output = await zip.generateAsync({ type: "blob" });
  saveAs(output, `${runId}.zip`);
}
