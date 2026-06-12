from __future__ import annotations

from .contracts import parse_request
from .models import dataclass_to_dict
from .solver import solve
from .stacking import compute_stacking_analysis


def recommend(req: dict, max_options: int = 25) -> dict:
    normalized = parse_request(req)
    solver_result = solve(normalized, max_options=max_options)

    top_cases_per_layer = 0
    if solver_result.solutions:
        top_cases_per_layer = solver_result.solutions[0].metrics.cases_per_layer

    stacking = compute_stacking_analysis(normalized, top_cases_per_layer)

    return {
        "status": solver_result.status,
        "reasons": [dataclass_to_dict(r) for r in solver_result.reasons],
        "solutions": [dataclass_to_dict(s) for s in solver_result.solutions],
        "stacking": dataclass_to_dict(stacking),
    }
