import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Home } from "./Home";

const navigateMock = vi.fn();
const postSolveMock = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

vi.mock("../api/endpoints", () => ({
  postSolve: (...args: unknown[]) => postSolveMock(...args),
}));

describe("Home page", () => {
  beforeEach(() => {
    navigateMock.mockReset();
    postSolveMock.mockReset();
  });

  it("disables submit when required values are invalid", () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    const button = screen.getByRole("button", { name: "Get Started" });
    expect(button).toBeDisabled();
  });

  it("submits solve and navigates to run route", async () => {
    postSolveMock.mockResolvedValue({ run_id: "R0001_20260417" });

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );

    fireEvent.change(screen.getAllByLabelText(/Length/i)[0], { target: { value: "300" } });
    fireEvent.change(screen.getAllByLabelText(/Width/i)[0], { target: { value: "200" } });
    fireEvent.change(screen.getAllByLabelText(/Height/i)[0], { target: { value: "150" } });

    fireEvent.click(screen.getAllByRole("button", { name: "Get Started" })[0]);

    await waitFor(() => expect(postSolveMock).toHaveBeenCalledTimes(1));
    expect(navigateMock).toHaveBeenCalledWith("/runs/R0001_20260417", { state: { summaryPending: true } });
  });
});
