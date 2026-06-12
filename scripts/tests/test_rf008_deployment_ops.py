from __future__ import annotations

from pathlib import Path

import pytest

from pallet_coach import config


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_load_env_ai_reads_env_file_without_overriding_existing(monkeypatch, tmp_path):
    env_file = tmp_path / "env.ai"
    env_file.write_text(
        "AZURE_OAI_MODEL=from-file\nAZURE_OAI_TIMEOUT_S=77\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(config, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(config, "_ENV_LOADED", False)
    monkeypatch.setenv("AZURE_OAI_MODEL", "from-env")
    monkeypatch.delenv("AZURE_OAI_TIMEOUT_S", raising=False)

    config.load_env_ai()

    assert config.os.getenv("AZURE_OAI_MODEL") == "from-env"
    assert config.os.getenv("AZURE_OAI_TIMEOUT_S") == "77"


def test_validate_runtime_config_rejects_invalid_timeout(monkeypatch):
    monkeypatch.setenv("AZURE_OAI_TIMEOUT_S", "invalid-number")

    with pytest.raises(RuntimeError, match="AZURE_OAI_TIMEOUT_S"):
        config.validate_runtime_config()


def test_deployment_assets_exist_and_include_required_contracts():
    root = _repo_root()

    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    nginx_conf = (root / "docker" / "nginx.conf").read_text(encoding="utf-8")
    entrypoint = (root / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    init_ps1 = (root / "init_project.ps1").read_text(encoding="utf-8")
    api_ps1 = (root / "start_api.ps1").read_text(encoding="utf-8")
    ui_ps1 = (root / "start_ui.ps1").read_text(encoding="utf-8")
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")

    assert "FROM node:18" in dockerfile
    assert "FROM python:3.11-slim" in dockerfile
    assert "location /api/" in nginx_conf
    assert "location /output/" in nginx_conf
    assert "try_files $uri $uri/ /index.html;" in nginx_conf
    assert "uvicorn pallet_coach.api.app:app" in entrypoint
    assert "pip install -r scripts/requirements.txt" in init_ps1
    assert "uvicorn pallet_coach.api.app:app" in api_ps1
    assert "npm run dev" in ui_ps1
    assert "env.ai" in gitignore
