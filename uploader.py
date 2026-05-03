"""
uploader.py
YouTube pe automatically shorts upload karta hai
"""

import os
import json
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from dotenv import load_dotenv

load_dotenv()

# YouTube API scope
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'
]

TOKEN_FILE = "assets/youtube_token.pkl"
CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")


def get_youtube_service():
    """YouTube API service authenticate karo"""
    creds = None
    
    # Saved token check karo
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)
    
    # Token expired ya nahi hai
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS):
                print(f"❌ {CLIENT_SECRETS} file nahi mili!")
                print("📖 README mein dekho YouTube API setup kaise karna hai")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Token save karo
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
    
    service = build('youtube', 'v3', credentials=creds)
    print("✅ YouTube API connected!")
    return service


def upload_short(service, video_info):
    """
    Ek video YouTube pe upload karo
    
    video_info: {
        "path": "video file path",
        "title": "video title",
        "description": "description",
        "hashtags": ["#tag1", "#tag2"],
        "thumbnail": "thumbnail path"
    }
    """
    if not service:
        return None
    
    video_path = video_info.get("path")
    if not os.path.exists(video_path):
        print(f"❌ Video file nahi mili: {video_path}")
        return None
    
    title = video_info.get("title", "")[:100]  # YouTube max 100 chars
    description = video_info.get("description", "")
    hashtags = video_info.get("hashtags", [])
    
    # Description mein hashtags add karo
    hashtag_text = " ".join(hashtags) if hashtags else "#shorts #viral #hindi"
    full_description = f"{description}\n\n{hashtag_text}\n\n#Shorts"
    
    # Tags list banao
    tags = [tag.replace('#', '') for tag in hashtags] + ['shorts', 'viral', 'hindi', 'india']
    
    print(f"\n📤 Upload ho rahi hai: {title}")
    
    body = {
        'snippet': {
            'title': title,
            'description': full_description[:5000],
            'tags': tags[:500],
            'categoryId': '22',  # People & Blogs
            'defaultLanguage': 'hi',
        },
        'status': {
            'privacyStatus': 'public',  # Direct public upload
            'selfDeclaredMadeForKids': False,
        }
    }
    
    try:
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024*5  # 5MB chunks
        )
        
        request = service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        # Upload progress show karo
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"  ⬆️ Upload: {progress}%", end='\r')
        
        video_id = response.get('id')
        video_url = f"https://youtube.com/shorts/{video_id}"
        
        print(f"\n✅ Upload successful!")
        print(f"🔗 URL: {video_url}")
        
        # Thumbnail upload karo
        thumbnail_path = video_info.get("thumbnail")
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                service.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
                ).execute()
                print("✅ Thumbnail upload ho gayi!")
            except Exception as e:
                print(f"⚠️ Thumbnail upload failed: {e}")
        
        return video_id
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None


def upload_all_videos(videos_list):
    """Sabhi videos upload karo"""
    
    service = get_youtube_service()
    if not service:
        print("❌ YouTube service connect nahi hua")
        return []
    
    uploaded = []
    
    for i, video_info in enumerate(videos_list):
        print(f"\n{'='*50}")
        print(f"Video {i+1}/{len(videos_list)} upload ho rahi hai...")
        
        video_id = upload_short(service, video_info)
        
        if video_id:
            uploaded.append({
                "video_id": video_id,
                "url": f"https://youtube.com/shorts/{video_id}",
                "title": video_info.get("title")
            })
        
        # YouTube rate limit ke liye wait karo
        if i < len(videos_list) - 1:
            print("⏳ Next upload ke pehle 30 second wait...")
            time.sleep(30)
    
    # Save uploaded info
    with open("logs/uploaded_videos.json", "w", encoding="utf-8") as f:
        json.dump(uploaded, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 {len(uploaded)}/{len(videos_list)} videos successfully upload hui!")
    for v in uploaded:
        print(f"  ✅ {v['title']}: {v['url']}")
    
    return uploaded
