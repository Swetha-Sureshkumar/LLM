import json
import os
import subprocess
import time
from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context
from werkzeug.utils import secure_filename
from rag_store import rag_store
import uuid

app = Flask(__name__, static_folder='public', static_url_path='')

OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')
PORT = int(os.environ.get('PORT', '3000'))
SYSTEM_PROMPT = os.environ.get(
    'SYSTEM_PROMPT',
    'You are a helpful assistant. Answer clearly and politely, and do not invent facts.',
)


def build_prompt(messages):
    prompt_lines = [SYSTEM_PROMPT.strip(), '']

    for message in messages:
        role = message.get('role', 'user')
        content = str(message.get('content', '')).strip()
        if not content:
            continue

        if role == 'assistant':
            prompt_lines.append(f'Assistant: {content}')
        else:
            prompt_lines.append(f'User: {content}')

    prompt_lines.append('Assistant:')
    return '\n'.join(prompt_lines)


def parse_ollama_output(raw_text):
    raw_text = raw_text.strip()
    if not raw_text:
        return ''

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return raw_text

    if isinstance(payload, dict):
        for key in ('output', 'content', 'response', 'message', 'text', 'greeting'):
            if key in payload:
                return str(payload[key])

        if len(payload) == 1:
            return str(next(iter(payload.values())))

    return json.dumps(payload, ensure_ascii=False, indent=None)


def run_ollama(prompt):
    command = [
        'ollama',
        'run',
        OLLAMA_MODEL,
        '--format',
        'json',
        prompt,
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if completed.returncode != 0:
        error = completed.stderr.strip() or completed.stdout.strip() or 'Unknown Ollama error.'
        raise RuntimeError(error)

    return parse_ollama_output(completed.stdout)


@app.route('/api/chat', methods=['POST'])
def chat():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or 'messages' not in payload:
        return jsonify({'error': "Expected JSON body with a 'messages' list."}), 400

    messages = payload['messages']
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({'error': 'messages must be a non-empty list'}), 400

    prompt = build_prompt(messages)

    try:
        answer = run_ollama(prompt)
        return jsonify({'assistant': answer})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


def stream_answer(prompt):
    try:
        full_answer = run_ollama(prompt)
    except Exception as exc:
        yield f"Error: {str(exc)}\n"
        return

    words = full_answer.split()
    chunk = ''
    for w in words:
        chunk += w + ' '
        if len(chunk) > 50:
            yield chunk
            chunk = ''
            time.sleep(0.02)

    if chunk:
        yield chunk


@app.route('/api/stream', methods=['POST'])
def stream():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or 'messages' not in payload:
        return jsonify({'error': "Expected JSON body with a 'messages' list."}), 400

    messages = payload['messages']
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({'error': 'messages must be a non-empty list'}), 400

    prompt = build_prompt(messages)

    return Response(stream_with_context(stream_answer(prompt)), content_type='text/plain; charset=utf-8')


@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': "Expected a file field named 'file'"}), 400

    f = request.files['file']
    filename = secure_filename(f.filename or 'uploaded.pdf')
    data = f.read()
    doc_id = request.form.get('doc_id') or str(uuid.uuid4())
    try:
        doc_id = rag_store.add_pdf(data, doc_id=doc_id, filename=filename)
        doc = rag_store._docs.get(doc_id, {})
        return jsonify({'doc_id': doc_id, 'chunks': len(doc.get('chunks', []))})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/ask-pdf', methods=['POST'])
def ask_pdf():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or 'doc_id' not in payload or 'question' not in payload:
        return jsonify({'error': "Expected JSON with 'doc_id' and 'question'"}), 400

    doc_id = payload['doc_id']
    question = payload['question']
    top_k = int(payload.get('top_k', 3))

    if doc_id not in rag_store._docs:
        return jsonify({'error': 'doc_id not found'}), 404

    contexts = rag_store.query(doc_id, question, top_k=top_k)
    context_text = '\n\n'.join([c['chunk'] for c in contexts])
    prompt_lines = [SYSTEM_PROMPT.strip(), '', 'Context:', context_text, '', f'Question: {question}', 'Assistant:']
    prompt = '\n'.join(prompt_lines)

    try:
        answer = run_ollama(prompt)
        return jsonify({'assistant': answer, 'sources': contexts})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
