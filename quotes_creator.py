"""
quotes_creator.py  -  MOTIVATIONAL QUOTES VIDEO (India)
=========================================================
Kyun curated bank hai, AI se free-form quotes nahi banwaye:
  Agar Gemini se "Kalam ka quote do" bolo, wo kabhi kabhi ek quote
  BANA (hallucinate) kar dega jo unhone kabhi kaha hi nahi - aur wo
  ek real, named insaan ke naam se jhooth ban jaayega. Isliye yahan
  sirf WELL-DOCUMENTED, widely verified quotes ka apna curated bank
  hai. AI sirf HOOK aur CONTEXT likhta hai (quote khud nahi).

Video structure (4 beats):
  1. HOOK       - curiosity wala 1-liner (AI likhta hai, quote nahi)
  2. QUOTE      - premium Devanagari card, poora hold hota hai (asli quote)
  3. AUTHOR     - kaun bola, chhota context (curated bank se)
  4. CTA        - follow/like

Real logon ka AI face NAHI banaya jaata - sirf symbolic/thematic stock
visuals (rocket, charkha, tiranga, diya, granth...) use hote hain.

Use:
    from quotes_creator import create_quote_video, QUOTE_BANK
    path = create_quote_video(quote_id=None, video_index=0)   # None agar fail
"""

import os
import re
import json
import random
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from sync_video_creator import (
    W, H, FPS, XFADE, BEAT_GAP,
    OUTPUT_DIR, CHANNEL_TAG,
    find_font, ff_path, run, probe_duration,
    synth_beat, to_wav_padded, build_voice_track,
    motion_filter, caption_chunks, caption_version,
    fetch_stock, merge_all, find_music, _save_as_jpeg,
)

# ──────────────────────────────────────────
DEVA_CANDIDATES = [
    os.getenv("DEVANAGARI_FONT_PATH", ""),
    "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
]


def find_devanagari_font():
    for p in DEVA_CANDIDATES:
        if p and os.path.exists(p):
            return p
    # last resort: glob search
    for hit in Path("/usr/share/fonts").rglob("*[Dd]evanagari*.ttf"):
        return str(hit)
    return None


CATEGORY_THEME = {
    "freedom":  {"a": (255, 153, 51),  "b": (12, 8, 4),   "label": "AZAADI KI SOCH"},
    "business": {"a": (255, 200, 60),  "b": (8, 12, 22),  "label": "SUCCESS MANTRA"},
    "chanakya": {"a": (210, 160, 60),  "b": (20, 8, 6),   "label": "CHANAKYA NEETI"},
    "gita":     {"a": (255, 175, 60),  "b": (6, 10, 26),  "label": "GEETA GYAN"},
}

# ══════════════════════════════════════════
# CURATED QUOTE BANK - verified, well-documented only
# ══════════════════════════════════════════

