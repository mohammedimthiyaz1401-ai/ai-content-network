# ============================================================
# 🧠 AI CONTENT NETWORK - MEMORY FILE
# ============================================================
# LAST UPDATED: 2026-08-14 (evening, after API setup complete)
# STATUS: IN PROGRESS
# CURRENT PHASE: Step 17 - Full pipeline test
# ============================================================

# ⚠️ IMPORTANT: THIS FILE MUST BE UPDATED AFTER EVERY CHANGE
# Every time you make any modification to the project,
# update this file to reflect the current state.
# This is the single source of truth for the project.
# ============================================================


# ============================================================
# 1. PROJECT OVERVIEW
# ============================================================

PROJECT NAME: AI Content Network
GitHub Repo: mohammedimthiyaz1401-ai/ai-content-network
GitHub Email: mohammedimthiyaz1401@gmail.com

OBJECTIVE: Build a fully automated YouTube content network generating
AI-powered videos on autopilot using:
- Serverless GPU (Replicate.com)
- Free AI APIs (Gemini)
- GitHub Actions (Free CI/CD)


# ============================================================
# 2. CHANNEL STRATEGY
# ============================================================

CURRENT FOCUS: Channel 1 ONLY (Aria Future)
LATER: Create separate accounts for Channel 2 & 3

| Channel | Name | Status |
|---------|------|--------|
| Ch.1 | Aria Future | ✅ ACTIVE - Building now |
| Ch.2 | Future Intelligence News | 🔜 LATER (separate account) |
| Ch.3 | The Mystery Algorithm | 🔜 LATER (separate account) |

WHY SEPARATE ACCOUNTS:
- Strikes are per-channel (isolated)
- Terminations are per-account (affects all channels)
- Separate accounts = maximum protection
- Each channel needs: separate Gmail, YouTube, Google Cloud, API keys


# ============================================================
# 3. CREDENTIALS - CHANNEL 1 (ARIA FUTURE)
# ============================================================

GITHUB ACCOUNT:
- Email: mohammedimthiyaz1401@gmail.com
- Repo: mohammedimthiyaz1401-ai/ai-content-network

YOUTUBE CHANNEL 1 (Aria Future):
- Channel URL: https://www.youtube.com/channel/UCd5yt5eiM97UDyWkt9mZGQw
- Channel ID: UCd5yt5eiM97UDyWkt9mZGQw

YOUTUBE OAUTH2:
- Client ID: ✅ Stored in GitHub Secrets (YOUTUBE_CLIENT_ID)
- Client Secret: ✅ Stored in GitHub Secrets (YOUTUBE_CLIENT_SECRET)
- Refresh Token: ✅ Stored in GitHub Secrets (YOUTUBE_REFRESH_TOKEN)

GOOGLE CLOUD PROJECT:
- Project ID: aiscriptforyoutube
- Project Name: ai-content-network

GEMINI API:
- Status: ✅ WORKING (tested - generated 1643-word script)
- Model: gemini-3.1-flash-lite (via google-genai package)
- Cost: $10 prepay credits (bought 2026-08-14) - lasts 12 months
- IMPORTANT: Since Mar 2026, new AI Studio users require prepay credits.
  The $300 Google Cloud free trial does NOT cover Gemini API usage.
  Billing must be enabled on project: aiscriptforyoutube

REPLICATE API:
- Status: ✅ WORKING (tested - SDXL image generated)
- URL: https://replicate.com/account/api-tokens
- Credit: $5 added (2026-08-14)
- Model: stability-ai/sdxl (must use version ID, NOT :latest tag)
- Working version: 7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc
- Rate limit: 6 req/min with <$5 credit (small delay between calls)


# ============================================================
# 4. GITHUB SECRETS (Already Added)
# ============================================================

| Secret Name | Status |
|-------------|--------|
| REPLICATE_API_TOKEN | ✅ Updated with real token |
| GEMINI_API_KEY | ✅ Updated with real key |
| YOUTUBE_CLIENT_ID | ✅ Added |
| YOUTUBE_CLIENT_SECRET | ✅ Added |
| YOUTUBE_REFRESH_TOKEN | ✅ Added |
| YOUTUBE_CHANNEL_ID | ✅ Added |

GitHub Secrets URL: https://github.com/mohammedimthiyaz1401-ai/ai-content-network/settings/secrets/actions


# ============================================================
# 5. PROJECT STRUCTURE
# ============================================================

