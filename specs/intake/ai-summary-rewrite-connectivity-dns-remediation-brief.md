# Requirement Brief - AI Summary Rewrite Connectivity and DNS Remediation

**Date:** 2026-06-30  
**Request Type:** Bug | Workflow Improvement

## Business Ask
- Restore AI rewrite availability by fixing endpoint connectivity and DNS for the rewrite provider host.
- Avoid stale deterministic fallback reuse by forcing regeneration or running a new run context.
- Use latest trace reason codes to confirm remediation status.

## Problem Statement
- Summary requests can remain in deterministic fallback mode after provider connectivity failure.
- Reuse-policy cache can continue serving fallback artifacts, obscuring whether connectivity has been restored.

## Business Objective
- Recover rewrite-success behavior for affected runs/environments.
- Reduce repeated fallback user experience caused by stale artifact reuse.
- Improve operational confidence with reason-code-driven verification.

## Target Users
- Internal planning users consuming AI-enhanced summaries.
- Platform maintainers responsible for runtime endpoint, DNS, and environment configuration.
- Support/product stakeholders monitoring summary reliability.

## Carlsberg Context
- In operations and planning workflows, summary reliability affects decision speed and trust.
- Persistent fallback behavior can increase manual rework and support escalation volume.

## User Journey / Workflow
1. Validate endpoint host resolution/connectivity for the configured rewrite provider.
2. Trigger force regeneration (or new run) so cached fallback artifact is not reused.
3. Re-check newest trace events and reason codes.
4. Confirm rewrite-success path or escalate with updated failure class evidence.

## Functional Requirements
- Verify `AZURE_OAI_RESPONSES_ENDPOINT` host validity and DNS reachability in active runtime.
- Ensure users/operators can force fresh rewrite attempt for affected runs.
- Confirm latest `ai_calls.jsonl` entries expose actionable `reason_code` and mode values.
- Preserve deterministic fallback as safe degraded-path behavior.

## Non-Functional Expectations
- Fast diagnosis and remediation turnaround.
- Stable and searchable diagnostics for fallback root-cause classes.
- Safe diagnostics without secret leakage.

## Constraints and Assumptions
- External network/provider conditions may intermittently fail.
- Existing RF-011 tracing fields are available for diagnosis.
- Public summary response contracts remain unchanged.

## Success Criteria
- Forced regeneration yields rewrite-success when connectivity is fixed.
- Cached fallback no longer masks current provider health state.
- Latest trace events provide clear reason-code classification for failures.

## Risks and Dependencies
- DNS/network policy restrictions outside application code control may persist.
- Misconfigured endpoint or credentials may continue to force fallback.
- Small post-fix sample size may require repeated validation runs.

## Open Questions
- Which environment is currently primary for remediation: local, Docker local, or hosted runtime?
- Is the failure limited to DNS resolution, or does it include auth/TLS path issues?
- Who owns endpoint and DNS policy changes for the affected runtime?

## Recommended Next Agent
- `infra_agent`

## Handoff Rationale
- The request is runtime connectivity and environment remediation, which should be validated first through infrastructure/setup checks before any additional feature or code planning.
