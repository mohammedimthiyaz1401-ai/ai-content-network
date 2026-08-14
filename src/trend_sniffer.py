"""
trend_sniffer.py
----------------
Scrapes YouTube for viral topics from the last 24 hours.
Uses youtube-transcript-api and yt-dlp for trend detection.

Cost: $0 (free tier)
NO .env dependency
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

DATA_DIR = Path(__file__).parent.parent / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Channel-specific search queries
CHANNEL_TOPICS = {
    "channel_1": {
        "name": "Aria Future",
        "queries": [
            "AI tools 2026",
            "passive income AI",
            "ChatGPT tricks",
            "make money online AI",
            "best AI tools",
            "AI side hustle",
            "future technology",
        ],
        "category": "tech",
    },
}


def search_youtube_videos(query: str, max_results: int = 10) -> List[Dict]:
    import yt_dlp
    
    search_opts = {
        "default_search": "ytsearch",
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": max_results,
    }
    
    videos = []
    
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            
            if "entries" in result:
                for entry in result["entries"]:
                    if entry:
                        videos.append({
                            "id": entry.get("id"),
                            "title": entry.get("title"),
                            "url": f"https://youtube.com/watch?v={entry.get('id')}",
                            "view_count": entry.get("view_count", 0),
                            "duration": entry.get("duration", 0),
                        })
    except Exception as e:
        print(f"[ERROR] yt-dlp search failed for '{query}': {e}")
    
    return videos


def get_video_transcript(video_id: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=["en"])
        
        full_text = " ".join([snippet.text for snippet in transcript.snippets])
        
        return full_text
    
    except Exception as e:
        print(f"[WARN] Transcript unavailable for {video_id}: {e}")
        return ""


def get_trending_topics(channel: str, max_results: int = 5) -> List[Dict]:
    if channel not in CHANNEL_TOPICS:
        raise ValueError(f"Unknown channel: {channel}")
    
    config = CHANNEL_TOPICS[channel]
    all_videos = []
    
    print(f"\n{'='*60}")
    print(f"SCANNING: {config['name']}")
    print(f"{'='*60}")
    
    for query in config["queries"]:
        print(f"\n[SEARCH] Query: '{query}'")
        
        videos = search_youtube_videos(query, max_results)
        
        for video in videos:
            transcript = get_video_transcript(video["id"])
            
            if transcript and len(transcript) > 500:
                video["transcript"] = transcript
                video["query"] = query
                video["channel"] = channel
                all_videos.append(video)
                print(f"[FOUND] {video['title'][:60].encode('ascii', 'ignore').decode('ascii')}... ({len(transcript)} chars)")
    
    all_videos.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    
    print(f"\n[TOTAL] Found {len(all_videos)} videos with transcripts for {config['name']}")
    
    return all_videos[:10]


def analyze_viral_potential(videos: List[Dict]) -> List[Dict]:
    for video in videos:
        score = 0
        
        title_len = len(video.get("title", ""))
        if 40 <= title_len <= 70:
            score += 20
        
        transcript_len = len(video.get("transcript", ""))
        if transcript_len > 2000:
            score += 30
        elif transcript_len > 1000:
            score += 15
        
        views = video.get("view_count", 0)
        if views > 1000000:
            score += 30
        elif views > 100000:
            score += 20
        elif views > 10000:
            score += 10
        
        duration = video.get("duration", 0)
        if duration > 480:
            score += 20
        
        video["viral_score"] = score
    
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
    print("TREND SNIFFER - TEST MODE")
    print("=" * 60)
    
    trends = get_trending_topics("channel_1", max_results=2)
    scored = analyze_viral_potential(trends)
    
    print("\n[RESULTS]")
    for i, video in enumerate(scored[:3], 1):
        print(f"{i}. {video.get('title', 'N/A')[:60]}...")
        print(f"   Viral Score: {video.get('viral_score', 0)}")
        print(f"   Transcript: {len(video.get('transcript', ''))} chars")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
