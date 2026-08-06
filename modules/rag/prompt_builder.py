def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context = "\n\n".join([chunk["text"] for chunk in context_chunks])

    prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:"""

    return prompt