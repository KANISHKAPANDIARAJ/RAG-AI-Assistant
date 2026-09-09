// Multimodal RAG Assistant Client Controller
const API_BASE = (window.location.origin.startsWith('http') && window.location.port === '8000') 
    ? window.location.origin 
    : 'http://127.0.0.1:8000';


let promptAttachment = null;
let chatMessages = [
    {
        sender: 'assistant',
        text: 'Welcome to **Multimodal RAG Assistant**! Upload PDFs, PowerPoint presentations, images, audio, or text documents in the Knowledge Base sidebar. Then ask questions to retrieve grounded context with exact page, slide, or timestamp citations.',
        sources: []
    }
];

document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();
    renderChat();
    fetchDocuments();
    refreshVectorStatus();

    // Auto-resizing textarea
    const textarea = document.getElementById('user-input');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 160) + 'px';
    });

    // Setup drag-and-drop on dropzone
    const dropzone = document.getElementById('kb-dropzone');
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            uploadFiles(Array.from(e.dataTransfer.files));
        }
    });
});

// Fetch Knowledge Base Documents
async function fetchDocuments() {
    try {
        const res = await fetch(`${API_BASE}/api/vectordb/documents`);
        if (!res.ok) throw new Error("Failed to fetch documents");
        const data = await res.json();
        renderDocumentsList(data.documents || []);
    } catch (err) {
        console.error("Error fetching documents:", err);
    }
}

function renderDocumentsList(docs) {
    const container = document.getElementById('knowledge-list');
    const countBadge = document.getElementById('kb-count');
    countBadge.innerText = `${docs.length} file${docs.length === 1 ? '' : 's'}`;

    if (!docs || docs.length === 0) {
        container.innerHTML = '<div class="empty-hint">No files indexed yet. Upload documents above to start searching.</div>';
        return;
    }

    container.innerHTML = docs.map(doc => {
        let icon = "file-text";
        let metaDetail = `${doc.chunks} chunks`;

        if (doc.content_type === "pdf") {
            icon = "file";
            metaDetail = `${doc.pages || '?'} pages • ${doc.chunks} chunks`;
        } else if (doc.content_type === "pptx") {
            icon = "presentation";
            metaDetail = `${doc.slides || '?'} slides • ${doc.chunks} chunks`;
        } else if (doc.content_type === "image") {
            icon = "image";
            metaDetail = `Image • ${doc.chunks} chunks`;
        } else if (doc.content_type === "audio") {
            icon = "headphones";
            metaDetail = `${doc.duration_seconds ? doc.duration_seconds + 's' : 'Audio'} • ${doc.chunks} chunks`;
        }

        return `
            <div class="doc-card" title="${doc.source_file}">
                <div class="doc-info">
                    <i data-lucide="${icon}" size="16" style="color: var(--accent-cyan); flex-shrink: 0;"></i>
                    <div style="overflow: hidden;">
                        <div class="doc-name">${escapeHtml(doc.source_file)}</div>
                        <div class="doc-meta-sub">${metaDetail}</div>
                    </div>
                </div>
                <span class="doc-badge">✓ Indexed</span>
            </div>
        `;
    }).join('');
    lucide.createIcons();
}

