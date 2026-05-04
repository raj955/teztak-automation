"""
elevenlabs_voice.py - FULL INTEGRATION
- Text to Speech (A1 Hindi voice)
- Sound Effects (intro/outro/transitions)
- Background Music (mood based)
- Full fallback chain - system kabhi band nahi hoga
"""

import os, re, requests, json, subprocess
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "").strip()

Path("assets/audio").mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════
# API STATUS CHECK
# ══════════════════════════════════════════

def is_elevenlabs_available():
    """ElevenLabs available hai ya nahi"""
    if not ELEVENLABS_API_KEY:
        return False
    try:
        r = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False


def get_credits():
    """Remaining credits"""
    if not ELEVENLABS_API_KEY:
        return 0
    try:
        r = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10
        )
        if r.status_code == 200:
            sub = r.json().get("subscription", {})
            return sub.get("character_limit", 0) - sub.get("character_count", 0)
    except:
        pass
    return 99999


# ══════════════════════════════════════════
# VOICE SELECTION
# ══════════════════════════════════════════

def get_best_hindi_voice():
    """Best Hindi voice auto-select"""
    saved = ELEVENLABS_VOICE_ID
    if saved:
        return saved

    try:
        r = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=15
        )
        if r.status_code != 200:
            return None

        voices = r.json().get("voices", [])

        # Best natural Hindi voices - priority order
        priority_voices = ["kamal", "devi", "riya", "arjun", "priya", "nisha"]
        
        # First try exact name match
        for priority in priority_voices:
            for v in voices:
                if priority in v.get("name", "").lower():
                    print(f"  ✅ Voice: {v['name']}")
                    return v["voice_id"]
        
        # Then try by language/accent labels
        for v in voices:
            name = v.get("name", "").lower()
            labels = str(v.get("labels", {})).lower()
            if any(x in name + labels for x in ["hindi", "indian"]):
                print(f"  ✅ Voice: {v['name']}")
                return v["voice_id"]

        if voices:
            return voices[0]["voice_id"]
    except:
        pass
    return None


# ══════════════════════════════════════════
# TEXT TO SPEECH
# ══════════════════════════════════════════

FORMAT_SETTINGS = {
    # Natural human feel: stability low=varied, similarity high=consistent, style low=natural
    "facts":              {"stability": 0.45, "style": 0.25, "similarity_boost": 0.95},
    "story":              {"stability": 0.35, "style": 0.08, "similarity_boost": 0.98},  # Most natural
    "roast":              {"stability": 0.40, "style": 0.35, "similarity_boost": 0.92},
    "countdown":          {"stability": 0.42, "style": 0.28, "similarity_boost": 0.95},
    "news_breakdown":     {"stability": 0.50, "style": 0.20, "similarity_boost": 0.95},
    "shayari_sad":        {"stability": 0.30, "style": 0.05, "similarity_boost": 0.98},  # Most emotional
    "shayari_romantic":   {"stability": 0.32, "style": 0.06, "similarity_boost": 0.98},
    "shayari_motivational":{"stability": 0.45, "style": 0.22, "similarity_boost": 0.95},
    "emotional":          {"stability": 0.28, "style": 0.04, "similarity_boost": 0.99},  # Most human
}


def make_elevenlabs_tts(text, output_path, fmt="facts"):
    """ElevenLabs TTS"""
    if not is_elevenlabs_available():
        return False

    voice_id = get_best_hindi_voice()
    if not voice_id:
        return False

    settings = FORMAT_SETTINGS.get(fmt, FORMAT_SETTINGS["facts"])

    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Best for Hindi - natural prosody
                "voice_settings": {
                    "stability": settings["stability"],
                    "similarity_boost": settings["similarity_boost"],
                    "style": settings["style"],
                    "use_speaker_boost": True
                }
            },
            timeout=60
        )

        if r.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            if os.path.getsize(output_path) > 1000:
                print(f"  ✅ ElevenLabs TTS ready!")
                return True
        else:
            print(f"  ⚠️ TTS error {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  ⚠️ TTS exception: {e}")
    return False


# ══════════════════════════════════════════
# SOUND EFFECTS
# ══════════════════════════════════════════

SOUND_EFFECTS = {
    "news_intro":    "Breaking news dramatic intro sound effect",
    "shayari_intro": "Soft harmonium tanpura Indian classical music intro",
    "whoosh":        "Whoosh transition sound effect",
    "suspense":      "Suspense thriller short sting sound effect",
    "applause":      "Crowd applause short",
    "bell":          "Temple bell ding short",
    "heartbeat":     "Heartbeat suspense sound effect",
}


