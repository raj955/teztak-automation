"""
scheduler.py - SMART AUTO SCHEDULER
News: Subah 7AM, 1PM, 7PM
Shayari: 7PM, 8:30PM, 9:30PM
- Har shayari unique - duplicate nahi
- PC on rehna chahiye (ya Windows Task Scheduler use karo)
"""

import schedule
import time
import subprocess
import sys
import os
import json
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

Path("logs").mkdir(exist_ok=True)
USED_SHAYARI_FILE = "logs/used_shayari.json"


# ─────────────────────────────────────────
# USED SHAYARI TRACKER - Duplicate prevent
# ─────────────────────────────────────────

def get_used_shayari():
    """Pehle use ki gayi shayari ka record"""
    if os.path.exists(USED_SHAYARI_FILE):
        with open(USED_SHAYARI_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def mark_shayari_used(shayar, theme):
    """Shayari ko used mark karo"""
    used = get_used_shayari()
    entry = f"{shayar}_{theme}"
    if entry not in used:
        used.append(entry)
    # Save
    with open(USED_SHAYARI_FILE, 'w', encoding='utf-8') as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def get_unused_shayari():
    """Jo shayari abhi tak use nahi hui"""
    from shayari_database import SHAYARI_COLLECTION
    
    used = get_used_shayari()
    unused = [s for s in SHAYARI_COLLECTION 
              if f"{s['shayar']}_{s['theme']}" not in used]
    
    # Agar sab use ho gayi toh reset karo
    if not unused:
        print("  ♻️ Sab shayari use ho gayi - reset ho rahi hai...")
        with open(USED_SHAYARI_FILE, 'w') as f:
            json.dump([], f)
        unused = SHAYARI_COLLECTION.copy()
    
    return unused


# ─────────────────────────────────────────
# UPLOAD HELPER
# ─────────────────────────────────────────

def upload_video(video_info):
    """Video ko sab platforms pe upload karo"""
    try:
        # YouTube
        from uploader import get_youtube_service, upload_short
        service = get_youtube_service()
        if service:
            yt_id = upload_short(service, video_info)
            if yt_id:
                print(f"  ✅ YouTube: https://youtube.com/shorts/{yt_id}")
    except Exception as e:
        print(f"  ⚠️ YouTube: {e}")

    try:
        # Facebook
        from social_uploader import upload_to_facebook
        upload_to_facebook(
            video_info['path'],
            video_info['title'],
            video_info['description'],
            video_info.get('hashtags', [])
        )
    except Exception as e:
        print(f"  ⚠️ Facebook: {e}")


# ─────────────────────────────────────────
# SHAYARI JOB
# ─────────────────────────────────────────

def shayari_job(slot_name="Shayari"):
    """Auto shayari video banao aur upload karo"""
    now = datetime.now().strftime('%H:%M')
    print(f"\n{'='*55}")
    print(f"🌹 {slot_name} | {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*55}")
    
    try:
        from shayari_creator import create_shayari_video
        
        # Unused shayari lo
        unused = get_unused_shayari()
        if not unused:
            print("❌ Koi shayari nahi mili")
            return
        
        # Random pick
        shayari_data = random.choice(unused)
        print(f"  📜 {shayari_data['shayar']} - {shayari_data['theme']}")
        
        # Video banao
        slot_num = int(datetime.now().strftime('%H%M'))
        result = create_shayari_video(
            shayari_data=shayari_data,
            video_index=slot_num
        )
        
        if result:
            # Used mark karo
            mark_shayari_used(shayari_data['shayar'], shayari_data['theme'])
            
            # Upload
            print(f"\n  📤 Upload ho raha hai...")
            upload_video(result)
            
            print(f"\n  ✅ {slot_name} complete!")
        else:
            print(f"  ❌ Video nahi bani")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ─────────────────────────────────────────
# NEWS JOB
# ─────────────────────────────────────────

def news_job(slot_name="News"):
    """Auto news video banao aur upload karo"""
    print(f"\n{'='*55}")
    print(f"📰 {slot_name} | {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*55}")
    
    try:
        result = subprocess.run(
            [sys.executable, 'main.py', '--count', '1'],
            capture_output=False,
            timeout=600
        )
        if result.returncode == 0:
            print(f"  ✅ {slot_name} complete!")
        else:
            print(f"  ⚠️ News job mein issue tha")
    except Exception as e:
        print(f"  ❌ Error: {e}")


# ─────────────────────────────────────────
# SCHEDULE SETUP
# ─────────────────────────────────────────

def setup_schedule():
    """Poora schedule setup karo"""
    
    # ── NEWS SCHEDULE ──────────────────────
    # Mon-Sat subah 7 AM
    schedule.every().monday.at("07:00").do(news_job, "🌅 Subah News")
    schedule.every().tuesday.at("07:00").do(news_job, "🌅 Subah News")
    schedule.every().wednesday.at("07:00").do(news_job, "🌅 Subah News")
    schedule.every().thursday.at("07:00").do(news_job, "🌅 Subah News")
    schedule.every().friday.at("07:00").do(news_job, "🌅 Subah News")
    schedule.every().saturday.at("07:00").do(news_job, "🌅 Subah News")
    
    # Dopahar 1 PM
    schedule.every().monday.at("13:00").do(news_job, "☀️ Dopahar News")
    schedule.every().tuesday.at("13:00").do(news_job, "☀️ Dopahar News")
    schedule.every().wednesday.at("13:00").do(news_job, "☀️ Dopahar News")
    schedule.every().thursday.at("13:00").do(news_job, "☀️ Dopahar News")
    schedule.every().friday.at("13:00").do(news_job, "☀️ Dopahar News")
    schedule.every().saturday.at("13:00").do(news_job, "☀️ Dopahar News")
    
    # ── SHAYARI SCHEDULE ───────────────────
    # Roz 7 PM
    schedule.every().day.at("19:00").do(shayari_job, "🌹 Shayari 7PM")
    
    # Roz 8:30 PM
    schedule.every().day.at("20:30").do(shayari_job, "🌹 Shayari 8:30PM")
    
    # Roz 9:30 PM
    schedule.every().day.at("21:30").do(shayari_job, "🌹 Shayari 9:30PM")


def print_schedule_info():
    """Schedule ka overview print karo"""
    print("""
╔══════════════════════════════════════════════════════╗
║         🗓️  AUTO SCHEDULER - TEZTAK                  ║
╠══════════════════════════════════════════════════════╣
║  📰 NEWS VIDEOS (Mon-Sat):                           ║
║     🌅 7:00  AM  - Subah news                        ║
║     ☀️  1:00  PM  - Dopahar news                     ║
║                                                      ║
║  🌹 SHAYARI VIDEOS (Daily):                          ║
║     🌹 7:00  PM  - Shayari 1                         ║
║     🌹 8:30  PM  - Shayari 2                         ║
║     🌹 9:30  PM  - Shayari 3                         ║
║                                                      ║
║  ✅ Har shayari UNIQUE - duplicate nahi hogi         ║
║  ⚠️  PC on rehna chahiye                             ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # Unused shayari count
    try:
        unused = get_unused_shayari()
        from shayari_database import SHAYARI_COLLECTION
        print(f"  📜 Available shayari: {len(unused)}/{len(SHAYARI_COLLECTION)}")
    except:
        pass
    
    # Next job
    jobs = sorted(schedule.jobs, key=lambda x: x.next_run)
    if jobs:
        next_job = jobs[0]
        print(f"  ⏰ Next job: {next_job.next_run.strftime('%A %I:%M %p')}")
    print()


def main():
    """Main scheduler"""
    setup_schedule()
    print_schedule_info()
    
    print("Abhi test run karna chahoge? (y/n): ", end="", flush=True)
    try:
        choice = input().strip().lower()
        if choice == 'y':
            print("\nKya test karein?")
            print("  1 = Shayari test")
            print("  2 = News test")
            print("Choice: ", end="")
            test_choice = input().strip()
            if test_choice == '1':
                shayari_job("🧪 Test Shayari")
            elif test_choice == '2':
                news_job("🧪 Test News")
    except:
        pass
    
    print("\n✅ Scheduler active hai!")
    print("PC on rakhna — background mein chalega")
    print("Band karne ke liye: Ctrl+C\n")
    
    print("Scheduler chal raha hai... (Ctrl+C se band karo)\n")
    try:
        while True:
            schedule.run_pending()
            
            # Har ghante status print karo
            now = datetime.now()
            if now.minute == 0 and now.second < 5:
                jobs = sorted(schedule.jobs, key=lambda x: x.next_run)
                if jobs:
                    next_time = jobs[0].next_run.strftime('%I:%M %p')
                    print(f"⏳ {now.strftime('%I:%M %p')} | Next: {next_time}")
            
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n✅ Scheduler band ho gaya. Phir chalane ke liye: python scheduler.py")


if __name__ == "__main__":
    main()