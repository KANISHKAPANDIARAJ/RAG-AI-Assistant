import os
from sentence_transformers import SentenceTransformer
from modules.embeddings.models import EMBEDDING_MODEL

# Ensure HF token is recognized if present in .env
if "HF_TOKEN" not in os.environ and "HF_API_KEY" in os.environ:
    os.environ["HF_TOKEN"] = os.environ["HF_API_KEY"]

_model = None


def get_encoder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    return _model
