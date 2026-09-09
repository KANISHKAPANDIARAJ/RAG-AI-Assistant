from fastapi import APIRouter, HTTPException
from modules.preprocessing import preprocess
import os
import fitz

router = APIRouter()


@router.post("/process")
def process_image(payload: dict):
    path = payload.get("path")

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=400, detail="File not found")

    if path.lower().endswith(".pdf"):
        doc = fitz.open(path)
        if len(doc) == 0:
            doc.close()
            raise HTTPException(status_code=400, detail="Empty PDF")
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        rendered_path = os.path.splitext(path)[0] + "_preview.png"
        pix.save(rendered_path)
        doc.close()
        processed_path = preprocess(rendered_path)
    else:
        processed_path = preprocess(path)

    return {
        "message": "Image processed successfully",
        "processed_path": processed_path
    }