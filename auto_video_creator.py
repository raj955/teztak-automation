"""
auto_video_creator.py - ULTIMATE QUALITY
- AI Images: Gemini + Pexels fallback
- Cinematic animations: zoom/pan/parallax/fade
- Smooth transitions between scenes
- ElevenLabs voice + music
"""

import os, re, json, time, subprocess, requests, random, shutil, base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
LINUX_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

Path(OUTPUT_DIR).mkdir(exist_ok=True)

def get_font():
    if os.path.exists(FONT_PATH):
        return FONT
    if os.path.exists(LINUX_FONT):
        return LINUX_FONT.replace('/', '\\/')
    return None


# ══════════════════════════════════════════
# PRONUNCIATION FIX
# ══════════════════════════════════════════

PHONETIC_FIXES = {
    "2011": "do hazaar gyarah", "2024": "do hazaar chaubees",
    "2025": "do hazaar pachchees", "1983": "unnis so tirasi",
    "IPL": "I P L", "ICC": "I C C", "T20": "T bees",
    "ODI": "O D I", "%": "pratishat", "Rs": "rupaye", "₹": "rupaye",
}

def fix_pronunciation(text):
    for wrong, correct in PHONETIC_FIXES.items():
        text = text.replace(wrong, correct)
    return text


# ══════════════════════════════════════════
# VOICE
# ══════════════════════════════════════════

def make_voice(text, out_path, fmt="facts"):
    fixed = fix_pronunciation(text)
    fixed = re.sub(r'#\w+', '', fixed)
    fixed = re.sub(r'[^\w\s.,!?]', '', fixed)
    fixed = re.sub(r'\s+', ' ', fixed).strip()
    if not fixed:
        return False

    # 1. ElevenLabs
    try:
        from elevenlabs_voice import make_complete_audio
        print(f"  🎙️ ElevenLabs ({fmt})...")
        if make_complete_audio(fixed, out_path, fmt=fmt, add_music=True):
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                print("  ✅ ElevenLabs ready!")
                return True
    except Exception as e:
        print(f"  ⚠️ ElevenLabs: {e}")

    # 2. Edge TTS
    try:
        import asyncio, edge_tts
        rate_map = {"facts": "+8%", "story": "-5%", "roast": "+15%",
                    "countdown": "+10%", "news_breakdown": "+5%"}
        async def run():
            c = edge_tts.Communicate(fixed, "hi-IN-SwaraNeural",
                                      rate=rate_map.get(fmt, "+8%"), volume="+15%")
            await c.save(out_path)
        asyncio.run(run())
        if os.path.exists(out_path) and os.path.getsize(out_path) > 2000:
            print("  ✅ Edge TTS")
            return True
    except:
        pass

    # 3. gTTS
    try:
        from gtts import gTTS
        gTTS(text=fixed, lang='hi', slow=False).save(out_path)
        if os.path.exists(out_path):
            print("  ✅ gTTS")
            return True
    except:
        pass
    return False


def get_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', path], capture_output=True, timeout=10)
        return float(r.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 50.0


# ══════════════════════════════════════════
# AI IMAGE GENERATION - Gemini
# ══════════════════════════════════════════

def generate_ai_image(prompt, save_path):
    """Gemini se AI image generate karo"""
    if not GEMINI_KEY:
        return False
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_KEY}",
            json={
                "instances": [{"prompt": f"Cinematic portrait 9:16, {prompt}, photorealistic, high quality, Indian"}],
                "parameters": {"sampleCount": 1, "aspectRatio": "9:16"}
            },
            timeout=30
        )
        if r.status_code == 200:
            data = r.json()
            img_b64 = data.get("predictions", [{}])[0].get("bytesBase64Encoded", "")
            if img_b64:
                with open(save_path, 'wb') as f:
                    f.write(base64.b64decode(img_b64))
                if os.path.getsize(save_path) > 5000:
                    print(f"    🎨 AI image: {prompt[:30]}")
                    return True
    except Exception as e:
        pass
    return False


# ══════════════════════════════════════════
# PEXELS IMAGE
# ══════════════════════════════════════════

