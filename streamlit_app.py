from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pallet_coach.recommender import recommend  # noqa: E402

PALLET_PRESETS = {
    "Euro (1200 x 800)": {"type": "euro", "length_mm": 1200, "width_mm": 800},
    "Industrial (1200 x 1000)": {"type": "industrial", "length_mm": 1200, "width_mm": 1000},
    "Custom": {"type": "custom", "length_mm": 1200, "width_mm": 800},
}


def _box_mesh(x: float, y: float, z: float, dx: float, dy: float, dz: float, color: str, name: str) -> go.Mesh3d:
    x0, x1 = x, x + dx
    y0, y1 = y, y + dy
    z0, z1 = z, z + dz

    vertices_x = [x0, x1, x1, x0, x0, x1, x1, x0]
    vertices_y = [y0, y0, y1, y1, y0, y0, y1, y1]
    vertices_z = [z0, z0, z0, z0, z1, z1, z1, z1]

    # 12 triangles composing a cuboid.
    i = [0, 0, 0, 1, 4, 5, 0, 1, 2, 0, 3, 7]
    j = [1, 2, 4, 2, 5, 6, 1, 5, 6, 3, 2, 4]
    k = [2, 3, 5, 6, 6, 7, 5, 6, 7, 7, 7, 3]

    return go.Mesh3d(
        x=vertices_x,
        y=vertices_y,
        z=vertices_z,
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=0.92,
        flatshading=True,
        name=name,
        hoverinfo="name",
        showscale=False,
    )


