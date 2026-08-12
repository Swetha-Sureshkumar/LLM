# Ollama Chatbot Project

A clean Python-only chatbot that uses the local Ollama CLI to generate assistant responses.

## Setup

1. Open a terminal in `llm-chatbot-project`.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install Python dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Install Ollama if needed:

   - https://ollama.com/docs/installation

5. Download the model you want to use:

   ```powershell
   ollama pull llama2
   ```

6. Start the Flask app:

   ```powershell
   python app.py
   ```

7. Open the browser at:

   ```text
   http://localhost:3000
   ```

## How it works

- The frontend sends the conversation history to `/api/chat`.
- The Python backend builds a text prompt from the chat history.
- The backend calls `ollama run` directly and returns the assistant text.

## Learning

- Implemented a lightweight Flask frontend/backend chat loop that calls the local Ollama CLI.
- Added a simple streaming endpoint to emulate incremental assistant output and a streaming-capable frontend.
- Wrote tests that mock the model call so CI can run without Ollama installed.

## Architecture

- `app.py`: Flask app exposing two endpoints: `/api/chat` (batch) and `/api/stream` (streaming).
- `public/`: Static frontend files; `public/app.js` connects to `/api/stream` and renders partial assistant output as it arrives.
- `tests/`: `test_app.py` contains basic pytest tests which patch `run_ollama`.

## Tests

Run tests from `llm-chatbot-project`:

```powershell
python -m pip install -r requirements.txt
pytest -q
```

## Screenshots

View the placeholder screenshot at `public/screenshot.svg`.

## Notes on Streaming

The `/api/stream` endpoint provides real-time response streaming for better UX:

- **How it works**: The backend calls `run_ollama` to get the full response, then yields it in chunks (>50 chars) with a 20ms delay between chunks.
- **Frontend**: `public/app.js` reads the stream and appends partial text to the chat in real-time, creating a "typing" effect.
- **Why stream?** Instead of waiting for the full response, users see partial output immediately, making the app feel responsive.
- **Future improvement**: Replace the simulated chunking with a true streaming model client (e.g., Ollama's streaming API) for token-by-token output.


## PDF QA (RAG)

Upload a PDF and ask questions about its content (retrieval-augmented generation using TF‑IDF retrieval).

- Upload endpoint: `POST /api/upload-pdf` (multipart form, field name `file`). Returns `{doc_id, chunks}`.
- Ask endpoint: `POST /api/ask-pdf` with JSON `{ "doc_id": "...", "question": "...", "top_k": 3 }`. Returns `{ assistant, sources }`.

Example upload (PowerShell):

```powershell
curl -X POST -F "file=@C:\path\to\doc.pdf" http://localhost:3000/api/upload-pdf
```

Example ask:

```powershell
curl -X POST -H "Content-Type: application/json" -d '{"doc_id":"<id>","question":"What is the main idea?"}' http://localhost:3000/api/ask-pdf
```

### Testing PDF Upload

1. **Prepare a test PDF**: Use any PDF file (e.g., research paper, documentation, article).
2. **Start the app**: Run `python app.py` and open `http://localhost:3000`.
3. **Upload via web interface**: Use the file upload button to select and upload your PDF.
4. **Take a screenshot**: Capture the upload confirmation showing the document ID and extracted chunks.
5. **Ask questions**: Type questions about the PDF content and verify the relevant chunks are retrieved and answered.
6. **Screenshot results**: Capture the Q&A results showing the answer and source chunks.

### PDF Upload & Q&A Example

When you upload a PDF and ask a question, the interface shows:

```
📄 Document ID: a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6
📋 Chunks extracted: 12

💬 User: What is the main topic of this document?

🤖 Assistant: The document discusses machine learning fundamentals, 
including supervised learning, neural networks, and practical applications 
in natural language processing...

📌 Source chunks:
   - Chunk #2: "Machine learning is a subset of artificial intelligence..."
   - Chunk #5: "Neural networks consist of interconnected layers of nodes..."
   - Chunk #8: "Applications in NLP include text classification, sentiment analysis..."
```

Notes:

- The project uses an in-memory RAG store (`rag_store.py`) backed by TF‑IDF vectors for retrieval. For production, swap in a persistent vector DB and real embeddings.
- Uploads are not persisted across process restarts.



## Configuration

- `OLLAMA_MODEL`: default is `llama2`
- `PORT`: default is `3000`
- `SYSTEM_PROMPT`: default is a helpful assistant prompt

Example:

```powershell
$env:OLLAMA_MODEL = 'llama2'
$env:SYSTEM_PROMPT = 'You are a helpful, honest assistant.'
python app.py
```
