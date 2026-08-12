const chatWindow = document.getElementById('chatWindow');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

const messages = [
  { role: 'system', content: 'You are a helpful assistant.' }
];

let lastUploadedDocId = null;

const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const uploadStatus = document.getElementById('uploadStatus');
const pdfQuestionInput = document.getElementById('pdfQuestionInput');
const pdfAskButton = document.getElementById('pdfAskButton');

function appendMessage(role, text, id) {
  let wrapper;
  if (id) {
    wrapper = document.getElementById(id);
    if (!wrapper) {
      wrapper = document.createElement('div');
      wrapper.id = id;
      wrapper.className = `message ${role}`;
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      wrapper.appendChild(bubble);
      chatWindow.appendChild(wrapper);
    }
    wrapper.querySelector('.bubble').textContent = text;
  } else {
    wrapper = document.createElement('div');
    wrapper.className = `message ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    chatWindow.appendChild(wrapper);
  }
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  appendMessage('user', text);
  messages.push({ role: 'user', content: text });
  messageInput.value = '';
  sendButton.disabled = true;

  try {
    const resp = await fetch('/api/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      appendMessage('assistant', `Error: ${err.error || resp.statusText}`);
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let assistantId = `assistant-${Date.now()}`;
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      appendMessage('assistant', buffer, assistantId);
    }

    // finalize
    appendMessage('assistant', buffer, assistantId);
    messages.push({ role: 'assistant', content: buffer });
  } catch (error) {
    appendMessage('assistant', `Request failed: ${error.message}`);
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

async function uploadPdf() {
  if (!fileInput || !fileInput.files || fileInput.files.length === 0) return;
  const file = fileInput.files[0];
  if (!uploadButton || !uploadStatus) return;
  uploadButton.disabled = true;
  uploadStatus.textContent = 'Uploading...';

  try {
    const fd = new FormData();
    fd.append('file', file);
    const resp = await fetch('/api/upload-pdf', { method: 'POST', body: fd });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      uploadStatus.textContent = `Upload error: ${data.error || resp.statusText}`;
      return;
    }
    lastUploadedDocId = data.doc_id;
    uploadStatus.textContent = `Uploaded: ${file.name} (chunks: ${data.chunks})`;
    appendMessage('assistant', `Uploaded PDF. doc_id=${lastUploadedDocId}`);
  } catch (err) {
    uploadStatus.textContent = `Upload failed: ${err.message}`;
  } finally {
    uploadButton.disabled = false;
  }
}

async function askPdf() {
  if (!pdfQuestionInput) return;
  const q = pdfQuestionInput.value.trim();
  if (!q) return;
  if (!lastUploadedDocId) {
    appendMessage('assistant', 'No PDF uploaded yet.');
    return;
  }
  appendMessage('user', q);
  if (pdfAskButton) pdfAskButton.disabled = true;

  try {
    const resp = await fetch('/api/ask-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_id: lastUploadedDocId, question: q }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      appendMessage('assistant', `Error: ${data.error || resp.statusText}`);
      return;
    }
    const answer = data.assistant || 'No answer';
    appendMessage('assistant', answer);
    if (Array.isArray(data.sources)) {
      data.sources.forEach((s) => appendMessage('assistant', `Source (score=${s.score.toFixed(2)}): ${s.chunk}`));
    }
    pdfQuestionInput.value = '';
  } catch (err) {
    appendMessage('assistant', `Request failed: ${err.message}`);
  } finally {
    if (pdfAskButton) pdfAskButton.disabled = false;
  }
}

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendMessage();
  }
});

if (uploadButton) uploadButton.addEventListener('click', uploadPdf);
if (pdfAskButton) pdfAskButton.addEventListener('click', askPdf);
if (pdfQuestionInput) {
  pdfQuestionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      askPdf();
    }
  });
}

messageInput.focus();
