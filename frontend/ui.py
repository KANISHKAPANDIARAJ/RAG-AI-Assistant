import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import streamlit as st
import requests
from backend.config import BACKEND_URL

st.set_page_config(page_title="Multimodal RAG", layout="centered")
st.title("Multimodal RAG")
st.caption("Upload an image or PDF to get started")

for key in ["uploaded_data", "processed_path", "ocr_result", "embed_result",
            "store_result", "rag_result", "answer_result", "detection_result",
            "step", "upload_id"]:
    if key not in st.session_state:
        st.session_state[key] = None

uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None and (
    st.session_state.uploaded_data is None or
    st.session_state.uploaded_data["filename"] != uploaded_file.name
):
    with st.spinner("Uploading..."):
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        )
    if response.status_code == 200:
        st.session_state.uploaded_data = response.json()["data"]
        st.session_state.upload_id = uuid.uuid4().hex[:8]
        for key in ["processed_path", "ocr_result", "embed_result",
                    "store_result", "rag_result", "answer_result", "detection_result"]:
            st.session_state[key] = None
        st.session_state.step = "uploaded"
    else:
        try:
            st.error(response.json()["detail"])
        except Exception:
            st.error(f"Upload error {response.status_code}")

if st.session_state.uploaded_data:
    data = st.session_state.uploaded_data

    if data["type"] == "image":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(data["path"], caption=data["filename"], width='stretch')
        if st.session_state.processed_path:
            with col2:
                st.subheader("Processed")
                st.image(st.session_state.processed_path, caption="Processed", width='stretch')

        st.divider()

        # step 1 — detect objects
        if st.session_state.step == "uploaded":
            if st.button("Detect Objects"):
                with st.spinner("Running YOLO detection..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/detect",
                        json={"path": data["path"]}
                    )
                if res.status_code == 200:
                    st.session_state.detection_result = res.json()["data"]
                    st.session_state.step = "detected"
                    st.rerun()
                else:
                    try:
                        st.error(res.json()["detail"])
                    except Exception:
                        st.error(f"Detection error {res.status_code}")

        # step 2 — show detections
        if st.session_state.step == "detected":
            det = st.session_state.detection_result
            st.success(f"Detected {det['count']} objects")

            if det["count"] > 0:
                st.subheader("Detected Objects")
                st.image(det["annotated_path"], caption="Annotated", width='stretch')
                st.write("Labels found:", ", ".join(det["labels"]))
            else:
                st.info("No objects detected — try with a photo image")

            if st.button("Process Image"):
                with st.spinner("Processing..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/process",
                        json={"path": data["path"]}
                    )
                if res.status_code == 200:
                    st.session_state.processed_path = res.json()["processed_path"]
                    st.session_state.step = "processed"
                    st.rerun()
                else:
                    try:
                        st.error(res.json()["detail"])
                    except Exception:
                        st.error(f"Processing error {res.status_code}")

        # step 3
        if st.session_state.step == "processed":
            st.success("Processing complete")
            if st.button("Extract Text (OCR)"):
                with st.spinner("Running OCR..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/ocr",
                        json={"path": st.session_state.processed_path}
                    )
                if res.status_code == 200:
                    st.session_state.ocr_result = res.json()["data"]
                    st.session_state.step = "ocr_done"
                    st.rerun()
                else:
                    try:
                        st.error(res.json()["detail"])
                    except Exception:
                        st.error(f"OCR error {res.status_code}")

        # step 4
        if st.session_state.step == "ocr_done":
            st.success("OCR complete")
            st.text_area("OCR Output", value=st.session_state.ocr_result["full_text"], height=150)
            st.caption(f"{len(st.session_state.ocr_result['lines'])} lines detected")

            if len(st.session_state.ocr_result['lines']) == 0:
                st.warning("No text found in image — using image description as context")
                if st.button("Continue with object detection context"):
                    det = st.session_state.detection_result
                    if det and det["count"] > 0:
                        fake_text = f"This image contains: {', '.join(det['labels'])}"
                    else:
                        fake_text = "No text or objects detected in this image"
                    st.session_state.embed_result = None
                    st.session_state.step = "embedded"
                    res = requests.post(
                        f"{BACKEND_URL}/api/embed",
                        json={"text": fake_text, "upload_id": st.session_state.upload_id}
                    )
                    if res.status_code == 200:
                        st.session_state.embed_result = res.json()["data"]
                        st.rerun()
            else:
                if st.button("Generate Embeddings"):
                    with st.spinner("Generating embeddings..."):
                        res = requests.post(
                            f"{BACKEND_URL}/api/embed",
                            json={
                                "text": st.session_state.ocr_result["full_text"],
                                "upload_id": st.session_state.upload_id
                            }
                        )
                    if res.status_code == 200:
                        st.session_state.embed_result = res.json()["data"]
                        st.session_state.step = "embedded"
                        st.rerun()
                    else:
                        try:
                            st.error(res.json()["detail"])
                        except Exception:
                            st.error(f"Embedding error {res.status_code}")

        # step 5
        if st.session_state.step == "embedded":
            st.success("Embeddings generated")
            ed = st.session_state.embed_result
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chunks", ed["embeddings_count"])
            with col2:
                st.metric("Dimensions", ed["embedding_dimension"])
            if st.button("Store in FAISS"):
                with st.spinner("Storing..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/vectordb/store",
                        json={
                            "chunks": ed["chunks"],
                            "embeddings": ed["embeddings"],
                            "upload_id": st.session_state.upload_id,
                            "source_file": data["filename"]
                        }
                    )
                if res.status_code == 200:
                    st.session_state.store_result = res.json()["data"]
                    st.session_state.step = "stored"
                    st.rerun()
                else:
                    try:
                        st.error(res.json()["detail"])
                    except Exception:
                        st.error(f"Store error {res.status_code}")

        # step 6
        if st.session_state.step in ["stored", "answered"]:
            st.success("Stored in FAISS")
            st.divider()
            st.subheader("Ask a Question")
            question = st.text_input("Type your question about the image")

            if st.button("Get Answer") and question:
                with st.spinner("Thinking..."):
                    res = requests.post(
                        f"{BACKEND_URL}/api/vlm/ask",
                        json={
                            "question": question,
                            "image_path": data["path"],
                            "upload_id": st.session_state.upload_id
                        }
                    )
                if res.status_code == 200:
                    st.session_state.answer_result = res.json()["data"]
                    st.session_state.step = "answered"
                    st.rerun()
                else:
                    try:
                        st.error(res.json()["detail"])
                    except Exception:
                        st.error(f"Server error {res.status_code} — check FastAPI terminal for details")

        # step 7
        if st.session_state.step == "answered":
            ans = st.session_state.answer_result
            st.divider()
            st.subheader("Answer")
            st.success(ans["answer"])
            st.caption(f"Based on {ans['context_used']} context chunks")

            if st.button("Ask Another Question"):
                st.session_state.answer_result = None
                st.session_state.step = "stored"
                st.rerun()

            if st.button("Start Over"):
                for key in ["uploaded_data", "processed_path", "ocr_result", "embed_result",
                            "store_result", "rag_result", "answer_result", "detection_result",
                            "step", "upload_id"]:
                    st.session_state[key] = None
                st.rerun()
    else:
        st.info(f"PDF uploaded: {data['filename']}")