QUOTE_BANK = [
    {
        "id": "kalam_1", "category": "business",
        "author_hi": "डॉ. ए.पी.जे. अब्दुल कलाम", "author_roman": "Doctor A P J Abdul Kalam",
        "author_context": "Bharat ke Missile Man, jo President bhi bane",
        "hi": "सपना वो नहीं जो आप सोते हुए देखते हैं, सपना वो है जो आपको सोने ही नहीं देता।",
        "roman": "Sapna wo nahi jo aap sote hue dekhte hain... sapna wo hai jo aapko sone hi nahi deta.",
        "hook": "Jo log bade sapne dekhte hain, unki raatein alag hoti hain...",
        "hook_visual": "person looking at stars night sky india",
        "author_visual": "rocket launch space india",
    },
    {
        "id": "kalam_2", "category": "business",
        "author_hi": "डॉ. ए.पी.जे. अब्दुल कलाम", "author_roman": "Doctor A P J Abdul Kalam",
        "author_context": "Bharat ke Missile Man, jo President bhi bane",
        "hi": "अगर आप सूरज की तरह चमकना चाहते हैं, तो पहले सूरज की तरह जलना सीखो।",
        "roman": "Agar aap sooraj ki tarah chamakna chahte hain... to pehle sooraj ki tarah jalna seekho.",
        "hook": "Chamakne se pehle, ek cheez seekhni padti hai...",
        "hook_visual": "sunrise mountains india golden light",
        "author_visual": "science laboratory research india",
    },
    {
        "id": "kalam_3", "category": "business",
        "author_hi": "डॉ. ए.पी.जे. अब्दुल कलाम", "author_roman": "Doctor A P J Abdul Kalam",
        "author_context": "Bharat ke Missile Man, jo President bhi bane",
        "hi": "उत्कृष्टता एक सतत प्रक्रिया है, कोई संयोग नहीं।",
        "roman": "Utkrishtata ek satat prakriya hai... koi sanyog nahi.",
        "hook": "Kya safalta kismat hoti hai, ya kuch aur...",
        "hook_visual": "student studying late night india",
        "author_visual": "indian flag hoisting proud",
    },
    {
        "id": "vivekananda_1", "category": "gita",
        "author_hi": "स्वामी विवेकानंद", "author_roman": "Swami Vivekananda",
        "author_context": "Jinhone Chicago mein Bharat ka gyan poori duniya ko dikhaya",
        "hi": "उठो, जागो और तब तक मत रुको जब तक लक्ष्य प्राप्त न हो जाए।",
        "roman": "Utho, jaago... aur tab tak mat ruko jab tak lakshya prapt na ho jaaye.",
        "hook": "Ek sadhu ne poori duniya ko sirf teen shabdon mein jagaya tha...",
        "hook_visual": "himalaya sunrise monk india",
        "author_visual": "temple bells morning india",
    },
    {
        "id": "vivekananda_2", "category": "gita",
        "author_hi": "स्वामी विवेकानंद", "author_roman": "Swami Vivekananda",
        "author_context": "Jinhone Chicago mein Bharat ka gyan poori duniya ko dikhaya",
        "hi": "सारी शक्तियां पहले से ही हमारे भीतर हैं, हमने खुद अपनी आंखों पर हाथ रखकर अंधेरे का रोना रोया है।",
        "roman": "Saari shaktiyan pehle se hi hamare bheetar hain... hum khud apni aankhon par haath rakh kar andhere ka rona rote hain.",
        "hook": "Taakat kahin bahar nahi milti... wo hamesha ek jagah chhupi hoti hai",
        "hook_visual": "person meditation sunrise silhouette",
        "author_visual": "diya lamp light dark temple",
    },
    {
        "id": "gandhi_1", "category": "freedom",
        "author_hi": "महात्मा गांधी", "author_roman": "Mahatma Gandhi",
        "author_context": "Rashtrapita, jinhone ahimsa se azaadi dilayi",
        "hi": "वह परिवर्तन खुद बनो, जो तुम दुनिया में देखना चाहते हो।",
        "roman": "Wo parivartan khud bano... jo tum duniya mein dekhna chahte ho.",
        "hook": "Duniya badalne ka sabse pehla kadam kya hai...",
        "hook_visual": "charkha spinning wheel india",
        "author_visual": "indian village morning sunrise",
    },
    {
        "id": "gandhi_2", "category": "freedom",
        "author_hi": "महात्मा गांधी", "author_roman": "Mahatma Gandhi",
        "author_context": "Rashtrapita, jinhone ahimsa se azaadi dilayi",
        "hi": "शक्ति शरीर की क्षमता से नहीं, बल्कि अटूट इच्छाशक्ति से आती है।",
        "roman": "Shakti shareer ki kshamata se nahi... balki atoot ichchhashakti se aati hai.",
        "hook": "Sabse takatwar insaan wo nahi jiska badan mazboot ho...",
        "hook_visual": "old man walking determined india road",
        "author_visual": "sabarmati river peaceful morning",
    },
    {
        "id": "bhagat_singh_1", "category": "freedom",
        "author_hi": "भगत सिंह", "author_roman": "Bhagat Singh",
        "author_context": "23 saal ki umar mein desh ke liye phaansi chadh gaye",
        "hi": "वे मुझे मार सकते हैं, लेकिन मेरे विचारों को नहीं मार सकते।",
        "roman": "Ve mujhe maar sakte hain... lekin mere vicharon ko nahi maar sakte.",
        "hook": "23 saal ki umar mein ek ladke ne aisi baat kahi thi...",
        "hook_visual": "indian flag waving fort",
        "author_visual": "old jail cell historic india",
    },
    {
        "id": "bose_1", "category": "freedom",
        "author_hi": "सुभाष चंद्र बोस", "author_roman": "Subhas Chandra Bose",
        "author_context": "Netaji, jinhone Azad Hind Fauj banayi thi",
        "hi": "तुम मुझे खून दो, मैं तुम्हें आज़ादी दूंगा।",
        "roman": "Tum mujhe khoon do... main tumhein azaadi doonga.",
        "hook": "1944 mein ek bhaashan ne poori fauj ko khada kar diya tha...",
        "hook_visual": "crowd marching indian flag historic",
        "author_visual": "red fort delhi sunrise",
    },
    {
        "id": "tata_1", "category": "business",
        "author_hi": "रतन टाटा", "author_roman": "Ratan Tata",
        "author_context": "Tata Group ke chairman, jinki simplicity duniya bhar mein jaani jaati hai",
        "hi": "मैं सही फैसले लेने में विश्वास नहीं रखता, मैं फैसला लेता हूं और फिर उसे सही साबित करता हूं।",
        "roman": "Main sahi faisle lene mein vishwas nahi rakhta... main faisla leta hoon aur phir use sahi sabit karta hoon.",
        "hook": "Ek business legend ne apni success ka raaz kuch alag hi bataya tha...",
        "hook_visual": "modern office building mumbai skyline",
        "author_visual": "factory industry india workers",
    },
    {
        "id": "ambani_1", "category": "business",
        "author_hi": "धीरूभाई अंबानी", "author_roman": "Dhirubhai Ambani",
        "author_context": "Reliance ke sansthapak, jinhone chhote gaon se safar shuru kiya tha",
        "hi": "सिर्फ सपने मत देखो, बड़े सपने देखो। और सिर्फ बड़े सपने मत देखो, उन सपनों को अपने कर्मों से सच करो।",
        "roman": "Sirf sapne mat dekho, bade sapne dekho... aur un sapnon ko apne karmon se sach karo.",
        "hook": "Ek chhote gaon se aane wale ladke ne aisi baat sikhayi thi...",
        "hook_visual": "petrol refinery industry night india",
        "author_visual": "busy market street india",
    },
    {
        "id": "kalpana_1", "category": "business",
        "author_hi": "कल्पना चावला", "author_roman": "Kalpana Chawla",
        "author_context": "Antariksh mein jaane wali pehli Bharatiya mahila",
        "hi": "सपनों से सफलता तक का रास्ता ज़रूर होता है।",
        "roman": "Sapno se safalta tak ka raasta zaroor hota hai.",
        "hook": "Ek chhote se Haryana ke shehar se antariksh tak ka safar...",
        "hook_visual": "night sky stars space india",
        "author_visual": "rocket launch space india",
    },
    {
        "id": "chanakya_1", "category": "chanakya",
        "author_hi": "चाणक्य नीति", "author_roman": "Chanakya Neeti",
        "author_context": "Prachin Bharat ke mahaan neeti-shastri ka gyan",
        "hi": "जो व्यक्ति जिस काम को शुरू करता है, उसे बीच में मत छोड़ो। जो निष्ठा से काम करता है, वही सबसे सुखी होता है।",
        "roman": "Jo kaam shuru karo, use beech mein mat chodo... jo nishtha se kaam karta hai, wahi sabse sukhi hota hai.",
        "hook": "Hazaaron saal purani ek neeti aaj bhi utni hi sach hai...",
        "hook_visual": "ancient scroll ink pen india",
        "author_visual": "old library books ancient india",
    },
    {
        "id": "chanakya_2", "category": "chanakya",
        "author_hi": "चाणक्य नीति", "author_roman": "Chanakya Neeti",
        "author_context": "Prachin Bharat ke mahaan neeti-shastri ka gyan",
        "hi": "बहुत ज़्यादा ईमानदार मत बनो। सीधे पेड़ सबसे पहले काटे जाते हैं।",
        "roman": "Bahut zyada eemaandaar mat bano... seedhe ped sabse pehle kaate jaate hain.",
        "hook": "Chanakya ne ek ajeeb lekin gehri baat kahi thi...",
        "hook_visual": "forest trees tall india",
        "author_visual": "ancient temple pillars india",
    },
    {
        "id": "chanakya_3", "category": "chanakya",
        "author_hi": "चाणक्य नीति", "author_roman": "Chanakya Neeti",
        "author_context": "Prachin Bharat ke mahaan neeti-shastri ka gyan",
        "hi": "विद्या ही सबसे अच्छी मित्र है। शिक्षित व्यक्ति हर जगह सम्मान पाता है।",
        "roman": "Vidya hi sabse achi mitra hai... shikshit vyakti har jagah samman paata hai.",
        "hook": "Chanakya ke hisaab se sabse bada dost kaun hai...",
        "hook_visual": "books library student india",
        "author_visual": "old manuscript sanskrit india",
    },
    {
        "id": "gita_1", "category": "gita",
        "author_hi": "भगवद्गीता", "author_roman": "Bhagavad Gita",
        "author_context": "Karm Yoga ka mool updesh",
        "hi": "कर्म करने में ही तुम्हारा अधिकार है, फल में कभी नहीं।",
        "roman": "Karm karne mein hi tumhara adhikaar hai... fal mein kabhi nahi.",
        "hook": "Geeta ka ek shlok aaj bhi har stress ka jawab hai...",
        "hook_visual": "sunrise river temple india peaceful",
        "author_visual": "diya lamp temple evening india",
    },
    {
        "id": "gita_2", "category": "gita",
        "author_hi": "भगवद्गीता", "author_roman": "Bhagavad Gita",
        "author_context": "Sukh-dukh ke prati santulan ka updesh",
        "hi": "सुख-दुख आते जाते रहते हैं, जैसे सर्दी-गर्मी। इन्हें सहन करना सीखो।",
        "roman": "Sukh dukh aate jaate rehte hain... jaise sardi garmi. Inhe sahan karna seekho.",
        "hook": "Dukh kabhi permanent nahi hota... Geeta ye baat kehti hai",
        "hook_visual": "changing seasons nature india",
        "author_visual": "old temple stone carving india",
    },
    {
        "id": "gita_3", "category": "gita",
        "author_hi": "भगवद्गीता", "author_roman": "Bhagavad Gita",
        "author_context": "Mann ko sadhne ka updesh",
        "hi": "अपने आप को अपने ही मन से ऊपर उठाओ, क्योंकि मन ही अपना मित्र है और मन ही अपना शत्रु।",
        "roman": "Apne aap ko apne hi mann se oopar uthao... kyunki mann hi apna mitra hai aur mann hi apna shatru.",
        "hook": "Tumhara sabse bada dost aur dushman, dono ek hi hai...",
        "hook_visual": "calm lake reflection mountains india",
        "author_visual": "peaceful meditation silhouette sunrise",
    },
]

