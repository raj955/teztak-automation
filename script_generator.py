"""
script_generator.py - A1 QUALITY
Script topic ke hisab se best format auto-choose karta hai.
5 formats: facts, story, roast, countdown, news_breakdown
Sab Roman Hindi mein - voice ke liye crystal clear
"""

import json, time, random
from gemini_client import generate
from dotenv import load_dotenv
load_dotenv()

CHANNEL = "Tez Tak"

# Format selection logic - topic/category ke hisab se
FORMAT_MAP = {
    "cricket":    ["facts", "story", "countdown"],
    "sports":     ["facts", "countdown", "story"],
    "politics":   ["news_breakdown", "story", "facts"],
    "crime":      ["story", "facts", "news_breakdown"],
    "finance":    ["facts", "news_breakdown", "countdown"],
    "technology": ["facts", "countdown", "roast"],
    "weather":    ["news_breakdown", "facts", "story"],
    "bollywood":  ["facts", "roast", "countdown"],
    "motivation": ["facts", "story", "countdown"],
    "news":       ["news_breakdown", "facts", "story"],
}

FORMAT_PROMPTS = {
    "facts": """
VIRAL FACTS FORMAT - No anchor. Seedha shocking facts.

HOOK formulas (ek choose karo - sabse powerful):
- "99 percent log nahi jaante ki [topic ke baare mein shocking fact]..."
- "Ye [number] facts sun ke aap raat ko so nahi paoge..."
- "[Topic] ka wo sach jo media ne chhupa liya..."
- "Ek minute ke liye ruko... [shocking statement about topic]"

Structure:
- HOOK (0-4s): Scroll rokne wala - pehla sentence hi killer hona chahiye
- FACT 1 (4-12s): Interesting but not best yet
- FACT 2 (12-22s): Aur interesting - curiosity badho
- FACT 3 (22-32s): Wow moment
- FACT 4 (32-42s): Even more shocking
- CLIMAX (42-50s): SABSE BADA FACT - is ke liye log ruke the
- CTA (50-55s): "Like karo, comment mein batao, aur subscribe zarur karo!"

Voice rules:
- Max 8 words per sentence
- Pauses: "..." use karo
- Power words: "shocking", "secret", "sach", "pehli baar", "hairan"
- Roman Hindi ONLY - no Devanagari
- 140-160 words total
- LAST LINE MUST BE: "Like karo, comment karo, aur subscribe zarur karo!"
""",

    "story": """
THRILLER STORY FORMAT - Netflix documentary style. No anchor.

HOOK formulas:
- "Ye kahani sun ke raat ko akele mat rehna..."
- "[Year] ki us raat jab [something shocking] hua..."
- "Ek [ordinary person] jo aaj bhi [shocking outcome]..."
- "Police ne jab file kholi, andar jo mila wo sochne pe majboor kar deta hai..."

Structure:
- HOOK (0-5s): Mystery create karo - incomplete statement
- SETUP (5-15s): Scene set karo - jagah, time, character introduce
- BUILD (15-28s): Suspense badho - clues do but answer mat do
- TWIST (28-40s): Unexpected turn - viewer shock mein
- REVEAL (40-50s): Poora sach - payoff moment
- END (50-55s): "Ye sun ke aap bhi hairan reh gaye? Like karo!"

Voice rules:
- Slow dramatic pace - pauses important hain "..."
- Atmosphere words: "andhera", "khamoshi", "raaz", "sach"
- Short sentences - max 7 words
- Roman Hindi ONLY
- 140-160 words total
""",

    "roast": """
ROAST/COMEDY FORMAT - Sarcastic commentary. No anchor.

HOOK formulas:
- "Bhai seriously... ye kya ho raha hai?"
- "Matlab main samajh nahi pa raha hoon..."
- "2025 mein ye hoga, kisi ne socha bhi nahi tha..."
- "Ye log seriously aisa sochte hain? Main haan..."

Structure:
- HOOK (0-4s): Funny/shocking observation - instant reaction
- SETUP (4-14s): Main topic explain karo - sarcastic angle
- ROAST 1 (14-26s): Savage first point with comparison
- ROAST 2 (26-38s): Even funnier/more savage
- TWIST (38-48s): Unexpected funny conclusion
- CTA (48-55s): "Like karo agar ye dekh ke aap bhi confused ho gaye!"

Voice rules:
- Conversational Hinglish - dost se baat karne jaisa
- Emphasis: "seriously", "bhai", "matlab", "yaar"
- Energetic tone - smile feel aani chahiye
- Roman Hindi/Hinglish
- 140-160 words total
""",

    "countdown": """
COUNTDOWN FORMAT - Suspense list. No anchor.

HOOK formulas:
- "Top 5 [topic] jo sun ke aapki neend ud jaayegi... Number 1 sabse dangerous hai"
- "[Number] shocking facts - last wala sun ke aap screen tod doge"
- "Ye [number] cheezein jaanke aap [topic] ko kabhi alag nazar se dekhoge"

Structure:
- HOOK (0-5s): Curiosity gap - "last wala sun ke..." - tease ending
- #5 (5-14s): Interesting entry point
- #4 (14-23s): Better - "aur ye sirf number 4 hai..."
- #3 (23-32s): Wow - "abhi aur bhi hai..."
- #2 (32-41s): Almost best - tension build karo "number 1 ke liye tayaar ho?"
- #1 (41-51s): MOST SHOCKING - is ke liye log sab kuch sehte hain
- CTA (51-55s): "Number 1 ne hairan kiya? Like karo!"

Voice rules:
- Each number pe excitement BADHE
- "Ye sirf number X hai..." tease lines
- Short punchy sentences
- Roman Hindi ONLY
- 150-170 words total
""",

    "news_breakdown": """
NEWS BREAKDOWN FORMAT - Urgent breaking news style. No anchor face needed.

HOOK formulas:
- "Badi khabar! [Topic] ne machaaya bawaal - poori detail sun lo"
- "Sirf [Channel] pe - ye sach aaj pehli baar saamne aaya..."
- "Alert! Ye news aapko seedha affect karti hai..."
- "Breaking! [Topic] - ye sun ke aap bhi hairan ho jaoge"

Structure:
- HOOK (0-4s): URGENT headline - maximum energy
- WHAT (4-12s): Kya hua - bare facts
- WHY (12-22s): Kyun hua - context
- IMPACT (22-32s): Iska matlab kya hai - aap par asar
- DETAIL (32-42s): Sabse important detail
- CONCLUSION (42-50s): Aage kya hoga
- CTA (50-55s): "Like karo aur channel follow karo aisi khabron ke liye!"

Voice rules:
- Urgent news energy - har word important lagein
- Short sentences max 8 words
- Roman Hindi ONLY
- 140-160 words total
"""
}


