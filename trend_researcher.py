"""
trend_researcher.py
Aaj ke viral/trending topics dhundta hai India se
"""

import requests
import warnings
warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup
from gemini_client import generate
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()


def get_google_trends_india():
    try:
        url = "https://trends.google.com/trending/rss?geo=IN"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all('title')[1:]
        topics = [item.get_text().strip() for item in items[:15] if item.get_text().strip()]
        print(f"✅ Google Trends se {len(topics)} topics mili")
        return topics
    except Exception as e:
        print(f"⚠️ Google Trends error: {e}")
        return []


def get_news_trending():
    topics = []
    try:
        url = "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all('item')[:15]
        for item in items:
            title = item.find('title')
            if title:
                topics.append(title.get_text())
        print(f"✅ Google News se {len(topics)} topics mili")
    except Exception as e:
        print(f"⚠️ News error: {e}")
    return topics


def get_youtube_trending_india():
    topics = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        url = "https://www.youtube.com/feed/trending?gl=IN&hl=hi"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        titles = soup.find_all('title')
        for title in titles[:20]:
            text = title.get_text().strip()
            if len(text) > 5 and 'YouTube' not in text:
                topics.append(text)
        print(f"✅ YouTube se {len(topics)} topics mili")
    except Exception as e:
        print(f"⚠️ YouTube error: {e}")
    return topics


def analyze_viral_potential(topics):
    if not topics:
        return []

    topics_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(topics[:30])])

    prompt = f"""
Tu ek expert YouTube Shorts creator hai jo India mein viral content banata hai.

Neeche aaj ke trending topics ki list hai:
{topics_text}

Tujhe karna ye hai:
1. In topics mein se TOP 5 select kar jo YouTube Shorts pe VIRAL ho sakte hain
2. Har topic ke liye ek catchy SHORT title suggest kar (Hindi mein)
3. Batao kyun ye viral hoga

SIRF JSON format mein jawab de, kuch aur mat likho:
{{
  "viral_topics": [
    {{
      "original_topic": "topic ka naam",
      "short_title": "catchy hindi title",
      "category": "facts/horror/motivation/news/finance/sports",
      "viral_reason": "kyun viral hoga",
      "viral_score": 8
    }}
  ]
}}
"""

    try:
        text = generate(prompt)
        if not text:
            return []
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)
        topics_list = data.get("viral_topics", [])
        # Normalize keys - short_title ensure karo
        for t in topics_list:
            if 'short_title' not in t:
                t['short_title'] = t.get('title') or t.get('original_topic') or t.get('topic', 'Viral Topic')
            if 'category' not in t:
                t['category'] = 'facts'
        topics_list.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
        print(f"✅ Gemini ne {len(topics_list)} viral topics select kiye")
        return topics_list
    except Exception as e:
        print(f"⚠️ Gemini analysis error: {e}")
        return []


def research_todays_viral_topics():
    print("\n🔍 Aaj ke viral topics research ho rahi hai...\n")

    all_topics = []

    print("📊 Google Trends check kar raha hoon...")
    all_topics.extend(get_google_trends_india())
    time.sleep(1)

    print("📰 Google News check kar raha hoon...")
    all_topics.extend(get_news_trending())
    time.sleep(1)

    print("▶️ YouTube Trending check kar raha hoon...")
    all_topics.extend(get_youtube_trending_india())

    all_topics = list(dict.fromkeys(all_topics))
    print(f"\n📋 Total {len(all_topics)} unique topics mili")

    print("\n🤖 Gemini viral potential analyze kar raha hai...")
    viral_topics = analyze_viral_potential(all_topics)

    if not viral_topics:
        print("⚠️ Fallback topics use kar raha hoon...")
        viral_topics = [{
            "original_topic": "India history",
            "short_title": "Bharat ka wo raaz jo school mein nahi padhaya gaya",
            "category": "facts",
            "viral_reason": "Curiosity + nationalism",
            "viral_score": 7
        }]

    with open("logs/todays_topics.json", "w", encoding="utf-8") as f:
        json.dump(viral_topics, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 Top viral topics ready hain!\n")
    for i, topic in enumerate(viral_topics[:3], 1):
        print(f"  {i}. {topic['short_title']} (Score: {topic.get('viral_score', 'N/A')})")

    return viral_topics


if __name__ == "__main__":
    topics = research_todays_viral_topics()
    print("\n✅ Research complete!")