"""
validation.py
-------------
Hard quality gates that run BEFORE a video can be uploaded.
Each check returns (passed: bool, message: str).

Checks:
- MIN_DURATION: rendered video must be >= 480 seconds (8 min) for long-form
- Thumbnail: must exist and be non-empty
- File size: video must be larger than a minimum threshold
- Resolution: must match target dimensions
- Title/description: not empty
"""

import subprocess
import json
from pathlib import Path

MIN_DURATION_LONGFORM = 480   # 8 minutes
MIN_DURATION_SHORT = 15       # shorts are fine above 15s
MIN_VIDEO_SIZE_MB = 5
REQUIRED_FPS = 23.0


def probe_video(video_path: str) -> dict:
    """Use ffprobe to extract video metadata. Returns dict or raises."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    vstream = next((s for s in streams if s.get("codec_type") == "video"), None)
    astream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    format_info = data.get("format", {})
    duration = float(format_info.get("duration", 0) or 0)
    size_bytes = int(format_info.get("size", 0) or 0)

    return {
        "duration": duration,
        "size_mb": round(size_bytes / (1024 * 1024), 2),
        "width": int(vstream.get("width", 0)) if vstream else 0,
        "height": int(vstream.get("height", 0)) if vstream else 0,
        "fps": float(vstream.get("r_frame_rate", "0/0").split("/")[0]) / float(
            vstream.get("r_frame_rate", "0/1").split("/")[1]
        ) if vstream and "/" in vstream.get("r_frame_rate", "0/1") else 0.0,
        "has_audio": astream is not None,
        "codec": vstream.get("codec_name", "") if vstream else "",
    }


def check_duration(metadata: dict, is_short: bool = False) -> tuple:
    """Gate 1: video must be long enough for YouTube monetization."""
    min_dur = MIN_DURATION_SHORT if is_short else MIN_DURATION_LONGFORM
    duration = metadata.get("duration", 0)
    if duration < min_dur:
        return (False, f"Duration {duration:.0f}s < required {min_dur}s ({'short' if is_short else 'long-form'})")
    return (True, f"Duration {duration:.0f}s OK (>= {min_dur}s)")


def check_thumbnail(thumbnail_path: str, min_bytes: int = 30_000, required: bool = True) -> tuple:
    """Gate 2: thumbnail must exist and be a real image file.
    required=False for shorts (YouTube auto-generates the thumbnail frame)."""
    if not thumbnail_path or not Path(thumbnail_path).exists():
        if required:
            return (False, "Thumbnail file does not exist")
        return (True, "No thumbnail needed (short - auto-generated)")
    size = Path(thumbnail_path).stat().st_size
    if size < min_bytes:
        return (False, f"Thumbnail too small: {size} bytes < {min_bytes}")
    return (True, f"Thumbnail OK: {size} bytes")


def check_file_size(metadata: dict, min_mb: int = MIN_VIDEO_SIZE_MB, is_short: bool = False) -> tuple:
    """Gate 3: video file must be substantial (failed renders are tiny).
    Shorts have a lower floor (45s clips are naturally smaller)."""
    size_mb = metadata.get("size_mb", 0)
    threshold = 1.5 if is_short else min_mb
    if size_mb < threshold:
        return (False, f"File too small: {size_mb}MB < {threshold}MB")
    return (True, f"File size OK: {size_mb}MB")


def check_resolution(metadata: dict, target: tuple) -> tuple:
    """Gate 4: resolution must match the intended output size."""
    w, h = metadata.get("width", 0), metadata.get("height", 0)
    tw, th = target
    if (w, h) != (tw, th):
        return (False, f"Resolution {w}x{h} != target {tw}x{th}")
    return (True, f"Resolution OK: {w}x{h}")


def check_has_audio(metadata: dict) -> tuple:
    """Gate 5: must have an audio track (muted videos fail monetization)."""
    if not metadata.get("has_audio"):
        return (False, "No audio track found")
    if metadata.get("duration", 0) <= 0:
        return (False, "Video duration is zero")
    return (True, "Audio present")


def check_metadata_fields(video_info: dict) -> tuple:
    """Gate 6: title/description/tags must be non-empty (upload requirement)."""
    missing = []
    if not video_info.get("title"):
        missing.append("title")
    if not video_info.get("description"):
        missing.append("description")
    if not video_info.get("tags"):
        missing.append("tags")
    if missing:
        return (False, f"Missing {', '.join(missing)}")
    return (True, "Metadata OK")


def validate_video(
    video_path: str,
    thumbnail_path: str,
    video_info: dict,
    is_short: bool = False,
    target_size: tuple = (1920, 1080),
) -> dict:
    """
    Run ALL gates for a video. Returns result dict:
    {
      "passed": bool, "checks": {name: {"passed": bool, "message": str}}, "metadata": {...}
    }
    """
    checks = {}
    try:
        metadata = probe_video(video_path)
    except Exception as e:
        return {
            "passed": False,
            "checks": {"probe": {"passed": False, "message": str(e)}},
            "metadata": {},
        }

    gates = {
        "duration": check_duration(metadata, is_short),
        "file_size": check_file_size(metadata, is_short=is_short),
        "resolution": check_resolution(metadata, target_size),
        "audio": check_has_audio(metadata),
        "thumbnail": check_thumbnail(thumbnail_path, required=not is_short),
        "metadata_fields": check_metadata_fields(video_info),
    }

    for name, (passed, message) in gates.items():
        checks[name] = {"passed": bool(passed), "message": message}

    all_passed = all(c["passed"] for c in checks.values())
    return {"passed": all_passed, "checks": checks, "metadata": metadata}


if __name__ == "__main__":
    print("VALIDATION MODULE - self test")
    sample = {"duration": 500, "size_mb": 50, "width": 1920, "height": 1080,
              "fps": 30.0, "has_audio": True}
    print(check_duration(sample, is_short=False))
    print(check_resolution(sample, (1920, 1080)))
    print("OK")