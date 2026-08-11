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
