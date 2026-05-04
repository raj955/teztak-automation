"""
shayari_creator.py - A1 QUALITY
Famous shayars ki real shayari
Indian cinematic visuals
Crystal clear emotional voice
"""

import os, re, json, time, subprocess, requests, random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
Path(OUTPUT_DIR).mkdir(exist_ok=True)


# ══════════════════════════════════════════
# VOICE - Emotional & Clear
# ══════════════════════════════════════════

def make_shayari_voice(text, out_path, mood="romantic"):
    """A1 Shayari Voice - ElevenLabs first, then fallback"""
    # Clean text
    text = re.sub(r'[^\w\s.,!?\n]', '', text)
    text = re.sub(r' +', ' ', text).strip()
    if not text:
        return False

    # 1. ElevenLabs - PEHLE TRY KARO
    try:
        from elevenlabs_voice import make_complete_audio
        fmt = f"shayari_{mood}" if mood in ["sad", "romantic", "motivational", "emotional"] else "shayari_romantic"
        print(f"  🎙️ ElevenLabs ({mood})...")
        if make_complete_audio(text, out_path, fmt=fmt, mood=mood, add_music=True):
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                print(f"  ✅ ElevenLabs voice ready!")
                return True
    except Exception as e:
        print(f"  ⚠️ ElevenLabs: {e}")

    # 2. Edge TTS fallback
    try:
        import asyncio, edge_tts
        rate_map = {"sad": "-15%", "emotional": "-18%", "romantic": "-12%",
                    "motivational": "-5%", "poetic": "-10%", "philosophical": "-8%"}
        rate = rate_map.get(mood, "-12%")
        async def run():
            c = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate=rate, volume="+10%")
            await c.save(out_path)
        asyncio.run(run())
        if os.path.exists(out_path) and os.path.getsize(out_path) > 2000:
            print(f"  ✅ Voice: Edge TTS")
            return True
    except:
        pass

    # 3. gTTS fallback
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='hi', slow=True)
        tts.save(out_path)
        if os.path.exists(out_path):
            print("  ✅ Voice: gTTS")
            return True
    except Exception as e:
        print(f"  ❌ Voice failed: {e}")
    return False


def get_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
            capture_output=True, timeout=10
        )
        return float(r.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 40.0


# ══════════════════════════════════════════
# PEXELS - Indian Relevant Images
# ══════════════════════════════════════════

def get_image(query, save_path, attempt=0):
    """Indian relevant portrait image"""
    if not PEXELS_KEY or PEXELS_KEY == "your_pexels_api_key_here":
        return False
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 15, "orientation": "portrait"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        photos = r.json().get("photos", []) if r.status_code == 200 else []
        
        if not photos:
            # Broader search
            q2 = ' '.join(query.split()[:2])
            r2 = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q2, "per_page": 10},
                headers={"Authorization": PEXELS_KEY}, timeout=10
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
# CINEMATIC SHAYARI SCENE
# ══════════════════════════════════════════

# Mood-based cinematic color grading
MOOD_SETTINGS = {
    "romantic":           {"tint": "colorbalance=rs=0.08:gs=-0.05:bs=0.12", "accent": "FF69B4", "bg": "0x120008"},
    "emotional":          {"tint": "colorbalance=rs=0.05:gs=-0.02:bs=0.08", "accent": "DDA0DD", "bg": "0x0a0512"},
    "sad":                {"tint": "colorbalance=rs=-0.08:gs=-0.03:bs=0.12", "accent": "6699BB", "bg": "0x030810"},
    "classical_romantic": {"tint": "colorbalance=rs=0.10:gs=0.05:bs=-0.05", "accent": "DAA520", "bg": "0x120a00"},
    "classical_sad":      {"tint": "colorbalance=rs=-0.05:gs=-0.05:bs=0.10", "accent": "8899AA", "bg": "0x050810"},
    "philosophical":      {"tint": "colorbalance=rs=0.05:gs=0.05:bs=-0.08", "accent": "C8A96E", "bg": "0x100a03"},
    "motivational":       {"tint": "colorbalance=rs=0.10:gs=0.08:bs=-0.05", "accent": "FFD700", "bg": "0x0a0800"},
    "poetic":             {"tint": "colorbalance=rs=0.03:gs=0.08:bs=0.05",  "accent": "98D8C8", "bg": "0x030a08"},
    "intense":            {"tint": "colorbalance=rs=0.15:gs=-0.08:bs=-0.08", "accent": "FF4400", "bg": "0x120200"},
    "melancholic":        {"tint": "colorbalance=rs=-0.05:gs=-0.05:bs=0.08", "accent": "7799AA", "bg": "0x030810"},
}

