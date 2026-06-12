import { useEffect, useMemo, useState } from "react";
import type { Bundle } from "../api/types";

interface PalletDigitalTwin3DProps {
  bundle: Bundle;
}

type MotionProfile = "idle" | "city" | "highway" | "hard_brake";

interface Point3D {
  x: number;
  y: number;
  z: number;
}

interface Point2D {
  x: number;
  y: number;
}

interface Cuboid {
  id: string;
  x: number;
  y: number;
  z: number;
  dx: number;
  dy: number;
  dz: number;
}

interface ProfileCfg {
  baseG: number;
  vibrationG: number;
  frequencyHz: number;
}

const MOTION_PROFILE: Record<MotionProfile, ProfileCfg> = {
  idle: { baseG: 0.05, vibrationG: 0.04, frequencyHz: 1.1 },
  city: { baseG: 0.22, vibrationG: 0.12, frequencyHz: 2.1 },
  highway: { baseG: 0.36, vibrationG: 0.16, frequencyHz: 2.8 },
  hard_brake: { baseG: 0.62, vibrationG: 0.24, frequencyHz: 3.4 },
};

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

function projectIso(point: Point3D, yawRad: number, elevationScale: number): Point2D {
  const ux = point.x - point.y;
  const uy = (point.x + point.y) * 0.5;
  return {
    x: ux * Math.cos(yawRad),
    y: uy * Math.sin(yawRad) - point.z * elevationScale,
  };
}

function toSvgPoints(points: Point2D[], sx: number, sy: number, ox: number, oy: number): string {
  return points
    .map((p) => `${(ox + p.x * sx).toFixed(2)},${(oy + p.y * sy).toFixed(2)}`)
    .join(" ");
}

function buildStack(layout: Bundle["recommender"]["solutions"][number]["layout"], layers: number, caseHeight: number): Cuboid[] {
  const out: Cuboid[] = [];
  for (let layer = 0; layer < Math.max(1, layers); layer += 1) {
    for (let i = 0; i < layout.length; i += 1) {
      const p = layout[i];
      out.push({
        id: `L${layer + 1}-C${i + 1}`,
        x: p.x_mm,
        y: p.y_mm,
        z: layer * caseHeight,
        dx: p.dim_x_mm,
        dy: p.dim_y_mm,
        dz: caseHeight,
      });
    }
  }
  return out;
}

function simulateStep(
  boxes: Cuboid[],
  tSec: number,
  palletLength: number,
  palletWidth: number,
  layerCount: number,
  caseHeight: number,
  profile: ProfileCfg,
  mu: number
): {
  boxes: Cuboid[];
  maxSlipMm: number;
  overhangEvents: number;
  collisionEvents: number;
  score: number;
  lateralShiftMm: number;
} {
  const stackHeight = Math.max(1, layerCount * caseHeight);
  const accelG = profile.baseG + profile.vibrationG * Math.sin(2 * Math.PI * profile.frequencyHz * tSec);
  const slipRatio = Math.max(0, (Math.abs(accelG) - mu) / Math.max(0.01, mu));

  let maxSlipMm = 0;
  let overhangEvents = 0;
  let collisionEvents = 0;

  const shifted = boxes.map((b) => {
    const layerFactor = 1 + (b.z / stackHeight) * 0.6;
    const xNorm = b.x / Math.max(1, palletLength);
    const differential = 1 + 0.12 * xNorm;
    const shiftX = slipRatio * (18 + 42 * layerFactor) * differential;
    maxSlipMm = Math.max(maxSlipMm, shiftX);
    const nb = { ...b, x: b.x + shiftX };
    if (nb.x < 0 || nb.y < 0 || nb.x + nb.dx > palletLength || nb.y + nb.dy > palletWidth) {
      overhangEvents += 1;
    }
    return nb;
  });

  for (let i = 0; i < shifted.length; i += 1) {
    const a = shifted[i];
    for (let j = i + 1; j < shifted.length; j += 1) {
      const b = shifted[j];
      if (!(a.x + a.dx <= b.x || b.x + b.dx <= a.x || a.y + a.dy <= b.y || b.y + b.dy <= a.y)) {
        collisionEvents += 1;
      }
    }
  }

  const cx = shifted.reduce((acc, b) => acc + b.x + b.dx / 2, 0) / Math.max(1, shifted.length);
  const cy = shifted.reduce((acc, b) => acc + b.y + b.dy / 2, 0) / Math.max(1, shifted.length);
  const lateralShiftMm = Math.hypot(cx - palletLength / 2, cy - palletWidth / 2);
  const lateralNorm = lateralShiftMm / Math.max(1, Math.min(palletLength, palletWidth) * 0.5);

  const risk = lateralNorm * 55 + (maxSlipMm / 120) * 60 + Math.min(30, overhangEvents / 30);
  const score = clamp(Math.round(100 - risk), 0, 100);

  return { boxes: shifted, maxSlipMm, overhangEvents, collisionEvents, score, lateralShiftMm };
}

