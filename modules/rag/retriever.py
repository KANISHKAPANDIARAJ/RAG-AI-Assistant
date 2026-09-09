from modules.embeddings.text_embedding import embed_text
from modules.vector_db.faiss_store import load_index
from modules.vector_db.search import search_index


def retrieve(question: str, top_k: int = 3, upload_id: str = None) -> list[dict]:
    """
    Search vector store for chunks relevant to the question.
    Safely preserves all source metadata (page, slide, timestamp, etc.).
    """
    if not question or not question.strip():
        return []

    index, metadata = load_index()

    if index is None or index.ntotal == 0 or not metadata:
        return []

    # If upload_id is supplied, search deeper to guarantee finding top_k matching chunks
    search_k = min(top_k * 10, index.ntotal) if upload_id else min(top_k * 2, index.ntotal)

    try:
        query_embedding = embed_text(question)
        distances, indices = search_index(
            index,
            query_embedding,
            top_k=search_k
        )
    except Exception as e:
        print(f"[RETRIEVER ERROR] Failed during vector search: {e}")
        return []

    results = []

    for dist, idx in zip(distances, indices):
        # FAISS returns -1 when there are fewer entries than requested
        if idx == -1:
            continue

        idx = int(idx)

        # Strict bounds checking to prevent IndexError
        if not (0 <= idx < len(metadata)):
            print(
                f"[RETRIEVER ERROR] Index {idx} out of bounds for metadata size {len(metadata)}"
            )
            continue

        meta = metadata[idx]

        if not isinstance(meta, dict):
            continue

        # Filter by upload_id if specified
        if upload_id and meta.get("upload_id") != upload_id:
            continue

        text = meta.get("text", "").strip()
        if not text:
            continue

        result_item = {
            "text": text,
            "distance": round(float(dist), 4),
            "index": idx,
            "upload_id": meta.get("upload_id", ""),
            "source_file": meta.get("source_file", "unknown"),
            "content_type": meta.get("content_type", "document"),
            "chunk_id": meta.get("chunk_id", idx),
        }

        # Optional modality-specific metadata
        if "page" in meta and meta["page"] is not None:
            result_item["page"] = meta["page"]
        if "slide" in meta and meta["slide"] is not None:
            result_item["slide"] = meta["slide"]
        if "start_time" in meta and meta["start_time"] is not None:
            result_item["start_time"] = meta["start_time"]
        if "end_time" in meta and meta["end_time"] is not None:
            result_item["end_time"] = meta["end_time"]
        if "detected_objects" in meta and meta["detected_objects"]:
            result_item["detected_objects"] = meta["detected_objects"]

        results.append(result_item)

        if len(results) >= top_k:
            break

    return results