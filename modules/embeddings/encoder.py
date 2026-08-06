from sentence_transformers import SentenceTransformer
from modules.embeddings.models import EMBEDDING_MODEL

_model = None

def get_encoder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model