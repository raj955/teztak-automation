"""
video_creator.py - FIXED VERSION
- Unicode/Hindi text crash fix
- Gameplay fallback fix
- Robust error handling
"""

import os
import json
import time
import re
import subprocess
import random
import shutil
from pathlib import Path
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
GAMEPLAY_DIR = "assets/gameplay"


def create_voiceover(script_text, output_file):
    try:
        # Script clean karo
        if isinstance(script_text, list):
            script_text = ' '.join(str(s) for s in script_text)
        script_text = str(script_text).strip()
        
        # Emojis aur special chars remove karo voice ke liye
        import re as _re
        script_text = _re.sub(r"[🀀-🿿]", "", script_text)
        script_text = _re.sub(r"[☀-⛿✀-➿]", "", script_text)
        script_text = _re.sub(r"#\w+", "", script_text)
        script_text = _re.sub(r"https?://\S+", "", script_text)
        script_text = _re.sub(r"\s+", " ", script_text).strip()
        
        if not script_text:
            print("⚠️ Script empty hai")
            return False
        
        print(f"🎤 Script length: {len(script_text)} chars")
        
        # gTTS se voice banao
        tts = gTTS(text=script_text, lang="hi", slow=False)
        tts.save(output_file)
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
            print("✅ Voiceover ready")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Voiceover error: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_audio_duration(audio_file):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries',
             'format=duration', '-of', 'csv=p=0', audio_file],
            capture_output=True, timeout=30
        )
        return float(result.stdout.decode('utf-8', errors='ignore').strip())
    except:
        return 45.0


def get_gameplay_video(category="facts"):
    """Gameplay video select karo"""
    try:
        from download_gameplay import get_available_gameplay
        videos = get_available_gameplay()
        if not videos:
            return None
        preference = {
            "facts":      ["minecraft", "satisfying"],
            "horror":     ["minecraft"],
            "motivation": ["satisfying", "subway"],
            "news":       ["subway"],
            "finance":    ["satisfying"],
            "sports":     ["subway"],
        }
        preferred = preference.get(category, ["minecraft", "subway"])
        for ptype in preferred:
            matching = [v for v in videos if v.get("type") == ptype]
            if matching:
                return random.choice(matching)["path"]
        return random.choice(videos)["path"]
    except:
        return None


