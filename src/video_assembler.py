"""
video_assembler.py
------------------
Stitches AI images, voiceover, and subtitles into final videos.
Uses MoviePy 2.x + FFmpeg for assembly.

Outputs:
- 1920x1080 (Long-form)
- 1080x1920 (Shorts/Reels)

Notes:
- Uses PIL-based text rendering (NO ImageMagick dependency)
- Compatible with moviepy 2.x (imports from moviepy, not moviepy.editor)
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    VideoFileClip,
)
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = DATA_DIR / "images"
AUDIO_DIR = DATA_DIR / "audio"
VIDEOS_DIR = DATA_DIR / "videos"
SUBTITLES_DIR = DATA_DIR / "subtitles"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)

# Video settings
LONG_FORM_SIZE = (1920, 1080)
SHORTS_SIZE = (1080, 1920)
FPS = 30
IMAGE_DURATION = 5  # seconds per image
WATERMARK_TEXT = "AI"


def _get_font(size: int):
    """Load a bold font, falling back to default if unavailable."""
    for font_path in [
        FONTS_DIR / "arial.ttf",
        "arial.ttf",
        "DejaVuSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            continue
    try:
        return ImageFont.truetype("arial", size)
    except Exception:
        return ImageFont.load_default()


def _make_text_png(text: str, output_size: tuple, fontsize: int = 48,
                    color: str = "white", stroke: bool = True) -> ImageClip:
    """
    Render text to a transparent PNG using PIL (no ImageMagick needed).
    
    Args:
        text: Text to render
        output_size: (width, height) of the canvas
        fontsize: Font size
        color: Text color
        stroke: Whether to add black outline
    
    Returns:
        ImageClip with transparent background
    """
    from PIL import Image as PILImage
    from moviepy import ImageClip as MPImageClip
    
    img = PILImage.new("RGBA", output_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _get_font(fontsize)
    
    # Wrap text to fit width
    max_width = int(output_size[0] * 0.85)
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(" ".join(current_line))
    
    # Draw each line centered
    line_height = fontsize + 10
    total_height = len(lines) * line_height
    start_y = (output_size[1] - total_height) // 2
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (output_size[0] - text_width) // 2
        y = start_y + i * line_height
        
        if stroke:
            # Outline
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx * dx + dy * dy <= 9:
                        draw.text((x + dx, y + dy), line, font=font, fill="black")
        
        draw.text((x, y), line, font=font, fill=color)
    
    # Save to temp file
    temp_path = str(SUBTITLES_DIR / f"text_{datetime.now().strftime('%H%M%S_%f')}.png")
    img.save(temp_path)
    
    clip = MPImageClip(temp_path).with_duration(1)
    clip._temp_path = temp_path
    return clip


def load_images(image_paths: List[str]) -> List[ImageClip]:
    """
    Load images and create clips.
    
    Args:
        image_paths: List of image file paths
    
    Returns:
        List of ImageClip objects
    """
    clips = []
    
    for path in image_paths:
        if os.path.exists(path):
            try:
                clip = ImageClip(path).with_duration(IMAGE_DURATION)
                clips.append(clip)
            except Exception as e:
                print(f"[WARN] Failed to load image {path}: {e}")
    
    print(f"[IMAGES] Loaded {len(clips)} image clips")
    return clips


def create_video_from_images(image_paths: List[str], output_size: tuple = LONG_FORM_SIZE) -> Optional[CompositeVideoClip]:
    """
    Create video from images with proper sizing.
    
    Args:
        image_paths: List of image paths
        output_size: Target video size (width, height)
    
    Returns:
        CompositeVideoClip or None
    """
    clips = load_images(image_paths)
    
    if not clips:
        print("[ERROR] No image clips loaded")
        return None
    
    resized_clips = []
    for clip in clips:
        try:
            resized = clip.resized(output_size)
            resized_clips.append(resized.with_duration(clip.duration))
        except Exception as e:
            print(f"[WARN] Failed to resize clip: {e}")
            continue
    
    if not resized_clips:
        print("[ERROR] All clips failed to resize")
        return None
    
    return concatenate_videoclips(resized_clips, method="compose")


def add_subtitles(
    video: CompositeVideoClip,
    subtitle_text: str,
    output_size: tuple = LONG_FORM_SIZE,
) -> CompositeVideoClip:
    """
    Add styled subtitles to video using PIL-rendered text.
    
    Args:
        video: Input video clip
        subtitle_text: Full subtitle text
        output_size: Video size for positioning
    
    Returns:
        Video with subtitles
    """
    if not subtitle_text:
        return video
    
    try:
        words = subtitle_text.split()
        chunk_size = 8
        subtitle_chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            subtitle_chunks.append(chunk)
        
        subtitle_clips = []
        chunk_duration = 3.0
        subtitle_height = 200
        subtitle_size = (output_size[0], subtitle_height)
        
        for i, chunk in enumerate(subtitle_chunks):
            start_time = i * chunk_duration
            
            if start_time >= video.duration:
                break
            
            try:
                txt_clip = _make_text_png(chunk, subtitle_size, fontsize=44)
                txt_clip = txt_clip.with_duration(chunk_duration)
                # Position at bottom center
                y_pos = output_size[1] - subtitle_height - 60
                txt_clip = txt_clip.with_position(("center", y_pos))
                txt_clip = txt_clip.with_start(start_time)
                subtitle_clips.append(txt_clip)
            except Exception as e:
                print(f"[WARN] Failed to create subtitle clip: {e}")
                continue
        
        if subtitle_clips:
            return CompositeVideoClip([video] + subtitle_clips)
    
    except Exception as e:
        print(f"[WARN] Subtitle addition failed: {e}")
    
    return video


def add_watermark(
    video: CompositeVideoClip,
    output_size: tuple = LONG_FORM_SIZE,
) -> CompositeVideoClip:
    """
    Add AI watermark to video (Instagram requirement).
    
    Args:
        video: Input video clip
        output_size: Video size
    
    Returns:
        Video with watermark
    """
    try:
        watermark = _make_text_png("AI", (200, 100), fontsize=48)
        watermark = watermark.with_duration(video.duration)
        watermark = watermark.with_opacity(0.7)
        
        margin = 30
        watermark = watermark.with_position((
            output_size[0] - 200 - margin,
            output_size[1] - 100 - margin,
        ))
        
        return CompositeVideoClip([video, watermark])
    
    except Exception as e:
        print(f"[WARN] Watermark addition failed: {e}")
        return video


def generate_thumbnail(
    image_path: str,
    title: str,
    output_path: str,
    output_size: tuple = LONG_FORM_SIZE,
) -> str:
    """
    Generate thumbnail from best SDXL image + text overlay.
    
    Args:
        image_path: Path to source image
        title: Video title for thumbnail
        output_path: Where to save thumbnail
        output_size: Thumbnail size
    
    Returns:
        Path to saved thumbnail
    """
    try:
        img = Image.open(image_path).convert("RGB")
        
        img = img.resize(output_size, Image.LANCZOS)
        
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)
        
        draw = ImageDraw.Draw(img)
        font_size = 80
        font = _get_font(font_size)
        
        # Wrap text
        max_chars = 20
        lines = []
        words = title.split()
        current_line = []
        
        for word in words:
            if len(" ".join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        text_y = output_size[1] // 2 - (len(lines) * font_size) // 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (output_size[0] - text_width) // 2
            
            # Black outline
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx * dx + dy * dy <= 9:
                        draw.text((text_x + dx, text_y + dy), line, font=font, fill="black")
            
            # White text
            draw.text((text_x, text_y), line, font=font, fill="yellow")
            text_y += font_size + 10
        
        img.save(output_path, quality=95)
        print(f"[THUMBNAIL] Saved: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"[ERROR] Thumbnail generation failed: {e}")
        return ""


def splice_host_clips(
    video: CompositeVideoClip,
    host_clips: List[str],
    output_size: tuple = LONG_FORM_SIZE,
) -> CompositeVideoClip:
    """
    Splice talking-host segments into the video:
      - First host clip becomes the INTRO (host introduces the topic)
      - Remaining host clips become transitions (spliced every ~90s)
      Returns a concatenated video with host segments interleaved.

    host_clips: list of paths. Each can be an animated MP4 (SadTalker) or
    a static image (fallback). Static images get IMAGE_DURATION each.
    """
    if not host_clips:
        return video

    segments = [VideoFileClip(p) if p.lower().endswith(".mp4")
                else ImageClip(p).with_duration(IMAGE_DURATION) for p in host_clips]

    # Resize the base video AND host segments to a common size for splicing
    host = []
    for h in segments:
        try:
            h = h.resized(output_size)
            host.append(h)
        except Exception as e:
            print(f"[WARN] Host clip resize failed: {e}")

    if not host:
        return video

    total = [host[0], video]  # intro host, then main video
    # Extra host clips become transitions. We splice them by splitting the main
    # video into N equal chunks and interleaving host segments.
    n_trans = len(host) - 1
    if n_trans > 0:
        main = video
        chunk = main.duration / n_trans
        pieces = []
        for i in range(n_trans):
            part = main.subclipped(i * chunk, min((i + 1) * chunk, main.duration))
            pieces.append(part)
            pieces.append(host[i + 1])
        total = [host[0]] + pieces

    print(f"[HOST] Splice complete: intro + {n_trans} transition(s)")
    return concatenate_videoclips(total, method="compose")


def assemble_video(
    image_paths: List[str],
    audio_path: str,
    subtitle_text: str,
    channel: str,
    output_size: tuple = LONG_FORM_SIZE,
    is_short: bool = False,
    host_clips: List[str] = None,
) -> str:
    """
    Complete video assembly pipeline.
    
    Args:
        image_paths: List of image paths
        audio_path: Path to voiceover audio
        subtitle_text: Full subtitle text
        channel: Channel identifier
        output_size: Target video size
        is_short: Whether this is a Short/Reel
        host_clips: Optional talking-host segments (intro + transitions)

    Returns:
        Path to assembled video
    """
    print(f"\n{'='*60}")
    print(f"VIDEO ASSEMBLY")
    print(f"Channel: {channel}")
    print(f"Type: {'Short' if is_short else 'Long-form'}")
    print(f"{'='*60}")
    
    print("\n[1/5] Creating video from images...")
    video = create_video_from_images(image_paths, output_size)
    
    if video is None:
        raise Exception("Failed to create video from images")
    
    print(f"[1/5] Video duration: {video.duration}s")
    
    print("[2/5] Adding audio...")
    if os.path.exists(audio_path):
        try:
            audio = AudioFileClip(audio_path)
            
            # Loop video if audio is longer
            if audio.duration > video.duration:
                loops_needed = int(audio.duration / video.duration) + 1
                video = concatenate_videoclips([video] * loops_needed, method="compose")
                video = video.subclipped(0, audio.duration)
            
            video = video.with_audio(audio)
            print(f"[2/5] Audio added: {audio.duration}s")
        except Exception as e:
            print(f"[WARN] Audio addition failed: {e}")
    else:
        print(f"[WARN] Audio file not found: {audio_path}")
    
    print("[3/5] Adding host segments (intro + transitions)...")
    if host_clips:
        try:
            video = splice_host_clips(video, host_clips, output_size)
            print(f"[3/5] Host spliced: {len(host_clips)} segment(s)")
        except Exception as e:
            print(f"[WARN] Host splice failed: {e}")
    
    print("[4/5] Adding subtitles...")
    if subtitle_text:
        video = add_subtitles(video, subtitle_text if not is_short else subtitle_text[:200], output_size)
    
    print("[5/5] Adding watermark...")
    if is_short:
        video = add_watermark(video, output_size)
    
    print("[5/5] Exporting video...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_type = "short" if is_short else "longform"
    filename = f"{channel}_{video_type}_{timestamp}.mp4"
    output_path = str(VIDEOS_DIR / filename)
    
    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium" if not is_short else "fast",
        logger=None,
    )
    
    video.close()
    
    print(f"\n[COMPLETE] Video saved: {output_path}")
    return output_path


def create_short_from_longform(
    longform_path: str,
    subtitle_text: str,
    channel: str,
    start_time: int = 0,
) -> str:
    """
    Create a 60-second Short from long-form video.
    
    Args:
        longform_path: Path to long-form video
        subtitle_text: Subtitle text
        channel: Channel identifier
        start_time: Start time in seconds for clip
    
    Returns:
        Path to Short video
    """
    print(f"\n[SHORT] Creating Short from {longform_path}")
    
    try:
        video = VideoFileClip(longform_path)
        
        end_time = min(start_time + 60, video.duration)
        short = video.subclipped(start_time, end_time)
        
        # Resize to vertical (9:16) - crop center
        short = short.resized(SHORTS_SIZE)
        
        short = add_watermark(short, SHORTS_SIZE)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{channel}_short_{timestamp}.mp4"
        output_path = str(VIDEOS_DIR / filename)
        
        short.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            threads=2,
            preset="fast",
            logger=None,
        )
        
        video.close()
        short.close()
        
        print(f"[SHORT] Saved: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"[ERROR] Short creation failed: {e}")
        return ""


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("VIDEO ASSEMBLER - TEST MODE")
    print("=" * 60)
    
    # Create test images
    test_images = []
    for i in range(3):
        img = Image.new("RGB", (1024, 1024), color=(50, 50, 100 + i * 50))
        img_path = str(IMAGES_DIR / f"test_{i}.png")
        img.save(img_path)
        test_images.append(img_path)
    
    print("[TEST] Created 3 test images")
    print("[TEST] Run with real audio/images for full test")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
