import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = None


def get_groq_client():
    global _client

    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found")

        _client = Groq(api_key=api_key)

    return _client


def ask_groq(question, context=""):
    client = get_groq_client()

    prompt = question

    if context:
        prompt = f"""
Context:

{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content