def make_shayari_scene(img_path, line_text, duration, out_path, idx=0, mood="romantic"):
    """Beautiful cinematic shayari scene"""
    
    ms = MOOD_SETTINGS.get(mood, MOOD_SETTINGS["romantic"])
    accent = ms["accent"]
    tint = ms["tint"]
    bg = ms["bg"]
    has_font = os.path.exists(FONT_PATH)

    # Clean text
    clean = re.sub(r'[^\w\s.,!?]', '', line_text).strip()
    clean = clean.replace("'", "").replace('"', "").replace("\\", "")
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > 40:
        clean = clean[:37] + "..."

    frames = int(duration * 25)

    # Elegant text overlay - center of screen for shayari
    if has_font and clean:
        txt_vf = (
            # Dark vignette bottom half
            f",drawbox=x=0:y=ih*0.52:w=iw:h=ih*0.48:color=black@0.72:t=fill"
            # Thin golden/colored line above text
            f",drawbox=x=60:y=ih*0.58:w=iw-120:h=2:color={accent}@0.9:t=fill"
            # Main shayari text
            f",drawtext=fontfile='{FONT}'"
            f":text='{clean}'"
            f":fontsize=44"
            f":fontcolor=white"
            f":bordercolor=black:borderw=2"
            f":shadowcolor=black:shadowx=4:shadowy=4"
            f":x=(w-text_w)/2:y=h*0.63"
            # Thin line below text
            f",drawbox=x=60:y=ih*0.75:w=iw-120:h=1:color={accent}@0.5:t=fill"
        )
    elif clean:
        txt_vf = (
            f",drawbox=x=0:y=ih*0.52:w=iw:h=ih*0.48:color=black@0.72:t=fill"
            f",drawtext=text='{clean}':fontsize=40:fontcolor=white"
            f":bordercolor=black:borderw=2:x=(w-text_w)/2:y=h*0.63"
        )
    else:
        txt_vf = ""

    if img_path and os.path.exists(img_path):
        # Very slow cinematic motion - shayari feel
        motions = [
            f"zoompan=z='min(zoom+0.0003,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            f"zoompan=z='if(lte(zoom,1.0),1.05,max(1.001,zoom-0.0003))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
            f"zoompan=z='1.05':x='iw/2-(iw/zoom/2)':y='if(lte(on,1),ih-ih/zoom,max(0,y-0.2))':d={frames}:s=1080x1920",
            f"zoompan=z='1.05':x='if(lte(on,1),0,min(x+0.2,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920",
        ]
        motion = motions[idx % 4]

        vf = (
            f"scale=1920:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,"
            f"{motion},"
            f"{tint}"  # Mood color grading
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
        # Atmospheric gradient
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
# MERGE WITH REVERB
# ══════════════════════════════════════════

def merge_shayari(scene_files, audio_path, output_path):
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
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart', temp
        ], capture_output=True, timeout=300)
        if os.path.exists(lf): os.remove(lf)

    if not os.path.exists(temp):
        return False

    # Audio: warm emotional - slight reverb for shayari atmosphere
    r2 = subprocess.run([
        'ffmpeg', '-y', '-i', temp, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-af', (
            'volume=1.4,'
            'equalizer=f=200:width_type=o:width=2:g=4,'
            'equalizer=f=2500:width_type=o:width=2:g=2,'
            'highpass=f=80,'
            'aecho=0.8:0.88:60:0.4'   # Subtle reverb - shayari mehfil feel
        ),
        '-shortest', '-movflags', '+faststart', output_path
    ], capture_output=True, timeout=120)

    if os.path.exists(temp): os.remove(temp)
    return r2.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 200000


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def create_shayari_video(shayari_data=None, theme=None, video_index=0):
    """
    Famous shayar ki shayari se beautiful video banao
    shayari_data: database se specific entry
    theme: random theme se lo
    """
    from shayari_database import get_shayari_by_theme, get_random_shayari

    if shayari_data is None:
        if theme:
            results = get_shayari_by_theme(theme)
        else:
            results = get_random_shayari()
        
        if not results:
            print("❌ Shayari nahi mili")
            return None
        shayari_data = results[0]

    shayar = shayari_data.get("shayar", "Unknown")
    theme_name = shayari_data.get("theme", "ishq")
    mood = shayari_data.get("mood", "romantic")
    lines = shayari_data.get("lines", [])
    full_shayari = shayari_data.get("shayari", "")
    queries = shayari_data.get("pexels_queries", ["india nature portrait"])

    work_dir = f"assets/shayari_{video_index}"
    Path(work_dir).mkdir(parents=True, exist_ok=True)

    audio_path = f"{work_dir}/voice.mp3"
    output_path = f"{OUTPUT_DIR}/shayari_{video_index}_{theme_name}.mp4"

    print(f"\n{'='*55}")
    print(f"🌹 {shayar} | {theme_name.upper()} | {mood}")
    print(f"{'='*55}")
    print(f"\n📜 Shayari:\n{full_shayari}\n")

    # CTA full script mein add karo - voice mein bhi bolega
    cta = "Like karo, comment mein batao kaisi lagi, aur subscribe zarur karo!"
    full_shayari_with_cta = full_shayari.strip() + "\n" + cta

    # 1. Voice
    print("🎤 Voice generate ho rahi hai...")
    if not make_shayari_voice(full_shayari_with_cta, audio_path, mood):
        return None
    duration = get_duration(audio_path)
    print(f"  Duration: {duration:.1f}s")

    # 2. Scenes - har line alag scene
    if not lines:
        lines = [l.strip() for l in full_shayari.split('\n') if l.strip()]
    
    # CTA last mein add karo
    lines.append("Like karo, comment mein batao kaisi lagi, aur subscribe zarur karo!")

    scene_dur = duration / max(len(lines), 1)
    has_pexels = bool(PEXELS_KEY and PEXELS_KEY != "your_pexels_api_key_here")

    print(f"\n🖼️  {len(lines)} cinematic scenes ban rahi hain...")
    scene_files = []

    for i, line in enumerate(lines):
        query = queries[i % len(queries)]
        img_path = f"{work_dir}/img_{i}.jpg"
        scene_path = f"{work_dir}/scene_{i}.mp4"

        has_img = False
        if has_pexels:
            has_img = get_image(query, img_path, attempt=i)

        status = f"📸 {query[:30]}" if has_img else f"🎨 {mood} gradient"

        if make_shayari_scene(
            img_path if has_img else None,
            line, scene_dur, scene_path,
            idx=i, mood=mood
        ):
            scene_files.append(scene_path)
            print(f"  ✅ {i+1}: {status}")
            print(f"      \"{line[:45]}\"")
        else:
            print(f"  ❌ Scene {i+1} fail")

    if not scene_files:
        print("❌ Koi scene nahi bana!")
        return None

    # 3. Merge
    print(f"\n🎞️  Merging {len(scene_files)} scenes + voice...")
    if merge_shayari(scene_files, audio_path, output_path):
        mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n✅ Shayari video ready! {mb:.1f} MB")
        print(f"📁 {output_path}")
        
        return {
            "path": output_path,
            "title": f"{shayar} ki shayari - {theme_name}",
            "description": f"{full_shayari[:120]}\n\n#{shayar.replace(' ','')} #shayari #urdu #viral #poetry",
            "hashtags": ["#shayari", "#urdu", "#viral", "#poetry", f"#{theme_name}",
                        "#KumarVishwas", "#RahatIndori", "#Gulzar", "#hindi"]
        }

    print("❌ Merge failed!")
    return None


def create_shayari_batch(themes=None, count=3):
    """Multiple shayari videos banao"""
    from shayari_database import SHAYARI_COLLECTION, get_shayari_by_theme

    # Select shayari entries
    if themes:
        pool = []
        for t in themes:
            pool.extend(get_shayari_by_theme(t))
    else:
        pool = SHAYARI_COLLECTION.copy()

    random.shuffle(pool)
    selected = pool[:count]

    created = []
    for i, shayari_data in enumerate(selected):
        result = create_shayari_video(shayari_data=shayari_data, video_index=i)
        if result:
            created.append(result)
        time.sleep(2)

    print(f"\n🎉 {len(created)}/{count} shayari videos ready!")
    return created


if __name__ == "__main__":
    import sys
    theme = sys.argv[1] if len(sys.argv) > 1 else None
    create_shayari_video(theme=theme, video_index=0)