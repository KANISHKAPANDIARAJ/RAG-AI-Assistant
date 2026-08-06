# <h1><b>AI-Powered Multimodal Document Intelligence System</b></h1>

<h2><b>Overview</b></h2>

AI-powered Multimodal Retrieval-Augmented Generation (RAG) system designed to understand, retrieve, and answer questions from documents such as PDFs and images. The system combines Optical Character Recognition (OCR), semantic retrieval, vector search, and Large Language Models (LLMs) to provide accurate, context-aware responses from uploaded documents.

The application is built using **FastAPI** for the backend and **Streamlit** for the frontend, enabling users to upload documents, retrieve relevant information, and interact with them through an intelligent conversational interface.

---

<h2><b>Problem Statement</b></h2>

Traditional document search relies on keyword matching and manual navigation, making it difficult to locate relevant information in large or scanned documents. Additionally, image-based documents require OCR before they become searchable.

There is a need for an intelligent document understanding system capable of extracting information from multiple document formats, retrieving semantically relevant content, and generating human-like responses using modern AI models.

---

<h2><b>Solution Approach</b></h2>

The system processes uploaded documents through a structured AI pipeline.

### Document Upload

* PDF Documents
* PNG Images
* JPG/JPEG Images

### Document Processing

* File Validation
* PDF Page Extraction
* Image Loading
* OCR Text Extraction
* Text Cleaning
* Metadata Generation

### Chunking

* Document Segmentation
* Context Preservation
* Token-aware Chunking

### Embedding Generation

* Sentence Transformer Embeddings
* Vector Representation
* Metadata Storage

### Retrieval

* Semantic Similarity Search
* Top-K Retrieval
* Context Ranking

### AI Response Generation

* Prompt Construction
* Context Injection
* LLM-based Answer Generation

### Output

* Context-aware Response
* Retrieved References
* Confidence-based Retrieval
* Conversational Interface

---

<h2><b>System Architecture</b></h2>

```text
                         +----------------------+
                         |      User Browser    |
                         +----------+-----------+
                                    |
                              Upload Document
                                    |
                                    v
                       +-------------------------+
                       |   Streamlit Frontend    |
                       +-----------+-------------+
                                   |
                                   |
                        REST API Request
                                   |
                                   v
                      +---------------------------+
                      |      FastAPI Backend      |
                      +------------+--------------+
                                   |
       ------------------------------------------------------------
       |                 Multimodal RAG Pipeline                  |
       ------------------------------------------------------------
                                   |
                                   v
                    +------------------------------+
                    | File Validation              |
                    | file_handler.py              |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | Document Loader              |
                    |                              |
                    | • PDF Loader                 |
                    | • Image Loader               |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | OCR Extraction               |
                    | ocr_extractor.py             |
                    |                              |
                    | • Text Detection             |
                    | • Image Text Extraction      |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | Text Preprocessing           |
                    | preprocess.py               |
                    |                              |
                    | • Cleaning                  |
                    | • Chunking                  |
                    | • Metadata                  |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | Embedding Generator          |
                    | embedding.py                |
                    |                              |
                    | • Sentence Transformers      |
                    | • Vector Embeddings          |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | Vector Store                |
                    |                              |
                    | • FAISS                     |
                    | • Similarity Search         |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | Retriever                   |
                    | retriever.py               |
                    |                              |
                    | • Top-K Search              |
                    | • Ranking                   |
                    +--------------+---------------+
                                   |
                                   v
                    +------------------------------+
                    | LLM Generator               |
                    | llm.py                     |
                    |                              |
                    | • Prompt Engineering        |
                    | • Context Injection         |
                    | • AI Response               |
                    +--------------+---------------+
                                   |
                                   v
                       JSON Response (FastAPI)
                                   |
                                   v
                    +------------------------------+
                    | Streamlit Chat Interface     |
                    |                              |
                    | • Chat Window               |
                    | • Sources                  |
                    | • Upload Panel             |
                    | • Model Settings           |
                    +------------------------------+
```

---

<h2><b>Tech Stack</b></h2>

### Backend

* Python
* FastAPI
* Uvicorn

### Frontend

* Streamlit

### Artificial Intelligence

* Hugging Face Transformers
* Sentence Transformers
* Retrieval-Augmented Generation (RAG)

### OCR

* PaddleOCR / Tesseract OCR

### Vector Search

* FAISS

### Image Processing

* OpenCV
* Pillow

### Utilities

* NumPy
* Pandas

---

<h2><b>Project Structure</b></h2>

| Folder / File            | Description                                      |
| ------------------------ | ------------------------------------------------ |
| **backend/**             | FastAPI application and REST API endpoints.      |
| **frontend/**            | Streamlit-based user interface.                  |
| **modules/**             | Core AI pipeline modules.                        |
| ├── **file_handler.py**  | Upload validation and file management.           |
| ├── **ocr_extractor.py** | OCR processing for scanned documents and images. |
| ├── **preprocess.py**    | Cleans extracted text and prepares chunks.       |
| ├── **embedding.py**     | Generates semantic embeddings.                   |
| ├── **retriever.py**     | Performs semantic retrieval using vector search. |
| ├── **llm.py**           | Generates AI responses using retrieved context.  |
| **uploads/**             | Stores uploaded documents.                       |
| **outputs/**             | Generated responses and temporary outputs.       |
| **requirements.txt**     | Project dependencies.                            |
| **README.md**            | Project documentation.                           |

---

<h2><b>Features</b></h2>

* Upload PDF and Image documents
* OCR-based text extraction
* Intelligent document chunking
* Semantic vector search
* Retrieval-Augmented Generation (RAG)
* Context-aware AI Question Answering
* Modern conversational interface
* Fast document retrieval
* Multimodal document understanding
* Enterprise-ready architecture

---

<h2><b>API Endpoints</b></h2>

### GET /

Returns the application status.

### POST /api/upload

Uploads a document.

### POST /api/ask

Accepts a user question and returns an AI-generated answer using retrieved document context.

Request

* document
* question

Response

* answer
* retrieved_context
* confidence
* metadata

---

<h2><b>How to Run the Project</b></h2>

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start FastAPI

```bash
uvicorn backend.main:app --reload
```

### 3. Start Streamlit

```bash
streamlit run frontend/app.py
```

---

<h2><b>Output Description</b></h2>

The system provides:

* AI-generated answers
* Retrieved document context
* OCR-extracted text
* Semantic search results
* Conversational chat interface
* Intelligent document understanding

---

<h2><b>Current Limitations</b></h2>

* Retrieval quality depends on embedding accuracy.
* OCR performance depends on image quality.
* Large documents may increase indexing time.
* Currently optimized for PDFs and image documents.

---

<h2><b>Future Improvements</b></h2>

* Multi-document conversational memory
* Hybrid keyword + semantic search
* Agentic RAG workflows
* Table and chart understanding
* Audio and video document support
* Knowledge Graph integration
* Cloud deployment
* Authentication and user management
* Citation highlighting
* Streaming AI responses
