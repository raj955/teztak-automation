"""
main.py
Poora automation ek command se chalao!

Usage:
    python main.py              # Normal run - research, create, upload
    python main.py --no-upload  # Sirf videos banao, upload mat karo
    python main.py --count 5    # 5 videos banao (default 3)
    python main.py --test       # Test mode - ek video banao
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Folders ensure karo
for folder in ["output", "assets", "logs"]:
    Path(folder).mkdir(exist_ok=True)


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║   🎬 YouTube Shorts Auto Generator           ║
║   Powered by Gemini AI                       ║  
║   Daily Viral Content - Fully Automated      ║
╚══════════════════════════════════════════════╝
    """)


def check_requirements():
    """Zaroori cheezein check karo"""
    errors = []
    
    # Gemini API key
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        errors.append("❌ GEMINI_API_KEY .env file mein set nahi hai")
    
    # FFmpeg check
    import subprocess
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
    if result.returncode != 0:
        errors.append("❌ FFmpeg install nahi hai - https://ffmpeg.org/download.html")
    
    if errors:
        print("\n⚠️ Setup incomplete hai:\n")
        for e in errors:
            print(f"  {e}")
        print("\nREADME.md dekho setup ke liye\n")
        return False
    
    print("✅ Sab requirements check ho gayi!\n")
    return True


def run_full_pipeline(count=3, upload=True):
    """Poora pipeline chalao"""
    
    start_time = time.time()
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n🚀 Pipeline start: {today}")
    print(f"📊 {count} shorts banenge aaj\n")
    
    # ── STEP 1: Research ──────────────────────────────
    print("=" * 50)
    print("STEP 1: Aaj ke viral topics dhundh raha hoon...")
    print("=" * 50)
    
    from trend_researcher import research_todays_viral_topics
    viral_topics = research_todays_viral_topics()
    
    if not viral_topics:
        print("❌ Koi viral topics nahi mili. Kal try karo.")
        return
    
    print(f"\n✅ {len(viral_topics)} viral topics mili!")
    
    # ── STEP 2: Script Generation ─────────────────────
    print("\n" + "=" * 50)
    print("STEP 2: Scripts likh raha hoon...")
    print("=" * 50)
    
    from script_generator import generate_multiple_scripts
    scripts = generate_multiple_scripts(viral_topics, count=count)
    
    if not scripts:
        print("❌ Scripts generate nahi hue.")
        return
    
    print(f"\n✅ {len(scripts)} scripts ready!")
    
    # ── STEP 3: Video Creation ────────────────────────
    print("\n" + "=" * 50)
    print("STEP 3: Videos ban rahi hain...")
    print("=" * 50)
    
    # Always use auto_video_creator - reliable, no API credits needed
    print('🎬 Auto Video mode - Facts/Story/News with images')
    from auto_video_creator import create_all_auto_videos
    videos = create_all_auto_videos(scripts)
    
    if not videos:
        print("❌ Koi video nahi bani.")
        return
    
    print(f"\n✅ {len(videos)} videos ready!")
    
    # ── STEP 4: Upload ────────────────────────────────
    if upload:
        print("\n" + "=" * 50)
        print("STEP 4: YouTube pe upload ho raha hai...")
        print("=" * 50)
        
        from uploader import upload_all_videos
        uploaded = upload_all_videos(videos)
        
        print(f"\n✅ {len(uploaded)} videos live hain YouTube pe!")
    else:
        print("\n⏭️ Upload skip kiya (--no-upload flag tha)")
        print(f"📁 Videos yahan hain: {os.path.abspath('output/')}")
    
    # ── SUMMARY ───────────────────────────────────────
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 50)
    print("🎉 AAJ KA KAAM COMPLETE!")
    print("=" * 50)
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"📹 Videos bane: {len(videos)}")
    
    if upload:
        print(f"📤 Uploaded: {len(uploaded) if 'uploaded' in dir() else 0}")
    
    # Log save karo
    log = {
        "date": today,
        "topics_found": len(viral_topics),
        "scripts_generated": len(scripts),
        "videos_created": len(videos),
        "uploaded": len(uploaded) if (upload and 'uploaded' in dir()) else 0,
        "time_taken_minutes": round(elapsed/60, 1)
    }
    
    with open(f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "w") as f:
        json.dump(log, f, indent=2)
    
    print("\n📊 Log save ho gaya logs/ folder mein")


def main():
    parser = argparse.ArgumentParser(description='YouTube Shorts Auto Generator')
    parser.add_argument('--count', type=int, default=3,
                        help='Kitne shorts banane hain (default: 3)')
    parser.add_argument('--no-upload', action='store_true',
                        help='Sirf videos banao, upload mat karo')
    parser.add_argument('--test', action='store_true',
                        help='Test mode - ek video banao, upload nahi')
    
    args = parser.parse_args()
    
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    if args.test:
        print("🧪 TEST MODE - Ek video banenge, upload nahi hoga\n")
        run_full_pipeline(count=1, upload=False)
    else:
        count = args.count
        upload = not args.no_upload
        run_full_pipeline(count=count, upload=upload)


if __name__ == "__main__":
    main()