from __future__ import annotations

from datetime import datetime, timezone

import pytest

from pallet_coach.api import run_store


def test_run_id_format_and_daily_increment(tmp_path, monkeypatch):
    monkeypatch.setattr(run_store, "get_output_root", lambda: tmp_path)

    rid1 = run_store.allocate_run_id(datetime(2026, 4, 17, tzinfo=timezone.utc))
    run_store.create_run_dir(rid1)
    rid2 = run_store.allocate_run_id(datetime(2026, 4, 17, tzinfo=timezone.utc))

    assert rid1 == "R0001_20260417"
    assert rid2 == "R0002_20260417"


def test_safe_run_path_allows_valid_and_blocks_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(run_store, "get_output_root", lambda: tmp_path)

    run_store.ensure_output_root()
    run_dir = run_store.create_run_dir("R0001_20260417")
    assert run_store.resolve_run_dir_safe("R0001_20260417") == run_dir

    with pytest.raises(FileNotFoundError):
        run_store.resolve_run_dir_safe("../escape")
