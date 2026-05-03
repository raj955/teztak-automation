"""
github_runner.py
GitHub Actions pe chalane ke liye
Interactive input nahi - fully automatic
"""

import sys
import os
import random
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
Path("assets").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

# GitHub pe Windows fonts nahi hain - Linux font use karo
LINUX_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fix_font_for_linux():
    """Linux pe font path fix karo"""
    import auto_video_creator
    import shayari_creator

    if os.path.exists(LINUX_FONT):
        linux_font_escaped = LINUX_FONT.replace('/', '\\/')
        auto_video_creator.FONT = LINUX_FONT
        auto_video_creator.FONT_PATH = LINUX_FONT
        shayari_creator.FONT = LINUX_FONT
        shayari_creator.FONT_PATH = LINUX_FONT
        print(f"✅ Linux font: {LINUX_FONT}")
    else:
        print("⚠️ Font nahi mili - text bina font ke hoga")


def run_shayari():
    """Shayari video banao aur upload karo"""
    print("\n🌹 GitHub Shayari Job")

    fix_font_for_linux()

    from shayari_creator import create_shayari_video
    from shayari_database import SHAYARI_COLLECTION

    # Used shayari track
    used_file = "logs/used_shayari.json"
    used = json.load(open(used_file, encoding='utf-8')) if os.path.exists(used_file) else []

    # Unused dhundho
    unused = [s for s in SHAYARI_COLLECTION
              if f"{s['shayar']}_{s['theme']}" not in used]

    if not unused:
        print("♻️ Reset - sab shayari use ho gayi")
        unused = SHAYARI_COLLECTION.copy()
        with open(used_file, 'w') as f:
            json.dump([], f)

    shayari_data = random.choice(unused)
    print(f"📜 {shayari_data['shayar']} - {shayari_data['theme']}")

    result = create_shayari_video(shayari_data=shayari_data, video_index=1)

    if result:
        # Mark used
        used.append(f"{shayari_data['shayar']}_{shayari_data['theme']}")
        with open(used_file, 'w', encoding='utf-8') as f:
            json.dump(used, f, ensure_ascii=False, indent=2)

        # Upload
        upload(result)
        print("✅ Shayari job complete!")
    else:
        print("❌ Video nahi bani")
        sys.exit(1)


def run_news():
    """News video banao aur upload karo"""
    print("\n📰 GitHub News Job")

    fix_font_for_linux()

    from trend_researcher import research_todays_viral_topics
    from script_generator import generate_multiple_scripts
    from auto_video_creator import create_auto_video

    # Topics
    topics = research_todays_viral_topics()
    if not topics:
        print("❌ Topics nahi mile")
        sys.exit(1)

    # Script
    scripts = generate_multiple_scripts(topics, count=1)
    if not scripts:
        print("❌ Script nahi bani")
        sys.exit(1)

    script = scripts[0]
    print(f"✅ Script: {script.get('title', '')[:50]}")

    # Video
    path = create_auto_video(script, video_index=0)
    if not path:
        print("❌ Video nahi bani")
        sys.exit(1)

    video_info = {
        "path": path,
        "title": script.get("title", ""),
        "description": script.get("description", ""),
        "hashtags": script.get("hashtags", [])
    }

    upload(video_info)
    print("✅ News job complete!")


def upload(video_info):
    """YouTube + Facebook upload"""

    # YouTube
    try:
        from uploader import get_youtube_service, upload_short
        service = get_youtube_service()
        if service:
            yt_id = upload_short(service, video_info)
            if yt_id:
                print(f"✅ YouTube: https://youtube.com/shorts/{yt_id}")
    except Exception as e:
        print(f"⚠️ YouTube: {e}")

    # Facebook
    try:
        from social_uploader import upload_to_facebook
        upload_to_facebook(
            video_info['path'],
            video_info['title'],
            video_info.get('description', ''),
            video_info.get('hashtags', [])
        )
    except Exception as e:
        print(f"⚠️ Facebook: {e}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "shayari"

    if mode == "shayari":
        run_shayari()
    elif mode == "news":
        run_news()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
