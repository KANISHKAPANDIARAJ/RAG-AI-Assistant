import faiss
import json
import os
import threading
from backend.config import INDEX_PATH, METADATA_PATH, VECTOR_STORE_DIR

_store_lock = threading.Lock()


def save_index(index: faiss.IndexFlatL2, metadata: list):
    """
    Save FAISS index and metadata ensuring index.ntotal == len(metadata).
    Uses atomic file replacement to prevent partial writes.
    """
    with _store_lock:
        if index is None or metadata is None:
            raise ValueError("Cannot save None index or metadata.")

        if index.ntotal != len(metadata):
            raise ValueError(
                f"FAISS invariant violated: {index.ntotal} vectors vs {len(metadata)} metadata entries. "
                "Aborting save to prevent corruption."
            )

        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

        # Write metadata atomically
        temp_meta_path = METADATA_PATH + ".tmp"
        with open(temp_meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Write FAISS index atomically
        temp_index_path = INDEX_PATH + ".tmp"
        faiss.write_index(index, temp_index_path)

        # Replace targets
        if os.path.exists(temp_meta_path):
            if os.path.exists(METADATA_PATH):
                os.remove(METADATA_PATH)
            os.rename(temp_meta_path, METADATA_PATH)

        if os.path.exists(temp_index_path):
            if os.path.exists(INDEX_PATH):
                os.remove(INDEX_PATH)
            os.rename(temp_index_path, INDEX_PATH)


def load_index():
    """
    Safely load index and metadata.
    Returns (index, metadata) if valid and synchronized, otherwise (None, []).
    """
    with _store_lock:
        if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
            return None, []

        try:
            index = faiss.read_index(INDEX_PATH)
        except Exception as e:
            print(f"[VECTOR DB ERROR] Failed to read FAISS index: {e}")
            return None, []

        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"[VECTOR DB ERROR] Failed to parse metadata JSON: {e}")
            return None, []

        if not isinstance(metadata, list):
            print(f"[VECTOR DB ERROR] Metadata is not a list: {type(metadata)}")
            return None, []

        if index.ntotal != len(metadata):
            print(
                f"[VECTOR DB ERROR] Invariant mismatch: {index.ntotal} vectors != {len(metadata)} metadata entries."
            )
            return None, []

        return index, metadata


def index_exists() -> bool:
    return os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH)


def reset_index() -> bool:
    """
    Safely reset the FAISS index and metadata.
    """
    with _store_lock:
        try:
            if os.path.exists(INDEX_PATH):
                os.remove(INDEX_PATH)
            if os.path.exists(METADATA_PATH):
                os.remove(METADATA_PATH)
            if os.path.exists(INDEX_PATH + ".tmp"):
                os.remove(INDEX_PATH + ".tmp")
            if os.path.exists(METADATA_PATH + ".tmp"):
                os.remove(METADATA_PATH + ".tmp")
            return True
        except Exception as e:
            print(f"[VECTOR DB ERROR] Failed to reset index: {e}")
            return False