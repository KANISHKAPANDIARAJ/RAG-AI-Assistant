from fastapi import APIRouter, HTTPException
from modules.preprocessing import preprocess
import os

router = APIRouter()

@router.post("/process")
def process_image(payload: dict):
    path = payload.get("path")

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=400, detail="File not found")

    if path.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDFs not supported in Phase 5")

    processed_path = preprocess(path)
    return {
        "message": "Image processed successfully",
        "processed_path": processed_path
    }