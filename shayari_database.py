"""
shayari_database.py
Famous shayars ki real shayari + AI generation
"""

SHAYARI_COLLECTION = [

    # ─── KUMAR VISHWAS ───────────────────────────────
    {
        "shayar": "Kumar Vishwas",
        "theme": "ishq",
        "mood": "romantic",
        "shayari": "Koi deewana kehta hai koi pagal samajhta hai.\nMeri mohabbat ko duniya yun hi aasaan samajhta hai.\nJo aag maine seene mein jalaai hai barasaon se,\nWo rozaana ki justajoo hai na koi mushkil samajhta hai.",
        "lines": [
            "Koi deewana kehta hai koi pagal samajhta hai.",
            "Meri mohabbat ko duniya yun hi aasaan samajhta hai.",
            "Jo aag maine seene mein jalaai hai barasaon se,",
            "Wo rozaana ki justajoo hai na koi mushkil samajhta hai."
        ],
        "pexels_queries": ["lonely man rain india", "indian man thinking alone", "rain drops window india", "indian man sad portrait"]
    },
    {
        "shayar": "Kumar Vishwas",
        "theme": "maa",
        "mood": "emotional",
        "shayari": "Mere ghar mein roshni bankar wohi toh aati hai.\nKabhi aankhon mein aansu bankar toh kabhi muskurati hai.\nWoh toh sab kuch jaanti hai bin kahe sab sun leti hai.\nUski dua ki chaadar mein hi toh meri duniya simti hai.",
        "lines": [
            "Mere ghar mein roshni bankar wohi toh aati hai.",
            "Kabhi aankhon mein aansu bankar toh kabhi muskurati hai.",
            "Woh toh sab kuch jaanti hai bin kahe sab sun leti hai.",
            "Uski dua ki chaadar mein hi toh meri duniya simti hai."
        ],
        "pexels_queries": ["indian mother praying hands", "mother child india emotional", "indian woman tears eyes", "mother hug child india"]
    },
    {
        "shayar": "Kumar Vishwas",
        "theme": "judai",
        "mood": "sad",
        "shayari": "Maine poochha tha kabhi unse ke tum kaisi ho.\nWo muskurai thi magar aankhein bheegi bheegi thi.\nBaat kuch keh nahi paaye the alfaaz bhi ruke ruke.\nDard ki bhasha thi jo unne bina bole kahi thi.",
        "lines": [
            "Maine poochha tha kabhi unse ke tum kaisi ho.",
            "Wo muskurai thi magar aankhein bheegi bheegi thi.",
            "Baat kuch keh nahi paaye the alfaaz bhi ruke ruke.",
            "Dard ki bhasha thi jo unne bina bole kahi thi."
        ],
        "pexels_queries": ["indian woman tears rain", "sad woman portrait india", "woman alone thinking india", "rainy day sad india"]
    },

    # ─── SHYAM SRIVASTAV ─────────────────────────────
    {
        "shayar": "Shyam Srivastav",
        "theme": "zindagi",
        "mood": "philosophical",
        "shayari": "Zindagi ne jo diya hai hum use apna lete hain.\nGham bhi khushi jaisa lagta hai jab hum use seene se lagate hain.\nRaah mein kankar bhi aate hain phool bhi milte hain,\nHum thak kar nahi ruke hain chalne ka naam lete hain.",
        "lines": [
            "Zindagi ne jo diya hai hum use apna lete hain.",
            "Gham bhi khushi jaisa lagta hai jab hum use seene se lagate hain.",
            "Raah mein kankar bhi aate hain phool bhi milte hain,",
            "Hum thak kar nahi ruke hain chalne ka naam lete hain."
        ],
        "pexels_queries": ["india road journey sunset", "man walking alone india road", "india path nature", "sunrise india hope"]
    },
    {
        "shayar": "Shyam Srivastav",
        "theme": "dard",
        "mood": "sad",
        "shayari": "Dil mein ek dard hai jo kisi ko nahi batate.\nAankhon mein aansu hain jo hum chhupaate chhupaate hain.\nMuskurahat ke peeche ek toot jaane ki kahani hai,\nHum khud se bhi yeh raaz nahi jaane kab chupaate hain.",
        "lines": [
            "Dil mein ek dard hai jo kisi ko nahi batate.",
            "Aankhon mein aansu hain jo hum chhupaate chhupaate hain.",
            "Muskurahat ke peeche ek toot jaane ki kahani hai,",
            "Hum khud se bhi yeh raaz nahi jaane kab chupaate hain."
        ],
        "pexels_queries": ["india man alone dark", "sad face indian portrait", "candle dark room india", "rain window night india"]
    },
    {
        "shayar": "Shyam Srivastav",
        "theme": "wafa",
        "mood": "romantic",
        "shayari": "Tum aao toh lagta hai jaise bahar aa gayi.\nTumhare jaane se lagta hai sab ujar gayi.\nIs mohabbat ka koi mol nahi lagata hai,\nDil ki har dhadkan mein bas teri surat aa gayi.",
        "lines": [
            "Tum aao toh lagta hai jaise bahar aa gayi.",
            "Tumhare jaane se lagta hai sab ujar gayi.",
            "Is mohabbat ka koi mol nahi lagata hai,",
            "Dil ki har dhadkan mein bas teri surat aa gayi."
        ],
        "pexels_queries": ["couple india romantic", "india flowers garden romantic", "indian woman portrait beautiful", "sunset couple silhouette india"]
    },
    {
        "shayar": "Shyam Srivastav",
        "theme": "khwaab",
        "mood": "motivational",
        "shayari": "Khwaab wo nahi jo neend mein aate hain.\nKhwaab wo hain jo neend na aane dete hain.\nHimmat se chal manzil door nahi hai,\nWo raste hi khud raahdari dikhate hain.",
        "lines": [
            "Khwaab wo nahi jo neend mein aate hain.",
            "Khwaab wo hain jo neend na aane dete hain.",
            "Himmat se chal manzil door nahi hai,",
            "Wo raste hi khud raahdari dikhate hain."
        ],
        "pexels_queries": ["india mountain success man", "young indian man determined", "stars night sky india dream", "india sunrise horizon hope"]
    },

    # ─── RAHAT INDORI ────────────────────────────────
    {
        "shayar": "Rahat Indori",
        "theme": "zindagi",
        "mood": "philosophical",
        "shayari": "Bulati hai magar jaane ka nahi.\nYe duniya hai agar jaane ka nahi.\nJo log gaye unhe yaad karo,\nMagar apne aap ko mitaane ka nahi.",
        "lines": [
            "Bulati hai magar jaane ka nahi.",
            "Ye duniya hai agar jaane ka nahi.",
            "Jo log gaye unhe yaad karo,",
            "Magar apne aap ko mitaane ka nahi."
        ],
        "pexels_queries": ["india old city street sunset", "indian man walking alone road", "india heritage old building", "sunset india silhouette man"]
    },
    {
        "shayar": "Rahat Indori",
        "theme": "dard",
        "mood": "intense",
        "shayari": "Lagta hai aaj bhi koi intezaar kar raha hai.\nKhidki pe chaand aaya toh andar nazar kar raha hai.\nJis ghar ko chhod aaye the hum saalon pehle,\nUssi darwaaze pe koyi aaj bhi pukaar raha hai.",
        "lines": [
            "Lagta hai aaj bhi koi intezaar kar raha hai.",
            "Khidki pe chaand aaya toh andar nazar kar raha hai.",
            "Jis ghar ko chhod aaye the hum saalon pehle,",
            "Ussi darwaaze pe koyi aaj bhi pukaar raha hai."
        ],
        "pexels_queries": ["indian house window moonlight", "old door india night", "india village house night", "moon india dark night"]
    },

    # ─── MIRZA GHALIB ────────────────────────────────
    {
        "shayar": "Mirza Ghalib",
        "theme": "ishq",
        "mood": "classical_romantic",
        "shayari": "Hazaaron khwahishen aisi ke har khwahish pe dam nikle.\nBahut nikle mere armaan lekin phir bhi kam nikle.\nNikalna khuld se Aadam ka sunte aaye hain lekin,\nBahut be-aabru hokar tere kuuche se hum nikle.",
        "lines": [
            "Hazaaron khwahishen aisi ke har khwahish pe dam nikle.",
            "Bahut nikle mere armaan lekin phir bhi kam nikle.",
            "Nikalna khuld se Aadam ka sunte aaye hain lekin,",
            "Bahut be-aabru hokar tere kuuche se hum nikle."
        ],
        "pexels_queries": ["mughal architecture india", "old haveli india twilight", "india classical poetry candle", "ancient india street night lamp"]
    },
    {
        "shayar": "Mirza Ghalib",
        "theme": "dard",
        "mood": "classical_sad",
        "shayari": "Dil-e-nadaan tujhe hua kya hai.\nAakhir is dard ki dawaa kya hai.\nHum hain mushtaaq aur woh bezaar,\nYa Ilahi ye maajra kya hai.",
        "lines": [
            "Dil-e-nadaan tujhe hua kya hai.",
            "Aakhir is dard ki dawaa kya hai.",
            "Hum hain mushtaaq aur woh bezaar,",
            "Ya Ilahi ye maajra kya hai."
        ],
        "pexels_queries": ["india candle dark room", "old india haveli window", "night sky india stars", "india old lamp street"]
    },

    # ─── GULZAR ──────────────────────────────────────
    {
        "shayar": "Gulzar",
        "theme": "tanhaai",
        "mood": "melancholic",
        "shayari": "Tanha hai toh kya gham hai.\nDil mein apna aalam hai.\nJo beet gayi woh raatein,\nUnka bhi kuch kaam hai.",
        "lines": [
            "Tanha hai toh kya gham hai.",
            "Dil mein apna aalam hai.",
            "Jo beet gayi woh raatein,",
            "Unka bhi kuch kaam hai."
        ],
        "pexels_queries": ["india lonely bench night", "empty street india fog", "india night lights alone", "person window rain india"]
    },

    # ─── ALLAMA IQBAL ────────────────────────────────
    {
        "shayar": "Allama Iqbal",
        "theme": "khwaab",
        "mood": "motivational",
        "shayari": "Khudi ko kar buland itna ke har taqdir se pehle.\nKhuda bande se khud pooche bata teri raza kya hai.\nNahi teri umeed ka sahara kisi ko,\nTu hi teri dunia ka khuda hai.",
        "lines": [
            "Khudi ko kar buland itna ke har taqdir se pehle.",
            "Khuda bande se khud pooche bata teri raza kya hai.",
            "Nahi teri umeed ka sahara kisi ko,",
            "Tu hi teri dunia ka khuda hai."
        ],
        "pexels_queries": ["india mountain top sunrise man", "young man determined india", "india sky clouds dramatic", "india eagle flying sky"]
    },

    # ─── JAVED AKHTAR ────────────────────────────────
    {
        "shayar": "Javed Akhtar",
        "theme": "wafa",
        "mood": "romantic",
        "shayari": "Seene mein jalan aankhon mein toofan sa kyun hai.\nIs shehar mein har shakhs pareshaan sa kyun hai.\nDil hai toh dhadakne ka bahana dhundhega,\nPathar ki tarah be-hiss insaan sa kyun hai.",
        "lines": [
            "Seene mein jalan aankhon mein toofan sa kyun hai.",
            "Is shehar mein har shakhs pareshaan sa kyun hai.",
            "Dil hai toh dhadakne ka bahana dhundhega,",
            "Pathar ki tarah be-hiss insaan sa kyun hai."
        ],
        "pexels_queries": ["india city night lights crowd", "india busy street evening", "man city lights india portrait", "india urban night fog"]
    },

    # ─── HARIVANSH RAI BACHCHAN ──────────────────────
    {
        "shayar": "Harivansh Rai Bachchan",
        "theme": "zindagi",
        "mood": "philosophical",
        "shayari": "Jo beet gayi so baat gayi.\nJeevan mein ek sitaara tha,\nMaana woh behad pyaara tha,\nWoh doob gaya toh doob gaya.",
        "lines": [
            "Jo beet gayi so baat gayi.",
            "Jeevan mein ek sitaara tha,",
            "Maana woh behad pyaara tha,",
            "Woh doob gaya toh doob gaya."
        ],
        "pexels_queries": ["india night sky stars", "india river reflection sunset", "old man India contemplating", "india lamp oil night"]
    },

    # ─── DUSHYANT KUMAR ──────────────────────────────
    {
        "shayar": "Dushyant Kumar",
        "theme": "dard",
        "mood": "intense",
        "shayari": "Ho gayi hai peer parvat si pighalni chahiye.\nIs himalay se koi ganga nikalti chahiye.\nAaj yeh deewaar pardon ki tarah hilne lagi,\nShart lekin yeh hai ke pehle ek deewaar girni chahiye.",
        "lines": [
            "Ho gayi hai peer parvat si pighalni chahiye.",
            "Is himalay se koi ganga nikalti chahiye.",
            "Aaj yeh deewaar pardon ki tarah hilne lagi,",
            "Shart lekin yeh hai ke pehle ek deewaar girni chahiye."
        ],
        "pexels_queries": ["himalaya mountains dramatic india", "ganga river india sunrise", "india old wall crumbling", "india dramatic sky clouds storm"]
    },
]