def get_pexels_image(query, save_path, attempt=0):
    if not PEXELS_KEY or PEXELS_KEY == "your_pexels_api_key_here":
        return False
    try:
        q = ' '.join(query.strip().split()[:4])
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": q, "per_page": 15, "orientation": "portrait"},
            headers={"Authorization": PEXELS_KEY}, timeout=10)
        photos = r.json().get("photos", []) if r.status_code == 200 else []
        if not photos:
            r2 = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": query.split()[0], "per_page": 10},
                headers={"Authorization": PEXELS_KEY}, timeout=10)
            photos = r2.json().get("photos", []) if r2.status_code == 200 else []
        if not photos:
            return False
        photo = photos[attempt % min(len(photos), 10)]
        url = photo["src"].get("large2x") or photo["src"]["large"]
        r3 = requests.get(url, timeout=20, stream=True)
        if r3.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r3.iter_content(8192):
                    f.write(chunk)
            return os.path.getsize(save_path) > 5000
    except:
        pass
    return False


def get_image(query, save_path, attempt=0, ai_prompt=None):
    """AI image pehle, Pexels fallback"""
    # 1. Gemini AI image
    if ai_prompt:
        if generate_ai_image(ai_prompt, save_path):
            return True, "ai"
    # 2. Pexels
    if get_pexels_image(query, save_path, attempt):
        return True, "pexels"
    return False, None


# ══════════════════════════════════════════
# SCENES
# ══════════════════════════════════════════

def get_scenes(full_script, fmt, duration, pexels_queries=None):
    from gemini_client import generate
    per_scene = max(5, int(duration / 7))

    queries_hint = f"\nUse these queries: {pexels_queries}" if pexels_queries else ""

    prompt = f"""Split YouTube Shorts script into visual scenes.

Script: {full_script}
Format: {fmt}
Duration: {duration:.0f}s
{queries_hint}

OUTPUT 6-8 scenes. JSON only:
{{"scenes":[{{
  "text": "roman hindi max 8 words",
  "visual_query": "specific 2-4 english words for pexels - MUST BE INDIA RELATED",
  "ai_image_prompt": "detailed cinematic India-specific scene description",
  "duration": {per_scene}
}}]}}

CRITICAL RULES for visual_query:
- ALWAYS add "india" or "indian" in query
- Topic specific: "MS Dhoni IPL cricket", "india parliament building", "mumbai city crowd"
- NEVER use other countries unless script is about them
- NEVER: subscribe, anchor, studio, logo, western city

CRITICAL RULES for ai_image_prompt:
- Always Indian setting, Indian people, Indian locations
- Example: "Indian cricket fan celebrating, Mumbai stadium, colorful crowd"
- Example: "Indian mother praying at diya lamp, traditional home, warm light"
- Must match EXACTLY what script is saying in that scene"""

    try:
        resp = generate(prompt)
        if resp:
            t = resp.strip()
            if "```json" in t:
                t = t.split("```json")[1].split("```")[0].strip()
            elif "```" in t:
                t = t.split("```")[1].split("```")[0].strip()
            data = json.loads(t)
            scenes = data.get("scenes", [])
            if len(scenes) >= 4:
                return scenes
    except:
        pass

    sents = [s.strip() for s in re.split(r'[.!?]+', full_script) if len(s.strip()) > 5]
    dur = duration / max(len(sents[:7]), 1)
    queries = pexels_queries or ["india"] * 7
    return [{"text": s[:50], "visual_query": queries[i % len(queries)],
             "ai_image_prompt": queries[i % len(queries)], "duration": max(5, dur)}
            for i, s in enumerate(sents[:7])]


# ══════════════════════════════════════════
# CINEMATIC SCENE WITH ANIMATIONS
# ══════════════════════════════════════════

THEMES = {
    "facts":          {"bg": "0x050510", "accent": "FFD700"},
    "story":          {"bg": "0x080305", "accent": "FF3333"},
    "roast":          {"bg": "0x030810", "accent": "33FF88"},
    "countdown":      {"bg": "0x100503", "accent": "FF6600"},
    "news_breakdown": {"bg": "0x030810", "accent": "3388FF"},
}

