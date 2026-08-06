import faiss
import numpy as np

def search_index(index: faiss.IndexFlatL2, query_embedding: list, top_k: int = 3):
    query = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query, top_k)
    return distances[0].tolist(), indices[0].tolist()