"""
manual_workflow.py - FINAL FIXED
- Facts/Story/Roast/Countdown: Auto banti hain
- Anchor: HeyGen se banao
- Koi bhi naam se video rakho
"""

import os
import json
import time
import glob
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HEYGEN_VIDEOS_DIR = "heygen_ready"
Path(HEYGEN_VIDEOS_DIR).mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)


def generate_scripts(count=3):
    print("\n" + "="*55)
    print("STEP 1: Scripts ban rahi hain...")
    print("="*55)
    from trend_researcher import research_todays_viral_topics
    topics = research_todays_viral_topics()
    if not topics:
        return []
    from script_generator import generate_multiple_scripts
    return generate_multiple_scripts(topics, count=count)


def show_scripts(scripts):
    print("\n" + "="*55)
    print("STEP 2: Scripts Ready")
    print("="*55)

    scripts_data = []
    heygen_count = 0
    auto_count = 0

    for i, script in enumerate(scripts, 1):
        title = script.get('title', '')
        full_script = script.get('full_script', '')
        description = script.get('description', '')
        hashtags = ' '.join(script.get('hashtags', []))
        fmt = script.get('format', 'anchor')
        anchor = script.get('anchor_name', '')
        needs_heygen = (fmt == 'anchor' or bool(anchor))

        if needs_heygen:
            heygen_count += 1
            print(f"\n{'='*55}")
            print(f"SCRIPT {i} [HEYGEN SE BANAO] - {title[:50]}")
            print(f"Anchor: {anchor} | Format: {fmt}")
        else:
            auto_count += 1
            print(f"\n{'='*55}")
            print(f"SCRIPT {i} [AUTO BANEGI] - {title[:50]}")
            print(f"Format: {fmt} (HeyGen nahi chahiye)")

        print("="*55)
        print(full_script[:500])
        print(f"\nTitle: {title}")
        print(f"Description: {description[:100]}")
        print(f"Hashtags: {hashtags}")

        scripts_data.append({
            "index": i,
            "title": title,
            "description": description,
            "hashtags": script.get('hashtags', []),
            "full_script": full_script,
            "format": fmt,
            "anchor_name": anchor,
            "needs_heygen": needs_heygen
        })

    print(f"\n{'='*55}")
    print(f"Summary:")
    print(f"  Auto banengi (HeyGen nahi chahiye): {auto_count} videos")
    print(f"  HeyGen se banani hain: {heygen_count} videos")
    print("="*55)

    with open("logs/pending_upload.json", "w", encoding="utf-8") as f:
        json.dump(scripts_data, f, ensure_ascii=False, indent=2)

    # User se puchho - har script ke liye
    print("\n" + "="*55)
    print("Har script ke liye choose karo:")
    print("  1 = Auto banao (system banayega - facts/story style)")
    print("  2 = HeyGen se banaunga (anchor style)")
    print("  s = Skip - ye script nahi chahiye")
    print("="*55)

    final_scripts = []
    for s in scripts_data:
        print(f"\nScript {s['index']}: {s['title'][:50]}")
        print(f"Default format: {s['format']} | ", end="")
        print("Choice (1=Auto / 2=HeyGen / s=Skip): ", end="")
        try:
            choice = input().strip().lower()
        except:
            choice = '1'

        if choice == 's':
            print("Skip kiya")
            continue
        elif choice == '2':
            s['needs_heygen'] = True
            s['format'] = 'anchor'
            print(f"HeyGen se banoge")
        else:
            s['needs_heygen'] = False
            if s['format'] == 'anchor':
                s['format'] = 'facts'  # Auto ke liye facts use karo
            print(f"Auto banega [{s['format']}]")

        final_scripts.append(s)

    return final_scripts


