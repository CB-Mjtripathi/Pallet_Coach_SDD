from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_TEMPLATE_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def _prompt_root() -> Path:
    return Path(__file__).resolve().parent / "prompts"


def load_prompt_template(name: str) -> str:
    path = _prompt_root() / name
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {name}")
    return path.read_text(encoding="utf-8")


def render_prompt_template(name: str, variables: dict[str, Any]) -> str:
    template = load_prompt_template(name)

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Missing template variable: {key}")
        return str(variables[key])

    return _TEMPLATE_PATTERN.sub(_replace, template)
