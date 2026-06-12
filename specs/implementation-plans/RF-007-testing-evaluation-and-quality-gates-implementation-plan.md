# Implementation Plan: Testing, Evaluation, and Quality Gates
**Feature ID:** RF-007  
**Generated:** 2026-04-17  
**Agent:** Tech Lead v1.0  
**Approach:** HYBRID (Enhancement + Gap Closure)

---

## Executive Summary

**Feature:** Testing, Evaluation, and Quality Gates  
**Status:** Partially Implemented  
**Implementation Approach:** HYBRID  
**Estimated Complexity:** Medium  
**Risk Level:** Medium

**Summary:**
RF-007 already has substantial implementation coverage: required core unit tests exist, the evaluation harness iterates over canonical test cases, and baseline scenarios pass. Remaining gaps are concentrated in parity enforcement with reference sample bundles and richer expected-vs-actual diff reporting. The recommended approach is to preserve existing test/eval structure and add targeted parity checks, stronger diff output, and lightweight quality-gate automation.

---

## Table of Contents
1. Feature Analysis
2. Implementation Status
3. Impact Analysis
4. Development Plan
5. Testing Strategy
6. Developer Checklist

---

## Feature Analysis

### Feature Overview
**Feature ID:** RF-007  
**Feature Name:** Testing, Evaluation, and Quality Gates  
**Priority:** Critical  
**Complexity:** Medium

### Scope Summary
RF-007 defines deterministic quality controls for solver/stacking correctness and scenario-level regression detection. It requires mandatory unit tests in scripts/tests, standardized evaluation runs in eval/run_eval.py using eval/test_cases.json, and parity checks against sample bundles with strict variance policy.

### Key Requirements
1. Preserve deterministic unit tests for solver and stacking correctness.
2. Ensure eval harness covers required scenarios and reports pass/fail with expected-vs-actual diffs.
3. Enforce sample parity checks against reference bundles with mm-field rounding-only variance allowance.
4. Keep the suite practical for CI and suitable as release gating input.

### User Stories Summary
- **US-7.1:** Validate solver and stacking correctness through deterministic unit tests.
- **US-7.2:** Evaluate end-to-end expected outputs from standardized case fixtures.
- **US-7.3:** Preserve parity with known reference sample bundles.

