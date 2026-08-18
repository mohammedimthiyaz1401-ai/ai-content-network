"""
sadtalker_host.py
-----------------
Generates a real talking-host (talking head) for the videos using SadTalker
via Replicate (Apache-2.0, commercial-safe). This gives Aria Future a
professional female host who actually SPEAKS on camera, like other influencers.

Pipeline input:
  - A single host portrait image (the fixed SDXL female face, CHANNEL_SEEDS)
  - A short voice clip of the host saying the intro/transition line (XTTS voice)

SadTalker (image + audio) -> talking-head MP4 clip.

FALLBACK CHAIN:
  1. SadTalker via Replicate (premium - animated host)
  2. Static host image clip (still portrait, NO animation) - always works

This keeps the video flowing even if the paid model fails.
"""

import os
import time
import random
import replicate
import requests
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from config import REPLICATE_API_TOKEN, FREE_TIER
from media_generator import _get_speaker_sample, log_fallback, _extract_output_url

DATA_DIR = Path(__file__).parent.parent / "data"
HOST_DIR = DATA_DIR / "host_clips"
HOST_DIR.mkdir(parents=True, exist_ok=True)

# SadTalker (Apache-2.0, open source). Version pinned (NOT :latest tag).
SADTALKER_MODEL = "cjwbw/sadtalker:a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3"

# Canonical host portrait for Aria Future. SadTalker requires a REAL,
# detectable face in the source image - topic/screenshot images without a
# face cause server-side failure ("exceptions must derive from BaseException").
PORTRAIT_CANDIDATES = [
    Path(__file__).parent.parent / "assets" / "branding" / "profile.jpg",
    Path(__file__).parent.parent / "assets" / "avatars" / "candidates" / "studio_mic_spotlight.png",
    Path(__file__).parent.parent / "assets" / "avatars" / "candidates" / "bright_office_laptop.png",
    Path(__file__).parent.parent / "assets" / "avatars" / "candidates" / "library_laptop.png",
]


def get_host_portrait() -> str:
    """Return the best available host portrait (a REAL face image) or ''."""
    for p in PORTRAIT_CANDIDATES:
        if p.exists():
            return str(p)
    return ""

INSTAGRAM_REQUEST_INTERVAL = 12  # seconds (share Replicate rate limit)
_LAST_CALL = 0

# Cache of uploaded-file URLs keyed by local path (File objects expire in 24h)
_UPLOAD_CACHE = {}


def get_uploaded_uri(local_path: str) -> str:
    """Upload a local file to Replicate and return its accessible URL.
    SadTalker requires source_image and driven_audio as URIs, not local paths."""
    from datetime import datetime, timedelta
    cached = _UPLOAD_CACHE.get(local_path)
    if cached and cached[1] > datetime.now():
        return cached[0]

    from replicate import files
    _throttle()
    print(f"[UPLOAD] Uploading for SadTalker: {Path(local_path).name}")
    f = files.create(local_path)
    url = f.urls["get"]
    _UPLOAD_CACHE[local_path] = (url, datetime.now() + timedelta(hours=23))
    return url


def _throttle():
    global _LAST_CALL
    wait = max(0, INSTAGRAM_REQUEST_INTERVAL - (time.time() - _LAST_CALL))
    if wait > 0:
        print(f"[HOST] Waiting {wait:.0f}s for Replicate rate limit...")
        time.sleep(wait)
    _LAST_CALL = time.time()


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=10, max=30), reraise=True)
def generate_talking_clip_sadtalker(
    source_image: str,
    audio_path: str,
    channel: str = "channel_1",
) -> str:
    """Primary host method: SadTalker animates a single portrait + audio -> talking clip."""
    _throttle()
    print("[HOST] SadTalker: animating host portrait with voice...")

    # SadTalker requires both inputs as URIs (uploaded files, not local paths)
    source_uri = get_uploaded_uri(source_image)
    audio_uri = get_uploaded_uri(audio_path)

    input_params = {
        "source_image": source_uri,
        "driven_audio": audio_uri,
        "still_mode": True,       # steady head, professional presentation
        "preprocess": "crop",
        "facerender": "facevid2vid",
        "use_eyeblink": True,
        "use_enhancer": False,
        "pose_style": 0,
    }

    try:
        output = replicate.run(SADTALKER_MODEL, input=input_params)
        video_url = _extract_output_url(output)

        filename = f"{channel}_host_{int(time.time())}_{random.randint(100,999)}.mp4"
        filepath = HOST_DIR / filename

        resp = requests.get(video_url, timeout=300)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)

        if os.path.getsize(filepath) < 50_000:
            raise RuntimeError(f"Host clip suspiciously small: {os.path.getsize(filepath)} bytes")

        log_fallback("host", "SadTalker", "used")
        print(f"[HOST] Talking clip saved: {filepath.name} ({os.path.getsize(filepath)//1024} KB)")
        return str(filepath)

    except Exception as e:
        log_fallback("host", "SadTalker", "failed", str(e)[:200])
        raise


