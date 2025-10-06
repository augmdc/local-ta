from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_app_endpoints(monkeypatch):
    # Stub out Ollama startup to avoid external dependency during tests
    from app import ollama_manager

    monkeypatch.setattr(ollama_manager, "ensure_server", lambda *a, **k: True)
    monkeypatch.setattr(ollama_manager, "ensure_models", lambda *a, **k: ["model-a", "model-b"])
    monkeypatch.setattr(ollama_manager, "list_models", lambda *a, **k: ["model-a", "model-b"])

    with TestClient(app) as client:
        # health under both base and router path
        r = client.get("/health")
        assert r.status_code == 200
        r = client.get("/api/health")
        assert r.status_code == 200

        # ingest
        r = client.post("/api/ingest")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        # query
        r = client.post("/api/query", json={"question": "Hello", "top_k": 2})
        assert r.status_code == 200
        assert "answer" in r.json()


