from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

SAFE_CHARS = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
REPO_ROOT = Path(__file__).resolve().parents[3]
UPLOADS_DIR = REPO_ROOT / "storage" / "uploads"
RUBRICS_DIR = REPO_ROOT / "storage" / "rubrics"


def get_repo_root() -> Path:
    return REPO_ROOT


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_storage_dirs() -> Path:
    return _ensure_dir(UPLOADS_DIR)


def ensure_rubrics_dir() -> Path:
    return _ensure_dir(RUBRICS_DIR)


def sanitize_filename(filename: str) -> str:
    cleaned = "".join(c for c in filename if c in SAFE_CHARS)
    return cleaned or "upload.bin"


def compute_sha256(path: Path, chunk_size: int = 1 << 20) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(chunk_size), b""):
            sha.update(chunk)
    return sha.hexdigest()


def save_upload(stream: BinaryIO, dest_path: Path, chunk_size: int = 1 << 20) -> int:
    size = 0
    with dest_path.open("wb") as dst:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            dst.write(chunk)
            size += len(chunk)
    return size
