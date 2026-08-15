"""
local_models.py
---------------
Local (GPU server) alternatives for every Replicate call in the pipeline.

When running on a rented GPU server (RunPod/Vast.ai) with USE_LOCAL_MODELS=1,
these replace the paid Replicate API:
  - SDXL image generation   -> diffusers + local SDXL weights
  - XTTS-v2 voice synthesis -> Coqui TTS local inference
  - SadTalker talking host  -> official SadTalker inference.py (subprocess)

They keep the SAME function signatures as media_generator / sadtalker_host
so the pipeline needs zero changes. Falls back to Replicate if local models
aren't installed (dev machines / GitHub Actions).

Enabled via env var USE_LOCAL_MODELS=1 (set in runpod_entrypoint.sh).
Model weights are stored under /models (set by provisioning).
"""

import os
import sys
import time
import random
import subprocess
from pathlib import Path

LOCAL_MODEL_DIR = Path(os.getenv("LOCAL_MODEL_DIR", "/models"))


def local_available() -> bool:
    """True when USE_LOCAL_MODELS=1 AND the model dir exists (set by provisioning)."""
    if os.getenv("USE_LOCAL_MODELS", "0") != "1":
        return False
    return LOCAL_MODEL_DIR.exists()


# ---------------------------------------------------------------------
# SDXL image generation (diffusers)
# ---------------------------------------------------------------------
_sdxl_pipe = None
_last_sdxl = 0
MIN_SDXL_INTERVAL = 6  # keep VRAM free between batch generations


def _get_sdxl_pipe():
    global _sdxl_pipe
    if _sdxl_pipe is None:
        import torch
        from diffusers import DiffusionPipeline

        model = os.getenv("SDXL_LOCAL_MODEL", str(LOCAL_MODEL_DIR / "sdxl"))
        print(f"[LOCAL-SDXL] Loading {model} on {torch.cuda.get_device_name(0)}")
        _sdxl_pipe = DiffusionPipeline.from_pretrained(
            model, torch_dtype=torch.float16, variant="fp16"
        ).to("cuda")
        _sdxl_pipe.enable_attention_slicing()
    return _sdxl_pipe


def generate_image_local(
    prompt: str, seed: int, width: int = 1024, height: int = 1024
) -> str:
    """Generate an SDXL image locally; returns a path like media_generator."""
    global _last_sdxl
    import torch

    wait = max(0, MIN_SDXL_INTERVAL - (time.time() - _last_sdxl))
    if wait:
        time.sleep(wait)
    _last_sdxl = time.time()

    pipe = _get_sdxl_pipe()
    gen = torch.Generator("cuda").manual_seed(seed or random.randint(0, 2**31))

    img = pipe(
        prompt=prompt,
        negative_prompt=(
            "low quality, blurry, deformed, watermark, text, logo, "
            "extra fingers, ugly, duplicate, bad anatomy"
        ),
        num_inference_steps=30,
        guidance_scale=7.5,
        width=width,
        height=height,
        generator=gen,
    ).images[0]

    out_dir = Path(__file__).parent.parent / "data" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"local_sdxl_{int(time.time())}_{random.randint(100,999)}.png"
    img.save(path)
    return str(path)


# ---------------------------------------------------------------------
# XTTS-v2 voice (Coqui TTS local)
# ---------------------------------------------------------------------
_tts_model = None
_last_tts = 0
MIN_TTS_INTERVAL = 3


def _get_tts():
    global _tts_model
    if _tts_model is None:
        from TTS.api import TTS

        checkpoint = os.getenv("XTTS_LOCAL_MODEL", str(LOCAL_MODEL_DIR / "xtts"))
        print(f"[LOCAL-XTTS] Loading XTTS from {checkpoint}")
        _tts_model = TTS(checkpoint).to("cuda")
    return _tts_model


def generate_voice_local(text: str, speaker_wav: str, language: str = "en") -> str:
    """Synthesize voice locally; returns a path like media_generator."""
    global _last_tts

    wait = max(0, MIN_TTS_INTERVAL - (time.time() - _last_tts))
    if wait:
        time.sleep(wait)
    _last_tts = time.time()

    tts = _get_tts()
    out_dir = Path(__file__).parent.parent / "data" / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"local_tts_{int(time.time())}_{random.randint(100,999)}.wav"

    tts.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        language=language,
        file_path=str(path),
    )
    return str(path)


# ---------------------------------------------------------------------
# SadTalker talking host (official repo inference.py via subprocess)
# ---------------------------------------------------------------------
def generate_host_clip_local(
    source_image: str, audio_path: str, channel: str = "channel_1"
) -> str:
    """Run official SadTalker inference.py to animate a portrait + audio.
    Returns path to the resulting MP4."""
    repo = os.getenv("SADTALKER_LOCAL_REPO", str(LOCAL_MODEL_DIR / "sadtalker"))
    inference = Path(repo) / "inference.py"
    if not inference.exists():
        raise FileNotFoundError(
            f"SadTalker inference.py not found at {inference}. "
            f"Run scripts/runpod_provision.sh first."
        )

    out_dir = Path(__file__).parent.parent / "data" / "host_clips"
    out_dir.mkdir(parents=True, exist_ok=True)
    result_video = out_dir / f"local_host_{int(time.time())}_{random.randint(100,999)}.mp4"

    # Map the pipeline's input names to SadTalker CLI flags
    cmd = [
        sys.executable, str(inference),
        "--driven_audio", str(audio_path),
        "--source_image", str(source_image),
        "--still_mode",
        "--preprocess", "crop",
        "--enhancer", "none",
        "--result_dir", str(out_dir),
        "--cpu",  # replaced with cuda by provisioning env flag
    ]

    env = dict(os.environ)
    env["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")

    print(f"[LOCAL-SADTALKER] {' '.join(cmd)}")
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            f"SadTalker inference failed (rc={proc.returncode}):\n"
            f"{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}"
        )

    # SadTalker writes <result_dir>/<timestamp>.mp4 ; grab the newest mp4
    candidates = sorted(out_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise RuntimeError("SadTalker produced no mp4 output")
    newest = candidates[-1]
    newest.rename(result_video)
    print(f"[LOCAL-SADTALKER] Host clip saved: {result_video}")
    return str(result_video)


# ---------------------------------------------------------------------
# Dispatch helpers used by media_generator / sadtalker_host
# ---------------------------------------------------------------------
def should_use_local() -> bool:
    """Decide once per process whether to route to local models."""
    if local_available():
        print("[LOCAL] Running with local models (no Replicate cost)")
        return True
    return False
