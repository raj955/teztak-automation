"""
osho_creator.py
Osho/Spiritual wisdom videos - Hindi
60-90 second full content
Daily unique - Gemini se fresh content
"""

import os, re, json, time, subprocess, requests, random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
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
# TOPICS
# ══════════════════════════════════════════

WISDOM_TOPICS = [
    # Osho style
    ("osho", "mann ki shanti", "peaceful"),
    ("osho", "prem aur mohabbat", "romantic"),
    ("osho", "dar aur azadi", "intense"),
    ("osho", "khud ko jaano", "philosophical"),
    ("osho", "zindagi ka raaz", "philosophical"),
    ("osho", "sach kya hai", "philosophical"),
    ("osho", "anand aur dukh", "emotional"),
    ("osho", "dhyan meditation", "peaceful"),
    # General spiritual
    ("spiritual", "karma aur bhagya", "philosophical"),
    ("spiritual", "maa ka pyaar", "emotional"),
    ("spiritual", "sapne aur haqeeqat", "philosophical"),
    ("spiritual", "rishte aur bandhan", "emotional"),
    ("spiritual", "safalta ka raaz", "motivational"),
    ("spiritual", "dil ki awaaz", "romantic"),
    ("spiritual", "waqt aur zindagi", "philosophical"),
    ("spiritual", "khushi ka raaz", "peaceful"),
]

VISUAL_QUERIES = {
    "peaceful":      ["india meditation sunrise", "nature peaceful india", "himalaya mountains fog", "india temple morning"],
    "philosophical": ["india night stars sky", "old man wisdom india", "india ancient tree", "india river reflection"],
    "emotional":     ["india candle light dark", "rain window india", "india sunset emotional", "person alone nature india"],
    "motivational":  ["india mountain peak", "sunrise india hope", "young man india determined", "india eagle sky"],
    "romantic":      ["india flowers garden", "sunset india couple", "india rose petals", "moonlight india"],
    "intense":       ["india storm dramatic", "lightning india dark", "india dramatic clouds", "fire india dark"],
}


# ══════════════════════════════════════════
# SCRIPT GENERATOR
# ══════════════════════════════════════════

def generate_wisdom_script(topic_type="osho", topic="mann ki shanti", mood="philosophical"):
    """Gemini se deep wisdom script generate karo"""
    from gemini_client import generate

    style_prompts = {
        "osho": f"""Tu Osho jaisa depth wala spiritual narrator hai.
Osho ki style: direct, provocative, thought-provoking, paradoxical
Topic: {topic}

Osho ke famous style mein script likho:
- Seedha dil pe lagti ho
- Common beliefs ko challenge kare
- Stories ya metaphors use karo
- Log sochne pe majboor ho jaayein
- "Tum pooch rahe ho..." ya "Dekho..." se shuru karo""",

        "spiritual": f"""Tu ek deep spiritual narrator hai.
Topic: {topic}
Style: calm, wise, heart-touching, relatable Hindi"""
    }

    style = style_prompts.get(topic_type, style_prompts["spiritual"])

    prompt = f"""
{style}

60-90 second ka FULL script banao jo:
1. Pehle 5 second mein hi viewer rok le
2. Har line mein depth ho
3. Middle mein ek shocking/beautiful revelation ho
4. End mein dil ko chhu jaaye
5. Like/subscribe naturally feel ho - forcefully nahi

SIRF Roman Hindi (Hinglish) - Devanagari NAHI
Short sentences - max 8 words each
Pauses ke liye "..." use karo
Total 180-220 words

SIRF JSON:
{{
  "title": "catchy Hindi title 60 chars max",
  "script": "poora Roman Hindi script 180-220 words",
  "hook": "pehli line jo scroll rokegi",
  "key_message": "main message ek line mein",
  "scenes": [
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}},
    {{"text": "roman hindi 8 words", "visual": "india specific pexels query", "duration": 10}}
  ],
  "hashtags": ["#osho", "#spiritual", "#hindi", "#viral", "#motivation"]
}}"""

    try:
        resp = generate(prompt)
        if resp:
            t = resp.strip()
            if "```json" in t:
                t = t.split("```json")[1].split("```")[0].strip()
            elif "```" in t:
                t = t.split("```")[1].split("```")[0].strip()
            data = json.loads(t)
            if data.get("script") and data.get("scenes"):
                print(f"  ✅ Script: {data.get('title', '')[:50]}")
                return data
    except Exception as e:
        print(f"  ❌ Script error: {e}")
    return None


# ══════════════════════════════════════════
# VOICE
# ══════════════════════════════════════════

