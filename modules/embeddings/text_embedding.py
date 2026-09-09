import numpy as np
from modules.embeddings.encoder import get_encoder
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP


def embed_text(text: str) -> list:
    model = get_encoder()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_chunks(chunks: list[str]) -> list:
    if not chunks:
        return []
    model = get_encoder()
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.tolist()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Splits text into overlapping word chunks.
    Ensures no infinite loops and cleans whitespace.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [" ".join(words)]

    step = max(1, chunk_size - overlap)
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += step

    return chunks