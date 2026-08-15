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
# GOOGLE GEMINI API (Scriptwriting - FREE)
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ============================================================
# YOUTUBE OAUTH2 (Channel 1: Aria Future only)
# ============================================================
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# ============================================================
# YOUTUBE CHANNEL ID (Aria Future only)
# Public data (not secret); env var overrides when set.
# ============================================================
YOUTUBE_CHANNEL_ID = os.getenv(
    "YOUTUBE_CHANNEL_ID", "UCd5yt5eiM97UDyWkt9mZGQw"
)

# ============================================================
# TELEGRAM NOTIFICATION (Daily report delivery)
# Create a bot via @BotFather, add to your chat, get chat_id via @userinfobot
# ============================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ============================================================
# CHANNEL CONFIGURATION
# ============================================================
CHANNELS = {
    "channel_1": {
        "name": "Aria Future",
        "youtube_channel_id": YOUTUBE_CHANNEL_ID,
        "category_id": "28",  # Science & Technology
        "default_tags": ["AI", "artificial intelligence", "technology", "future", "passive income", "tech tools"],
    },
    # Channel 2 & 3 will be added later with separate accounts
    # "channel_2": {...},
    # "channel_3": {...},
}

# ============================================================
# ACTIVE CHANNELS (Only Channel 1 for now)
# ============================================================
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
