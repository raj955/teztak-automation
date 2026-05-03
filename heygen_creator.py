"""
heygen_creator.py - NEWS ANCHOR FORMAT
Tez Tak channel - Female anchor + News studio + Relevant images
"""

import os
import requests
import json
import time
import subprocess
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_BASE = "https://api.heygen.com"
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# ── Tez Tak Branding Colors ──
STUDIO_BG_COLOR = "#0a0a2e"  # Dark navy - news channel feel
TICKER_COLOR = "#cc0000"     # Red - breaking news


def heygen_headers():
    return {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }


def get_avatars():
    """Avatars fetch karo - retry ke saath"""
    for attempt in range(4):
        try:
            r = requests.get(
                f"{HEYGEN_BASE}/v2/avatars",
                headers=heygen_headers(),
                timeout=30
            )
            data = r.json()
            avatars = data.get("data", {}).get("avatars", [])
            if avatars:
                print(f"✅ {len(avatars)} avatars available")
                return avatars
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt+1}/4: {e}")
            time.sleep(8)
    return []


def select_best_indian_female_avatar(avatars):
    """
    Best Indian female avatar choose karo
    Priority: Indian > Female > Young > Professional
    """
    if not avatars:
        return None, None

    # Search terms priority order
    female_terms = ["indian", "priya", "anjali", "neha", "kavya", "ananya",
                    "female", "woman", "girl", "she", "her"]
    
    # Score each avatar
    scored = []
    for av in avatars:
        name = av.get("avatar_name", "").lower()
        tags = str(av.get("tags", "")).lower()
        gender = av.get("gender", "").lower()
        
        score = 0
        for term in female_terms:
            if term in name:
                score += 3
            if term in tags:
                score += 2
        if "female" in gender or "woman" in gender:
            score += 5
        if "news" in name or "news" in tags:
            score += 4
        if "professional" in tags:
            score += 2
            
        scored.append((score, av))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Top avatar
    best = scored[0][1]
    avatar_id = best.get("avatar_id")
    avatar_name = best.get("avatar_name", "Unknown")
    
    print(f"✅ Selected avatar: {avatar_name} (ID: {avatar_id})")
    
    # Show top 3
    print("   Top choices:")
    for score, av in scored[:3]:
        print(f"   - {av.get('avatar_name')} (score: {score})")
    
    return avatar_id, avatar_name


def get_hindi_voice(voices=None):
    """Best Hindi female voice choose karo"""
    if not voices:
        try:
            r = requests.get(f"{HEYGEN_BASE}/v2/voices", headers=heygen_headers(), timeout=20)
            data = r.json()
            voices = data.get("data", {}).get("voices", [])
        except:
            voices = []

    # Hindi female voice dhundo
    hindi_female = []
    for v in voices:
        lang = v.get("language", "").lower()
        locale = v.get("locale", "").lower()
        name = v.get("name", "").lower()
        gender = v.get("gender", "").lower()

        is_hindi = "hindi" in lang or "hi-in" in locale or "hindi" in name
        is_female = "female" in gender or "woman" in gender or \
                    any(n in name for n in ["priya", "anjali", "neha", "kavya", "ananya", "divya"])

        if is_hindi and is_female:
            hindi_female.append(v)
        elif is_hindi:
            hindi_female.append(v)  # Hindi but not confirmed female

    if hindi_female:
        voice = hindi_female[0]
        print(f"✅ Voice: {voice.get('name')} ({voice.get('language', '')})")
        return voice["voice_id"]

    # Known HeyGen Hindi voice IDs fallback
    fallback_voices = [
        "2d5b0e6cf36f460aa7fc47e3eee4ba54",  # Hindi Female
        "1bd001e7e50f421d891986aad5158bc8",  # Hindi
    ]
    print("⚠️ Hindi voice list se nahi mili, default use karunga")
    return fallback_voices[0]


def create_heygen_video(avatar_id, voice_id, script_text, duration_hint=45):
    """HeyGen se avatar video create karo"""
    
    # Script clean
    clean_script = re.sub(r'#\w+', '', script_text)
    clean_script = re.sub(r'https?://\S+', '', clean_script)
    clean_script = re.sub(r'\s+', ' ', clean_script).strip()
    clean_script = clean_script[:2500]

    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "input_text": clean_script,
                "voice_id": voice_id,
                "speed": 1.15,
                "pitch": 0
            },
            "background": {
                "type": "color",
                "value": STUDIO_BG_COLOR
            }
        }],
        "dimension": {"width": 1080, "height": 1920},
        "test": False
    }

    try:
        r = requests.post(
            f"{HEYGEN_BASE}/v2/video/generate",
            headers=heygen_headers(),
            json=payload,
            timeout=30
        )
        data = r.json()
        video_id = data.get("data", {}).get("video_id")
        if video_id:
            print(f"✅ HeyGen video queued! ID: {video_id}")
            return video_id
        else:
            print(f"❌ HeyGen error: {data}")
            return None
    except Exception as e:
        print(f"❌ HeyGen API error: {e}")
        return None


