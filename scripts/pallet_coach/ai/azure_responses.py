from __future__ import annotations

import json
import os
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


def _call_azure(system_prompt: str, user_prompt: str) -> tuple[str, dict[str, Any]]:
    endpoint = _required_env("AZURE_OAI_RESPONSES_ENDPOINT")
    api_key = _required_env("AZURE_OAI_API_KEY")
    model = _required_env("AZURE_OAI_MODEL")
    timeout_s = float(os.getenv("AZURE_OAI_TIMEOUT_S", "60"))

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

    started = time.perf_counter()
    response = httpx.post(endpoint, headers=headers, json=payload, timeout=timeout_s)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    response.raise_for_status()

    body = response.json()
    text = _extract_output_text(body)
    if not text:
        raise RuntimeError("Azure Responses API returned empty output")

    usage = body.get("usage", {}) if isinstance(body, dict) else {}
    metadata = {
        "provider": "azure_openai",
        "endpoint": endpoint,
        "model": model,
        "latency_ms": elapsed_ms,
        "prompt_tokens": usage.get("input_tokens") if isinstance(usage, dict) else None,
        "completion_tokens": usage.get("output_tokens") if isinstance(usage, dict) else None,
    }
    return text, metadata


def generate_summary_markdown(bundle: dict[str, Any], style: str = "detailed") -> tuple[str, dict[str, Any]]:
    minimized = build_minimized_bundle(bundle)
    system_prompt = load_prompt_template("azure_summary_system.md")
    user_prompt = (
        f"Style: {style}\n\n"
        "Create a stakeholder summary from this minimized run bundle JSON."
        " Use only data present in the input.\n\n"
        f"{json.dumps(minimized, indent=2)}"
    )
    return _call_azure(system_prompt, user_prompt)


def generate_summary_ui_markdown(
    summary_markdown: str,
    bundle: dict[str, Any],
    style: str = "detailed",
) -> tuple[str, dict[str, Any]]:
    minimized = build_minimized_bundle(bundle)
    system_prompt = load_prompt_template("azure_summary_ui_system.md")
    user_prompt = (
        f"Style: {style}\n\n"
        "Rewrite this deterministic markdown summary for UI readability."
        " Do not invent numbers.\n\n"
        "Deterministic summary:\n"
        f"{summary_markdown}\n\n"
        "Reference context JSON:\n"
        f"{json.dumps(minimized, indent=2)}"
    )
    return _call_azure(system_prompt, user_prompt)
