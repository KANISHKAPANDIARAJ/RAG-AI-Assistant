import os
from modules.vlm.groq_client import transcribe_audio
from modules.embeddings.text_embedding import chunk_text


def ingest_audio(file_path: str, upload_id: str, original_filename: str = None) -> tuple[list[dict], dict]:
    """
    Process audio file:
    1. Transcribe with timestamps using Groq Whisper.
    2. Group segments into timestamp-aware chunks.
    3. Preserve start_time and end_time for context retrieval.
    """
    if original_filename is None:
        original_filename = os.path.basename(file_path)

    result = transcribe_audio(file_path)
    full_transcript = result.get("text", "").strip()
    segments = result.get("segments", [])

    chunks = []
    chunk_counter = 0

    if segments:
        # Group segments into ~30-60 second chunks
        current_text = []
        current_start = None
        current_end = None

        for seg in segments:
            seg_start = round(seg.get("start", 0.0), 2)
            seg_end = round(seg.get("end", 0.0), 2)
            seg_text = seg.get("text", "").strip()

            if not seg_text:
                continue

            if current_start is None:
                current_start = seg_start

            current_text.append(seg_text)
            current_end = seg_end

            # Flush when duration reaches ~45 seconds or text is long enough
            if (current_end - current_start >= 45.0) or (len(" ".join(current_text).split()) >= 150):
                chunk_counter += 1
                chunks.append({
                    "text": " ".join(current_text),
                    "upload_id": upload_id,
                    "source_file": original_filename,
                    "content_type": "audio",
                    "start_time": current_start,
                    "end_time": current_end,
                    "chunk_id": chunk_counter
                })
                current_text = []
                current_start = None
                current_end = None

        if current_text and current_start is not None:
            chunk_counter += 1
            chunks.append({
                "text": " ".join(current_text),
                "upload_id": upload_id,
                "source_file": original_filename,
                "content_type": "audio",
                "start_time": current_start,
                "end_time": current_end,
                "chunk_id": chunk_counter
            })
    else:
        # Fallback if no segments returned
        raw_chunks = chunk_text(full_transcript)
        if not raw_chunks:
            raw_chunks = [full_transcript] if full_transcript else ["Audio recording with no transcribed speech."]

        for chk in raw_chunks:
            chunk_counter += 1
            chunks.append({
                "text": chk,
                "upload_id": upload_id,
                "source_file": original_filename,
                "content_type": "audio",
                "start_time": 0.0,
                "end_time": None,
                "chunk_id": chunk_counter
            })

    total_duration = segments[-1].get("end", 0.0) if segments else None

    doc_meta = {
        "upload_id": upload_id,
        "source_file": original_filename,
        "content_type": "audio",
        "duration_seconds": round(total_duration, 1) if total_duration else None,
        "chunks": len(chunks),
        "status": "indexed"
    }

    return chunks, doc_meta
