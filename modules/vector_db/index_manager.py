import faiss
import numpy as np

def create_index(dimension: int) -> faiss.IndexFlatL2:
    index = faiss.IndexFlatL2(dimension)
    return index

def add_to_index(index: faiss.IndexFlatL2, embeddings: list) -> faiss.IndexFlatL2:
    vectors = np.array(embeddings, dtype=np.float32)
    index.add(vectors)
    return index