def make_sound_effect(prompt_key, output_path, duration=3.0):
    """ElevenLabs Sound Effect generate karo"""
    if not is_elevenlabs_available():
        return False

    prompt = SOUND_EFFECTS.get(prompt_key, prompt_key)

    try:
        r = requests.post(
            "https://api.elevenlabs.io/v1/sound-generation",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": prompt,
                "duration_seconds": duration,
                "prompt_influence": 0.3
            },
            timeout=30
        )

        if r.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            if os.path.getsize(output_path) > 500:
                print(f"  ✅ Sound effect: {prompt_key}")
                return True
        elif r.status_code == 403:
            print(f"  ⚠️ SFX: Plan mein available nahi, skip")
        else:
            print(f"  ⚠️ SFX error {r.status_code}")
    except Exception as e:
        print(f"  ⚠️ SFX exception: {e}")
    return False


# ══════════════════════════════════════════
# BACKGROUND MUSIC
# ══════════════════════════════════════════

MUSIC_PROMPTS = {
    "facts":          "Upbeat Indian news background music soft instrumental",
    "story":          "Suspense thriller Indian background music low tempo",
    "roast":          "Fun upbeat Indian background music comedy",
    "countdown":      "Exciting countdown background music Indian drums",
    "news_breakdown": "News channel background music Indian professional",
    "shayari_sad":    "Sad ghazal background music soft sitar tabla",
    "shayari_romantic":"Romantic Indian instrumental background music soft",
    "shayari_motivational": "Motivational Indian background music tabla dhol",
    "emotional":      "Emotional Indian background music soft piano sitar",
}


def make_background_music(fmt, output_path, duration=55.0):
    """ElevenLabs Music generate karo"""
    if not is_elevenlabs_available():
        return False

    prompt = MUSIC_PROMPTS.get(fmt, "Soft Indian instrumental background music")

    try:
        r = requests.post(
            "https://api.elevenlabs.io/v1/sound-generation",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": prompt,
                "duration_seconds": min(duration, 22),
                "prompt_influence": 0.3
            },
            timeout=60
        )

        if r.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            if os.path.getsize(output_path) > 1000:
                print(f"  ✅ Background music ready!")
                return True
        elif r.status_code == 403:
            print(f"  ⚠️ Music: Plan mein available nahi, skip kar raha hoon")
        else:
            print(f"  ⚠️ Music error {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  ⚠️ Music exception: {e}")
    return False


# ══════════════════════════════════════════
# AUDIO MIXER - Voice + Music + SFX
# ══════════════════════════════════════════

def mix_audio(voice_path, output_path, music_path=None, sfx_intro_path=None):
    """Audio mix with fallback to simple copy"""
    import shutil
    
    if not os.path.exists(voice_path):
        return False

    # Validate music/sfx files
    valid_music = music_path and os.path.exists(music_path) and os.path.getsize(music_path) > 1000
    valid_sfx = sfx_intro_path and os.path.exists(sfx_intro_path) and os.path.getsize(sfx_intro_path) > 1000

    if not valid_music and not valid_sfx:
        shutil.copy(voice_path, output_path)
        return True

    try:
        inputs = ['-i', voice_path]
        filters = []
        streams = []
        n = 1

        # Voice
        filters.append("[0:a]volume=1.4[v0]")
        streams.append("[v0]")

        # SFX
        if valid_sfx:
            inputs += ['-i', sfx_intro_path]
            filters.append(f"[{n}:a]volume=0.7[sfx]")
            streams.append("[sfx]")
            n += 1

        # Music
        if valid_music:
            inputs += ['-i', music_path]
            filters.append(f"[{n}:a]volume=0.10[music]")
            streams.append("[music]")
            n += 1

        n_streams = len(streams)
        filter_str = ";".join(filters)
        filter_str += f";" + "".join(streams) + f"amix=inputs={n_streams}:duration=first[out]"

        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', filter_str,
            '-map', '[out]',
            '-c:a', 'libmp3lame', '-b:a', '192k', '-q:a', '2',
            output_path
        ]

        r = subprocess.run(cmd, capture_output=True, timeout=120)
        if r.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"  ✅ Mix ready!")
            return True
        else:
            # Debug: show ffmpeg error
            err = r.stderr.decode('utf-8', errors='ignore')[-300:]
            print(f"  ⚠️ Mix error: {err}")
            shutil.copy(voice_path, output_path)
            return True

    except Exception as e:
        print(f"  ⚠️ Mix error: {e}")
        shutil.copy(voice_path, output_path)
        return True


# ══════════════════════════════════════════
# MAIN VOICE FUNCTION WITH FULL FALLBACK
# ══════════════════════════════════════════

