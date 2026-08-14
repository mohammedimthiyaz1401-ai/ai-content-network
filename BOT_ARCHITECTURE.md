# BOT_ARCHITECTURE.md - Living Document

> **Last Updated:** 2026-08-14
> **Version:** 1.0.0

---

## Project Overview

Fully automated YouTube & Instagram content network generating 3 channels of AI-powered videos.

**Monthly Budget:** $7.00 USD (~520 INR)

---

## Channel Network

| Channel | Persona | Face? | Visual Style |
|---|---|---|---|
| **Ch.1: AI Influencer** | 25yo female tech/finance | YES | SDXL photorealistic |
| **Ch.2: Future Intelligence** | Faceless news anchor | NO | AnimateDiff clips |
| **Ch.3: Mysteries** | Deep mysterious narrator | NO | AnimateDiff clips |

---

## Daily Output

| Type | Per Channel | Total (3 Channels) |
|---|---|---|
| Long-form (8-10 min) | 2 | 6 |
| Shorts (<60 sec) | 4 | 12 |

---

## Tech Stack

| Component | Tool | Source | Cost |
|---|---|---|---|
| **Orchestration** | GitHub Actions | Free tier | $0 |
| **Trend Sniffer** | youtube-transcript-api | GitHub: jdepoix | $0 |
| **Scriptwriter** | Google Gemini API | Free tier | $0 |
| **Voice** | XTTS-v2 | Replicate | $0.015/min |
| **Images** | SDXL | Replicate | $0.004/image |
| **Subtitles** | WhisperX | Local | $0 |
| **Assembly** | MoviePy + FFmpeg | Local | $0 |
| **Thumbnails** | Pillow (PIL) | Local | $0 |

---

## API Keys Required (GitHub Secrets)

| Service | Key | Location |
|---|---|---|
| Replicate | `REPLICATE_API_TOKEN` | `config.py` + GitHub Secrets |
| Gemini | `GEMINI_API_KEY` | `config.py` + GitHub Secrets |
| YouTube OAuth | `YOUTUBE_CLIENT_ID` | `config.py` + GitHub Secrets |
| YouTube OAuth | `YOUTUBE_CLIENT_SECRET` | `config.py` + GitHub Secrets |
| YouTube OAuth | `YOUTUBE_REFRESH_TOKEN` | `config.py` + GitHub Secrets |
| YouTube Channel | `YOUTUBE_CHANNEL_ID` | `config.py` + GitHub Secrets |

> **NO .env FILE REQUIRED** - All secrets hardcoded in `src/config.py`

---

## File Structure

```
ai-content-network/
├── .github/workflows/daily_automation.yml
├── src/
│   ├── __init__.py
│   ├── config.py               ✅ DONE (API keys - NO .env)
│   ├── main_pipeline.py        ✅ DONE (Master orchestrator)
│   ├── media_generator.py      ✅ DONE
│   ├── trend_sniffer.py        ✅ DONE
│   ├── scriptwriter.py         ✅ DONE
│   ├── video_assembler.py      ✅ DONE
│   └── youtube_uploader.py     ✅ DONE
├── data/
│   ├── scripts/
│   ├── audio/
│   ├── images/
│   ├── videos/
│   └── subtitles/
├── assets/
│   ├── voice_samples/
│   └── fonts/
├── .gitignore
├── requirements.txt
└── BOT_ARCHITECTURE.md
```

---

## Cost Tracking

| Component | Daily Cost | Monthly Cost |
|---|---|---|
| XTTS-v2 Voice (2 videos) | $0.27 | $8.10 |
| SDXL Images (20 images) | $0.08 | $2.40 |
| GitHub Actions | $0 | $0 |
| Gemini API | $0 | $0 |
| **TOTAL** | **$0.35** | **$10.50** |

> **Note:** Slightly over $7 budget. Can reduce to 1 long-form video/day to hit target.

---

## Quality Gates

| Gate | Requirement | Action on Fail |
|---|---|---|
| Script length | 1,500+ words | Reject and regenerate |
| Video duration | 8+ minutes | Reject before upload |
| Audio quality | SNR > 20dB | Log warning, proceed |
| Subtitle sync | Within 0.5s | Skip subtitles, proceed |

---

## Upload Rules

| Platform | Privacy | Disclosure |
|---|---|---|
| YouTube | PRIVATE (manual publish) | `altered_content: true` |
| Instagram | PUBLIC (manual post) | "AI" watermark |

---

## Change Log

| Date | Change | Author |
|---|---|---|
| 2026-08-14 | Initial architecture created | AI Assistant |
| 2026-08-14 | Added media_generator.py (Replicate SDXL + XTTS-v2) | AI Assistant |
| 2026-08-14 | Added trend_sniffer.py (YouTube scraper) | AI Assistant |
| 2026-08-14 | Added scriptwriter.py (Gemini API) | AI Assistant |
| 2026-08-14 | Added video_assembler.py (MoviePy + FFmpeg) | AI Assistant |
| 2026-08-14 | Added youtube_uploader.py (YouTube API v3) | AI Assistant |
| 2026-08-14 | Added daily_automation.yml (GitHub Actions) | AI Assistant |
| 2026-08-14 | Added main_pipeline.py (Master orchestrator) | AI Assistant |
| 2026-08-14 | Removed .env dependency - all secrets in config.py | AI Assistant |
| 2026-08-14 | Focus: Channel 1 only (Aria Future) | AI Assistant |

---

> **REMINDER:** Update this document whenever a new tool, API, or strategy is added.