def process_and_upload(scripts_data):
    all_videos = []

    # ── Auto videos pehle banao ──
    auto_scripts = [s for s in scripts_data if not s['needs_heygen']]
    heygen_scripts = [s for s in scripts_data if s['needs_heygen']]

    if auto_scripts:
        print(f"\n{'='*55}")
        print(f"AUTO VIDEOS BAN RAHI HAIN ({len(auto_scripts)} videos)...")
        print(f"Facts/Story/Roast/Countdown — relevant images + Edge TTS")
        print("="*55)

        try:
            from auto_video_creator import create_auto_video
            for s in auto_scripts:
                print(f"\nBan rahi hai: {s['title'][:45]} [{s['format']}]")
                path = create_auto_video(s, video_index=s['index'])
                if path:
                    all_videos.append({
                        "path": path,
                        "title": s['title'],
                        "description": s['description'],
                        "hashtags": s['hashtags']
                    })
                    print(f"✅ Auto video ready!")
                else:
                    print(f"❌ Auto video fail hui")
        except Exception as e:
            print(f"Auto video error: {e}")
            import traceback
            traceback.print_exc()

    # ── HeyGen videos ──
    if heygen_scripts:
        print(f"\n{'='*55}")
        print(f"HEYGEN VIDEOS ({len(heygen_scripts)} scripts):")
        for s in heygen_scripts:
            print(f"  → Script {s['index']}: {s['title'][:45]}")
            print(f"    Anchor: {s['anchor_name']}")
        print(f"\nHeyGen pe banao aur '{os.path.abspath(HEYGEN_VIDEOS_DIR)}/' mein rakho")
        print(f"Koi bhi naam se rakho — Enter dabao jab ready ho...")
        print("="*55)
        input()

        # Folder se videos lo
        existing_paths = {v['path'] for v in all_videos}
        mp4s = sorted(
            [f for f in glob.glob(os.path.join(HEYGEN_VIDEOS_DIR, "*.mp4"))
             if os.path.getsize(f) > 100000],
            key=os.path.getctime
        )

        if mp4s:
            print(f"\n{len(mp4s)} videos mili folder mein!")
            for j, mp4 in enumerate(mp4s):
                script = heygen_scripts[j] if j < len(heygen_scripts) else heygen_scripts[-1]
                print(f"  {os.path.basename(mp4)} → {script['title'][:40]}")
                all_videos.append({
                    "path": mp4,
                    "title": script['title'],
                    "description": script['description'],
                    "hashtags": script['hashtags']
                })
        else:
            print("Koi video nahi mili folder mein!")

    if not all_videos:
        print("\nKoi video upload ke liye nahi hai!")
        return

    # ── Upload loop ──
    print(f"\n{'='*55}")
    print(f"UPLOAD: {len(all_videos)} videos ready hain")
    print("="*55)

    for video in all_videos:
        print(f"\nVideo: {os.path.basename(video['path'])}")
        print(f"Title: {video['title'][:50]}")
        print(f"Upload karna hai? (y/n/skip): ", end="")

        try:
            choice = input().strip().lower()
        except:
            choice = 'y'

        if choice == 'n' or choice == 'skip':
            print("Skip kiya")
            continue

        do_upload(video)

    print(f"\nSab ho gaya!")


def do_upload(video_info):
    """YouTube + Facebook + Instagram"""
    print(f"\nUpload ho raha hai: {video_info['title'][:45]}")

    # YouTube
    try:
        from uploader import get_youtube_service, upload_short
        service = get_youtube_service()
        if service:
            yt_id = upload_short(service, video_info)
            if yt_id:
                print(f"✅ YouTube: https://youtube.com/shorts/{yt_id}")
    except Exception as e:
        print(f"YouTube error: {e}")

    # Facebook
    try:
        from social_uploader import upload_to_facebook
        fb_id = upload_to_facebook(
            video_info['path'], video_info['title'],
            video_info['description'], video_info['hashtags']
        )
        if fb_id:
            print(f"✅ Facebook: https://www.facebook.com/watch/?v={fb_id}")
    except Exception as e:
        print(f"Facebook error: {e}")

    # Instagram
    try:
        from social_uploader import upload_to_instagram
        upload_to_instagram(
            video_info['path'], video_info['title'],
            video_info['description'], video_info['hashtags']
        )
    except Exception as e:
        print(f"Instagram error: {e}")




def run_shayari():
    """Shayari videos banao aur upload karo"""
    from shayari_creator import create_shayari_batch
    from shayari_database import get_all_themes
    import random

    print("\nKitne shayari videos? (default 3): ", end="")
    try:
        count = int(input().strip() or "3")
    except:
        count = 3

    all_themes = get_all_themes()
    themes = random.sample(all_themes, min(count, len(all_themes)))
    print(f"Themes: {themes}")

    results = create_shayari_batch(themes=themes, count=count)

    if results:
        print(f"\n{len(results)} shayari videos ready!")
        for r in results:
            print(f"\nVideo: {os.path.basename(r['path'])}")
            print(f"Title: {r['title'][:50]}")
            print("Upload? (y/n): ", end="")
            if input().strip().lower() == 'y':
                do_upload(r)


def run():
    import sys
    print("\n====================================================")
    print("   Tez Tak - Smart Workflow")
    print("====================================================")
    print("\n  1 = News/Facts/Story videos")
    print("  2 = Shayari videos")
    print("\nChoice (default 1): ", end="")
    try:
        mode = input().strip()
    except:
        mode = "1"

    if mode == "2":
        run_shayari()
        return

    count = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
    scripts = generate_scripts(count=count)
    if not scripts:
        return
    scripts_data = show_scripts(scripts)
    process_and_upload(scripts_data)


if __name__ == "__main__":
    run()