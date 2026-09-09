import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.config import UPLOAD_DIR, BASE_DIR
from backend.routes.upload import router as upload_router
from backend.routes.process import router as process_router
from backend.routes.ocr import router as ocr_router
from backend.routes.embed import router as embed_router
from backend.routes.vectordb import router as vectordb_router
from backend.routes.rag import router as rag_router
from backend.routes.vlm import router as vlm_router
from backend.routes.detection import router as detection_router

app = FastAPI(title="Multimodal RAG Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(upload_router, prefix="/api")
app.include_router(process_router, prefix="/api")
app.include_router(ocr_router, prefix="/api")
app.include_router(embed_router, prefix="/api")
app.include_router(vectordb_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(vlm_router, prefix="/api")
app.include_router(detection_router, prefix="/api")

# Static files for uploaded images & previews
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Frontend directory
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Mount frontend assets
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend_static")


@app.get("/")
def serve_frontend():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "Multimodal RAG Assistant backend is running",
        "docs": "/docs"
    }


# Global exception handler to avoid raw Python tracebacks leaking to user
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[UNHANDLED SERVER ERROR] {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing your request."}
    )