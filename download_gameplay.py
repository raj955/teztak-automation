"""
download_gameplay.py - UPDATED
Multiple methods try karta hai gameplay download karne ke liye
"""

import subprocess
import os
import sys
import requests
from pathlib import Path

GAMEPLAY_DIR = "assets/gameplay"
Path(GAMEPLAY_DIR).mkdir(parents=True, exist_ok=True)

# Direct MP4 links - different sources
SOURCES = [
    # Pexels portrait videos (moving backgrounds)
    {
        "url": "https://videos.pexels.com/video-files/856973/856973-hd_1080_1920_25fps.mp4",
        "name": "bg_1.mp4", "type": "minecraft"
    },
    {
        "url": "https://videos.pexels.com/video-files/3571264/3571264-sd_360_640_25fps.mp4",
        "name": "bg_2.mp4", "type": "subway"
    },
    {
        "url": "https://videos.pexels.com/video-files/1093662/1093662-hd_1080_1920_30fps.mp4",
        "name": "bg_3.mp4", "type": "satisfying"
    },
    {
        "url": "https://videos.pexels.com/video-files/2516159/2516159-hd_1080_1920_24fps.mp4",
        "name": "bg_4.mp4", "type": "minecraft"
    },
    {
        "url": "https://videos.pexels.com/video-files/3194277/3194277-hd_1080_1920_25fps.mp4",
        "name": "bg_5.mp4", "type": "subway"
    },
]

def try_download(url, filepath):
    """Multiple methods se download try karo"""
    
    # Method 1: requests
    try:
        print(f"    Method 1: Direct download...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.pexels.com/",
            "Accept": "*/*",
        }
        r = requests.get(url, headers=headers, stream=True, timeout=60)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=1024*512):
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"    {downloaded//1024//1024}MB", end='\r')
            print()
            if os.path.getsize(filepath) > 100000:
                return True
    except Exception as e:
        print(f"    Method 1 fail: {e}")
    
    # Method 2: curl
    try:
        print(f"    Method 2: curl...")
        result = subprocess.run([
            'curl', '-L', '-o', filepath,
            '--user-agent', 'Mozilla/5.0',
            '--referer', 'https://www.pexels.com/',
            '--max-time', '60',
            url
        ], capture_output=True, timeout=120)
        if result.returncode == 0 and os.path.exists(filepath):
            if os.path.getsize(filepath) > 100000:
                return True
    except Exception as e:
        print(f"    Method 2 fail: {e}")

    # Method 3: wget
    try:
        print(f"    Method 3: wget...")
        result = subprocess.run([
            'wget', '-O', filepath, url,
            '--user-agent=Mozilla/5.0',
            '--timeout=60'
        ], capture_output=True, timeout=120)
        if result.returncode == 0 and os.path.exists(filepath):
            if os.path.getsize(filepath) > 100000:
                return True
    except Exception as e:
        print(f"    Method 3 fail: {e}")
    
    return False


def download_all_gameplay():
    print("""
╔══════════════════════════════════════════╗
║   🎮 Gameplay Downloader v3               ║
╚══════════════════════════════════════════╝
    """)

    downloaded = []

    for i, source in enumerate(SOURCES):
        name = source['name']
        final_path = os.path.join(GAMEPLAY_DIR, name)

        if os.path.exists(final_path) and os.path.getsize(final_path) > 100000:
            print(f"[{i+1}/{len(SOURCES)}] ⏭️  Already hai: {name}")
            downloaded.append({"path": final_path, "type": source['type']})
            continue

        print(f"\n[{i+1}/{len(SOURCES)}] Downloading: {name}")
        
        if try_download(source['url'], final_path):
            size = os.path.getsize(final_path) / 1024 / 1024
            print(f"  ✅ {name} ({size:.1f} MB)")
            downloaded.append({"path": final_path, "type": source['type']})
        else:
            print(f"  ❌ Failed: {name}")
            if os.path.exists(final_path):
                os.remove(final_path)

    # Index save
    import json
    with open(os.path.join(GAMEPLAY_DIR, "index.json"), "w") as f:
        json.dump({"videos": downloaded}, f, indent=2)

    print(f"\n{'='*50}")
    print(f"✅ {len(downloaded)}/{len(SOURCES)} videos ready!")

    if downloaded:
        print("\n🎮 Ab 'python main.py --test' chalao!")
    else:
        print("\n❌ Download nahi hua.")
        print("\n👉 MANUAL OPTION:")
        print("1. Apne phone se koi bhi vertical video lo")
        print("2. Copy karo: assets\\gameplay\\minecraft_1.mp4")
        print("3. python main.py --test chalao")

    return downloaded


def get_available_gameplay():
    import json
    index_file = os.path.join(GAMEPLAY_DIR, "index.json")
    if os.path.exists(index_file):
        with open(index_file) as f:
            data = json.load(f)
            return [v for v in data.get("videos", []) if os.path.exists(v["path"])]
    videos = []
    for f in Path(GAMEPLAY_DIR).glob("*.mp4"):
        if f.stat().st_size > 100000:
            vtype = "minecraft" if "minecraft" in f.name else \
                    "subway" if "subway" in f.name else "satisfying"
            videos.append({"path": str(f), "type": vtype})
    return videos


if __name__ == "__main__":
    download_all_gameplay()