from __future__ import annotations

from pathlib import Path
from chromadb import PersistentClient

from app.config.settings import get_settings


def get_chroma_client() -> PersistentClient:
    settings = get_settings()
    # storage dir beside app.db, but under chroma/
    db_path = Path(settings.db_path)
    chroma_dir = db_path.parent / "chroma"
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return PersistentClient(path=str(chroma_dir))


def get_default_collection(name: str = "documents"):
    client = get_chroma_client()
    # create if not exists
    return client.get_or_create_collection(name)
