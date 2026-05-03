"""
auto_video_creator.py - A1 QUALITY FINAL
- Crystal clear voice with phonetic fixes
- Exact relevant images per scene  
- Real cinematic motion (Ken Burns + parallax)
"""

import os, re, json, time, subprocess, requests, random, shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
Path(OUTPUT_DIR).mkdir(exist_ok=True)


# ══════════════════════════════════════════
# VOICE - Crystal Clear
# ══════════════════════════════════════════

# Words jo TTS galat bolta hai - phonetic fixes
PHONETIC_FIXES = {
    "2011": "do hazaar gyarah",
    "2023": "do hazaar teis",
    "2024": "do hazaar chaubees",
    "2025": "do hazaar pachchees",
    "1983": "unnis so tirasi",
    "1971": "unnis so ikhattar",
    "IPL":  "I P L",
    "ICC":  "I C C",
    "BCCI": "B C C I",
    "T20":  "T bees",
    "ODI":  "O D I",
    "1st":  "pehla",
    "2nd":  "doosra", 
    "3rd":  "teesra",
    "4th":  "chautha",
    "5th":  "paanchva",
    "km":   "kilometer",
    "km/h": "kilometer per ghanta",
    "kmph": "kilometer per ghanta",
    "%":    "pratishat",
    "Rs":   "rupaye",
    "₹":    "rupaye",
    "kg":   "kilogram",
    "no.":  "number",
    "No.":  "number",
    "vs":   "versus",
    "VS":   "versus",
    "ft":   "feet",
}

def fix_pronunciation(text):
    """TTS ke liye text ko phonetically correct banao"""
    for wrong, correct in PHONETIC_FIXES.items():
        text = text.replace(wrong, correct)
    
    # Numbers ko words mein convert karo (basic)
    # 100+ → "sau se zyada"
    text = re.sub(r'\b(\d+)\b', lambda m: convert_number(int(m.group())), text)
    
    return text

def convert_number(n):
    """Common numbers ko Hindi words mein"""
    ones = ["", "ek", "do", "teen", "chaar", "paanch", "chhah", "saat", "aath", "nau"]
    teens = ["das", "gyarah", "barah", "terah", "chaudah", "pandrah", 
             "solah", "satrah", "atharah", "unnis"]
    tens = ["", "", "bees", "tees", "chaalees", "pachaas", 
            "saath", "sattar", "assi", "nabbe"]
    
    if n == 0: return "shunya"
    if n < 10: return ones[n]
    if n < 20: return teens[n-10]
    if n < 100:
        t, o = divmod(n, 10)
        return tens[t] + (" " + ones[o] if o else "")
    if n < 1000:
        h, r = divmod(n, 100)
        return ones[h] + " sau" + (" " + convert_number(r) if r else "")
    if n < 100000:
        t, r = divmod(n, 1000)
        return convert_number(t) + " hazaar" + (" " + convert_number(r) if r else "")
    if n < 10000000:
        l, r = divmod(n, 100000)
        return convert_number(l) + " lakh" + (" " + convert_number(r) if r else "")
    
    return str(n)  # Fallback for very large numbers


def make_voice(text, out_path, fmt="facts"):
    """Crystal clear Hindi voice"""
    
    # Step 1: Pronunciation fix
    fixed_text = fix_pronunciation(text)
    
    # Clean text
    fixed_text = re.sub(r'#\w+', '', fixed_text)
    fixed_text = re.sub(r'[^\w\s.,!?]', '', fixed_text)
    fixed_text = re.sub(r'\s+', ' ', fixed_text).strip()
    
    if not fixed_text:
        return False
    
    # Format ke hisab se voice speed
    rate_map = {
        "facts":          "+8%",
        "story":          "-5%",   # Slower - dramatic
        "roast":          "+15%",  # Faster - energetic
        "countdown":      "+10%",
        "news_breakdown": "+5%",
    }
    rate = rate_map.get(fmt, "+8%")
    
    try:
        import asyncio, edge_tts
        
        async def run():
            c = edge_tts.Communicate(
                fixed_text,
                "hi-IN-SwaraNeural",
                rate=rate,
                volume="+20%"
            )
            await c.save(out_path)
        
        asyncio.run(run())
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 2000:
            print(f"  ✅ Voice: SwaraNeural (rate={rate})")
            return True
    except Exception as e:
        pass
    
    # gTTS fallback with fixed text
    try:
        from gtts import gTTS
        tts = gTTS(text=fixed_text, lang='hi', slow=False)
        tts.save(out_path)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            print("  ✅ Voice: gTTS")
            return True
    except Exception as e:
        print(f"  ❌ Voice: {e}")
    return False


