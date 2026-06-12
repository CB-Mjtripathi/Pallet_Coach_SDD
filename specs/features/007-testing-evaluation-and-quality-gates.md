# Feature: Testing, Evaluation, and Quality Gates

**Feature ID:** RF-007
**Status:** Implemented
**Priority:** Critical
**Target Release:** Phase 1 (Step 1 MVP)
**Source Documentation:** Attached: requirement.md (Section 12)

---

## Overview

This feature defines mandatory quality controls for solver correctness, stacking policy validation, regression detection, and evaluation harness behavior. It ensures the system remains deterministic, mathematically accurate, and production-safe as implementation evolves.

It includes unit test requirements under `scripts/tests/`, evaluation harness requirements under `eval/`, and sample bundle parity targets under `samples/`.

---

## User Stories

### US-7.1: Validate solver and stacking correctness

**As an** AI/CoE developer  
**I want to** run deterministic unit tests for core logic  
**So that** geometry and policy math regressions are caught early

**Acceptance Criteria:**
- ✅ `test_solver_centered_strict_tolerances.py` validates feasible layouts under strict tolerances.
- ✅ `test_stacking_model.py` validates `StackingAnalysis` fields against hand calculations.
- ✅ `test_layer_count_exceedance_highlight.py` validates warnings/status when layer count exceeds policy constraints.
- ✅ Tests execute with `pytest` in project venv.

**Technical Details:**
- Test path: `scripts/tests/`
- Deterministic fixture sets for pallet/case combinations

---

### US-7.2: Evaluate end-to-end expected outputs

**As a** quality engineer  
**I want to** run standardized case-based evaluations  
**So that** solver behavior is compared against known expected outputs

**Acceptance Criteria:**
- ✅ `eval/run_eval.py` iterates over `eval/test_cases.json`.
- ✅ Test cases include perfect fit, underhang tolerance, impossible case, and rotation-required case.
- ✅ Evaluation report includes pass/fail and expected-vs-actual diffs.

**Technical Details:**
- Input object shape follows canonical request contract
- Expected object contains selected metric assertions

---

### US-7.3: Preserve parity with reference sample bundles

**As a** supply chain analyst  
**I want to** compare against known sample runs  
**So that** business trust is maintained across rebuilds

**Acceptance Criteria:**
- ✅ Rebuilt solver output for provided sample inputs matches sample bundles.
- ✅ Allowed variance is limited to integer rounding on mm fields only.

**Technical Details:**
- Reference artifacts:
  - `samples/R1_perfect_fit/bundle.json`
  - `samples/R13_underhang_tolerance/bundle.json`

---

## Dependencies

### Prerequisites
- RF-001 through RF-004 implementation coverage

### Related Features
- RF-008 deployment pipelines should execute tests before release

---

## Technical Architecture

### Components Involved
- `scripts/tests/*`
- `eval/run_eval.py`
- `eval/test_cases.json`
- `samples/*`

### Data Flow
1. Unit test suite validates logic-level invariants.
2. Eval harness runs scenario-level assertions.
3. Sample bundle comparison validates historical parity.
4. CI gate blocks release on failures.

### APIs & Integrations
- Optional API-mode evaluation by invoking `/api/solve` in harness

---

## Non-Functional Requirements

### Performance
- Test suite runtime should remain practical for CI use.

### Security
- Test fixtures must not include secrets.

### Scalability
- Eval case set should grow with Phase 2 features while preserving baseline cases.

---

## Implementation Notes

- Use deterministic sorting in assertions to avoid flaky tests.
- Include explicit tolerance math checks in test expectations.

---

## Test Coverage

### Unit Tests Required
- See mandatory tests above plus negative contract-validation tests.

### UAT Tests Required
- UI end-to-end run from submit to artifact review
- Download bundle and inspect expected file set

---

## Traceability

**Source Documents:**
- Attached: `requirement.md` section 12 (testing and evaluation)

**Related ADRs:**
- None yet

**Implementation Files:**
- `scripts/tests/*.py`
- `eval/run_eval.py`
- `eval/test_cases.json`
- `samples/*`

---

## Open Questions

- Define target CI duration budget once implementation stabilizes.

---

**Last Updated:** 2026-04-17
**Author:** Engineering Lead Agent

---

## Implementation Notes

**Implemented:** 2026-04-17  
**Implementation Plan:** specs/implementation-plans/RF-007-testing-evaluation-and-quality-gates-implementation-plan.md

### Files Created
- eval/__init__.py
- eval/sample_parity.py
- eval/sample_parity_cases.json
- scripts/tests/test_sample_bundle_parity.py
- scripts/tests/test_contract_validation_negative.py
- .github/workflows/quality-gates.yml

### Files Modified
- eval/run_eval.py
- eval/test_cases.json
- samples/R1_perfect_fit/bundle.json
- samples/R13_underhang_tolerance/bundle.json

### Validation
- c:/python314/python.exe -m pytest scripts/tests -q: 33 passed
- $env:PYTHONPATH='scripts'; c:/python314/python.exe eval/run_eval.py --include-sample-parity: 6 passed, 0 failed
- eval/reports/latest.json generated with structured case-level expected vs actual diagnostics

### Acceptance Criteria Coverage
- US-7.1: Required deterministic tests are preserved and passing.
- US-7.2: Eval harness now emits pass/fail and structured expected-vs-actual diff report.
- US-7.3: Sample bundle parity checks implemented with mm-field rounding policy and enforced in tests/eval.
