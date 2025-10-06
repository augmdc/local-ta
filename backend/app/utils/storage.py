from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import BinaryIO, Tuple

SAFE_CHARS = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_repo_root() -> Path:
    # backend/app/utils/storage.py -> repo root is parents[3]
    return Path(__file__).resolve().parents[3]


def get_storage_dir() -> Path:
    return get_repo_root() / "storage" / "uploads"


def ensure_storage_dirs() -> Path:
    uploads = get_storage_dir()
    uploads.mkdir(parents=True, exist_ok=True)
    return uploads


def get_rubrics_dir() -> Path:
    return get_repo_root() / "storage" / "rubrics"


def ensure_rubrics_dir() -> Path:
    rubrics = get_rubrics_dir()
    rubrics.mkdir(parents=True, exist_ok=True)
    return rubrics


def sanitize_filename(filename: str) -> str:
    return "".join(c for c in filename if c in SAFE_CHARS) or "upload.bin"


def compute_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def save_upload(stream: BinaryIO, dest_path: Path, chunk_size: int = 1024 * 1024) -> int:
    bytes_written = 0
    with dest_path.open("wb") as out:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            out.write(chunk)
            bytes_written += len(chunk)
    return bytes_written
