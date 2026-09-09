import os
import pytesseract
from PIL import Image
from backend.config import TESSERACT_CMD

if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def run_ocr(image_or_path) -> list:
    """
    Run Tesseract OCR on a file path or PIL Image object.
    Returns list of [[bbox], text, confidence].
    """
    if isinstance(image_or_path, str):
        if not os.path.exists(image_or_path):
            return []
        image = Image.open(image_or_path)
    elif isinstance(image_or_path, Image.Image):
        image = image_or_path
    else:
        return []

    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    except Exception as e:
        print(f"[OCR ERROR] Tesseract OCR failed: {e}")
        return []

    results = []
    for i in range(len(data.get('text', []))):
        text = data['text'][i].strip()
        conf = int(data['conf'][i])
        if text and conf > 0:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            bbox = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
            results.append([bbox, text, conf / 100.0])

    return results