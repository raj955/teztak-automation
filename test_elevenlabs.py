"""Debug ElevenLabs API"""
import os, requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("ELEVENLABS_API_KEY", "").strip()
voice_id = "qsz5tTEjPvsiIJZIpM8S"
text = "Namaste, ye ek test hai."

print(f"Key length: {len(key)}")
print(f"Key starts with: {key[:10]}...")

# Test 1: Old API endpoint
print("\nTest 1: v1 endpoint...")
r = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={"xi-api-key": key, "Content-Type": "application/json"},
    json={"text": text, "model_id": "eleven_multilingual_v2"},
    timeout=30
)
print(f"Status: {r.status_code}")
if r.status_code != 200:
    print(f"Error: {r.text[:200]}")
else:
    with open("test_eleven.mp3", "wb") as f:
        f.write(r.content)
    print(f"✅ Success! Size: {len(r.content)} bytes")

# Test 2: Check what model IDs are available
print("\nTest 2: Available models...")
r2 = requests.get(
    "https://api.elevenlabs.io/v1/models",
    headers={"xi-api-key": key},
    timeout=10
)
print(f"Models status: {r2.status_code}")
if r2.status_code == 200:
    models = r2.json()
    for m in models[:3]:
        print(f"  - {m.get('model_id')}: {m.get('name')}")