# ─────────────────────────────────────────
# AI SHAYARI GENERATOR
# ─────────────────────────────────────────

SHAYAR_STYLES = {
    "Kumar Vishwas":        "romantic melodious heart-touching Hindi shayari with deep imagery and emotions",
    "Shyam Srivastav":      "philosophical life-wisdom shayari with simple but powerful relatable words",
    "Rahat Indori":         "bold rebellious thought-provoking shayari with strong powerful imagery",
    "Mirza Ghalib":         "classical Urdu shayari with Persian words deep metaphors and timeless wisdom",
    "Gulzar":               "poetic metaphorical nature-inspired dreamy shayari",
    "Allama Iqbal":         "motivational self-empowerment shayari with philosophical and patriotic depth",
    "Javed Akhtar":         "urban relatable modern shayari about life love and society",
    "Bashir Badr":          "simple yet profound romantic Urdu shayari about love and longing",
    "Nida Fazli":           "everyday life philosophical shayari with deep human emotions",
    "Munawwar Rana":        "heart-touching emotional shayari especially about mother and relationships",
    "Wasim Barelvi":        "classical romantic Urdu shayari with beautiful metaphors",
    "Piyush Mishra":        "raw rebellious life-philosophy shayari with modern twist",
    "Suryabala":            "feminine perspective emotional shayari about love life and pain",
    "Amrita Pritam":        "deep emotional romantic shayari about love loss and longing",
}

