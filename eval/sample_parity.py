from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pallet_coach.recommender import recommend


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_mm_path(path: str) -> bool:
    normalized = path.replace("[", ".").replace("]", "")
    tokens = [token for token in normalized.split(".") if token]
    return any(token.endswith("_mm") for token in tokens)


def compare_expected_subset(expected: Any, actual: Any, path: str = "") -> list[str]:
    diffs: list[str] = []

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            diffs.append(f"{path or '<root>'}: expected object, got {type(actual).__name__}")
            return diffs
        for key, expected_value in expected.items():
            next_path = f"{path}.{key}" if path else key
            if key not in actual:
                diffs.append(f"{next_path}: missing in actual")
                continue
            diffs.extend(compare_expected_subset(expected_value, actual[key], next_path))
        return diffs

    if isinstance(expected, list):
        if not isinstance(actual, list):
            diffs.append(f"{path or '<root>'}: expected list, got {type(actual).__name__}")
            return diffs
        if len(expected) != len(actual):
            diffs.append(f"{path or '<root>'}: length mismatch expected {len(expected)} got {len(actual)}")
            return diffs
        for idx, expected_item in enumerate(expected):
            next_path = f"{path}[{idx}]" if path else f"[{idx}]"
            diffs.extend(compare_expected_subset(expected_item, actual[idx], next_path))
        return diffs

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if _is_mm_path(path):
            if round(float(expected)) != round(float(actual)):
                diffs.append(
                    f"{path}: mm-rounding mismatch expected {round(float(expected))} got {round(float(actual))}"
                )
            return diffs

    if expected != actual:
        diffs.append(f"{path or '<root>'}: expected {expected!r} got {actual!r}")

    return diffs


def build_recommendation_snapshot(result: dict[str, Any]) -> dict[str, Any]:
    top = result["solutions"][0] if result.get("solutions") else None
    return {
        "status": result.get("status"),
        "top_solution_id": None if top is None else top.get("solution_id"),
        "top_metrics": None if top is None else top.get("metrics"),
        "stacking": result.get("stacking"),
    }


def evaluate_sample_case(case: dict[str, Any], workspace_root: Path) -> dict[str, Any]:
    sample_bundle = workspace_root / case["sample_bundle"]
    sample_data = _load_json(sample_bundle)

    input_payload = {"request": sample_data["request"]}
    actual_result = recommend(input_payload)
    actual_snapshot = build_recommendation_snapshot(actual_result)

    expected_snapshot = sample_data.get("reference", {}).get("expected")
    if expected_snapshot is None:
        fallback_status = sample_data.get("recommender", {}).get("status")
        expected_snapshot = {"status": fallback_status}

    diffs = compare_expected_subset(expected_snapshot, actual_snapshot)

    return {
        "name": case["name"],
        "sample_bundle": case["sample_bundle"],
        "passed": not diffs,
        "diffs": diffs,
        "expected": expected_snapshot,
        "actual": actual_snapshot,
    }


def run_sample_parity_cases(cases_path: Path | None = None) -> dict[str, Any]:
    workspace_root = Path(__file__).resolve().parents[1]
    default_manifest = Path(__file__).resolve().parent / "sample_parity_cases.json"
    manifest_path = default_manifest if cases_path is None else cases_path
    if not manifest_path.is_absolute():
        manifest_path = workspace_root / manifest_path
    manifest_path = manifest_path.resolve()

    cases = _load_json(manifest_path)

    case_results = [evaluate_sample_case(case, workspace_root) for case in cases]
    passed = sum(1 for c in case_results if c["passed"])
    failed = len(case_results) - passed

    return {
        "manifest": str(manifest_path.relative_to(workspace_root)),
        "passed": passed,
        "failed": failed,
        "cases": case_results,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sample bundle parity checks")
    parser.add_argument("--cases", default=None, help="Path to sample parity cases JSON")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    cases_path = None if args.cases is None else Path(args.cases)
    report = run_sample_parity_cases(cases_path=cases_path)

    for case in report["cases"]:
        if case["passed"]:
            print(f"PASS  {case['name']}: parity match")
        else:
            print(f"FAIL  {case['name']}: {case['diffs'][0]}")

    print(f"\nSample parity summary: {report['passed']} passed, {report['failed']} failed")
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
