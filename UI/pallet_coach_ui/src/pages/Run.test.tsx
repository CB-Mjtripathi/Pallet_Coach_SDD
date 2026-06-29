import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Run } from "./Run";

const getBundleMock = vi.fn();
const getLogsMock = vi.fn();
const postSummaryUiMock = vi.fn();
const postDiagramMock = vi.fn();
const artifactExistsMock = vi.fn();

vi.mock("../api/endpoints", () => ({
  getBundle: (...args: unknown[]) => getBundleMock(...args),
  getLogs: (...args: unknown[]) => getLogsMock(...args),
  postSummaryUi: (...args: unknown[]) => postSummaryUiMock(...args),
  postDiagram: (...args: unknown[]) => postDiagramMock(...args),
  artifactExists: (...args: unknown[]) => artifactExistsMock(...args),
}));

vi.mock("../lib/exportZip", () => ({
  downloadRunBundleZip: vi.fn(),
}));

describe("Run page", () => {
  beforeEach(() => {
    getBundleMock.mockReset();
    getLogsMock.mockReset();
    postSummaryUiMock.mockReset();
    postDiagramMock.mockReset();
    artifactExistsMock.mockReset();

    getBundleMock.mockResolvedValue({
      run_id: "R0001_20260417",
      request: {
        pallet: { type: "euro", length_mm: 1200, width_mm: 800 },
        case: { length_mm: 300, width_mm: 200, height_mm: 150 },
        stack: { layer_count: 8 },
        tolerances: {
          max_overhang_l_mm: 0,
          max_overhang_w_mm: 0,
          max_underhang_l_mm: 0,
          max_underhang_w_mm: 0,
        },
      },
      recommender: {
        status: "ok",
        reasons: [],
        solutions: [
          {
            solution_id: "grid_4x3_rot0",
            layout: [
              { x_mm: 0, y_mm: 0, rotation_deg: 0, dim_x_mm: 300, dim_y_mm: 200 },
              { x_mm: 300, y_mm: 0, rotation_deg: 0, dim_x_mm: 300, dim_y_mm: 200 },
            ],
            metrics: {
              cases_per_layer: 12,
              total_cases: 96,
              total_height_mm: 1344,
              total_weight_kg: 200,
              area_fill_efficiency_pct: 75,
              interlock: false,
            },
          },
          {
            solution_id: "mixed_irregular_opt",
            layout: [
              { x_mm: 0, y_mm: 0, rotation_deg: 90, dim_x_mm: 200, dim_y_mm: 300 },
              { x_mm: 200, y_mm: 0, rotation_deg: 0, dim_x_mm: 300, dim_y_mm: 200 },
            ],
            metrics: {
              cases_per_layer: 13,
              total_cases: 104,
              total_height_mm: 1344,
              total_weight_kg: 200,
              area_fill_efficiency_pct: 80,
              interlock: false,
            },
          },
        ],
      },
      stacking: {
        max_stack_height_mm: 2000,
        pallet_height_mm: 144,
        current_stack_height_mm: 1344,
        headroom_mm: 656,
        current_layers: 8,
        max_layers_at_max_height: 12,
        addable_layers_to_max_height: 4,
        recommended_layers_range: { min: 9, max: 11 },
      },
      artifacts: {
        summary_ui: { path: "summary_ui.md" },
      },
    });

    getLogsMock.mockResolvedValue("log line");
    artifactExistsMock.mockResolvedValue(true);

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => "summary markdown",
    }) as unknown as typeof fetch;
  });

  it("renders run details from bundle", async () => {
    render(
      <MemoryRouter initialEntries={["/runs/R0001_20260417"]}>
        <Routes>
          <Route path="/runs/:runId" element={<Run />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(getBundleMock).toHaveBeenCalled());
    expect(screen.getByText("R0001_20260417")).toBeInTheDocument();
    expect(screen.getByText(/Input Summary/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /isometric exploded/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /show json/i })).toBeInTheDocument();
    expect(screen.getByText(/recommended layers/i)).toBeInTheDocument();
  });

  it("hides JSON by default and toggles on demand", async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={["/runs/R0001_20260417"]}>
        <Routes>
          <Route path="/runs/:runId" element={<Run />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(getBundleMock).toHaveBeenCalled());
    expect(screen.queryByText(/"run_id"/i)).not.toBeInTheDocument();

    const showButtons = screen.getAllByRole("button", { name: /show json/i });
    await user.click(showButtons[0]);
    expect(screen.getByText(/"run_id": "R0001_20260417"/i)).toBeInTheDocument();

    const hideButtons = screen.getAllByRole("button", { name: /hide json/i });
    await user.click(hideButtons[0]);
    expect(screen.queryByText(/"run_id": "R0001_20260417"/i)).not.toBeInTheDocument();
  });

  it("auto-generates summary after navigation when requested", async () => {
    postSummaryUiMock.mockResolvedValue({ summary_markdown: "generated summary" });
    artifactExistsMock.mockResolvedValue(false);

    render(
      <MemoryRouter initialEntries={[{ pathname: "/runs/R0001_20260417", state: { summaryPending: true } }] }>
        <Routes>
          <Route path="/runs/:runId" element={<Run />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(postSummaryUiMock).toHaveBeenCalledWith("R0001_20260417", false));
    expect(screen.getByText(/generated summary/i)).toBeInTheDocument();
  });

  it("prevents duplicate in-flight regenerate calls", async () => {
    const user = userEvent.setup();
    let resolveSummary: ((value: { summary_markdown: string }) => void) | null = null;
    postSummaryUiMock.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSummary = resolve;
        })
    );

    render(
      <MemoryRouter initialEntries={["/runs/R0001_20260417"]}>
        <Routes>
          <Route path="/runs/:runId" element={<Run />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(getBundleMock).toHaveBeenCalled());

    const regenerate = screen.getAllByRole("button", { name: /^regenerate$/i })[0];
    await user.click(regenerate);
    await user.click(regenerate);

    expect(postSummaryUiMock).toHaveBeenCalledTimes(1);
    expect(postSummaryUiMock).toHaveBeenCalledWith("R0001_20260417", true);

    resolveSummary?.({ summary_markdown: "done" });
    await waitFor(() => expect(screen.getByText(/done/i)).toBeInTheDocument());
  });

  it("keeps run page actions non-blocking while summary is in flight", async () => {
    const user = userEvent.setup();
    postSummaryUiMock.mockImplementation(() => new Promise(() => {}));
    postDiagramMock.mockResolvedValue({ diagram_path: "diagram_flat.png" });

    render(
      <MemoryRouter initialEntries={["/runs/R0001_20260417"]}>
        <Routes>
          <Route path="/runs/:runId" element={<Run />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(getBundleMock).toHaveBeenCalled());

    await user.click(screen.getAllByRole("button", { name: /^regenerate$/i })[0]);
    const diagramButton = screen.getAllByRole("button", { name: /generate flat ai diagram/i })[0];
    expect(diagramButton).toBeEnabled();

    await user.click(diagramButton);
    await waitFor(() => expect(postDiagramMock).toHaveBeenCalledWith("R0001_20260417", "flat"));
  });
});
