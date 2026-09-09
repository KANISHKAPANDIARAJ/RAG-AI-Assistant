from fastapi import APIRouter, HTTPException
from collections import defaultdict

from modules.vector_db.index_manager import create_index, add_to_index
from modules.vector_db.faiss_store import save_index, load_index, index_exists, reset_index
from modules.embeddings.models import EMBEDDING_DIMENSION

router = APIRouter()


@router.post("/vectordb/store")
def store_embeddings(payload: dict):
    chunks = payload.get("chunks")
    embeddings = payload.get("embeddings")
    upload_id = payload.get("upload_id")
    source_file = payload.get("source_file", "unknown")
    content_type = payload.get("content_type", "document")

    if not chunks or not embeddings:
        raise HTTPException(
            status_code=400,
            detail="No chunks or embeddings provided"
        )

    if not upload_id:
        raise HTTPException(
            status_code=400,
            detail="No upload_id provided"
        )

    # Load existing index
    if index_exists():
        index, metadata = load_index()
        if index is None:
            raise HTTPException(
                status_code=500,
                detail="FAISS index and metadata are out of sync. Please reset the vector store."
            )
    else:
        index = create_index(EMBEDDING_DIMENSION)
        metadata = []

    # Add embeddings
    index = add_to_index(index, embeddings)

    # Add matching metadata
    for i, chunk in enumerate(chunks):
        metadata.append({
            "text": chunk,
            "upload_id": upload_id,
            "source_file": source_file,
            "content_type": content_type,
            "chunk_id": i + 1
        })

    # Safety check
    if index.ntotal != len(metadata):
        raise HTTPException(
            status_code=500,
            detail=(
                f"Vector/metadata mismatch after insertion: "
                f"{index.ntotal} vectors vs {len(metadata)} metadata entries"
            )
        )

    save_index(index, metadata)

    return {
        "message": "Embeddings stored in FAISS",
        "data": {
            "total_vectors": index.ntotal,
            "metadata_count": len(metadata),
            "chunks_stored": len(chunks),
            "upload_id": upload_id,
            "source_file": source_file
        }
    }


@router.get("/vectordb/status")
def get_status():
    if not index_exists():
        return {
            "exists": False,
            "total_vectors": 0,
            "metadata_count": 0,
            "document_count": 0,
            "synchronized": True
        }

    index, metadata = load_index()

    if index is None:
        return {
            "exists": True,
            "total_vectors": 0,
            "metadata_count": 0,
            "document_count": 0,
            "synchronized": False
        }

    # Count unique documents
    unique_docs = len(set(m.get("upload_id") for m in metadata if isinstance(m, dict) and m.get("upload_id")))

    return {
        "exists": True,
        "total_vectors": index.ntotal,
        "metadata_count": len(metadata),
        "document_count": unique_docs,
        "synchronized": index.ntotal == len(metadata)
    }


@router.get("/vectordb/documents")
def get_documents():
    """
    Return all indexed documents grouped by upload_id.
    """
    if not index_exists():
        return {"documents": []}

    index, metadata = load_index()
    if not metadata:
        return {"documents": []}

    docs_map = defaultdict(lambda: {
        "upload_id": "",
        "source_file": "",
        "content_type": "document",
        "pages": 0,
        "slides": 0,
        "chunks": 0,
        "status": "indexed"
    })

    seen_pages = defaultdict(set)
    seen_slides = defaultdict(set)

    for item in metadata:
        if not isinstance(item, dict):
            continue
        uid = item.get("upload_id") or "legacy"
        docs_map[uid]["upload_id"] = uid
        docs_map[uid]["source_file"] = item.get("source_file", "unknown")
        docs_map[uid]["content_type"] = item.get("content_type", "document")
        docs_map[uid]["chunks"] += 1

        if "page" in item and item["page"] is not None:
            seen_pages[uid].add(item["page"])
        if "slide" in item and item["slide"] is not None:
            seen_slides[uid].add(item["slide"])

    documents = []
    for uid, doc in docs_map.items():
        if seen_pages[uid]:
            doc["pages"] = len(seen_pages[uid])
        if seen_slides[uid]:
            doc["slides"] = len(seen_slides[uid])
        documents.append(doc)

    return {"documents": documents}


@router.post("/vectordb/reset")
def reset_store():
    """
    Safely wipe the FAISS vector store and metadata.
    """
    success = reset_index()
    if success:
        return {
            "message": "Vector store reset successfully",
            "status": "cleared"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to reset vector store."
        )