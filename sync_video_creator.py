"""
sync_video_creator.py  -  NARRATION <-> VISUAL SYNC PIPELINE
=============================================================
Problem jo fix karta hai:
  Purane pipeline mein scenes ka time FIXED tha (~7s har scene) aur images
  generic Pexels stock thi, isliye bolna aur dikhna match nahi hota tha.

Ye kaise kaam karta hai:
  1. Script ko "beats" mein todta hai (1 beat = 1-2 chhote sentences, ~3-5 sec)
  2. HAR beat ki voice alag generate hoti hai  -> exact duration pata hoti hai
  3. Gemini se HAR beat ke liye uska apna visual plan banwata hai
     (ai image / stock photo / big-text card)
  4. Har scene ki length = us beat ki voice ki length  -> perfect sync
  5. Captions = jo actual bola ja raha hai (2-3 words at a time)
  6. Scenes ke beech crossfade, optional music ducking

Use:
    from sync_video_creator import create_synced_video
    path = create_synced_video(script_data, video_index=0)   # None agar fail

Env (optional):
    SYNC_MAX_AI_IMAGES=4        # ek video mein max AI images (cost control)
    SYNC_USE_AI_IMAGES=1        # 0 = AI image band (sirf stock + cards)
    SYNC_IMAGE_MODEL=gemini-2.5-flash-image
    CHANNEL_TAG="TEZ TAK"
    FONT_PATH=...               # custom font (optional)
"""

import os
import re
import io
import json
import random
import shutil
import subprocess
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────
# SETTINGS
# ──────────────────────────────────────────
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "").strip()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
CHANNEL_TAG = os.getenv("CHANNEL_TAG", "TEZ TAK")

W, H, FPS = 1080, 1920, 25
XFADE = 0.25          # crossfade seconds between scenes
BEAT_GAP = 0.12       # chhota pause har beat ke baad (breathing room)
MIN_BEAT_WORDS = 6
MAX_BEAT_WORDS = 15
MIN_BEAT_SECS = 1.2

MAX_AI_IMAGES = int(os.getenv("SYNC_MAX_AI_IMAGES", "4"))
USE_AI_IMAGES = os.getenv("SYNC_USE_AI_IMAGES", "1") == "1"
IMAGE_MODEL = os.getenv("SYNC_IMAGE_MODEL", "gemini-2.5-flash-image")

THEMES = {
    "facts":          {"a": (255, 200, 0),   "b": (16, 16, 40)},
    "story":          {"a": (230, 50, 50),   "b": (28, 8, 12)},
    "roast":          {"a": (50, 230, 130),  "b": (6, 22, 30)},
    "countdown":      {"a": (255, 110, 20),  "b": (30, 12, 6)},
    "news_breakdown": {"a": (60, 140, 255),  "b": (6, 16, 40)},
}

PHONETIC_FIXES = {
    "2011": "do hazaar gyarah", "2024": "do hazaar chaubees",
    "2025": "do hazaar pachchees", "2026": "do hazaar chhabbees",
    "1983": "unnis so tirasi",
    "IPL": "I P L", "ICC": "I C C", "T20": "T bees", "ODI": "O D I",
    "GST": "G S T", "RBI": "R B I", "FIR": "F I R",
}

_ai_disabled = False   # circuit breaker: ek baar AI image fail -> is run mein band


def _log(msg):
    print(msg, flush=True)


# ══════════════════════════════════════════
# SMALL HELPERS
# ══════════════════════════════════════════

def find_font():
    for p in [
        os.getenv("FONT_PATH", ""),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]:
        if p and os.path.exists(p):
            return p
    return None


def ff_path(p):
    """ffmpeg filter option ke liye path escape (Windows C: colon fix)."""
    return p.replace("\\", "/").replace(":", "\\:")


def run(cmd, timeout=600):
    r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return r.returncode == 0, r.stderr.decode("utf-8", errors="ignore")


def probe_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", path], capture_output=True, timeout=20)
        return float(r.stdout.decode().strip())
    except Exception:
        return 0.0


