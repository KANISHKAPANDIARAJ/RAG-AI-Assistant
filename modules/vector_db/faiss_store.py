import faiss
import json
import os

INDEX_PATH = "vector_store/index.faiss"
METADATA_PATH = "vector_store/metadata.json"

def save_index(index: faiss.IndexFlatL2, metadata: list):
    os.makedirs("vector_store", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f)

def load_index():
    if not os.path.exists(INDEX_PATH):
        return None, []
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)
    return index, metadata

def index_exists() -> bool:
    return os.path.exists(INDEX_PATH)