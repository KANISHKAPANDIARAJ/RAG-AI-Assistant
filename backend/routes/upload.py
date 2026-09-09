from fastapi import APIRouter, UploadFile, File, HTTPException
from modules.file_handler import save_file
from modules.ingestion.dispatcher import ingest_file

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Unified file upload endpoint.
    Automatically saves the file, detects type, processes content,
    generates embeddings, and indexes into FAISS.
    """
    try:
        saved_file = save_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save file: {str(e)}")

    try:
        ingest_summary = ingest_file(
            file_path=saved_file["path"],
            original_filename=saved_file["filename"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing error during ingestion: {str(e)}"
        )

    # Combine file info and indexing summary
    response_data = {
        **saved_file,
        **ingest_summary
    }

    return {
        "message": f"'{saved_file['filename']}' uploaded and indexed successfully",
        "data": response_data
    }