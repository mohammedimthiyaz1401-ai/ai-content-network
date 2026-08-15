"""
trend_sniffer.py
----------------
Selects viral topics for the channel.
USES GEMINI to brainstorm fresh, high-CTR topics (no YouTube transcript
scraping - YouTube blocks those requests from home AND cloud IPs, which
flooded the logs and broke harvest).

Fallback chain:
  1. Gemini brainstormed topic (premium, fresh) - uses script source transcript
  2. Curated evergreen topic (always works, $0)

Cost: $0.001 (one Gemini call per day)
NO .env dependency
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

DATA_DIR = Path(__file__).parent.parent / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Channel-specific evergreen topics (fallback when Gemini unavailable)
CHANNEL_TOPICS = {
    "channel_1": {
        "name": "Aria Future",
        "evergreen": [
            "The 3 AI tools that feel illegal to know in 2026",
            "How I built a $10k/month AI automation workflow",
            "5 ChatGPT tricks that actually save you hours daily",
            "Passive income with AI: the honest 2026 playbook",
        ],
        "category": "tech",
    },
}

_TOPIC_CACHE = {}


def brainstorm_topics_gemini(channel: str, count: int = 3) -> List[Dict]:
    """PRIMARY METHOD: ask Gemini for fresh viral topics, returns topics with a
    mini transcript seed so the scriptwriter has source material."""
    try:
        from scriptwriter import client, GEMINI_API_KEY, MODEL_NAME
        if not GEMINI_API_KEY:
            return []

        prompt = (
            f"You are a YouTube strategist for '{channel}' (female AI/tech influencer). "
            f"Create {count} high-CTR video topics from the last 24 hours of tech/AI news. "
            f"For each return JSON: {{\"title\": \"...\", "
            f"\"transcript\": \"15-word overview of what the video covers\"}}. "
            f"Topics must feel valuable, specific, and curiosity-driven. JSON array only."
        )
        resp = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = resp.text.strip()

        try:
            arr = json.loads(text)
        except Exception:
            start, end = text.find("["), text.rfind("]")
            if start != -1 and end != -1:
                arr = json.loads(text[start:end + 1])
            else:
                arr = []

        topics = []
        for item in arr if isinstance(arr, list) else []:
            topics.append({
                "title": item.get("title", "AI Tools 2026"),
                "transcript": item.get("transcript", "Top AI tools and strategies for 2026."),
                "query": item.get("title", "")[:40],
            })
        return topics

    except Exception as e:
        print(f"[TRENDS] Gemini brainstorm failed (falling back): {e}")
        return []


def get_curated_topics(channel: str, count: int = 3) -> List[Dict]:
    """FALLBACK METHOD: evergreen curated topics. Always works, $0 cost."""
    config = CHANNEL_TOPICS[channel]
    topics = []
    for title in config["evergreen"][:count]:
        topics.append({
            "title": title,
            "transcript": f"A practical walkthrough of: {title}",
            "query": title[:40],
        })
    return topics


def get_trending_topics(channel: str, max_results: int = 5) -> List[Dict]:
    """FALLBACK CHAIN (no YouTube scraping - immune to IP blocks):
      1. Gemini brainstorm (fresh, relevant)
      2. Curated evergreen (always works)"""
    if channel not in CHANNEL_TOPICS:
        raise ValueError(f"Unknown channel: {channel}")

    if channel in _TOPIC_CACHE:
        return _TOPIC_CACHE[channel]

    print(f"\n{'='*60}")
    print(f"SCANNING: {CHANNEL_TOPICS[channel]['name']}")
    print(f"Method: Gemini brainstorm -> curated evergreen")
    print(f"{'='*60}")

    topics = brainstorm_topics_gemini(channel, count=max_results)
    source = "Gemini"
    if not topics:
        topics = get_curated_topics(channel, count=max_results)
        source = "Curated evergreen"

    for t in topics:
        t["channel"] = channel
        t["source"] = source

    print(f"[TRENDS] Got {len(topics)} topics from {source}")
    _TOPIC_CACHE[channel] = topics
    return topics


def analyze_viral_potential(videos: List[Dict]) -> List[Dict]:
    """Kept for compatibility - topics don't need scoring now, but this
    orders by title length (nicer for thumbnails/CTR)."""
    def score(v):
        s = 0
        tl = len(v.get("title", ""))
        if 40 <= tl <= 72:
            s += 20        # ideal thumbnail/title length
        if len(v.get("transcript", "")) > 80:
            s += 15        # has material to script from
        return s

    for v in videos:
        v["viral_score"] = score(v)
    videos.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
    return videos


def save_trends(videos: List[Dict], channel: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trends_{channel}_{timestamp}.json"
    filepath = DATA_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Trends saved to: {filepath}")
    return str(filepath)


def get_all_trends() -> Dict[str, List[Dict]]:
    all_trends = {}
    for channel in CHANNEL_TOPICS.keys():
        videos = get_trending_topics(channel, max_results=3)
        scored_videos = analyze_viral_potential(videos)
        save_trends(scored_videos, channel)
        all_trends[channel] = scored_videos
    return all_trends


if __name__ == "__main__":
    print("=" * 60)
    print("TREND SNIFFER - TEST MODE (no YouTube scraping)")
    print("=" * 60)

    trends = get_trending_topics("channel_1", max_results=3)
    scored = analyze_viral_potential(trends)

    print("\n[RESULTS]")
    for i, video in enumerate(scored[:3], 1):
        print(f"{i}. {video.get('title', 'N/A')[:70]}")
        print(f"   Source: {video.get('source', 'n/a')}")

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
