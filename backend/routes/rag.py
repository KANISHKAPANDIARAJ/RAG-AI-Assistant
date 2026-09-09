from fastapi import APIRouter, HTTPException
from modules.rag.pipeline import answer_question
from backend.config import TOP_K

router = APIRouter()


@router.post("/ask")
def ask_question(payload: dict):
    """
    Ask a question across the knowledge base or scoped to a specific upload_id.
    """
    question = payload.get("question")
    upload_id = payload.get("upload_id")
    image_path = payload.get("image_path")
    top_k = payload.get("top_k", TOP_K)

    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="No question provided")

    try:
        result = answer_question(
            question=question.strip(),
            image_path=image_path,
            upload_id=upload_id,
            top_k=top_k
        )
        return {
            "message": "Answer generated",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))