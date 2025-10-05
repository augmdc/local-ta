from __future__ import annotations

from typing import Dict

from fastapi import FastAPI

from .config import get_config
from .ollama_manager import ensure_models, ensure_server, list_models

app = FastAPI(title="local-ta backend")


@app.on_event("startup")
def _startup() -> None:
    cfg = get_config()
    # Ensure Ollama server is up
    ensure_server(cfg.ollama_host)
    # Ensure required models are available
    ensure_models(cfg.ollama_host, [cfg.default_llm, cfg.embedding_model], quiet=True)


@app.get("/health")
def health() -> Dict[str, object]:
    cfg = get_config()
    models = list_models(cfg.ollama_host)
    return {
        "ok": True,
        "ollama_host": cfg.ollama_host,
        "default_llm": cfg.default_llm,
        "embedding_model": cfg.embedding_model,
        "installed_models": models,
    }


