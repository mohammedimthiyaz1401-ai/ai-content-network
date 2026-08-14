"""
media_generator.py
-----------------
Replicate API integration for:
- SDXL image generation (Stable Diffusion XL)
- XTTS-v2 voice synthesis (Coqui TTS)

Uses tenacity for retry logic with exponential backoff.
"""

import os
import replicate
import requests
from pathlib import Path
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"
AUDIO_DIR = DATA_DIR / "audio"

# Create directories if they don't exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Channel-specific face seeds for consistency
CHANNEL_SEEDS = {
    "channel_1": 12345,  # AI Influencer - fixed female face
    "channel_2": 0,      # No face needed (news visuals)
    "channel_3": 0,      # No face needed (mystery visuals)
}

# Voice configurations per channel
VOICE_CONFIG = {
    "channel_1": {
        "voice": "en-US-JennyNeural",  # Professional female
        "style": "cheerful",
    },
    "channel_2": {
        "voice": "en-US-AriaNeural",  # News anchor
        "style": "newscast-formal",
    },
    "channel_3": {
        "voice": "en-US-GuyNeural",  # Deep mysterious
        "style": "narration-professional",
    },
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_image_sdxl(prompt: str, channel: str = "channel_1", width: int = 1024, height: int = 1024) -> str:
    """
    Generate an image using Stable Diffusion XL via Replicate.
    
    Args:
        prompt: Text description of the image
        channel: Channel name for seed consistency
        width: Image width (default 1024)
        height: Image height (default 1024)
    
    Returns:
        Path to saved image file
    """
    seed = CHANNEL_SEEDS.get(channel, 0)
    
    input_params = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_outputs": 1,
        "guidance_scale": 7.5,
        "num_inference_steps": 50,
    }
    
    # Add seed for face consistency (only for Channel 1)
    if seed > 0:
        input_params["seed"] = seed
    
    print(f"[SDXL] Generating image for {channel}...")
    print(f"[SDXL] Prompt: {prompt[:100]}...")
    
    output = replicate.run(
        "stability-ai/sdxl:latest",
        input=input_params
    )
    
    # output is a list of URLs
    image_url = output[0]
    
    # Download and save
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
    """
    Generate voice audio using XTTS-v2 via Replicate.
    
    Args:
        text: Script text to convert to speech
        channel: Channel name for voice selection
        cleanup: Enable cleanup_voice for studio quality
    
    Returns:
        Path to saved audio file
    """
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
    
    # output is a URL to the audio file
    audio_url = output
    
    # Download and save
    filename = f"{channel}_voice_{hash(text) % 10000}.wav"
    filepath = AUDIO_DIR / filename
    
    response = requests.get(audio_url, timeout=120)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    print(f"[XTTS] Audio saved: {filepath}")
    return str(filepath)


def generate_video_visuals(prompt: str, channel: str, num_images: int = 10) -> list:
    """
    Generate multiple images for a single video.
    
    Args:
        prompt: Base prompt for the video
        channel: Channel name
        num_images: Number of images to generate (10-15 per video)
    
    Returns:
        List of image file paths
    """
    image_paths = []
    
    for i in range(num_images):
        # Add variation to each image
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
    """
    Generate complete voiceover audio from script.
    
    Args:
        script: Full 1500+ word script
        channel: Channel name
    
    Returns:
        Path to saved audio file
    """
    # Clean script for TTS
    clean_script = script.strip().replace("\n", " ")
    
    # XTTS-v2 has a character limit per call
    # For long scripts, we may need to chunk
    MAX_CHARS = 5000
    
    if len(clean_script) <= MAX_CHARS:
        return generate_voice_xtts(clean_script, channel)
    
    # Chunk long scripts
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
    
    # Generate audio for each chunk
    audio_files = []
    for i, chunk in enumerate(chunks):
        try:
            path = generate_voice_xtts(chunk, channel)
            audio_files.append(path)
        except Exception as e:
            print(f"[ERROR] Failed to generate chunk {i+1}: {e}")
            continue
    
    # Note: For now, we return the last chunk
    # Full audio concatenation will be handled by video_assembler.py
    if audio_files:
        return audio_files[-1]
    
    raise Exception("Failed to generate any audio chunks")


# Quick test function
if __name__ == "__main__":
    print("=" * 50)
    print("MEDIA GENERATOR - TEST MODE")
    print("=" * 50)
    
    # Test image generation
    test_prompt = "25 year old attractive female tech influencer, modern luxury apartment, wearing blazer, professional lighting, photorealistic"
    
    try:
        image_path = generate_image_sdxl(test_prompt, "channel_1")
        print(f"[SUCCESS] Image generated: {image_path}")
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
    
    # Test voice generation
    test_script = "Welcome to Aria Future. Today we're going to explore three AI tools that feel illegal to know. Let's dive in."
    
    try:
        audio_path = generate_voice_xtts(test_script, "channel_1")
        print(f"[SUCCESS] Voice generated: {audio_path}")
    except Exception as e:
        print(f"[ERROR] Voice generation failed: {e}")
    
    print("=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
