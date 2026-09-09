import os
import fitz  # PyMuPDF
from modules.ocr.ocr_engine import run_ocr
from modules.embeddings.text_embedding import chunk_text
from backend.config import MAX_PDF_PAGES, UPLOAD_DIR


def ingest_pdf(file_path: str, upload_id: str, original_filename: str = None) -> tuple[list[dict], dict]:
    """
    Process a PDF file page by page:
    1. Extract selectable text via PyMuPDF.
    2. If page has minimal text (< 30 chars), render page to image and run Tesseract OCR.
    3. Create page-aware chunks preserving page number for every chunk.
    """
    if original_filename is None:
        original_filename = os.path.basename(file_path)

    doc = fitz.open(file_path)
    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        raise ValueError(f"PDF '{original_filename}' has 0 pages.")

    pages_to_process = min(total_pages, MAX_PDF_PAGES)
    chunks = []
    chunk_counter = 0

    render_dir = os.path.join(UPLOAD_DIR, "rendered_pages")
    os.makedirs(render_dir, exist_ok=True)

    for page_num in range(1, pages_to_process + 1):
        page = doc.load_page(page_num - 1)
        
        # Try direct text extraction
        extracted_text = page.get_text("text").strip()
        page_image_path = None

        # Fallback to OCR if page has very little selectable text
        if len(extracted_text) < 30:
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                base_name = os.path.splitext(original_filename)[0]
                page_image_path = os.path.join(render_dir, f"{base_name}_p{page_num}_{upload_id[:6]}.png")
                pix.save(page_image_path)
                
                ocr_results = run_ocr(page_image_path)
                ocr_lines = [str(item[1]) for item in ocr_results if len(item) >= 2]
                ocr_text = " ".join(ocr_lines).strip()
                if ocr_text:
                    extracted_text = ocr_text
            except Exception as e:
                print(f"[PDF INGESTER] OCR fallback error on page {page_num}: {e}")

        if not extracted_text:
            extracted_text = f"[Page {page_num} of {original_filename} contains non-text or visual content]"

        # Chunk this page's text
        page_chunks = chunk_text(extracted_text)
        if not page_chunks:
            page_chunks = [extracted_text]

        for p_chk in page_chunks:
            chunk_counter += 1
            chunks.append({
                "text": p_chk,
                "upload_id": upload_id,
                "source_file": original_filename,
                "content_type": "pdf",
                "page": page_num,
                "chunk_id": chunk_counter,
                "image_path": page_image_path
            })

    doc.close()

    doc_meta = {
        "upload_id": upload_id,
        "source_file": original_filename,
        "content_type": "pdf",
        "pages": pages_to_process,
        "total_pages": total_pages,
        "chunks": len(chunks),
        "status": "indexed"
    }

    return chunks, doc_meta