function stabilityLabel(score: number): string {
  if (score < 60) {
    return "High Risk";
  }
  if (score < 78) {
    return "Moderate";
  }
  return "Stable";
}

function Scene({
  title,
  boxes,
  palletLength,
  palletWidth,
  yawRad,
  elevation,
  width,
  height,
}: {
  title: string;
  boxes: Cuboid[];
  palletLength: number;
  palletWidth: number;
  yawRad: number;
  elevation: number;
  width: number;
  height: number;
}): JSX.Element {
  const sx = 0.35;
  const sy = 0.35;
  const ox = width / 2;
  const oy = height * 0.7;

  const palletTop = useMemo(() => {
    const a = projectIso({ x: 0, y: 0, z: 0 }, yawRad, elevation);
    const b = projectIso({ x: palletLength, y: 0, z: 0 }, yawRad, elevation);
    const c = projectIso({ x: palletLength, y: palletWidth, z: 0 }, yawRad, elevation);
    const d = projectIso({ x: 0, y: palletWidth, z: 0 }, yawRad, elevation);
    return toSvgPoints([a, b, c, d], sx, sy, ox, oy);
  }, [elevation, ox, oy, palletLength, palletWidth, sx, sy, yawRad]);

  const shapes = useMemo(() => {
    const sorted = [...boxes].sort((a, b) => a.x + a.y + a.z - (b.x + b.y + b.z));
    return sorted.map((box) => {
      const p100 = projectIso({ x: box.x + box.dx, y: box.y, z: box.z }, yawRad, elevation);
      const p110 = projectIso({ x: box.x + box.dx, y: box.y + box.dy, z: box.z }, yawRad, elevation);
      const p010 = projectIso({ x: box.x, y: box.y + box.dy, z: box.z }, yawRad, elevation);

      const p001 = projectIso({ x: box.x, y: box.y, z: box.z + box.dz }, yawRad, elevation);
      const p101 = projectIso({ x: box.x + box.dx, y: box.y, z: box.z + box.dz }, yawRad, elevation);
      const p111 = projectIso({ x: box.x + box.dx, y: box.y + box.dy, z: box.z + box.dz }, yawRad, elevation);
      const p011 = projectIso({ x: box.x, y: box.y + box.dy, z: box.z + box.dz }, yawRad, elevation);

      return {
        id: box.id,
        top: toSvgPoints([p001, p101, p111, p011], sx, sy, ox, oy),
        sideX: toSvgPoints([p100, p110, p111, p101], sx, sy, ox, oy),
        sideY: toSvgPoints([p010, p110, p111, p011], sx, sy, ox, oy),
      };
    });
  }, [boxes, elevation, ox, oy, sx, sy, yawRad]);

  return (
    <div className="rounded-sm border border-[rgb(var(--line))] bg-[rgb(var(--panel2))]">
      <div className="border-b border-[rgb(var(--line))] px-3 py-2 text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">{title}</div>
      <svg viewBox={`0 0 ${width} ${height}`} className="h-[360px] w-full">
        <rect x="0" y="0" width={width} height={height} fill="rgba(255,255,255,0.02)" />
        <polygon points={palletTop} fill="#FFFFFF" opacity="0.92" stroke="#333333" strokeWidth="1" />
        {shapes.map((shape) => (
          <g key={shape.id}>
            <polygon points={shape.sideX} fill="#1976D2" opacity="0.86" stroke="#111" strokeWidth="0.5" />
            <polygon points={shape.sideY} fill="#1565C0" opacity="0.86" stroke="#111" strokeWidth="0.5" />
            <polygon points={shape.top} fill="#1E88E5" opacity="0.96" stroke="#111" strokeWidth="0.5" />
          </g>
        ))}
      </svg>
    </div>
  );
}

