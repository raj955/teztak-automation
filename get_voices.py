import requests, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('HEYGEN_API_KEY')
r = requests.get('https://api.heygen.com/v2/voices', headers={'X-Api-Key': key}, timeout=30)
data = r.json()
voices = data.get('data', {}).get('voices', [])
print(f"Total voices: {len(voices)}\n")
for v in voices:
    lang = v.get('language','').lower()
    locale = v.get('locale','').lower()
    name = v.get('name','').lower()
    if 'hindi' in lang or 'hi-in' in locale or 'hindi' in name:
        print(v.get('voice_id'), '|', v.get('name'), '|', v.get('gender',''), '|', locale)