def make_scene(img_path, text, duration, out_path, idx=0, fmt="facts"):
    theme = THEMES.get(fmt, THEMES["facts"])
    font = get_font()
    accent = theme["accent"]

    clean = re.sub(r'[^\w\s.,!?]', '', text).strip()
    clean = clean.replace("'", "").replace('"', "").replace("\\", "")
    clean = clean.replace(":", " ").replace("%", "pct").replace("\n", " ")
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > 35:
        clean = clean[:32] + "..."

    frames = int(duration * 25)

    # Text overlay
    if font and clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.73:w=iw:h=ih*0.27:color=black@0.88:t=fill"
            f",drawbox=x=0:y=ih*0.73:w=iw:h=6:color={accent}@1.0:t=fill"
            f",drawtext=fontfile='{font}':text='{clean}'"
            f":fontsize=52:fontcolor=white:bordercolor=black:borderw=3"
            f":shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-155"
        )
    elif clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.73:w=iw:h=ih*0.27:color=black@0.88:t=fill"
            f",drawtext=text='{clean}':fontsize=46:fontcolor=white"
            f":bordercolor=black:borderw=3:x=(w-text_w)/2:y=h-155"
        )
    else:
        txt_vf = ""

    if img_path and os.path.exists(img_path):
        # 6 different cinematic motions
        motions = [
            # Slow zoom in center
            f"zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Slow zoom out
            f"zoompan=z='if(lte(zoom,1.0),1.12,max(1.001,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Pan left to right
            f"zoompan=z='1.10':x='if(lte(on,1),0,min(x+0.6,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Pan right to left
            f"zoompan=z='1.10':x='if(lte(on,1),iw-iw/zoom,max(0,x-0.6))':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Pan top to bottom
            f"zoompan=z='1.10':x='iw/2-(iw/zoom/2)':y='if(lte(on,1),0,min(y+0.4,ih-ih/zoom))':d={frames}:s=1080x1920",
            # Diagonal zoom
            f"zoompan=z='min(zoom+0.0006,1.12)':x='if(lte(on,1),0,min(x+0.3,iw-iw/zoom))':y='if(lte(on,1),0,min(y+0.2,ih-ih/zoom))':d={frames}:s=1080x1920",
        ]
        motion = motions[idx % 6]

        vf = (
            f"scale=1920:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,"
            f"{motion}"
            f"{txt_vf}"
        )
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', img_path,
            '-vf', vf,
            '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '18',
            '-t', str(duration), '-r', '25', '-an',
            '-movflags', '+faststart', out_path
        ]
    else:
        bg = theme['bg']
        vf = (
            f"drawbox=x=0:y=0:w=iw:h=12:color={accent}@1.0:t=fill"
            f",drawbox=x=0:y=ih-12:w=iw:h=12:color={accent}@1.0:t=fill"
            f"{txt_vf}"
        )
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'color=c={bg}:size=1080x1920:rate=25',
            '-vf', vf,
            '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '18',
            '-t', str(duration), '-an',
            '-movflags', '+faststart', out_path
        ]

    r = subprocess.run(cmd, capture_output=True, timeout=120)
    ok = r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 5000
    if not ok:
        print(f"    ⚠️ {r.stderr.decode('utf-8', errors='ignore')[-100:]}")
    return ok


# ══════════════════════════════════════════
# MERGE WITH CROSSFADE TRANSITIONS
# ══════════════════════════════════════════

