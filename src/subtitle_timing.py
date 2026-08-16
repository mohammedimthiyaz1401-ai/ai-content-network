"""
subtitle_timing.py
------------------
Gives subtitles REAL speech timing instead of fixed 3-second chunks.
Uses openai-whisper (base model) to transcribe the generated audio and get
segment timestamps, so captions appear exactly when each phrase is spoken.

WHY IT MATTERS: fixed 3s chunks drift from the actual voiceover; word/segment
timed captions look professional and match the strategy doc (WhisperX-style).

FAILSAFE: if whisper is unavailable/fails/model download fails, returns the
original fixed-chunk schedule so the video STILL assembles (never breaks).

Cost: $0 (local CPU). Note: base model ~140MB, transcribes 8-min audio in
~2-4 min on a GitHub Actions CPU - acceptable.
"""

import os
import time
from typing import List, Dict, Optional


def _fixed_chunks(text: str, chunk_duration: float = 3.0, chunk_size: int = 8) -> List[Dict]:
    """Fallback: evenly space chunks (matches old video_assembler behavior)."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        start = (i // chunk_size) * chunk_duration
        chunks.append({"start": start, "end": start + chunk_duration, "text": chunk})
    return chunks


def get_timed_subtitles(audio_path: str, text: str) -> List[Dict]:
    """
    Return [{start, end, text}, ...] with real speech timing.
    Falls back to fixed chunks if whisper is not available or fails.

    WHISPER_SUBTITLES env gate (default "0"):
      GitHub Actions runners are CPU-only: loading the whisper base model +
      numba JIT consumes ~100 minutes (confirmed: 09:20:40 -> 11:02:09 on a
      successful run; twice it stalled >120 min and timed out). So whisper is
      DISABLED by default. Enable with WHISPER_SUBTITLES=1 ONLY on a machine
      where it's FAST (GPU server / local GPU), e.g. set it in the entrypoint.
    """
    if os.getenv("WHISPER_SUBTITLES", "0") != "1":
        print("[SUBTITLES] Whisper disabled (WHISPER_SUBTITLES!=1) - using fixed chunks")
        return _fixed_chunks(text)

    try:
        import whisper
        print("[SUBTITLES] Loading whisper base model...")
        model = whisper.load_model("base")
        print("[SUBTITLES] Transcribing audio for timed subtitles...")
        result = model.transcribe(audio_path, language="en")
        segs = result.get("segments", [])
        if segs:
            chunks = [{
                "start": float(s.get("start", 0)),
                "end": float(s.get("end", 3)),
                "text": s.get("text", "").strip(),
            } for s in segs if s.get("text", "").strip()]
            if chunks:
                print(f"[SUBTITLES] Got {len(chunks)} timed segments from whisper")
                return chunks
        print("[SUBTITLES] No whisper segments - using fixed chunks")
    except Exception as e:
        print(f"[SUBTITLES] Whisper unavailable ({str(e)[:120]}) - using fixed chunks")
    return _fixed_chunks(text)


if __name__ == "__main__":
    import sys, glob
    print("=" * 50)
    print("SUBTITLE TIMING - TEST MODE")
    print("=" * 50)
    audio = glob.glob("data/audio/*.wav")
    if audio:
        chunks = get_timed_subtitles(audio[0], "This is a test of timed subtitles across multiple words to verify the timing works correctly.")
        for c in chunks[:5]:
            print(f"[{c['start']:5.1f}-{c['end']:5.1f}] {c['text'][:60]}")
    else:
        print("No audio found - testing fallback only")
        for c in _fixed_chunks("This is a fallback test.", 3.0, 8):
            print(f"[{c['start']:5.1f}-{c['end']:5.1f}] {c['text']}")
    print("=" * 50)