THEME_MOODS = {
    "ishq":     "romantic",
    "zindagi":  "philosophical",
    "dard":     "sad",
    "wafa":     "romantic",
    "judai":    "sad",
    "khwaab":   "motivational",
    "dost":     "emotional",
    "maa":      "emotional",
    "waqt":     "philosophical",
    "tanhaai":  "melancholic",
}

THEME_QUERIES = {
    "ishq":     ["romantic couple india", "rose petals india", "moonlight india romantic", "indian couple silhouette"],
    "zindagi":  ["india road journey", "sunrise india hope", "old man india wisdom", "india nature peaceful"],
    "dard":     ["rain window india sad", "candle dark room india", "lonely man india night", "india tears pain"],
    "wafa":     ["couple holding hands india", "indian couple portrait", "flowers india love", "sunset couple india"],
    "judai":    ["train leaving india", "empty bench india", "walking alone beach india", "person alone window india"],
    "khwaab":   ["stars night sky india", "mountain top india success", "young man dream india", "sunrise horizon india"],
    "dost":     ["friends laughing india", "old friends tea india", "friends walking india", "friendship india"],
    "maa":      ["indian mother praying", "mother child india", "mother hug child india", "woman praying diya"],
    "waqt":     ["clock old india", "old city street india", "calendar pages time", "india heritage monument"],
    "tanhaai":  ["person alone window india", "empty street india fog", "single candle dark", "india lonely night"],
}