def make_wisdom_voice(text, out_path, mood="philosophical"):
    """Deep calm voice for wisdom content"""
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s.,!?\n।]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return False

    # 1. ElevenLabs - deep slow voice
    try:
        from elevenlabs_voice import make_complete_audio
        fmt = "shayari_sad" if mood in ["philosophical", "peaceful"] else "shayari_motivational"
        print(f"  🎙️ ElevenLabs wisdom voice...")
        if make_complete_audio(text, out_path, fmt=fmt, mood=mood, add_music=True):
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                print("  ✅ ElevenLabs ready!")
                return True
    except Exception as e:
        print(f"  ⚠️ ElevenLabs: {e}")

    # 2. Edge TTS - slow deep
    try:
        import asyncio, edge_tts
        async def run():
            c = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="-10%", volume="+10%")
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
        gTTS(text=text, lang='hi', slow=True).save(out_path)
        return os.path.exists(out_path)
    except:
        return False


def get_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', path], capture_output=True, timeout=10)
        return float(r.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 70.0


# ══════════════════════════════════════════
# IMAGE
# ══════════════════════════════════════════

def get_image(query, save_path, attempt=0):
    if not PEXELS_KEY:
        return False
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 15, "orientation": "portrait"},
            headers={"Authorization": PEXELS_KEY}, timeout=10)
        photos = r.json().get("photos", []) if r.status_code == 200 else []
        if not photos:
            r2 = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": query.split()[0] + " india", "per_page": 10},
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


# ══════════════════════════════════════════
# SCENE MAKER - Spiritual Style
# ══════════════════════════════════════════

