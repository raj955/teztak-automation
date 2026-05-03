"""
social_uploader.py
Facebook + Instagram auto upload
Instagram: Facebook Cross-posting ya Resumable Upload
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")


# ─────────────────────────────────────────
# FACEBOOK UPLOAD
# ─────────────────────────────────────────

def upload_to_facebook(video_path, title, description, hashtags):
    """Facebook Page pe Reels upload karo"""
    print("\n📘 Facebook pe upload ho raha hai...")

    hashtag_text = " ".join(hashtags) if hashtags else "#shorts #viral #hindi"
    caption = f"{title}\n\n{description}\n\n{hashtag_text}"

    url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/videos"

    try:
        with open(video_path, 'rb') as vf:
            r = requests.post(
                url,
                data={
                    "description": caption[:2000],
                    "title": title[:100],
                    "access_token": FACEBOOK_ACCESS_TOKEN,
                },
                files={"source": vf},
                timeout=300
            )
        data = r.json()

        if "id" in data:
            print(f"✅ Facebook upload success!")
            print(f"🔗 https://www.facebook.com/watch/?v={data['id']}")
            return data["id"]
        else:
            print(f"❌ Facebook error: {data}")
            return None
    except Exception as e:
        print(f"❌ Facebook error: {e}")
        return None


# ─────────────────────────────────────────
# INSTAGRAM UPLOAD - RESUMABLE METHOD
# ─────────────────────────────────────────

def get_instagram_id():
    """Instagram Business Account ID lo"""
    ig_id = INSTAGRAM_ACCOUNT_ID
    if ig_id:
        return ig_id

    try:
        r = requests.get(
            f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}",
            params={"fields": "instagram_business_account", "access_token": FACEBOOK_ACCESS_TOKEN},
            timeout=15
        )
        ig_id = r.json().get("instagram_business_account", {}).get("id")
        if ig_id:
            # Save to .env
            env_content = open(".env").read()
            if "INSTAGRAM_ACCOUNT_ID" not in env_content:
                with open(".env", "a") as f:
                    f.write(f"\nINSTAGRAM_ACCOUNT_ID={ig_id}")
            print(f"✅ Instagram ID: {ig_id}")
        return ig_id
    except Exception as e:
        print(f"⚠️ Instagram ID error: {e}")
        return None


def upload_to_instagram(video_path, title, description, hashtags):
    """Instagram Reels upload - Direct video_url method"""
    print("\n📸 Instagram Reels upload ho raha hai...")

    ig_id = get_instagram_id()
    if not ig_id:
        print("❌ Instagram ID nahi mila")
        return None

    hashtag_text = " ".join(hashtags) if hashtags else "#reels #viral #hindi"
    caption = f"{title}\n\n{description}\n\n{hashtag_text}\n\n#Reels"

    try:
        # Step 1: Pehle video Facebook pe upload karo (public URL ke liye)
        print("  📤 Facebook pe temporarily upload ho rahi hai...")
        fb_url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/videos"
        
        with open(video_path, "rb") as vf:
            fb_r = requests.post(
                fb_url,
                data={
                    "published": "true",
                    "access_token": FACEBOOK_ACCESS_TOKEN,
                    "description": caption[:2000],
                },
                files={"source": vf},
                timeout=300
            )
        
        fb_data = fb_r.json()
        if "id" not in fb_data:
            print(f"  ❌ Facebook upload error: {fb_data}")
            return None
        
        fb_video_id = fb_data["id"]
        print(f"  ✅ Facebook video ID: {fb_video_id}")
        
        # Step 2: Facebook video URL se Instagram container banao
        video_url = f"https://www.facebook.com/video/upload/v2.0/{fb_video_id}"
        
        # Actually - seedha file size se resumable karo
        file_size = os.path.getsize(video_path)
        
        print("  📦 Instagram container ban raha hai...")
        init_r = requests.post(
            f"https://graph.facebook.com/v18.0/{ig_id}/media",
            data={
                "media_type": "REELS",
                "upload_type": "resumable",
                "caption": caption[:2200],
                "access_token": FACEBOOK_ACCESS_TOKEN,
            },
            timeout=30
        )
        
        init_data = init_r.json()
        print(f"  Container response: {init_data}")
        
        if "uri" not in init_data:
            print(f"  ❌ Container error: {init_data}")
            return None
        
        upload_uri = init_data["uri"]
        container_id = init_data.get("id", "")
        
        # Step 3: Video bytes upload
        print(f"  ⬆️ Video upload ({file_size//1024//1024}MB)...")
        with open(video_path, "rb") as vf:
            video_data = vf.read()
        
        upload_r = requests.post(
            upload_uri,
            headers={
                "Authorization": f"OAuth {FACEBOOK_ACCESS_TOKEN}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream",
            },
            data=video_data,
            timeout=300
        )
        
        upload_resp = upload_r.json() if upload_r.content else {}
        print(f"  Upload response: {upload_resp}")
        
        if not container_id:
            container_id = upload_resp.get("id", "")
        
        if not container_id:
            print("  ❌ Container ID nahi mila")
            return None
        
        # Step 4: Status check
        print("  ⏳ Processing", end="", flush=True)
        for _ in range(30):
            time.sleep(5)
            status_r = requests.get(
                f"https://graph.facebook.com/v18.0/{container_id}",
                params={"fields": "status_code,status", "access_token": FACEBOOK_ACCESS_TOKEN},
                timeout=15
            )
            status_data = status_r.json()
            status = status_data.get("status_code", "")
            if status == "FINISHED":
                print(" ✅")
                break
            elif status == "ERROR":
                print(f" ❌ {status_data}")
                return None
            print(".", end="", flush=True)
        
        # Step 5: Publish
        print("  📤 Publishing...")
        pub_r = requests.post(
            f"https://graph.facebook.com/v18.0/{ig_id}/media_publish",
            data={"creation_id": container_id, "access_token": FACEBOOK_ACCESS_TOKEN},
            timeout=30
        )
        pub_data = pub_r.json()
        
        if "id" in pub_data:
            print(f"✅ Instagram success! ID: {pub_data['id']}")
            return pub_data["id"]
        else:
            print(f"❌ Publish error: {pub_data}")
            return None

    except Exception as e:
        print(f"❌ Instagram error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ─────────────────────────────────────────
# MAIN - SAB PLATFORMS
# ─────────────────────────────────────────

def upload_to_all_platforms(video_info):
    """Facebook + Instagram pe upload karo"""
    results = {"title": video_info.get("title", ""), "facebook": None, "instagram": None}

    video_path = video_info.get("path")
    title = video_info.get("title", "")
    description = video_info.get("description", "")
    hashtags = video_info.get("hashtags", [])

    if not video_path or not os.path.exists(video_path):
        print(f"❌ Video nahi mili: {video_path}")
        return results

    print(f"\n{'='*55}")
    print(f"📤 Uploading: {title[:45]}")
    print(f"{'='*55}")

    # Facebook
    results["facebook"] = upload_to_facebook(video_path, title, description, hashtags)
    time.sleep(3)

    # Instagram
    results["instagram"] = upload_to_instagram(video_path, title, description, hashtags)

    return results


def upload_all_to_social(videos_list):
    """Sabhi videos Facebook + Instagram pe upload karo"""
    print("""