def spoken_version(text):
    """TTS ke liye text (pronunciation fixes)."""
    t = text
    for wrong, right in PHONETIC_FIXES.items():
        t = re.sub(rf"(?<![A-Za-z0-9]){re.escape(wrong)}(?![A-Za-z0-9])", right, t)
    t = re.sub(r"(\d+)\s*%", r"\1 pratishat", t)
    t = t.replace("₹", " rupaye ")
    t = re.sub(r"\bRs\.?\s*", "rupaye ", t)
    t = re.sub(r"#\w+", "", t)
    t = re.sub(r"[^\w\s.,!?।'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def caption_version(text):
    """Screen pe dikhane ke liye text (original digits waghera rakho)."""
    t = re.sub(r"#\w+", "", text)
    t = re.sub(r"[^\w\s.,!?%₹।'-]", "", t)
    return re.sub(r"\s+", " ", t).strip()


# ══════════════════════════════════════════
# 1. BEATS
# ══════════════════════════════════════════

def split_beats(script):
    """Script -> list of beats (1-2 sentences each)."""
    t = re.sub(r"#\w+", " ", script or "")
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return []

    sents = [s.strip() for s in re.split(r"(?<=[.!?।])\s+", t) if s.strip()]

    # bahut lambe sentence ko comma pe todo
    expanded = []
    for s in sents:
        if len(s.split()) > MAX_BEAT_WORDS + 5:
            parts = [p.strip() for p in re.split(r"(?<=,)\s+", s) if p.strip()]
            expanded.extend(parts if len(parts) > 1 else [s])
        else:
            expanded.append(s)

    beats, buf = [], ""
    for s in expanded:
        if not buf:
            buf = s
            continue
        wb, ws = len(buf.split()), len(s.split())
        if wb < MIN_BEAT_WORDS and wb + ws <= MAX_BEAT_WORDS + 4:
            buf = f"{buf} {s}"
        elif wb + ws <= MAX_BEAT_WORDS and wb < MAX_BEAT_WORDS - 4:
            buf = f"{buf} {s}"
        else:
            beats.append(buf)
            buf = s
    if buf:
        if beats and len(buf.split()) < 3:
            beats[-1] = f"{beats[-1]} {buf}"
        else:
            beats.append(buf)
    return beats


# ══════════════════════════════════════════
# 2. VISUAL PLAN (Gemini, beat-by-beat)
# ══════════════════════════════════════════

CTA_RE = re.compile(r"(subscribe|follow|like karo|comment karo|share karo)", re.I)


def extract_card_text(beat):
    """Beat se card ke liye 1-3 word keyword nikaalo (fallback)."""
    if CTA_RE.search(beat):
        return "LIKE  FOLLOW"
    m = re.search(r"\d[\d,\.]*\s*(?:crore|lakh|hazaar|million|billion|pratishat|%|percent|saal|log|rupaye)?",
                  beat, re.I)
    if m and len(m.group(0).strip()) >= 2:
        return m.group(0).strip().upper()[:18]
    words = [w for w in re.findall(r"[A-Za-z0-9]+", beat) if len(w) > 4]
    words = sorted(words, key=len, reverse=True)[:2]
    return " ".join(words).upper() if words else "BREAKING"


def fallback_shot(beat, i, pexels_queries):
    if CTA_RE.search(beat):
        return {"kind": "card", "card_text": "LIKE  FOLLOW"}
    if pexels_queries:
        return {"kind": "stock", "stock_query": pexels_queries[i % len(pexels_queries)],
                "card_text": extract_card_text(beat)}
    return {"kind": "card", "card_text": extract_card_text(beat)}


def _extract_json(text):
    if not text:
        return None
    t = text.strip()
    if "```json" in t:
        t = t.split("```json")[1].split("```")[0]
    elif "```" in t:
        t = t.split("```")[1].split("```")[0]
    s, e = t.find("{"), t.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        return json.loads(t[s:e + 1])
    except Exception:
        return None


def plan_visuals(beats, title, fmt, pexels_queries):
    """Har beat ke liye visual choose karo. Kabhi fail nahi hota (fallback)."""
    n = len(beats)
    shots = [fallback_shot(b, i, pexels_queries) for i, b in enumerate(beats)]

    try:
        from gemini_client import generate
        listing = "\n".join(f"{i}: {b}" for i, b in enumerate(beats))
        prompt = f"""You are the video editor of a Hindi news/story short. Each numbered line is ONE spoken beat (Roman Hindi).
For EVERY beat pick the visual that shows exactly what is being SAID in that beat, not the general topic.

VIDEO TITLE: {title}
FORMAT: {fmt}
BEATS:
{listing}

Return ONLY JSON:
{{"shots":[{{"i":0,"kind":"ai","image_prompt":"...","stock_query":"...","card_text":"..."}}]}}

RULES:
- Exactly {n} shots, i = 0..{n-1}, same order as beats.
- kind "ai": image_prompt in English, 25-40 words: concrete subject + place + action + mood + lighting. Documentary photo style.
  NEVER show recognisable real people's faces (use wide shots, silhouettes, backs of heads, hands, objects, crowds, landmarks, documents, screens, symbolic scenes).
  NEVER include text, letters, logos or flags with writing in the image.
- kind "stock": a real-world generic scene (crowd, road, court, market, hospital, stadium, farm...). stock_query = 2-4 English concrete nouns. No country name unless essential.
- kind "card": use when the beat is about a number, price, date, name, quote or the call-to-action. card_text = max 3 words, ROMAN letters/digits, UPPERCASE (e.g. "500 CRORE", "8 MARCH", "LIKE FOLLOW").
- Use kind "ai" for AT MOST {MAX_AI_IMAGES} beats: only the most important story moments. Beat 0 (the hook) should be "ai" or "card".
- Always fill stock_query and card_text too (fallbacks).
"""
        data = _extract_json(generate(prompt))
        got = (data or {}).get("shots", [])
        if isinstance(got, list):
            for item in got:
                try:
                    idx = int(item.get("i"))
                except Exception:
                    continue
                if 0 <= idx < n:
                    kind = str(item.get("kind", "")).lower()
                    if kind not in ("ai", "stock", "card"):
                        continue
                    shots[idx] = {
                        "kind": kind,
                        "image_prompt": str(item.get("image_prompt", "")).strip(),
                        "stock_query": str(item.get("stock_query", "")).strip(),
                        "card_text": str(item.get("card_text", "")).strip().upper()[:18]
                        or extract_card_text(beats[idx]),
                    }
            _log(f"  🧠 Visual plan: {len(got)}/{n} shots Gemini se aaye")
    except Exception as e:
        _log(f"  ⚠️ Visual plan fallback ({str(e)[:60]})")

    # sanity + AI cap
    ai_count = 0
    for i, s in enumerate(shots):
        if s["kind"] == "ai":
            if not s.get("image_prompt"):
                s["kind"] = "stock" if s.get("stock_query") else "card"
            else:
                ai_count += 1
                if ai_count > MAX_AI_IMAGES or not USE_AI_IMAGES:
                    s["kind"] = "stock" if s.get("stock_query") else "card"
        if s["kind"] == "stock" and not s.get("stock_query"):
            s["kind"] = "card"
        if not s.get("card_text"):
            s["card_text"] = extract_card_text(beats[i])
    return shots


# ══════════════════════════════════════════
# 3. VOICE PER BEAT (exact timing)
# ══════════════════════════════════════════

def _edge_tts_fallback(text, out_path):
    try:
        import asyncio
        import edge_tts

        async def go():
            c = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+5%", volume="+15%")
            await c.save(out_path)
        asyncio.run(go())
        return os.path.exists(out_path) and os.path.getsize(out_path) > 1500
    except Exception:
        return False


def synth_beat(text, out_path, fmt):
    spoken = spoken_version(text)
    if not spoken:
        return False
    try:
        from elevenlabs_voice import make_voice_with_fallback
        if make_voice_with_fallback(spoken, out_path, fmt):
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                return True
    except Exception as e:
        _log(f"    ⚠️ voice module: {str(e)[:70]}")
    return _edge_tts_fallback(spoken, out_path)


def to_wav_padded(src, dst):
    """mp3 -> exact wav (mono 44.1k) + chhota gap. Duration sample-exact."""
    ok, err = run(["ffmpeg", "-y", "-i", src, "-ar", "44100", "-ac", "1",
                   "-af", f"apad=pad_dur={BEAT_GAP}", dst], timeout=120)
    return ok and os.path.exists(dst)


def build_voice_track(wavs, out_wav):
    lst = out_wav.replace(".wav", "_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for w in wavs:
            f.write(f"file '{os.path.abspath(w).replace(chr(92), '/')}'\n")
    ok, err = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                   "-c", "copy", out_wav], timeout=120)
    try:
        os.remove(lst)
    except Exception:
        pass
    if not ok:
        _log(f"    ❌ voice concat: {err[-120:]}")
    return ok


