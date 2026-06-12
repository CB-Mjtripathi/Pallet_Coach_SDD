from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    request: dict[str, Any]
    max_solutions: int = Field(default=25, ge=1, le=250)
    include_timestamp: bool = True


class SolveResponse(BaseModel):
    run_id: str
    out_dir: str
    solver_status: str
    best_metrics: dict[str, Any] | None = None
    artifacts: dict[str, Any]


class SummaryRequest(BaseModel):
    run_id: str
    style: Literal["short", "detailed"] = "detailed"


class SummaryResponse(BaseModel):
    run_id: str
    out_dir: str
    summary_path: str
    summary_markdown: str


class SummaryUiRequest(BaseModel):
    run_id: str
    style: Literal["short", "detailed"] = "detailed"
    force: bool = False


class SummaryUiResponse(BaseModel):
    run_id: str
    out_dir: str
    summary_ui_path: str
    summary_markdown: str


class DiagramRequest(BaseModel):
    run_id: str
    view: Literal["flat", "3d"]


class DiagramResponse(BaseModel):
    run_id: str
    out_dir: str
    diagram_path: str