ai-content-network/
├── .github/workflows/
│   └── daily_automation.yml    ✅ DONE
├── src/
│   ├── __init__.py
│   ├── config.py               ✅ DONE (API keys - NO .env)
│   ├── main_pipeline.py        ✅ DONE (Master orchestrator)
│   ├── media_generator.py      ✅ DONE (SDXL + XTTS-v2)
│   ├── trend_sniffer.py        ✅ DONE (YouTube scraper)
│   ├── scriptwriter.py         ✅ DONE (Gemini API)
│   ├── video_assembler.py      ✅ DONE (MoviePy + FFmpeg)
│   └── youtube_uploader.py     ✅ DONE (OAuth2 refresh token)
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


# ============================================================
# 6. TECH STACK
# ============================================================

| Component | Tool | Cost |
|-----------|------|------|
| Orchestration | GitHub Actions | $0 (free) |
| Trend Sniffer | youtube-transcript-api + yt-dlp | $0 (free) |
| Scriptwriter | Gemini API (gemini-3.1-flash-lite) | $10 prepay / 12mo |
| Voice | XTTS-v2 (Replicate) | ~$0.015/min |
| Images | SDXL (Replicate) | ~$0.004/image |
| Subtitles | WhisperX | $0 (local) |
| Video Assembly | MoviePy + FFmpeg | $0 (local) |
| Thumbnails | Pillow (PIL) | $0 (local) |
| YouTube Upload | YouTube Data API v3 | $0 (free) |

ONE-TIME COSTS (2026-08-14):
- Gemini prepay: $10 (12 months of scriptwriting)
- Replicate credit: $5 (SDXL images + XTTS-v2 voice)
- TOTAL invested: $15

MONTHLY BUDGET: $7.00 USD (~520 INR)
RUNNING COST: ~$2.40/month (Replicate) + $0.83/month (Gemini) = ~$3.23/month


# ============================================================
# 7. WHAT'S COMPLETED
# ============================================================

✅ Step 1: Project folder structure created
✅ Step 2: requirements.txt set up
✅ Step 3: media_generator.py written (SDXL + XTTS-v2)
✅ Step 4: trend_sniffer.py written (YouTube scraper)
✅ Step 5: scriptwriter.py written (Gemini API)
✅ Step 6: video_assembler.py written (MoviePy)
✅ Step 7: youtube_uploader.py written (OAuth2)
✅ Step 8: main_pipeline.py written (orchestrator)
✅ Step 9: config.py created (NO .env dependency)
✅ Step 10: GitHub Actions workflow created
✅ Step 11: GitHub Secrets added
✅ Step 12: YouTube OAuth2 tokens obtained
✅ Step 13: .env file removed (not needed)
✅ Step 13b: scriptwriter.py migrated to google-genai (gemini-3.1-flash-lite)
✅ Step 13c: trend_sniffer.py updated for youtube-transcript-api v1.x API
✅ Step 13d: requirements.txt updated (google-genai)
✅ Step 13e: scripts/load_secrets.ps1.example added for local testing
✅ Step 14: Replicate API token obtained and tested (SDXL image generated)
   - Added $5 Replicate credit
   - Fixed model version (latest tag broken, use version ID)
✅ Step 15: Gemini prepay credits bought ($10) - API now works
   - Was hitting 403 (billing disabled) then 429 (prepay credits depleted)
   - Fixed by: enabling billing + buying $10 prepay credits
✅ Step 16: All GitHub Secrets updated with real values
   - REPLICATE_API_TOKEN, GEMINI_API_KEY both updated


# ============================================================
# 8. WHAT'S PENDING (NEXT STEPS)
# ============================================================

🔜 STEP 17: Test full pipeline locally
   - . .\scripts\load_secrets.ps1 (create from .example with real keys)
   - python src/main_pipeline.py --test
   - Tests: trend sniffer + scriptwriter + media gen (SDXL/XTTS) + video assembly
   - Skips: YouTube upload (--test flag)
   - NOTE: video_assembler.py needs update for moviepy 2.x API (changed imports)

🔜 STEP 18: Fix video_assembler.py for moviepy 2.x
   - moviepy 2.2.1 installed but video_assembler.py uses v1.x imports
   - Need to update: from moviepy.editor import ... → from moviepy import ...

🔜 STEP 19: Run full pipeline on GitHub Actions
   - Trigger workflow manually
   - Check if video uploads as Private

🔜 STEP 20: Manual publish on YouTube
   - Go to YouTube Studio
   - Find Private video
   - Click Publish

🔜 STEP 21: Create Channel 2 & 3 (separate accounts)
   - Create new Gmail for each
   - Create YouTube channel
   - Get new OAuth2 credentials
   - Update config.py


# ============================================================
# 9. DAILY OUTPUT TARGET
# ============================================================