# ══════════════════════════════════════════
# 4. IMAGES: ai / stock / card
# ══════════════════════════════════════════

def _save_as_jpeg(data, path):
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if min(im.size) < 500:
        return False
    im.save(path, "JPEG", quality=93)
    return True


def gen_ai_image(prompt, path):
    """Gemini image model (Nano Banana). Paid billing chahiye - fail hua to
    silently stock/card pe chala jayega."""
    global _ai_disabled
    if _ai_disabled or not USE_AI_IMAGES or not GEMINI_KEY:
        return False
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_KEY)
        full = (f"{prompt}. Vertical 9:16 composition, photorealistic documentary photograph, "
                f"natural lighting, no text, no letters, no watermark, no logos.")
        resp = None
        try:
            cfg = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"))
            resp = client.models.generate_content(model=IMAGE_MODEL, contents=full, config=cfg)
        except Exception as e1:
            if any(k in str(e1) for k in ("429", "RESOURCE_EXHAUSTED", "quota", "PERMISSION",
                                          "billing", "404", "NOT_FOUND")):
                raise
            cfg = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
            resp = client.models.generate_content(model=IMAGE_MODEL, contents=full, config=cfg)

        for cand in (resp.candidates or []):
            for part in (cand.content.parts or []):
                inline = getattr(part, "inline_data", None)
                if inline and inline.data:
                    if _save_as_jpeg(inline.data, path):
                        return True
        return False
    except Exception as e:
        msg = str(e)
        _log(f"    ⚠️ AI image fail: {msg[:90]}")
        if any(k in msg for k in ("429", "RESOURCE_EXHAUSTED", "quota", "PERMISSION",
                                  "billing", "404", "NOT_FOUND", "not found")):
            _ai_disabled = True
            _log("    ⏭️ AI image is run mein band (stock/cards use honge)")
        return False


