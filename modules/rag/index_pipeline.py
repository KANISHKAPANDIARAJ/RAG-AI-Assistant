import os
from modules.ingestion.dispatcher import ingest_file


def index_document(file_path: str, original_filename: str = None, upload_id: str = None) -> str:
    """
    Delegate document indexing to the unified ingestion dispatcher.
    Returns upload_id.
    """
    result = ingest_file(file_path, original_filename=original_filename, upload_id=upload_id)
    return result["upload_id"]