from fastapi import APIRouter, HTTPException
from modules.ocr.ocr_engine import run_ocr
from modules.ocr.parser import parse_ocr_result
from modules.ocr.utils import filter_low_confidence
import os

router = APIRouter()

@router.post("/ocr")
def extract_text(payload: dict):
    path = payload.get("path")

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=400, detail="File not found")

    raw_result = run_ocr(path)
    parsed = parse_ocr_result(raw_result)
    parsed["lines"] = filter_low_confidence(parsed["lines"])

    return {
        "message": "OCR completed",
        "data": parsed
    }