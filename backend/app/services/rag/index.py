from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self) -> None:
        self._index_built = False

    def build(self) -> None:
        try:
            # Use absolute path from repo root
            repo_root = Path(__file__).resolve().parents[4]  # backend/app/services/rag/index.py -> repo root
            data_dir = repo_root / "data" / "sources"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Simple file count for now
            files = list(data_dir.glob("*"))
            logger.info(f"Found {len(files)} files in {data_dir}")
            self._index_built = True
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise

    def query(self, question: str, top_k: int = 3) -> str:
        try:
            if not self._index_built:
                self.build()
            
            # Simple response for now
            return f"I received your question: '{question}'. The RAG system is working but using a simplified response for testing."
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Error: {e}"
