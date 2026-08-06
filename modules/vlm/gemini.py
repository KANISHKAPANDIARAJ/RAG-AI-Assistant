from pathlib import Path

from google import genai
from google.genai import types
import mimetypes
import traceback
from modules.vlm.client import get_gemini_client
from modules.vlm.groq_client import ask_groq


MODEL_NAME = "gemini-3.6-flash"


def ask_gemini(
    question: str,
    image_path: str = None,
    context: str = None
) -> str:
    """
    Analyze an image together with retrieved OCR context.

    Falls back to Groq if Gemini fails.
    """

    prompt = f"""
You are a multimodal Retrieval-Augmented Generation (RAG) assistant.

You have two sources of information:

1. OCR text retrieved from the vector database.
2. The uploaded image.

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