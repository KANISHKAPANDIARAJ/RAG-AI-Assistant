from fastapi import APIRouter, HTTPException
from modules.embeddings.text_embedding import embed_text, chunk_text, embed_chunks

router = APIRouter()

@router.post("/embed")
def generate_embeddings(payload: dict):
    text = payload.get("text")
    upload_id = payload.get("upload_id")

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    if not upload_id:
        raise HTTPException(status_code=400, detail="No upload_id provided")

    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    return {
        "message": "Embeddings generated",
        "data": {
            "chunks": chunks,
            "embeddings_count": len(embeddings),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
            "embeddings": embeddings,
            "upload_id": upload_id
        }
    }