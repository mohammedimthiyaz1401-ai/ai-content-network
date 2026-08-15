"""
scriptwriter.py
---------------
Uses Google Gemini API to generate 1500+ word scripts from viral transcripts.
Includes SEO optimization for titles and descriptions.

Uses google-genai (new package, NOT deprecated google-generativeai)
Cost: $0 (Gemini free tier)
"""

import os
import json
from google import genai
from pathlib import Path
from datetime import datetime
from typing import Dict
from config import GEMINI_API_KEY

DATA_DIR = Path(__file__).parent.parent / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Configure Gemini API
client = genai.Client(api_key=GEMINI_API_KEY)
genai = genai
MODEL_NAME = "gemini-3.1-flash-lite"

# Channel-specific persona prompts
CHANNEL_PERSONAS = {
    "channel_1": {
        "name": "Aria Future",
        "persona": """You are Aria Future, a 25-year-old highly attractive, modern female tech/finance influencer.
Your tone is confident, energetic, and slightly informal - like talking to a friend who wants to get rich.
You use phrases like 'Let me break this down for you', 'Here's the thing', and 'Trust me on this'.
You're passionate about AI tools, passive income, and tech lifehacks.
You speak in first person and share personal experiences.""",
    },
}


def generate_script(
    transcript: str,
    channel: str,
    topic: str = "",
    word_count_target: int = 1500,
) -> Dict[str, str]:
    if channel not in CHANNEL_PERSONAS:
        raise ValueError(f"Unknown channel: {channel}")
    
    persona = CHANNEL_PERSONAS[channel]
    
    prompt = f"""You are {persona['name']}.

{persona['persona']}

TASK: Rewrite the following viral video transcript into an ORIGINAL, engaging script.
The script MUST be at least {word_count_target} words to qualify for YouTube mid-roll ads.

IMPORTANT RULES:
1. The script MUST be at least {word_count_target} words. Count your words carefully.
2. Make it ORIGINAL - rewrite completely, do not copy phrases directly.
3. Add personal opinions, anecdotes, and commentary to make it unique.
4. Structure with a hook (first 30 seconds), main content, and strong CTA.
5. Include natural ad-break points every 2-3 minutes for mid-roll placement.
6. Make it sound 100% human - conversational, not robotic.

OUTPUT FORMAT (JSON):
{{
    "title": "SEO-optimized YouTube title (40-70 characters, with keywords)",
    "script": "The full 1500+ word script with natural paragraph breaks",
    "description": "YouTube description (100+ words, with keywords and timestamps)",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}

SOURCE TRANSCRIPT:
{transcript[:3000]}

TOPIC: {topic if topic else "General topic based on transcript"}

Generate the JSON output now:"""
    
    print(f"\n[SCRIPTWRITER] Generating script for {persona['name']}...")
    print(f"[SCRIPTWRITER] Source transcript: {len(transcript)} chars")
    print(f"[SCRIPTWRITER] Target: {word_count_target}+ words")
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    
    try:
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        result = json.loads(response_text)
        
        script_words = len(result.get("script", "").split())
        print(f"[SCRIPTWRITER] Generated: {script_words} words")
        
        if script_words < word_count_target:
            print(f"[WARN] Script only {script_words} words, regenerating...")
            return generate_script(
                transcript,
                channel,
                topic,
                word_count_target,
            )
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse Gemini response: {e}")
        print(f"[DEBUG] Response text: {response.text[:500]}")
        
        return {
            "title": topic or "Untitled Video",
            "script": response.text,
            "description": "Video description",
            "keywords": ["AI", "technology", "future"],
        }


def generate_seo_metadata(script_data: Dict, channel: str) -> Dict:
    persona = CHANNEL_PERSONAS.get(channel, CHANNEL_PERSONAS["channel_1"])
    
    prompt = f"""You are an expert YouTube SEO specialist.

Analyze this video script and generate optimized metadata:

TITLE: {script_data.get('title', '')}
SCRIPT EXCERPT: {script_data.get('script', '')[:500]}

Generate improved SEO metadata:
{{
    "title": "Improved clickbait title (40-70 chars, with main keyword)",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"],
    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
    "description": "Full YouTube description (150+ words, with timestamps, links placeholders, and keywords)"
}}

Generate the JSON now:"""
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    
    try:
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        seo_data = json.loads(response_text)
        
        script_data["seo"] = seo_data
        script_data["title"] = seo_data.get("title", script_data.get("title"))
        script_data["description"] = seo_data.get("description", script_data.get("description"))
        script_data["tags"] = seo_data.get("tags", [])
        script_data["hashtags"] = seo_data.get("hashtags", [])
        
    except Exception as e:
        print(f"[WARN] SEO enhancement failed: {e}")
    
    return script_data


def save_script(script_data: Dict, channel: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"script_{channel}_{timestamp}.json"
    filepath = SCRIPTS_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    
    txt_filename = f"script_{channel}_{timestamp}.txt"
    txt_filepath = SCRIPTS_DIR / txt_filename
    
    with open(txt_filepath, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {script_data.get('title', 'N/A')}\n\n")
        f.write(f"DESCRIPTION:\n{script_data.get('description', 'N/A')}\n\n")
        f.write(f"KEYWORDS: {', '.join(script_data.get('keywords', []))}\n\n")
        f.write("=" * 60 + "\n\n")
        f.write("SCRIPT:\n\n")
        f.write(script_data.get("script", "N/A"))
    
    print(f"[SAVED] Script saved to: {filepath}")
    print(f"[SAVED] Text version: {txt_filepath}")
    
    return str(filepath)


def generate_full_video_script(
    channel: str,
    transcript: str,
    topic: str = "",
    enhance_seo: bool = True,
) -> Dict:
    print(f"\n{'='*60}")
    print(f"SCRIPT GENERATION PIPELINE")
    print(f"Channel: {CHANNEL_PERSONAS[channel]['name']}")
    print(f"{'='*60}")
    
    script_data = generate_script(transcript, channel, topic)
    
    if enhance_seo:
        script_data = generate_seo_metadata(script_data, channel)
    
    save_script(script_data, channel)
    
    word_count = len(script_data.get("script", "").split())
    print(f"\n[COMPLETE] Script generated successfully!")
    print(f"[STATS] Words: {word_count}")
    print(f"[STATS] Title: {script_data.get('title', 'N/A')[:60]}")
    
    return script_data


if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPTWRITER - TEST MODE")
    print("=" * 60)
    
    test_transcript = """
    Artificial intelligence is changing everything. We're seeing tools that can write code,
    generate images, create music, and even have conversations. The question is - how can
    you use these tools to make money? Well, there are several ways. First, you can use
    AI to create content faster. Second, you can automate repetitive tasks. Third, you
    can build AI-powered products. Let me break down the top three AI tools that are
    changing the game right now.
    """
    
    try:
        result = generate_full_video_script(
            channel="channel_1",
            transcript=test_transcript,
            topic="Top 3 AI Tools That Feel Illegal to Know",
            enhance_seo=True,
        )
        
        print("\n[TEST RESULT]")
        print(f"Title: {result.get('title')}")
        print(f"Words: {len(result.get('script', '').split())}")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        print("[HINT] Check GEMINI_API_KEY in config.py")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