def get_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
            capture_output=True, timeout=10
        )
        return float(r.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 50.0


# ══════════════════════════════════════════
# PEXELS - Topic Exact Images
# ══════════════════════════════════════════

def get_image(query, save_path, attempt=0):
    """Pexels se exact relevant portrait image"""
    if not PEXELS_KEY or PEXELS_KEY == "your_pexels_api_key_here":
        return False

    try:
        q = ' '.join(query.strip().split()[:4])
        
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": q, "per_page": 15, "orientation": "portrait"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        photos = r.json().get("photos", []) if r.status_code == 200 else []

        if not photos:
            # 1 word broader search
            r2 = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": query.split()[0], "per_page": 10},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
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
# SCENES BREAKDOWN
# ══════════════════════════════════════════

def get_scenes(full_script, fmt, duration, pexels_queries=None):
    from gemini_client import generate

    per_scene = max(5, int(duration / 7))

    queries_hint = ""
    if pexels_queries:
        ql = json.dumps(pexels_queries)
        queries_hint = f"\nUse these as visual_query (already topic-specific): {ql}"

    prompt = f"""
Split YouTube Shorts script into timed visual scenes.

Script: {full_script}
Format: {fmt}
Total: {duration:.0f}s
{queries_hint}

RULES:
- 6-8 scenes
- text: Roman Hindi, max 8 words, from script
- visual_query: 2-4 specific English words EXACTLY about scene content
  If script mentions Dhoni → "MS Dhoni cricket"
  If script mentions World Cup 2011 → "cricket world cup 2011"
  If script mentions stadium → "cricket stadium crowd"
  NEVER: subscribe, anchor, logo, studio, meme
- duration: ~{per_scene}s each
- Each visual_query UNIQUE

JSON only:
{{"scenes":[{{"text":"roman hindi","visual_query":"specific english","duration":{per_scene}}}]}}"""

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

    # Fallback
    sents = [s.strip() for s in re.split(r'[.!?]+', full_script) if len(s.strip()) > 5]
    dur = duration / max(len(sents[:7]), 1)
    queries = pexels_queries or ["india"] * 7
    return [
        {"text": s[:50], "visual_query": queries[i % len(queries)], "duration": max(5, dur)}
        for i, s in enumerate(sents[:7])
    ]


# ══════════════════════════════════════════
# CINEMATIC SCENE MAKER
# ══════════════════════════════════════════

THEMES = {
    "facts":          {"bg": "0x050510", "accent": "FFD700"},
    "story":          {"bg": "0x080305", "accent": "FF3333"},
    "roast":          {"bg": "0x030810", "accent": "33FF88"},
    "countdown":      {"bg": "0x100503", "accent": "FF6600"},
    "news_breakdown": {"bg": "0x030810", "accent": "3388FF"},
}

def make_scene(img_path, text, duration, out_path, idx=0, fmt="facts"):
    """Cinematic scene - real motion feel"""
    
    theme = THEMES.get(fmt, THEMES["facts"])
    has_font = os.path.exists(FONT_PATH)

    # Clean text
    clean = re.sub(r'[^\w\s.,!?]', '', text).strip()
    clean = clean.replace("'", "").replace('"', "").replace("\\", "")
    clean = clean.replace(":", " ").replace("%", "pct").replace("\n", " ")
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > 35:
        clean = clean[:32] + "..."

    frames = int(duration * 25)
    accent = theme['accent']

    # Text overlay
    if has_font and clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.73:w=iw:h=ih*0.27:color=black@0.90:t=fill"
            f",drawbox=x=0:y=ih*0.73:w=iw:h=6:color={accent}@1.0:t=fill"
            f",drawtext=fontfile='{FONT}':text='{clean}'"
            f":fontsize=52:fontcolor=white:bordercolor=black:borderw=3"
            f":shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-155"
        )
    elif clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.73:w=iw:h=ih*0.27:color=black@0.90:t=fill"
            f",drawtext=text='{clean}':fontsize=46:fontcolor=white"
            f":bordercolor=black:borderw=3:x=(w-text_w)/2:y=h-155"
        )
    else:
        txt_vf = ""

    if img_path and os.path.exists(img_path):
        # CINEMATIC MOTION - 4 different movements
        motions = [
            # Slow zoom in center
            f"zoompan=z='min(zoom+0.0007,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Slow zoom out
            f"zoompan=z='if(lte(zoom,1.0),1.10,max(1.001,zoom-0.0007))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Pan left to right
            f"zoompan=z='1.08':x='if(lte(on,1),0,min(x+0.5,(iw-iw/zoom)))':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            # Pan top to bottom
            f"zoompan=z='1.08':x='iw/2-(iw/zoom/2)':y='if(lte(on,1),0,min(y+0.4,(ih-ih/zoom)))':d={frames}:s=1080x1920",
        ]
        motion = motions[idx % 4]

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
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '20',
            '-t', str(duration), '-r', '25', '-an',
            '-movflags', '+faststart', out_path
        ]
    else:
        # Themed gradient - animated
        bg = theme['bg']
        
        # Subtle animated background
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
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '20',
            '-t', str(duration), '-an',
            '-movflags', '+faststart', out_path
        ]

    r = subprocess.run(cmd, capture_output=True, timeout=120)
    ok = r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 5000
    if not ok:
        err = r.stderr.decode('utf-8', errors='ignore')[-150:]
        print(f"    ⚠️ FFmpeg: {err}")
    return ok


