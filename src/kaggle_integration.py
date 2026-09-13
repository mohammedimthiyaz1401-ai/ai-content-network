"""Kaggle GPU integration for AI Content Network.

Wraps the shared kaggle_gpu module with AI Content Network specific tasks.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy import to avoid hard dependency
_kaggle_gpu = None


def _get_gpu():
    """Lazy-load KaggleGPU instance."""
    global _kaggle_gpu
    if _kaggle_gpu is None:
        try:
            from kaggle_gpu import KaggleGPU, GPUTask
            _kaggle_gpu = KaggleGPU(project_name="ai-content-network")
        except Exception as e:
            logger.warning(f"Kaggle GPU init failed: {e}")
            _kaggle_gpu = False  # Mark as failed, don't retry
    return _kaggle_gpu if _kaggle_gpu is not False else None


def kaggle_generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    num_images: int = 1,
    steps: int = 30,
    guidance: float = 7.5,
) -> str:
    """Generate image via Kaggle GPU (SDXL).

    Returns: path to generated image, or empty string if Kaggle unavailable.
    """
    gpu = _get_gpu()
    if not gpu:
        return ""

    try:
        from kaggle_gpu import GPUTask
        result = gpu.run_task(
            task=GPUTask.SDXL_IMAGE,
            payload={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_images": num_images,
                "steps": steps,
                "guidance": guidance,
            },
            estimated_hours=0.15 * num_images,
        )
        if result and result.get("output_files"):
            return result["output_files"][0]
        return ""
    except Exception as e:
        logger.warning(f"Kaggle image generation failed: {e}")
        return ""


def kaggle_generate_voice(
    text: str,
    speaker_wav: str = "",
    language: str = "en",
    model: str = "tts_models/multilingual/multi-dataset/xtts_v2",
) -> str:
    """Generate voice via Kaggle GPU (XTTS).

    Returns: path to generated audio, or empty string if Kaggle unavailable.
    """
    gpu = _get_gpu()
    if not gpu:
        return ""

    try:
        from kaggle_gpu import GPUTask
        payload = {"text": text, "language": language, "model": model}
        if speaker_wav:
            payload["speaker_wav"] = speaker_wav

        result = gpu.run_task(
            task=GPUTask.XTTS_VOICE,
            payload=payload,
            estimated_hours=0.10,
        )
        if result and result.get("output_files"):
            return result["output_files"][0]
        return ""
    except Exception as e:
        logger.warning(f"Kaggle voice generation failed: {e}")
        return ""


def kaggle_animate_face(
    source_image: str,
    driven_audio: str,
) -> str:
    """Animate face via Kaggle GPU (SadTalker).

    Returns: path to generated video, or empty string if Kaggle unavailable.
    """
    gpu = _get_gpu()
    if not gpu:
        return ""

    try:
        from kaggle_gpu import GPUTask
        result = gpu.run_task(
            task=GPUTask.SADTALKER,
            payload={
                "source_image": source_image,
                "driven_audio": driven_audio,
            },
            estimated_hours=0.25,
        )
        if result and result.get("output_files"):
            return result["output_files"][0]
        return ""
    except Exception as e:
        logger.warning(f"Kaggle face animation failed: {e}")
        return ""


def kaggle_transcribe(audio_path: str, model: str = "base") -> dict:
    """Transcribe audio via Kaggle GPU (Whisper).

    Returns: transcription dict, or empty dict if Kaggle unavailable.
    """
    gpu = _get_gpu()
    if not gpu:
        return {}

    try:
        from kaggle_gpu import GPUTask
        result = gpu.run_task(
            task=GPUTask.WHISPER,
            payload={
                "audio_path": audio_path,
                "model": model,
            },
            estimated_hours=0.30,
        )
        if result and result.get("output_files"):
            import json
            with open(result["output_files"][0]) as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.warning(f"Kaggle transcription failed: {e}")
        return {}


def kaggle_status() -> dict:
    """Get Kaggle GPU integration status."""
    gpu = _get_gpu()
    if not gpu:
        return {"enabled": False, "reason": "Not configured or init failed"}
    return gpu.get_status()
