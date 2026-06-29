# Architecture Summary - RF-010 AI Summary Latency Optimization

Date: 2026-06-29
Scope: RF-010 AI Summary Latency Optimization
Source Feature: specs/features/010-ai-summary-latency-optimization.md
Source Plan: specs/implementation-plans/RF-010-ai-summary-latency-optimization-implementation-plan.md
Supporting Inputs: specs/intake/ai-summary-latency-optimization-brief.md, specs/features/FEATURE_DEPENDENCY_MAP.mermaid, PRODUCT_BACKLOG.md

## Architecture Type
- Target State with Delta Summary

## Purpose
Lock architecture-level policy and flow decisions that are open in the implementation plan so development can proceed without pre-dev blockers.

## Decision Records
- ADR-RF010-001: Latency target framework and release gate model
- ADR-RF010-002: Reuse freshness policy and eligibility model
- ADR-RF010-003: Timeout/retry/fallback architecture
- ADR-RF010-004: Quality guardrails under latency pressure
- ADR-RF010-005: Scope guardrails and non-goals for RF-010

## Architecture Overview
RF-010 introduces a policy-driven summary orchestration layer inside existing summary endpoints. The layer classifies each request into reuse, generation, or fallback outcomes and emits stage-level telemetry for release gates. The architecture keeps endpoint contracts unchanged, preserves deterministic fallback behavior, and hardens UI responsiveness via non-blocking status plus in-flight dedup semantics.

## Delta Summary
Unchanged:
- Existing endpoint contracts for POST /api/summary and POST /api/summary_ui.
- Existing artifacts recommendation_summary.md and summary_ui.md.
- Existing Azure OpenAI provider integration and trace persistence location.

Modified:
- Summary endpoint orchestration to include policy evaluation and deterministic path classification.
- Trace payload schema to include stage timings, payload profile, and outcome reason codes.
- UI request lifecycle handling to prevent duplicate equivalent in-flight calls.

New:
- Formal latency profile framework with p50/p95/p99 gates by endpoint and profile.
- Reuse eligibility policy based on strict fingerprint identity plus bounded near-identical path.
- Timeout/retry/fallback policy envelope with path-specific time budget and bounded retries.
- Quality guardrail checks that constrain what latency optimizations are allowed.

## Locked Decisions

### ADR-RF010-001: Latency Target Framework
Status: Accepted

Decision:
- Use profile-specific targets for Small, Medium, Large bundles.
- Enforce p50 and p95 as hard release gates.
- Treat p99 as phased gate:
  - Release 1 (RF-010): non-regression gate (must not degrade by more than 10 percent vs baseline by endpoint/profile).
  - Release 2 (post RF-010 hardening): convert p99 to hard absolute SLO thresholds.
- Keep separate path budgets for summary_ui reuse vs summary_ui generation.

Locked Gate Set:
- /api/summary and /api/summary_ui generation:
  - p50 hard gate
  - p95 hard gate
  - p99 non-regression gate for RF-010 release
- /api/summary_ui reuse path:
  - p50/p95/p99 hard gates due to deterministic low-latency objective
- Reliability gate:
  - endpoint error rate increase must be <= +1.0 percentage point from approved baseline

Rationale:
- Resolves open blocker on p95/p99 governance while avoiding release freeze due to provider tail variance.
- Aligns with feature requirement for measurable and auditable targets.

Traceability:
- RF-010 US-10.1, US-10.5
- Implementation plan sections 4, 10

### ADR-RF010-002: Reuse Freshness Policy
Status: Accepted

Decision:
- Introduce two-tier reuse eligibility:
  - Tier A Identical Reuse (default): fingerprint exact match required.
  - Tier B Near-Identical Reuse (opt-in by policy flag): allowed only when all guarded fields match and change is within bounded tolerance.
- Fingerprint basis must include run_id, summary mode, normalized minimized-context hash, source artifact revision marker, and model configuration key.
- Freshness TTL:
  - Identical reuse: 24 hours max age.
  - Near-identical reuse: 30 minutes max age.
- Force regenerate bypasses both tiers.
- Every reuse decision must emit explicit reason_code and policy_tier in trace.

Near-Identical Allowed Conditions:
- No structural change in minimized context shape.
- Numeric drift only in non-safety-critical metrics and within policy threshold.
- No changes to prompt template version, model deployment identifier, or safety mode.

Near-Identical Disallowed Conditions:
- Any safety-related context change.
- Any rules/policy/config version change.
- Any missing provenance fields for deterministic comparison.

Rationale:
- Balances first-response speed and freshness guarantees.
- Prevents silent stale-output risk by constraining near-identical reuse with explicit policy and short TTL.

Traceability:
- RF-010 US-10.3, US-10.5
- Implementation plan sections 3.2, 5 Phase 3, 10

### ADR-RF010-003: Timeout/Retry/Fallback Architecture
Status: Accepted