def run_ffmpeg(cmd):
    """FFmpeg chalao - Unicode safe"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        stdout = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ''
        stderr = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ''
        return result.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        return -1, '', 'Timeout'
    except Exception as e:
        return -1, '', str(e)


def clean_for_drawtext(text):
    """
    Text ko FFmpeg drawtext ke liye safe banao
    Hindi Unicode remove karke transliteration ya symbols rakho
    """
    # Emojis aur special chars remove karo
    text = re.sub(r'[^\x00-\x7F\u0900-\u097F ]', '', text)
    # Hindi text ke liye - FFmpeg drawtext Hindi font ke bina crash karta hai
    # Isliye romanize karte hain simple version
    # Special ffmpeg chars escape karo
    text = text.replace('\\', '')
    text = text.replace("'", '')
    text = text.replace('"', '')
    text = text.replace(':', ' ')
    text = text.replace('%', ' percent ')
    text = text.replace('[', '')
    text = text.replace(']', '')
    text = text.replace(',', ' ')
    text = text.strip()
    return text[:70]  # Max length


def create_subtitle_file(sentences, duration, srt_path):
    """
    SRT subtitle file banao - Hindi ke liye ye approach better hai
    FFmpeg subtitles filter Unicode support karta hai
    """
    time_per = duration / max(len(sentences), 1)
    
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, sent in enumerate(sentences):
            start = i * time_per
            end = min(start + time_per - 0.1, duration)
            
            # SRT time format: HH:MM:SS,mmm
            def fmt(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int((sec % 1) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            
            f.write(f"{i+1}\n")
            f.write(f"{fmt(start)} --> {fmt(end)}\n")
            f.write(f"{sent[:80]}\n\n")
    
    return srt_path


def add_subtitles_with_srt(input_path, full_script, duration, output_path):
    """
    SRT file se subtitles add karo - Hindi ke liye best approach
    """
    sentences = [s.strip() for s in re.split(r'[।.!?\n]+', full_script) if len(s.strip()) > 3]
    
    if not sentences:
        shutil.copy(input_path, output_path)
        return output_path
    
    srt_path = input_path.replace('.mp4', '.srt')
    create_subtitle_file(sentences, duration, srt_path)
    
    # Windows font path for Hindi
    font_path = None
    for fp in [
        "C:/Windows/Fonts/mangal.ttf",      # Hindi support
        "C:/Windows/Fonts/arialbd.ttf",      # Fallback
        "C:/Windows/Fonts/calibrib.ttf",
    ]:
        if os.path.exists(fp):
            font_path = fp.replace('\\', '/').replace('C:/', 'C\\\\:/')
            break
    
    # Bottom dark bar + subtitles
    if font_path:
        subtitle_filter = (
            f"drawbox=x=0:y=ih-340:w=iw:h=340:color=black@0.6:t=fill,"
            f"subtitles='{srt_path.replace(chr(92), '/').replace('C:/', 'C\\\\:/')}':"
            f"force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFF00,"
            f"OutlineColour=&H00000000,Outline=3,Shadow=2,"
            f"Alignment=2,MarginV=60'"
        )
    else:
        subtitle_filter = (
            f"drawbox=x=0:y=ih-340:w=iw:h=340:color=black@0.6:t=fill,"
            f"subtitles='{srt_path.replace(chr(92), '/').replace('C:/', 'C\\\\:/')}':"
            f"force_style='FontSize=20,PrimaryColour=&H00FFFF00,"
            f"OutlineColour=&H00000000,Outline=3,"
            f"Alignment=2,MarginV=60'"
        )
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-vf', subtitle_filter,
        '-c:v', 'libx264',
        '-profile:v', 'baseline',
        '-level', '3.0',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'copy',
        '-movflags', '+faststart',
        output_path
    ]
    
    code, out, err = run_ffmpeg(cmd)
    
    # SRT cleanup
    if os.path.exists(srt_path):
        os.remove(srt_path)
    
    if code == 0 and os.path.exists(output_path):
        print("✅ Subtitles add ho gayi!")
        return output_path
    else:
        print(f"⚠️ Subtitle error, bina subtitle ke save kar raha hoon")
        if err:
            print(err[-300:])
        shutil.copy(input_path, output_path)
        return output_path


def create_shorts_video_ffmpeg(script_data, video_index=0):
    title = script_data.get("title", "viral_short")
    # Safe filename - sirf ASCII
    safe_title = re.sub(r'[^\w\s-]', '', title.encode('ascii', 'ignore').decode())[:25].strip()
    if not safe_title:
        safe_title = f"short_{video_index}"
    
    category = script_data.get("topic_data", {}).get("category", "facts")
    audio_path = f"assets/voiceover_{video_index}.mp3"
    temp_path = f"assets/temp_{video_index}.mp4"
    output_path = f"{OUTPUT_DIR}/short_{video_index}_{safe_title}.mp4"

    print(f"\n🎬 Video ban rahi hai: {title[:50]}")

    # Step 1: Voiceover
    print("🎤 Voiceover generate ho rahi hai...")
    full_script = script_data.get("full_script", "")
    # Script clean karo - hashtags, titles, extra text remove karo
    import re as _re
    full_script = _re.sub(r'#\w+', '', full_script)           # hashtags remove
    full_script = _re.sub(r'https?://\S+', '', full_script)   # URLs remove  
    full_script = _re.sub(r'[🀀-🿿]', '', full_script)  # emojis remove
    full_script = _re.sub(r'\s+', ' ', full_script).strip()   # extra spaces
    if not create_voiceover(full_script, audio_path):
        return None

    duration = get_audio_duration(audio_path)
    print(f"⏱️ Duration: {duration:.1f}s")

    # Step 2: Gameplay select
    print("🎮 Gameplay video select ho raha hai...")
    gameplay_path = get_gameplay_video(category)

    if gameplay_path and os.path.exists(gameplay_path):
        print(f"✅ Gameplay: {os.path.basename(gameplay_path)}")
    else:
        print("⚠️ Gameplay nahi mili - dark background use karunga")
        gameplay_path = None

    # Step 3: Base video
    print("🎞️ Base video compile ho rahi hai...")

    try:
        if gameplay_path:
            base_cmd = [
                'ffmpeg', '-y',
                '-stream_loop', '-1',
                '-i', gameplay_path,
                '-i', audio_path,
                '-vf', (
                    'scale=iw*max(1080/iw\\,1920/ih):ih*max(1080/iw\\,1920/ih),'
                    'crop=1080:1920,setsar=1,'
                    'colorbalance=rs=-0.05:gs=-0.05:bs=-0.05'
                ),
                '-c:v', 'libx264',
                '-profile:v', 'baseline',
                '-level', '3.0',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-t', str(duration + 0.5),
                '-shortest',
                '-movflags', '+faststart',
                temp_path
            ]
        else:
            base_cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'color=c=0x050510:size=1080x1920:rate=30',
                '-i', audio_path,
                '-c:v', 'libx264',
                '-profile:v', 'baseline',
                '-level', '3.0',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-t', str(duration + 0.5),
                '-shortest',
                '-movflags', '+faststart',
                temp_path
            ]

        code, out, err = run_ffmpeg(base_cmd)
        
        if code != 0 or not os.path.exists(temp_path):
            print(f"❌ Base video error:\n{err[-400:]}")
            return None

        print("✅ Base video ready")

        # Step 4: Subtitles
        print("📝 Subtitles add ho rahi hain...")
        final_path = add_subtitles_with_srt(temp_path, full_script, duration, output_path)

        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if final_path and os.path.exists(final_path):
            size_mb = os.path.getsize(final_path) / (1024*1024)
            print(f"✅ Video ready! ({size_mb:.1f} MB)")
            print(f"📁 {final_path}")
            return final_path

    except FileNotFoundError:
        print("❌ FFmpeg install nahi hai!")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_all_videos(scripts):
    created_videos = []
    for i, script in enumerate(scripts):
        print(f"\n{'='*50}")
        print(f"Video {i+1}/{len(scripts)} ban rahi hai...")
        video_path = create_shorts_video_ffmpeg(script, video_index=i)
        if video_path:
            created_videos.append({
                "path": video_path,
                "title": script.get("title", ""),
                "description": script.get("description", ""),
                "hashtags": script.get("hashtags", []),
            })
        time.sleep(1)

    print(f"\n🎉 {len(created_videos)}/{len(scripts)} videos ready!")
    with open("logs/created_videos.json", "w", encoding="utf-8") as f:
        json.dump(created_videos, f, ensure_ascii=False, indent=2)
    return created_videos


if __name__ == "__main__":
    test_script = {
        "title": "Bumrah ka Jaadu",
        "full_script": "Kya aap jaante hain Bumrah ke baare mein ye raaz? Bumrah ki yorker speed 145 kmph hai. Unhone 300 se zyada international wickets liye hain. Woh duniya ke number one bowler hain. India ke liye ye sabse khaas player hain. Agar ye nahi pata tha toh like zarur karo.",
        "description": "Cricket facts",
        "hashtags": ["#cricket", "#shorts", "#bumrah"],
        "topic_data": {"category": "sports"}
    }
    create_shorts_video_ffmpeg(test_script, 0)