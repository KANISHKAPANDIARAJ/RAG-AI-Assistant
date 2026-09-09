import os
from dotenv import load_dotenv
from groq import Groq
from backend.config import GROQ_TEXT_MODEL, GROQ_WHISPER_MODEL

load_dotenv()

_client = None


def get_groq_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        _client = Groq(api_key=api_key)
    return _client


def ask_groq(question: str, context: str = "") -> str:
    """
    Generate grounded response using Groq text LLM.
    Uses GROQ_TEXT_MODEL with graceful fallback.
    """
    client = get_groq_client()

    system_prompt = (
        "You are an expert Multimodal Retrieval-Augmented Generation (RAG) assistant. "
        "Your task is to answer the user's question accurately using ONLY the provided retrieved context. "
        "Do NOT invent unsupported facts or extrapolate beyond the context. "
        "If the context does not contain the answer, explicitly state: "
        "'The provided context does not contain information to answer this question.' "
        "Always cite relevant sources (e.g., document name, page, slide, or timestamp) when available."
    )

    user_content = question
    if context:
        user_content = f"Retrieved Context:\n{context}\n\nQuestion:\n{question}"

    models_to_try = [GROQ_TEXT_MODEL, "openai/gpt-oss-20b", "qwen/qwen3.6-27b"]
    last_err = None

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            last_err = e
            print(f"[GROQ] Model {model_name} failed: {e}. Trying next fallback...")

    raise RuntimeError(f"All Groq models failed. Last error: {last_err}")


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio file with timestamps using Groq Whisper.
    Returns verbose_json response containing text and segments with start/end times.
    """
    client = get_groq_client()

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), audio_file.read()),
            model=GROQ_WHISPER_MODEL,
            response_format="verbose_json"
        )

    # Groq returns a Transcription or dict with text and segments
    if hasattr(transcription, "model_dump"):
        return transcription.model_dump()
    elif isinstance(transcription, dict):
        return transcription
    else:
        return {"text": getattr(transcription, "text", str(transcription)), "segments": []}