import os
import shutil
from pathlib import Path

import fitz  # PyMuPDF

from fastapi import UploadFile, HTTPException
from backend.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB


def pdf_to_image(pdf_path: str) -> str:
    """
    Convert the first page of a PDF into a PNG image.
    Returns the generated image path.
    """
    doc = fitz.open(pdf_path)

    if len(doc) == 0:
        doc.close()
        raise HTTPException(status_code=400, detail="PDF has no pages.")

    page = doc.load_page(0)

    # Higher resolution for better OCR
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    image_path = str(Path(pdf_path).with_suffix(".png"))

    pix.save(image_path)

    doc.close()

    return image_path


def save_file(file: UploadFile) -> dict:
    ext = Path(file.filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Use jpg, jpeg, png or pdf."
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = os.path.getsize(save_path) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        os.remove(save_path)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB."
        )

    # -------- PDF --------
    if ext == ".pdf":
        image_path = pdf_to_image(save_path)

        return {
            "filename": file.filename,
            "path": image_path,          # PNG path
            "original_pdf": save_path,   # original PDF
            "type": "image",             # continue through image pipeline
            "size_mb": round(file_size_mb, 2)
        }

    # -------- IMAGE --------
    return {
        "filename": file.filename,
        "path": save_path,
        "type": "image",
        "size_mb": round(file_size_mb, 2)
    }