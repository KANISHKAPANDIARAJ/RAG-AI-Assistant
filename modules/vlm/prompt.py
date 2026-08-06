def build_vlm_prompt(question: str, context_chunks: list[dict]) -> str:
    context = "\n\n".join([chunk["text"] for chunk in context_chunks])

    prompt = f"""You are an intelligent document assistant analyzing an image.

Use BOTH:

• the uploaded image
• the OCR extracted text
• the user's question

OCR Text
--------

{context}

Based on both the image and the extracted text, please answer this question:

{question}

Instructions

- Prioritize information visible in the drawing.
- Use OCR text only as supporting information.
- Never invent dimensions or labels.
- If information is not visible, clearly state that.
- Answer in a concise technical style."""

    return prompt