from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

RUN_ID_RE = re.compile(r"^R(\d{4})_(\d{8})$")


def get_output_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "04_Output"


def ensure_output_root() -> Path:
    root = get_output_root()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_name(name: str) -> str:
    if not name or "/" in name or "\\" in name or ".." in name:
        raise FileNotFoundError("Invalid run identifier")
    return name


def allocate_run_id(now_utc: datetime | None = None) -> str:
    now_utc = now_utc or datetime.now(timezone.utc)
    date_key = now_utc.strftime("%Y%m%d")
    root = ensure_output_root()

    max_idx = 0
    for child in root.iterdir():
        if not child.is_dir():
            continue
        m = RUN_ID_RE.match(child.name)
        if not m:
            continue
        idx = int(m.group(1))
        date_part = m.group(2)
        if date_part == date_key:
            max_idx = max(max_idx, idx)

    return f"R{max_idx + 1:04d}_{date_key}"


def create_run_dir(run_id: str) -> Path:
    run_id = _safe_name(run_id)
    root = ensure_output_root().resolve()
    candidate = (root / run_id).resolve()
    if root not in candidate.parents and candidate != root:
        raise FileNotFoundError("Unsafe run path")
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def resolve_run_dir_safe(run_id: str) -> Path:
    run_id = _safe_name(run_id)
    root = ensure_output_root().resolve()
    candidate = (root / run_id).resolve()

    if root not in candidate.parents:
        raise FileNotFoundError("Run not found")
    if not candidate.exists() or not candidate.is_dir():
        raise FileNotFoundError("Run not found")
    return candidate


def write_bundle(run_dir: Path, bundle: dict) -> Path:
    path = run_dir / "bundle.json"
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return path


def append_run_log(run_dir: Path, message: str) -> Path:
    path = run_dir / "run_log.txt"
    ts = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{ts}] {message}\n")
    return path


def tail_run_log(run_dir: Path, n_lines: int = 200) -> str:
    path = run_dir / "run_log.txt"
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-max(1, n_lines):])


def archive_loose_root_files() -> None:
    root = ensure_output_root()
    loose_files = [p for p in root.iterdir() if p.is_file()]
    if not loose_files:
        return

    archive_dir = root / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for fpath in loose_files:
        target = archive_dir / f"{stamp}_{fpath.name}"
        fpath.rename(target)
