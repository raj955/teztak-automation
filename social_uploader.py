"""
social_uploader.py
Facebook Page + Instagram pe automatic video upload
Same video - teen platforms pe ek saath!
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")  # FB se milega


# ─────────────────────────────────────────
# FACEBOOK PAGE UPLOAD
# ─────────────────────────────────────────

def upload_to_facebook(video_path, title, description, hashtags):
    """Facebook Page pe video upload karo"""
    
    print("\n📘 Facebook pe upload ho raha hai...")
    
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("❌ Facebook credentials .env mein nahi hain")
        return None
    
    # Caption banao
    hashtag_text = " ".join(hashtags) if hashtags else "#shorts #viral #hindi"
    caption = f"{title}\n\n{description}\n\n{hashtag_text}"
    
    url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/videos"
    
    try:
        with open(video_path, 'rb') as video_file:
            response = requests.post(
                url,
                data={
                    "description": caption[:2000],
                    "title": title[:100],
                    "access_token": FACEBOOK_ACCESS_TOKEN,
                },
                files={"source": video_file},
                timeout=300
            )
        
        data = response.json()
        
        if "id" in data:
            video_id = data["id"]
            fb_url = f"https://www.facebook.com/watch/?v={video_id}"
            print(f"✅ Facebook upload success!")
            print(f"🔗 {fb_url}")
            return video_id
        else:
            print(f"❌ Facebook error: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Facebook upload error: {e}")
        return None


# ─────────────────────────────────────────
# INSTAGRAM UPLOAD
# ─────────────────────────────────────────

def get_instagram_account_id():
    """Facebook Page se Instagram Account ID lo"""
    
    if INSTAGRAM_ACCOUNT_ID:
        return INSTAGRAM_ACCOUNT_ID
    
    try:
        url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}"
        params = {
            "fields": "instagram_business_account",
            "access_token": FACEBOOK_ACCESS_TOKEN
        }
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        ig_id = data.get("instagram_business_account", {}).get("id")
        
        if ig_id:
            print(f"✅ Instagram Account ID: {ig_id}")
            # .env mein save karo
            with open(".env", "a") as f:
                f.write(f"\nINSTAGRAM_ACCOUNT_ID={ig_id}")
            return ig_id
        else:
            print("⚠️ Instagram account Facebook Page se linked nahi hai")
            print("   Instagram ko Facebook Page se connect karo:")
            print("   Instagram → Settings → Account → Linked Accounts → Facebook")
            return None
    except Exception as e:
        print(f"❌ Instagram ID fetch error: {e}")
        return None


def upload_to_instagram(video_path, title, description, hashtags):
    """Instagram Reels pe upload karo"""
    
    print("\n📸 Instagram pe upload ho raha hai...")
    
    ig_id = get_instagram_account_id()
    if not ig_id:
        print("❌ Instagram Account ID nahi mila")
        return None
    
    hashtag_text = " ".join(hashtags) if hashtags else "#shorts #viral #hindi"
    caption = f"{title}\n\n{description}\n\n{hashtag_text}\n\n#Reels #Instagram"
    
    # Step 1: Video file publicly accessible URL chahiye
    # Pehle Facebook pe upload karo, phir URL use karo
    # Ya direct upload karo
    
    try:
        # Instagram Container banao
        container_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
        
        # Video file read karo
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        # Multipart upload
        container_params = {
            "media_type": "REELS",
            "caption": caption[:2200],
            "access_token": FACEBOOK_ACCESS_TOKEN,
        }
        
        files = {"video_file": ("video.mp4", video_data, "video/mp4")}
        
        r1 = requests.post(
            container_url,
            data=container_params,
            files=files,
            timeout=300
        )
        
        container_data = r1.json()
        
        if "id" not in container_data:
            print(f"❌ Container error: {container_data}")
            return None
        
        container_id = container_data["id"]
        print(f"  📦 Container ready: {container_id}")
        
        # Step 2: Processing wait karo
        print("  ⏳ Processing...", end="", flush=True)
        for _ in range(30):
            time.sleep(5)
            status_r = requests.get(
                f"https://graph.facebook.com/v18.0/{container_id}",
                params={"fields": "status_code", "access_token": FACEBOOK_ACCESS_TOKEN},
                timeout=15
            )
            status = status_r.json().get("status_code", "")
            if status == "FINISHED":
                print(" Ready!")
                break
            elif status == "ERROR":
                print(f" Error!")
                return None
            else:
                print(".", end="", flush=True)
        
        # Step 3: Publish karo
        publish_url = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
        r3 = requests.post(
            publish_url,
            data={
                "creation_id": container_id,
                "access_token": FACEBOOK_ACCESS_TOKEN
            },
            timeout=30
        )
        
        publish_data = r3.json()
        
        if "id" in publish_data:
            media_id = publish_data["id"]
            print(f"✅ Instagram Reels upload success!")
            print(f"🔗 instagram.com/reels/{media_id}")
            return media_id
        else:
            print(f"❌ Publish error: {publish_data}")
            return None
            
    except Exception as e:
        print(f"❌ Instagram upload error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ─────────────────────────────────────────
# MAIN - TEEN PLATFORMS PE UPLOAD
# ─────────────────────────────────────────

def upload_to_all_platforms(video_info):
    """
    Ek video ko teen platforms pe upload karo:
    YouTube + Facebook + Instagram
    """
    results = {
        "title": video_info.get("title", ""),
        "youtube": None,
        "facebook": None,
        "instagram": None
    }
    
    video_path = video_info.get("path")
    title = video_info.get("title", "")
    description = video_info.get("description", "")
    hashtags = video_info.get("hashtags", [])
    
    if not video_path or not os.path.exists(video_path):
        print(f"❌ Video file nahi mili: {video_path}")
        return results
    
    print(f"\n{'='*55}")
    print(f"📤 Uploading: {title[:45]}")
    print(f"{'='*55}")
    
    # Facebook
    fb_id = upload_to_facebook(video_path, title, description, hashtags)
    results["facebook"] = fb_id
    time.sleep(3)
    
    # Instagram
    ig_id = upload_to_instagram(video_path, title, description, hashtags)
    results["instagram"] = ig_id
    
    return results


def upload_all_to_social(videos_list):
    """Sabhi videos teen platforms pe upload karo"""
    
    print("""
