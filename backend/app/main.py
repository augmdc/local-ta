from __future__ import annotations

import logging
from typing import Dict

from fastapi import FastAPI

from .config import get_config
from .logging.setup import configure_json_logging
from .ollama_manager import ensure_models, ensure_server, list_models
from .api.routers.health import router as health_router
from .api.routers.rag import router as rag_router
from .api.routers.storage import router as storage_router
from .config.settings import get_settings

settings = get_settings()

# Configure JSON logging
configure_json_logging(level=getattr(logging, settings.log_level, logging.INFO))

app = FastAPI(title="local-ta backend")

# Mount API routers under configured prefix
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(rag_router, prefix=settings.api_prefix)
app.include_router(storage_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def _startup() -> None:
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


