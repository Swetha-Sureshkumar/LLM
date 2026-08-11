import json
import os
import subprocess
from flask import Flask, jsonify, request, send_from_directory

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