CTA_LINES = [
    "Aisi hi baatein roz chahiye to FOLLOW kar lo.",
    "Ye baat kisi ko yaad dilani ho to SHARE kar do.",
    "Roz ek naya vichaar chahiye to abhi FOLLOW karo.",
]


def load_used(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return []


def pick_quote(quote_id=None, used_file="logs/used_quotes.json"):
    if quote_id:
        for q in QUOTE_BANK:
            if q["id"] == quote_id:
                return q
    used = load_used(used_file)
    unused = [q for q in QUOTE_BANK if q["id"] not in used]
    if not unused:
        unused = QUOTE_BANK.copy()
        used = []
    q = random.choice(unused)
    used.append(q["id"])
    try:
        Path("logs").mkdir(exist_ok=True)
        json.dump(used, open(used_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except Exception:
        pass
    return q


# ══════════════════════════════════════════
# QUOTE CARD (premium, Devanagari)
# ══════════════════════════════════════════

def wrap_devanagari(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = f"{cur} {w_}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def make_quote_card(q, path):
    from PIL import Image, ImageDraw, ImageFont

    th = CATEGORY_THEME.get(q["category"], CATEGORY_THEME["business"])
    a, b = th["a"], th["b"]
    img = Image.new("RGB", (W, H), b)
    d = ImageDraw.Draw(img)

    for y in range(H):
        k = 1 - abs(y / H - 0.42) * 1.3
        k = max(0, min(1, k))
        row = tuple(min(255, int(b[c] + a[c] * 0.16 * k)) for c in range(3))
        d.line([(0, y), (W, y)], fill=row)

    # frame + corner accents
    d.rectangle([36, 36, W - 36, H - 36], outline=a, width=3)
    for cx, cy, sx, sy in [(36, 36, 1, 1), (W - 36, 36, -1, 1), (36, H - 36, 1, -1), (W - 36, H - 36, -1, -1)]:
        d.line([(cx, cy), (cx + 70 * sx, cy)], fill=a, width=6)
        d.line([(cx, cy), (cx, cy + 70 * sy)], fill=a, width=6)

    # category tag
    tag_font = ImageFont.truetype(find_font(), 34) if find_font() else ImageFont.load_default()
    tag = th["label"]
    tw = d.textbbox((0, 0), tag, font=tag_font)[2]
    d.rectangle([(W - tw) / 2 - 30, 86, (W + tw) / 2 + 30, 148], outline=a, width=2)
    d.text(((W - tw) / 2, 96), tag, font=tag_font, fill=a)

    # giant quotation mark
    deva = find_devanagari_font()
    qmark_font = ImageFont.truetype(find_font(), 230) if find_font() else ImageFont.load_default()
    d.text((W / 2 - 62, 165), '"', font=qmark_font, fill=(*a, 255) if False else a)

    # quote text (Devanagari), auto-fit
    quote = q["hi"]
    max_w = W * 0.80
    size = 92
    lines, font = [], None
    while size > 46:
        font = ImageFont.truetype(deva, size) if deva else ImageFont.load_default()
        lines = wrap_devanagari(d, quote, font, max_w)
        total_h = len(lines) * int(size * 1.55)
        if total_h <= H * 0.46 and len(lines) <= 6:
            break
        size -= 4

    line_h = int(size * 1.55)
    y0 = H * 0.40 - (line_h * len(lines)) / 2
    for i, ln in enumerate(lines):
        tw = d.textbbox((0, 0), ln, font=font)[2]
        x = (W - tw) / 2
        y = y0 + i * line_h
        d.text((x + 4, y + 4), ln, font=font, fill=(0, 0, 0))
        d.text((x, y), ln, font=font, fill=(255, 250, 235))

    # divider
    dy = y0 + len(lines) * line_h + 34
    d.line([(W / 2 - 90, dy), (W / 2 + 90, dy)], fill=a, width=4)

    # author (Devanagari)
    au_font = ImageFont.truetype(deva, 56) if deva else ImageFont.load_default()
    au = f"— {q['author_hi']}"
    atw = d.textbbox((0, 0), au, font=au_font)[2]
    d.text(((W - atw) / 2, dy + 26), au, font=au_font, fill=a)

    # channel tag bottom
    cfont = ImageFont.truetype(find_font(), 34) if find_font() else ImageFont.load_default()
    ctw = d.textbbox((0, 0), CHANNEL_TAG, font=cfont)[2]
    d.text(((W - ctw) / 2, H - 110), CHANNEL_TAG, font=cfont, fill=a)

    img.save(path, "JPEG", quality=95)
    return True


def make_cta_card(q, text, path):
    """Dedicated follow/share card - quote card se alag dikhta hai."""
    from PIL import Image, ImageDraw, ImageFont
    th = CATEGORY_THEME.get(q["category"], CATEGORY_THEME["business"])
    a, b = th["a"], th["b"]
    img = Image.new("RGB", (W, H), b)
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = 1 - abs(y / H - 0.5) * 2
        row = tuple(min(255, int(b[c] + a[c] * 0.24 * max(0, k))) for c in range(3))
        d.line([(0, y), (W, y)], fill=row)
    d.ellipse([W / 2 - 260, H / 2 - 460, W / 2 + 260, H / 2 + 60], outline=a, width=5)

    fp = find_font()
    big = ImageFont.truetype(fp, 130) if fp else ImageFont.load_default()
    word = "FOLLOW" if "FOLLOW" in text.upper() else "SHARE"
    tw = d.textbbox((0, 0), word, font=big)[2]
    d.text(((W - tw) / 2, H / 2 - 300), word, font=big, fill=a)

    sub_font = ImageFont.truetype(fp, 46) if fp else ImageFont.load_default()
    lines = wrap_devanagari(d, text.upper(), sub_font, W * 0.7)  # roman text, Latin font
    for i, ln in enumerate(lines):
        tw2 = d.textbbox((0, 0), ln, font=sub_font)[2]
        d.text(((W - tw2) / 2, H / 2 - 120 + i * 60), ln, font=sub_font, fill=(240, 240, 240))

    d.rectangle([W / 2 - 70, H / 2 + 40, W / 2 + 70, H / 2 + 52], fill=a)
    img.save(path, "JPEG", quality=94)
    return True


def make_author_card(q, path):
    """Author naam + context, symbolic photo ke upar overlay hota hai render_beat mein,
    is card ka use sirf tab jab stock na mile."""
    from PIL import Image, ImageDraw, ImageFont
    th = CATEGORY_THEME.get(q["category"], CATEGORY_THEME["business"])
    a, b = th["a"], th["b"]
    img = Image.new("RGB", (W, H), b)
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = 1 - abs(y / H - 0.5) * 2
        row = tuple(min(255, int(b[c] + a[c] * 0.20 * max(0, k))) for c in range(3))
        d.line([(0, y), (W, y)], fill=row)
    deva = find_devanagari_font()
    f1 = ImageFont.truetype(deva, 78) if deva else ImageFont.load_default()
    au = q["author_hi"]
    tw = d.textbbox((0, 0), au, font=f1)[2]
    d.text(((W - tw) / 2, H / 2 - 60), au, font=f1, fill=(255, 250, 235))
    d.line([(W / 2 - 100, H / 2 + 60), (W / 2 + 100, H / 2 + 60)], fill=a, width=4)
    img.save(path, "JPEG", quality=94)
    return True


# ══════════════════════════════════════════
# SCENE RENDER (reuses sync_video_creator's motion + caption style)
# ══════════════════════════════════════════

def render_beat_scene(img, caption_text, shot_idx, clip_len, speak_secs,
                       work_dir, out_path, show_caption=True, tag_text=None):
    frames = int(round(clip_len * FPS))
    font = find_font()
    fparam = f":fontfile='{ff_path(font)}'" if font else ""
    vf = [motion_filter(shot_idx, frames)]

    if tag_text:
        tag_file = f"{work_dir}/tag_{shot_idx}.txt"
        Path(tag_file).write_text(tag_text, encoding="utf-8")
        vf.append(f"drawtext=textfile='{ff_path(tag_file)}'{fparam}:fontsize=40:fontcolor=white"
                  f":x=48:y=110:box=1:boxcolor=0x2A2A2A@0.85:boxborderw=14:expansion=none")

    if show_caption and caption_text:
        chunks = caption_chunks(caption_text, speak_secs)
        for k, (txt, a_, b_) in enumerate(chunks):
            cf = f"{work_dir}/cap_{shot_idx}_{k}.txt"
            Path(cf).write_text(txt.upper(), encoding="utf-8")
            end = b_ if k < len(chunks) - 1 else clip_len
            vf.append(
                f"drawtext=textfile='{ff_path(cf)}'{fparam}:fontsize=74:fontcolor=white"
                f":borderw=7:bordercolor=black:shadowx=3:shadowy=3"
                f":x=(w-text_w)/2:y=h*0.70:expansion=none"
                f":enable='between(t,{a_:.3f},{end:.3f})'")

    cmd = ["ffmpeg", "-y", "-i", img, "-vf", ",".join(vf),
           "-frames:v", str(frames), "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
           "-pix_fmt", "yuv420p", "-an", out_path]
    ok, err = run(cmd, timeout=300)
    if not ok:
        print(f"    ❌ scene render: {err[-200:]}")
    return ok and os.path.exists(out_path) and os.path.getsize(out_path) > 5000


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def create_quote_video(quote_id=None, video_index=0):
    q = pick_quote(quote_id)
    safe = re.sub(r"[^\w-]", "", q["id"])
    work_dir = f"assets/quote_{video_index}"
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/quote_{video_index}_{safe}.mp4"

    print(f"\n{'=' * 55}\n💬 QUOTE [{q['category'].upper()}] {q['author_roman']}\n{'=' * 55}")

    if not find_devanagari_font():
        print("  ⚠️ Devanagari font nahi mili (fonts-lohit-deva install karo) - quote tofu boxes mein dikhega")

    cta = random.choice(CTA_LINES)
    beats = [
        {"role": "hook", "text": q["hook"], "visual": q["hook_visual"], "caption": True},
        {"role": "quote", "text": q["roman"], "visual": None, "caption": False},
        {"role": "author", "text": f"{q['author_roman']}. {q['author_context']}.", "visual": q["author_visual"], "caption": True},
        {"role": "cta", "text": cta, "visual": None, "caption": False},
    ]

    # 1. voice per beat (quote beat gets a bit more breathing room)
    print("\n🎤 Voice...")
    wavs, durs = [], []
    for i, bt in enumerate(beats):
        mp3 = f"{work_dir}/beat_{i}.mp3"
        wav = f"{work_dir}/beat_{i}.wav"
        if not synth_beat(bt["text"], mp3, "story") or not to_wav_padded(mp3, wav):
            print(f"  ❌ Beat {i} ({bt['role']}) voice fail")
            return None
        d_ = probe_duration(wav)
        if bt["role"] == "quote":
            d_ = max(d_, 3.2) + 1.3   # quote ko padhne ke liye extra hold
        d_ = max(d_, 1.2)
        wavs.append(wav)
        durs.append(d_)
        print(f"  ✅ {bt['role']:<7} {d_:.1f}s")

    voice_wav = f"{work_dir}/voice.wav"
    if not build_voice_track(wavs, voice_wav):
        return None

    # 2. visuals
    print("\n🖼️  Scenes...")
    used_ids = set()
    scene_files = []
    for i, bt in enumerate(beats):
        img = f"{work_dir}/img_{i}.jpg"
        if bt["role"] == "quote":
            make_quote_card(q, img)
            src = "quote-card"
        elif bt["role"] == "cta":
            make_cta_card(q, bt["text"], img)
            src = "cta-card"
        else:
            got = fetch_stock(bt["visual"], img, used_ids) if bt["visual"] else False
            if not got and bt["role"] == "author":
                make_author_card(q, img)
                src = "author-card"
            elif not got:
                make_author_card(q, img)  # hook fallback - themed bg, quote card se alag
                src = "fallback"
            else:
                src = "stock"

        last = i == len(beats) - 1
        clip_len = durs[i] + (0 if last else XFADE)
        scene = f"{work_dir}/scene_{i}.mp4"
        speak = max(durs[i] - BEAT_GAP, 0.8)
        tag = CATEGORY_THEME.get(q["category"], {}).get("label") if bt["role"] in ("hook", "author") else None
        ok = render_beat_scene(img, bt["text"], i, clip_len, speak, work_dir, scene,
                                show_caption=bt["caption"], tag_text=tag)
        if not ok:
            print(f"  ❌ scene {i} ({bt['role']}) fail")
            return None
        scene_files.append(scene)
        print(f"  ✅ {bt['role']:<7} [{src}] {durs[i]:.1f}s")

    # 3. merge
    print(f"\n🎞️  Merging...")
    if not merge_all(scene_files, durs, voice_wav, out_path):
        return None

    vdur = probe_duration(out_path)
    mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\n✅ {vdur:.1f}s, {mb:.1f} MB -> {out_path}")

    title = f"{q['author_roman']} - {q['hi'][:40]}..."
    description = f"{q['hi']}\n— {q['author_hi']}\n\n#motivation #quotes #{q['category']}"
    hashtags = ["#motivation", "#quotes", "#shorts", f"#{q['category']}", "#india"]
    return {"path": out_path, "title": title[:95], "description": description, "hashtags": hashtags}


if __name__ == "__main__":
    print(create_quote_video(video_index=98))
