# Pallet Coach — Requirements Meta-Prompt

> **How to use this file.**  
> Paste the full contents of this document into any capable LLM (GPT-4o, Claude, Gemini, etc.) with the instruction: *"Generate a complete, production-grade `requirements.md` for the Pallet Coach system using the specification below as the single source of truth."*  
> The output document must be comprehensive enough that a new engineering team could rebuild every layer — backend solver, API, artifact pipeline, React UI, styling system, and AI integrations — from scratch without access to the original repository.

---

## 0. Meta-prompt instructions for the LLM

You are a senior software architect and business analyst. Using every piece of information in this document, produce a **single `requirements.md`** that acts as the canonical specification for the Pallet Coach system. The document you produce must include all of the following top-level sections, in order:

1. Executive summary and product purpose  
2. Stakeholder map and user personas  
3. Business rules and domain logic  
4. Functional requirements — backend solver  
5. Functional requirements — API layer  
6. Functional requirements — artifact pipeline  
7. Functional requirements — AI integrations  
8. Functional requirements — React UI  
9. Data contracts (input, output, bundle schema)  
10. Non-functional requirements (performance, security, scalability)  
11. UI/UX design system and styling rules  
12. Testing and evaluation requirements  
13. Deployment and infrastructure  
14. Glossary  

Do **not** paraphrase or omit any rule, field, formula, or constraint listed below. Reproduce every data table, formula, and enumeration exactly. Where a rule says "must", the requirement must be labelled **[MUST]**. Where a rule says "should", label it **[SHOULD]**. Where a rule says "may" or "optional", label it **[MAY]**.

---

## 1. Product overview

**Product name**: Pallet Coach (runtime name in all code, docs, and UI).  
**Alternate name used in architecture documentation**: AI Palette.  
**One-line description**: A math-first, deterministic pallet pattern recommendation tool for single-SKU palletisation optimisation, augmented with optional generative-AI summaries and diagrams.

**Core value proposition**:
- Enumeration of all geometrically feasible single-layer case-placement patterns for a given pallet × case geometry combination.
- Deterministic, reproducible ranking of patterns by cases-per-layer and area fill efficiency.
- Policy-based stacking guidance (height cap 2 000 mm floor-to-top-of-load, pallet height 144 mm, weight ceiling when provided).
- Optional GenAI augmentation: LLM-authored narrative summaries and AI-generated diagram images.
- All outputs persisted to a per-run filesystem bundle for traceability.

**Phase context**: Step 1 MVP. Upright-only single-SKU patterns. No mixed layers, no tipping, no multi-SKU, no multi-layer interlocking (interlock toggle is optional/experimental). Step 2+ extensions are noted but out of scope.

---

## 2. Stakeholder map and user personas

### 2.1 Primary users
| Persona | Role | Goals |
|---|---|---|
| Logistics Engineer | Configures pallet patterns for production | Find the maximum cases-per-layer that fits within site tolerance rules. |
| Operations Manager | Reviews adoption feasibility | Understand how many layers can safely be added given height / weight constraints. |
| Supply Chain Analyst | Validates and documents patterns | Export run bundles for compliance records; compare before/after patterns. |

### 2.2 Secondary users
| Persona | Role |
|---|---|
| AI/CoE Developer | Maintains and extends the tool; writes evaluations. |
| DevOps / Platform Engineer | Deploys container, manages secrets and runtime. |

---

## 3. Business rules and domain logic

### 3.1 Coordinate system
- Origin `(0, 0)` is the **bottom-left** corner of the pallet surface.  
- `x` axis runs along pallet **length**.  
- `y` axis runs along pallet **width**.  
- All dimensions are in **millimetres (mm)** internally. Unit conversion happens at the UI boundary.

### 3.2 Case placement rules
- **Upright-only**: `case.height_mm` is always vertical. No face-down or tilted placement.  
- **In-plane rotation**: When `constraints.allow_rotation_90 = true`, cases may be rotated 90° in-plane (swap `length_mm` ↔ `width_mm`). `rotation_deg` must be either `0` or `90`.  
- **No overlap**: No two case bounding boxes may intersect.  
- **Grid-only patterns** (Step 1): all placements within a solution form a regular grid (uniform `nx × ny`). Mixed/alternating patterns are Phase 2.  
- **Interlock** (optional/experimental): When `constraints.allow_interlock = true`, the solver may generate alternating-row offset patterns. Interlock solutions are labeled `_interlock` in their `solution_id`.

### 3.3 Tolerance rules — per MVP semantics
**Overhang** (case footprint extends beyond pallet edge):
- Enforced **per-side**. Both sides on each axis must satisfy `max_overhang_*`.  
- `left_overhang_mm = max(0, -clearance["left_mm"])`  
- `right_overhang_mm = max(0, -clearance["right_mm"])`  
- Passes if: `left_overhang_mm ≤ max_overhang_l_mm` AND `right_overhang_mm ≤ max_overhang_l_mm`  
- Same logic applies to `bottom`/`top` vs `max_overhang_w_mm`.

**Underhang** (gap between case footprint edge and pallet edge):
- Enforced as an **anchoring** constraint per axis.  
- Length axis passes if: `min(left_underhang_mm, right_underhang_mm) ≤ max_underhang_l_mm`  
- Width axis passes if: `min(bottom_underhang_mm, top_underhang_mm) ≤ max_underhang_w_mm`  

**`auto_underhang` flag**: When `constraints.auto_underhang = true`, the solver automatically selects the minimum feasible underhang value for the winning pattern, overriding the explicit `max_underhang_*` fields.

**Default tolerances** (applied when UI fields are omitted):
```
max_overhang_l_mm  = 0
max_overhang_w_mm  = 0
max_underhang_l_mm = 20
max_underhang_w_mm = 20
```

