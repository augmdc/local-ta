from __future__ import annotations

import io
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import storage as storage_router
from app.utils import storage


def _setup_storage(monkeypatch, tmp_path: Path) -> None:
    uploads = tmp_path / "storage" / "uploads"
    rubrics = tmp_path / "storage" / "rubrics"

    monkeypatch.setattr(storage, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(storage, "UPLOADS_DIR", uploads)
    monkeypatch.setattr(storage, "RUBRICS_DIR", rubrics)

    monkeypatch.setattr(storage_router, "ensure_storage_dirs", storage.ensure_storage_dirs)
    monkeypatch.setattr(storage_router, "ensure_rubrics_dir", storage.ensure_rubrics_dir)
    monkeypatch.setattr(storage_router, "get_repo_root", storage.get_repo_root)


def _create_client(monkeypatch, tmp_path: Path) -> TestClient:
    _setup_storage(monkeypatch, tmp_path)
    app = FastAPI()
    app.include_router(storage_router.router, prefix="/api")
    return TestClient(app)


def test_upload_pdf_success(tmp_path, monkeypatch):
    with _create_client(monkeypatch, tmp_path) as client:
        payload = io.BytesIO(b"sample pdf bytes")
        response = client.post(
            "/api/upload",
            files={"file": ("example.PDF", payload, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    expected_sha = storage.compute_sha256(tmp_path / data["stored_as"])
    assert data == {
        "status": "ok",
        "filename": "example.PDF",
        "stored_as": data["stored_as"],
        "bytes": len(b"sample pdf bytes"),
        "sha256": expected_sha,
    }

    stored_file = tmp_path / data["stored_as"]
    assert stored_file.exists()
    assert stored_file.read_bytes() == b"sample pdf bytes"


def test_upload_rejects_non_pdf(tmp_path, monkeypatch):
    with _create_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/api/upload",
            files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are accepted at this endpoint"


def test_upload_rubric_allows_text(tmp_path, monkeypatch):
    with _create_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/api/upload-rubric",
            files={"file": ("rubric.TXT", io.BytesIO(b"rubric"), "text/plain")},
        )

    assert response.status_code == 200
    data = response.json()
    stored_file = tmp_path / data["stored_as"]
    assert stored_file.exists()
    assert stored_file.read_text() == "rubric"