def fetch_stock(query, path, used_ids):
    if not PEXELS_KEY or PEXELS_KEY == "your_pexels_api_key_here":
        return False
    words = query.split()
    attempts = [query] + ([" ".join(words[:2])] if len(words) > 2 else [])
    for q in attempts:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 20, "orientation": "portrait"},
                headers={"Authorization": PEXELS_KEY}, timeout=12)
            if r.status_code != 200:
                continue
            for ph in r.json().get("photos", []):
                if ph["id"] in used_ids:
                    continue
                if ph.get("width", 0) < 900:
                    continue
                url = ph["src"].get("large2x") or ph["src"].get("large")
                d = requests.get(url, timeout=25)
                if d.status_code == 200 and _save_as_jpeg(d.content, path):
                    used_ids.add(ph["id"])
                    return True
        except Exception:
            continue
    return False


def make_card_image(text, path, fmt, idx):
    """Branded big-text card (koi irrelevant photo nahi - seedha keyword)."""
    from PIL import Image, ImageDraw, ImageFont
    th = THEMES.get(fmt, THEMES["facts"])
    a, b = th["a"], th["b"]
    img = Image.new("RGB", (W, H), b)
    d = ImageDraw.Draw(img)
    for y in range(H):                      # vertical gradient (fast: line per row)
        k = 1 - abs(y / H - 0.5) * 2
        row = tuple(min(255, int(b[c] + a[c] * 0.22 * k)) for c in range(3))
        d.line([(0, y), (W, y)], fill=row)
    d.rectangle([0, 0, W, 14], fill=a)
    d.rectangle([0, H - 14, W, H], fill=a)
    d.ellipse([W - 420, -200, W + 200, 420], outline=a, width=6)
    d.ellipse([-260, H - 520, 300, H + 40], outline=a, width=6)

    fp = find_font()
    text = text.strip() or "BREAKING"
    words = text.split()
    lines = []
    cur = ""
    for w_ in words:
        if len(cur) + len(w_) + 1 <= 11:
            cur = f"{cur} {w_}".strip()
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    lines = lines[:3]
    # auto-fit: sabse chaudi line screen ke 68% se andar (zoom crop ke liye margin)
    size = 200
    font = ImageFont.load_default()
    while size > 50:
        font = ImageFont.truetype(fp, size) if fp else ImageFont.load_default()
        widest = max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines)
        if widest <= W * 0.68 or not fp:
            break
        size -= 6
    line_h = int(size * 1.2)
    y0 = H // 2 - (line_h * len(lines)) // 2 - 40
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = y0 + i * line_h
        d.text((x + 6, y + 6), ln, font=font, fill=(0, 0, 0))
        d.text((x, y), ln, font=font, fill=(255, 255, 255) if i else a)
    d.rectangle([W // 2 - 140, y0 + line_h * len(lines) + 30, W // 2 + 140,
                 y0 + line_h * len(lines) + 42], fill=a)
    img.save(path, "JPEG", quality=94)
    return True


