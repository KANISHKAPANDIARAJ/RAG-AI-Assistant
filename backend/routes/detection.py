from fastapi import APIRouter, HTTPException
from modules.detection.detector import run_detection
from modules.detection.metadata import parse_detections
from modules.detection.visualization import draw_boxes
import os

router = APIRouter()

@router.post("/detect")
def detect_objects(payload: dict):
    path = payload.get("path")

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=400, detail="File not found")

    results = run_detection(path)
    parsed = parse_detections(results)

    save_path = path.replace(".jpg", "_detected.jpg").replace(".png", "_detected.png")
    draw_boxes(path, parsed["detections"], save_path)

    parsed["annotated_path"] = save_path

    return {
        "message": "Detection complete",
        "data": parsed
    }