from fastapi import APIRouter, UploadFile, File

from modules.file_handler import save_file
from modules.rag.index_pipeline import index_document

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    result = save_file(file)

    upload_id = index_document(result["path"])

    result["upload_id"] = upload_id

    return {
        "message": "File uploaded and indexed successfully",
        "data": result
    }