def get_visual(i, shot, beat, work_dir, fmt, used_ids, cache):
    """Return (image_path, source_label). Kabhi None nahi - card guaranteed."""
    kind = shot["kind"]
    key = (kind, shot.get("image_prompt") if kind == "ai" else
           shot.get("stock_query") if kind == "stock" else shot.get("card_text"))
    if key in cache:
        return cache[key], f"{kind}(reuse)"

    path = f"{work_dir}/img_{i}.jpg"
    if kind == "ai" and gen_ai_image(shot["image_prompt"], path):
        cache[key] = path
        return path, "ai"
    if kind in ("ai", "stock") and shot.get("stock_query") and fetch_stock(shot["stock_query"], path, used_ids):
        cache[key] = path
        return path, "stock"
    make_card_image(shot.get("card_text") or extract_card_text(beat), path, fmt, i)
    cache[(("card"), shot.get("card_text"))] = path
    return path, "card"


# ══════════════════════════════════════════
# 5. SCENE RENDER (motion + captions)
# ══════════════════════════════════════════

def motion_filter(idx, frames):
    N = max(frames, 2)
    up = "scale=3240:5760:force_original_aspect_ratio=increase,crop=3240:5760,setsar=1"
    common = f"d={N}:s={W}x{H}:fps={FPS}"
    m = idx % 6
    if m == 0:    # slow zoom in (center)
        zp = f"zoompan=z='1+0.14*on/{N}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':{common}"
    elif m == 1:  # pan left -> right
        zp = f"zoompan=z='1.12':x='(iw-iw/zoom)*on/{N}':y='(ih-ih/zoom)/2':{common}"
    elif m == 2:  # zoom in towards upper part
        zp = f"zoompan=z='1+0.16*on/{N}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.30':{common}"
    elif m == 3:  # slow zoom out
        zp = f"zoompan=z='1.14-0.14*on/{N}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':{common}"
    elif m == 4:  # pan right -> left
        zp = f"zoompan=z='1.12':x='(iw-iw/zoom)*(1-on/{N})':y='(ih-ih/zoom)/2':{common}"
    else:         # tilt down
        zp = f"zoompan=z='1.12':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*on/{N}':{common}"
    return f"{up},{zp}"


def caption_chunks(text, speak_secs):
    """Beat ke words -> [(chunk_text, t_start, t_end)] (2-3 words each)."""
    words = caption_version(text).split()
    if not words:
        return []
    chunks, cur = [], []
    for w_ in words:
        cur.append(w_)
        if len(cur) >= 3 or len(" ".join(cur)) >= 18 or re.search(r"[.!?,।]$", w_):
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    total = sum(max(len(c), 4) for c in chunks)
    out, t = [], 0.0
    for c in chunks:
        share = speak_secs * max(len(c), 4) / total
        out.append((c, t, t + share))
        t += share
    return out