// Refresh Vector Store Status
async function refreshVectorStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/vectordb/status`);
        if (!res.ok) throw new Error("Failed to fetch vector status");
        const status = await res.json();

        document.getElementById('stat-docs').innerText = status.document_count || 0;
        document.getElementById('stat-chunks').innerText = status.metadata_count || 0;
        document.getElementById('stat-vectors').innerText = status.total_vectors || 0;

        const dotFaiss = document.getElementById('dot-faiss');
        const lblFaiss = document.getElementById('lbl-faiss');
        const dotMeta = document.getElementById('dot-meta');
        const lblMeta = document.getElementById('lbl-meta');

        if (status.synchronized) {
            dotFaiss.className = "sync-dot";
            lblFaiss.innerText = "Ready";
            lblFaiss.style.color = "var(--text-main)";

            dotMeta.className = "sync-dot";
            lblMeta.innerText = "In Sync";
            lblMeta.style.color = "var(--text-main)";
        } else {
            dotFaiss.className = "sync-dot warning";
            lblFaiss.innerText = "Mismatch";
            lblFaiss.style.color = "var(--accent-red)";

            dotMeta.className = "sync-dot warning";
            lblMeta.innerText = "Rebuild Needed";
            lblMeta.style.color = "var(--accent-red)";
        }
    } catch (err) {
        console.error("Vector status error:", err);
    }
}

// File Upload Handler
function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
        uploadFiles(files);
    }
}

async function uploadFiles(files) {
    const progressBox = document.getElementById('upload-progress-box');
    const filenameLbl = document.getElementById('progress-filename');
    const percentLbl = document.getElementById('progress-percent');
    const barFill = document.getElementById('progress-bar-fill');
    const stepText = document.getElementById('progress-step-text');

    progressBox.style.display = 'block';

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        filenameLbl.innerText = file.name;
        percentLbl.innerText = `0%`;
        barFill.style.width = `15%`;
        stepText.innerText = `Uploading and initiating local pipeline...`;

        const formData = new FormData();
        formData.append('file', file);

        try {
            barFill.style.width = `50%`;
            stepText.innerText = `Extracting, OCR/Whisper, and generating local embeddings...`;

            const res = await fetch(`${API_BASE}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Upload failed");
            }

            barFill.style.width = `100%`;
            percentLbl.innerText = `100%`;
            stepText.innerText = `Indexed into FAISS successfully!`;

            // Append status message in chat
            chatMessages.push({
                sender: 'assistant',
                text: `Successfully ingested **${file.name}** into Knowledge Base.\n- Chunks: ${data.data?.chunks || '?'}\n- Status: Indexed into FAISS`,
                sources: []
            });
            renderChat();

        } catch (err) {
            console.error("Upload error:", err);
            stepText.innerText = `Error: ${err.message}`;
            chatMessages.push({
                sender: 'assistant',
                text: `Failed to process **${file.name}**: ${err.message}`,
                sources: []
            });
            renderChat();
        }
    }

    setTimeout(() => {
        progressBox.style.display = 'none';
        barFill.style.width = '0%';
    }, 2000);

    fetchDocuments();
    refreshVectorStatus();
    document.getElementById('kb-file-input').value = '';
}

// Prompt Attachment Handling
function handlePromptFileAttach(event) {
    const file = event.target.files[0];
    if (file) {
        promptAttachment = file;
        renderPromptAttachmentPreview();
    }
}

function renderPromptAttachmentPreview() {
    const container = document.getElementById('attached-preview');
    if (!promptAttachment) {
        container.innerHTML = '';
        return;
    }
    container.innerHTML = `
        <div class="preview-pill">
            <i data-lucide="paperclip" size="12"></i>
            <span>${escapeHtml(promptAttachment.name)}</span>
            <i data-lucide="x" size="12" style="cursor:pointer;" onclick="removePromptAttachment()"></i>
        </div>
    `;
    lucide.createIcons();
}

function removePromptAttachment() {
    promptAttachment = null;
    document.getElementById('prompt-file-input').value = '';
    renderPromptAttachmentPreview();
}

