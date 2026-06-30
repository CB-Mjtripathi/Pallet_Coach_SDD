# RF-011 Reliability Baseline Report

Date: 2026-06-30
Scope: Baseline rewrite/fallback behavior before RF-011 trace-shape adoption
Data source: 50 trace files under `04_Output/**/ai_traces/ai_calls.jsonl`
Operations included: `summary`, `summary_ui`

## Method

1. Baseline cohort is defined as summary events without RF-011 fields (`rewrite_mode` and `readiness_status`).
2. For legacy events, mode is inferred as:
- `deterministic_fallback` when outcome starts with `fallback` or reason indicates provider failure.
- `rewrite_success` when outcome is `generation`/`reused_artifact` or reason indicates success/reuse.
- `unknown` when legacy event shape is insufficient to classify.

## Baseline Distribution

- Total baseline events: 80
- Classified events: 29
- Unclassified (`unknown`): 51

Classified mode distribution:
- `rewrite_success`: 20
- `deterministic_fallback`: 9

Classified rates:
- Rewrite success rate: 68.97% (20/29)
- Fallback rate: 31.03% (9/29)

## Endpoint Breakdown

- `/api/summary_ui`: 18 rewrite_success, 7 deterministic_fallback
- `/api/summary`: 2 rewrite_success, 2 deterministic_fallback
- `unknown` endpoint (legacy trace shape): 51 unknown

## Legacy Reason-Code Distribution (Baseline Cohort)

- `identical_fingerprint`: 16
- `provider_timeout`: 3
- `provider_error`: 4
- `provider_exception`: 2
- `provider_success`: 4
- `unknown`: 51

## Notes

- Baseline traces are heterogeneous and include legacy events without standardized RF-011 dimensions.
- Baseline rates should be interpreted from classified events only.
- This report is intended as the comparison anchor for post-change monitoring.
