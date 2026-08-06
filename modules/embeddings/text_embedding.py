import numpy as np
from modules.embeddings.encoder import get_encoder

def embed_text(text: str) -> list:
    model = get_encoder()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def embed_chunks(chunks: list[str]) -> list:
    model = get_encoder()
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.tolist()

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks