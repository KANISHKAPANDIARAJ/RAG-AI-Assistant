FROM python:3.12-slim

# Install system dependencies: tesseract, ffmpeg, libgl1 for opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY modules/ ./modules/
COPY frontend/ ./frontend/
COPY yolov8n.pt .

# Create directory for uploads and vector store
RUN mkdir -p uploads vector_store

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV UPLOAD_DIR=uploads
ENV MAX_FILE_SIZE_MB=10

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
