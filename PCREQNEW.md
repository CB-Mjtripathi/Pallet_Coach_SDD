# Pallet Coach - Production Architecture and Build Specification

## 1. Product Overview

Pallet Coach is a production-grade web application for logistics planning that computes physically valid pallet stacking layouts, visualizes them in real-time 3D, and simulates truck/container loading sequences.

Primary outcomes:
- Maximize carton utilization while preserving strict safety constraints.
- Provide deterministic and explainable placement decisions.
- Offer interactive 3D validation for warehouse and planning teams.
- Export machine-readable and human-readable reports for operations.

Primary users:
- Supply chain planners
- Warehouse managers
- Logistics engineers

## 2. Scope and Functional Guarantees

The system must guarantee:
- No overhang beyond configured limits.
- No collision between boxes or pallets.
- No unsupported placement below minimum support percentage.
- Center of gravity (CoG) remains inside pallet footprint.
- No stack that violates height or load limits.

If any hard constraint is violated, the placement is rejected.

## 3. Input Model

### 3.1 Pallet Inputs
- lengthMm: number
- widthMm: number
- maxHeightMm: number
- maxLoadKg: number

### 3.2 Case Inputs
- lengthMm: number
- widthMm: number
- heightMm: number
- weightKg: number
- allowedRotations: "fixed" | "swap-lw"

### 3.3 Constraint Inputs
- maxStackHeightMm: number
- fragile: boolean
- stackable: boolean
- minSupportAreaPct: number
- allowInterlock: boolean

### 3.4 Truck/Container Inputs
- lengthMm: number
- widthMm: number
- heightMm: number
- maxPalletCount: number
- loadingDirection: "rear-to-front" | "front-to-rear" | "left-to-right" | "right-to-left"

## 4. System Architecture

### 4.1 Technology Stack
- Frontend: React + TypeScript + Vite
- 3D: three.js via @react-three/fiber and @react-three/drei
- State: Zustand
- Backend API: FastAPI (Python)
- Report generation: JSON + Markdown + optional PDF

### 4.2 Module Layout (Mandatory)

- /engine/packingEngine.ts
- /engine/physicsEngine.ts
- /engine/collisionEngine.ts
- /components/3DScene.tsx
- /hooks/usePalletEngine.ts
- /store/useAppStore.ts

### 4.3 Proposed Full Project Structure

```text
PalletCoach/
  backend/
    app/
      api/
        routes/
          solve.py
          simulate.py
          export.py
      core/
        config.py
      domain/
        models.py
        validators.py
      services/
        packing_service.py
        physics_service.py
        loading_service.py
      main.py
    tests/
      test_api_solve.py
      test_api_export.py
  frontend/
    src/
      engine/
        packingEngine.ts
        physicsEngine.ts
        collisionEngine.ts
        loadingEngine.ts
      components/
        layout/
          LeftControlPanel.tsx
          RightAnalyticsPanel.tsx
          BottomTimelinePanel.tsx
        scene/
          3DScene.tsx
          PalletMesh.tsx
          BoxesInstanced.tsx
          TruckScene.tsx
          DebugOverlays.tsx
      hooks/
        usePalletEngine.ts
        useSimulationLoop.ts
      store/
        useAppStore.ts
      types/
        domain.ts
      utils/
        math.ts
        export.ts
      pages/
        HomePage.tsx
      App.tsx
      main.tsx
    tests/
      engine/
        packingEngine.test.ts
        physicsEngine.test.ts
      components/
        3DScene.test.tsx
```

## 5. Data Structures

```ts
export type Vec3 = { x: number; y: number; z: number };

export type Dimensions = {
  lengthMm: number;
  widthMm: number;
  heightMm: number;
};

export type BoxRotation = 0 | 90;

export type Box = {
  id: string;
  dimensions: Dimensions;
  position: Vec3;
  rotation: BoxRotation;
  weightKg: number;
  fragile: boolean;
  stackable: boolean;
};

export type Pallet = {
  dimensions: Dimensions;
  maxLoadKg: number;
  stackedBoxes: Box[];
};

export type PlacementResult = {
  accepted: boolean;
  reason?:
    | "OVERHANG"
    | "UNSUPPORTED"
    | "COLLISION"
    | "COG_OUTSIDE_BASE"
    | "HEIGHT_EXCEEDED"
    | "WEIGHT_EXCEEDED"
    | "STACKING_FORBIDDEN";
};
```

