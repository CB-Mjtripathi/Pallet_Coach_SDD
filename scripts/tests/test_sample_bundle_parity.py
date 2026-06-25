from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.sample_parity import compare_expected_subset, run_sample_parity_cases


def test_mm_rounding_only_applies_to_mm_fields():
    mm_diffs = compare_expected_subset(
        {"total_height_mm": 1344.0},
        {"total_height_mm": 1344.49},
    )
    assert not mm_diffs

    non_mm_diffs = compare_expected_subset(
        {"area_fill_efficiency_pct": 96.6},
        {"area_fill_efficiency_pct": 96.7},
    )
    assert non_mm_diffs


def test_sample_bundle_parity_cases_pass():
    report = run_sample_parity_cases(Path("eval/sample_parity_cases.json"))
    assert report["failed"] == 0
    assert report["passed"] >= 2
