from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from ..ai.azure_responses import generate_summary_markdown, generate_summary_ui_markdown
from ..ai.google_ai_studio import generate_diagram_image
from ..ai.tracing import append_ai_trace
from ..artifacts import (
    update_bundle_artifacts,
    write_3d_stability_report,
    write_image_prompts,
    write_overhang_underhang_table,
    write_printable_loading_sheet,
    write_recommendation_summary,
)
from ..config import load_env_ai, validate_runtime_config
from ..diagram import (
    render_comparison_3d_png,
    render_comparison_flat_png,
    render_isometric_exploded_3d_png,
    render_layer_png,
    render_onpallet_3d_png,
)
from ..errors import ContractError
from ..recommender import recommend
from .models import (
    DiagramRequest,
    DiagramResponse,
    SolveRequest,
    SolveResponse,
    SummaryRequest,
    SummaryResponse,
    SummaryUiRequest,
    SummaryUiResponse,
)
from .run_store import (
    allocate_run_id,
    append_run_log,
    archive_loose_root_files,
    create_run_dir,
    ensure_output_root,
    resolve_run_dir_safe,
    tail_run_log,
    write_bundle,
)

app = FastAPI(title="Pallet Coach API", version="0.1.0")

# Enable CORS for development (UI running on different port)
# This is necessary because:
# - UI runs on http://127.0.0.1:5173 (port 5173)
# - API runs on http://127.0.0.1:8000 (port 8000)
# - Browsers block cross-origin requests unless CORS headers are set
# For production, restrict allowed_origins to specific domains only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Development: UI local host
        "http://127.0.0.1:5173",      # Development: UI loopback
        "http://localhost:3000",      # Alternative dev port (React dev server)
        "http://127.0.0.1:3000",      # Alternative dev port loopback
    ],
    allow_credentials=True,
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all request headers (Content-Type, etc.)
)


@app.on_event("startup")
def on_startup() -> None:
    load_env_ai()
    validate_runtime_config()
    ensure_output_root()
    archive_loose_root_files()


