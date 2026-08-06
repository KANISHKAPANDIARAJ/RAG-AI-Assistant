from modules.rag.retriever import retrieve
from modules.vlm.gemini import ask_gemini


def answer_question(question: str, image_path: str = None, upload_id: str = None, top_k: int = 3) -> dict:
    """
    Full RAG pipeline: retrieve context, then answer with VLM (which also sees the image).
    
    Args:
        question: User's question
        image_path: Path to image file (optional, but required for vision responses)
        upload_id: Filter retrieval to specific upload (optional)
        top_k: Number of context chunks to retrieve
    
    Returns:
        {
            "answer": str,
            "context_chunks": list[dict],
            "image_used": bool
        }
    """
    
    # Step 1: Retrieve relevant text context from FAISS
    context_chunks = retrieve(question, top_k=top_k, upload_id=upload_id)
    print("\n========== RETRIEVED CHUNKS ==========")

    for i, chunk in enumerate(context_chunks, 1):
        print(f"\nChunk {i}")
        print(chunk["text"][:1000])

    print("=====================================\n")
    # Step 2: Build context string from retrieved chunks
    context_text = "\n".join([chunk["text"] for chunk in context_chunks]) if context_chunks else None
    
    # Step 3: Ask VLM with both context and image
    answer = ask_gemini(
        question=question,
        image_path=image_path,
        context=context_text
    )
    
    return {
        "answer": answer,
        "context_chunks": context_chunks,
        "image_used": image_path is not None
    }