PER CHANNEL:
- 2 Long-form videos (8-10 mins each)
- 4 Shorts (<60 secs each)

TOTAL (3 channels):
- 6 Long-form videos
- 12 Shorts

NOTE: Currently only Channel 1 is active


# ============================================================
# 10. MONETIZATION STRATEGY
# ============================================================

YOUTUBE ADSENSE:
- All scripts MUST be 1,500+ words
- Videos MUST exceed 8 minutes
- Qualifies for Mid-Roll Ads ($15-$30 CPM)

UPLOAD RULES:
- Videos uploaded as PRIVATE (not public)
- Human clicks "Publish" manually
- This prevents YouTube bot spam detection

COMPLIANCE:
- altered_content: true (2026 AI disclosure)
- "AI" watermark on Instagram Reels


# ============================================================
# 11. CHANNEL BRANDING
# ============================================================

CHANNEL 1: Aria Future
- Persona: 25yo female tech/finance influencer
- Aesthetic: High-status, luxury, professional
- Topics: AI tools, passive income, tech lifehacks
- CPM: $15-$30 (high)
- Visual: SDXL photorealistic images + XTTS-v2 voice


# ============================================================
# 12. REJECTED CONCEPTS (Don't Suggest These)
# ============================================================

❌ Anti-Detection/Proxies - Not needed (low volume + manual publish)
❌ Plagiarism APIs - Gemini rewrite is sufficiently transformative
❌ A/B Testing Framework - For channels with 100K+ subscribers
❌ Analytics Dashboard - YouTube Studio has free analytics
❌ SEO Optimizer API - Gemini can do this in the script prompt


# ============================================================
# 13. IMPORTANT COMMANDS
# ============================================================

TEST LOCALLY:
. .\scripts\load_secrets.ps1
python src/main_pipeline.py --test

TEST CHANNEL 1 ONLY:
python src/main_pipeline.py channel_1

PUSH TO GITHUB:
cd ai-content-network
git add .
git commit -m "Your message"
git push

VIEW GITHUB ACTIONS:
https://github.com/mohammedimthiyaz1401-ai/ai-content-network/actions


# ============================================================
# 14. TROUBLESHOOTING
# ============================================================

IF YOUTUBE TRANSCRIPT FAILS:
- YouTube blocks cloud/datacenter IPs — run locally from home network
- Pipeline falls back to "AI Tools 2026" topic if no transcripts found
- GitHub Actions may hit same issue; consider pre-fetched topics as fallback

IF YOUTUBE UPLOAD FAILS:
- Check refresh token hasn't expired (lasts ~1 week)
- Re-authenticate if needed using OAuth flow
- Verify channel ID is correct

IF REPLICATE FAILS:
- Check API token is valid (r8_...)
- Check you have credits remaining (must add at least $5)
- Model version: use specific version ID, NOT :latest tag
- Rate limit: 6 req/min with <$5 credit - add small delays between calls

IF REPLICATE RETURNS "Invalid version or not permitted" (422):
- The :latest tag does NOT work - use a specific version ID
- SDXL working version: 7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc

IF GEMINI FAILS:
- Check API key is valid
- 403 = billing not enabled on the project the key belongs to
- 429 "prepayment credits depleted" = need to buy prepay credits (min $10)
  since March 2026 the $300 free trial does NOT cover Gemini API
- Model: gemini-3.1-flash-lite (google-genai package, NOT google-generativeai)

IF VIDEO ASSEMBLY FAILS:
- Ensure FFmpeg is installed
- Check moviepy version
- Verify image paths exist


# ============================================================
# 15. CONTACT & ACCOUNTS
# ============================================================

USER: Mohammed Imthiyaz
EMAIL: mohammedimthiyaz1401@gmail.com
GITHUB: mohammedimthiyaz1401-ai
PROJECT REPO: ai-content-network

GOOGLE CLOUD CONSOLE: https://console.cloud.google.com
YOUTUBE STUDIO: https://studio.youtube.com
REPLICATE: https://replicate.com
GITHUB SECRETS: https://github.com/mohammedimthiyaz1401-ai/ai-content-network/settings/secrets/actions


# ============================================================
# 16. NEXT SESSION STARTER PROMPT
# ============================================================

When starting a new session, paste this file and say:

"I am building an AI Content Network project. Here is the memory file 
with all progress. Last status: All APIs working (Gemini + Replicate),
GitHub secrets updated. Next step: Test full pipeline locally, fix 
video_assembler.py for moviepy 2.x, then run on GitHub Actions. 
Continue from where we left off."


# ============================================================
# END OF MEMORY FILE
# ============================================================
