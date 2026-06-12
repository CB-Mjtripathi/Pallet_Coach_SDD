from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PalletInput:
    type: str
    length_mm: int
    width_mm: int


@dataclass(frozen=True)
class CaseInput:
    length_mm: int
    width_mm: int
    height_mm: int
    weight_kg: float | None = None


@dataclass(frozen=True)
class StackInput:
    layer_count: int


@dataclass(frozen=True)
class ToleranceInput:
    max_overhang_l_mm: int
    max_overhang_w_mm: int
    max_underhang_l_mm: int
    max_underhang_w_mm: int


@dataclass(frozen=True)
class ConstraintInput:
    allow_rotation_90: bool = True
    allow_interlock: bool = False
    auto_underhang: bool = False
    max_pallet_weight_kg: float | None = None
    max_overhang_percent: float | None = None
    min_underhang_percent: float | None = None


@dataclass(frozen=True)
class SolveRequestNormalized:
    request_id: str | None
    meta: dict[str, Any]
    pallet: PalletInput
    case: CaseInput
    stack: StackInput
    tolerances: ToleranceInput
    constraints: ConstraintInput


@dataclass(frozen=True)
class Placement:
    x_mm: float
    y_mm: float
    rotation_deg: int
    dim_x_mm: float
    dim_y_mm: float


@dataclass(frozen=True)
class EdgeClearance:
    left_mm: float
    right_mm: float
    bottom_mm: float
    top_mm: float


@dataclass(frozen=True)
class FootprintBBox:
    min_x_mm: float
    min_y_mm: float
    max_x_mm: float
    max_y_mm: float


@dataclass(frozen=True)
class InnerAxisSegments:
    x_segments_mm: list[float]
    y_segments_mm: list[float]


@dataclass(frozen=True)
class SolutionMetrics:
    cases_per_layer: int
    total_cases: int
    total_height_mm: int
    total_weight_kg: float | None
    area_fill_efficiency_pct: float
    footprint_bbox_mm: FootprintBBox
    edge_clearance_mm: EdgeClearance
    tolerance_pass: bool
    inner_axis_segments_mm: InnerAxisSegments
    interlock: bool


@dataclass(frozen=True)
class Solution:
    solution_id: str
    layout: list[Placement]
    metrics: SolutionMetrics


@dataclass(frozen=True)
class SolverReason:
    code: str
    message: str


@dataclass(frozen=True)
class SolverResult:
    status: str
    reasons: list[SolverReason] = field(default_factory=list)
    solutions: list[Solution] = field(default_factory=list)


@dataclass(frozen=True)
class RecommendedRange:
    min: int
    max: int


@dataclass(frozen=True)
class StackingAnalysis:
    current_layers: int
    max_stack_height_mm: int
    pallet_height_mm: int
    current_stack_height_mm: int
    headroom_mm: int
    height_ceiling_layers: int
    weight_ceiling_layers: int | None
    effective_ceiling_layers: int
    recommended_layers_range: RecommendedRange
    max_layers_at_max_height: int
    addable_layers_to_max_height: int
    warnings: list[str]
    assumptions: dict[str, int]


def dataclass_to_dict(value: Any) -> Any:
    return asdict(value)
