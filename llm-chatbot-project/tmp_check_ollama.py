import requests

ENDPOINTS = [
    '/v1/chat/completions',
    '/v1/completions',
    '/v1/models',
    '/health',
]

for path in ENDPOINTS:
    url = 'http://127.0.0.1:11434' + path
    try:
        r = requests.get(url, timeout=10)
        print(path, r.status_code)
        print(r.text[:400])
    except Exception as e:
        print(path, 'ERROR', repr(e))
