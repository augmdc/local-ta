from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.utils.storage import (
    compute_sha256,
    ensure_rubrics_dir,
    ensure_storage_dirs,
    get_repo_root,
    sanitize_filename,
    save_upload,
)

router = APIRouter()


def _store(
    file: UploadFile,
    ensure_dir: Callable[[], Path],
    allowed_exts: Iterable[str],
    error_detail: str,
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    name = file.filename.lower()
    if allowed_exts and not any(name.endswith(ext) for ext in allowed_exts):
        raise HTTPException(status_code=400, detail=error_detail)

    directory = ensure_dir()
    target = directory / sanitize_filename(file.filename)

    written = save_upload(file.file, target)
    checksum = compute_sha256(target)

    try:
        stored_rel = str(target.relative_to(get_repo_root()))
    except ValueError:
        stored_rel = str(target)

    return {
        "status": "ok",
        "filename": file.filename,
        "stored_as": stored_rel,
        "bytes": written,
        "sha256": checksum,
    }


@router.post("/upload", tags=["storage"])
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    return _store(file, ensure_storage_dirs, (".pdf",), "Only PDF files are accepted at this endpoint")


@router.post("/upload-rubric", tags=["storage"])
async def upload_rubric(file: UploadFile = File(...)) -> dict:
    return _store(
        file,
        ensure_rubrics_dir,
        (".pdf", ".txt", ".md"),
        "Rubric must be a PDF, TXT, or MD file",
    )
