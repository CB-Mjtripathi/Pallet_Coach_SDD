from __future__ import annotations

import pytest

from pallet_coach.prompt_templates import load_prompt_template, render_prompt_template


def test_load_prompt_template_reads_existing_file():
    text = load_prompt_template("azure_summary_system.md")
    assert "Pallet Coach" in text


def test_render_prompt_template_substitutes_variables():
    rendered = render_prompt_template(
        "image_prompt_flat_template.md",
        {"run_id": "R0001_20260417", "context_json": "{\"k\":\"v\"}"},
    )
    assert "R0001_20260417" in rendered
    assert "{\"k\":\"v\"}" in rendered
    assert "{{run_id}}" not in rendered


def test_render_prompt_template_missing_variable_raises_key_error():
    with pytest.raises(KeyError):
        render_prompt_template("image_prompt_3d_template.md", {"run_id": "R0002_20260417"})