def wait_for_video(video_id, max_wait=600):
    """Video ready hone ka wait karo"""
    print("⏳ Processing", end="", flush=True)
    start = time.time()

    while time.time() - start < max_wait:
        try:
            r = requests.get(
                f"{HEYGEN_BASE}/v1/video_status.get?video_id={video_id}",
                headers=heygen_headers(),
                timeout=20
            )
            data = r.json()
            status = data.get("data", {}).get("status", "")

            if status == "completed":
                url = data["data"].get("video_url", "")
                print(f"\n✅ Video ready!")
                return url
            elif status == "failed":
                err = data.get("data", {}).get("error", "Unknown")
                print(f"\n❌ Failed: {err}")
                return None
            else:
                print(".", end="", flush=True)
                time.sleep(10)
        except Exception as e:
            time.sleep(5)

    print(f"\n❌ Timeout")
    return None


def download_file(url, filepath):
    try:
        r = requests.get(url, stream=True, timeout=120,
                        headers={"User-Agent": "Mozilla/5.0"})
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return os.path.exists(filepath) and os.path.getsize(filepath) > 10000
    except Exception as e:
        print(f"⚠️ Download error: {e}")
        return False


def fetch_news_image(query, save_path):
    """News related image fetch karo"""
    PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")

    if PEXELS_KEY and PEXELS_KEY != "your_pexels_api_key_here":
        try:
            headers = {"Authorization": PEXELS_KEY}
            url = f"https://api.pexels.com/v1/search?query={query}&per_page=5"
            r = requests.get(url, headers=headers, timeout=15)
            photos = r.json().get("photos", [])
            if photos:
                img_url = photos[0]["src"]["large2x"]
                return download_file(img_url, save_path)
        except:
            pass

    # Unsplash fallback
    try:
        encoded = requests.utils.quote(query)
        url = f"https://source.unsplash.com/1080x1920/?{encoded}"
        r = requests.get(url, timeout=20, allow_redirects=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return os.path.getsize(save_path) > 5000
    except:
        pass

    return False


def add_news_ticker_overlay(input_path, headline, output_path):
    """
    News style ticker + branding add karo
    - Top: "TEZ TAK" logo bar
    - Bottom: Breaking news ticker
    - Professional look
    """
    # Clean headline
    clean_headline = re.sub(r'[^\w\s।,!?]', '', headline)[:60]
    
    font_file = None
    for fp in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]:
        if os.path.exists(fp):
            font_file = fp.replace('\\', '/').replace('C:/', 'C\\\\:/')
            break

    filters = []

    # Top bar - channel branding
    filters.append("drawbox=x=0:y=0:w=iw:h=120:color=0xcc0000@1.0:t=fill")

    # Channel name
    if font_file:
        filters.append(
            f"drawtext=fontfile='{font_file}':text='TEZ TAK':"
            f"fontsize=70:fontcolor=white:x=(w-text_w)/2:y=25"
        )

    # Bottom ticker bar
    filters.append("drawbox=x=0:y=ih-140:w=iw:h=140:color=0xcc0000@0.95:t=fill")
    filters.append("drawbox=x=0:y=ih-145:w=iw:h=5:color=white@1.0:t=fill")

    # BREAKING NEWS label
    if font_file:
        filters.append(
            f"drawtext=fontfile='{font_file}':text='BREAKING NEWS':"
            f"fontsize=30:fontcolor=yellow:x=20:y=ih-130"
        )
        # Headline text
        if clean_headline:
            safe_hl = clean_headline.replace("'", "").replace(":", " ").replace(",", " ")
            filters.append(
                f"drawtext=fontfile='{font_file}':text='{safe_hl}':"
                f"fontsize=36:fontcolor=white:x=20:y=ih-80"
            )

    vf = ",".join(filters)

    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', vf,
        '-c:v', 'libx264', '-profile:v', 'baseline',
        '-level', '3.0', '-pix_fmt', 'yuv420p',
        '-preset', 'fast', '-crf', '22',
        '-c:a', 'copy',
        '-movflags', '+faststart',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, timeout=120)
    return result.returncode == 0 and os.path.exists(output_path)


