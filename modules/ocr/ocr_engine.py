import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

def run_ocr(image_path: str) -> list:
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    results = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        conf = int(data['conf'][i])
        if text and conf > 0:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            bbox = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
            results.append([bbox, text, conf / 100.0])

    return results