def generate_ai_shayari(shayar=None, theme=None):
    """Gemini se fresh unique shayari generate karo"""
    from gemini_client import generate
    import random as _random

    if not shayar:
        shayar = _random.choice(list(SHAYAR_STYLES.keys()))
    if not theme:
        theme = _random.choice(list(THEME_MOODS.keys()))

    style = SHAYAR_STYLES.get(shayar, "beautiful Hindi shayari")
    mood = THEME_MOODS.get(theme, "emotional")
    queries = THEME_QUERIES.get(theme, ["india nature portrait"])

    prompt = f"""
Tu ek legendary shayar hai jiska style {shayar} jaisa hai.

Style: {style}
Theme: {theme}
Mood: {mood}

Ek ORIGINAL shayari likho jo:
1. Bilkul {shayar} ke style mein ho
2. Theme {theme} ke baare mein ho
3. 4-6 lines, dil ko chhu jaaye
4. SIRF Roman Hindi mein (Devanagari NAHI)
5. Har line punch wali ho
6. Log screenshot leke share karein

SIRF JSON mein jawab do:
{{
  "shayar": "{shayar}",
  "theme": "{theme}",
  "mood": "{mood}",
  "shayari": "poori shayari Roman Hindi mein\\nhar line naye line pe",
  "lines": ["line 1", "line 2", "line 3", "line 4"],
  "pexels_queries": ["{queries[0]}", "{queries[1]}", "{queries[2] if len(queries) > 2 else queries[0]}"]
}}"""

    try:
        resp = generate(prompt)
        if resp:
            t = resp.strip()
            if "```json" in t:
                t = t.split("```json")[1].split("```")[0].strip()
            elif "```" in t:
                t = t.split("```")[1].split("```")[0].strip()
            data = __import__('json').loads(t)
            if data.get("shayari") and data.get("lines"):
                print(f"  ✅ AI shayari: {shayar} - {theme}")
                return data
    except Exception as e:
        print(f"  ⚠️ AI shayari error: {e}")
    return None


def get_shayari_by_theme(theme, count=1):
    import random
    matching = [s for s in SHAYARI_COLLECTION if s["theme"] == theme]
    if not matching:
        matching = SHAYARI_COLLECTION
    return random.sample(matching, min(count, len(matching)))


def get_random_shayari(count=1):
    import random
    return random.sample(SHAYARI_COLLECTION, min(count, len(SHAYARI_COLLECTION)))


def get_all_themes():
    return sorted(list(set(s["theme"] for s in SHAYARI_COLLECTION)))


def get_all_shayars():
    return sorted(list(set(s["shayar"] for s in SHAYARI_COLLECTION)))


if __name__ == "__main__":
    print(f"Database: {len(SHAYARI_COLLECTION)} shayari")
    print(f"Shayars: {get_all_shayars()}")
    print(f"Themes: {get_all_themes()}")
    print("\nAI shayari test...")
    result = generate_ai_shayari("Kumar Vishwas", "ishq")
    if result:
        print(result["shayari"])