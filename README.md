# 🎬 YouTube Shorts Auto Generator
## Gemini AI se Daily Viral Shorts - Fully Automated

---

## Ye kya karta hai?

Ye system **roz khud se**:
1. 🔍 Google Trends + YouTube + News se **viral topics dhundta hai**
2. 🤖 Gemini AI se **Hindi script likhta hai** (powerful hooks ke saath)
3. 🎬 **Real looking video banata hai** (footage + voiceover + captions)
4. 📤 **YouTube pe automatically upload** kar deta hai

---

## Setup (Ek baar karna hai)

### Step 1: Python Install Karo
- Python 3.9+ chahiye: https://python.org/downloads
- Download karo aur install karo ✓

### Step 2: FFmpeg Install Karo (Video ke liye zaruri)
1. https://ffmpeg.org/download.html pe jao
2. Windows ke liye: "Windows builds from gyan.de" pe click karo
3. Download karo, extract karo `C:\ffmpeg` mein
4. Environment variables mein add karo:
   - Start > "Environment Variables" search karo
   - "Path" edit karo
   - `C:\ffmpeg\bin` add karo
5. CMD mein check karo: `ffmpeg -version`

### Step 3: Dependencies Install Karo
```bash
cd youtube_shorts_automation
pip install -r requirements.txt
```

### Step 4: Gemini API Key
1. https://aistudio.google.com/app/apikey pe jao
2. "Create API Key" karo
3. `.env` file kholna aur apni key dalo:
   ```
   GEMINI_API_KEY=AIzaSy... (apni key)
   ```

### Step 5: Pexels API Key (Real background footage ke liye)
1. https://www.pexels.com/api/ pe free account banao
2. API key copy karo
3. `.env` mein dalo:
   ```
   PEXELS_API_KEY=your_key_here
   ```

### Step 6: YouTube API Setup
1. https://console.cloud.google.com/ pe jao
2. New Project banao: "YouTube Shorts Bot"
3. "APIs & Services" > "Enable APIs" > "YouTube Data API v3" enable karo
4. "Credentials" > "Create Credentials" > "OAuth 2.0 Client ID"
5. Application type: "Desktop app"
6. Download karo JSON file
7. **Rename karke `client_secrets.json` rakh do project folder mein**

---

## Chalane Ka Tarika

### Pehli baar test karo:
```bash
python main.py --test
```
(Ek video banega, upload nahi hoga - check karo sab sahi hai)

### Normal run (3 videos banao + upload):
```bash
python main.py
```

### Zyada videos:
```bash
python main.py --count 5
```

### Sirf videos banao, upload nahi:
```bash
python main.py --no-upload
```

### Daily automatic scheduler:
```bash
python scheduler.py
```
(Roz subah 9 baje khud chalega)

---

## Folder Structure

```
youtube_shorts_automation/
├── main.py                 ← Main file (yahi chalao)
├── trend_researcher.py     ← Viral topics dhundta hai
├── script_generator.py     ← Gemini se script banata hai
├── video_creator.py        ← Video banata hai
├── uploader.py             ← YouTube pe upload karta hai
├── scheduler.py            ← Daily automatic run
├── .env                    ← API keys (secret rakho!)
├── client_secrets.json     ← YouTube OAuth (aap download karoge)
├── requirements.txt        ← Dependencies
├── output/                 ← Bani hui videos yahan
├── assets/                 ← Temporary files
└── logs/                   ← Run history
```

---

## Troubleshooting

**"FFmpeg not found"**
→ FFmpeg install karo aur PATH mein add karo (Step 2 dekho)

**"GEMINI_API_KEY not set"**
→ `.env` file mein key check karo

**"client_secrets.json not found"**
→ YouTube API setup karo (Step 6 dekho)

**"Quota exceeded"**
→ YouTube pe daily 6 videos upload limit hai free account pe

**Video mein audio nahi hai**
→ `pip install gtts` run karo

---

## Tips for Viral Growth

1. **Consistency** - Roz kam se kam 2-3 videos
2. **First 3 seconds** - Hook sab se important hai
3. **Hashtags** - #Shorts #Viral #Hindi ZARUR use karo
4. **Upload time** - Subah 7-9 AM best time India ke liye
5. **Engage** - Comments ka jawab do pehle hafte

---

## Important Notes

- Pehli baar YouTube pe authenticate karne ke liye browser khunega
- Token save ho jaata hai, baar baar login nahi karna padega
- `.env` file kabhi bhi share mat karo (API keys hain)
- `output/` folder mein videos save hoti hain