## 6. Core Engine Design

### 6.1 Packing Engine

Algorithm strategy:
1. Sort candidate boxes by descending base area, then by descending weight (FFD).
2. For each box, evaluate all allowed orientations.
3. Generate candidate coordinates using a snap grid and skyline/frontier points.
4. Score each candidate with Best Fit heuristic:
   - primary: minimum wasted area in current layer
   - secondary: support quality
   - tertiary: CoG contribution and load balance
5. Validate with hard constraints before committing.

Scoring formula (example):

$$
score = w_1(1 - wastedAreaRatio) + w_2(supportPct) + w_3(balanceScore) - w_4(collisionRisk)
$$

TypeScript skeleton:

```ts
export function packCasesFFDAndBestFit(input: EngineInput): EngineOutput {
  const placed: Box[] = [];
  const sorted = [...input.cases].sort((a, b) => {
    const areaA = a.dimensions.lengthMm * a.dimensions.widthMm;
    const areaB = b.dimensions.lengthMm * b.dimensions.widthMm;
    if (areaB !== areaA) return areaB - areaA;
    return b.weightKg - a.weightKg;
  });

  for (const box of sorted) {
    const orientations = getAllowedOrientations(box, input.constraints);
    let bestCandidate: Candidate | null = null;

    for (const orientation of orientations) {
      const candidates = generateSnapCandidates(input.pallet, placed, orientation);
      for (const c of candidates) {
        const trial = withPlacement(box, orientation, c);
        const validation = validatePlacement(trial, placed, input);
        if (!validation.accepted) continue;

        const score = scoreCandidate(trial, placed, input);
        if (!bestCandidate || score > bestCandidate.score) {
          bestCandidate = { placement: trial, score };
        }
      }
    }

    if (bestCandidate) placed.push(bestCandidate.placement);
  }

  return buildEngineOutput(placed, input);
}
```

### 6.2 Physics and Stability Engine

Checks required per accepted placement:
- Dynamic CoG of full stack.
- Support area >= minSupportAreaPct for each non-ground box.
- Weight distribution across pallet quadrants for top-heaviness control.
- Layer pattern strategy: column or brick/interlock chosen automatically.

CoG formula:

$$
CoG_x = \frac{\sum_i m_i x_i}{\sum_i m_i}, \quad
CoG_y = \frac{\sum_i m_i y_i}{\sum_i m_i}, \quad
CoG_z = \frac{\sum_i m_i z_i}{\sum_i m_i}
$$

Support area ratio:

$$
supportPct = 100 \times \frac{overlapArea(box, supportSurface)}{baseArea(box)}
$$

TypeScript skeleton:

```ts
export function evaluateStability(boxes: Box[], pallet: Pallet, minSupportAreaPct: number): StabilityReport {
  const cog = computeCoG(boxes);
  const cogInsideBase =
    cog.x >= 0 && cog.x <= pallet.dimensions.lengthMm &&
    cog.y >= 0 && cog.y <= pallet.dimensions.widthMm;

  const unsupported = boxes.filter((b) => {
    if (b.position.z === 0) return false;
    const supportPct = computeSupportPct(b, boxes);
    return supportPct < minSupportAreaPct;
  });

  const loadDistribution = computeQuadrantLoads(boxes, pallet.dimensions);
  const topHeavyRisk = computeTopHeavyRisk(boxes);

  return {
    cog,
    cogInsideBase,
    unsupportedBoxIds: unsupported.map((b) => b.id),
    loadDistribution,
    topHeavyRisk,
    stable: cogInsideBase && unsupported.length === 0 && topHeavyRisk < 0.7,
  };
}
```

### 6.3 Collision Engine (AABB)