@app.exception_handler(ContractError)
async def contract_error_handler(_, exc: ContractError):
    return PlainTextResponse(
        content=json.dumps({"error": str(exc), "details": exc.details}),
        status_code=422,
        media_type="application/json",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _build_artifacts() -> dict[str, Any]:
    return {
        "bundle": {"path": "bundle.json"},
        "run_log": {"path": "run_log.txt"},
        "recommendation_summary": {"path": "recommendation_summary.md"},
        "layer_diagram": {"path": "layer_diagram.png"},
        "comparison_flat": {"path": "comparison_flat.png"},
        "comparison_3d": {"path": "comparison_3d.png"},
        "onpallet_3d": {"path": "onpallet_3d.png"},
        "isometric_exploded_3d": {"path": "isometric_exploded_3d.png"},
        "image_prompt_flat": {"path": "image_prompt_flat.md"},
        "image_prompt_3d": {"path": "image_prompt_3d.md"},
        "stability_report_3d": {"path": "stability_report_3d.json"},
        "stability_report_3d_md": {"path": "stability_report_3d.md"},
        "overhang_underhang_table": {"path": "overhang_underhang_table.md"},
        "summary_ui": {"path": "summary_ui.md"},
        "diagram_flat": {"path": "diagram_flat.png"},
        "diagram_3d": {"path": "diagram_3d.png"},
    }


def _load_bundle_or_404(run_dir: Path) -> dict[str, Any]:
    bundle_path = run_dir / "bundle.json"
    if not bundle_path.exists():
        raise HTTPException(status_code=404, detail="Run bundle not found")
    return json.loads(bundle_path.read_text(encoding="utf-8"))


def _build_summary_ui_fallback(source_summary: str, reason: str) -> str:
    fallback = source_summary.strip() or "No deterministic summary available."
    return (
        "# Recommendation Summary\n\n"
        "_AI rewrite unavailable in this environment. Showing deterministic summary instead._\n\n"
        f"{fallback}\n\n"
        f"---\n\nProvider error: {reason}\n"
    )


@app.post("/api/solve", response_model=SolveResponse)
def solve_endpoint(payload: SolveRequest) -> SolveResponse:
    run_id = allocate_run_id()
    run_dir = create_run_dir(run_id)
    append_run_log(run_dir, "Solve request received")

    # Recommend may raise ContractError, mapped by exception handler.
    rec = recommend({"request": payload.request}, max_options=payload.max_solutions)

    now = datetime.now(timezone.utc).isoformat() if payload.include_timestamp else None
    bundle = {
        "run_id": run_id,
        "created_at": now,
        "request": payload.request,
        "recommender": {
            "status": rec["status"],
            "reasons": rec["reasons"],
            "solutions": rec["solutions"],
        },
        "stacking": rec.get("stacking"),
        "artifacts": _build_artifacts(),
        "ai_assist": {
            "summary_generated": False,
            "summary_ui_generated": False,
            "diagram_flat_generated": False,
            "diagram_3d_generated": False,
        },
        "provenance": {
            "solver_version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    best_solution = rec["solutions"][0] if rec.get("solutions") else None
    request_data = payload.request
    baseline_cpl = request_data.get("baseline_cases_per_layer")

    append_run_log(run_dir, "Generating deterministic artifacts")
    write_recommendation_summary(run_dir, bundle)
    write_image_prompts(run_dir, bundle)
    write_printable_loading_sheet(run_dir, bundle)
    write_overhang_underhang_table(run_dir, bundle)
    write_3d_stability_report(run_dir, bundle)

    render_layer_png(run_dir, best_solution, request_data)
    render_comparison_flat_png(
        run_dir,
        best_solution,
        request_data,
        baseline_cases_per_layer=baseline_cpl,
    )
    render_comparison_3d_png(
        run_dir,
        best_solution,
        request_data,
        baseline_cases_per_layer=baseline_cpl,
    )
    render_onpallet_3d_png(run_dir, best_solution, request_data)
    render_isometric_exploded_3d_png(run_dir, best_solution, request_data)

    update_bundle_artifacts(
        bundle,
        {
            "bundle": "bundle.json",
            "run_log": "run_log.txt",
            "recommendation_summary": "recommendation_summary.md",
            "layer_diagram": "layer_diagram.png",
            "comparison_flat": "comparison_flat.png",
            "comparison_3d": "comparison_3d.png",
            "onpallet_3d": "onpallet_3d.png",
            "isometric_exploded_3d": "isometric_exploded_3d.png",
            "image_prompt_flat": "image_prompt_flat.md",
            "image_prompt_3d": "image_prompt_3d.md",
            "stability_report_3d": "stability_report_3d.json",
            "stability_report_3d_md": "stability_report_3d.md",
            "overhang_underhang_table": "overhang_underhang_table.md",
        },
    )

    write_bundle(run_dir, bundle)
    append_run_log(run_dir, "Deterministic artifacts generated")
    append_run_log(run_dir, f"Solve completed with status={rec['status']}")

    best_metrics = None
    if rec.get("solutions"):
        metrics = rec["solutions"][0].get("metrics", {})
        best_metrics = {
            "cases_per_layer": metrics.get("cases_per_layer"),
            "total_cases": metrics.get("total_cases"),
            "area_fill_efficiency_pct": metrics.get("area_fill_efficiency_pct"),
            "total_height_mm": metrics.get("total_height_mm"),
        }

    return SolveResponse(
        run_id=run_id,
        out_dir=str(run_dir),
        solver_status=rec["status"],
        best_metrics=best_metrics,
        artifacts={
            "bundle": {"path": "bundle.json"},
            "run_log": {"path": "run_log.txt"},
            "recommendation_summary": {"path": "recommendation_summary.md"},
            "layer_diagram": {"path": "layer_diagram.png"},
            "comparison_flat": {"path": "comparison_flat.png"},
            "comparison_3d": {"path": "comparison_3d.png"},
            "onpallet_3d": {"path": "onpallet_3d.png"},
            "isometric_exploded_3d": {"path": "isometric_exploded_3d.png"},
            "image_prompt_flat": {"path": "image_prompt_flat.md"},
            "image_prompt_3d": {"path": "image_prompt_3d.md"},
            "stability_report_3d": {"path": "stability_report_3d.json"},
            "stability_report_3d_md": {"path": "stability_report_3d.md"},
            "overhang_underhang_table": {"path": "overhang_underhang_table.md"},
        },
    )


@app.get("/api/runs/{run_id}")
def get_run_bundle(run_id: str) -> dict[str, Any]:
    try:
        run_dir = resolve_run_dir_safe(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc

    bundle_path = run_dir / "bundle.json"
    if not bundle_path.exists():
        raise HTTPException(status_code=404, detail="Run bundle not found")

    return json.loads(bundle_path.read_text(encoding="utf-8"))


@app.get("/api/runs/{run_id}/logs", response_class=PlainTextResponse)
def get_run_logs(run_id: str, n_lines: int = 200) -> str:
    try:
        run_dir = resolve_run_dir_safe(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc

    return tail_run_log(run_dir, n_lines=n_lines)


@app.post("/api/summary", response_model=SummaryResponse)
def summary_endpoint(payload: SummaryRequest) -> SummaryResponse:
    try:
        run_dir = resolve_run_dir_safe(payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc

    bundle = _load_bundle_or_404(run_dir)
    append_run_log(run_dir, "AI summary generation started")

    try:
        summary_markdown, meta = generate_summary_markdown(bundle, style=payload.style)
    except Exception as exc:
        append_run_log(run_dir, f"AI summary generation failed: {exc}")
        append_ai_trace(
            run_dir,
            {
                "provider": "azure_openai",
                "operation": "summary",
                "run_id": payload.run_id,
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=502, detail=f"Summary generation failed: {exc}") from exc

    summary_path = run_dir / "recommendation_summary.md"
    summary_path.write_text(summary_markdown, encoding="utf-8")

    update_bundle_artifacts(bundle, {"recommendation_summary": "recommendation_summary.md"})
    ai_assist = dict(bundle.get("ai_assist", {}))
    ai_assist["summary_generated"] = True
    bundle["ai_assist"] = ai_assist
    write_bundle(run_dir, bundle)

    append_ai_trace(
        run_dir,
        {
            **meta,
            "operation": "summary",
            "run_id": payload.run_id,
        },
    )
    append_run_log(run_dir, "AI summary generation completed")

    return SummaryResponse(
        run_id=payload.run_id,
        out_dir=str(run_dir),
        summary_path="recommendation_summary.md",
        summary_markdown=summary_markdown,
    )


@app.post("/api/summary_ui", response_model=SummaryUiResponse)
def summary_ui_endpoint(payload: SummaryUiRequest) -> SummaryUiResponse:
    try:
        run_dir = resolve_run_dir_safe(payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc

    bundle = _load_bundle_or_404(run_dir)
    summary_ui_path = run_dir / "summary_ui.md"

    if summary_ui_path.exists() and not payload.force:
        return SummaryUiResponse(
            run_id=payload.run_id,
            out_dir=str(run_dir),
            summary_ui_path="summary_ui.md",
            summary_markdown=summary_ui_path.read_text(encoding="utf-8"),
        )

    append_run_log(run_dir, "AI summary_ui generation started")

    source_summary_path = run_dir / "recommendation_summary.md"
    source_summary = source_summary_path.read_text(encoding="utf-8") if source_summary_path.exists() else ""
    if not source_summary:
        source_summary = "No deterministic summary available. Use bundle context only."

    try:
        summary_markdown, meta = generate_summary_ui_markdown(
            source_summary,
            bundle,
            style=payload.style,
        )
    except Exception as exc:
        append_run_log(run_dir, f"AI summary_ui generation failed: {exc}")
        append_ai_trace(
            run_dir,
            {
                "provider": "azure_openai",
                "operation": "summary_ui",
                "run_id": payload.run_id,
                "error": str(exc),
            },
        )
        summary_markdown = _build_summary_ui_fallback(source_summary, str(exc))
        meta = {
            "provider": "fallback",
            "model": "deterministic",
            "reason": str(exc),
        }
        append_run_log(run_dir, "AI summary_ui fallback generated from deterministic summary")

    summary_ui_path.write_text(summary_markdown, encoding="utf-8")
    update_bundle_artifacts(bundle, {"summary_ui": "summary_ui.md"})
    ai_assist = dict(bundle.get("ai_assist", {}))
    ai_assist["summary_ui_generated"] = True
    bundle["ai_assist"] = ai_assist
    write_bundle(run_dir, bundle)

    append_ai_trace(
        run_dir,
        {
            **meta,
            "operation": "summary_ui",
            "run_id": payload.run_id,
        },
    )
    append_run_log(run_dir, "AI summary_ui generation completed")

    return SummaryUiResponse(
        run_id=payload.run_id,
        out_dir=str(run_dir),
        summary_ui_path="summary_ui.md",
        summary_markdown=summary_markdown,
    )


@app.post("/api/diagram", response_model=DiagramResponse)
def diagram_endpoint(payload: DiagramRequest) -> DiagramResponse:
    try:
        run_dir = resolve_run_dir_safe(payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc

    bundle = _load_bundle_or_404(run_dir)
    append_run_log(run_dir, f"AI diagram generation started for view={payload.view}")

    prompt_name = "image_prompt_flat.md" if payload.view == "flat" else "image_prompt_3d.md"
    prompt_path = run_dir / prompt_name
    if not prompt_path.exists():
        raise HTTPException(status_code=404, detail=f"Prompt file not found: {prompt_name}")
    prompt_text = prompt_path.read_text(encoding="utf-8")

    try:
        image_bytes, meta = generate_diagram_image(prompt_text=prompt_text, view=payload.view)
    except Exception as exc:
        append_run_log(run_dir, f"AI diagram generation failed for view={payload.view}: {exc}")
        append_ai_trace(
            run_dir,
            {
                "provider": "google_ai_studio",
                "operation": f"diagram_{payload.view}",
                "run_id": payload.run_id,
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=502, detail=f"Diagram generation failed: {exc}") from exc

    filename = "diagram_flat.png" if payload.view == "flat" else "diagram_3d.png"
    out_path = run_dir / filename
    out_path.write_bytes(image_bytes)

    artifact_key = "diagram_flat" if payload.view == "flat" else "diagram_3d"
    update_bundle_artifacts(bundle, {artifact_key: filename})

    ai_assist = dict(bundle.get("ai_assist", {}))
    if payload.view == "flat":
        ai_assist["diagram_flat_generated"] = True
    else:
        ai_assist["diagram_3d_generated"] = True
    bundle["ai_assist"] = ai_assist
    write_bundle(run_dir, bundle)

    append_ai_trace(
        run_dir,
        {
            **meta,
            "operation": f"diagram_{payload.view}",
            "run_id": payload.run_id,
        },
    )
    append_run_log(run_dir, f"AI diagram generation completed for view={payload.view}")

    return DiagramResponse(
        run_id=payload.run_id,
        out_dir=str(run_dir),
        diagram_path=filename,
    )


@app.get("/output/{run_id}/{filename}")
def get_output_file(run_id: str, filename: str):
    try:
        run_dir = resolve_run_dir_safe(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc

    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=404, detail="File not found")

    target = (run_dir / filename).resolve()
    if run_dir.resolve() not in target.parents:
        raise HTTPException(status_code=404, detail="File not found")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=target)


# Mount static output artifacts from 04_Output in repository root.
app.mount("/output", StaticFiles(directory=str(ensure_output_root())), name="output")
