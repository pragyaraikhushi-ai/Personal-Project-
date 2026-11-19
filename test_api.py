"""API endpoint tests for DocuSpeak backend."""
import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test /health
r = client.get('/health')
assert r.status_code == 200, f"health failed: {r.status_code}"
print("PASS: GET /health =>", r.json())

# Test /voices
r = client.get('/voices')
assert r.status_code == 200
voices = r.json()
assert 'English (US)' in voices
print(f"PASS: GET /voices => {len(voices)} languages")

# Test /parse with plain text
files = {'file': ('hello.txt', b'This is a test document.', 'text/plain')}
r = client.post('/parse', files=files)
assert r.status_code == 200, f"parse failed: {r.text}"
data = r.json()
assert data['text'] == 'This is a test document.'
wc = data['word_count']
print(f"PASS: POST /parse => {wc} words")

# Test /synthesize
r = client.post('/synthesize', data={
    'text': 'Hello world.',
    'voice_id': 'en-US-JennyNeural',
    'rate': '+0%',
    'pitch': '+0Hz',
})
assert r.status_code == 200, f"synthesize failed: {r.text}"
assert len(r.content) > 500
print(f"PASS: POST /synthesize => {len(r.content)} bytes")

# Test /preview
files = {'file': ('hello.txt', b'Preview test document content here.', 'text/plain')}
r = client.post('/preview', data={'chars': '10'}, files=files)
assert r.status_code == 200, f"preview failed: {r.text}"
data = r.json()
print(f"PASS: POST /preview => preview={repr(data['preview'])}")

# Test /convert (full pipeline)
files = {'file': ('sample.txt', b'Convert this text to audio now.', 'text/plain')}
r = client.post('/convert', data={
    'voice_id': 'en-US-GuyNeural',
    'rate': '+10%',
    'pitch': '+0Hz',
}, files=files)
assert r.status_code == 200, f"convert failed: {r.text}"
assert r.headers['content-type'] == 'audio/mpeg'
assert len(r.content) > 500
print(f"PASS: POST /convert => {len(r.content)} bytes MP3")

print()
print("=" * 40)
print("All API endpoint tests PASSED!")
print("=" * 40)
