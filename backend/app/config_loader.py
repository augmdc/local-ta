from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class AppConfig:
    ollama_host: str
    default_llm: str
    embedding_model: str


def load_yaml_config() -> Dict[str, Any]:
    # Resolve repo root from this file: backend/app/config.py -> repo root is parents[2]
    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / "configs" / "app.yaml"
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_config() -> AppConfig:
    cfg = load_yaml_config()

    # Support both legacy nested keys and new flat keys
    server_cfg = (cfg.get("server") or {}) if isinstance(cfg, dict) else {}
    models_cfg = (cfg.get("models") or {}) if isinstance(cfg, dict) else {}

    # New flat keys
    flat_ollama = cfg.get("ollama_base_url") if isinstance(cfg, dict) else None
    flat_default = cfg.get("default_model") if isinstance(cfg, dict) else None
    flat_embed = cfg.get("embedding_model") if isinstance(cfg, dict) else None

    ollama_host = (
        os.getenv("OLLAMA_HOST")
        or flat_ollama
        or server_cfg.get("ollama_host")
        or "http://127.0.0.1:11434"
    )
    default_llm = (
        os.getenv("DEFAULT_MODEL")
        or flat_default
        or models_cfg.get("default_llm")
        or "qwen2.5:7b-instruct"
    )
    embedding_model = (
        os.getenv("EMBED_MODEL")
        or flat_embed
        or models_cfg.get("embedding")
        or "nomic-embed-text"
    )

    return AppConfig(
        ollama_host=ollama_host,
        default_llm=default_llm,
        embedding_model=embedding_model,
    )
