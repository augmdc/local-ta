from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(
        str(PROJECT_ROOT / "configs" / ".env"),
        str(PROJECT_ROOT / ".env"),
    ), env_file_encoding="utf-8", extra="ignore")

    # Service
    environment: str = Field(default="development")
    api_prefix: str = Field(default="/api")
    log_level: str = Field(default="INFO")

    # Models / LLM runtime
    ollama_base_url: str = Field(default="http://localhost:11434")
    default_model: str = Field(default="qwen2.5:7b-instruct")
    embedding_model: str = Field(default="nomic-embed-text")

    # Database
    db_path: str = Field(default=str(PROJECT_ROOT / "storage/app.db"))

    # Optional external YAML config that can override fields
    app_config_path: str = Field(default=str(PROJECT_ROOT / "configs/app.yaml"))

    def apply_yaml_overrides(self) -> None:
        config_path = Path(self.app_config_path)
        if not config_path.exists():
            return
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data: Dict[str, Any] = yaml.safe_load(f) or {}
        except Exception:
            return

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.apply_yaml_overrides()
    return settings