def render_scene(img, beat, shot_idx, clip_len, speak_secs, fmt, work_dir, out_path, first):
    frames = int(round(clip_len * FPS))
    th = THEMES.get(fmt, THEMES["facts"])
    accent = "%02X%02X%02X" % th["a"]
    font = find_font()
    fparam = f":fontfile='{ff_path(font)}'" if font else ""

    vf = [motion_filter(shot_idx, frames)]

    # top tag
    tag = "BREAKING" if fmt == "news_breakdown" else CHANNEL_TAG
    tag_file = f"{work_dir}/tag_{shot_idx}.txt"
    Path(tag_file).write_text(tag, encoding="utf-8")
    vf.append(f"drawtext=textfile='{ff_path(tag_file)}'{fparam}:fontsize=44:fontcolor=white"
              f":x=48:y=110:box=1:boxcolor=0x{accent}@0.95:boxborderw=16:expansion=none")

    # captions (jo bola ja raha hai - chunk by chunk)
    chunks = caption_chunks(beat, speak_secs)
    for k, (txt, a, b) in enumerate(chunks):
        cf = f"{work_dir}/cap_{shot_idx}_{k}.txt"
        Path(cf).write_text(txt.upper(), encoding="utf-8")
        color = "yellow" if re.search(r"\d", txt) else "white"
        end = b if k < len(chunks) - 1 else clip_len
        vf.append(
            f"drawtext=textfile='{ff_path(cf)}'{fparam}:fontsize=78:fontcolor={color}"
            f":borderw=7:bordercolor=black:shadowx=3:shadowy=3"
            f":x=(w-text_w)/2:y=h*0.66:expansion=none"
            f":enable='between(t,{a:.3f},{end:.3f})'")

    cmd = ["ffmpeg", "-y", "-i", img, "-vf", ",".join(vf),
           "-frames:v", str(frames), "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
           "-pix_fmt", "yuv420p", "-an", out_path]
    ok, err = run(cmd, timeout=300)
    if not ok:
        _log(f"    ❌ scene render: {err[-200:]}")
    return ok and os.path.exists(out_path) and os.path.getsize(out_path) > 5000


# ══════════════════════════════════════════
# 6. FINAL MERGE (xfade + audio/music)
# ══════════════════════════════════════════

def find_music():
    for d in ("assets/music", "music"):
        files = []
        for ext in ("mp3", "wav", "m4a", "ogg"):
            files += list(Path(d).glob(f"*.{ext}"))
        if files:
            return str(random.choice(files))
    return None


