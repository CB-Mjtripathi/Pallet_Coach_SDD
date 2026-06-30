# RF-011 Reliability Post-Change Report

Date: 2026-06-30
Scope: Post-change rewrite/fallback behavior after RF-011 instrumentation
Data source: 50 trace files under `04_Output/**/ai_traces/ai_calls.jsonl`
Operations included: `summary`, `summary_ui`

## Method

1. Post-change cohort is defined as summary events that include RF-011 dimensions (`rewrite_mode` and/or `readiness_status`).
2. Mode and reason code are taken directly from trace fields (no inference).

## Post-Change Distribution

- Total post-change events: 5
- Post-change run count: 5

Mode distribution:
- `rewrite_success`: 2
- `deterministic_fallback`: 3

Rates:
- Rewrite success rate: 40.00% (2/5)
- Fallback rate: 60.00% (3/5)

## Readiness and Reason Codes

Readiness status distribution:
- `pass`: 4
- `fail`: 1

Reason-code distribution:
- `provider_success`: 2
- `provider_error`: 1
- `timeout`: 1
- `config_missing`: 1

## Endpoint Breakdown

- `/api/summary`: 1 rewrite_success, 1 deterministic_fallback
- `/api/summary_ui`: 1 rewrite_success, 2 deterministic_fallback

## Comparison vs Baseline (Classified Events)

- Baseline rewrite success rate: 68.97% (20/29)
- Post-change rewrite success rate: 40.00% (2/5)
- Baseline fallback rate: 31.03% (9/29)
- Post-change fallback rate: 60.00% (3/5)

## Notes and Interpretation

- Current post-change sample is small (5 events) and should not be treated as a stable steady-state signal.
- The key RF-011 improvement is now present: all post-change fallback events are reason-coded and readiness-classified.
- Immediate operational action should focus on resolving `config_missing` and investigating timeout/provider errors.

## Next Monitoring Steps

1. Recompute this report after at least 50 post-change events.
2. Track success/fallback by environment (local, Docker local, hosted).
3. Use reason-code trend alerts for `config_missing`, `timeout`, and `provider_error`.
