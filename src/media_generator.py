"""
media_generator.py
----------------
Replicate API integration for:
- SDXL image generation (Stable Diffusion XL)
- XTTS-v2 voice synthesis (Coqui TTS)

Uses tenacity for retry logic with exponential backoff.
Handles Replicate rate limits (6 req/min with <$5 credit).
Includes FALLBACK CHAIN: Method 1 -> Method 2 -> Method 3.

NOTE: Must use specific model version IDs, NOT :latest tag.
"""

import os
import time
import random
import replicate
import requests
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from config import REPLICATE_API_TOKEN

DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"
AUDIO_DIR = DATA_DIR / "audio"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
VOICE_SAMPLES_DIR = ASSETS_DIR / "voice_samples"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
VOICE_SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# Expected voice-cloning sample per channel (e.g. assets/voice_samples/channel_1.wav)
VOICE_SAMPLE_FILES = {
    "channel_1": VOICE_SAMPLES_DIR / "channel_1.wav",
}


def _get_speaker_sample(channel: str) -> str:
    """Return the voice-cloning reference sample path for a channel.
    Falls back to any .wav/.mp3 in assets/voice_samples/ if the exact name is missing."""
    path = VOICE_SAMPLE_FILES.get(channel)
    if path and path.exists():
        return str(path)
    # fallback: any audio file in voice_samples dir
    samples = list(VOICE_SAMPLES_DIR.glob("*.wav")) + list(VOICE_SAMPLES_DIR.glob("*.mp3"))
    if samples:
        return str(samples[0])
    raise FileNotFoundError(
        f"No voice-cloning sample found. Add a 10-20s recording of the host voice at: "
        f"{VOICE_SAMPLES_DIR} (e.g. channel_1.wav)"
    )


def _extract_output_url(output) -> str:
    """Replicate SDK 1.x wraps URL outputs in FileOutput objects with a .url attr.
    Handle str, list, or FileOutput for maximum SDK compatibility."""
    if isinstance(output, str):
        return output
    if hasattr(output, "url"):
        return output.url
    if isinstance(output, (list, tuple)):
        return _extract_output_url(output[0])
    return str(output)


def _get_speaker_url(channel: str) -> str:
    """Upload the local speaker sample to Replicate and return its accessible URL.
    XTTS-v2 requires 'speaker' to be a URI (uploaded file), NOT a local path.
    Uploads once per process and caches the URL."""
    from datetime import datetime, timedelta
    cached = _SPEAKER_URL_CACHE.get(channel)
    if cached and cached[1] > datetime.now():
        return cached[0]

    from replicate import files
    sample_path = _get_speaker_sample(channel)
    _throttle("speaker_upload")
    print(f"[UPLOAD] Uploading speaker sample for {channel}: {Path(sample_path).name}")
    f = files.create(sample_path)
    url = f.urls["get"]
    _SPEAKER_URL_CACHE[channel] = (url, datetime.now() + timedelta(hours=23))
    print(f"[UPLOAD] Speaker URL ready (expires ~24h)")
    return url

# ============================================================
# MODEL CONFIGURATION (specific version IDs - :latest is broken)
# ============================================================
SDXL_MODEL = "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"
XTTS_MODEL = "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e"

# Rate limit: Replicate allows ~6 req/min and 1 burst with <$5 credit
MIN_REQUEST_INTERVAL = 12  # seconds between API calls
LAST_REQUEST_TIME = {}  # per-function last call time

# Cached speaker upload URL per channel (Replicate File objects expire in 24h;
# we upload once per process and reuse the URL across voice calls)
_SPEAKER_URL_CACHE = {}

# ============================================================
# FALLBACK EVENT LOG
# Every method attempt is recorded here so the daily report can
# show exactly WHAT failed and WHAT we fell back to.
# Format: {"service", "method", "status", "detail"}
# ============================================================
FALLBACK_LOG = []


def log_fallback(service: str, method: str, status: str, detail: str = ""):
    """Record a method attempt for the daily report. Detail holds full error text."""
    from datetime import datetime
    FALLBACK_LOG.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "service": service,
        "method": method,
        "status": status,  # "used" (primary), "failed", "fallback_used", "success"
        "detail": detail,
    })


def get_fallback_log() -> list:
    """Return a copy of the fallback log for the report."""
    return list(FALLBACK_LOG)


def clear_fallback_log():
    """Reset the log at the start of each pipeline run."""
    FALLBACK_LOG.clear()


