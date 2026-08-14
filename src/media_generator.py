"""
media_generator.py
-----------------
Replicate API integration for:
- SDXL image generation (Stable Diffusion XL)
- XTTS-v2 voice synthesis (Coqui TTS)

Uses tenacity for retry logic with exponential backoff.
NO .env dependency - uses config.py
"""

import os
import replicate
import requests
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from config import REPLICATE_API_TOKEN

DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"
AUDIO_DIR = DATA_DIR / "audio"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_image_sdxl(prompt: str, channel: str = "channel_1", width: int = 1024, height: int = 1024) -> str:
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
    
    print(f"[SDXL] Generating image for {channel}...")
    print(f"[SDXL] Prompt: {prompt[:100]}...")
    
    output = replicate.run(
        "stability-ai/sdxl:latest",
        input=input_params
    )
    
    image_url = output[0]
    
    filename = f"{channel}_img_{hash(prompt) % 10000}.png"
    filepath = IMAGES_DIR / filename
    
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    print(f"[SDXL] Image saved: {filepath}")
    return str(filepath)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_voice_xtts(text: str, channel: str = "channel_1", cleanup: bool = True) -> str:
    voice_config = VOICE_CONFIG.get(channel, VOICE_CONFIG["channel_1"])
    
    input_params = {
        "text": text,
        "language": "en",
        "cleanup_voice": cleanup,
    }
    
    print(f"[XTTS] Generating voice for {channel}...")
    print(f"[XTTS] Text length: {len(text)} chars")
    print(f"[XTTS] Voice: {voice_config['voice']}")
    
    output = replicate.run(
        "coqui-ai/xtts-v2",
        input=input_params
    )
    
    audio_url = output
    
    filename = f"{channel}_voice_{hash(text) % 10000}.wav"
    filepath = AUDIO_DIR / filename
    
    response = requests.get(audio_url, timeout=120)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    print(f"[XTTS] Audio saved: {filepath}")
    return str(filepath)


def generate_video_visuals(prompt: str, channel: str, num_images: int = 10) -> list:
    image_paths = []
    
    for i in range(num_images):
        varied_prompt = f"{prompt}, shot {i+1}, different angle"
        try:
            path = generate_image_sdxl(varied_prompt, channel)
            image_paths.append(path)
        except Exception as e:
            print(f"[ERROR] Failed to generate image {i+1}: {e}")
            continue
    
    print(f"[VISUALS] Generated {len(image_paths)}/{num_images} images")
    return image_paths


def generate_full_audio(script: str, channel: str) -> str:
    clean_script = script.strip().replace("\n", " ")
    
    MAX_CHARS = 5000
    
    if len(clean_script) <= MAX_CHARS:
        return generate_voice_xtts(clean_script, channel)
    
    chunks = []
    words = clean_script.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_length += len(word) + 1
        if current_length > MAX_CHARS:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    print(f"[AUDIO] Script split into {len(chunks)} chunks")
    
    audio_files = []
    for i, chunk in enumerate(chunks):
        try:
            path = generate_voice_xtts(chunk, channel)
            audio_files.append(path)
        except Exception as e:
            print(f"[ERROR] Failed to generate chunk {i+1}: {e}")
            continue
    
    if audio_files:
        return audio_files[-1]
    
    raise Exception("Failed to generate any audio chunks")


if __name__ == "__main__":
    print("=" * 50)
    print("MEDIA GENERATOR - TEST MODE")
    print("=" * 50)
    
    test_prompt = "25 year old attractive female tech influencer, modern luxury apartment, wearing blazer, professional lighting, photorealistic"
    
    try:
        image_path = generate_image_sdxl(test_prompt, "channel_1")
        print(f"[SUCCESS] Image generated: {image_path}")
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
    
    test_script = "Welcome to Aria Future. Today we're going to explore three AI tools that feel illegal to know. Let's dive in."
    
    try:
        audio_path = generate_voice_xtts(test_script, "channel_1")
        print(f"[SUCCESS] Voice generated: {audio_path}")
    except Exception as e:
        print(f"[ERROR] Voice generation failed: {e}")
    
    print("=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
