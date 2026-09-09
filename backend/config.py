import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", str(BASE_DIR / "vector_store"))
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.json")

# Limits & Parameters
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 25))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", 100))
MAX_PPT_SLIDES = int(os.getenv("MAX_PPT_SLIDES", 100))
AUDIO_CHUNK_SECONDS = int(os.getenv("AUDIO_CHUNK_SECONDS", 120))
TOP_K = int(os.getenv("TOP_K", 3))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 200))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Supported file extensions by category
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PDF_EXTENSIONS = {".pdf"}
PPT_EXTENSIONS = {".ppt", ".pptx"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".flac"}
TEXT_EXTENSIONS = {".txt", ".docx", ".md"}

ALLOWED_EXTENSIONS = (
    IMAGE_EXTENSIONS
    | PDF_EXTENSIONS
    | PPT_EXTENSIONS
    | AUDIO_EXTENSIONS
    | TEXT_EXTENSIONS
)

# Tesseract
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"D:\Tesseract-OCR\tesseract.exe")

# Models
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-20b")
GROQ_WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384