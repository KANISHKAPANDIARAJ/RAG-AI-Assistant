# Multimodal RAG Assistant

An end-to-end, production-style **Multimodal Retrieval-Augmented Generation (RAG) Assistant** supporting documents, presentations, images, and audio. Built with **FastAPI**, **FAISS**, **SentenceTransformers**, **Groq (Whisper + GPT-OSS)**, **Gemini 3.6 Flash (VLM)**, and **YOLOv8**.

---

## Key Features

- **Multi-Format Ingestion**:
  - **PDF Documents** (.pdf): Multi-page digital text extraction via PyMuPDF with automatic fallback to high-resolution Tesseract OCR for scanned pages.
  - **PowerPoint Decks** (.pptx, .ppt): Slide-by-slide parsing of titles, body shapes, notes, and OCR on embedded images.
  - **Images** (.png, .jpg, .jpeg, .webp): Image preprocessing, Tesseract OCR text extraction, and YOLOv8 object detection.
  - **Audio Files** (.wav, .mp3, .m4a, etc.): Automatic speech-to-text via Groq Whisper (whisper-large-v3) with timestamp-aware chunking.
  - **Text Files** (.txt, .docx, .md): Clean chunking with sliding window overlap.
- **Robust FAISS Vector Store**:
  - Dense text embeddings via local sentence-transformers/all-MiniLM-L6-v2.
  - Strict synchronization invariant: index.ntotal == len(metadata).
  - Scoped retrieval by upload_id and bounds-checked similarity search.
- **Dual Reasoning Engines**:
  - **Text RAG**: Grounded, anti-hallucination context synthesis powered by Groq (openai/gpt-oss-20b).
  - **Multimodal Visual RAG**: Direct visual understanding and diagram reasoning powered by Gemini VLM (gemini-3.6-flash).
- **Glassmorphic Web Interface**:
  - Interactive knowledge base sidebar with drag-and-drop upload and progress tracking.
  - Live vector store statistics (documents, chunks, vectors, FAISS/metadata sync status).
  - Grounded source citations displaying document name, page, slide, timestamp, and similarity distance.
  - Export chat history as JSON or formatted PDF.

---

## Directory Structure

\\\	ext
D:\multimodel-rag\
├── backend/
│   ├── config.py             # Centralized settings & model configurations
│   ├── main.py               # FastAPI application & static file serving
│   └── routes/               # API endpoints (upload, rag, vlm, vectordb, etc.)
├── frontend/
│   ├── index.html            # Production dark glassmorphic web UI
│   ├── style.css             # Glassmorphism styling and responsive layout
│   └── app.js                # Frontend state management, RAG chat, and uploads
├── modules/
│   ├── ingestion/            # Unified ingestion engine (PDF, PPTX, image, audio, text)
│   ├── vector_db/            # FAISS index and metadata store manager
│   ├── embeddings/           # SentenceTransformer embedding encoder
│   ├── rag/                  # RAG pipeline, prompt builder, and retriever
│   ├── vlm/                  # Gemini VLM and Groq clients
│   ├── ocr/                  # Tesseract OCR engine
│   └── detection/            # YOLOv8 object detection
├── uploads/                  # Ingested documents and media files
├── vector_store/             # FAISS index (index.faiss) & metadata (metadata.json)
├── requirements.txt          # Python dependencies
└── .env                      # API keys and environment variables
\\\

---

## Prerequisites

1. **Python 3.10+** (tested on Python 3.12)
2. **Tesseract OCR**:
   - Windows path: D:\Tesseract-OCR\tesseract.exe (or configured in ackend/config.py)
3. **API Keys** (stored in .env):
   - GROQ_API_KEY: Groq API key (for Whisper and GPT-OSS text LLM)
   - GEMINI_API_KEY: Google Gemini API key (for Gemini 3.6 Flash VLM)
   - HF_API_KEY: Hugging Face token (for SentenceTransformer models)

---

## Installation & Setup

1. **Navigate to the project directory**:
   \\\ash
   cd D:\multimodel-rag
   \\\

2. **Activate the virtual environment**:
   \\\ash
   .\venv\Scripts\Activate.ps1
   \\\

3. **Install dependencies**:
   \\\ash
   pip install -r requirements.txt
   \\\

---

## Running the Application

Start the FastAPI server:
\\\ash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
\\\

Open your browser at:
**http://127.0.0.1:8000**

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Serves the glassmorphic web UI (rontend/index.html). |
| POST | /api/upload | Uploads and automatically ingests any supported document into the vector store. |
| POST | /api/rag/ask | Queries the vector store with RAG grounding using Groq LLM. |
| POST | /api/vlm/query | Multimodal query with context grounding using Gemini 3.6 Flash VLM. |
| GET | /api/vectordb/status | Returns vector store health (document count, chunk count, FAISS/metadata sync). |
| GET | /api/vectordb/documents | Returns the list of indexed documents and their chunk counts. |
| POST | /api/vectordb/reset | Resets and clears the FAISS index and metadata store. |