╔══════════════════════════════════════════════╗
║   📱 Social Media Auto Upload                ║
║   Facebook + Instagram                       ║
╚══════════════════════════════════════════════╝
    """)
    
    all_results = []
    
    for i, video in enumerate(videos_list):
        print(f"\nVideo {i+1}/{len(videos_list)}")
        result = upload_to_all_platforms(video)
        all_results.append(result)
        
        # Rate limit ke liye wait
        if i < len(videos_list) - 1:
            print("⏳ 15 second wait (rate limit)...")
            time.sleep(15)
    
    # Summary
    print(f"\n{'='*55}")
    print("📊 UPLOAD SUMMARY")
    print(f"{'='*55}")
    
    for r in all_results:
        title = r['title'][:35]
        fb = "✅" if r['facebook'] else "❌"
        ig = "✅" if r['instagram'] else "❌"
        print(f"{title}")
        print(f"  📘 Facebook: {fb}  📸 Instagram: {ig}")
    
    # Save results
    with open("logs/social_uploads.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    return all_results


if __name__ == "__main__":
    # Test with a sample video
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Latest video dhundo
        import glob
        videos = glob.glob("output/*.mp4") + glob.glob("heygen_ready/*.mp4")
        if not videos:
            print("❌ Koi video nahi mili output/ ya heygen_ready/ mein")
            sys.exit(1)
        video_path = max(videos, key=os.path.getctime)
        print(f"Latest video: {video_path}")
    
    test_video = {
        "path": video_path,
        "title": "Test Upload - Viral Hindi Short",
        "description": "Test video upload",
        "hashtags": ["#shorts", "#viral", "#hindi"]
    }
    
    upload_to_all_platforms(test_video)