def pick_format(category, index=0):
    """Category ke hisab se best format choose karo"""
    formats = FORMAT_MAP.get(category.lower(), ["facts", "story", "news_breakdown"])
    return formats[index % len(formats)]


def generate_viral_script(topic_data, forced_format=None):
    category = topic_data.get("category", "news")
    title = topic_data.get("short_title") or topic_data.get("title", "")
    index = topic_data.get("script_index", 0)

    fmt = forced_format or pick_format(category, index)
    format_guide = FORMAT_PROMPTS.get(fmt, FORMAT_PROMPTS["facts"])

    prompt = f"""
Tu world ka best viral Hindi YouTube Shorts scriptwriter hai.
Channel: {CHANNEL}

Topic: {title}
Category: {category}
Format: {fmt.upper()}

{format_guide}

SIRF JSON mein jawab do - kuch aur mat likho:
{{
  "format": "{fmt}",
  "anchor_name": "",
  "needs_heygen": false,
  "title": "catchy Hindi/Hinglish title - 60 chars max - curiosity gap hona chahiye",
  "description": "3 engaging lines - keywords include karo",
  "hashtags": ["#shorts", "#viral", "#hindi", "#{category}", "#TezTak"],
  "full_script": "poora Roman Hindi script - EXACTLY format ke rules follow karo",
  "thumbnail_text": "6 words max - scroll rokne wala",
  "pexels_queries": [
    "specific 2-3 word english query for scene 1",
    "specific 2-3 word english query for scene 2",
    "specific 2-3 word english query for scene 3",
    "specific 2-3 word english query for scene 4",
    "specific 2-3 word english query for scene 5"
  ]
}}

pexels_queries rules:
- Directly related to topic - "{title}"
- NEVER: "subscribe button", "news anchor", "logo", "meme"
- Real searchable terms: "MS Dhoni batting", "india election", "mumbai flood"
"""

    try:
        text = generate(prompt)
        if not text:
            return None

        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)

        # Ensure full_script is string
        fs = data.get("full_script", "")
        if isinstance(fs, list):
            fs = " ".join(str(x) for x in fs)
        data["full_script"] = str(fs).strip()
        data["format"] = fmt
        data["needs_heygen"] = False
        data["anchor_name"] = ""

        print(f"  ✅ [{fmt.upper()}] {data.get('title', '')[:50]}")
        return data

    except Exception as e:
        print(f"  ❌ Script error: {e}")
        return None


def generate_multiple_scripts(viral_topics, count=3):
    """Multiple scripts - varied formats"""
    scripts = []

    # Format cycle for variety
    format_cycle = ["facts", "story", "countdown", "roast", "news_breakdown"]

    for i, topic in enumerate(viral_topics[:count]):
        # Force format cycle for variety
        forced = format_cycle[i % len(format_cycle)]
        topic["script_index"] = i

        print(f"\n📝 Script {i+1}/{count} [{forced.upper()}]: {topic.get('short_title', topic.get('title', ''))[:45]}")

        script = generate_viral_script(topic, forced_format=forced)
        if script:
            script["topic_data"] = topic
            scripts.append(script)
        time.sleep(1)

    with open("logs/generated_scripts.json", "w", encoding="utf-8") as f:
        json.dump(scripts, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(scripts)} scripts ready!")
    return scripts


if __name__ == "__main__":
    test = {
        "short_title": "Dhoni ka wo last six World Cup 2011",
        "category": "cricket",
        "script_index": 0
    }
    s = generate_viral_script(test)
    if s:
        print(s["full_script"])