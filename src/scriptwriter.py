"""
scriptwriter.py
---------------
Uses Google Gemini API to generate 1500+ word scripts from viral transcripts.
Includes SEO optimization for titles and descriptions.

Cost: $0 (Gemini free tier)
"""

import os
import json
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    "channel_2": {
        "name": "Future Intelligence News",
        "persona": """You are a premium, faceless news anchor for Future Intelligence News.
Your tone is authoritative, professional, and slightly futuristic.
You deliver breaking news about AI breakthroughs, crypto, space, and future tech.
You use phrases like 'Breaking news', 'In a groundbreaking development', and 'Here's what you need to know'.
You speak in third person and cite sources.""",
    },
    "channel_3": {
        "name": "The Mystery Algorithm",
        "persona": """You are the narrator for The Mystery Algorithm - a deep, mysterious voice.
Your tone is suspenseful, intriguing, and slightly eerie.
You explore internet mysteries, psychology hacks, and viral Reddit stories.
You use phrases like 'What if I told you', 'The truth is stranger than fiction', and 'Nobody knows for sure'.
You speak in second person, drawing the listener into the mystery.""",
    },
}


def generate_script(
    transcript: str,
    channel: str,
    topic: str = "",
    word_count_target: int = 1500,
) -> Dict[str, str]:
    """
    Generate a 1500+ word script from a viral transcript using Gemini.
    
    Args:
        transcript: Source transcript to rewrite
        channel: Channel identifier
        topic: Video topic/title
        word_count_target: Target word count (minimum 1500)
    
    Returns:
        Dict with title, script, description, keywords
    """
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
    
    model = genai.GenerativeModel("gemini-pro")
    
    response = model.generate_content(prompt)
    
    # Parse response
    try:
        # Clean up response text
        response_text = response.text.strip()
        
        # Remove markdown code block if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        result = json.loads(response_text)
        
        # Validate word count
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
        
        # Return raw response as fallback
        return {
            "title": topic or "Untitled Video",
            "script": response.text,
            "description": "Video description",
            "keywords": ["AI", "technology", "future"],
        }


def generate_seo_metadata(script_data: Dict, channel: str) -> Dict:
    """
    Generate enhanced SEO metadata using Gemini.
    
    Args:
        script_data: Generated script data
        channel: Channel identifier
    
    Returns:
        Enhanced script data with SEO metadata
    """
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
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    try:
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        seo_data = json.loads(response_text)
        
        # Merge with original script data
        script_data["seo"] = seo_data
        script_data["title"] = seo_data.get("title", script_data.get("title"))
        script_data["description"] = seo_data.get("description", script_data.get("description"))
        script_data["tags"] = seo_data.get("tags", [])
        script_data["hashtags"] = seo_data.get("hashtags", [])
        
    except Exception as e:
        print(f"[WARN] SEO enhancement failed: {e}")
    
    return script_data


def save_script(script_data: Dict, channel: str) -> str:
    """
    Save generated script to file.
    
    Args:
        script_data: Script content
        channel: Channel identifier
    
    Returns:
        Path to saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"script_{channel}_{timestamp}.json"
    filepath = SCRIPTS_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    
    # Also save plain text version
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
    """
    Complete script generation pipeline.
    
    Args:
        channel: Channel identifier
        transcript: Source viral transcript
        topic: Video topic
        enhance_seo: Whether to add SEO metadata
    
    Returns:
        Complete script data dict
    """
    print(f"\n{'='*60}")
    print(f"SCRIPT GENERATION PIPELINE")
    print(f"Channel: {CHANNEL_PERSONAS[channel]['name']}")
    print(f"{'='*60}")
    
    # Step 1: Generate main script
    script_data = generate_script(transcript, channel, topic)
    
    # Step 2: Enhance SEO if requested
    if enhance_seo:
        script_data = generate_seo_metadata(script_data, channel)
    
    # Step 3: Save to files
    save_script(script_data, channel)
    
    # Step 4: Log stats
    word_count = len(script_data.get("script", "").split())
    print(f"\n[COMPLETE] Script generated successfully!")
    print(f"[STATS] Words: {word_count}")
    print(f"[STATS] Title: {script_data.get('title', 'N/A')[:60]}")
    
    return script_data


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPTWRITER - TEST MODE")
    print("=" * 60)
    
    # Test transcript
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
        print("[HINT] Make sure GEMINI_API_KEY is set in .env")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
