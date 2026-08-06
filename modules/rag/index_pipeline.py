import uuid
from modules.pdf.pdf_utils import pdf_to_image
from modules.ocr.ocr_engine import run_ocr
from modules.embeddings.text_embedding import (
    chunk_text,
    embed_chunks,
)
from modules.vector_db.faiss_store import (
    load_index,
    save_index,
    index_exists,
)
from modules.vector_db.index_manager import (
    create_index,
    add_to_index,
)
from modules.embeddings.models import EMBEDDING_DIMENSION


def index_document(file_path: str):
    """
    OCR -> Chunk -> Embed -> Store in FAISS
    """

    upload_id = str(uuid.uuid4())
    # Convert PDF to image if needed
    if file_path.lower().endswith(".pdf"):
        image_path = pdf_to_image(file_path)
    else:
        image_path = file_path
    # OCR
    ocr_results = run_ocr(image_path)

    full_text = " ".join(
        [item[1] for item in ocr_results]
    )

    if not full_text.strip():
        raise Exception("No OCR text extracted.")

    # Chunk
    chunks = chunk_text(full_text)

    # Embed
    embeddings = embed_chunks(chunks)

    # Load/Create FAISS
    if index_exists():
        index, metadata = load_index()
    else:
        index = create_index(EMBEDDING_DIMENSION)
        metadata = []

    # Store vectors
    index = add_to_index(index, embeddings)

    # Store metadata
    for chunk in chunks:
        metadata.append({
            "text": chunk,
            "upload_id": upload_id,
            "source_file": image_path
        })

    save_index(index, metadata)

    return upload_id