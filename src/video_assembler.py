"""
video_assembler.py
------------------
Stitches AI images, voiceover, and subtitles into final videos.
Uses MoviePy + FFmpeg for assembly.

Outputs:
- 1920x1080 (Long-form)
- 1080x1920 (Shorts/Reels)
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
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
                clip = ImageClip(path).set_duration(IMAGE_DURATION)
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
    
    def resize_frame(clip):
        """Resize and crop frame to fit output size."""
        img = clip.get_frame(0)
        pil_img = Image.fromarray(img)
        
        # Calculate resize dimensions
        target_w, target_h = output_size
        img_w, img_h = pil_img.size
        
        # Scale to fill
        scale = max(target_w / img_w, target_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
        
        # Center crop
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        pil_img = pil_img.crop((left, top, left + target_w, top + target_h))
        
        return ImageClip(pil_img)
    
    # Resize all clips
    resized_clips = []
    for clip in clips:
        try:
            resized = resize_frame(clip)
            resized_clips.append(resized.set_duration(clip.duration))
        except Exception as e:
            print(f"[WARN] Failed to resize clip: {e}")
    
    if not resized_clips:
        return None
    
    return concatenate_videoclips(resized_clips, method="compose")


def add_subtitles(
    video: CompositeVideoClip,
    subtitle_text: str,
    output_size: tuple = LONG_FORM_SIZE,
) -> CompositeVideoClip:
    """
    Add styled subtitles to video.
    
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
        # Split subtitle into chunks for display
        words = subtitle_text.split()
        chunk_size = 8  # words per subtitle
        subtitle_chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            subtitle_chunks.append(chunk)
        
        # Create subtitle clips
        subtitle_clips = []
        chunk_duration = 3  # seconds per subtitle chunk
        
        for i, chunk in enumerate(subtitle_chunks):
            start_time = i * chunk_duration
            
            if start_time >= video.duration:
                break
            
            try:
                txt_clip = TextClip(
                    chunk,
                    fontsize=48,
                    color="white",
                    font="Arial-Bold",
                    stroke_color="black",
                    stroke_width=3,
                    size=(output_size[0] - 200, None),
                    method="caption",
                )
                
                # Position at bottom
                txt_clip = txt_clip.set_position(("center", output_size[1] - 150))
                txt_clip = txt_clip.set_start(start_time)
                txt_clip = txt_clip.set_duration(chunk_duration)
                
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
        watermark = TextClip(
            WATERMARK_TEXT,
            fontsize=24,
            color="white",
            font="Arial",
            stroke_color="black",
            stroke_width=1,
        )
        
        # Position bottom-right with margin
        margin = 30
        watermark = watermark.set_position((
            output_size[0] - watermark.size[0] - margin,
            output_size[1] - watermark.size[1] - margin,
        ))
        watermark = watermark.set_duration(video.duration)
        watermark = watermark.set_opacity(0.7)
        
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
        img = Image.open(image_path)
        
        # Resize to thumbnail size
        img = img.resize(output_size, Image.LANCZOS)
        
        # Darken image
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)
        
        # Add text overlay
        draw = ImageDraw.Draw(img)
        
        # Try to load a bold font
        font_size = 80
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype(FONTS_DIR / "arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
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
        
        # Draw text with outline
        text_y = output_size[1] // 2 - (len(lines) * font_size) // 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (output_size[0] - text_width) // 2
            
            # Black outline
            for dx in [-3, -2, -1, 0, 1, 2, 3]:
                for dy in [-3, -2, -1, 0, 1, 2, 3]:
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


def assemble_video(
    image_paths: List[str],
    audio_path: str,
    subtitle_text: str,
    channel: str,
    output_size: tuple = LONG_FORM_SIZE,
    is_short: bool = False,
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
    
    Returns:
        Path to assembled video
    """
    print(f"\n{'='*60}")
    print(f"VIDEO ASSEMBLY")
    print(f"Channel: {channel}")
    print(f"Type: {'Short' if is_short else 'Long-form'}")
    print(f"{'='*60}")
    
    # Step 1: Create video from images
    print("\n[1/5] Creating video from images...")
    video = create_video_from_images(image_paths, output_size)
    
    if video is None:
        raise Exception("Failed to create video from images")
    
    print(f"[1/5] Video duration: {video.duration}s")
    
    # Step 2: Add audio
    print("[2/5] Adding audio...")
    if os.path.exists(audio_path):
        try:
            audio = AudioFileClip(audio_path)
            
            # Loop video if audio is longer
            if audio.duration > video.duration:
                loops_needed = int(audio.duration / video.duration) + 1
                video = concatenate_videoclips([video] * loops_needed)
                video = video.subclip(0, audio.duration)
            
            video = video.set_audio(audio)
            print(f"[2/5] Audio added: {audio.duration}s")
        except Exception as e:
            print(f"[WARN] Audio addition failed: {e}")
    else:
        print(f"[WARN] Audio file not found: {audio_path}")
    
    # Step 3: Add subtitles
    print("[3/5] Adding subtitles...")
    if subtitle_text and not is_short:
        video = add_subtitles(video, subtitle_text, output_size)
    elif is_short and subtitle_text:
        # Shorts: Add shorter subtitles
        video = add_subtitles(video, subtitle_text[:200], output_size)
    
    # Step 4: Add watermark (Instagram requirement)
    print("[4/5] Adding watermark...")
    if is_short:
        video = add_watermark(video, output_size)
    
    # Step 5: Export
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
    
    # Cleanup
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
        from moviepy.editor import VideoFileClip
        
        # Load long-form video
        video = VideoFileClip(longform_path)
        
        # Extract 60-second clip
        end_time = min(start_time + 60, video.duration)
        short = video.subclip(start_time, end_time)
        
        # Resize to vertical (9:16)
        short = short.resize(SHORTS_SIZE)
        
        # Add watermark
        short = add_watermark(short, SHORTS_SIZE)
        
        # Export
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
        img_path = str(DATA_DIR / "images" / f"test_{i}.png")
        img.save(img_path)
        test_images.append(img_path)
    
    print("[TEST] Created 3 test images")
    print("[TEST] Run with real audio/images for full test")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
