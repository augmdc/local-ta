from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag.index import RagService

router = APIRouter()
_service = RagService()


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


@router.post("/ingest", tags=["rag"])
def ingest() -> dict:
    _service.build()
    return {"status": "ok"}


@router.post("/query", tags=["rag"])
def query(req: QueryRequest) -> dict:
    answer = _service.query(req.question, top_k=req.top_k)
    return {"answer": answer}
