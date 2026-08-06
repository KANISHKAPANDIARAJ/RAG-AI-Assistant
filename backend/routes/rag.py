# Example update for your backend/routes/rag.py or similar endpoint

from fastapi import APIRouter, HTTPException
from modules.rag.pipeline import answer_question

router = APIRouter()

@router.post("/ask")
def ask_question(payload: dict):
    """
    Ask a question about uploaded documents + images.
    
    Payload:
    {
        "question": str,          # Required: user's question
        "upload_id": str,         # Required: scopes retrieval to this upload
        "image_path": str,        # Optional: path to image for vision model
        "top_k": int              # Optional: number of context chunks (default 3)
    }
    """
    question = payload.get("question")
    upload_id = payload.get("upload_id")
    image_path = payload.get("image_path")  # NEW: image for vision model
    top_k = payload.get("top_k", 3)
    
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    if not upload_id:
        raise HTTPException(status_code=400, detail="No upload_id provided")
    
    try:
        result = answer_question(
            question=question,
            image_path=image_path,     # Pass through to RAG pipeline
            upload_id=upload_id,
            top_k=top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))