Collision detection uses axis-aligned bounding boxes.

Two boxes overlap iff all axis intervals overlap.

```ts
export function intersectsAABB(a: AABB, b: AABB): boolean {
  const x = a.minX < b.maxX && a.maxX > b.minX;
  const y = a.minY < b.maxY && a.maxY > b.minY;
  const z = a.minZ < b.maxZ && a.maxZ > b.minZ;
  return x && y && z;
}

export function hasCollision(candidate: Box, placed: Box[]): boolean {
  const ca = toAABB(candidate);
  for (const p of placed) {
    if (intersectsAABB(ca, toAABB(p))) return true;
  }
  return false;
}
```

### 6.4 Hard Constraint Gate

Placement is rejected when any condition fails:
- Overhang exists.
- Unsupported support area.
- AABB collision exists.
- CoG goes outside pallet base.
- Height limit exceeded.
- Weight limit exceeded.
- Item marked non-stackable but placed above ground.

## 7. Truck Loading Simulation

Simulation behavior:
- Build virtual truck bounding volume.
- Convert each completed pallet stack into a moving rigid unit.
- Animate each pallet along the loading direction path.
- Detect wall and pallet-to-pallet collisions.
- Enforce minimum spacing distance.

Loading sequence:
1. Reserve target slot grid in truck floor plan.
2. Move pallet along bezier or linear path.
3. Validate swept volume against static obstacles.
4. Commit final slot position.

## 8. Frontend UI/UX Specification

### 8.1 Main Layout

- Left Panel: controls and constraints.
- Center Canvas: live 3D scene.
- Right Panel: metrics and stability analytics.
- Bottom Timeline: layer and simulation playback.

### 8.2 Left Panel Controls

Sections:
- Pallet configuration
- Case configuration
- Constraints
- Truck/container setup

Actions:
- Generate Stack
- Auto Optimize
- Simulate Loading
- Reset

### 8.3 Center 3D Canvas

Must support:
- Orbit, pan, zoom camera controls.
- Smooth stacking animation.
- Invalid placements highlighted in red.
- Optional overlays and debug visualization.

### 8.4 Right Analytics Panel

Live metrics:
- Total cases placed
- Utilization percentage
- Total weight
- CoG coordinates
- Stability status: Stable or Risky
- Constraint failure breakdown counts

### 8.5 Bottom Timeline

Features:
- Per-layer step sequence
- Play/pause
- Scrubber
- Jump to event (collision, instability, unsupported)

## 9. Visual Debug Tools

Toggleable overlays:
- Show CoG marker
- Show bounding boxes
- Show support area heatmap
- Highlight unstable boxes

Recommended color rules:
- Stable: #16A34A
- Warning: #F59E0B
- Invalid: #DC2626
- CoG marker: #2563EB

## 10. Performance Requirements

Mandatory techniques:
- Use InstancedMesh for box rendering.
- Keep transforms in typed arrays for batch updates.
- Use React.memo for static panels.
- Use useMemo and selector-based Zustand subscriptions.
- Separate simulation step loop from React render loop.
- Frustum culling and optional LOD for large scenes.

Performance targets:
- 60 FPS target for common workloads.
- Stable interaction under 2,000 visible boxes.
- First simulation response under 1.5 seconds for normal input size.

## 11. Store and Hook Contracts

### 11.1 Zustand Store

```ts
type AppState = {
  pallet: PalletInput;
  caseInput: CaseInput;
  constraints: ConstraintInput;
  truck: TruckInput;
  boxes: Box[];
  analytics: Analytics;
  debug: DebugFlags;
  timeline: TimelineState;
  setPallet: (p: PalletInput) => void;
  setCaseInput: (c: CaseInput) => void;
  setConstraints: (c: ConstraintInput) => void;
  runGenerate: () => Promise<void>;
  runOptimize: () => Promise<void>;
  runLoadingSimulation: () => Promise<void>;
  resetAll: () => void;
};
```

### 11.2 usePalletEngine Hook