def merge_all(scene_files, beat_durs, voice_wav, out_path):
    n = len(scene_files)
    total = sum(beat_durs)

    inputs = []
    for f in scene_files:
        inputs += ["-i", f]
    inputs += ["-i", voice_wav]
    music = find_music()
    if music:
        inputs += ["-stream_loop", "-1", "-i", music]

    # video chain: xfade with exact offsets
    if n == 1:
        vchain = "[0:v]null[vout]"
    else:
        parts, acc, offset = [], "[0:v]", 0.0
        for k in range(1, n):
            offset += beat_durs[k - 1]
            lbl = "[vout]" if k == n - 1 else f"[x{k}]"
            parts.append(f"{acc}[{k}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}{lbl}")
            acc = lbl
        vchain = ";".join(parts)

    a_idx = n
    def build(with_music):
        if with_music:
            m_idx = n + 1
            achain = (f"[{a_idx}:a]asplit=2[vo1][vo2];"
                      f"[{m_idx}:a]atrim=0:{total + 1:.2f},volume=0.30[mus];"
                      f"[mus][vo1]sidechaincompress=threshold=0.04:ratio=10:attack=15:release=350[duck];"
                      f"[duck][vo2]amix=inputs=2:duration=shortest:dropout_transition=0,"
                      f"highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=11[aout]")
        else:
            achain = f"[{a_idx}:a]highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=11[aout]"
        return ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", f"{vchain};{achain}",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-t", f"{total:.3f}", "-movflags", "+faststart", out_path]

    if music:
        ok, err = run(build(True), timeout=900)
        if ok and os.path.exists(out_path) and os.path.getsize(out_path) > 200000:
            return True
        _log(f"    ⚠️ music mix fail, bina music: {err[-120:]}")
        # music input hata ke retry
        inputs[:] = [x for x in inputs][: 2 * n + 2]
    ok, err = run(build(False), timeout=900)
    if not ok:
        _log(f"    ❌ merge: {err[-250:]}")
    return ok and os.path.exists(out_path) and os.path.getsize(out_path) > 200000


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def create_synced_video(script_data, video_index=0):
    global _ai_disabled
    title = script_data.get("title", "video")
    fmt = script_data.get("format", "facts")
    full_script = script_data.get("full_script", "")
    pexels_queries = script_data.get("pexels_queries", []) or []

    safe = re.sub(r"[^\w\s-]", "", title.encode("ascii", "ignore").decode())[:18].strip() or f"v{video_index}"
    work_dir = f"assets/sync_{video_index}"
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/auto_{video_index}_{safe}.mp4"

    _log(f"\n{'=' * 55}\n🎬 SYNC [{fmt.upper()}] {title[:50]}\n{'=' * 55}")

    # 1. beats
    beats = split_beats(full_script)
    if len(beats) < 3:
        _log("  ❌ Script bahut chhota - beats nahi bane")
        return None
    _log(f"  📌 {len(beats)} beats")

    # 2. visual plan
    _log("\n🧠 Visual plan (beat-by-beat)...")
    shots = plan_visuals(beats, title, fmt, pexels_queries)

    # 3. voice per beat
    _log("\n🎤 Voice (beat-by-beat, exact timing)...")
    wavs, durs = [], []
    for i, b in enumerate(beats):
        mp3 = f"{work_dir}/beat_{i}.mp3"
        wav = f"{work_dir}/beat_{i}.wav"
        if not synth_beat(b, mp3, fmt) or not to_wav_padded(mp3, wav):
            _log(f"  ❌ Beat {i} voice fail - sync mode band")
            return None
        d = probe_duration(wav)
        if d < MIN_BEAT_SECS:
            d = MIN_BEAT_SECS
        wavs.append(wav)
        durs.append(d)
        _log(f"  ✅ beat {i + 1}/{len(beats)}: {d:.1f}s")
        time.sleep(0.3)

    voice_wav = f"{work_dir}/voice.wav"
    if not build_voice_track(wavs, voice_wav):
        return None
    audio_len = probe_duration(voice_wav)
    total = sum(durs)
    if abs(audio_len - total) > 0.4:      # safety: real audio length ko truth maano
        _log(f"  ⚠️ audio {audio_len:.2f}s vs beats {total:.2f}s")
        durs[-1] = max(MIN_BEAT_SECS, durs[-1] + (audio_len - total))
    _log(f"  ⏱️ total {sum(durs):.1f}s")

    # 4. visuals + scenes
    _log("\n🖼️  Scenes (har beat ka apna visual)...")
    used_ids, cache, scene_files, plan_dump = set(), {}, [], []
    for i, (b, shot) in enumerate(zip(beats, shots)):
        img, src = get_visual(i, shot, b, work_dir, fmt, used_ids, cache)
        last = i == len(beats) - 1
        clip_len = durs[i] + (0 if last else XFADE)
        scene = f"{work_dir}/scene_{i}.mp4"
        speak = max(durs[i] - BEAT_GAP, 0.8)
        if not render_scene(img, b, i, clip_len, speak, fmt, work_dir, scene, i == 0):
            _log(f"  ❌ scene {i + 1} fail")
            return None
        scene_files.append(scene)
        scene_label = shot.get("image_prompt") or shot.get("stock_query") or shot.get("card_text")
        _log(f"  ✅ {i + 1:>2}. [{src:<11}] {durs[i]:.1f}s | {b[:38]}... -> {str(scene_label)[:34]}")
        plan_dump.append({"i": i, "text": b, "secs": round(durs[i], 2), "source": src, "shot": shot})

    # 5. merge
    _log(f"\n🎞️  Merging {len(scene_files)} scenes + voice...")
    if not merge_all(scene_files, durs, voice_wav, out_path):
        return None

    vdur = probe_duration(out_path)
    _log(f"  📏 video {vdur:.2f}s vs voice {sum(durs):.2f}s")
    try:
        Path(f"{work_dir}/plan.json").write_text(
            json.dumps(plan_dump, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    mb = os.path.getsize(out_path) / 1024 / 1024
    _log(f"\n✅ {mb:.1f} MB -> {out_path}")
    return out_path


if __name__ == "__main__":
    demo = {
        "title": "Demo sync video",
        "format": "news_breakdown",
        "full_script": ("Badi khabar! Sarkar ne aaj petrol ki keemat mein paanch rupaye ki katauti ka elaan kiya. "
                        "Ye faisla raat ko cabinet ki meeting mein hua. "
                        "Ab aam aadmi ko har mahine hazaaron rupaye ki bachat hogi. "
                        "Lekin vipaksh ne isse chunavi stunt bataya hai. "
                        "Like karo aur channel follow karo aisi khabron ke liye!"),
        "pexels_queries": ["petrol pump india", "cabinet meeting", "indian family market"],
    }
    print(create_synced_video(demo, 99))