Decision:
- Apply single-request latency budget partitioning:
  - T_total (endpoint budget) = T_pre + T_provider + T_post.
- Provider policy:
  - One primary provider attempt.
  - At most one retry only on transient transport/timeouts and only if remaining budget >= retry_min_budget.
  - No retry on semantic/provider 4xx errors.
- Retry strategy:
  - bounded jittered backoff capped by remaining endpoint budget.
- Fallback trigger:
  - Trigger fallback when provider path cannot complete within remaining budget or terminal provider error occurs.
- Fallback response:
  - deterministic, clearly labeled, non-fabricated summary shell.
  - classification in trace: fallback_timeout or fallback_error.

Path Precedence:
1. Reuse eligible -> return reuse.
2. Reuse not eligible -> provider generation path.
3. Provider path violates budget or fails terminally -> fallback.

Rationale:
- Controls tail latency and avoids retry storms.
- Preserves reliability and transparency for operators and users.

Traceability:
- RF-010 US-10.3
- Implementation plan sections 3.2, 5 Phase 3, 7

### ADR-RF010-004: Quality Guardrails Under Latency Pressure
Status: Accepted

Decision:
- Latency optimization must be quality-safe by policy.
- Disallowed optimization shortcuts:
  - prompt truncation that removes required safety context.
  - suppression of failure state messaging.
  - serving fallback as if it were normal generation.
- Required checks per path:
  - Generation path: minimum structural completeness checks before persist/return.
  - Reuse path: provenance and freshness checks must pass before reuse return.
  - Fallback path: explicit status marker and deterministic text template.
- Release gate coupling:
  - latency gate pass is invalid if quality parity smoke checks fail.

Rationale:
- Closes open question on acceptable trade-offs by defining strict boundaries: no hidden quality degradation for latency gains.

Traceability:
- RF-010 US-10.3, US-10.5
- Intake brief constraints and success criteria
- Implementation plan sections 4.3, 7, 8, 10

### ADR-RF010-005: Non-Goals and Scope Guardrails
Status: Accepted

Decision:
RF-010 will not include:
- model/provider migration,
- response schema changes,
- broad observability platform migration,
- summary content-style redesign,
- full UI redesign outside summary state handling,
- cross-run semantic cache that spans incompatible model/prompt versions.

Guardrails:
- Architecture changes must remain endpoint-local plus adjacent tracing/UI state boundaries.
- Any proposal introducing new persistent cache infrastructure requires separate feature/ADR.
- Any request to relax safety checks requires explicit product + reliability sign-off outside RF-010.

Rationale:
- Prevents scope creep and protects delivery of high-priority backlog item RF-010 in current sprint.

Traceability:
- PRODUCT_BACKLOG priority context
- RF-010 scope/non-goals
- Implementation plan section 1.1

## Component Responsibilities
| Component | Responsibility | RF-010 Traceability |
|---|---|---|
| Summary API Orchestrator | Evaluate reuse policy, apply timeout/retry/fallback policy, return classified outcome | US-10.2, US-10.3 |
| Reuse Policy Evaluator | Compute fingerprint, enforce freshness TTL, assign reason codes | US-10.3 |
| Provider Adapter | Execute bounded provider calls with stage timings and retry rules | US-10.2, US-10.3 |
| Trace/Telemetry Emitter | Emit stage latencies, payload profile, outcome class, policy tier | US-10.1, US-10.5 |
| UI Summary State Controller | Non-blocking state updates and in-flight dedup per run/mode | US-10.4 |

## Key Flows (Locked)
1. Request classified by payload profile and policy context.
2. Reuse eligibility evaluated before model invocation.
3. If non-reuse, provider call executes inside bounded budget with at most one transient retry.
4. On budget exhaustion or terminal error, deterministic fallback is returned.
5. All paths emit trace metadata with outcome, timings, and reason codes.

## Diagram Artifacts
- specs/architecture/diagrams/RF-010-ai-summary-latency-optimization-architecture.mermaid
- specs/architecture/diagrams/RF-010-summary-request-policy-flow.mermaid

## Architecture Guardrails
- Keep SummaryResponse and SummaryUiResponse contracts unchanged.
- Keep current artifact file naming/placement behavior stable.
- All policy decisions must be auditable from trace and run artifacts.
- Release decision requires both latency gate pass and quality parity pass.

## Remaining Risks
- Provider-side latency variance may still dominate large-profile p99 tails.
- Near-identical policy thresholds may need one calibration iteration from production-like data.
- Retry budget tuning can be environment-sensitive and requires controlled canary validation.

## Unresolved Items (Not Blocking Architecture)
- Exact numeric threshold for near-identical numeric drift tolerance requires baseline distribution data.
- Final p99 absolute SLO values are deferred to post RF-010 hardening milestone.

## Recommended Next Agent
- tech_lead

Reason:
- Architecture blockers are now resolved and converted to explicit policy decisions.
- Next step is implementation task breakdown updates and execution sequencing against these locked ADRs.
