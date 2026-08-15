"""
main_pipeline.py
----------------
Master orchestration script that ties all modules together.
Runs the complete daily content generation pipeline:
1. Trend Sniffer → Find viral topics
2. Scriptwriter → Generate 1500+ word scripts
3. Media Generator → Create images + voice
4. Video Assembler → Stitch everything
5. Validator → Quality gates (8-min minimum, thumbnail, audio, resolution)
6. YouTube Uploader → Upload as Private (only videos that pass gates)
7. Reporter → Daily report vs targets (did we hit 2 long + 4 shorts?)

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

from config import ACTIVE_CHANNELS, CHANNELS, LONGFORM_TARGET, SHORTS_TARGET
from trend_sniffer import get_trending_topics, analyze_viral_potential
from scriptwriter import generate_full_video_script
from media_generator import (
    generate_video_visuals, generate_full_audio,
    get_fallback_log, clear_fallback_log,
)
from video_assembler import assemble_video, generate_thumbnail
from shorts_clipper import clip_shorts
from sadtalker_host import generate_host_intro, get_host_portrait
from youtube_uploader import upload_video, batch_upload
from validation import validate_video
from reporting import build_report, render_human, save_report
from telegram_notifier import send_report as send_telegram_report
from diagnostics import (
    record_error, get_errors, clear_errors,
    get_system_info, render_diagnostics,
)

DATA_DIR = Path(__file__).parent.parent / "data"
VIDEOS_DIR = DATA_DIR / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

DAILY_TARGETS = {
    "longform": LONGFORM_TARGET,
    "shorts": SHORTS_TARGET,
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
            record_error("scriptwriter", e)
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
            
            # Determine if we had to fall back to a lower-quality method
            # by inspecting the fallback log entries produced for this video.
            log = get_fallback_log()
            used_fallback = any(
                e.get("status") == "fallback_used" for e in log
            )
            silent_audio = any(
                e.get("method") == "Silent Audio" for e in log
            )
            
            media_list.append({
                "script": script,
                "image_paths": image_paths,
                "audio_path": audio_path,
                "degraded": used_fallback,
                "silent_audio": silent_audio,
            })
            
            quality = "DEGRADED (fallback used)" if used_fallback else "PREMIUM"
            print(f"[SUCCESS] Media {i}: {len(image_paths)} images, audio ready [{quality}]")
            
        except Exception as e:
            print(f"[ERROR] Media generation failed: {e}")
            record_error("media_generator", e)
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
            # TALKING HOST: generate intro + one transition clip (uses a dedicated
            # host PORTRAIT with a real face - topic images fail SadTalker face detection)
            host_clips = []
            host_degraded = False
            host_portrait = get_host_portrait()
            if host_portrait:
                intro_line = script.get("hook", "")[:90] or script.get("title", "Welcome back to Aria Future.")[:90]
                print("[HOST] Generating talking-host intro...")
                host_intro = generate_host_intro(
                    host_image=host_portrait,
                    channel=channel,
                    line=intro_line,
                )
                if host_intro["clip_path"]:
                    host_clips.append(host_intro["clip_path"])
                host_degraded = host_degraded or host_intro.get("degraded", True)
                
                if len(image_paths) > 5:
                    print("[HOST] Generating talking-host transition...")
                    host_trans = generate_host_intro(
                        host_image=host_portrait,
                        channel=channel,
                        line="Let's get into it.",
                    )
                    if host_trans["clip_path"]:
                        host_clips.append(host_trans["clip_path"])
                    host_degraded = host_degraded or host_trans.get("degraded", True)
            else:
                print("[HOST] No host portrait found - skipping talking host")
            
            print("[VIDEO] Assembling long-form video...")
            video_path = assemble_video(
                image_paths=image_paths,
                audio_path=audio_path,
                subtitle_text=script.get("script", ""),
                channel=channel,
                output_size=(1920, 1080),
                is_short=False,
                host_clips=host_clips,
            )
            
            print("[THUMBNAIL] Generating thumbnail...")
            thumbnail_path = video_path.replace(".mp4", "_thumb.jpg")
            if image_paths:
                generate_thumbnail(
                    image_path=image_paths[0],
                    title=script.get("title", "Video"),
                    output_path=thumbnail_path,
                )
            
            video_entry = {
                "video_path": video_path,
                "thumbnail_path": thumbnail_path,
                "title": script.get("title", "Untitled Video"),
                "description": script.get("description", ""),
                "tags": script.get("tags", []),
                "keywords": script.get("keywords", []),
                "word_count": len(script.get("script", "").split()),
                "is_short": False,
                "degraded": media.get("degraded", False) or host_degraded,
                "silent_audio": media.get("silent_audio", False),
            }
            
            # QUALITY GATE: validate before treating as success
            validation = validate_video(
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                video_info=video_entry,
                is_short=False,
                target_size=(1920, 1080),
            )
            video_entry["validation"] = validation
            videos.append(video_entry)

            if validation["passed"]:
                print(f"[SUCCESS] Video {i} PASSED all quality gates: {video_path}")
                print(f"         Duration {validation['metadata'].get('duration',0):.0f}s "
                      f"res {validation['metadata'].get('width',0)}x{validation['metadata'].get('height',0)}")
            else:
                failed = [k for k, c in validation["checks"].items() if not c["passed"]]
                print(f"[VETO] Video {i} FAILED gates {failed}: will not be uploaded")
            
        except Exception as e:
            print(f"[ERROR] Video assembly failed: {e}")
            record_error("video_assembler", e)
            continue
    
    print(f"\n[ASSEMBLER] Assembled {len(videos)} videos")
    return videos


def run_shorts_clipper(channel: str, videos: list) -> list:
    """
    Clip N shorts from each PASSED, non-degraded long-form video.
    This is the 'clip from long-form' strategy - zero extra API cost.
    """
    print(f"\n{'='*60}")
    print(f"STEP 4.5: SHORTS CLIPPER - {channel}")
    print(f"{'='*60}")

    shorts = []

    # Only clip from long videos that passed quality gates AND are premium quality
    sources = [
        v for v in videos
        if not v.get("is_short")
        and v.get("validation", {}).get("passed")
        and not v.get("degraded")
        and not v.get("silent_audio")
    ]

    per_video = max(1, DAILY_TARGETS["shorts"] // max(1, len(sources)))

    for v in sources:
        print(f"[SHORTS] Clipping from: {v['title'][:40]}")
        clips = clip_shorts(
            video_path=v["video_path"],
            channel=channel,
            num_shorts=per_video,
            title=v["title"],
        )
        for c in clips:
            c["validation"] = validate_video(
                video_path=c["video_path"],
                thumbnail_path="",  # shorts use frame, no separate thumb needed
                video_info={"title": c["title"], "description": v["description"],
                            "tags": v["tags"]},
                is_short=True,
                target_size=(1080, 1920),
            )
            c["degraded"] = False
            c["silent_audio"] = False
            c["description"] = v["description"]
            c["tags"] = v.get("tags", [])
            c["keywords"] = v.get("keywords", [])
        shorts.extend(clips)

    print(f"\n[SHORTS] Generated {len(shorts)} shorts")
    return shorts


def run_youtube_uploader(channel: str, videos: list) -> list:
    print(f"\n{'='*60}")
    print(f"STEP 5: YOUTUBE UPLOADER - {channel}")
    print(f"{'='*60}")
    
    # Policy: only upload videos that PASSED quality gates AND were NOT degraded.
    # Degraded / silent videos are NOT auto-uploaded (they need human review).
    valid_videos = [v for v in videos
                    if v.get("validation", {}).get("passed")
                    and not v.get("degraded")
                    and not v.get("silent_audio")]
    rejected = [v for v in videos if v not in valid_videos]
    
    if rejected:
        print(f"[GATE] {len(rejected)} video(s) held back from auto-upload:")
        for v in rejected:
            reasons = []
            if v.get("degraded"):
                reasons.append("used fallback method")
            if v.get("silent_audio"):
                reasons.append("silent audio")
            if not v.get("validation", {}).get("passed"):
                failed = [k for k, c in v.get("validation", {}).get("checks", {}).items()
                          if not c["passed"]]
                reasons.append(f"failed gates: {failed}")
            print(f"         - {v['title']}: {', '.join(reasons)} [NEEDS REVIEW]")
    
    for video in valid_videos:
        hashtags = video.get("keywords", [])[:3]
        hashtag_str = " ".join([f"#{tag.replace(' ', '')}" for tag in hashtags])
        video["description"] = f"{video['description']}\n\n{hashtag_str}"
    
    results = batch_upload(valid_videos, channel, privacy_status="private")
    
    # Record upload status onto videos for the report
    for video, res in zip(valid_videos, results):
        video["uploaded"] = res.get("success", False)
    
    return results


def run_pipeline(test_mode: bool = False):
    print("="*60)
    print("AI CONTENT NETWORK - DAILY PIPELINE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Active Channel: Aria Future (Channel 1)")
    print("="*60)
    
    all_results = {}
    all_videos_report = {}
    
    for ch in ACTIVE_CHANNELS:
        print(f"\n\n{'#'*60}")
        print(f"# PROCESSING: {CHANNELS[ch]['name']}")
        print(f"{'#'*60}")
        
        try:
            clear_fallback_log()  # reset method-failure log for this run
            clear_errors()        # reset diagnostics for this run
            
            trends = run_trend_sniffer(ch, max_results=3)
            
            scripts = run_scriptwriter(ch, trends, num_scripts=DAILY_TARGETS["longform"])
            
            if not scripts:
                print(f"[SKIP] No scripts generated for {ch}")
                all_results[ch] = [{"success": False, "error": "No scripts"}]
                continue
            
            media_list = run_media_generator(ch, scripts)
            
            videos = run_video_assembler(ch, media_list)
            
            # Clip shorts from passing premium long-form videos
            shorts = run_shorts_clipper(ch, videos)
            videos.extend(shorts)
            
            if not test_mode:
                results = run_youtube_uploader(ch, videos)
                all_results[ch] = results
            else:
                print("\n[TEST MODE] Skipping YouTube upload")
                for v in videos:
                    v["uploaded"] = False
                all_results[ch] = [{"success": True, "test": True}]
            
            # Build + save the daily validation report (includes fallback method log)
            report = build_report(
                channel=ch,
                videos=videos,
                test_mode=test_mode,
                targets=DAILY_TARGETS,
                fallback_log=get_fallback_log(),
            )
            all_videos_report[ch] = report
            path = save_report(report, ch)
            print(f"\n[REPORT] Daily report saved: {path}")
            print(render_human(report))
            
            # Push the report + diagnostics to Telegram (no-op if not configured)
            human = render_human(report)
            diagnostics = render_diagnostics(get_errors(), get_system_info())
            telegram_text = f"{human}\n\n{diagnostics}"
            send_telegram_report(telegram_text)
            
        except Exception as e:
            record_error("pipeline", e)
            print(f"\n[ERROR] Pipeline failed for {ch}: {e}")
            all_results[ch] = [{"success": False, "error": str(e)}]
            # Still push a failure report to Telegram
            try:
                diagnostics = render_diagnostics(get_errors(), get_system_info())
                send_telegram_report(
                    f"<b>Pipeline FAILED for {CHANNELS[ch]['name']}</b>\n\n{diagnostics}"
                )
            except Exception:
                pass
    
    print("\n\n" + "="*60)
    print("DAILY PIPELINE SUMMARY")
    print("="*60)
    
    for ch, results in all_results.items():
        success = sum(1 for r in results if r.get("success"))
        total = len(results)
        print(f"[{CHANNELS[ch]['name']}] {success}/{total} uploaded successfully")
    
    # Targets summary
    print("\n" + "="*60)
    print("TARGETS CHECK")
    print("="*60)
    for ch, report in all_videos_report.items():
        counts = report["counts"]
        met = report["targets_met"]
        print(f"[{CHANNELS[ch]['name']}] "
              f"Long: {counts['longform_passed']}/{counts['longform_target']} ({'MET' if met['longform'] else 'MISSED'}) | "
              f"Shorts: {counts['shorts_passed']}/{counts['shorts_target']} ({'MET' if met['shorts'] else 'MISSED'})")
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    
    return all_results


if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    run_pipeline(test_mode=test_mode)