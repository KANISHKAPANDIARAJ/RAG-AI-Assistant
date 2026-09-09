# Multimodal RAG Assistant

An end-to-end, production-style **Multimodal Retrieval-Augmented Generation (RAG) Assistant** supporting documents, presentations, images, and audio.  
Built with **FastAPI**, **FAISS**, **SentenceTransformers**, **Groq (Whisper + GPT-OSS)**, **Gemini VLM**, and **YOLOv8**.

---

##  Key Features

###  Multi-Format Ingestion

- **PDF Documents (`.pdf`)**
  - Multi-page digital text extraction using PyMuPDF.
  - Automatic fallback to high-resolution Tesseract OCR for scanned pages.
  - Page-level metadata preservation.
- **PowerPoint Presentations (`.pptx`, `.ppt`)**
  - Slide-by-slide parsing.
  - Extraction of titles, body text, and notes.
  - OCR processing of embedded images.
- **Images (`.png`, `.jpg`, `.jpeg`, `.webp`)**
  - Image preprocessing.
  - Tesseract OCR text extraction.
  - YOLOv8 object detection.
- **Audio Files (`.wav`, `.mp3`, `.m4a`, etc.)**
  - Automatic speech-to-text using Groq Whisper.
  - Timestamp-aware transcription and chunking.
- **Text Files (`.txt`, `.docx`, `.md`)**
  - Text extraction.
  - Sliding-window chunking with overlap.

---

##  RAG & AI Capabilities

### Robust FAISS Vector Store
- Dense text embeddings using:
  `sentence-transformers/all-MiniLM-L6-v2`
- FAISS-based similarity search.
- Metadata synchronization between FAISS and JSON.
- Strict invariant:
  `index.ntotal == len(metadata)`
- Retrieval scoped by `upload_id`.
- Bounds-checked similarity search.

### Dual Reasoning Engines

#### 1. Text RAG
Grounded question answering using:
- **Groq** (`openai/gpt-oss-20b`)
- **FAISS retrieval**
- **SentenceTransformer embeddings**

The system retrieves relevant document chunks and generates answers grounded strictly in the retrieved context.

#### 2. Multimodal Visual RAG
Visual understanding and diagram reasoning using:
- **Gemini VLM** (`gemini-3.6-flash`)
- Image preprocessing
- OCR (Tesseract)
- YOLOv8

This enables the system to reason about visual content such as diagrams, figures, screenshots, and scanned documents.

---

##  Web Interface

The application includes a dark glassmorphic web interface with:
- Drag-and-drop file upload.
- Knowledge Base sidebar.
- Upload progress tracking.
- RAG question-answering interface.
- Vector store statistics.
- FAISS/metadata synchronization status.
- Grounded source citations.
- Page, slide, and timestamp references.
- Chat history export as JSON.
- Chat history export as PDF.

---

##  Directory Structure

```text
multimodel-rag/
│
├── backend/
│   ├── config.py
│   ├── main.py
│   └── routes/
│       ├── process.py
│       ├── rag.py
│       ├── upload.py
│       ├── vectordb.py
│       └── vlm.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── modules/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── dispatcher.py
│   │   ├── pdf_ingester.py
│   │   ├── ppt_ingester.py
│   │   ├── image_ingester.py
│   │   ├── audio_ingester.py
│   │   └── text_ingester.py
│   │
│   ├── vector_db/
│   │   └── faiss_store.py
│   │
│   ├── embeddings/
│   │   ├── encoder.py
│   │   └── text_embedding.py
│   │
│   ├── rag/
│   │   ├── index_pipeline.py
│   │   ├── pipeline.py
│   │   ├── prompt_builder.py
│   │   └── retriever.py
│   │
│   ├── vlm/
│   │   ├── gemini.py
│   │   └── groq_client.py
│   │
│   ├── ocr/
│   │   └── ocr_engine.py
│   │
│   └── detection/
│       └── ...
│
├── uploads/
├── vector_store/
│   ├── index.faiss
│   └── metadata.json
│
├── .dockerignore
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

##  Prerequisites

### Local Development
- Python 3.10+ (Python 3.12 recommended)
- Tesseract OCR
- Git

### Docker Deployment
- Docker Desktop
- Docker Compose

---

##  API Keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
HF_API_KEY=your_huggingface_api_key
```

> **Security Note:** Never commit `.env` to GitHub. Make sure `.gitignore` contains:
> ```
> .env
> venv/
> __pycache__/
> uploads/
> ```

---

