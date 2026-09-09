import os
from modules.rag.retriever import retrieve
from modules.rag.prompt_builder import build_prompt
from modules.vlm.gemini import ask_gemini
from modules.vlm.groq_client import ask_groq


def is_visual_question(question: str) -> bool:
    """
    Determine if a question specifically asks about visual elements.
    """
    visual_keywords = {
        "image", "picture", "photo", "diagram", "chart", "graph", "plot",
        "figure", "draw", "visual", "look like", "color", "appearance",
        "layout", "shape", "logo", "icon", "flowchart", "architecture diagram"
    }
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in visual_keywords)


def answer_question(
    question: str,
    image_path: str = None,
    upload_id: str = None,
    top_k: int = 3,
    force_vlm: bool = False
) -> dict:
    """
    Deterministic Multimodal RAG Pipeline:
    - Normal text/doc/audio question -> FAISS -> Groq text LLM
    - Visual reasoning question (or explicit image) -> FAISS + image -> Gemini VLM (fallback to Groq)
    """
    context_chunks = retrieve(question, top_k=top_k, upload_id=upload_id)

    # Determine if visual reasoning is required
    requires_visual = force_vlm or (image_path is not None and os.path.exists(image_path) and is_visual_question(question))

    # If an image_path was passed but not explicitly asking for visual reasoning, check if retrieved chunks are from an image
    if not requires_visual and image_path and os.path.exists(image_path):
        if is_visual_question(question):
            requires_visual = True

    model_used = "groq/gpt-oss-20b"

    if requires_visual and image_path and os.path.exists(image_path):
        # Format context for Gemini VLM
        context_text = "\n\n".join([f"[{c.get('source_file')}] {c.get('text')}" for c in context_chunks])
        try:
            answer = ask_gemini(
                question=question,
                image_path=image_path,
                context=context_text
            )
            model_used = "gemini-3.6-flash"
        except Exception as e:
            print(f"[RAG] Gemini VLM failed ({e}), falling back to Groq text LLM...")
            prompt = build_prompt(question, context_chunks)
            answer = ask_groq(question=prompt)
            model_used = "groq/gpt-oss-20b (fallback)"
    else:
        # Standard text/audio/document RAG using Groq LLM
        prompt = build_prompt(question, context_chunks)
        try:
            answer = ask_groq(question=prompt)
            model_used = "groq/gpt-oss-20b"
        except Exception as e:
            print(f"[RAG ERROR] Groq text LLM failed: {e}")
            answer = f"Error generating answer: {e}"

    sources = []
    for chunk in context_chunks:
        src = {
            "source_file": chunk.get("source_file", "unknown"),
            "content_type": chunk.get("content_type", "document"),
            "chunk_id": chunk.get("chunk_id", 0),
            "text": chunk.get("text", ""),
            "distance": chunk.get("distance", 0.0),
        }
        if "page" in chunk:
            src["page"] = chunk["page"]
        if "slide" in chunk:
            src["slide"] = chunk["slide"]
        if "start_time" in chunk:
            src["start_time"] = chunk["start_time"]
        if "end_time" in chunk:
            src["end_time"] = chunk["end_time"]
        sources.append(src)

    return {
        "answer": answer,
        "question": question,
        "context_used": len(context_chunks),
        "model_used": model_used,
        "sources": sources
    }