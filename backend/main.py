from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.process import router as process_router
from backend.routes.ocr import router as ocr_router
from backend.routes.embed import router as embed_router
from backend.routes.vectordb import router as vectordb_router
from backend.routes.rag import router as rag_router
from backend.routes.vlm import router as vlm_router
from backend.routes.detection import router as detection_router

app = FastAPI(title="Multimodal RAG")

app.include_router(upload_router, prefix="/api")
app.include_router(process_router, prefix="/api")
app.include_router(ocr_router, prefix="/api")
app.include_router(embed_router, prefix="/api")
app.include_router(vectordb_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(vlm_router, prefix="/api")
app.include_router(detection_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Multimodal RAG backend is running"}