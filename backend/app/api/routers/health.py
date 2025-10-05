from fastapi import APIRouter

from app.config.settings import get_settings


router = APIRouter()


@router.get("/health", tags=["system"])
def healthcheck() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "ollama_base_url": settings.ollama_base_url,
        "default_model": settings.default_model,
        "embedding_model": settings.embedding_model,
    }