##  Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/KANISHKAPANDIARAJ/RAG-AI-Assistant.git
cd RAG-AI-Assistant
```

### 2. Create a Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

##  Running Locally

Start the FastAPI server:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- Open the application: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- FastAPI Swagger documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

##  Running with Docker

Make sure Docker Desktop is running.

Build and start the application:
```bash
docker compose up --build
```

Run in detached mode:
```bash
docker compose up -d --build
```

Check running containers:
```bash
docker compose ps
```

View application logs:
```bash
docker compose logs -f
```

Stop the application:
```bash
docker compose down
```

The application will be available at:
- Web App: [http://localhost:8000](http://localhost:8000)
- Swagger API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web interface |
| `POST` | `/api/upload` | Uploads and ingests supported files |
| `POST` | `/api/rag/ask` | Performs grounded RAG question answering |
| `POST` | `/api/vlm/query` | Performs multimodal visual reasoning |
| `GET` | `/api/vectordb/status` | Returns vector store health and statistics |
| `GET` | `/api/vectordb/documents` | Returns indexed documents and chunk counts |
| `POST` | `/api/vectordb/reset` | Resets the FAISS index and metadata |

---

##  Multimodal Processing Pipeline

```text
┌──────────────────┐
│   User Upload    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ File Dispatcher  │
└────────┬─────────┘
         │
    ┌────┴────────────┬──────────────┐
    │                 │              │
    ▼                 ▼              ▼
   PDF               PPTX          Image
    │                 │              │
    ▼                 ▼              ▼
PyMuPDF/OCR       Text/OCR        OCR/YOLO
    │                 │              │
    └────┬────────────┴──────────────┘
         │
         ▼
┌─────────────────┐
│  Audio / Text   │
│   Processing    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Chunking  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embeddings    │
│(SentenceTrans.) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FAISS Vector   │
│      Store      │
└────────┬────────┘
         │ User Question
         ▼
┌─────────────────┐
│    Retriever    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Groq / Gemini   │
│    Reasoning    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Answer +     │
│    Grounded     │
│    Citations    │
└─────────────────┘
```

---

##  Supported File Types

| File Type | Processing | Output |
|---|---|---|
| **PDF** | PyMuPDF + Tesseract OCR | Text + page metadata |
| **PPT / PPTX** | Slide parsing + OCR | Text + slide metadata |
| **PNG / JPG / JPEG / WEBP** | OCR + YOLOv8 | Text + visual information |
| **WAV / MP3 / M4A** | Groq Whisper | Timestamped transcript |
| **TXT / MD / DOCX** | Text extraction | Chunked text |

---

##  Grounding & Citation

Retrieved information is associated with source metadata such as:

```json
{
  "source": "document.pdf",
  "page": 3,
  "chunk_id": "page_3_chunk_2"
}
```

Depending on the input type, citations can identify:
- Document name
- Page number
- Slide number
- Audio timestamp
- Similarity distance

The system is designed to avoid fabricating source locations.

---

##  Example Questions

After uploading a document, users can ask:
- *What are the main concepts discussed in Unit 1?*
- *Explain the diagram on page 5.*
- *What does the presentation say about human factors?*
- *Summarize the uploaded lecture.*
- *At what timestamp does the speaker discuss machine learning?*

---

##  Technology Stack

| Component | Technology |
|---|---|
| **Backend** | FastAPI |
| **Frontend** | HTML, CSS, JavaScript (Glassmorphic) |
| **Vector Database** | FAISS |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Text LLM** | Groq (`openai/gpt-oss-20b`) |
| **Speech-to-Text** | Groq Whisper (`whisper-large-v3`) |
| **Vision Language Model** | Gemini (`gemini-3.6-flash`) |
| **OCR** | Tesseract OCR |
| **Object Detection** | YOLOv8 |
| **PDF Processing** | PyMuPDF |
| **Presentation Processing** | python-pptx |
| **Database/Metadata** | JSON + FAISS |
| **Containerization** | Docker + Docker Compose |

---

##  Project Status

The application currently supports:
-  PDF ingestion
-  Multi-page PDF processing
-  PowerPoint ingestion
-  Image ingestion
-  Audio transcription
-  Text document ingestion
-  OCR
-  YOLOv8 object detection
-  SentenceTransformer embeddings
-  FAISS vector search
   Groq-based text RAG
-  Gemini-based visual reasoning
-  Source citations
-  Docker deployment
-  FastAPI backend
-  Web-based frontend

---

##  Author

**Kanishka Pandiaraj**  
GitHub: [https://github.com/KANISHKAPANDIARAJ](https://github.com/KANISHKAPANDIARAJ)

---

##  License

This project is intended for educational, research, and demonstration purposes.
```