# ══════════════════════════════════════════
# MERGE
# ══════════════════════════════════════════

def merge_video_audio(scene_files, audio_path, output_path):
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
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '20',
            '-movflags', '+faststart', temp
        ], capture_output=True, timeout=300
    )

    if r1.returncode != 0:
        lf = temp.replace('.mp4', '_list.txt')
        with open(lf, 'w') as f:
            for v in valid:
                f.write(f"file '{os.path.abspath(v).replace(chr(92), '/')}'\n")
        r1b = subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lf,
            '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '20',
            '-movflags', '+faststart', temp
        ], capture_output=True, timeout=300)
        if os.path.exists(lf): os.remove(lf)
        if r1b.returncode != 0:
            return False

    if not os.path.exists(temp):
        return False

    # Audio: clear voice enhancement
    r2 = subprocess.run([
        'ffmpeg', '-y', '-i', temp, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-af', (
            'volume=1.5,'
            'equalizer=f=300:width_type=o:width=2:g=2,'   # Warmth
            'equalizer=f=3000:width_type=o:width=2:g=3,'  # Clarity
            'equalizer=f=8000:width_type=o:width=2:g=2,'  # Presence
            'highpass=f=100,'                              # Remove rumble
            'compand=attacks=0:decays=0.1:points=-90/-90|-70/-70|-20/-15|0/-5'  # Compression
        ),
        '-shortest', '-movflags', '+faststart', output_path
    ], capture_output=True, timeout=120)

    if os.path.exists(temp): os.remove(temp)

    if r2.returncode == 0 and os.path.exists(output_path):
        return os.path.getsize(output_path) > 500000
    return False


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
    print(f"  {len(scenes)} scenes planned")

    # 3. Build scenes
    print("\n🖼️  Building cinematic scenes...")
    has_pexels = bool(PEXELS_KEY and PEXELS_KEY != "your_pexels_api_key_here")
    scene_files = []

    for i, scene in enumerate(scenes):
        query = scene.get("visual_query", "india")
        dur = float(scene.get("duration", max(5, duration / len(scenes))))
        text = scene.get("text", "")

        img_path = f"{work_dir}/img_{i}.jpg"
        scene_path = f"{work_dir}/scene_{i}.mp4"

        has_img = False
        if has_pexels:
            has_img = get_image(query, img_path, attempt=i)

        status = f"📸 {query[:30]}" if has_img else f"🎨 {fmt}"

        if make_scene(img_path if has_img else None, text, dur, scene_path, idx=i, fmt=fmt):
            scene_files.append(scene_path)
            print(f"  ✅ {i+1}: {status}")
            print(f"      Text: {text[:40]}")
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
        "title": "Dhoni 2011 World Cup Last Six Story",
        "format": "story",
        "full_script": "Ye raat thi do April do hazaar gyarah ki... Wankhede stadium mein teenees hazaar log the... India ko chahiye tha World Cup... Dhoni ne khud batting order change kiya... Gabbar Yuvraj se pehle aaye... Aur phir wo moment aaya... Nuwan Kulasekara ki ball... Dhoni ne helicopter shot maara... Ball stadium se bahar gayi... Poora India ek saath chillaya... Aansu aaye aankhon mein... Ye tha cricket history ka sabse bada moment... Comment mein likho tum kahan the us raat!",
        "pexels_queries": [
            "cricket night stadium lights",
            "MS Dhoni batting",
            "cricket world cup trophy",
            "india cricket celebration",
            "cricket helicopter shot",
            "cricket stadium crowd cheering",
            "india team victory"
        ]
    }
    create_auto_video(test, 0)