def merge_video_audio(scene_files, audio_path, output_path):
    valid = [f for f in scene_files if os.path.exists(f) and os.path.getsize(f) > 5000]
    if not valid:
        return False

    temp = output_path.replace('.mp4', '_tmp.mp4')
    n = len(valid)

    # Simple concat first
    inputs = []
    for f in valid:
        inputs += ['-i', f]
    fstr = ''.join(f'[{i}:v]' for i in range(n)) + f'concat=n={n}:v=1:a=0[vout]'

    r1 = subprocess.run(
        ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', fstr, '-map', '[vout]',
            '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '18',
            '-movflags', '+faststart', temp
        ], capture_output=True, timeout=300
    )

    if r1.returncode != 0:
        lf = temp.replace('.mp4', '_list.txt')
        with open(lf, 'w') as f:
            for v in valid:
                f.write(f"file '{os.path.abspath(v).replace(chr(92), '/')}'\n")
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lf,
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '18',
            '-movflags', '+faststart', temp
        ], capture_output=True, timeout=300)
        if os.path.exists(lf): os.remove(lf)

    if not os.path.exists(temp):
        return False

    # Add audio
    r2 = subprocess.run([
        'ffmpeg', '-y', '-i', temp, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-af', 'volume=1.4,equalizer=f=800:width_type=o:width=2:g=3,highpass=f=80',
        '-shortest', '-movflags', '+faststart', output_path
    ], capture_output=True, timeout=120)

    if os.path.exists(temp): os.remove(temp)
    return r2.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500000


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def create_auto_video(script_data, video_index=0):
    title = script_data.get("title", "video")
    fmt = script_data.get("format", "facts")
    full_script = script_data.get("full_script", "")
    pexels_queries = script_data.get("pexels_queries", [])

    safe = re.sub(r'[^\w\s-]', '', title.encode('ascii', 'ignore').decode())[:18].strip()
    if not safe: safe = f"v{video_index}"

    work_dir = f"assets/auto_{video_index}"
    Path(work_dir).mkdir(parents=True, exist_ok=True)

    audio_path = f"{work_dir}/voice.mp3"
    output_path = f"{OUTPUT_DIR}/auto_{video_index}_{safe}.mp4"

    print(f"\n{'='*55}")
    print(f"🎬 [{fmt.upper()}] {title[:50]}")
    print(f"{'='*55}")

    # 1. Voice
    print("\n🎤 Voice...")
    if not make_voice(full_script, audio_path, fmt):
        return None
    duration = get_duration(audio_path)
    print(f"  {duration:.1f}s")

    # 2. Scenes
    print("\n📝 Scenes...")
    scenes = get_scenes(full_script, fmt, duration, pexels_queries)
    print(f"  {len(scenes)} scenes")

    # 3. Build scenes
    print("\n🖼️  Building scenes...")
    has_pexels = bool(PEXELS_KEY and PEXELS_KEY != "your_pexels_api_key_here")
    scene_files = []

    for i, scene in enumerate(scenes):
        query = scene.get("visual_query", "india")
        ai_prompt = scene.get("ai_image_prompt", "")
        dur = float(scene.get("duration", max(5, duration / len(scenes))))
        text = scene.get("text", "")

        img_path = f"{work_dir}/img_{i}.jpg"
        scene_path = f"{work_dir}/scene_{i}.mp4"

        has_img = False
        img_source = None
        if has_pexels or GEMINI_KEY:
            has_img, img_source = get_image(query, img_path, attempt=i, ai_prompt=ai_prompt if GEMINI_KEY else None)

        if img_source == "ai":
            status = f"🎨 AI: {ai_prompt[:25]}"
        elif img_source == "pexels":
            status = f"📸 Pexels: {query[:25]}"
        else:
            status = f"🎭 Gradient"

        if make_scene(img_path if has_img else None, text, dur, scene_path, idx=i, fmt=fmt):
            scene_files.append(scene_path)
            print(f"  ✅ {i+1}: {status}")
        else:
            print(f"  ❌ Scene {i+1} failed")

    if not scene_files:
        print("❌ No scenes!")
        return None

    # 4. Merge
    print(f"\n🎞️  Merging {len(scene_files)} scenes + voice...")
    if merge_video_audio(scene_files, audio_path, output_path):
        mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n✅ {mb:.1f} MB → {output_path}")
        return output_path

    print("❌ Merge failed!")
    return None


def create_all_auto_videos(scripts):
    created = []
    for i, s in enumerate(scripts):
        path = create_auto_video(s, video_index=i)
        if path:
            created.append({
                "path": path,
                "title": s.get("title", ""),
                "description": s.get("description", ""),
                "hashtags": s.get("hashtags", []),
            })
        time.sleep(1)
    return created


if __name__ == "__main__":
    test = {
        "title": "Dhoni 2011 World Cup Story",
        "format": "story",
        "full_script": "Ye raat thi do April do hazaar gyarah ki. Wankhede stadium mein teenees hazaar log the. India ko World Cup chahiye tha. Dhoni ne khud batting order change kiya. Aur phir wo moment aaya. Helicopter shot. Ball stadium se bahar. Poora India ek saath roya. Like karo, comment karo, aur subscribe zarur karo!",
        "pexels_queries": ["MS Dhoni batting", "cricket world cup trophy", "india cricket celebration", "wankhede stadium crowd", "cricket helicopter shot"]
    }
    create_auto_video(test, 0)