def _throttle(func_name: str):
    """Enforce minimum interval between Replicate API calls to avoid 429 rate limits."""
    now = time.time()
    last = LAST_REQUEST_TIME.get(func_name, 0)
    wait_time = max(0, MIN_REQUEST_INTERVAL - (now - last))
    if wait_time > 0:
        print(f"[RATE] Waiting {wait_time:.0f}s to respect Replicate rate limit...")
        time.sleep(wait_time)
    LAST_REQUEST_TIME[func_name] = time.time()


# Channel-specific face seeds for consistency
CHANNEL_SEEDS = {
    "channel_1": 12345,  # AI Influencer - fixed female face
}

# Voice configurations per channel
VOICE_CONFIG = {
    "channel_1": {
        "voice": "en-US-JennyNeural",
        "style": "cheerful",
    },
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=15, max=60))
def generate_image_sdxl(prompt: str, channel: str = "channel_1", width: int = 1024, height: int = 1024) -> str:
    """Primary image generation method (Replicate SDXL). Uses specific version ID."""
    seed = CHANNEL_SEEDS.get(channel, 0)
    
    input_params = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_outputs": 1,
        "guidance_scale": 7.5,
        "num_inference_steps": 50,
    }
    
    if seed > 0:
        input_params["seed"] = seed
    
    _throttle("sdxl")
    print(f"[SDXL] Generating image for {channel}...")
    
    try:
        output = replicate.run(
            SDXL_MODEL,
            input=input_params,
        )
    except Exception as e:
        log_fallback("image", "SDXL Replicate", "failed", str(e)[:200])
        raise
        
    image_url = output[0] if isinstance(output, list) else output
    
    filename = f"{channel}_img_{int(time.time())}_{random.randint(100,999)}.png"
    filepath = IMAGES_DIR / filename
    
    response = requests.get(str(image_url), timeout=120)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    log_fallback("image", "SDXL Replicate", "used")
    print(f"[SDXL] Image saved: {filepath.name}")
    return str(filepath)


def generate_image_fallback(prompt: str, channel: str) -> str:
    """
    FALLBACK 2: Generate a solid-color placeholder image if Replicate SDXL fails.
    This ensures the pipeline continues even if the paid API is down.
    """
    from PIL import Image, ImageDraw, ImageFont
    
    print(f"[FALLBACK] Generating placeholder image for {channel}...")
    
    # Create a branded 1024x1024 placeholder with channel name
    img = Image.new("RGB", (1024, 1024), color=(30, 30, 60))
    draw = ImageDraw.Draw(img)
    
    # Simple gradient-ish pattern
    for x in range(0, 1024, 64):
        shade = int(30 + x / 1024 * 40)
        draw.rectangle([x, 0, x + 64, 1024], fill=(shade, shade, shade + 20))
    
    filename = f"{channel}_img_{int(time.time())}_{random.randint(100,999)}.png"
    filepath = IMAGES_DIR / filename
    img.save(filepath)
    print(f"[FALLBACK] Placeholder saved: {filepath.name}")
    return str(filepath)


def generate_image(prompt: str, channel: str = "channel_1") -> str:
    """
    FALLBACK CHAIN for image generation:
      1. Replicate SDXL (premium)
      2. Local placeholder (always works)
    Returns first successful image path.
    """
    methods = [
        ("SDXL Replicate", lambda: generate_image_sdxl(prompt, channel)),
        ("Placeholder", lambda: generate_image_fallback(prompt, channel)),
    ]
    
    for name, method in methods:
        try:
            print(f"[IMG-METHOD] Trying method: {name}")
            result = method()
            # If we did NOT use the primary method, log the fallback clearly
            if name != "SDXL Replicate":
                log_fallback("image", name, "fallback_used", "SDXL primary failed")
            return result
        except Exception as e:
            print(f"[IMG-METHOD] Method '{name}' failed: {e}")
            continue
    
    raise Exception("All image generation methods failed")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=15, max=60))
def generate_voice_xtts(text: str, channel: str = "channel_1", cleanup: bool = True) -> str:
    """Primary voice generation method (Replicate XTTS-v2).
    Requires a 'speaker' voice-cloning reference sample per channel.
    The speaker sample is uploaded to Replicate and passed as a URI."""
    voice_config = VOICE_CONFIG.get(channel, VOICE_CONFIG["channel_1"])
    speaker_url = _get_speaker_url(channel)

    input_params = {
        "text": text,
        "speaker": speaker_url,
        "language": "en",
        "cleanup_voice": cleanup,
    }
    
    _throttle("xtts")
    print(f"[XTTS] Generating voice for {channel}...")
    
    try:
        output = replicate.run(
            XTTS_MODEL,
            input=input_params,
        )
    except Exception as e:
        log_fallback("voice", "XTTS Replicate", "failed", str(e)[:200])
        raise
        
    audio_url = _extract_output_url(output)
    
    filename = f"{channel}_voice_{int(time.time())}_{random.randint(100,999)}.wav"
    filepath = AUDIO_DIR / filename
    
    response = requests.get(audio_url, timeout=300)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    log_fallback("voice", "XTTS Replicate", "used")
    print(f"[XTTS] Audio saved: {filepath.name}")
    return str(filepath)