### 3.4 Stacking policy rules (Phase 2b)
- Default maximum stack height: **2 000 mm** (floor to top of load).  
- Pallet height assumption: **144 mm** (deck height for Euro/Industrial/Custom).  
- Available load height = `max_stack_height_mm − pallet_height_mm`.  
- Height ceiling layers = `floor(available_load_height / case.height_mm)`.  
- Weight ceiling layers (when `case.weight_kg` and `max_pallet_weight_kg` are provided):  
  `floor((max_pallet_weight_kg − pallet_tare_kg) / (cases_per_layer × case.weight_kg))`  
- Pallet tare weights: Euro = 25 kg, Industrial = 30 kg, Custom = 25 kg.  
- Effective ceiling = `min(height_ceiling_layers, weight_ceiling_layers)` (use whichever bound is binding).  
- Recommended adoption range: `[current_layers + 1 .. min(current_layers + 3, effective_ceiling)]`.  
- `current_stack_height_mm = pallet_height_mm + (current_layers × case.height_mm)`.  
- `headroom_mm = max_stack_height_mm − current_stack_height_mm`.

### 3.5 Ranking rules
Solutions are ranked by:
1. `cases_per_layer` descending (primary).  
2. `area_fill_efficiency_pct` descending (tiebreaker).  
3. Only solutions where `tolerance_pass = true` are included in the ranked output.

### 3.6 Metrics — mandatory computed fields per solution
| Field | Formula |
|---|---|
| `cases_per_layer` | Count of placements in the layer. |
| `total_cases` | `cases_per_layer × stack.layer_count` |
| `total_height_mm` | `pallet_height_mm + stack.layer_count × case.height_mm` |
| `total_weight_kg` | `cases_per_layer × stack.layer_count × case.weight_kg` (when `weight_kg` present) |
| `area_fill_efficiency_pct` | `100 × (cases_per_layer × case.length_mm × case.width_mm) / (pallet.length_mm × pallet.width_mm)` |
| `footprint_bbox_mm` | `{ min_x_mm, min_y_mm, max_x_mm, max_y_mm }` |
| `edge_clearance_mm` | `{ left_mm, right_mm, bottom_mm, top_mm }`. Positive = underhang; negative = overhang. |
| `tolerance_pass` | Boolean derived from section 3.3. |
| `inner_axis_segments_mm` | Unique case-edge positions projected onto x and y axes (for dimension-line diagrams). |
| `interlock` | Boolean — true if solution is an interlock variant. |

---

## 4. Functional requirements — backend solver

### 4.1 Solver engine (`scripts/pallet_coach/solver.py`)
- **[MUST]** Enumerate all distinct `(nx, ny, rotation)` grid combinations where the footprint fits within tolerance.  
- **[MUST]** Evaluate both `rotation_deg = 0` and `rotation_deg = 90` when `allow_rotation_90 = true`.  
- **[MUST]** Return `status = "impossible"` with reason code when no feasible solution exists.  
- **[MUST]** Return `status = "ok"` with ranked solutions (max 25 by default, max 250 by API parameter).  
- **[MUST]** Compute all metrics defined in section 3.6 for every solution.  
- **[MUST]** Expose `inner_axis_segments_mm` for diagram dimension lines.  
- **[SHOULD]** Generate interlock variants when `allow_interlock = true` (alternating row offset = `case.width_mm / 2`).

### 4.2 Contract parsing (`scripts/pallet_coach/contracts.py`)
- **[MUST]** Validate all required fields; raise `ContractError` for missing or invalid inputs.  
- **[MUST]** Apply default tolerance values when omitted (section 3.3).  
- **[MUST]** Enforce: `pallet.length_mm ≥ 1`, `pallet.width_mm ≥ 1`, `case.length_mm ≥ 1`, `case.width_mm ≥ 1`, `case.height_mm ≥ 1`, `stack.layer_count ≥ 1`.  
- **[MUST]** Support all fields in sections 1.3–1.7 of the Solver Contract.

### 4.3 Stacking analysis (`scripts/pallet_coach/stacking.py`)
- **[MUST]** Compute all fields in the `StackingAnalysis` dataclass (see section 3.4).  
- **[MUST]** Emit warnings when: stack height exceeds 2 000 mm; weight ceiling is more restrictive than height ceiling.  
- **[MUST]** Return `None` (not error) for optional ceilings when data is absent (e.g., no `weight_kg`).

### 4.4 Recommender (`scripts/pallet_coach/recommender.py`)
- **[MUST]** Expose a `recommend(req, max_options=25)` function as the primary entry point.  
- **[MUST]** Delegate to `solver.solve()` internally.

---

## 5. Functional requirements — API layer

