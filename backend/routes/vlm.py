from fastapi import APIRouter, HTTPException
from modules.rag.pipeline import answer_question
from backend.config import TOP_K

router = APIRouter()


@router.post("/vlm/ask")
def ask(payload: dict):
    """
    Multimodal RAG answering endpoint.
    Handles text, image visual reasoning, PDFs, slides, and audio.
    """
    question = payload.get("question")
    image_path = payload.get("image_path")
    upload_id = payload.get("upload_id")
    top_k = payload.get("top_k", TOP_K)

    if not question or not question.strip():
        raise HTTPException(
            status_code=400,
            detail="No question provided"
        )

    try:
        result = answer_question(
            question=question.strip(),
            image_path=image_path,
            upload_id=upload_id,
            top_k=top_k
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )

    return {
        "message": "Answer generated",
        "data": {
            "question": result["question"],
            "answer": result["answer"],
            "context_used": result["context_used"],
            "model_used": result.get("model_used", "groq/gpt-oss-20b"),
            "sources": result.get("sources", [])
        }
    }