import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}