### 5.1 FastAPI application (`scripts/pallet_coach/api/app.py`)

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}`. |
| `POST` | `/api/solve` | Validates request, runs solver, writes bundle, returns `SolveResponse`. |
| `GET` | `/api/runs/{run_id}` | Returns parsed `bundle.json` for the run. |
| `GET` | `/api/runs/{run_id}/logs` | Returns last N lines of the run log (plain text). |
| `POST` | `/api/summary` | Generates AI summary using Azure OpenAI; writes to run directory. |
| `POST` | `/api/summary_ui` | Generates UI-friendly AI summary (reformatted markdown); writes to run directory. |
| `POST` | `/api/diagram` | Generates AI diagram image using Google AI Studio; writes to run directory. |
| `GET` | `/output/{run_id}/{filename}` | Static file serving of per-run artifacts (PNG, markdown, JSON). |

**Behaviour rules:**
- **[MUST]** Mount `/output` as a static files route pointing to `04_Output/` in the repo root.  
- **[MUST]** Resolve `run_id` to a run directory safely — path-traversal attacks must be mitigated.  
- **[MUST]** Return HTTP 422 with `ContractError` details for invalid solver requests.  
- **[MUST]** Return HTTP 404 when a `run_id` does not correspond to an existing run directory.  
- **[MUST]** Prefix all API routes with `/api` (Vite proxy routes `/api` and `/output` to the backend in dev).  
- **[SHOULD]** Archive any loose files in the `04_Output/` root (non-directory) at server startup.  
- **[MAY]** Accept `max_solutions` (int, 1–250, default 25) and `include_timestamp` (bool, default true) on `/api/solve`.

**Pydantic models (`scripts/pallet_coach/api/models.py`):**
```
SolveRequest      { request: Dict, max_solutions: int = 25, include_timestamp: bool = True }
SolveResponse     { run_id, out_dir, solver_status, best_metrics?, artifacts }
SummaryRequest    { run_id, style: "short"|"detailed" = "detailed" }
SummaryResponse   { run_id, out_dir, summary_path, summary_markdown }
SummaryUiRequest  { run_id, style: "short"|"detailed" = "detailed", force: bool = False }
SummaryUiResponse { run_id, out_dir, summary_ui_path, summary_markdown }
DiagramRequest    { run_id, view: "flat"|"3d" }
DiagramResponse   { run_id, out_dir, diagram_path }
```

---

## 6. Functional requirements — artifact pipeline

### 6.1 Run directory structure
- **[MUST]** Every `/api/solve` call allocates a unique run directory under `04_Output/<run_id>/`.  
- **[MUST]** `run_id` format: `R{n:04d}_{YYYYMMDD}` where `n` is a monotonically incrementing integer scoped to the current day.  
- **[MUST]** The following files must be written for every successful solve:

| Artifact key | Filename pattern | Content |
|---|---|---|
| `bundle` | `bundle.json` | Master run record (full schema, section 9.3). |
| `run_log` | `run_log.txt` | Append-only plain-text log with timestamped events. |
| `recommendation_summary` | `recommendation_summary.md` | Deterministic markdown summary. |
| `layer_diagram` | `layer_diagram.png` | Top-down layer PNG from the best solution. |
| `comparison_flat` | `comparison_flat.png` | Side-by-side before/after flat PNG. |
| `comparison_3d` | `comparison_3d.png` | Before/after 3D stack PNG. |
| `onpallet_3d` | `onpallet_3d.png` | Isometric 3D pallet view PNG. |
| `image_prompt_flat` | `image_prompt_flat.md` | Rendered prompt for flat AI diagram. |
| `image_prompt_3d` | `image_prompt_3d.md` | Rendered prompt for 3D AI diagram. |

- **[MAY]** Write optional AI artifacts:

| Artifact key | Filename | Trigger |
|---|---|---|
| `summary_ui` | `summary_ui.md` | `/api/summary_ui` call |
| `diagram_flat` | `diagram_flat.png` | `/api/diagram` with `view=flat` |
| `diagram_3d` | `diagram_3d.png` | `/api/diagram` with `view=3d` |
| `ai_traces/ai_calls.jsonl` | JSONL | Every AI call (best-effort secret redaction) |

### 6.2 Diagram rendering (`scripts/pallet_coach/diagram.py`)

**Four rendering functions — each must produce a PNG:**

| Function | Description |
|---|---|
| `render_layer_png(...)` | Top-down single-layer view with numbered case labels, dimension lines, edge-clearance colouring. |
| `render_comparison_flat_png(...)` | Two-panel horizontal PNG: BEFORE (baseline inferred grid) vs AFTER (best solution). |
| `render_comparison_3d_png(...)` | Two-panel 3D stack comparison. |
| `render_onpallet_3d_png(...)` | Single isometric 3D view of the stacked pallet. |

**Diagram colour palette (exact hex values):**
```
pallet_fill:    #E8E8E8   (light grey pallet surface)
pallet_border:  #333333   (dark border)
case_fill:      #FFFFFF   (white case faces)
case_border:    #1A1A1A   (near-black case border)
case_top:       #1E88E5   (blue case top)
interlock_a:    #F9D65C   (yellow — interlock layer A)
interlock_b:    #E53935   (red — interlock layer B)
tolerance_ok:   #4CAF50   (green — within tolerance)
tolerance_warn: #FFC107   (amber — near limit)
tolerance_fail: #F44336   (red — exceeds)
underhang_zone: #90CAF9   (light blue underhang envelope)
overhang_zone:  #FFCC80   (light orange overhang envelope)
text_primary:   #1A1A1A
text_secondary: #666666
background:     #FFFFFF
grid_line:      #CCCCCC
dimension_line: #333333
```

**Rendering rules:**
- **[MUST]** Draw pallet rectangle as reference boundary.  
- **[MUST]** Draw each case as a rectangle; label with sequential index and `rotation_deg`.  
- **[MUST]** Render dimension lines using `inner_axis_segments_mm` values.  
- **[MUST]** Colour edge-clearance zones per tolerance status (ok / warn / fail).  
- **[MUST]** Use `matplotlib` with `Agg` backend (no display/GUI dependency).  
- **[MUST]** Output PNG at a resolution sufficient for A4 print (≥ 150 dpi).

### 6.3 Baseline inferred grid (BEFORE panel)
- **[MUST]** When a `baseline_cases_per_layer` value is present in the request, infer a plausible `(nx, ny)` grid that equals that case count using the reported case aspect ratio.  
- **[MUST]** Score candidate `(nx, ny)` factor pairs by implied footprint area and grid balance; select the highest-scoring valid pair.  
- **[MUST]** This inferred grid is used **only for the BEFORE diagram panel** — it is not a solver output.

---

## 7. Functional requirements — AI integrations

### 7.1 Azure OpenAI (`scripts/pallet_coach/ai/azure_responses.py`)
- **[MUST]** Use the Azure OpenAI Responses API endpoint (full URL including `api-version`).  
- **[MUST]** Read config from environment variables: `AZURE_OAI_RESPONSES_ENDPOINT`, `AZURE_OAI_API_KEY`, `AZURE_OAI_MODEL`, `AZURE_OAI_TIMEOUT_S` (default 60 s).  
- **[MUST]** Pass a minimised bundle view to the LLM (top 5 solutions; request, recommender status, stacking block only — no raw placements array).  
- **[MUST]** Use the system prompt from `scripts/pallet_coach/prompts/azure_summary_system.md`.  
- **[MUST]** Use the UI-rewrite system prompt from `scripts/pallet_coach/prompts/azure_summary_ui_system.md` for `/api/summary_ui`.  
- **[MUST]** Write the AI trace (request + response metadata) to `ai_calls.jsonl` with best-effort secret redaction before writing.

**UI summary system prompt rules (must be reproduced in the rebuilt prompt):**
- You are "Pallet Coach", a logistics pallet-optimisation assistant.  
- Rewrite a deterministic summary into a UI-friendly Markdown summary.  
- Use **only** numbers that appear in the provided input — do not invent numbers.  
- Preserve meaning; simplify wording for non-technical stakeholders.  
- Keep it scannable: short paragraphs, bullets, small tables.  
- Always include (when present): pallet size, case size, current layers, stacking height info (2.0 m cap), best option cases/layer, top warnings.  
- If solver status is `impossible`, explain why and what to change.  
- Use traffic-light emojis: ✅ for within-limit, 🟡 for near-limit, 📏 for height.  
- Style: Palantir-style professional tone. Markdown only. No preamble or meta-commentary.

### 7.2 Google AI Studio (`scripts/pallet_coach/ai/google_ai_studio.py`)
- **[MUST]** Read config from: `GOOGLE_AI_API_KEY`, `GOOGLE_AI_IMAGE_MODEL` (default `gemini-3-pro-image-preview`), `GOOGLE_AI_TIMEOUT_S` (default 120 s).  
- **[MUST]** Use the rendered prompt from `image_prompt_flat.md` or `image_prompt_3d.md` (chosen by `view` parameter).  
- **[MUST]** Write returned image bytes to `diagram_flat.png` or `diagram_3d.png` in the run directory.  
- **[MUST]** Update `bundle.json` artifact pointers after writing AI artifacts.

### 7.3 Prompt templates (`scripts/pallet_coach/prompt_templates.py`)
- **[MUST]** Load prompt templates from `scripts/pallet_coach/prompts/*.md`.  
- **[MUST]** Render templates using a variable substitution mechanism (Jinja-style or simple `{{var}}` replacement).  
- Template files: `azure_summary_system.md`, `azure_summary_ui_system.md`, `image_prompt_flat_template.md`, `image_prompt_3d_template.md`.

### 7.4 Tracing
- **[MUST]** Write every AI call to `ai_traces/ai_calls.jsonl` (append, JSONL format).  
- **[MUST]** Redact values matching environment variable names (`AZURE_OAI_API_KEY`, `GOOGLE_AI_API_KEY`) before writing traces.  
- **[SHOULD]** Include: timestamp, endpoint/model, prompt token count, completion token count, latency_ms, run_id.

---

## 8. Functional requirements — React UI

### 8.1 Technology stack
- React 18+ with TypeScript (strict mode).  
- Vite 7+ as build tool and dev server.  
- Tailwind CSS 3+ for utility styling.  
- `react-router-dom` for client-side routing.  
- `react-markdown` + `remark-gfm` for rendering AI summary markdown.  
- `jszip` + `file-saver` for bundle download/export.  
- `@tailwindcss/typography` plugin for prose rendering.

### 8.2 Routes
| Path | Component | Description |
|---|---|---|
| `/` | `Home` | Input form page. |
| `/runs/:runId` | `Run` | Results and artifact view page. |

### 8.3 Home page — input form

**Form sections (in order):**

1. **Unit toggles** (top of form, 2-column grid):
   - Dimension unit: `mm` | `inch` (default: `mm`)
   - Weight unit: `kg` | `lbs` (default: `kg`)

2. **SKU metadata** (2-column grid, optional):
   - SKU code: free text, e.g. "10263"
   - SKU description: free text, e.g. "CB NY DAWN_CAN_36X0.32..."

3. **Case dimensions** (section header "Case", 3-column grid, all required):
   - Length — positive number in selected dim unit
   - Width — positive number in selected dim unit
   - Height — positive number in selected dim unit

4. **Case weight** (optional):
   - Weight — positive number in selected weight unit

5. **Pallet preset** (dropdown):
   - `Industrial 1200×1000` → `{ pallet_type: "industrial", length_mm: 1200, width_mm: 1000 }`
   - `Euro 1200×800` → `{ pallet_type: "euro", length_mm: 1200, width_mm: 800 }`
   - *(Contract specifies additional presets for Phase 2: GMA 40×48, half-pallet 800×600, Australian 1160×1160, custom. Implement as future extension.)*

6. **Stacking** (section header "Stack"):
   - Layers: positive integer (default `8`)

7. **Advanced constraints** (section header "Constraints"):
   - Interlock toggle (boolean, default `false`) — labelled "Allow interlock"
   - Max pallet weight: optional positive number in selected weight unit

**Normalisation before POST (implemented in UI):**
- `inch → mm`: `mm = round(inch × 25.4)`
- `lbs → kg`: `kg = round(lbs × 0.453592, 3)`
- `auto_underhang` is always sent as `true`.
- Tolerances are always sent as `{ max_overhang_l_mm: 0, max_overhang_w_mm: 0, max_underhang_l_mm: 0, max_underhang_w_mm: 0 }` (auto_underhang overrides).

**Validation (real-time, before submit):**
- Length, Width, Height: `parsePositiveInt` — must be a positive integer.
- Layers: positive integer.
- Weight fields (case weight, max pallet weight): `parseFiniteNumber` — must be a positive finite number if provided.
- Submit button disabled if any required field fails validation or form is submitting.

**Submit behaviour:**
1. POST to `/api/solve`.
2. Immediately POST to `/api/summary_ui` (fire-and-forget; failure logged as a non-blocking warning).
3. Navigate to `/runs/:runId` passing any summary-generation warning in router state.

### 8.4 Run page — results view

**Data loading:**
- Load `bundle.json` via `GET /api/runs/:runId`.
- Check artifact URLs via HEAD requests to determine which images exist.

**Page sections (in order):**

1. **Header row**: Back link ("← Home"), run ID badge, weight unit toggle (`kg` / `lbs`).

2. **AI summary panel** (when `summary_ui.md` exists):
   - Render markdown using `react-markdown` + `remark-gfm`.
   - "Regenerate" button → calls `/api/summary_ui` with `force: true`, reloads.
   - Loading spinner while generating.

3. **Diagram carousel** (tab-style switcher):
   - Tab 1: "Flat comparison" — shows `comparison_flat.png`.
   - Tab 2: "3D view" — shows `comparison_3d.png`.
   - Each tab has a "Generate AI diagram" button → calls `/api/diagram` with the appropriate `view` param, reloads image after.
   - Images served from `/output/:runId/:filename`.

4. **Options table** (top 5 solutions from `bundle.json`):

   | Column | Source field |
   |---|---|
   | Rank | Position (1-indexed). |
   | Pattern | `solution_id` stripped of `grid_` prefix and `_rot{n}` suffix formatted as "{n} deg"; `_interlock` suffix stripped. |
   | Interlock | "Interlock" if `metrics.interlock = true`, else "Normal". |
   | Cases/Layer | `metrics.cases_per_layer` |
   | Total Layers | `total_cases / cases_per_layer` (rounded). |
   | Total Cases | `metrics.total_cases` |
   | Total Weight | `metrics.total_weight_kg` converted to selected weight unit, to 1 decimal place. |
   | Eff % | `metrics.area_fill_efficiency_pct` to 1 decimal. |
   | Total Height | `metrics.total_height_mm` in mm. |

5. **Stacking analysis table** ("Height & Layering (2.0 m cap)" or "Height, Weight & Layering" when weight ceiling is present):

   | Row label | Field |
   |---|---|
   | Max stack height | `stacking.max_stack_height_mm` mm |
   | Pallet height | `stacking.pallet_height_mm` mm |
   | Current stack height | `stacking.current_stack_height_mm` mm |
   | Headroom | `stacking.headroom_mm` mm |
   | Current Layers | `stacking.current_layers` |
   | Max layers at cap | `stacking.max_layers_at_max_height` |
   | Addable layers | `stacking.addable_layers_to_max_height` |
   | Weight ceiling (layers) | `stacking.weight_ceiling_layers_conservative` |
   | Recommended range | `{min}..{max} layers` from `stacking.recommended_layers_range` |
   | Height at recommended max | Derived: `pallet_height_mm + recommended_max × case_height_mm` |

6. **Input summary card**: Display the original request fields (pallet preset, case dims, layers, tolerances).

7. **Export / download**: "Download bundle" button — zips the run directory artifacts and triggers browser download using `jszip` + `file-saver`.

8. **Logs panel** (collapsible): Fetches `/api/runs/:runId/logs` and displays plain-text run log.

### 8.5 AppShell (layout wrapper)
- Sticky header, `z-index: 50`, `backdrop-blur-md`, border-bottom.  
- Left side: pulsing cyan status indicator (`.animate-pulse-slow` + `.animate-ping`), "Pallet Coach" logotype link to `/`, circular `?` help button.  
- Right side: green dot + "Step 1 MVP" badge.  
- Help button opens `HelpPanel` as a slide-in right-side drawer.

### 8.6 HelpPanel
- Full-height right drawer, `z-index: 70`, backdrop `z-index: 60`.  
- Closed by clicking backdrop, pressing Escape, or clicking the × button.  
- Focus trap: panel receives focus on open.  
- Sections: Welcome, How to Use, Reading Results, Tips.

---

## 9. Data contracts

### 9.1 Solver request (canonical — sent by UI to `/api/solve`)
```json
{
  "request": {
    "request_id": "<optional string>",
    "meta": {
      "dim_unit": "mm|inch",
      "weight_unit": "kg|lbs",
      "sku_code": "<optional>",
      "sku_description": "<optional>"
    },
    "pallet": {
      "type": "euro|industrial|custom",
      "length_mm": 1200,
      "width_mm": 800
    },
    "case": {
      "length_mm": 300,
      "width_mm": 200,
      "height_mm": 150,
      "weight_kg": 2.2
    },
    "stack": {
      "layer_count": 8
    },
    "tolerances": {
      "max_overhang_l_mm": 0,
      "max_overhang_w_mm": 0,
      "max_underhang_l_mm": 0,
      "max_underhang_w_mm": 0
    },
    "constraints": {
      "allow_rotation_90": true,
      "allow_interlock": false,
      "auto_underhang": true,
      "max_pallet_weight_kg": 1000
    }
  },
  "max_solutions": 25,
  "include_timestamp": true
}
```

### 9.2 Solve API response
```json
{
  "run_id": "R0001_20260417",
  "out_dir": "/absolute/path/to/04_Output/R0001_20260417",
  "solver_status": "ok",
  "best_metrics": {
    "cases_per_layer": 12,
    "total_cases": 96,
    "area_fill_efficiency_pct": 75.0,
    "total_height_mm": 1344
  },
  "artifacts": {
    "bundle": { "path": "bundle.json" },
    "layer_diagram": { "path": "layer_diagram.png" },
    "comparison_flat": { "path": "comparison_flat.png" },
    "comparison_3d": { "path": "comparison_3d.png" },
    "onpallet_3d": { "path": "onpallet_3d.png" }
  }
}
```

### 9.3 `bundle.json` schema (master run record)
```json
{
  "run_id": "R0001_20260417",
  "created_at": "<ISO-8601 UTC>",
  "request": { "<canonical solver request>" },
  "recommender": {
    "status": "ok|impossible|error",
    "reasons": [],
    "solutions": [
      {
        "solution_id": "grid_4x3_rot0",
        "layout": [
          { "x_mm": 0, "y_mm": 0, "rotation_deg": 0, "dim_x_mm": 300, "dim_y_mm": 200 }
        ],
        "metrics": {
          "cases_per_layer": 12,
          "total_cases": 96,
          "total_height_mm": 1344,
          "total_weight_kg": 211.2,
          "area_fill_efficiency_pct": 75.0,
          "footprint_bbox_mm": { "min_x_mm": 0, "min_y_mm": 0, "max_x_mm": 1200, "max_y_mm": 600 },
          "edge_clearance_mm": { "left_mm": 0, "right_mm": 0, "bottom_mm": 100, "top_mm": 100 },
          "tolerance_pass": true,
          "inner_axis_segments_mm": { "x_segments_mm": [300, 300, 300, 300], "y_segments_mm": [200, 200, 200] },
          "interlock": false
        }
      }
    ]
  },
  "stacking": {
    "current_layers": 8,
    "max_stack_height_mm": 2000,
    "pallet_height_mm": 144,
    "current_stack_height_mm": 1344,
    "headroom_mm": 656,
    "height_ceiling_layers": 12,
    "weight_ceiling_layers": null,
    "effective_ceiling_layers": 12,
    "recommended_layers_range": { "min": 9, "max": 11 },
    "max_layers_at_max_height": 12,
    "addable_layers_to_max_height": 4,
    "warnings": [],
    "assumptions": { "pallet_height_mm": 144, "max_stack_height_mm": 2000 }
  },
  "artifacts": {
    "bundle": { "path": "bundle.json" },
    "run_log": { "path": "run_log.txt" },
    "recommendation_summary": { "path": "recommendation_summary.md" },
    "layer_diagram": { "path": "layer_diagram.png" },
    "comparison_flat": { "path": "comparison_flat.png" },
    "comparison_3d": { "path": "comparison_3d.png" },
    "onpallet_3d": { "path": "onpallet_3d.png" },
    "image_prompt_flat": { "path": "image_prompt_flat.md" },
    "image_prompt_3d": { "path": "image_prompt_3d.md" },
    "summary_ui": { "path": "summary_ui.md" }
  },
  "ai_assist": {
    "summary_generated": true,
    "summary_ui_generated": true,
    "diagram_flat_generated": false,
    "diagram_3d_generated": false
  },
  "provenance": {
    "solver_version": "0.1.0",
    "generated_at": "<ISO-8601 UTC>"
  }
}
```

### 9.4 Impossible solver response
```json
{
  "status": "impossible",
  "reasons": [
    { "code": "NO_FEASIBLE_PATTERN", "message": "No placements satisfy the tolerance constraints." }
  ]
}
```

**Reason codes**: `NO_FEASIBLE_PATTERN`, `CASE_LARGER_THAN_PALLET_WITH_TOLERANCE`, `LAYER_COUNT_INVALID`.

### 9.5 Pallet preset mapping
| UI value | `pallet.type` | `length_mm` | `width_mm` |
|---|---|---:|---:|
| `europallet_1200x800` | `euro` | 1200 | 800 |
| `industrial_1200x1000` | `industrial` | 1200 | 1000 |
| `gma_40x48` *(Phase 2)* | `custom` | 1219 | 1016 |
| `halfpallet_800x600` *(Phase 2)* | `custom` | 800 | 600 |
| `australian_1160x1160` *(Phase 2)* | `custom` | 1160 | 1160 |
| `custom` | `custom` | from UI | from UI |

Note: For `gma_40x48`, 48 in maps to length axis (1219 mm) and 40 in maps to width axis (1016 mm).

---

## 10. Non-functional requirements

### 10.1 Performance
- **[MUST]** `/api/solve` must return a response (including diagram generation) within **10 seconds** for typical inputs (single-SKU, ≤ 25 solutions, standard pallet presets).  
- **[SHOULD]** Diagram PNG generation should complete within **3 seconds** per diagram.  
- **[MAY]** AI summary and diagram endpoints may take up to 60 s (Azure) and 120 s (Google) respectively per configured timeout.

### 10.2 Security
- **[MUST]** API keys must be loaded from environment variables or `env.ai` file — never hardcoded.  
- **[MUST]** `env.ai` must be listed in `.gitignore`.  
- **[MUST]** `run_id` path traversal must be mitigated: resolve the run directory and verify it is a child of `04_Output/`.  
- **[MUST]** AI trace files must redact secrets before writing (scan for env var values matching `AZURE_OAI_API_KEY`, `GOOGLE_AI_API_KEY`).  
- **[SHOULD]** Add authentication/authorisation before external or multi-user exposure.  
- **[SHOULD]** Add rate limiting on `/api/solve` and AI endpoints.

### 10.3 Scalability / reliability
- **[SHOULD]** File-based run storage should be migrated to a database + object storage tier for multi-user or high-concurrency deployments.  
- **[SHOULD]** AI calls should be moved to async background jobs/queue for better UX and reliability.  
- **[SHOULD]** Implement structured logging, metrics, trace IDs, and a split health/readiness endpoint.

### 10.4 Compatibility
- **[MUST]** Python backend: Python 3.10+. Pydantic 2.11+ (for Python 3.14 compatibility).  
- **[MUST]** Frontend: Node.js 18+. Browser targets: last 2 versions of Chrome, Firefox, Edge, Safari.  
- **[MUST]** Fonts served from Google Fonts CDN (IBM Plex Sans, JetBrains Mono) — must gracefully degrade if unavailable.

---

## 11. UI/UX design system and styling rules

### 11.1 Visual theme: "Precision Industrial Dark"
The UI is a single-page application with a consistent dark theme. Every colour, font, spacing, and animation value below is canonical — rebuilders must not substitute alternatives.

### 11.2 Colour palette (CSS custom properties on `:root`)
```css
--bg:      10  12  14    /* near-black background */
--panel:   14  16  18    /* card / panel surface */
--panel2:  18  20  24    /* secondary panel, table background */
--line:    38  42  48    /* border / divider */
--text:   235 239 244    /* primary text */
--muted:  155 165 178    /* secondary / label text */
--accent:  80 220 255    /* primary accent — bright cyan */
--danger: 255 108 108    /* error / danger red */
--shadow:   0   0   0    /* shadow base */
```

All colours are used via `rgb(var(--token))` or `rgba(var(--token), opacity)`.

### 11.3 Typography
- **Body font**: IBM Plex Sans (weights 400, 500, 600). Fallback: `ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial`.  
- **Heading / monospace font**: JetBrains Mono (weights 400, 500). Applied to `h1`, `h2`, `h3` globally. Fallback: `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`.  
- **Body**: `letter-spacing: normal`, `text-rendering: optimizeLegibility`, `-webkit-font-smoothing: antialiased`.  
- **Headings**: `letter-spacing: -0.02em`, `font-weight: 500`.  
- **Labels / section headers**: `text-xs uppercase tracking-[0.18em] text-[rgb(var(--muted))]`.  
- **Accent text / mono values**: `font-mono text-xs text-[rgb(var(--accent))]`.

### 11.4 Scan-line texture
A global CSS pseudo-element overlays the entire viewport with a subtle scan-line texture:
```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0px, transparent 2px,
    rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px
  );
  pointer-events: none;
  z-index: 9999;
}
```

### 11.5 Component specifications

**Card**
```
border: 1px solid rgb(var(--line))
background: rgb(var(--panel))
border-radius: 2px (rounded-sm)
box-shadow: 0 4px 24px -4px rgba(0,0,0,0.5)
transition: box-shadow 300ms
```
- `glow` variant adds class `glow-accent` (cyan box-shadow glow on hover).  
- Top highlight: 1px gradient line `from-transparent via-[rgba(var(--accent),0.3)] to-transparent`.

**Button — primary**
```
border: rgba(var(--accent),0.4)
background: rgba(var(--accent),0.15)
text: rgb(var(--text))
hover background: rgba(var(--accent),0.22)
hover shadow: 0 0 16px -2px rgba(var(--accent),0.4)
active scale: 0.98
padding: px-4 py-2
font: text-sm uppercase tracking-[0.12em]
border-radius: rounded-sm
```
- Inner top-highlight gradient on primary buttons.  
- Loading state: animated SVG spinner (24×24 `animate-spin`).

**Button — secondary**: `border: rgb(var(--line))`, `bg: rgba(var(--panel2),0.35)`.  
**Button — ghost**: `border: transparent`, `bg: transparent`, text colour `--muted` → `--text` on hover.

**TextInput**
```
background: rgb(var(--panel2))
border: 1px solid rgb(var(--line))
border-radius: rounded-sm
padding: px-3 py-2
font: text-sm
color: rgb(var(--text))
placeholder: text-[rgb(var(--muted))]
focus: outline-none ring-1 ring-[rgba(var(--accent),0.4)] border-[rgba(var(--accent),0.4)]
```

**SelectInput**: Same visual rules as TextInput; native `<select>` styled with `appearance-none` and a custom chevron icon.

**Field (label wrapper)**
```
label: text-xs uppercase tracking-[0.15em] text-[rgb(var(--muted))] mb-1.5 block
error: text-xs text-[rgb(var(--danger))] mt-1
required marker: text-[rgb(var(--danger))] ml-0.5
```

**Toggle (boolean)**
- Pill-shaped track: 36×20 px.  
- On: `bg-[rgba(var(--accent),0.3)] border-[rgba(var(--accent),0.5)]`.  
- Off: `bg-[rgb(var(--panel2))] border-[rgb(var(--line))]`.  
- Thumb: 14×14 px circle, slides 16px when on.

**Table styling (OptionsTable, StackingTable)**
```
border: 1px solid rgb(var(--line))
background: rgb(var(--panel2))
thead: bg-[rgba(var(--panel),0.5)] text-xs uppercase tracking-wider text-[rgb(var(--muted))] border-b
tbody rows: divide-y divide-[rgb(var(--line))]
cells: px-4 py-3 text-sm
numeric cells: text-right font-mono text-xs text-[rgb(var(--accent))]
```

### 11.6 Animations
```css
/* Staggered fade-in for page entry */
.animate-in {
  animation: fadeInUp var(--duration-slow) var(--ease-out-expo) both;
}
.animate-delay-1 { animation-delay: 50ms; }
.animate-delay-2 { animation-delay: 100ms; }
.animate-delay-3 { animation-delay: 150ms; }
.animate-delay-4 { animation-delay: 200ms; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Pulsing status dot */
.animate-pulse-slow { animation: pulse 3s ease-in-out infinite; }

/* Help panel slide-in */
.help-panel-enter { animation: slideInRight var(--duration-normal) var(--ease-out-expo); }
@keyframes slideInRight {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}

/* Backdrop fade */
.backdrop-enter { animation: fadeIn var(--duration-fast) ease-out; }
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
```

### 11.7 Layout constants
- Max content width: `max-w-3xl` (Home), `max-w-6xl` (Run page, AppShell header).  
- Page padding: `px-6 py-10`.  
- Form section gap: `space-y-6`.  
- Grid gap: `gap-4`.  
- Section border-separator: `border-t border-[rgb(var(--line))] pt-6`.

### 11.8 Status badge (Home page hero)
```
border: rgba(var(--accent),0.3)
background: rgba(var(--accent),0.08)
border-radius: rounded-full
padding: px-3 py-1
dot: 1.5×1.5px rounded-full bg-[rgb(var(--accent))]
text: text-xs uppercase tracking-[0.18em] text-[rgb(var(--accent))]
label: "Online"
```

### 11.9 Gradient text (hero headline)
```css
.gradient-text {
  background: linear-gradient(135deg, rgb(var(--text)) 0%, rgb(var(--accent)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

---

## 12. Testing and evaluation requirements

### 12.1 Unit tests (`scripts/tests/`)
- **[MUST]** `test_solver_centered_strict_tolerances.py`: Verify the solver returns feasible layouts under zero-overhang, small-underhang constraints for known pallet × case combinations.  
- **[MUST]** `test_stacking_model.py`: Verify `StackingAnalysis` computed fields against hand-calculated expected values.  
- **[MUST]** `test_layer_count_exceedance_highlight.py`: Verify the solver emits a warning / appropriate status when `layer_count` would exceed the height ceiling.  
- **[MUST]** All tests run via `pytest` against the venv Python.

### 12.2 Evaluation harness (`eval/`)
- **[MUST]** `run_eval.py`: Iterates over test cases in `test_cases.json`, calls the solver (or API), and compares outputs against expected values.  
- **[MUST]** `test_cases.json`: JSON array of `{ input, expected }` objects covering at minimum: perfect-fit case, underhang tolerance case, impossible case, rotation-required case.  
- **[SHOULD]** Report pass/fail per case with diff of actual vs expected metrics.

### 12.3 Sample bundles (`samples/`)
- `samples/R1_perfect_fit/bundle.json` — reference output for a zero-clearance perfect-fit solve.  
- `samples/R13_underhang_tolerance/bundle.json` — reference output for a solve where underhang tolerance is the binding constraint.  
- **[MUST]** Rebuilt solver output for these inputs must match the reference bundles (within integer rounding on mm fields).

---

## 13. Deployment and infrastructure

### 13.1 Local development
```powershell
# One-time setup
.\init_project.ps1   # Creates .venv, pip install -r scripts/requirements.txt, npm install UI

# Runtime (two terminals)
.\start_api.ps1      # Uvicorn on http://127.0.0.1:8000
.\start_ui.ps1       # Vite dev server on http://localhost:5173
```

Vite proxy config (`vite.config.ts`) must forward:
- `/api` → `http://127.0.0.1:8000`
- `/output` → `http://127.0.0.1:8000`

### 13.2 Python dependencies (`scripts/requirements.txt`)
```
python-pptx==1.0.2
pypdf==6.9.2
extract-msg==0.52.0
pytest==8.3.4
matplotlib>=3.8
fastapi==0.135.2
uvicorn==0.32.1
pydantic>=2.11
python-dotenv==1.0.1
httpx==0.28.1
```

### 13.3 Container deployment (single-container)
```dockerfile
# Stage 1: Build React UI
FROM node:18-alpine AS ui-build
WORKDIR /app/UI/pallet_coach_ui
COPY UI/pallet_coach_ui/package*.json ./
RUN npm install
COPY UI/pallet_coach_ui/ ./
RUN npm run build

# Stage 2: Python backend + Nginx
FROM python:3.11-slim
RUN apt-get install -y nginx
COPY scripts/ /app/scripts/
COPY --from=ui-build /app/UI/pallet_coach_ui/dist /app/static/
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/entrypoint.sh /entrypoint.sh
WORKDIR /app
RUN pip install -r scripts/requirements.txt
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
```

Nginx configuration:
- Serve React SPA from `/app/static/`.  
- Proxy `/api` and `/output` to `http://127.0.0.1:8000`.  
- Serve `index.html` for all non-asset routes (SPA fallback).

### 13.4 Environment variables
| Variable | Required for | Default |
|---|---|---|
| `AZURE_OAI_RESPONSES_ENDPOINT` | AI summaries | — |
| `AZURE_OAI_API_KEY` | AI summaries | — |
| `AZURE_OAI_MODEL` | AI summaries | `gpt-5.2-chat` |
| `AZURE_OAI_TIMEOUT_S` | AI summaries | `60` |
| `GOOGLE_AI_API_KEY` | AI diagrams | — |
| `GOOGLE_AI_IMAGE_MODEL` | AI diagrams | `gemini-3-pro-image-preview` |
| `GOOGLE_AI_TIMEOUT_S` | AI diagrams | `120` |
| `AI_TRACE_DIRNAME` | Tracing | `ai_traces` |

---

## 14. Glossary

| Term | Definition |
|---|---|
| **SKU** | Stock Keeping Unit — a single product variant being palletised. |
| **Layer** | A single horizontal tier of cases placed on the pallet. |
| **Cases per layer** | Number of case units placed in one layer. |
| **Overhang** | Case footprint extends beyond the pallet edge. Negative `edge_clearance_mm` value. |
| **Underhang** | Gap between the case footprint boundary and the pallet edge. Positive `edge_clearance_mm` value. |
| **Tolerance** | Allowed overhang or underhang in mm per side per axis. |
| **auto_underhang** | Solver flag that automatically determines the minimum feasible underhang, overriding explicit tolerance inputs. |
| **Fill efficiency** | `(case footprint area × cases per layer) / pallet area × 100 %`. |
| **Interlock** | Alternating-row offset pattern where alternate rows are shifted by half a case width to improve stability. |
| **Run** | A single solver invocation; corresponds to one run directory and one `bundle.json`. |
| **Bundle** | The `bundle.json` master record plus all artifact files for a run, stored under `04_Output/<run_id>/`. |
| **Stack height** | Pallet deck height + (case height × layer count). Policy cap is 2 000 mm. |
| **Headroom** | `max_stack_height_mm − current_stack_height_mm`. Positive means room to add layers. |
| **Effective ceiling** | The most conservative binding upper bound on layer count from height and weight ceilings. |
| **Recommended adoption range** | `[current_layers + 1 .. min(current_layers + 3, effective_ceiling)]`. |
| **Run ID** | Unique identifier for a run: `R{n:04d}_{YYYYMMDD}`. |
| **Step 1 MVP** | Current phase: deterministic, upright-only, single-SKU, grid patterns only. |
| **Phase 2b** | Stacking guidance (height/weight analysis, adoption range) — implemented in Step 1 codebase. |
| **Precision Industrial Dark** | The name of the UI visual theme. |
| **Palantir-style** | The tone used for AI-authored summaries: concise, data-driven, professional, no filler phrases. |
