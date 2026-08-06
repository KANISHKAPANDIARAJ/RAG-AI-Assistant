from ultralytics import YOLO

_model = None

def get_model():
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")
    return _model

def run_detection(image_path: str) -> list:
    model = get_model()
    results = model(image_path, verbose=False)
    return results