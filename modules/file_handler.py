import os
import shutil
import re
from pathlib import Path
from fastapi import UploadFile, HTTPException
from backend.config import (
    UPLOAD_DIR,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    IMAGE_EXTENSIONS,
    PDF_EXTENSIONS,
    PPT_EXTENSIONS,
    AUDIO_EXTENSIONS,
    TEXT_EXTENSIONS
)


def sanitize_filename(filename: str) -> str:
    """
    Remove potentially dangerous characters from filename to prevent path traversal.
    """
    # Keep alphanumeric, dots, underscores, dashes, and spaces
    clean = os.path.basename(filename)
    clean = re.sub(r'[^\w\s\.-]', '_', clean).strip()
    return clean or "uploaded_file"


def get_content_type(ext: str) -> str:
    ext = ext.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in PPT_EXTENSIONS:
        return "pptx"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in TEXT_EXTENSIONS:
        return "text"
    return "document"


def save_file(file: UploadFile) -> dict:
    original_filename = file.filename or "uploaded_file"
    ext = Path(original_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        supported = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' is not supported. Supported types: {supported}"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = sanitize_filename(original_filename)
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    # Save stream to disk
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = os.path.getsize(save_path) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        os.remove(save_path)
        raise HTTPException(
            status_code=400,
            detail=f"File size ({round(file_size_mb, 1)}MB) exceeds limit of {MAX_FILE_SIZE_MB}MB."
        )

    content_type = get_content_type(ext)

    return {
        "filename": original_filename,
        "path": save_path,
        "type": content_type,
        "size_mb": round(file_size_mb, 2)
    }