def generate_voice_fallback(text: str, channel: str) -> str:
    """
    FALLBACK 2: Use pyttsx3 (offline TTS) if Replicate fails.
    Lower quality but ALWAYS works - ensures pipeline continues.
    """
    print(f"[FALLBACK] Generating offline voice for {channel}...")
    
    try:
        import pyttsx3
        
        temp_path = str(AUDIO_DIR / f"tts_{int(time.time())}.wav")
        engine = pyttsx3.init()
        engine.save_to_file(text[:3000], temp_path)
        engine.runAndWait()
        
        if os.path.exists(temp_path):
            print(f"[FALLBACK] Offline voice saved: {os.path.basename(temp_path)}")
            log_fallback("voice", "Offline TTS", "success")
            return temp_path
    except Exception as e:
        print(f"[FALLBACK] pyttsx3 failed: {e}")
        log_fallback("voice", "Offline TTS", "failed", str(e)[:200])
    
    # FALLBACK 3: Generate a silent audio file so the video still assembles
    print("[FALLBACK] Generating silent audio track...")
    silent_path = str(AUDIO_DIR / f"silent_{int(time.time())}.wav")
    try:
        import subprocess
        duration = max(10, len(text) // 15)
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
             "-t", str(duration), "-q:a", "9", "-acodec", "pcm_s16le", silent_path],
            capture_output=True,
        )
        if os.path.exists(silent_path) and os.path.getsize(silent_path) > 0:
            print(f"[FALLBACK] Silent audio saved: {os.path.basename(silent_path)}")
            log_fallback("voice", "Silent Audio", "fallback_used", "Both XTTS and offline TTS failed")
            return silent_path
    except Exception as e:
        print(f"[FALLBACK] Silent audio generation failed: {e}")
        log_fallback("voice", "Silent Audio", "failed", str(e)[:200])
    
    raise Exception("All voice generation methods failed")


def generate_voice(text: str, channel: str = "channel_1") -> str:
    """
    FALLBACK CHAIN for voice generation:
      1. Replicate XTTS-v2 (premium)
      2. Offline TTS (pyttsx3)
      3. Silent audio (ensures video assembles)
    Returns first successful audio path.
    """
    methods = [
        ("XTTS Replicate", lambda: generate_voice_xtts(text, channel)),
        ("Offline TTS", lambda: generate_voice_fallback(text, channel)),
    ]
    
    for name, method in methods:
        try:
            print(f"[VOICE-METHOD] Trying method: {name}")
            result = method()
            if name != "XTTS Replicate":
                log_fallback("voice", name, "fallback_used", "XTTS primary failed")
            return result
        except Exception as e:
            print(f"[VOICE-METHOD] Method '{name}' failed: {e}")
            continue
    
    raise Exception("All voice generation methods failed")


def generate_video_visuals(prompt: str, channel: str, num_images: int = 10) -> list:
    image_paths = []
    
    for i in range(num_images):
        varied_prompt = f"{prompt}, shot {i+1}, different angle"
        try:
            path = generate_image(varied_prompt, channel)
            image_paths.append(path)
        except Exception as e:
            print(f"[ERROR] Failed to generate image {i+1}: {e}")
            break
    
    print(f"[VISUALS] Generated {len(image_paths)}/{num_images} images")
    return image_paths


def generate_full_audio(script: str, channel: str) -> str:
    clean_script = script.strip().replace("\n", " ")
    
    # XTTS-v2 has character limits; chunk long scripts for TTS
    MAX_CHARS = 4000
    
    # Use offline/fallback full-audio path for reliability
    return generate_voice(clean_script[:12000], channel)


if __name__ == "__main__":
    print("=" * 50)
    print("MEDIA GENERATOR - TEST MODE")
    print("=" * 50)
    
    test_script = "Welcome to Aria Future. Today we're going to explore three AI tools that feel illegal to know. Let's dive in."
    
    # Test image with fallback chain
    try:
        img = generate_image("modern luxury apartment interior", "channel_1")
        print(f"[SUCCESS] Image: {img}")
    except Exception as e:
        print(f"[ERROR] Image failed: {e}")
    
    # Test voice with fallback chain
    try:
        audio = generate_voice(test_script, "channel_1")
        print(f"[SUCCESS] Voice: {audio}")
    except Exception as e:
        print(f"[ERROR] Voice failed: {e}")
    
    print("=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)