// Chat Flow Management
function renderChat() {
    const container = document.getElementById('chat-flow');
    container.innerHTML = chatMessages.map((m) => {
        const isUser = m.sender === 'user';
        const formattedText = typeof marked !== 'undefined' ? marked.parse(m.text) : escapeHtml(m.text);

        return `
            <div class="msg-row ${m.sender}">
                <div class="avatar">
                    ${isUser ? 'U' : '<i data-lucide="bot" size="18"></i>'}
                </div>
                <div class="msg-content-wrapper">
                    ${m.attachment ? `
                        <div class="chat-attachment">
                            <i data-lucide="paperclip" size="12"></i> ${escapeHtml(m.attachment)}
                        </div>
                    ` : ''}
                    <div class="msg-bubble">${formattedText}</div>
                    
                    ${m.sources && m.sources.length > 0 ? `
                        <div class="rag-citations">
                            <div class="citation-header">
                                <i data-lucide="layers" size="13"></i> Grounded Sources (${m.sources.length})
                            </div>
                            <div class="citation-grid">
                                ${m.sources.map(src => {
                                    let tag = "Chunk " + (src.chunk_id || 1);
                                    if (src.page) tag = `Page ${src.page}`;
                                    else if (src.slide) tag = `Slide ${src.slide}`;
                                    else if (src.start_time !== undefined) tag = `${src.start_time}s - ${src.end_time || '?'}s`;

                                    return `
                                        <div class="citation-card">
                                            <div class="citation-card-header">
                                                <span class="citation-title" title="${escapeHtml(src.source_file)}">${escapeHtml(src.source_file)}</span>
                                                <span class="citation-tag">${tag}</span>
                                            </div>
                                            <div class="citation-snippet">"${escapeHtml(src.text.slice(0, 140))}${src.text.length > 140 ? '...' : ''}"</div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${!isUser ? `
                        <div class="msg-actions">
                            <button class="msg-action-btn" onclick="copyToClipboard('${escapeJsString(m.text)}')" title="Copy Text">
                                <i data-lucide="copy" size="13"></i>
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
    lucide.createIcons();
    container.scrollTop = container.scrollHeight;
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        submitMessage();
    }
}

async function submitMessage() {
    const input = document.getElementById('user-input');
    const question = input.value.trim();
    if (!question && !promptAttachment) return;

    const attachmentName = promptAttachment ? promptAttachment.name : null;

    // Add User Message
    chatMessages.push({
        sender: 'user',
        text: question,
        attachment: attachmentName
    });

    input.value = '';
    input.style.height = '26px';
    const activeAttachment = promptAttachment;
    removePromptAttachment();
    renderChat();

    // Disable button & show spinner state
    const submitBtn = document.getElementById('btn-submit');
    submitBtn.disabled = true;

    try {
        let imagePath = null;

        // If an image was attached directly to the prompt, upload it first
        if (activeAttachment) {
            const formData = new FormData();
            formData.append('file', activeAttachment);
            const uploadRes = await fetch(`${API_BASE}/api/upload`, {
                method: 'POST',
                body: formData
            });
            const uploadData = await uploadRes.json();
            if (uploadRes.ok && uploadData.data?.path) {
                imagePath = uploadData.data.path;
            }
        }

        // Query RAG API
        const payload = {
            question: question,
            image_path: imagePath,
            top_k: 3
        };

        const res = await fetch(`${API_BASE}/api/vlm/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resData = await res.json();
        if (!res.ok) {
            throw new Error(resData.detail || "Server failed to generate answer.");
        }

        const data = resData.data;

        chatMessages.push({
            sender: 'assistant',
            text: data.answer,
            sources: data.sources || []
        });

    } catch (err) {
        console.error("Chat error:", err);
        chatMessages.push({
            sender: 'assistant',
            text: `⚠️ **Error:** ${err.message || 'Could not retrieve answer.'}`,
            sources: []
        });
    } finally {
        submitBtn.disabled = false;
        renderChat();
        refreshVectorStatus();
    }
}

// Reset Vector Store
async function confirmResetStore() {
    if (!confirm("Are you sure you want to reset the vector store? All indexed embeddings will be cleared.")) {
        return;
    }
    try {
        const res = await fetch(`${API_BASE}/api/vectordb/reset`, { method: 'POST' });
        if (!res.ok) throw new Error("Reset failed");
        alert("Vector store reset successfully.");
        fetchDocuments();
        refreshVectorStatus();
    } catch (err) {
        alert("Failed to reset store: " + err.message);
    }
}

// Utilities
function clearCurrentChat() {
    chatMessages = [
        {
            sender: 'assistant',
            text: 'Chat history cleared. What would you like to explore in your documents?',
            sources: []
        }
    ];
    renderChat();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
}

function exportChatJSON() {
    const payload = {
        timestamp: new Date().toISOString(),
        chatMessages: chatMessages
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MultimodalRAG_export_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function exportChatPDF() {
    const element = document.getElementById('chat-flow');
    const opt = {
        margin: 0.5,
        filename: `MultimodalRAG_conversation_${Date.now()}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, backgroundColor: '#07090e' },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(element).save();
    } else {
        window.print();
    }
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeJsString(str) {
    if (!str) return "";
    return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, ' ');
}
