from modules.embeddings.text_embedding import embed_text
from modules.vector_db.faiss_store import load_index
from modules.vector_db.search import search_index

def retrieve(question: str, top_k: int = 3, upload_id: str = None) -> list[dict]:
    query_embedding = embed_text(question)
    index, metadata = load_index()

    if index is None or index.ntotal == 0:
        return []

    search_k = min(top_k * 5, index.ntotal) if upload_id else min(top_k, index.ntotal)

    distances, indices = search_index(index, query_embedding, top_k=search_k)

    results = []
    for dist, idx in zip(distances, indices):
        if idx == -1:
            continue
        meta = metadata[idx]
        if upload_id and meta.get("upload_id") != upload_id:
            continue
        results.append({
            "text": meta["text"],
            "distance": round(float(dist), 4),
            "index": int(idx)
        })
        if len(results) >= top_k:
            break

    return results