### Technical Specifications
- **Required assets:** scripts/tests/*.py, eval/run_eval.py, eval/test_cases.json, samples/*.
- **Core expectations:** deterministic assertions, expected-vs-actual diagnostic output, sample parity comparator.
- **Execution:** pytest + eval harness in project environment.

### Dependencies
- **Prerequisites:** RF-001 to RF-004 functionality stability.
- **Related features:** RF-008 deployment/security/ops for formal release gating in pipelines.

### Complexity Assessment
**Estimated Complexity:** Medium  
**Reasoning:**
- Number of user stories: 3
- Number of modules involved: 6 to 9
- External integrations: none required for baseline implementation
- Data model complexity: low
- Test/eval complexity: moderate (diagnostics + parity tolerance handling)

---

## Implementation Status

### Search Results Analysis

#### Backend Test Coverage
- **File:** scripts/tests/test_solver_centered_strict_tolerances.py  
  - **Relevance:** High  
  - **Functionality:** deterministic solver feasibility, rotation-required case, impossible-case reason validation.  
  - **Match Level:** Exact for US-7.1 subset.

- **File:** scripts/tests/test_stacking_model.py  
  - **Relevance:** High  
  - **Functionality:** hand-check style stacking ceiling/range policy checks.  
  - **Match Level:** Exact.

- **File:** scripts/tests/test_layer_count_exceedance_highlight.py  
  - **Relevance:** High  
  - **Functionality:** warning behavior for exceedance and weight-binding conditions.  
  - **Match Level:** Exact.

#### Evaluation Harness
- **File:** eval/run_eval.py  
  - **Relevance:** High  
  - **Functionality:** iterates eval/test_cases.json and prints pass/fail with concise mismatch messages.  
  - **Match Level:** Partial (diff output currently minimal, no structured expected-vs-actual report object).

- **File:** eval/test_cases.json  
  - **Relevance:** High  
  - **Functionality:** includes perfect-fit, underhang-tolerance, impossible, rotation-required scenarios.  
  - **Match Level:** Exact.

#### Sample Parity Assets
- **Files:** samples/R1_perfect_fit/bundle.json, samples/R13_underhang_tolerance/bundle.json  
  - **Relevance:** High  
  - **Functionality:** present but currently placeholder-like references rather than full parity assertion targets.  
  - **Match Level:** Partial to missing for US-7.3 enforcement.

#### Quality Gate Automation
- **Observation:** no repository CI workflow file discovered under .github/workflows in current workspace snapshot.  
  - **Match Level:** Missing for automated gate execution (recommended alignment with RF-007 architecture and RF-008 dependency).

### Implementation Status: Partially Implemented

### Implementation Coverage

| User Story | Status | Existing Implementation | Gap |
|------------|--------|------------------------|-----|
| US-7.1 | Implemented | deterministic unit tests exist in scripts/tests | maintain + extend with negative contract tests if needed |
| US-7.2 | Partial | eval harness and required 4 scenarios exist | richer expected-vs-actual diff detail and optional machine-readable report output |
| US-7.3 | Not Implemented | sample bundle files exist | no robust parity comparator and bundles are placeholder-level |

### Coverage Summary
- **Implemented:** 1 / 3 user stories (33%)
- **Partially Implemented:** 1 / 3
- **Not Implemented:** 1 / 3

### Recommendation
**Primary Approach:** HYBRID  
**Reasoning:** preserve current validated tests/harness and add focused capabilities for parity checks, richer diagnostics, and optional CI gate integration.

### Requirements to Code Mapping

| Requirement | Acceptance Criteria | Existing Code | Status |
|-------------|-------------------|---------------|--------|
| Solver deterministic tests | strict tolerances + impossible/rotation behavior | scripts/tests/test_solver_centered_strict_tolerances.py | Implemented |
| Stacking policy calculations | hand-calculation aligned fields | scripts/tests/test_stacking_model.py | Implemented |
| Layer exceedance warnings | warning/highlight behavior | scripts/tests/test_layer_count_exceedance_highlight.py | Implemented |
| Eval cases and iteration | 4 canonical cases via test_cases.json | eval/run_eval.py + eval/test_cases.json | Implemented |
| Expected-vs-actual diffs | detailed diagnostic comparisons | eval/run_eval.py | Partial |
| Sample bundle parity | compare rebuilt solver outputs vs samples with mm rounding policy | samples/* only | Missing |

---

## Impact Analysis

### Affected Modules

### Evaluation Layer
- **File:** eval/run_eval.py
  - **Change Type:** Modification
  - **Impact Level:** High
  - **Reason:** add structured diff reporting and optional parity invocation.

- **File:** eval/test_cases.json
  - **Change Type:** Modification (optional)
  - **Impact Level:** Medium
  - **Reason:** include stronger expected assertions and parity metadata.

- **File to Create:** eval/sample_parity.py
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** central parity comparator utility with mm-field tolerance policy.

- **File to Create:** eval/sample_parity_cases.json
  - **Change Type:** New File
  - **Impact Level:** Medium
  - **Reason:** canonical mapping of sample inputs to expected reference bundle metrics.

### Test Layer
- **File to Create:** scripts/tests/test_sample_bundle_parity.py
  - **Change Type:** New File
  - **Impact Level:** High
  - **Reason:** enforce US-7.3 via deterministic tests.

- **File to Modify:** scripts/tests/test_api_app.py (optional extension)
  - **Change Type:** Modification
  - **Impact Level:** Low
  - **Reason:** optional negative contract-validation coverage under RF-007 notes.

### Automation Layer (Recommended)
- **File to Create:** .github/workflows/quality-gates.yml
  - **Change Type:** New File
  - **Impact Level:** Medium
  - **Reason:** execute pytest + eval harness on pull request/push for release safety.

### Integration Points

#### Internal Dependencies
- **Depends On:** RF-001 deterministic solver and stacking output shape.
- **Depends On:** RF-002 API contract stability (if API-mode eval is later enabled).
- **Depends On:** RF-003 artifact and bundle format if parity checks consume bundle-level metrics.

#### External Dependencies
- No new third-party dependencies required.
- Optional GitHub Actions runtime for automated gates.

### Features That Must NOT Be Impacted

1. **RF-001 solver/recommender deterministic behavior**
   - Preserve metric calculations and ranking semantics.

2. **RF-004 AI endpoint behavior**
   - Keep test/eval enhancements isolated from AI runtime logic.

3. **RF-005/RF-006 UI functionality**
   - Ensure RF-007 changes do not alter frontend runtime or API payload semantics.

### Risk Assessment

### Overall Risk Level: Medium

| Risk Category | Level | Description | Mitigation |
|--------------|-------|-------------|------------|
| Regression False Positives | Medium | stricter parity/diff checks may fail due representation drift | scope assertions to stable fields; tolerance config by field |
| Test Fragility | Medium | over-specified assertions may become brittle | keep deterministic ordering and compare key contract metrics only |
| Coverage Gap | Medium | parity may still miss edge cases | add additional parity case manifests incrementally |
| CI Runtime Growth | Low | extra gates can increase duration | split quick unit gate vs extended parity gate |
| Feature Coupling | Low | eval updates might leak into runtime code | keep logic inside eval and tests only |

#### Specific Risk 1: parity checks fail on non-material numeric formatting
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** centralized comparator that allows integer-rounding variance only on mm fields; strict exact comparison elsewhere.
- **Contingency:** output field-level diff report and allow explicit whitelist updates via reviewed changes.

#### Specific Risk 2: evaluator diagnostics remain insufficient for debugging
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** produce structured JSON diff output and concise console summary.
- **Contingency:** fallback debug mode with expanded mismatch dump.

#### Specific Risk 3: missing automated quality gates before releases
- **Probability:** High
- **Impact:** Medium
- **Mitigation:** add lightweight workflow invoking pytest + eval.
- **Contingency:** enforce pre-merge manual command checklist until workflow lands.

---

## Development Plan

## Implementation Approach: HYBRID (Modification + New Components)

### Rationale
Core RF-007 baseline exists and is passing, so the implementation should enhance diagnostics and add parity enforcement rather than rewrite existing tests.

### Strategy Summary
- **New Components:** 3 to 4
- **Modified Components:** 2 to 4
- **Unchanged Components:** solver/recommender runtime modules

## Files to MODIFY

### 1. Eval Harness
**File:** eval/run_eval.py

**Required Changes:**
1. Add normalized expected-vs-actual diff builder for each case.
2. Emit structured report object (for example JSON file under eval/reports/latest.json).
3. Preserve current console PASS/FAIL summary output.
4. Add optional flag to include sample parity checks in same run.

**Preservation Requirements:**
- Keep existing exit-code behavior (non-zero on failure).
- Keep compatibility with current eval/test_cases.json schema.

### 2. Eval Case Definitions
**File:** eval/test_cases.json

**Required Changes:**
1. Expand expected assertions for stable fields where appropriate.
2. Maintain existing four baseline scenarios unchanged.

### 3. Optional Gate Workflow
**File:** .github/workflows/quality-gates.yml (new if absent)

**Required Changes:**
1. Run scripts/tests pytest suite.
2. Run eval harness command.
3. Fail build if any step fails.

## Files to CREATE

### 1. Sample Parity Comparator
**File:** eval/sample_parity.py

**Purpose:**
- Load sample references and rebuilt outputs.
- Compare stable metrics and structure.
- Allow rounding-only tolerance on mm fields.
- Return human-readable and machine-readable diffs.

### 2. Parity Case Manifest
**File:** eval/sample_parity_cases.json

**Purpose:**
- Define sample run inputs, sample bundle paths, and asserted fields.
- Keep parity coverage explicit and extensible.

### 3. Parity Unit Tests
**File:** scripts/tests/test_sample_bundle_parity.py

**Purpose:**
- Enforce US-7.3 with deterministic assertions.
- Validate comparator tolerance rules and mismatch messaging.

### 4. Optional Negative Contract Tests
**File:** scripts/tests/test_contract_validation_negative.py

**Purpose:**
- Cover invalid/missing input contracts referenced in RF-007 implementation notes.

---

## Testing Strategy

### Unit Tests
1. Keep existing required tests green:
   - scripts/tests/test_solver_centered_strict_tolerances.py
   - scripts/tests/test_stacking_model.py
   - scripts/tests/test_layer_count_exceedance_highlight.py
2. Add parity test file for sample bundle comparison.
3. Add comparator unit tests for field-level tolerance handling.

### Eval Tests
1. Run eval/run_eval.py and validate:
   - four canonical cases still pass,
   - per-case diagnostics include expected-vs-actual mismatch details.
2. Validate optional report artifact generation (JSON).

### Regression
1. Run full scripts/tests suite.
2. Run eval harness before merge.
3. Ensure no solver/runtime behavior changes introduced by test-only additions.

### Validation Commands
- c:/python314/python.exe -m pytest scripts/tests -q
- $env:PYTHONPATH="scripts"; c:/python314/python.exe eval/run_eval.py
- Optional CI local dry-run: workflow-equivalent command sequence

---

## Developer Checklist

### Preparation
- [ ] Review RF-007 feature specification
- [ ] Review existing eval and test files
- [ ] Confirm sample bundle structures and stable assertion fields

### Implementation
- [ ] Modify eval/run_eval.py for structured diffs/report output
- [ ] Add sample parity comparator module
- [ ] Add parity case manifest
- [ ] Add sample parity unit tests
- [ ] Add optional negative contract tests
- [ ] Add workflow gate file if absent

### Testing
- [ ] Run targeted new tests (parity + comparator)
- [ ] Run full scripts/tests suite
- [ ] Run eval harness and inspect diff output format
- [ ] Verify baseline 4 eval cases still pass

### Validation
- [ ] Confirm mm-only rounding tolerance policy is enforced exactly
- [ ] Confirm non-mm metric mismatches fail clearly
- [ ] Confirm no runtime solver/API behavior changes

### Completion
- [ ] Update RF-007 feature status to Implemented after delivery
- [ ] Create RF-007 implementation complete report

---

## Additional Resources

- Feature specification: specs/features/007-testing-evaluation-and-quality-gates.md
- Existing tests: scripts/tests/*
- Existing evaluator: eval/run_eval.py
- Reference samples: samples/R1_perfect_fit/bundle.json, samples/R13_underhang_tolerance/bundle.json

---

**END OF IMPLEMENTATION PLAN**
