"""
config.py
---------
All API keys and configuration.
NO .env file dependency - reads from environment variables.

Focus: Channel 1 only (Aria Future)
Replicate API: Shared across all 3 channels (later)
"""

import os

# ============================================================
# REPLICATE API (Shared across all channels)
# ============================================================
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# ============================================================
# FREE TIER MODE (ZERO EXPENSE - no Replicate, no GPU)
# When FREE_TIER=1 the pipeline uses only free providers:
#   Images -> Pollinations.ai (free, no API key)
#   Voice  -> Microsoft EdgeTTS (free, no API key)
#   Host   -> static portrait (no animated talking head)
# Gemini scriptwriting stays on its free tier / prepay credits.
# This mode needs NO cloud server: runs on GitHub Actions alone.
# ============================================================
FREE_TIER = os.getenv("FREE_TIER", "0") == "1"

# ============================================================
# GOOGLE GEMINI API (Scriptwriting - FREE)
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ============================================================
# YOUTUBE OAUTH2 - PER CHANNEL
# Each channel uses its OWN Google Cloud project / OAuth app and
# refresh token (separate Google account). Env var names:
#   Channel 1 (Aria Future):          YOUTUBE_*  (legacy) or YOUTUBE_*_CH1
#   Channel 2 (Future Intelligence):  YOUTUBE_*_CH2
#   Channel 3 (Mystery Algorithm):    YOUTUBE_*_CH3
# ============================================================
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# ============================================================
# YOUTUBE CHANNEL ID (Aria Future - Channel 1)
# Public data (not secret); env var overrides when set.
# ============================================================
YOUTUBE_CHANNEL_ID = os.getenv(
    "YOUTUBE_CHANNEL_ID", os.getenv("YOUTUBE_CHANNEL_ID_CH1", "UCd5yt5eiM97UDyWkt9mZGQw")
)

# ============================================================
# TELEGRAM NOTIFICATION (Daily report delivery)
# Create a bot via @BotFather, add to your chat, get chat_id via @userinfobot
# ============================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ============================================================
# CHANNEL CONFIGURATION (per-channel OAuth credentials)
# A channel is ACTIVE only when its credentials are fully present,
# so Ch.2/Ch.3 auto-activate the moment you fill their secrets.
# ============================================================
def _ch1(legacy: str, suffixed: str) -> str:
    return os.getenv(suffixed, os.getenv(legacy, ""))


CHANNELS = {
    "channel_1": {
        "name": "Aria Future",
        "youtube_channel_id": YOUTUBE_CHANNEL_ID,
        "category_id": "28",  # Science & Technology
        "default_tags": ["AI", "artificial intelligence", "technology", "future", "passive income", "tech tools"],
        "client_id": _ch1("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_ID_CH1"),
        "client_secret": _ch1("YOUTUBE_CLIENT_SECRET", "YOUTUBE_CLIENT_SECRET_CH1"),
        "refresh_token": _ch1("YOUTUBE_REFRESH_TOKEN", "YOUTUBE_REFRESH_TOKEN_CH1"),
    },
    "channel_2": {
        "name": "Future Intelligence News",
        "youtube_channel_id": os.getenv("YOUTUBE_CHANNEL_ID_CH2", ""),
        "category_id": "28",  # Science & Technology
        "default_tags": ["AI news", "future", "technology", "artificial intelligence", "tech news"],
        "client_id": os.getenv("YOUTUBE_CLIENT_ID_CH2", ""),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET_CH2", ""),
        "refresh_token": os.getenv("YOUTUBE_REFRESH_TOKEN_CH2", ""),
    },
    "channel_3": {
        "name": "The Mystery Algorithm",
        "youtube_channel_id": os.getenv("YOUTUBE_CHANNEL_ID_CH3", ""),
        "category_id": "24",  # Entertainment (mystery/unsolved fits better here)
        "default_tags": ["mystery", "unsolved", "algorithm", "conspiracy", "AI"],
        "client_id": os.getenv("YOUTUBE_CLIENT_ID_CH3", ""),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET_CH3", ""),
        "refresh_token": os.getenv("YOUTUBE_REFRESH_TOKEN_CH3", ""),
    },
}

# ============================================================
# ACTIVE CHANNELS
# Only channels with FULL credentials (client_id + secret + refresh token
# + channel id) are processed. Ch.1 is always active once creds are set.
# ============================================================
ACTIVE_CHANNELS = [
    ch for ch, cfg in CHANNELS.items()
    if cfg["client_id"] and cfg["client_secret"] and cfg["refresh_token"] and cfg["youtube_channel_id"]
]
if not ACTIVE_CHANNELS:
    # Never silently run zero channels: default to Ch.1 config so errors surface
    ACTIVE_CHANNELS = ["channel_1"]

# ============================================================
# VIDEO SETTINGS
# ============================================================
LONG_FORM_SIZE = (1920, 1080)
SHORTS_SIZE = (1080, 1920)
FPS = 30
IMAGE_DURATION = 5  # seconds per image

# ============================================================
# DAILY TARGETS - split into halves for two runs/day
# Morning run:  1 long + 2 shorts (LONGFORM_TARGET=1, SHORTS_TARGET=2)
# Night run:    1 long + 2 shorts (same)
# Full run (manual): 2 long + 4 shorts (defaults below)
# Each run stays well under the 120-min workflow cap.
# ============================================================
LONGFORM_TARGET = int(os.getenv("LONGFORM_TARGET", "2"))
SHORTS_TARGET = int(os.getenv("SHORTS_TARGET", "4"))
