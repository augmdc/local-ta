from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import health


class _FakeSettings:
    def __init__(self) -> None:
        self.ollama_base_url = "http://example.com"
        self.default_model = "demo-model"
        self.embedding_model = "demo-embed"


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr(health, "get_settings", lambda: _FakeSettings())

    app = FastAPI()
    app.include_router(health.router, prefix="/api")

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "ollama_base_url": "http://example.com",
        "default_model": "demo-model",
        "embedding_model": "demo-embed",
    }
