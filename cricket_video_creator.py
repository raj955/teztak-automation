"""
cricket_video_creator.py
YouTube Creative Commons cricket footage + viral script
100% legal - copyright free
"""

import os, re, json, time, subprocess, random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path("assets/cricket").mkdir(parents=True, exist_ok=True)

FONT = "C\\:/Windows/Fonts/arialbd.ttf"

# ─────────────────────────────────────────
# STEP 1: YouTube CC Cricket Videos
# ─────────────────────────────────────────

# Creative Commons cricket search queries
CC_CRICKET_QUERIES = [
    "cricket highlights",
    "cricket batting",
    "cricket bowling action",
    "cricket six",
    "cricket wicket",
    "ipl cricket match",
    "india cricket",
    "cricket stadium",
]

def search_cc_cricket(query, max_results=5):
    """YouTube se Creative Commons cricket videos search karo"""
    try:
        # yt-dlp se CC videos search karo
        cmd = [
            'yt-dlp',
            f'ytsearch{max_results}:{query} cricket',
            '--match-filter', 'license = "Creative Commons Attribution license (reuse allowed)"',
            '--print', '%(id)s|||%(title)s|||%(duration)s|||%(uploader)s',
            '--no-download',
            '--quiet',
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|||' in line:
                parts = line.split('|||')
                if len(parts) >= 3:
                    vid_id, title, duration = parts[0], parts[1], parts[2]
                    uploader = parts[3] if len(parts) > 3 else ""
                    try:
                        dur = int(duration)
                        if 10 <= dur <= 600:  # 10 sec to 10 min
                            videos.append({
                                "id": vid_id,
                                "title": title,
                                "duration": dur,
                                "uploader": uploader,
                                "url": f"https://youtube.com/watch?v={vid_id}"
                            })
                    except:
                        pass
        
        print(f"  Found {len(videos)} CC cricket videos for '{query}'")
        return videos
        
    except Exception as e:
        print(f"  Search error: {e}")
        return []


def find_best_cricket_videos(topic="cricket highlights", count=4):
    """Topic ke liye best CC cricket videos dhundho"""
    print(f"\n🔍 Searching CC cricket videos: {topic}")
    
    all_videos = []
    
    # Topic-specific search
    all_videos.extend(search_cc_cricket(topic, max_results=5))
    time.sleep(1)
    
    # Generic cricket search as backup
    if len(all_videos) < count:
        for query in CC_CRICKET_QUERIES[:3]:
            if len(all_videos) >= count * 2:
                break
            all_videos.extend(search_cc_cricket(query, max_results=3))
            time.sleep(0.5)
    
    # Duplicates remove
    seen = set()
    unique = []
    for v in all_videos:
        if v['id'] not in seen:
            seen.add(v['id'])
            unique.append(v)
    
    print(f"  Total unique: {len(unique)} videos")
    return unique[:count * 2]  # Extra for backup


def download_cricket_clip(video_id, start_sec, duration_sec, output_path):
    """
    Cricket video ka specific clip download karo
    start_sec: kahan se start karo
    duration_sec: kitna lamba clip chahiye
    """
    url = f"https://youtube.com/watch?v={video_id}"
    temp_path = output_path.replace('.mp4', '_temp.mp4')
    
    try:
        # Download best quality
        cmd_download = [
            'yt-dlp',
            '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
            '--output', temp_path,
            '--no-playlist',
            '--quiet',
            url
        ]
        
        print(f"    📥 Downloading clip...")
        r = subprocess.run(cmd_download, capture_output=True, timeout=120)
        
        # Find downloaded file
        actual_file = None
        for ext in ['.mp4', '.webm', '.mkv']:
            test = temp_path.replace('.mp4', '') + ext if not temp_path.endswith(ext) else temp_path
            if os.path.exists(test) and os.path.getsize(test) > 10000:
                actual_file = test
                break
        
        if not actual_file:
            # Try temp_path directly
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 10000:
                actual_file = temp_path
        
        if not actual_file:
            return False
        
        # FFmpeg se clip extract karo + portrait crop
        cmd_clip = [
            'ffmpeg', '-y',
            '-ss', str(start_sec),
            '-i', actual_file,
            '-t', str(duration_sec),
            '-vf', (
                'scale=iw*max(1080/iw\\,1920/ih):ih*max(1080/iw\\,1920/ih),'
                'crop=1080:1920,setsar=1'
            ),
            '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ]
        
        r2 = subprocess.run(cmd_clip, capture_output=True, timeout=60)
        
        # Cleanup temp
        if os.path.exists(actual_file) and actual_file != output_path:
            os.remove(actual_file)
        
        return r2.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000
        
    except Exception as e:
        print(f"    Download error: {e}")
        return False


# ─────────────────────────────────────────
# STEP 2: Cricket Script Generator
# ─────────────────────────────────────────

def generate_cricket_script(topic):
    """Viral cricket script generate karo"""
    from gemini_client import generate
    
    prompt = f"""
Tu viral Hindi cricket facts/story scriptwriter hai.

Topic: {topic}

VIRAL CRICKET HOOKS (choose best):
- "Ye moment cricket history mein hamesha yaad rahega..."
- "99% cricket fans nahi jaante ye secret..."
- "[Player] ne ye kiya tab poora stadium hairan reh gaya..."
- "Ye [number] cricket facts sun ke aap hairan ho jaoge..."

Script rules:
- SIRF Roman Hindi (Hinglish) - Devanagari NAHI
- Voice ke liye short punchy sentences (max 8 words each)
- Dramatic pauses ke liye "..." use karo
- Real cricket stats/facts include karo
- 45-55 seconds ka content
- Max 150 words

Structure:
1. HOOK (0-5s): Scroll rokne wala opening
2. FACT/STORY (5-40s): 4-5 amazing cricket facts
3. CLIMAX (40-48s): Sabse shocking fact last mein
4. CTA (48-55s): "Like karo agar ye nahi pata tha!"

SIRF JSON:
{{
  "title": "catchy Hindi title max 60 chars",
  "description": "YouTube description 3 lines",
  "hashtags": ["#cricket", "#shorts", "#viral", "#dhoni", "#india"],
  "full_script": "poora Roman Hindi script",
  "search_queries": [
    "specific cricket search term for yt-dlp 1",
    "specific cricket search term for yt-dlp 2",
    "specific cricket search term for yt-dlp 3"
  ],
  "thumbnail_text": "thumbnail text max 6 words"
}}"""
    
    try:
        resp = generate(prompt)
        if resp:
            t = resp.strip()
            if "```json" in t:
                t = t.split("```json")[1].split("```")[0].strip()
            elif "```" in t:
                t = t.split("```")[1].split("```")[0].strip()
            return json.loads(t)
    except Exception as e:
        print(f"Script error: {e}")
    return None


# ─────────────────────────────────────────
# STEP 3: Cricket Short Banao
# ─────────────────────────────────────────

def make_voice(text, out_path):
    """Clear Hindi voice"""
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    try:
        import asyncio, edge_tts
        async def run():
            c = edge_tts.Communicate(text, "hi-IN-SwaraNeural", rate="+8%", volume="+20%")
            await c.save(out_path)
        asyncio.run(run())
        if os.path.exists(out_path) and os.path.getsize(out_path) > 2000:
            print(f"  ✅ Voice ready")
            return True
    except:
        pass
    
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save(out_path)
        return os.path.exists(out_path)
    except:
        return False


def get_audio_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
            capture_output=True, timeout=10
        )
        return float(r.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 50.0


def add_captions_to_video(video_path, script_text, output_path):
    """Video pe viral-style captions add karo"""
    
    sentences = [s.strip() for s in re.split(r'[.!?]+', script_text) if len(s.strip()) > 3]
    if not sentences:
        import shutil
        shutil.copy(video_path, output_path)
        return True
    
    duration = get_audio_duration(video_path)
    time_per = duration / len(sentences)
    
    # SRT file banao
    srt_path = video_path.replace('.mp4', '.srt')
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, sent in enumerate(sentences[:12]):
            start = i * time_per
            end = start + time_per - 0.1
            
            def fmt(s):
                h, m = int(s//3600), int((s%3600)//60)
                sec, ms = int(s%60), int((s%1)*1000)
                return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
            
            f.write(f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{sent[:70]}\n\n")
    
    has_font = os.path.exists("C:/Windows/Fonts/arialbd.ttf")
    
    if has_font:
        subtitle_style = (
            f"force_style='FontName=Arial Bold,FontSize=18,"
            f"PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,"
            f"Outline=3,Shadow=2,Alignment=2,MarginV=50'"
        )
    else:
        subtitle_style = (
            "force_style='FontSize=16,PrimaryColour=&H00FFFF00,"
            "OutlineColour=&H00000000,Outline=3,Alignment=2,MarginV=50'"
        )
    
    srt_escaped = os.path.abspath(srt_path).replace('\\', '/').replace('C:/', 'C\\\\:/')
    
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-vf', f"subtitles='{srt_escaped}':{subtitle_style}",
        '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
        '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '23',
        '-c:a', 'copy', '-movflags', '+faststart', output_path
    ]
    
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    
    if os.path.exists(srt_path):
        os.remove(srt_path)
    
    if r.returncode == 0 and os.path.exists(output_path):
        return True
    
    import shutil
    shutil.copy(video_path, output_path)
    return True


def merge_clips_with_audio(clip_files, audio_path, output_path):
    """Cricket clips + voiceover merge karo"""
    
    valid = [f for f in clip_files if os.path.exists(f) and os.path.getsize(f) > 10000]
    if not valid:
        return False
    
    audio_dur = get_audio_duration(audio_path)
    
    # filter_complex concat
    inputs = []
    for f in valid:
        inputs += ['-i', f]
    
    n = len(valid)
    fstr = ''.join(f'[{i}:v]' for i in range(n))
    fstr += f'concat=n={n}:v=1:a=0[vout]'
    
    temp = output_path.replace('.mp4', '_merged.mp4')
    
    r1 = subprocess.run(
        ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', fstr, '-map', '[vout]',
            '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
            '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '23',
            '-t', str(audio_dur + 1),
            '-movflags', '+faststart', temp
        ], capture_output=True, timeout=300
    )
    
    if r1.returncode != 0:
        # Fallback concat
        list_f = temp.replace('.mp4', '_list.txt')
        with open(list_f, 'w') as f:
            for v in valid:
                f.write(f"file '{os.path.abspath(v).replace(chr(92), '/')}'\n")
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_f,
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast',
            '-t', str(audio_dur + 1), temp
        ], capture_output=True, timeout=300)
        if os.path.exists(list_f):
            os.remove(list_f)
    
    if not os.path.exists(temp):
        return False
    
    # Add voiceover (mix with original audio - cricket sounds stay!)
    r2 = subprocess.run([
        'ffmpeg', '-y', '-i', temp, '-i', audio_path,
        '-filter_complex',
        '[0:a]volume=0.15[a1];[1:a]volume=1.4[a2];[a1][a2]amix=inputs=2:duration=shortest[aout]',
        '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-movflags', '+faststart', output_path
    ], capture_output=True, timeout=120)
    
    if os.path.exists(temp):
        os.remove(temp)
    
    return r2.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 100000


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def create_cricket_short(topic="Dhoni best moments", video_index=0):
    """
    Complete cricket short banao:
    CC footage + Hindi voiceover + captions
    """
    
    safe = re.sub(r'[^\w]', '_', topic)[:20]
    work_dir = f"assets/cricket_{video_index}"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    
    audio_path = f"{work_dir}/voice.mp3"
    output_raw = f"{work_dir}/raw.mp4"
    output_path = f"{OUTPUT_DIR}/cricket_{video_index}_{safe}.mp4"
    
    print(f"\n🏏 Cricket Short: {topic}")
    print("="*50)
    
    # Step 1: Script
    print("📝 Script generate ho raha hai...")
    script = generate_cricket_script(topic)
    if not script:
        print("❌ Script fail")
        return None
    
    full_script = script.get("full_script", "")
    search_queries = script.get("search_queries", ["cricket highlights", "cricket batting"])
    print(f"  ✅ Script ready: {script.get('title', '')[:50]}")
    
    # Step 2: Voice
    print("\n🎤 Voice ban rahi hai...")
    if not make_voice(full_script, audio_path):
        print("❌ Voice fail")
        return None
    
    audio_dur = get_audio_duration(audio_path)
    print(f"  ✅ {audio_dur:.1f}s")
    
    # Step 3: CC Cricket Videos Download
    print("\n🎥 Creative Commons cricket footage dhundh raha hoon...")
    
    clip_files = []
    clips_needed = 4
    clip_duration = audio_dur / clips_needed
    
    for i, query in enumerate(search_queries[:3]):
        if len(clip_files) >= clips_needed:
            break
        
        print(f"\n  Query {i+1}: '{query}'")
        videos = find_best_cricket_videos(query, count=3)
        
        for vid in videos[:2]:
            if len(clip_files) >= clips_needed:
                break
            
            clip_path = f"{work_dir}/clip_{len(clip_files)}.mp4"
            
            # Random start point
            max_start = max(0, vid['duration'] - int(clip_duration) - 5)
            start = random.randint(0, max_start) if max_start > 0 else 0
            
            print(f"    Video: {vid['title'][:40]}")
            if download_cricket_clip(vid['id'], start, int(clip_duration) + 2, clip_path):
                clip_files.append(clip_path)
                print(f"    ✅ Clip {len(clip_files)} ready ({int(clip_duration)}s)")
            else:
                print(f"    ❌ Download fail")
            
            time.sleep(1)
    
    if not clip_files:
        print("\n⚠️ CC clips nahi mili - Pexels cricket images use kar raha hoon...")
        # Fallback to auto_video_creator
        from auto_video_creator import create_auto_video
        script['format'] = 'facts'
        script['topic_data'] = {'category': 'sports'}
        return create_auto_video(script, video_index=video_index)
    
    print(f"\n✅ {len(clip_files)} cricket clips ready!")
    
    # Step 4: Merge clips + voice
    print("\n🎞️ Clips + voice merge ho raha hai...")
    if not merge_clips_with_audio(clip_files, audio_path, output_raw):
        print("❌ Merge fail")
        return None
    
    # Step 5: Captions add karo
    print("📝 Captions add ho rahi hain...")
    add_captions_to_video(output_raw, full_script, output_path)
    
    if os.path.exists(output_raw):
        os.remove(output_raw)
    
    if os.path.exists(output_path):
        mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n✅ Cricket Short Ready! {mb:.1f} MB")
        print(f"📁 {output_path}")
        
        return {
            "path": output_path,
            "title": script.get("title", ""),
            "description": script.get("description", ""),
            "hashtags": script.get("hashtags", [])
        }
    
    return None


if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Dhoni best cricket moments IPL"
    result = create_cricket_short(topic, video_index=0)
    if result:
        print(f"\n🎉 Done! Upload karo: python upload_video.py {result['path']}")