def _build_pallet_animation(
    layout: list[dict],
    pallet_l: int,
    pallet_w: int,
    case_h: int,
    layer_count: int,
    exploded_gap: int,
) -> go.Figure:
    layer_count = max(1, int(layer_count))

    base = _box_mesh(0, 0, 0, float(pallet_l), float(pallet_w), 20.0, "#b08968", "Wooden pallet")
    layer_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    def frame_data(show_layers: int) -> list[go.Mesh3d]:
        traces: list[go.Mesh3d] = [base]
        for layer in range(show_layers):
            z = 20.0 + layer * (case_h + exploded_gap)
            color = layer_colors[layer % len(layer_colors)]
            for idx, item in enumerate(layout, start=1):
                traces.append(
                    _box_mesh(
                        float(item.get("x_mm", 0.0)),
                        float(item.get("y_mm", 0.0)),
                        z,
                        float(item.get("dim_x_mm", 1.0)),
                        float(item.get("dim_y_mm", 1.0)),
                        float(case_h),
                        color,
                        f"Layer {layer + 1} carton {idx}",
                    )
                )
        return traces

    frames = [go.Frame(name=str(step), data=frame_data(step)) for step in range(1, layer_count + 1)]

    fig = go.Figure(data=frame_data(1), frames=frames)
    fig.update_layout(
        title="3D Pallet Stacking Animation (Exploded Layers)",
        scene={
            "xaxis_title": "Length (mm)",
            "yaxis_title": "Width (mm)",
            "zaxis_title": "Height (mm)",
            "aspectmode": "data",
            "camera": {"eye": {"x": 1.5, "y": -1.6, "z": 1.25}},
        },
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "x": 0.0,
                "y": 1.1,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    },
                ],
            }
        ],
        sliders=[
            {
                "active": 0,
                "pad": {"t": 35},
                "steps": [
                    {
                        "label": f"Layer {step}",
                        "method": "animate",
                        "args": [[str(step)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                    }
                    for step in range(1, layer_count + 1)
                ],
            }
        ],
        margin={"l": 0, "r": 0, "t": 65, "b": 0},
    )
    return fig

st.set_page_config(page_title="Pallet Coach - Streamlit", page_icon="📦", layout="wide")
st.title("Pallet Coach")
st.caption("Streamlit local app for palletization solve and stacking guidance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pallet")
    selected_pallet = st.selectbox("Preset", list(PALLET_PRESETS.keys()), index=0)
    preset = PALLET_PRESETS[selected_pallet]

    pallet_length = st.number_input(
        "Pallet length (mm)", min_value=1, value=int(preset["length_mm"]), step=1
    )
    pallet_width = st.number_input(
        "Pallet width (mm)", min_value=1, value=int(preset["width_mm"]), step=1
    )

    st.subheader("Case")
    case_length = st.number_input("Case length (mm)", min_value=1, value=300, step=1)
    case_width = st.number_input("Case width (mm)", min_value=1, value=200, step=1)
    case_height = st.number_input("Case height (mm)", min_value=1, value=150, step=1)
    case_weight = st.number_input("Case weight (kg)", min_value=0.0, value=2.2, step=0.1)

with col2:
    st.subheader("Stack")
    layer_count = st.number_input("Layer count", min_value=1, value=8, step=1)

    st.subheader("Tolerances (mm)")
    max_overhang_l = st.number_input("Max overhang length", min_value=0, value=0, step=1)
    max_overhang_w = st.number_input("Max overhang width", min_value=0, value=0, step=1)
    max_underhang_l = st.number_input("Max underhang length", min_value=0, value=20, step=1)
    max_underhang_w = st.number_input("Max underhang width", min_value=0, value=20, step=1)

    st.subheader("Constraints")
    allow_rotation_90 = st.toggle("Allow 90° rotation", value=True)
    allow_interlock = st.toggle("Allow interlock", value=False)
    auto_underhang = st.toggle("Auto underhang", value=False)
    max_pallet_weight = st.number_input("Max pallet weight (kg)", min_value=0.0, value=1000.0, step=10.0)
    exploded_gap_mm = st.number_input("3D exploded gap (mm)", min_value=0, value=40, step=5)

run_clicked = st.button("Run Solve", type="primary")

if run_clicked:
    payload = {
        "request": {
            "pallet": {
                "type": preset["type"] if selected_pallet != "Custom" else "custom",
                "length_mm": int(pallet_length),
                "width_mm": int(pallet_width),
            },
            "case": {
                "length_mm": int(case_length),
                "width_mm": int(case_width),
                "height_mm": int(case_height),
                "weight_kg": float(case_weight),
            },
            "stack": {"layer_count": int(layer_count)},
            "tolerances": {
                "max_overhang_l_mm": int(max_overhang_l),
                "max_overhang_w_mm": int(max_overhang_w),
                "max_underhang_l_mm": int(max_underhang_l),
                "max_underhang_w_mm": int(max_underhang_w),
            },
            "constraints": {
                "allow_rotation_90": bool(allow_rotation_90),
                "allow_interlock": bool(allow_interlock),
                "auto_underhang": bool(auto_underhang),
                "max_pallet_weight_kg": float(max_pallet_weight) if max_pallet_weight > 0 else None,
            },
        }
    }

    with st.spinner("Solving..."):
        try:
            result = recommend(payload, max_options=25)
        except Exception as exc:
            st.error(f"Solve failed: {exc}")
        else:
            st.success(f"Status: {result.get('status', 'unknown')}")

            reasons = result.get("reasons") or []
            if reasons:
                st.warning("Reasons")
                st.json(reasons)

            solutions = result.get("solutions") or []
            if solutions:
                top = solutions[0]
                metrics = top.get("metrics", {})
                layout = top.get("layout", [])
                st.subheader("Top Solution Metrics")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Cases/layer", metrics.get("cases_per_layer", "-"))
                m2.metric("Total cases", metrics.get("total_cases", "-"))
                m3.metric("Fill %", metrics.get("area_fill_efficiency_pct", "-"))
                m4.metric("Height mm", metrics.get("total_height_mm", "-"))

                if layout:
                    st.subheader("3D Pallet Animation")
                    fig = _build_pallet_animation(
                        layout=layout,
                        pallet_l=int(pallet_length),
                        pallet_w=int(pallet_width),
                        case_h=int(case_height),
                        layer_count=int(layer_count),
                        exploded_gap=int(exploded_gap_mm),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No layout geometry available to animate for this result.")

                st.subheader("Top Solution (JSON)")
                st.json(top)
            else:
                st.info("No feasible solutions returned for current constraints.")

            stacking = result.get("stacking")
            if stacking:
                st.subheader("Stacking Guidance")
                st.json(stacking)
