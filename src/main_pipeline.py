"""
main_pipeline.py
----------------
Master orchestration script that ties all modules together.
Runs the complete daily content generation pipeline:
1. Trend Sniffer → Find viral topics
2. Scriptwriter → Generate 1500+ word scripts
3. Media Generator → Create images + voice
4. Video Assembler → Stitch everything
5. YouTube Uploader → Upload as Private

Focus: Channel 1 only (Aria Future)
NO .env dependency - uses config.py

Usage:
    python src/main_pipeline.py                  # Run Channel 1
    python src/main_pipeline.py --test           # Test mode (no upload)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import ACTIVE_CHANNELS, CHANNELS
from trend_sniffer import get_trending_topics, analyze_viral_potential
from scriptwriter import generate_full_video_script
from media_generator import generate_video_visuals, generate_full_audio
from video_assembler import assemble_video, generate_thumbnail
from youtube_uploader import upload_video, batch_upload

DATA_DIR = Path(__file__).parent.parent / "data"
VIDEOS_DIR = DATA_DIR / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

DAILY_TARGETS = {
    "longform": 2,
    "shorts": 4,
}


def run_trend_sniffer(channel: str, max_results: int = 5) -> list:
    print(f"\n{'='*60}")
    print(f"STEP 1: TREND SNIFFER - {channel}")
    print(f"{'='*60}")
    
    videos = get_trending_topics(channel, max_results)
    scored = analyze_viral_potential(videos)
    
    print(f"[TRENDS] Found {len(scored)} trending topics")
    
    if not scored:
        print("[WARN] No trends found, using fallback topic")
        scored = [{
            "title": "AI Tools 2026",
            "transcript": "AI tools are changing the world. Here are the top tools you need to know about.",
            "query": "AI tools 2026",
        }]
    
    return scored


def run_scriptwriter(channel: str, trends: list, num_scripts: int = 2) -> list:
    print(f"\n{'='*60}")
    print(f"STEP 2: SCRIPTWRITER - {channel}")
    print(f"{'='*60}")
    
    scripts = []
    
    for i, trend in enumerate(trends[:num_scripts], 1):
        print(f"\n[SCRIPT {i}/{num_scripts}]")
        print(f"[TOPIC] {trend.get('title', 'Unknown')[:60]}...")
        
        try:
            script_data = generate_full_video_script(
                channel=channel,
                transcript=trend.get("transcript", ""),
                topic=trend.get("title", ""),
                enhance_seo=True,
            )
            scripts.append(script_data)
            
            word_count = len(script_data.get("script", "").split())
            print(f"[SUCCESS] Script {i}: {word_count} words")
            
        except Exception as e:
            print(f"[ERROR] Script generation failed: {e}")
            continue
    
    print(f"\n[SCRIPTWRITER] Generated {len(scripts)} scripts")
    return scripts


def run_media_generator(channel: str, scripts: list) -> list:
    print(f"\n{'='*60}")
    print(f"STEP 3: MEDIA GENERATOR - {channel}")
    print(f"{'='*60}")
    
    media_list = []
    
    for i, script in enumerate(scripts, 1):
        print(f"\n[MEDIA {i}/{len(scripts)}]")
        
        script_text = script.get("script", "")
        title = script.get("title", "Untitled")
        
        try:
            print("[IMAGES] Generating SDXL images...")
            image_paths = generate_video_visuals(
                prompt=title,
                channel=channel,
                num_images=10,
            )
            
            print("[VOICE] Generating XTTS-v2 voiceover...")
            audio_path = generate_full_audio(
                script=script_text,
                channel=channel,
            )
            
            media_list.append({
                "script": script,
                "image_paths": image_paths,
                "audio_path": audio_path,
            })
            
            print(f"[SUCCESS] Media {i}: {len(image_paths)} images, audio ready")
            
        except Exception as e:
            print(f"[ERROR] Media generation failed: {e}")
            continue
    
    print(f"\n[MEDIA] Generated media for {len(media_list)} videos")
    return media_list


def run_video_assembler(channel: str, media_list: list) -> list:
    print(f"\n{'='*60}")
    print(f"STEP 4: VIDEO ASSEMBLER - {channel}")
    print(f"{'='*60}")
    
    videos = []
    
    for i, media in enumerate(media_list, 1):
        print(f"\n[ASSEMBLY {i}/{len(media_list)}]")
        
        script = media["script"]
        image_paths = media["image_paths"]
        audio_path = media["audio_path"]
        
        try:
            print("[VIDEO] Assembling long-form video...")
            video_path = assemble_video(
                image_paths=image_paths,
                audio_path=audio_path,
                subtitle_text=script.get("script", ""),
                channel=channel,
                output_size=(1920, 1080),
                is_short=False,
            )
            
            print("[THUMBNAIL] Generating thumbnail...")
            thumbnail_path = video_path.replace(".mp4", "_thumb.jpg")
            if image_paths:
                generate_thumbnail(
                    image_path=image_paths[0],
                    title=script.get("title", "Video"),
                    output_path=thumbnail_path,
                )
            
            videos.append({
                "video_path": video_path,
                "thumbnail_path": thumbnail_path,
                "title": script.get("title", "Untitled Video"),
                "description": script.get("description", ""),
                "tags": script.get("tags", []),
                "keywords": script.get("keywords", []),
                "word_count": len(script.get("script", "").split()),
            })
            
            print(f"[SUCCESS] Video {i}: {video_path}")
            
        except Exception as e:
            print(f"[ERROR] Video assembly failed: {e}")
            continue
    
    print(f"\n[ASSEMBLER] Assembled {len(videos)} videos")
    return videos


def run_youtube_uploader(channel: str, videos: list) -> list:
    print(f"\n{'='*60}")
    print(f"STEP 5: YOUTUBE UPLOADER - {channel}")
    print(f"{'='*60}")
    
    for video in videos:
        hashtags = video.get("keywords", [])[:3]
        hashtag_str = " ".join([f"#{tag.replace(' ', '')}" for tag in hashtags])
        video["description"] = f"{video['description']}\n\n{hashtag_str}"
    
    results = batch_upload(videos, channel, privacy_status="private")
    
    return results


def run_pipeline(test_mode: bool = False):
    print("\n" + "="*60)
    print("🤖 AI CONTENT NETWORK - DAILY PIPELINE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Active Channel: Aria Future (Channel 1)")
    print("="*60)
    
    all_results = {}
    
    for ch in ACTIVE_CHANNELS:
        print(f"\n\n{'#'*60}")
        print(f"# PROCESSING: {CHANNELS[ch]['name']}")
        print(f"{'#'*60}")
        
        try:
            trends = run_trend_sniffer(ch, max_results=3)
            
            scripts = run_scriptwriter(ch, trends, num_scripts=DAILY_TARGETS["longform"])
            
            if not scripts:
                print(f"[SKIP] No scripts generated for {ch}")
                continue
            
            media_list = run_media_generator(ch, scripts)
            
            videos = run_video_assembler(ch, media_list)
            
            if not test_mode:
                results = run_youtube_uploader(ch, videos)
                all_results[ch] = results
            else:
                print("\n[TEST MODE] Skipping YouTube upload")
                all_results[ch] = [{"success": True, "test": True}]
            
        except Exception as e:
            print(f"\n[ERROR] Pipeline failed for {ch}: {e}")
            all_results[ch] = [{"success": False, "error": str(e)}]
    
    print("\n\n" + "="*60)
    print("📊 DAILY PIPELINE SUMMARY")
    print("="*60)
    
    for ch, results in all_results.items():
        success = sum(1 for r in results if r.get("success"))
        total = len(results)
        print(f"[{CHANNELS[ch]['name']}] {success}/{total} uploaded successfully")
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    
    return all_results


if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    run_pipeline(test_mode=test_mode)
