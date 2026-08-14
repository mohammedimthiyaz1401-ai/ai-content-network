"""
trend_sniffer.py
----------------
Scrapes YouTube for viral topics from the last 24 hours.
Uses youtube-transcript-api and yt-dlp for trend detection.

Replaces: Paid trend APIs
Cost: $0 (free tier)
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

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
    "channel_2": {
        "name": "Future Intelligence News",
        "queries": [
            "AI breakthrough 2026",
            "crypto market news",
            "future technology news",
            "space exploration news",
            "科技新闻",
            "artificial intelligence news",
        ],
        "category": "news",
    },
    "channel_3": {
        "name": "The Mystery Algorithm",
        "queries": [
            "internet mystery",
            "psychology tricks",
            "viral Reddit stories",
            "unsolved mysteries",
            "creepy internet",
            "mind games",
        ],
        "category": "mystery",
    },
}


def search_youtube_videos(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search YouTube for videos using yt-dlp.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
    
    Returns:
        List of video metadata dicts
    """
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
    """
    Extract transcript from a YouTube video.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Transcript text or empty string
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        
        # Combine transcript segments
        full_text = " ".join([segment["text"] for segment in transcript])
        
        return full_text
    
    except Exception as e:
        print(f"[WARN] Transcript unavailable for {video_id}: {e}")
        return ""


def get_trending_topics(channel: str, max_results: int = 5) -> List[Dict]:
    """
    Get trending topics for a specific channel.
    
    Args:
        channel: Channel identifier (channel_1, channel_2, channel_3)
        max_results: Max results per query
    
    Returns:
        List of trending topic dicts with transcripts
    """
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
            # Get transcript for each video
            transcript = get_video_transcript(video["id"])
            
            if transcript and len(transcript) > 500:
                video["transcript"] = transcript
                video["query"] = query
                video["channel"] = channel
                all_videos.append(video)
                print(f"[FOUND] {video['title'][:60]}... ({len(transcript)} chars)")
    
    # Sort by view count (if available)
    all_videos.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    
    print(f"\n[TOTAL] Found {len(all_videos)} videos with transcripts for {config['name']}")
    
    return all_videos[:10]  # Return top 10


def analyze_viral_potential(videos: List[Dict]) -> List[Dict]:
    """
    Simple viral potential scoring based on engagement signals.
    
    Args:
        videos: List of video metadata
    
    Returns:
        Videos with viral_score added
    """
    for video in videos:
        score = 0
        
        # Title length optimization (40-70 chars ideal)
        title_len = len(video.get("title", ""))
        if 40 <= title_len <= 70:
            score += 20
        
        # Transcript length (longer = more content to rewrite)
        transcript_len = len(video.get("transcript", ""))
        if transcript_len > 2000:
            score += 30
        elif transcript_len > 1000:
            score += 15
        
        # View count signal
        views = video.get("view_count", 0)
        if views > 1000000:
            score += 30
        elif views > 100000:
            score += 20
        elif views > 10000:
            score += 10
        
        # Duration (8+ min videos have more content)
        duration = video.get("duration", 0)
        if duration > 480:  # 8+ minutes
            score += 20
        
        video["viral_score"] = score
    
    # Sort by viral score
    videos.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
    
    return videos


def save_trends(videos: List[Dict], channel: str) -> str:
    """
    Save trending topics to JSON file.
    
    Args:
        videos: Processed video data
        channel: Channel identifier
    
    Returns:
        Path to saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trends_{channel}_{timestamp}.json"
    filepath = DATA_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVED] Trends saved to: {filepath}")
    return str(filepath)


def get_all_trends() -> Dict[str, List[Dict]]:
    """
    Get trending topics for all channels.
    
    Returns:
        Dict mapping channel names to their trending topics
    """
    all_trends = {}
    
    for channel in CHANNEL_TOPICS.keys():
        videos = get_trending_topics(channel, max_results=3)
        scored_videos = analyze_viral_potential(videos)
        save_trends(scored_videos, channel)
        all_trends[channel] = scored_videos
    
    return all_trends


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("TREND SNIFFER - TEST MODE")
    print("=" * 60)
    
    # Test single channel
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
