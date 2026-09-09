import os
import uuid
from backend.config import (
    IMAGE_EXTENSIONS,
    PDF_EXTENSIONS,
    PPT_EXTENSIONS,
    AUDIO_EXTENSIONS,
    TEXT_EXTENSIONS,
    EMBEDDING_DIMENSION
)
from modules.ingestion.image_ingester import ingest_image
from modules.ingestion.pdf_ingester import ingest_pdf
from modules.ingestion.ppt_ingester import ingest_pptx
from modules.ingestion.audio_ingester import ingest_audio
from modules.ingestion.text_ingester import ingest_text

from modules.embeddings.text_embedding import embed_chunks
from modules.vector_db.index_manager import create_index, add_to_index
from modules.vector_db.faiss_store import load_index, save_index, index_exists


def ingest_file(file_path: str, original_filename: str = None, upload_id: str = None) -> dict:
    """
    Central file dispatcher:
    1. Identifies file type.
    2. Invokes appropriate ingestion processor.
    3. Generates embeddings locally for all chunks.
    4. Safely adds to FAISS vector store ensuring invariant index.ntotal == len(metadata).
    5. Returns document summary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if original_filename is None:
        original_filename = os.path.basename(file_path)

    if upload_id is None:
        upload_id = uuid.uuid4().hex[:8]

    ext = os.path.splitext(original_filename)[1].lower()

    if ext in IMAGE_EXTENSIONS:
        chunks, doc_meta = ingest_image(file_path, upload_id, original_filename)
    elif ext in PDF_EXTENSIONS:
        chunks, doc_meta = ingest_pdf(file_path, upload_id, original_filename)
    elif ext in PPT_EXTENSIONS:
        chunks, doc_meta = ingest_pptx(file_path, upload_id, original_filename)
    elif ext in AUDIO_EXTENSIONS:
        chunks, doc_meta = ingest_audio(file_path, upload_id, original_filename)
    elif ext in TEXT_EXTENSIONS:
        chunks, doc_meta = ingest_text(file_path, upload_id, original_filename)
    else:
        raise ValueError(f"Unsupported file type '{ext}' for file: {original_filename}")

    if not chunks:
        raise ValueError(f"No text content could be extracted from: {original_filename}")

    # Generate embeddings locally
    texts_to_embed = [c["text"] for c in chunks]
    embeddings = embed_chunks(texts_to_embed)

    # Load or initialize FAISS index
    if index_exists():
        index, metadata = load_index()
        if index is None:
            print("[DISPATCHER] Corrupted index detected; creating fresh index...")
            index = create_index(EMBEDDING_DIMENSION)
            metadata = []
    else:
        index = create_index(EMBEDDING_DIMENSION)
        metadata = []

    # Append to FAISS
    index = add_to_index(index, embeddings)

    # Append metadata matching each vector
    for chunk in chunks:
        metadata.append(chunk)

    # Strict invariant validation
    if index.ntotal != len(metadata):
        raise RuntimeError(
            f"FAISS invariant violated during ingestion: {index.ntotal} vectors vs {len(metadata)} metadata items."
        )

    # Save to disk
    save_index(index, metadata)

    return {
        "upload_id": upload_id,
        "source_file": original_filename,
        "content_type": doc_meta.get("content_type", "unknown"),
        "pages": doc_meta.get("pages"),
        "slides": doc_meta.get("slides"),
        "duration_seconds": doc_meta.get("duration_seconds"),
        "chunks": len(chunks),
        "total_vectors": index.ntotal,
        "status": "indexed"
    }
