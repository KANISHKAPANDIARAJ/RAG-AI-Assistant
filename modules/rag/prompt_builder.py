def build_prompt(question: str, context_chunks: list[dict]) -> str:
    formatted_chunks = []
    for i, chunk in enumerate(context_chunks, 1):
        source_tag = f"[Source {i}: {chunk.get('source_file', 'unknown')}"
        if "page" in chunk and chunk["page"] is not None:
            source_tag += f", Page {chunk['page']}"
        elif "slide" in chunk and chunk["slide"] is not None:
            source_tag += f", Slide {chunk['slide']}"
        elif "start_time" in chunk and chunk["start_time"] is not None:
            source_tag += f", Time {chunk['start_time']}s - {chunk.get('end_time', '?')}s"
        source_tag += "]"

        formatted_chunks.append(f"{source_tag}\n{chunk.get('text', '')}")

    context = "\n\n---\n\n".join(formatted_chunks) if formatted_chunks else "No relevant context found."

    prompt = f"""You are an accurate, grounded Multimodal RAG Assistant.
Use the provided retrieved context below to answer the question.
If the context does not contain the answer, reply that the provided documents do not contain this information.
Cite the relevant source documents, pages, slides, or timestamps when appropriate.

Context:
{context}

Question: {question}

Answer:"""

    return prompt