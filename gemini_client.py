"""
gemini_client.py
Retry logic + fallback models ke saath Gemini client
"""

import time
import os
from dotenv import load_dotenv

load_dotenv()

# Import with fallback
try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except ImportError:
    try:
        import google.generativeai as genai_legacy
        genai = None
        client = None
    except ImportError:
        genai = None
        client = None

# Models priority order - pehla fail ho toh agla try karo
MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
]


def generate(prompt, retries=4, delay=8):
    """
    Retry + fallback ke saath Gemini call karo
    503 aaye toh wait karke dobara try karo
    """
    for model in MODELS:
        for attempt in range(retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if attempt > 0 or model != MODELS[0]:
                    print(f"  ✅ Model: {model} (attempt {attempt+1})")
                return response.text
                
            except Exception as e:
                err = str(e)
                if '503' in err or 'UNAVAILABLE' in err or 'overloaded' in err.lower():
                    wait = delay * (attempt + 1)  # 8s, 16s, 24s, 32s
                    print(f"  ⏳ Gemini busy ({model}), {wait}s baad retry...")
                    time.sleep(wait)
                elif '404' in err or 'not found' in err.lower():
                    # Model nahi mila - agla model try karo
                    print(f"  ⚠️ {model} nahi mila, agla try karo...")
                    break
                elif '429' in err or 'quota' in err.lower():
                    print(f"  ⏳ Rate limit, 30s wait...")
                    time.sleep(30)
                else:
                    print(f"  ❌ Error ({model}): {err[:100]}")
                    break
        
    print("❌ Sabhi models fail ho gaye")
    return None
