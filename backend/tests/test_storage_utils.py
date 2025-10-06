from __future__ import annotations

import io
import pytest

from app.utils import storage


@pytest.fixture
def temp_dirs(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    rubrics = tmp_path / "rubrics"

    monkeypatch.setattr(storage, "UPLOADS_DIR", uploads)
    monkeypatch.setattr(storage, "RUBRICS_DIR", rubrics)

    return uploads, rubrics


def test_sanitize_filename_preserves_safe_chars():
    assert storage.sanitize_filename("Hello-World_123.pdf") == "Hello-World_123.pdf"


def test_sanitize_filename_replaces_unsafe_chars():
    assert storage.sanitize_filename("../evil\\name?.txt") == "..evilname.txt"


def test_sanitize_filename_defaults_when_empty():
    assert storage.sanitize_filename("!!!") == "upload.bin"


def test_ensure_storage_dirs_creates_path(temp_dirs):
    uploads, _ = temp_dirs
    path = storage.ensure_storage_dirs()
    assert path == uploads
    assert uploads.exists()


def test_ensure_rubrics_dir_creates_path(temp_dirs):
    _, rubrics = temp_dirs
    path = storage.ensure_rubrics_dir()
    assert path == rubrics
    assert rubrics.exists()


def test_save_upload_writes_stream(tmp_path):
    dest = tmp_path / "file.bin"
    size = storage.save_upload(io.BytesIO(b"abc123"), dest, chunk_size=2)
    assert size == 6
    assert dest.read_bytes() == b"abc123"


def test_compute_sha256(tmp_path):
    target = tmp_path / "file.txt"
    target.write_bytes(b"hash me")
    digest = storage.compute_sha256(target, chunk_size=2)
    assert digest == "eb201af5aaf0d60629d3d2a61e466cfc0fedb517add831ecac5235e1daa963d6"
