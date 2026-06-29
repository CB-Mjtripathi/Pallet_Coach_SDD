from __future__ import annotations

import json
import statistics
import time
from pathlib import Path


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * p
    low = int(rank)
    high = min(low + 1, len(values) - 1)
    fraction = rank - low
    return values[low] * (1 - fraction) + values[high] * fraction


def summarize_latency(values_ms: list[float]) -> dict[str, float]:
    sorted_values = sorted(values_ms)
    return {
        "count": float(len(sorted_values)),
        "mean": statistics.fmean(sorted_values) if sorted_values else 0.0,
        "p50": percentile(sorted_values, 0.50),
        "p95": percentile(sorted_values, 0.95),
        "p99": percentile(sorted_values, 0.99),
    }


def write_latency_report(path: Path, endpoint: str, profile: str, metrics: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "endpoint": endpoint,
        "profile": profile,
        "metrics": metrics,
        "generated_at_ms": int(time.time() * 1000),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_summary_latency_report_helper(tmp_path: Path):
    sample = [120.0, 140.0, 180.0, 200.0, 240.0, 300.0]
    metrics = summarize_latency(sample)

    assert metrics["count"] == 6.0
    assert metrics["p50"] >= 180.0
    assert metrics["p95"] >= 240.0

    report_path = tmp_path / "summary-latency-report.json"
    write_latency_report(report_path, "/api/summary_ui", "small", metrics)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["endpoint"] == "/api/summary_ui"
    assert report["profile"] == "small"
    assert report["metrics"]["p95"] == metrics["p95"]
