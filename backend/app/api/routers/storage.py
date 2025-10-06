from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.utils.storage import ensure_storage_dirs, ensure_rubrics_dir, sanitize_filename, save_upload, compute_sha256, get_repo_root

router = APIRouter()


@router.post("/upload", tags=["storage"])
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    # Very light validation; the full parsing/embedding will validate PDF later
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted at this endpoint")

    uploads = ensure_storage_dirs()
    safe_name = sanitize_filename(file.filename)
    target = uploads / safe_name

    # Save to disk using chunked copy
    # Starlette UploadFile exposes a SpooledTemporaryFile via file.file
    bytes_written = save_upload(file.file, target)

    checksum = compute_sha256(target)

    # Prefer path relative to repo root for stability regardless of CWD
    try:
        stored_rel = str(target.relative_to(get_repo_root()))
    except Exception:
        stored_rel = str(target)

    return {
        "status": "ok",
        "filename": file.filename,
        "stored_as": stored_rel,
        "bytes": bytes_written,
        "sha256": checksum,
    }


@router.post("/upload-rubric", tags=["storage"])
async def upload_rubric(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    lower = file.filename.lower()
    if not (lower.endswith(".pdf") or lower.endswith(".txt") or lower.endswith(".md")):
        raise HTTPException(status_code=400, detail="Rubric must be a PDF, TXT, or MD file")

    rubrics_dir = ensure_rubrics_dir()
    safe_name = sanitize_filename(file.filename)
    target = rubrics_dir / safe_name

    bytes_written = save_upload(file.file, target)
    checksum = compute_sha256(target)

    try:
        stored_rel = str(target.relative_to(get_repo_root()))
    except Exception:
        stored_rel = str(target)

    return {
        "status": "ok",
        "filename": file.filename,
        "stored_as": stored_rel,
        "bytes": bytes_written,
        "sha256": checksum,
    }
