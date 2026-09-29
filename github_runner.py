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


def run_shayari(count=1):
    """Shayari video banao aur upload karo"""
    print(f"\n🌹 GitHub Shayari Job ({count} videos)")

    fix_font_for_linux()

    from shayari_creator import create_shayari_video
    from shayari_database import SHAYARI_COLLECTION

    # Used shayari track
    used_file = "logs/used_shayari.json"
    used = json.load(open(used_file, encoding='utf-8')) if os.path.exists(used_file) else []

    success = 0
    for i in range(count):
        # Unused dhundho
        unused = [s for s in SHAYARI_COLLECTION
                  if f"{s['shayar']}_{s['theme']}" not in used]

        if not unused:
            print("♻️ Reset - sab shayari use ho gayi")
            used = []
            with open(used_file, 'w') as f:
                json.dump([], f)
            unused = SHAYARI_COLLECTION.copy()

        shayari_data = random.choice(unused)
        print(f"\n📜 {i+1}/{count}: {shayari_data['shayar']} - {shayari_data['theme']}")

        result = create_shayari_video(shayari_data=shayari_data, video_index=i)

        if result:
            used.append(f"{shayari_data['shayar']}_{shayari_data['theme']}")
            with open(used_file, 'w', encoding='utf-8') as f:
                json.dump(used, f, ensure_ascii=False, indent=2)
            upload(result)
            success += 1
        else:
            print(f"❌ Video {i+1} nahi bani")

    print(f"\n✅ {success}/{count} shayari complete!")
    if success == 0:
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
    """YouTube + Facebook + Instagram upload"""

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

    # Instagram
    try:
        from social_uploader import upload_to_instagram
        upload_to_instagram(
            video_info['path'],
            video_info['title'],
            video_info.get('description', ''),
            video_info.get('hashtags', [])
        )
    except Exception as e:
        print(f"⚠️ Instagram: {e}")


def run_wisdom():
    """Osho/Spiritual wisdom video - roz 1"""
    print("\n🙏 GitHub Wisdom Job")
    fix_font_for_linux()

    from osho_creator import create_wisdom_video, WISDOM_TOPICS
    import random

    # Used topics track
    used_file = "logs/used_wisdom.json"
    try:
        used = json.load(open(used_file, encoding='utf-8'))
    except:
        used = []

    # Unused topics
    unused = [t for t in WISDOM_TOPICS if f"{t[0]}_{t[1]}" not in used]
    if not unused:
        used = []
        json.dump([], open(used_file, 'w'), ensure_ascii=False)
        unused = WISDOM_TOPICS.copy()

    t = random.choice(unused)
    topic_type, topic, mood = t
    print(f"Topic: {topic_type} - {topic}")

    result = create_wisdom_video(topic_type=topic_type, topic=topic, mood=mood, video_index=1)

    if result:
        used.append(f"{topic_type}_{topic}")
        json.dump(used, open(used_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        upload(result)
        print("✅ Wisdom job complete!")
    else:
        print("❌ Video nahi bani")
        sys.exit(1)


def run_quotes():
    """Motivational quotes video - curated bank se, roz 1"""
    print("\n💬 GitHub Quotes Job")
    fix_font_for_linux()

    from quotes_creator import create_quote_video

    result = create_quote_video(video_index=2)

    if result:
        upload(result)
        print("✅ Quotes job complete!")
    else:
        print("❌ Video nahi bani")
        sys.exit(1)


def run_viral():
    """Viral facts/story/countdown video - 10PM 11PM pe"""
    print("\n🔥 GitHub Viral Job")
    fix_font_for_linux()

    from trend_researcher import research_todays_viral_topics
    from script_generator import generate_viral_script
    from auto_video_creator import create_auto_video
    import random

    # Viral formats - raat ke liye best
    viral_formats = ["facts", "story", "countdown", "roast"]
    fmt = random.choice(viral_formats)

    topics = research_todays_viral_topics()
    if not topics:
        print("❌ Topics nahi mile")
        sys.exit(1)

    topic = topics[0]
    topic["script_index"] = 0
    print(f"Topic: {topic.get('short_title', topic.get('title', ''))[:50]}")

    script = generate_viral_script(topic, forced_format=fmt)
    if not script:
        print("❌ Script nahi bani")
        sys.exit(1)

    print(f"✅ [{fmt.upper()}] {script.get('title', '')[:50]}")

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
    print("✅ Viral job complete!")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "shayari"

    if mode == "shayari":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_shayari(count)
    elif mode == "news":
        run_news()
    elif mode == "wisdom":
        run_wisdom()
    elif mode == "viral":
        run_viral()
    elif mode == "quotes":
        run_quotes()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)