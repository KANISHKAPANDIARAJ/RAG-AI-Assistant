from pathlib import Path
import mimetypes
import traceback
from google import genai
from google.genai import types
from modules.vlm.client import get_gemini_client
from modules.vlm.groq_client import ask_groq
from backend.config import GEMINI_MODEL

MODEL_NAME = GEMINI_MODEL


def ask_gemini(
    question: str,
    image_path: str = None,
    context: str = None
) -> str:
    """
    Perform visual reasoning on an image/page/slide together with retrieved context.
    Falls back gracefully to Groq text LLM if Gemini is unavailable or rate-limited.
    """
    prompt = f"""
You are an expert multimodal Retrieval-Augmented Generation (RAG) assistant.

You have access to:
1. Retrieved document context from the vector database.
2. An accompanying image / rendered slide / page (if available).

Rules:
- Answer the user's question accurately and concisely.
- Base your answers strictly on the retrieved context and visual evidence.
- Do NOT invent or hallucinate unsupported details.
- If neither the image nor context contains the answer, state that clearly.
- Reference specific sections, pages, slides, or timestamps when available.


Always answer using the retrieved OCR context first.

Use the image only to:
- verify the OCR,
- resolve ambiguities,
- identify diagrams or objects that OCR cannot read.

Never summarize the entire document unless the user explicitly asks for a summary.

If the requested information exists in the OCR context, answer directly.

OCR Context
-----------
{context if context else "No OCR context available."}

Question
--------
{question}

Answer only the user's question.
"""

    try:

        client = get_gemini_client()

        contents = []

        if image_path:

            image_file = Path(image_path)

            if image_file.exists():

                with open(image_file, "rb") as f:

                    image_bytes = f.read()

                mime_type, _ = mimetypes.guess_type(image_path)

                if mime_type is None:
                    mime_type = "image/png"

                contents.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                )

        contents.append(
            "Answer ONLY the user's question using the OCR context whenever possible.\n\n"
            + prompt
        )

        print(f"Image path: {image_path}")
        print(f"Exists: {Path(image_path).exists() if image_path else False}")
        print(f"Contents length: {len(contents)}")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )

        if response.text:
            return response.text

        return "Gemini returned an empty response."

    except Exception:

        print("\n" + "=" * 80)
        traceback.print_exc()
        print("=" * 80 + "\n")

        print("[VLM] Switching to Groq...")

        return ask_groq(
            question=question,
            context=context
        )