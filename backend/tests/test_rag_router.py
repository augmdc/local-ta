from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import rag


class _Recorder:
    def __init__(self) -> None:
        self.built = 0
        self.queries = []

    def build(self) -> None:
        self.built += 1

    def query(self, question: str, top_k: int = 3) -> str:
        self.queries.append((question, top_k))
        return f"answer-for:{question}:{top_k}"


def _create_client(monkeypatch, service):
    monkeypatch.setattr(rag, "_service", service)
    app = FastAPI()
    app.include_router(rag.router, prefix="/api")
    return TestClient(app)


def test_ingest_triggers_build(monkeypatch):
    recorder = _Recorder()
    with _create_client(monkeypatch, recorder) as client:
        response = client.post("/api/ingest")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert recorder.built == 1


def test_query_uses_service(monkeypatch):
    recorder = _Recorder()
    with _create_client(monkeypatch, recorder) as client:
        response = client.post("/api/query", json={"question": "What?", "top_k": 5})

    assert response.status_code == 200
    assert response.json() == {"answer": "answer-for:What?:5"}
    assert recorder.queries == [("What?", 5)]


def test_query_defaults_top_k(monkeypatch):
    recorder = _Recorder()
    with _create_client(monkeypatch, recorder) as client:
        response = client.post("/api/query", json={"question": "Hi"})

    assert response.status_code == 200
    assert response.json() == {"answer": "answer-for:Hi:3"}
    assert recorder.queries == [("Hi", 3)]