def create_heygen_short(script_data, video_index=0):
    """Main function - Professional news anchor short banao"""

    title = script_data.get("title", "news_short")
    safe_title = re.sub(r'[^\w\s-]', '', title.encode('ascii', 'ignore').decode())[:25].strip()
    if not safe_title:
        safe_title = f"news_{video_index}"

    output_path = f"{OUTPUT_DIR}/teztак_{video_index}_{safe_title}.mp4"
    scenes_dir = f"assets/scenes_{video_index}"
    Path(scenes_dir).mkdir(exist_ok=True)

    print(f"\n📺 Tez Tak short ban rahi hai: {title[:50]}")
    print(f"   Anchor: {script_data.get('anchor_name', 'N/A')}")

    # Step 1: Avatar + Voice select
    print("\n👤 Best Indian female avatar select ho rahi hai...")
    avatars = get_avatars()

    if not avatars:
        print("❌ Avatars nahi mile")
        return None

    avatar_id, avatar_name = select_best_indian_female_avatar(avatars)
    if not avatar_id:
        print("❌ Suitable avatar nahi mila")
        return None

    voice_id = get_hindi_voice()

    # Step 2: HeyGen se anchor video banao
    print(f"\n🎬 HeyGen anchor video ban rahi hai...")
    full_script = script_data.get("full_script", "")

    hg_video_id = create_heygen_video(avatar_id, voice_id, full_script)
    if not hg_video_id:
        return None

    video_url = wait_for_video(hg_video_id)
    if not video_url:
        return None

    raw_video = f"{scenes_dir}/anchor_raw.mp4"
    print("📥 Video download ho rahi hai...")
    if not download_file(video_url, raw_video):
        print("❌ Download fail")
        return None

    # Step 3: Portrait crop karo
    print("✂️ Portrait format mein crop ho raha hai...")
    cropped = f"{scenes_dir}/anchor_cropped.mp4"
    crop_cmd = [
        'ffmpeg', '-y', '-i', raw_video,
        '-vf', 'scale=iw*max(1080/iw\\,1920/ih):ih*max(1080/iw\\,1920/ih),crop=1080:1920,setsar=1',
        '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
        '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart', cropped
    ]
    subprocess.run(crop_cmd, capture_output=True)
    
    base_video = cropped if os.path.exists(cropped) else raw_video

    # Step 4: News ticker + branding add karo
    print("📺 Tez Tak branding add ho rahi hai...")
    headline = script_data.get("thumbnail_text", title)[:60]
    branded = f"{scenes_dir}/anchor_branded.mp4"

    if add_news_ticker_overlay(base_video, headline, branded):
        final_source = branded
        print("✅ Branding add ho gayi!")
    else:
        final_source = base_video
        print("⚠️ Branding skip, clean video use karunga")

    # Step 5: Final copy
    import shutil
    shutil.copy(final_source, output_path)

    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024*1024)
        print(f"\n✅ Tez Tak short ready! ({size_mb:.1f} MB)")
        print(f"📁 {output_path}")
        return output_path

    return None


def create_all_heygen_videos(scripts):
    created = []
    for i, script in enumerate(scripts):
        print(f"\n{'='*50}")
        print(f"Video {i+1}/{len(scripts)}")
        path = create_heygen_short(script, video_index=i)
        if path:
            created.append({
                "path": path,
                "title": script.get("title", ""),
                "description": script.get("description", ""),
                "hashtags": script.get("hashtags", []),
            })
        time.sleep(2)

    print(f"\n🎉 {len(created)}/{len(scripts)} videos ready!")

    import json
    with open("logs/created_videos.json", "w", encoding="utf-8") as f:
        json.dump(created, f, ensure_ascii=False, indent=2)

    return created


if __name__ == "__main__":
    test_script = {
        "anchor_name": "Priya Sharma",
        "title": "Bengal Election Result",
        "full_script": "Tez Tak pe aapka swagat hai, main hoon Priya Sharma. Bengal mein badi khabar aa rahi hai. Exit polls ke mutabik TMC ek baar phir satta mein wapas aa sakti hai. Mamata Banerjee ki party ko 160 se zyada seats milne ka anuman hai. BJP ko bada jhatka lag sakta hai. Ye result poore desh ki rajniti ko badal sakta hai. Like aur subscribe zarur karein, Tez Tak ke saath judey rahein.",
        "thumbnail_text": "Bengal mein bada upset!",
        "topic_data": {"category": "news"}
    }
    create_heygen_short(test_script, 0)