export function PalletDigitalTwin3D({ bundle }: PalletDigitalTwin3DProps): JSX.Element | null {
  const [yawDeg, setYawDeg] = useState(38);
  const [elevation, setElevation] = useState(0.62);
  const [motionProfile, setMotionProfile] = useState<MotionProfile>("city");
  const [frictionMu, setFrictionMu] = useState(0.38);
  const [playing, setPlaying] = useState(true);
  const [timeSec, setTimeSec] = useState(0);

  const solutions = bundle.recommender.solutions;
  const after = solutions[0];
  const before = useMemo(
    () => solutions.find((s) => String(s.solution_id).startsWith("grid_")) ?? solutions[1] ?? solutions[0],
    [solutions]
  );

  if (!after?.layout?.length) {
    return null;
  }

  const palletLength = bundle.request.pallet.length_mm;
  const palletWidth = bundle.request.pallet.width_mm;
  const caseHeight = bundle.request.case.height_mm;
  const layerCount = bundle.request.stack.layer_count;

  useEffect(() => {
    if (!playing) {
      return;
    }
    const handle = setInterval(() => {
      setTimeSec((prev) => prev + 1 / 24);
    }, 1000 / 24);
    return () => clearInterval(handle);
  }, [playing]);

  const beforeBoxes = useMemo(() => buildStack(before.layout ?? [], layerCount, caseHeight), [before.layout, caseHeight, layerCount]);
  const afterBoxes = useMemo(() => buildStack(after.layout ?? [], layerCount, caseHeight), [after.layout, caseHeight, layerCount]);

  const profileCfg = MOTION_PROFILE[motionProfile];
  const beforeStep = useMemo(
    () => simulateStep(beforeBoxes, timeSec, palletLength, palletWidth, layerCount, caseHeight, profileCfg, frictionMu),
    [beforeBoxes, timeSec, palletLength, palletWidth, layerCount, caseHeight, profileCfg, frictionMu]
  );
  const afterStep = useMemo(
    () => simulateStep(afterBoxes, timeSec, palletLength, palletWidth, layerCount, caseHeight, profileCfg, frictionMu),
    [afterBoxes, timeSec, palletLength, palletWidth, layerCount, caseHeight, profileCfg, frictionMu]
  );

  const yawRad = (yawDeg * Math.PI) / 180;
  const delta = afterStep.score - beforeStep.score;

  return (
    <section className="card p-5 animate-in">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm uppercase tracking-[0.16em] text-[rgb(var(--muted))]">3D Physics Twin</h3>
          <p className="mt-2 text-sm text-[rgb(var(--muted))]">
            Time-step vibration and slip simulation with live before/after 3D comparison for truck loading risk.
          </p>
        </div>
        <div className="rounded-sm border border-[rgb(var(--line))] bg-[rgb(var(--panel2))] px-4 py-2 text-right">
          <div className="text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">Stability Delta</div>
          <div className="text-xl font-semibold text-[rgb(var(--text))]">{delta >= 0 ? `+${delta}` : delta}</div>
        </div>
      </div>

      <div className="mb-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <label className="text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">
          Camera yaw
          <input type="range" min={20} max={60} value={yawDeg} onChange={(e) => setYawDeg(Number(e.target.value))} className="mt-2 w-full" />
        </label>
        <label className="text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">
          Elevation depth
          <input
            type="range"
            min={0.4}
            max={0.9}
            step={0.05}
            value={elevation}
            onChange={(e) => setElevation(Number(e.target.value))}
            className="mt-2 w-full"
          />
        </label>
        <label className="text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">
          Friction mu
          <input
            type="range"
            min={0.2}
            max={0.8}
            step={0.01}
            value={frictionMu}
            onChange={(e) => setFrictionMu(Number(e.target.value))}
            className="mt-2 w-full"
          />
        </label>
        <label className="text-xs uppercase tracking-[0.12em] text-[rgb(var(--muted))]">
          Truck profile
          <select
            value={motionProfile}
            onChange={(e) => setMotionProfile(e.target.value as MotionProfile)}
            className="mt-2 w-full rounded-sm border border-[rgb(var(--line))] bg-[rgb(var(--panel))] px-2 py-2 text-sm"
          >
            <option value="idle">Idle warehouse</option>
            <option value="city">City route</option>
            <option value="highway">Highway route</option>
            <option value="hard_brake">Hard brake event</option>
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={() => setPlaying((p) => !p)}
            className="w-full rounded-sm border border-[rgb(var(--line))] bg-[rgb(var(--panel))] px-3 py-2 text-sm"
          >
            {playing ? "Pause simulation" : "Resume simulation"}
          </button>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div>
          <Scene
            title={`BEFORE (${before.solution_id})`}
            boxes={beforeStep.boxes}
            palletLength={palletLength}
            palletWidth={palletWidth}
            yawRad={yawRad}
            elevation={elevation}
            width={760}
            height={430}
          />
          <div className="mt-2 text-xs text-[rgb(var(--muted))]">
            Score {beforeStep.score}/100 ({stabilityLabel(beforeStep.score)}) | Slip {beforeStep.maxSlipMm.toFixed(1)} mm | Overhang events {beforeStep.overhangEvents} | Collisions {beforeStep.collisionEvents}
          </div>
        </div>

        <div>
          <Scene
            title={`AFTER (${after.solution_id})`}
            boxes={afterStep.boxes}
            palletLength={palletLength}
            palletWidth={palletWidth}
            yawRad={yawRad}
            elevation={elevation}
            width={760}
            height={430}
          />
          <div className="mt-2 text-xs text-[rgb(var(--muted))]">
            Score {afterStep.score}/100 ({stabilityLabel(afterStep.score)}) | Slip {afterStep.maxSlipMm.toFixed(1)} mm | Overhang events {afterStep.overhangEvents} | Collisions {afterStep.collisionEvents}
          </div>
        </div>
      </div>

      <div className="mt-4 text-xs text-[rgb(var(--muted))]">
        Time-step: {(1 / 24).toFixed(4)} s | Sim time: {timeSec.toFixed(2)} s | Friction: {frictionMu.toFixed(2)} | Base accel: {profileCfg.baseG.toFixed(2)}g | Vibration: {profileCfg.vibrationG.toFixed(2)}g @ {profileCfg.frequencyHz.toFixed(1)} Hz
      </div>
    </section>
  );
}