Responsibilities:
- Input normalization and validation.
- Invoke packing, collision, physics engines in sequence.
- Produce deterministic output artifacts for UI and export.
- Surface reasons for rejected placements.

## 12. 3D Scene Implementation Notes

Component breakdown:
- 3DScene.tsx: scene root, camera, lights, controls.
- PalletMesh.tsx: pallet geometry.
- BoxesInstanced.tsx: high-volume box rendering.
- TruckScene.tsx: truck shell and slots.
- DebugOverlays.tsx: CoG marker, AABB wireframes, heatmaps.

Animation approach:
- Keep simulation state in refs and immutable snapshots.
- Update transforms each frame via useFrame.
- Commit lightweight analytics updates at throttled interval.

## 13. API Contracts

### 13.1 POST /api/solve
Request:
- pallet
- case
- constraints
- truck

Response:
- placements
- analytics
- stabilityReport
- rejectedPlacements

### 13.2 POST /api/simulate-loading
Request:
- pallets[]
- truck

Response:
- sequenceFrames
- collisionEvents
- completionStatus

### 13.3 GET /api/export/{runId}
Returns bundle with:
- stackPlan.json
- stabilityReport.json
- screenshot.png
- optional report.pdf

## 14. Edge Cases and Handling

- Very small boxes on very large pallet:
  - enforce computational limits with adaptive grid resolution.
- Heavy top layers:
  - reject when top-heavy index exceeds threshold.
- Non-stackable items:
  - only allowed at z = 0 or rejected.
- Mixed orientations:
  - evaluate all legal rotations and choose best feasible score.

## 15. Export Features

Mandatory exports:
- JSON stacking plan
- 3D snapshot image
- stability report JSON and markdown

Optional export:
- PDF report containing:
  - input summary
  - utilization KPIs
  - stability diagnostics
  - loading sequence frames

## 16. Extensibility Design

Future-ready extension points:
- Add pallet templates and regional standards.
- Plug in AI optimizer strategy module.
- Swap simplified physics with Cannon.js adapter.
- Add multi-SKU mixed pallet planning.

Adapter pattern recommendation:

```ts
export interface PhysicsAdapter {
  step(state: SimulationState, dt: number): SimulationState;
  evaluate(state: SimulationState): StabilityReport;
}
```

## 17. Implementation Plan (Production)

Phase 1:
- Build deterministic packing + collision + support checks.
- Deliver core UI layout and 3D stack viewer.

Phase 2:
- Add dynamic loading simulation and event timeline.
- Add report generation and export API.

Phase 3:
- Add advanced optimization tuning and optional physics adapter.
- Add enterprise hardening: auth, audit trails, role controls.

## 18. Quality and Validation

Testing layers:
- Unit tests for each engine module.
- Property-based tests for collision and support checks.
- Integration tests for API solve and simulate flows.
- UI tests for controls, timeline, and debug toggles.
- Performance tests for FPS and solve latency budgets.

Acceptance criteria:
- No invalid placement can appear in final stack output.
- CoG, support, collision checks are consistent between UI and API.
- Exports match latest simulation state and are reproducible.

## 19. Security and Reliability

- Validate all numeric inputs and ranges server-side.
- Apply API rate limiting and request size limits.
- Sanitize file names and run IDs for exports.
- Log solve decisions with traceable reason codes.
- Use graceful fallback when optimization cannot improve baseline.

## 20. Ready-to-Implement Minimal Code Mapping

Required files and responsibilities:
- /engine/packingEngine.ts: FFD + Best Fit + orientation search.
- /engine/physicsEngine.ts: CoG, support, load spread, stability scoring.
- /engine/collisionEngine.ts: AABB overlap checks and occupancy validation.
- /components/3DScene.tsx: rendering, controls, animations, debug overlays.
- /hooks/usePalletEngine.ts: orchestration pipeline for generate/optimize/simulate.
- /store/useAppStore.ts: global app state and actions.

This specification is complete and can be used by engineering teams to implement a production-grade Pallet Coach application with strict physical constraints, deterministic optimization, and high-performance 3D interaction.
