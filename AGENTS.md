# AI Content Network - AGENTS.md

## What
YouTube channel producing AI/tech content. Aria Future host with talking-head animation, daily shorts + weekly long-form videos.

## Tech Stack
- Python 3.11+
- Google Gemini API (script generation)
- edge-tts (voice generation)
- Replicate (SDXL images, XTTS voice, SadTalker animation)
- Kaggle GPU (free SDXL, XTTS, SadTalker - 30hr/week per account)
- moviepy (video assembly)
- YouTube Data API v3 (upload via OAuth2)

## Key Files
- src/main_pipeline.py - Main entry point
- src/media_generator.py - Image/voice with Kaggle → Replicate → Pollinations fallback
- src/sadtalker_host.py - Talking head with Kaggle → Replicate → Static fallback
- src/config.py - Configuration
- src/kaggle_gpu/ - Kaggle GPU module (multi-account, budget tracking, retry)
- src/kaggle_integration.py - Kaggle wrapper (SDXL, XTTS, SadTalker)
- src/local_models.py - Local GPU models (server deployment)

## How to Deploy
1. Push to master branch
2. GitHub Actions triggers daily_morning.yml (Mon-Fri 6AM UTC) or daily_night.yml (Saturday 6PM UTC)
3. Pipeline runs main_pipeline.py
4. Video uploaded to YouTube

## Fallback Chain
- Images: Kaggle GPU SDXL → Local SDXL → Replicate SDXL → Pollinations → Placeholder
- Voice: Kaggle GPU XTTS → Local XTTS → Replicate XTTS → EdgeTTS → Offline TTS
- Host: Kaggle GPU SadTalker → Local SadTalker → Replicate SadTalker → Static portrait

## Environment
- REPLICATE_API_TOKEN: Required for Replicate models
- GEMINI_API_KEY: Required for script generation
- Kaggle GPU: Credentials hardcoded in kaggle_gpu/accounts.py (no env setup needed)

## YouTube Schedule
- Shorts: Mon-Fri 6AM UTC
- Long-form: Saturday 6PM UTC

## .gitignore
__pycache__/
output/
data/videos/
data/scripts/
data/reports/
*.pickle
client_secret.json
