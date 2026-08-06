from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

_client = None


def get_gemini_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        _client = genai.Client(api_key=api_key)

    return _client