import json
from app import app


def test_chat_endpoint(monkeypatch):
    # Patch run_ollama to avoid calling external CLI
    monkeypatch.setattr('app.run_ollama', lambda prompt: 'Test reply')

    client = app.test_client()
    resp = client.post('/api/chat', json={'messages': [{'role': 'user', 'content': 'Hello'}]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('assistant') == 'Test reply'


def test_stream_endpoint(monkeypatch):
    monkeypatch.setattr('app.run_ollama', lambda prompt: 'Streamed answer for testing')
    client = app.test_client()
    resp = client.post('/api/stream', json={'messages': [{'role': 'user', 'content': 'Hi'}]})
    assert resp.status_code == 200
    # read streamed text
    body = resp.get_data(as_text=True)
    assert 'Streamed answer' in body
