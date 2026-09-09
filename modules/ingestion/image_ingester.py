import os
from PIL import Image
from modules.ocr.ocr_engine import run_ocr
from modules.detection.detector import run_detection
from modules.detection.metadata import parse_detections
from modules.detection.visualization import draw_boxes
from modules.embeddings.text_embedding import chunk_text


def ingest_image(file_path: str, upload_id: str, original_filename: str = None) -> tuple[list[dict], dict]:
    """
    Process an image:
    1. Extract text using Tesseract OCR
    2. Detect objects using YOLO
    3. Generate annotated image if objects found
    4. Construct chunked representation with rich metadata
    """
    if original_filename is None:
        original_filename = os.path.basename(file_path)

    # 1. OCR Extraction
    ocr_results = run_ocr(file_path)
    ocr_lines = []
    for item in ocr_results:
        if len(item) >= 2:
            ocr_lines.append(str(item[1]))
    ocr_text = " ".join(ocr_lines).strip()

    # 2. YOLO Object Detection
    detected_labels = []
    try:
        detection_results = run_detection(file_path)
        parsed_detection = parse_detections(detection_results)
        detected_labels = parsed_detection.get("labels", [])
        if parsed_detection.get("count", 0) > 0:
            name, ext = os.path.splitext(file_path)
            annotated_path = f"{name}_detected{ext}"
            draw_boxes(file_path, parsed_detection["detections"], annotated_path)
    except Exception as e:
        print(f"[IMAGE INGESTER] Object detection warning: {e}")

    # 3. Combine OCR text & Object descriptions
    content_parts = []
    if ocr_text:
        content_parts.append(f"Extracted Text:\n{ocr_text}")
    if detected_labels:
        content_parts.append(f"Detected Objects: {', '.join(detected_labels)}")

    combined_text = "\n\n".join(content_parts)
    if not combined_text:
        combined_text = f"Image file {original_filename} with no readable text or recognized objects."

    # 4. Chunking
    raw_chunks = chunk_text(combined_text)
    if not raw_chunks:
        raw_chunks = [combined_text]

    chunks = []
    for i, chk in enumerate(raw_chunks):
        chunks.append({
            "text": chk,
            "upload_id": upload_id,
            "source_file": original_filename,
            "content_type": "image",
            "chunk_id": i + 1,
            "image_path": file_path,
            "detected_objects": detected_labels
        })

    doc_meta = {
        "upload_id": upload_id,
        "source_file": original_filename,
        "content_type": "image",
        "chunks": len(chunks),
        "detected_objects_count": len(detected_labels),
        "ocr_char_count": len(ocr_text),
        "status": "indexed"
    }

    return chunks, doc_meta