def make_wisdom_scene(img_path, text, duration, out_path, idx=0, mood="philosophical"):
    """Cinematic spiritual scene with mood colors"""
    font = get_font()

    # Mood colors - dark, deep, spiritual
    mood_themes = {
        "peaceful":      {"bg": "0x030810", "accent": "88CCFF", "tint": "colorbalance=rs=-0.05:gs=0.02:bs=0.12"},
        "philosophical": {"bg": "0x080605", "accent": "DAA520", "tint": "colorbalance=rs=0.05:gs=0.03:bs=-0.05"},
        "emotional":     {"bg": "0x080305", "accent": "DDA0DD", "tint": "colorbalance=rs=0.08:gs=-0.03:bs=0.08"},
        "motivational":  {"bg": "0x050805", "accent": "FFD700", "tint": "colorbalance=rs=0.05:gs=0.08:bs=-0.05"},
        "romantic":      {"bg": "0x080305", "accent": "FF69B4", "tint": "colorbalance=rs=0.10:gs=-0.05:bs=0.05"},
        "intense":       {"bg": "0x100302", "accent": "FF4400", "tint": "colorbalance=rs=0.15:gs=-0.08:bs=-0.08"},
    }
    theme = mood_themes.get(mood, mood_themes["philosophical"])
    accent = theme["accent"]
    tint = theme["tint"]
    bg = theme["bg"]

    clean = re.sub(r'[^\w\s.,!?]', '', text).strip()
    clean = clean.replace("'", "").replace('"', "").replace("\\", "")
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > 38:
        clean = clean[:35] + "..."

    frames = int(duration * 25)

    # Text overlay - centered, elegant
    if font and clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.55:w=iw:h=ih*0.45:color=black@0.75:t=fill"
            f",drawbox=x=60:y=ih*0.57:w=iw-120:h=3:color={accent}@0.9:t=fill"
            f",drawtext=fontfile='{font}':text='{clean}'"
            f":fontsize=46:fontcolor=white"
            f":bordercolor=black:borderw=2"
            f":shadowcolor=black:shadowx=4:shadowy=4"
            f":x=(w-text_w)/2:y=h*0.63"
            f",drawbox=x=60:y=ih*0.78:w=iw-120:h=1:color={accent}@0.4:t=fill"
        )
    elif clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.55:w=iw:h=ih*0.45:color=black@0.75:t=fill"
            f",drawtext=text='{clean}':fontsize=42:fontcolor=white"
            f":bordercolor=black:borderw=2:x=(w-text_w)/2:y=h*0.63"
        )
    else:
        txt_vf = ""

    if img_path and os.path.exists(img_path):
        # Very slow spiritual motion
        motions = [
            f"zoompan=z='min(zoom+0.0004,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            f"zoompan=z='if(lte(zoom,1.0),1.06,max(1.001,zoom-0.0004))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            f"zoompan=z='1.06':x='iw/2-(iw/zoom/2)':y='if(lte(on,1),ih-ih/zoom,max(0,y-0.2))':d={frames}:s=1080x1920",
            f"zoompan=z='1.06':x='if(lte(on,1),0,min(x+0.2,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            f"zoompan=z='min(zoom+0.0005,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            f"zoompan=z='1.08':x='if(lte(on,1),iw-iw/zoom,max(0,x-0.2))':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
        ]
        motion = motions[idx % 6]

        vf = (
            f"scale=1920:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,"
            f"{motion},"
            f"{tint}"
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
        vf = f"drawbox=x=0:y=0:w=iw:h=ih:color={bg}@1.0:t=fill{txt_vf}"
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
# MERGE
# ══════════════════════════════════════════

def merge_wisdom(scene_files, audio_path, output_path):
    valid = [f for f in scene_files if os.path.exists(f) and os.path.getsize(f) > 5000]
    if not valid:
        return False

    temp = output_path.replace('.mp4', '_tmp.mp4')
    n = len(valid)
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

    r2 = subprocess.run([
        'ffmpeg', '-y', '-i', temp, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-af', 'volume=1.3,equalizer=f=200:width_type=o:width=2:g=3,highpass=f=80,aecho=0.8:0.88:60:0.3',
        '-shortest', '-movflags', '+faststart', output_path
    ], capture_output=True, timeout=120)

    if os.path.exists(temp): os.remove(temp)
    return r2.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500000


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def create_wisdom_video(topic_type=None, topic=None, mood=None, video_index=0):
    """Osho/Spiritual wisdom video banao"""

    # Random topic select
    if not topic_type or not topic:
        t = random.choice(WISDOM_TOPICS)
        topic_type, topic, mood = t

    safe = re.sub(r'[^\w]', '_', topic)[:15]
    work_dir = f"assets/wisdom_{video_index}"
    Path(work_dir).mkdir(parents=True, exist_ok=True)

    audio_path = f"{work_dir}/voice.mp3"
    output_path = f"{OUTPUT_DIR}/wisdom_{video_index}_{safe}.mp4"

    print(f"\n{'='*55}")
    print(f"🙏 WISDOM: {topic_type.upper()} - {topic}")
    print(f"{'='*55}")

    # 1. Script
    print("\n📝 Script generating...")
    data = generate_wisdom_script(topic_type, topic, mood)
    if not data:
        print("❌ Script fail")
        return None

    script = data.get("script", "")
    scenes = data.get("scenes", [])
    title = data.get("title", f"Wisdom - {topic}")
    hashtags = data.get("hashtags", ["#osho", "#spiritual", "#hindi"])

    # CTA add karo
    script += "\nLike karo, comment mein batao kya laga, aur subscribe zarur karo!"

    print(f"\n  📜 {title[:50]}")

    # 2. Voice
    print("\n🎤 Voice...")
    if not make_wisdom_voice(script, audio_path, mood):
        return None
    duration = get_duration(audio_path)
    print(f"  {duration:.1f}s")

    # 3. Scenes
    has_pexels = bool(PEXELS_KEY and PEXELS_KEY != "your_pexels_api_key_here")
    scene_dur = duration / max(len(scenes), 1)
    visuals = VISUAL_QUERIES.get(mood, VISUAL_QUERIES["philosophical"])

    print(f"\n🖼️  {len(scenes)} scenes...")
    scene_files = []

    for i, scene in enumerate(scenes):
        query = scene.get("visual", visuals[i % len(visuals)])
        text = scene.get("text", "")
        dur = float(scene.get("duration", scene_dur))

        img_path = f"{work_dir}/img_{i}.jpg"
        scene_path = f"{work_dir}/scene_{i}.mp4"

        has_img = False
        if has_pexels:
            has_img = get_image(query, img_path, attempt=i)

        if make_wisdom_scene(
            img_path if has_img else None,
            text, dur, scene_path, idx=i, mood=mood
        ):
            scene_files.append(scene_path)
            print(f"  ✅ {i+1}: {query[:25]} | {text[:30]}")
        else:
            print(f"  ❌ Scene {i+1} fail")

    if not scene_files:
        return None

    # 4. Merge
    print(f"\n🎞️  Merging {len(scene_files)} scenes...")
    if merge_wisdom(scene_files, audio_path, output_path):
        mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n✅ Wisdom video ready! {mb:.1f} MB → {output_path}")
        return {
            "path": output_path,
            "title": title,
            "description": f"{data.get('key_message', topic)}\n\n#{topic_type} #spiritual #hindi #viral",
            "hashtags": hashtags
        }

    return None


if __name__ == "__main__":
    import sys
    topic_type = sys.argv[1] if len(sys.argv) > 1 else "osho"
    topic = sys.argv[2] if len(sys.argv) > 2 else "mann ki shanti"
    create_wisdom_video(topic_type=topic_type, topic=topic, video_index=0)