def generate_host_fallback(source_image: str, audio_path: str, channel: str) -> str:
    """
    FALLBACK 2: No animation - return the static portrait image as the visual.
    The pipeline overlays its own voice; the host appears as a talking-HEAD
    graphic (portrait + animated subtitle) instead of a moving avatar.
    """
    log_fallback("host", "Static portrait", "fallback_used", "SadTalker failed")
    print("[HOST] Fallback: using static host portrait (no animation)")
    return source_image  # image path; video_assembler treats it as a still clip


def generate_host_clip(
    source_image: str,
    audio_path: str,
    channel: str = "channel_1",
) -> str:
    """
    Generate the talking-host segment.
    Returns a path to either an animated MP4 (premium) or the static image (fallback).
    """
    methods = [
        ("Local SadTalker", lambda: _local_sadtalker(source_image, audio_path, channel)),
        ("SadTalker", lambda: generate_talking_clip_sadtalker(source_image, audio_path, channel)),
        ("Static portrait", lambda: generate_host_fallback(source_image, audio_path, channel)),
    ]
    for name, method in methods:
        try:
            print(f"[HOST-METHOD] Trying: {name}")
            return method()
        except Exception as e:
            print(f"[HOST-METHOD] '{name}' failed: {e}")
            continue
    raise Exception("All host methods failed")


def _local_sadtalker(source_image: str, audio_path: str, channel: str) -> str:
    """Route to local SadTalker if available; raises FileNotFoundError otherwise."""
    import local_models
    if not local_models.should_use_local():
        raise FileNotFoundError("Local models not configured (USE_LOCAL_MODELS=1 + /models)")
    return local_models.generate_host_clip_local(source_image, audio_path, channel)


# ------------------------------------------------------------------
# Convenience: voice the host says a line, then SadTalker animates it.
# ------------------------------------------------------------------
def generate_host_intro(
    host_image: str,
    channel: str,
    line: str,
) -> dict:
    """Generate a host speaking an intro/transition line.
    Returns {clip_path, is_animated, degraded}.

    In FREE_TIER mode the paid/animated path is SKIPPED entirely:
    the host appears as a static Ken-Burns portrait. This is the
    INTENDED free-tier look (not a failure -> not marked degraded).
    """
    if FREE_TIER:
        log_fallback("host", "Static portrait (FREE_TIER)", "used",
                     "Free tier: animated host skipped by design")
        print("[HOST] FREE_TIER: using static host portrait (no animation, $0)")
        return {"clip_path": host_image, "is_animated": False, "degraded": False}

    from media_generator import generate_voice_xtts
    degraded = False
    try:
        audio = generate_voice_xtts(line, channel)
    except Exception as e:
        log_fallback("host", "Intro voice", "failed", str(e)[:200])
        degraded = True
        return {"clip_path": host_image, "is_animated": False, "degraded": True}

    try:
        clip = generate_host_clip(host_image, audio, channel)
        is_animated = clip.lower().endswith(".mp4")
        return {"clip_path": clip, "is_animated": is_animated, "degraded": degraded}
    except Exception:
        return {"clip_path": host_image, "is_animated": False, "degraded": True}


if __name__ == "__main__":
    print("=" * 50)
    print("SADTALKER HOST - TEST MODE")
    print("=" * 50)
    import glob
    images = glob.glob(str(Path(__file__).parent.parent / "data" / "images" / "*.png"))
    if not images:
        print("No test image found in data/images/")
        sys_exit = 1
    else:
        test_img = images[0]
        result = generate_host_intro(
            test_img, "channel_1",
            "Welcome to Aria Future. Today we explore the AI tools changing everything.",
        )
        print(f"[HOST] clip={result['clip_path']} animated={result['is_animated']} "
              f"degraded={result['degraded']}")
    print("=" * 50)