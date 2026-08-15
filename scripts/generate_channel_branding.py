"""
generate_channel_branding.py
----------------------------
One-time generator for Aria Future channel branding:
  - Profile picture (800x800)  -> assets/branding/profile.png
  - Channel banner    (2560x1440) -> assets/branding/banner.png

Uses Replicate SDXL (Aria's fixed face seed 12345 for consistency)
plus PIL compositing for text/branding on the banner.

Run after:  . scripts\\load_secrets.ps1
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import media_generator
from PIL import Image, ImageDraw, ImageFont

BRANDING_DIR = Path(__file__).parent.parent / "assets" / "branding"
BRANDING_DIR.mkdir(parents=True, exist_ok=True)

SEED = media_generator.CHANNEL_SEEDS["channel_1"]
SDXL = media_generator.generate_image_sdxl


def load_font(size: int):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def generate_profile():
    """Aria's face, 800x800, consistent with video host."""
    prompt = (
        "Professional studio headshot portrait of a 25-year-old attractive modern female "
        "tech influencer, short dark hair, confident smile, smart casual blazer, futuristic "
        "soft cyan and purple lighting, clean dark gradient background, high quality, "
        "photorealistic, centered face, sharp focus"
    )
    print("[PROFILE] Generating Aria headshot via SDXL...")
    img_path = SDXL(prompt, "channel_1", width=800, height=800)
    img = Image.open(img_path).convert("RGB").resize((800, 800), Image.LANCZOS)
    out = BRANDING_DIR / "profile.png"
    img.save(out)
    print(f"[PROFILE] Saved: {out} ({img.size[0]}x{img.size[1]})")
    return out


def generate_banner():
    """16:9 futuristic tech backdrop + ARIA FUTURE branding text, 2560x1440."""
    prompt = (
        "Futuristic technology wallpaper, dark navy blue gradient with glowing cyan and "
        "purple neon circuit lines, abstract AI neural network, floating digital particles, "
        "clean, no text, no people, cinematic, high detail, wide composition"
    )
    print("[BANNER] Generating backdrop via SDXL...")
    img_path = SDXL(prompt, "channel_1", width=1024, height=576)
    bg = Image.open(img_path).convert("RGB").resize((2560, 1440), Image.LANCZOS)

    draw = ImageDraw.Draw(bg, "RGBA")
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, 0, 2560, 1440], fill=(5, 8, 24, 140))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)

    # Safe area: center on 2560x1440 -> readable band around middle
    title = load_font(160)
    tag = load_font(72)
    url_font = load_font(52)

    t = "ARIA FUTURE"
    s = "AI Tools  |  Passive Income  |  The Future of Tech"
    u = "youtube.com/@ariafuturetech"

    # title centered (slightly upper-middle, away from extreme edges)
    title_w = draw.textlength(t, font=title)
    draw.text(((2560 - title_w) / 2, 470), t, fill=(240, 248, 255, 255), font=title)
    tag_w = draw.textlength(s, font=tag)
    draw.text(((2560 - tag_w) / 2, 700), s, fill=(120, 220, 255, 255), font=tag)
    url_w = draw.textlength(u, font=url_font)
    draw.text(((2560 - url_w) / 2, 900), u, fill=(255, 255, 255, 180), font=url_font)

    out = BRANDING_DIR / "banner.png"
    bg.save(out)
    print(f"[BANNER] Saved: {out} ({bg.size[0]}x{bg.size[1]})")
    return out


if __name__ == "__main__":
    if not media_generator.REPLICATE_API_TOKEN:
        raise SystemExit(
            "REPLICATE_API_TOKEN not set. Run: .\\scripts\\load_secrets.ps1 first"
        )
    profile = generate_profile()
    banner = generate_banner()
    print("\nDONE. Files ready for YouTube upload:")
    print(f"  Profile: {profile}")
    print(f"  Banner : {banner}")