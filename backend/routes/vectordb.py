from fastapi import APIRouter, HTTPException
from modules.vector_db.index_manager import create_index, add_to_index
from modules.vector_db.faiss_store import save_index, load_index, index_exists
from modules.embeddings.models import EMBEDDING_DIMENSION

router = APIRouter()

@router.post("/vectordb/store")
def store_embeddings(payload: dict):
    chunks = payload.get("chunks")
    embeddings = payload.get("embeddings")
    upload_id = payload.get("upload_id")
    source_file = payload.get("source_file", "unknown")

    if not chunks or not embeddings:
        raise HTTPException(status_code=400, detail="No chunks or embeddings provided")
    if not upload_id:
        raise HTTPException(status_code=400, detail="No upload_id provided")

    if index_exists():
        index, metadata = load_index()
    else:
        index = create_index(EMBEDDING_DIMENSION)
        metadata = []

    index = add_to_index(index, embeddings)

    for chunk in chunks:
        metadata.append({
            "text": chunk,
            "upload_id": upload_id,
            "source_file": source_file
        })

    save_index(index, metadata)

    return {
        "message": "Embeddings stored in FAISS",
        "data": {
            "total_vectors": index.ntotal,
            "chunks_stored": len(chunks),
            "upload_id": upload_id
        }
    }

@router.get("/vectordb/status")
def get_status():
    if not index_exists():
        return {"exists": False, "total_vectors": 0}
    index, metadata = load_index()
    return {
        "exists": True,
        "total_vectors": index.ntotal,
        "metadata_count": len(metadata)
    }