from __future__ import annotations

import json
import os
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from ..ai.azure_responses import (
    build_minimized_bundle,
    generate_summary_markdown,
    generate_summary_ui_markdown,
)
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


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _age_seconds(created_at: str | None) -> float | None:
    if not created_at:
        return None
    try:
        created = datetime.fromisoformat(created_at)
    except ValueError:
        return None
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - created).total_seconds())


def _load_summary_meta(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_summary_meta(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _payload_profile(bundle: dict[str, Any]) -> str:
    recommender = bundle.get("recommender", {}) if isinstance(bundle, dict) else {}
    solutions = recommender.get("solutions", []) if isinstance(recommender, dict) else []
    request_blob = json.dumps(bundle.get("request", {}), ensure_ascii=False) if isinstance(bundle, dict) else ""

    score = len(solutions) * 100 + len(request_blob)
    if score < 1400:
        return "small"
    if score < 3800:
        return "medium"
    return "large"


def _reuse_policy_ttls() -> tuple[int, int, bool]:
    identical_ttl_s = max(60, int(os.getenv("SUMMARY_REUSE_IDENTICAL_TTL_S", "86400")))
    near_ttl_s = max(30, int(os.getenv("SUMMARY_REUSE_NEAR_TTL_S", "1800")))
    near_enabled = os.getenv("SUMMARY_REUSE_NEAR_ENABLED", "false").strip().lower() in {"1", "true", "yes"}
    return identical_ttl_s, near_ttl_s, near_enabled


def _retry_budget_ms() -> int:
    return max(500, int(os.getenv("SUMMARY_ENDPOINT_BUDGET_MS", "15000")))


def _classify_fallback(exc: Exception) -> str:
    text = str(exc).lower()
    if "timeout" in text or "budget" in text:
        return "fallback_timeout"
    return "fallback_error"


def _is_reuse_eligible(
    meta: dict[str, Any] | None,
    expected_fingerprint: str,
    *,
    near_enabled: bool,
    near_fields_hash: str,
    identical_ttl_s: int,
    near_ttl_s: int,
) -> tuple[bool, str, str]:
    if not meta:
        return False, "missing_metadata", "none"

    age_s = _age_seconds(meta.get("created_at"))
    if age_s is None:
        return False, "invalid_metadata_timestamp", "none"

    if meta.get("fingerprint") == expected_fingerprint:
        if age_s <= identical_ttl_s:
            return True, "identical_fingerprint", "identical"
        return False, "identical_expired", "identical"

    if near_enabled and meta.get("near_fields_hash") == near_fields_hash:
        if age_s <= near_ttl_s:
            return True, "near_identical_policy_match", "near"
        return False, "near_identical_expired", "near"

    return False, "fingerprint_mismatch", "none"


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
    request_started = time.perf_counter()
    stage_started = time.perf_counter()
    stage_timings: dict[str, int] = {}

    try:
        run_dir = resolve_run_dir_safe(payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    stage_timings["parse_ms"] = int((time.perf_counter() - stage_started) * 1000)

    stage_started = time.perf_counter()
    bundle = _load_bundle_or_404(run_dir)
    payload_profile = _payload_profile(bundle)
    stage_timings["bundle_load_ms"] = int((time.perf_counter() - stage_started) * 1000)

    stage_started = time.perf_counter()
    minimized_hash = _sha256_text(json.dumps(build_minimized_bundle(bundle), sort_keys=True, ensure_ascii=False))
    fingerprint = _sha256_text(
        json.dumps(
            {
                "run_id": payload.run_id,
                "mode": "summary",
                "style": payload.style,
                "minimized_hash": minimized_hash,
            },
            sort_keys=True,
        )
    )
    summary_path = run_dir / "recommendation_summary.md"
    summary_meta_path = run_dir / "recommendation_summary.meta.json"
    identical_ttl_s, near_ttl_s, near_enabled = _reuse_policy_ttls()
    near_fields_hash = _sha256_text(
        json.dumps(
            {"run_id": payload.run_id, "mode": "summary", "style": payload.style},
            sort_keys=True,
        )
    )
    reuse_meta = _load_summary_meta(summary_meta_path)
    reuse_ok, reuse_reason, policy_tier = _is_reuse_eligible(
        reuse_meta,
        fingerprint,
        near_enabled=near_enabled,
        near_fields_hash=near_fields_hash,
        identical_ttl_s=identical_ttl_s,
        near_ttl_s=near_ttl_s,
    )
    stage_timings["context_prep_ms"] = int((time.perf_counter() - stage_started) * 1000)

    if summary_path.exists() and reuse_ok:
        stage_started = time.perf_counter()
        summary_markdown = summary_path.read_text(encoding="utf-8")
        stage_timings["artifact_read_ms"] = int((time.perf_counter() - stage_started) * 1000)
        stage_timings["serialize_ms"] = 0
        stage_timings["total_ms"] = int((time.perf_counter() - request_started) * 1000)

        append_ai_trace(
            run_dir,
            {
                "provider": "reuse_policy",
                "operation": "summary",
                "endpoint": "/api/summary",
                "run_id": payload.run_id,
                "payload_profile": payload_profile,
                "outcome": "reused_artifact",
                "reason_code": reuse_reason,
                "policy_tier": policy_tier,
                "stage_timings_ms": stage_timings,
            },
        )
        append_run_log(run_dir, f"AI summary reused ({reuse_reason})")

        return SummaryResponse(
            run_id=payload.run_id,
            out_dir=str(run_dir),
            summary_path="recommendation_summary.md",
            summary_markdown=summary_markdown,
        )

    append_run_log(run_dir, "AI summary generation started")

    try:
        summary_markdown, meta = generate_summary_markdown(
            bundle,
            style=payload.style,
            endpoint_budget_ms=_retry_budget_ms(),
        )
        provider_timings = meta.get("timings_ms", {}) if isinstance(meta, dict) else {}
        stage_timings["provider_ms"] = int(provider_timings.get("provider_ms", meta.get("latency_ms", 0)) or 0)
        stage_timings["response_parse_ms"] = int(provider_timings.get("response_parse_ms", 0) or 0)
    except Exception as exc:
        stage_timings["provider_ms"] = int((time.perf_counter() - request_started) * 1000)
        stage_timings["total_ms"] = int((time.perf_counter() - request_started) * 1000)
        append_run_log(run_dir, f"AI summary generation failed: {exc}")
        append_ai_trace(
            run_dir,
            {
                "provider": "azure_openai",
                "operation": "summary",
                "endpoint": "/api/summary",
                "run_id": payload.run_id,
                "payload_profile": payload_profile,
                "outcome": "provider_error",
                "error": str(exc),
                "reason_code": "provider_exception",
                "stage_timings_ms": stage_timings,
            },
        )
        raise HTTPException(status_code=502, detail=f"Summary generation failed: {exc}") from exc

    stage_started = time.perf_counter()
    summary_path.write_text(summary_markdown, encoding="utf-8")

    _write_summary_meta(
        summary_meta_path,
        {
            "created_at": _iso_now(),
            "fingerprint": fingerprint,
            "near_fields_hash": near_fields_hash,
            "style": payload.style,
            "mode": "summary",
        },
    )
    stage_timings["artifact_write_ms"] = int((time.perf_counter() - stage_started) * 1000)

    update_bundle_artifacts(bundle, {"recommendation_summary": "recommendation_summary.md"})
    ai_assist = dict(bundle.get("ai_assist", {}))
    ai_assist["summary_generated"] = True
    bundle["ai_assist"] = ai_assist
    write_bundle(run_dir, bundle)
    stage_timings["serialize_ms"] = 0
    stage_timings["total_ms"] = int((time.perf_counter() - request_started) * 1000)

    append_ai_trace(
        run_dir,
        {
            **meta,
            "operation": "summary",
            "endpoint": "/api/summary",
            "run_id": payload.run_id,
            "payload_profile": payload_profile,
            "outcome": "generation",
            "reason_code": "provider_success",
            "policy_tier": "none",
            "stage_timings_ms": stage_timings,
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
    request_started = time.perf_counter()
    stage_started = time.perf_counter()
    stage_timings: dict[str, int] = {}

    try:
        run_dir = resolve_run_dir_safe(payload.run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    stage_timings["parse_ms"] = int((time.perf_counter() - stage_started) * 1000)

    stage_started = time.perf_counter()
    bundle = _load_bundle_or_404(run_dir)
    payload_profile = _payload_profile(bundle)
    summary_ui_path = run_dir / "summary_ui.md"
    summary_ui_meta_path = run_dir / "summary_ui.meta.json"
    stage_timings["bundle_load_ms"] = int((time.perf_counter() - stage_started) * 1000)

    source_summary_path = run_dir / "recommendation_summary.md"
    source_summary = source_summary_path.read_text(encoding="utf-8") if source_summary_path.exists() else ""
    if not source_summary:
        source_summary = "No deterministic summary available. Use bundle context only."

    stage_started = time.perf_counter()
    minimized_hash = _sha256_text(json.dumps(build_minimized_bundle(bundle), sort_keys=True, ensure_ascii=False))
    source_summary_hash = _sha256_text(source_summary)
    fingerprint = _sha256_text(
        json.dumps(
            {
                "run_id": payload.run_id,
                "mode": "summary_ui",
                "style": payload.style,
                "source_summary_hash": source_summary_hash,
                "minimized_hash": minimized_hash,
            },
            sort_keys=True,
        )
    )
    near_fields_hash = _sha256_text(
        json.dumps(
            {
                "run_id": payload.run_id,
                "mode": "summary_ui",
                "style": payload.style,
                "source_summary_hash": source_summary_hash,
            },
            sort_keys=True,
        )
    )
    identical_ttl_s, near_ttl_s, near_enabled = _reuse_policy_ttls()
    reuse_meta = _load_summary_meta(summary_ui_meta_path)
    reuse_ok, reuse_reason, policy_tier = _is_reuse_eligible(
        reuse_meta,
        fingerprint,
        near_enabled=near_enabled,
        near_fields_hash=near_fields_hash,
        identical_ttl_s=identical_ttl_s,
        near_ttl_s=near_ttl_s,
    )
    stage_timings["context_prep_ms"] = int((time.perf_counter() - stage_started) * 1000)

    if summary_ui_path.exists() and not payload.force and reuse_ok:
        stage_started = time.perf_counter()
        summary_markdown = summary_ui_path.read_text(encoding="utf-8")
        stage_timings["artifact_read_ms"] = int((time.perf_counter() - stage_started) * 1000)
        stage_timings["serialize_ms"] = 0
        stage_timings["total_ms"] = int((time.perf_counter() - request_started) * 1000)

        append_ai_trace(
            run_dir,
            {
                "provider": "reuse_policy",
                "operation": "summary_ui",
                "endpoint": "/api/summary_ui",
                "run_id": payload.run_id,
                "payload_profile": payload_profile,
                "outcome": "reused_artifact",
                "reason_code": reuse_reason,
                "policy_tier": policy_tier,
                "stage_timings_ms": stage_timings,
            },
        )
        return SummaryUiResponse(
            run_id=payload.run_id,
            out_dir=str(run_dir),
            summary_ui_path="summary_ui.md",
            summary_markdown=summary_markdown,
        )

    append_run_log(run_dir, "AI summary_ui generation started")

    try:
        summary_markdown, meta = generate_summary_ui_markdown(
            source_summary,
            bundle,
            style=payload.style,
            endpoint_budget_ms=_retry_budget_ms(),
        )
        provider_timings = meta.get("timings_ms", {}) if isinstance(meta, dict) else {}
        stage_timings["provider_ms"] = int(provider_timings.get("provider_ms", meta.get("latency_ms", 0)) or 0)
        stage_timings["response_parse_ms"] = int(provider_timings.get("response_parse_ms", 0) or 0)
        outcome = "generation"
        reason_code = "provider_success"
        provider_name = "azure_openai"
    except Exception as exc:
        append_run_log(run_dir, f"AI summary_ui generation failed: {exc}")
        outcome = _classify_fallback(exc)
        reason_code = "provider_timeout" if outcome == "fallback_timeout" else "provider_error"
        provider_name = "fallback"
        summary_markdown = _build_summary_ui_fallback(source_summary, str(exc))
        meta = {
            "provider": "fallback",
            "model": "deterministic",
            "reason": str(exc),
        }
        stage_timings["provider_ms"] = int((time.perf_counter() - request_started) * 1000)
        append_run_log(run_dir, "AI summary_ui fallback generated from deterministic summary")

    stage_started = time.perf_counter()
    summary_ui_path.write_text(summary_markdown, encoding="utf-8")
    _write_summary_meta(
        summary_ui_meta_path,
        {
            "created_at": _iso_now(),
            "fingerprint": fingerprint,
            "near_fields_hash": near_fields_hash,
            "style": payload.style,
            "mode": "summary_ui",
            "source_summary_hash": source_summary_hash,
        },
    )
    stage_timings["artifact_write_ms"] = int((time.perf_counter() - stage_started) * 1000)

    update_bundle_artifacts(bundle, {"summary_ui": "summary_ui.md"})
    ai_assist = dict(bundle.get("ai_assist", {}))
    ai_assist["summary_ui_generated"] = True
    bundle["ai_assist"] = ai_assist
    write_bundle(run_dir, bundle)
    stage_timings["serialize_ms"] = 0
    stage_timings["total_ms"] = int((time.perf_counter() - request_started) * 1000)

    append_ai_trace(
        run_dir,
        {
            **meta,
            "operation": "summary_ui",
            "endpoint": "/api/summary_ui",
            "run_id": payload.run_id,
            "provider": provider_name,
            "payload_profile": payload_profile,
            "outcome": outcome,
            "reason_code": reason_code,
            "policy_tier": "none" if payload.force else policy_tier,
            "stage_timings_ms": stage_timings,
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