╔══════════════════════════════════════════════╗
║   📱 Social Media Auto Upload                ║
║   Facebook Page + Instagram Reels           ║
╚══════════════════════════════════════════════╝
    """)

    all_results = []

    for i, video in enumerate(videos_list):
        print(f"\nVideo {i+1}/{len(videos_list)}")
        result = upload_to_all_platforms(video)
        all_results.append(result)
        if i < len(videos_list) - 1:
            print("⏳ 15 sec wait...")
            time.sleep(15)

    # Summary
    print(f"\n{'='*55}")
    print("📊 UPLOAD SUMMARY")
    print(f"{'='*55}")
    for r in all_results:
        fb = "✅" if r['facebook'] else "❌"
        ig = "✅" if r['instagram'] else "❌"
        print(f"📹 {r['title'][:40]}")
        print(f"   📘 Facebook: {fb}   📸 Instagram: {ig}")

    with open("logs/social_uploads.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    return all_results


if __name__ == "__main__":
    import sys, glob

    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        videos = glob.glob("output/*.mp4") + glob.glob("heygen_ready/*.mp4")
        if not videos:
            print("❌ Koi video nahi mili")
            sys.exit(1)
        video_path = max(videos, key=os.path.getctime)
        print(f"Latest video: {video_path}")

    test_video = {
        "path": video_path,
        "title": "Test Viral Hindi Short",
        "description": "Aaj ki sabse badi khabar",
        "hashtags": ["#shorts", "#viral", "#hindi", "#news"]
    }
    upload_to_all_platforms(test_video)