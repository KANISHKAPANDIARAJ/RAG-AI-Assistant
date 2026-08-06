from fastapi import APIRouter, HTTPException
from modules.rag.retriever import retrieve
from modules.vlm.prompt import build_vlm_prompt
from modules.vlm.gemini import ask_gemini
from modules.vlm.response_parser import parse_response

router = APIRouter()

@router.post("/vlm/ask")
def ask(payload: dict):
    question = payload.get("question")
    image_path = payload.get("image_path")
    print(f"Received image_path: {image_path}")
    upload_id = payload.get("upload_id")

    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    context = retrieve(question, top_k=3, upload_id=upload_id)

    if not context:
        raise HTTPException(
            status_code=404,
            detail="No matching context found in vector store for this upload"
        )

    context_text = "\n\n".join(chunk["text"] for chunk in context)

    raw_answer = ask_gemini(
        question=question,
        image_path=image_path,
        context=context_text
    )
    parsed = parse_response(raw_answer)

    return {
        "message": "Answer generated",
        "data": {
            "question": question,
            "answer": parsed["answer"],
            "context_used": len(context)
        }
    }