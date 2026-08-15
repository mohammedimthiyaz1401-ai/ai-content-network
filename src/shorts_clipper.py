"""
shorts_clipper.py
-----------------
Clips N shorts (9:16 vertical) from an already-assembled long-form video.
Strategy: split the video into N evenly-spaced windows, crop the center
region to 9:16, keep audio. Zero extra API cost.

This is the "clip from long-form" approach chosen for shorts.
"""

import subprocess
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SHORTS_DIR = DATA_DIR / "shorts"
SHORTS_DIR.mkdir(parents=True, exist_ok=True)

SHORT_DURATION = 45       # seconds per short
SHORT_SIZE = "1080:1920"  # ffmpeg scale/crop target


def get_duration(video_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json", "-show_format",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 0) or 0)


def clip_short(video_path: str, start: float, output_path: str) -> str:
    """
    Extract a 9:16 vertical clip starting at `start` seconds.
    Crops the center vertical strip from the 16:9 source.
    """
    crop_filter = (
        "crop=ih*9/16:ih:(iw-ow)/2:0,"
        "scale=1080:1920:flags=lanczos"
    )
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.2f}",
        "-t", str(SHORT_DURATION),
        "-i", video_path,
        "-vf", crop_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "-shortest",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg clip failed: {result.stderr[-500:]}")
    return output_path


def clip_shorts(
    video_path: str,
    channel: str,
    num_shorts: int = 4,
    title: str = "Short",
    short_duration: int = SHORT_DURATION,
) -> list:
    """
    Clip N shorts from a long-form video.
    Returns list of dicts: {video_path, title, is_short, source}.
    """
    duration = get_duration(video_path)
    print(f"[SHORTS] Source duration: {duration:.0f}s")

    if duration < short_duration:
        print(f"[SHORTS] Video too short ({duration:.0f}s) to clip - skipping")
        return []

    # Determine number of shorts we can actually fit
    max_shorts = max(1, int(duration // short_duration))
    num_shorts = min(num_shorts, max_shorts)

    # Evenly spaced start times across the video
    if num_shorts == 1:
        starts = [0]
    else:
        total_span = duration - short_duration
        step = total_span / num_shorts
        starts = [i * step for i in range(num_shorts)]

    shorts = []
    from pathlib import Path as P

    for i, start in enumerate(starts, 1):
        output_path = str(SHORTS_DIR / f"{channel}_short_{i}_{int(__import__('time').time())}.mp4")
        print(f"[SHORTS] Clipping short {i}/{num_shorts} at {start:.0f}s...")
        try:
            path = clip_short(video_path, start, output_path)
            shorts.append({
                "video_path": path,
                "title": f"{title} #shorts",
                "is_short": True,
                "source": video_path,
            })
            print(f"[SHORTS] Short {i} done: {path}")
        except Exception as e:
            print(f"[SHORTS] Short {i} failed: {e}")
            continue

    return shorts


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python shorts_clipper.py <video.mp4> [num_shorts]")
        sys.exit(1)
    video = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    clips = clip_shorts(video, "channel_1", num_shorts=n)
    for c in clips:
        print(f"  {c['title']}: {c['video_path']}")