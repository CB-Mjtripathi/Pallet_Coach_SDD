from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pallet_coach.recommender import recommend

try:
    from eval.sample_parity import compare_expected_subset, run_sample_parity_cases
except ImportError:  # pragma: no cover - supports direct script execution
    from sample_parity import compare_expected_subset, run_sample_parity_cases


def _build_case_snapshot(result: dict[str, Any]) -> dict[str, Any]:
    top = result["solutions"][0] if result.get("solutions") else None
    return {
        "status": result.get("status"),
        "top_solution_id": None if top is None else top.get("solution_id"),
        "top_metrics": None if top is None else top.get("metrics"),
        "stacking": result.get("stacking"),
    }


def _evaluate_case(case: dict[str, Any]) -> tuple[bool, str, list[str], dict[str, Any], dict[str, Any]]:
    result = recommend(case["input"])
    expected = case["expected"]

    snapshot = _build_case_snapshot(result)
    diffs: list[str] = []

    if result["status"] != expected["status"]:
        diffs.append(f"status mismatch: expected {expected['status']}, got {result['status']}")

    if expected["status"] == "ok":
        top = result["solutions"][0] if result["solutions"] else None
        if top is None:
            diffs.append("expected at least one solution")
        else:
            min_cases = expected.get("min_cases_per_layer")
            if min_cases is not None and top["metrics"]["cases_per_layer"] < min_cases:
                diffs.append(
                    "cases_per_layer too low: "
                    f"expected >= {min_cases}, got {top['metrics']['cases_per_layer']}"
                )

            expected_top_solution_id = expected.get("top_solution_id")
            if expected_top_solution_id is not None and top["solution_id"] != expected_top_solution_id:
                diffs.append(
                    "top_solution_id mismatch: "
                    f"expected {expected_top_solution_id!r}, got {top['solution_id']!r}"
                )

            expected_top_metrics = expected.get("expected_top_metrics")
            if expected_top_metrics is not None:
                diffs.extend(compare_expected_subset(expected_top_metrics, top["metrics"], path="top_metrics"))

            expected_stacking = expected.get("expected_stacking")
            if expected_stacking is not None:
                diffs.extend(compare_expected_subset(expected_stacking, result["stacking"], path="stacking"))

        suffix = expected.get("must_include_solution_suffix")
        if suffix:
            found = any(sol["solution_id"].endswith(suffix) for sol in result["solutions"])
            if not found:
                diffs.append(f"missing solution suffix '{suffix}'")

    ok = not diffs
    message = "ok" if ok else diffs[0]
    return ok, message, diffs, expected, snapshot


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic solver evaluation harness")
    parser.add_argument("--cases", default=None, help="Path to eval cases JSON")
    parser.add_argument("--report-path", default="eval/reports/latest.json", help="Path to JSON report output")
    parser.add_argument(
        "--include-sample-parity",
        action="store_true",
        help="Run sample bundle parity checks after main eval cases",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    workspace_root = Path(__file__).resolve().parents[1]

    case_path = Path(args.cases) if args.cases else (Path(__file__).resolve().parent / "test_cases.json")
    cases = json.loads(case_path.read_text(encoding="utf-8"))

    passed = 0
    failed = 0
    case_reports: list[dict[str, Any]] = []

    for case in cases:
        ok, message, diffs, expected, actual = _evaluate_case(case)
        case_reports.append(
            {
                "name": case["name"],
                "passed": ok,
                "message": message,
                "diffs": diffs,
                "expected": expected,
                "actual": actual,
            }
        )
        if ok:
            passed += 1
            print(f"PASS  {case['name']}: {message}")
        else:
            failed += 1
            print(f"FAIL  {case['name']}: {message}")

    sample_parity_report = None
    if args.include_sample_parity:
        sample_parity_report = run_sample_parity_cases()
        for case in sample_parity_report["cases"]:
            if case["passed"]:
                print(f"PASS  {case['name']}: parity match")
            else:
                print(f"FAIL  {case['name']}: {case['diffs'][0]}")
        passed += sample_parity_report["passed"]
        failed += sample_parity_report["failed"]

    report = {
        "summary": {
            "passed": passed,
            "failed": failed,
            "case_count": len(case_reports),
            "sample_parity_enabled": bool(args.include_sample_parity),
        },
        "cases": case_reports,
        "sample_parity": sample_parity_report,
    }

    report_path = workspace_root / args.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nSummary: {passed} passed, {failed} failed")
    print(f"Report: {report_path.relative_to(workspace_root)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