def make_voice_with_fallback(text, output_path, fmt="facts", mood=None):
    """
    FULL FALLBACK CHAIN:
    ElevenLabs TTS → Edge TTS → gTTS
    System kabhi band nahi hoga!
    """
    # Clean text
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s.,!?\n।]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return False

    key = mood or fmt

    # 1. ElevenLabs (Best)
    if ELEVENLABS_API_KEY:
        print("  🎙️ ElevenLabs...")
        if make_elevenlabs_tts(text, output_path, fmt=key):
            return True
        print("  ↳ Fallback to Edge TTS...")

    # 2. Edge TTS (Good)
    try:
        import asyncio, edge_tts
        rate_map = {
            "facts": "+8%", "story": "-5%", "roast": "+15%",
            "countdown": "+10%", "news_breakdown": "+5%",
            "shayari_sad": "-15%", "shayari_romantic": "-12%",
            "emotional": "-18%", "shayari_motivational": "-5%",
        }
        rate = rate_map.get(key, "+5%")

        async def run():
            c = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate=rate, volume="+15%")
            await c.save(output_path)

        asyncio.run(run())
        if os.path.exists(output_path) and os.path.getsize(output_path) > 2000:
            print("  ✅ Edge TTS voice ready")
            return True
    except Exception as e:
        print(f"  ↳ Edge TTS failed, trying gTTS...")

    # 3. gTTS (Always works)
    try:
        from gtts import gTTS
        slow = "shayari" in key or fmt == "story"
        tts = gTTS(text=text, lang='hi', slow=slow)
        tts.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print("  ✅ gTTS voice ready")
            return True
    except Exception as e:
        print(f"  ❌ All voice methods failed: {e}")

    return False


def make_complete_audio(text, output_path, fmt="facts", mood=None, add_music=True):
    """
    Complete professional audio:
    Voice + Background Music + Sound Effects
    """
    import tempfile

    key = mood or fmt
    work_dir = os.path.dirname(output_path)
    base = os.path.splitext(output_path)[0]

    voice_path = f"{base}_voice_raw.mp3"
    music_path = f"{base}_music.mp3"
    sfx_path = f"{base}_sfx.mp3"

    # 1. Voice
    if not make_voice_with_fallback(text, voice_path, fmt, mood):
        return False

    # 2 & 3: Music/SFX - try karo but skip gracefully
    has_music = False
    has_sfx = False
    
    if add_music and ELEVENLABS_API_KEY and is_elevenlabs_available():
        try:
            print("  🎵 Background music...")
            voice_dur = _get_audio_duration(voice_path)
            has_music = make_background_music(key, music_path, duration=min(voice_dur + 3, 20))
        except:
            pass
        
        try:
            sfx_key = "news_intro" if "news" in key else "shayari_intro" if "shayari" in key else None
            if sfx_key:
                print(f"  🔊 Sound effect...")
                has_sfx = make_sound_effect(sfx_key, sfx_path, duration=2.0)
        except:
            pass

    # 4. Mix or simple copy
    import shutil
    if has_music or has_sfx:
        print("  🎚️ Mixing...")
        success = mix_audio(
            voice_path, output_path,
            music_path=music_path if has_music else None,
            sfx_intro_path=sfx_path if has_sfx else None
        )
        if not success:
            shutil.copy(voice_path, output_path)
            success = True
    else:
        shutil.copy(voice_path, output_path)
        success = True

    # Cleanup temp files
    for f in [voice_path, music_path, sfx_path]:
        if os.path.exists(f):
            try: os.remove(f)
            except: pass

    return success and os.path.exists(output_path)


def _get_audio_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', path],
            capture_output=True, timeout=10
        )
        return float(r.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 50.0


if __name__ == "__main__":
    print("="*50)
    print("ElevenLabs Full Test")
    print("="*50)

    available = is_elevenlabs_available()
    credits = get_credits()
    print(f"Status: {'✅ Available' if available else '❌ Not available'}")
    print(f"Credits: {credits:,}")

    if available:
        voice_id = get_best_hindi_voice()
        print(f"Voice: {voice_id}")

    # Test complete audio
    print("\nTest: Complete audio with music...")
    text = "Mere ghar mein roshni bankar wohi toh aati hai. Kabhi aankhon mein aansu bankar toh kabhi muskurati hai."
    success = make_complete_audio(text, "test_complete.mp3", fmt="shayari_romantic", add_music=True)
    if success:
        size = os.path.getsize("test_complete.mp3") / 1024
        print(f"✅ Complete audio: {size:.1f} KB")
    else:
        print("❌ Failed")