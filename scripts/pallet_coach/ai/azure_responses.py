from __future__ import annotations

import json
import os
import random
import hashlib
import time
from typing import Any

import httpx

from ..config import load_env_ai
from ..prompt_templates import load_prompt_template


def _required_env(name: str) -> str:
    load_env_ai()
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _extract_output_text(data: dict[str, Any]) -> str:
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"].strip()

    parts: list[str] = []
    for item in data.get("output", []) if isinstance(data.get("output"), list) else []:
        for content in item.get("content", []) if isinstance(item.get("content"), list) else []:
            text = content.get("text") if isinstance(content, dict) else None
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
    return "\n".join(parts).strip()


def build_minimized_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    recommender = bundle.get("recommender", {})
    solutions = recommender.get("solutions", [])
    top_five = []

    for sol in solutions[:5]:
        if not isinstance(sol, dict):
            continue
        reduced = {k: v for k, v in sol.items() if k != "layout"}
        top_five.append(reduced)

    return {
        "run_id": bundle.get("run_id"),
        "request": bundle.get("request", {}),
        "recommender": {
            "status": recommender.get("status"),
            "reasons": recommender.get("reasons", []),
            "solutions": top_five,
        },
        "stacking": bundle.get("stacking", {}),
    }


def _compact_json(data: dict[str, Any]) -> str:
    # Compact separators reduce prompt-assembly overhead and payload size.
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _call_azure(
    system_prompt: str,
    user_prompt: str,
    *,
    endpoint_budget_ms: int | None = None,
) -> tuple[str, dict[str, Any]]:
    endpoint = _required_env("AZURE_OAI_RESPONSES_ENDPOINT")
    api_key = _required_env("AZURE_OAI_API_KEY")
    model = _required_env("AZURE_OAI_MODEL")
    timeout_s = float(os.getenv("AZURE_OAI_TIMEOUT_S", "60"))
    max_retries = max(0, int(os.getenv("AZURE_OAI_MAX_RETRIES", "1")))
    retry_min_budget_ms = max(0, int(os.getenv("AZURE_OAI_RETRY_MIN_BUDGET_MS", "500")))
    retry_backoff_ms = max(0, int(os.getenv("AZURE_OAI_RETRY_BACKOFF_MS", "120")))

    total_started = time.perf_counter()
    request_build_started = time.perf_counter()

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    request_build_ms = int((time.perf_counter() - request_build_started) * 1000)
    deadline = None if endpoint_budget_ms is None else total_started + (endpoint_budget_ms / 1000.0)
    attempt = 0
    provider_ms = 0
    response_parse_ms = 0
    retries_used = 0

    while True:
        attempt += 1
        remaining_ms = None if deadline is None else max(0, int((deadline - time.perf_counter()) * 1000))
        if remaining_ms is not None and remaining_ms <= 0:
            raise TimeoutError("provider budget exhausted before request dispatch")

        timeout_this_attempt = timeout_s
        if remaining_ms is not None:
            timeout_this_attempt = min(timeout_this_attempt, max(0.05, remaining_ms / 1000.0))

        network_started = time.perf_counter()
        try:
            response = httpx.post(endpoint, headers=headers, json=payload, timeout=timeout_this_attempt)
            provider_ms = int((time.perf_counter() - network_started) * 1000)
            response.raise_for_status()

            parse_started = time.perf_counter()
            body = response.json()
            text = _extract_output_text(body)
            response_parse_ms = int((time.perf_counter() - parse_started) * 1000)
            break
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            provider_ms = int((time.perf_counter() - network_started) * 1000)
            can_retry = attempt <= (max_retries + 1)
            if not can_retry:
                raise TimeoutError(f"provider transport failure after retries: {exc}") from exc

            remaining_ms = None if deadline is None else max(0, int((deadline - time.perf_counter()) * 1000))
            if remaining_ms is not None and remaining_ms < retry_min_budget_ms:
                raise TimeoutError(f"provider retry denied by remaining budget: {exc}") from exc

            retries_used += 1
            backoff_s = (retry_backoff_ms + random.randint(0, 50)) / 1000.0
            time.sleep(backoff_s)

    if not text:
        raise RuntimeError("Azure Responses API returned empty output")

    usage = body.get("usage", {}) if isinstance(body, dict) else {}
    total_ms = int((time.perf_counter() - total_started) * 1000)
    metadata = {
        "provider": "azure_openai",
        "endpoint": endpoint,
        "model": model,
        "latency_ms": total_ms,
        "prompt_tokens": usage.get("input_tokens") if isinstance(usage, dict) else None,
        "completion_tokens": usage.get("output_tokens") if isinstance(usage, dict) else None,
        "retry_count": retries_used,
        "timings_ms": {
            "request_build_ms": request_build_ms,
            "provider_ms": provider_ms,
            "response_parse_ms": response_parse_ms,
            "total_ms": total_ms,
        },
        "model_config_key": model,
    }
    return text, metadata


def generate_summary_markdown(
    bundle: dict[str, Any],
    style: str = "detailed",
    *,
    endpoint_budget_ms: int | None = None,
) -> tuple[str, dict[str, Any]]:
    prep_started = time.perf_counter()
    minimized = build_minimized_bundle(bundle)
    system_prompt = load_prompt_template("azure_summary_system.md")
    minimized_json = _compact_json(minimized)
    user_prompt = (
        f"Style: {style}\n\n"
        "Create a stakeholder summary from this minimized run bundle JSON."
        " Use only data present in the input.\n\n"
        f"{minimized_json}"
    )
    text, metadata = _call_azure(system_prompt, user_prompt, endpoint_budget_ms=endpoint_budget_ms)
    timings = dict(metadata.get("timings_ms", {}))
    timings.setdefault("context_prep_ms", int((time.perf_counter() - prep_started) * 1000))
    metadata["timings_ms"] = timings
    metadata["minimized_context_hash"] = _sha256_text(minimized_json)
    return text, metadata


def generate_summary_ui_markdown(
    summary_markdown: str,
    bundle: dict[str, Any],
    style: str = "detailed",
    *,
    endpoint_budget_ms: int | None = None,
) -> tuple[str, dict[str, Any]]:
    prep_started = time.perf_counter()
    minimized = build_minimized_bundle(bundle)
    system_prompt = load_prompt_template("azure_summary_ui_system.md")
    minimized_json = _compact_json(minimized)
    user_prompt = (
        f"Style: {style}\n\n"
        "Rewrite this deterministic markdown summary for UI readability."
        " Do not invent numbers.\n\n"
        "Deterministic summary:\n"
        f"{summary_markdown}\n\n"
        "Reference context JSON:\n"
        f"{minimized_json}"
    )
    text, metadata = _call_azure(system_prompt, user_prompt, endpoint_budget_ms=endpoint_budget_ms)
    timings = dict(metadata.get("timings_ms", {}))
    timings.setdefault("context_prep_ms", int((time.perf_counter() - prep_started) * 1000))
    metadata["timings_ms"] = timings
    metadata["minimized_context_hash"] = _sha256_text(minimized_json)
    return text, metadata
