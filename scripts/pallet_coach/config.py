from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values

_ENV_LOADED = False


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_env_ai() -> None:
    """Load env.ai values into process env without overriding existing vars."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    env_path = _repo_root() / "env.ai"
    if env_path.exists() and env_path.is_file():
        for key, value in dotenv_values(env_path).items():
            if key and value is not None and key not in os.environ:
                os.environ[key] = value

    _ENV_LOADED = True


def validate_runtime_config() -> None:
    """Validate runtime env values that must be well-formed when provided."""
    for timeout_var in ("AZURE_OAI_TIMEOUT_S", "GOOGLE_AI_TIMEOUT_S"):
        raw_value = os.getenv(timeout_var)
        if raw_value is None or str(raw_value).strip() == "":
            continue
        try:
            float(raw_value)
        except ValueError as exc:
            raise RuntimeError(f"Invalid numeric value for {timeout_var}: {raw_value}") from exc
