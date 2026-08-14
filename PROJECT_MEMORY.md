# ============================================================
# 🧠 AI CONTENT NETWORK - MEMORY FILE
# ============================================================
# LAST UPDATED: 2026-08-14
# STATUS: IN PROGRESS
# CURRENT PHASE: Step 6 - Ready to Test
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
- Status: ✅ Created (key in config.py)
- Cost: FREE

REPLICATE API:
- Status: 🔜 PENDING - User needs to create account
- URL: https://replicate.com
- Expected Cost: ~$0.035/video


# ============================================================
# 4. GITHUB SECRETS (Already Added)
# ============================================================

| Secret Name | Status |
|-------------|--------|
| REPLICATE_API_TOKEN | ✅ Added (placeholder - needs real token) |
| GEMINI_API_KEY | ✅ Added |
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
| Scriptwriter | Google Gemini API | $0 (free) |
| Voice | XTTS-v2 (Replicate) | ~$0.015/min |
| Images | SDXL (Replicate) | ~$0.004/image |
| Subtitles | WhisperX | $0 (local) |
| Video Assembly | MoviePy + FFmpeg | $0 (local) |
| Thumbnails | Pillow (PIL) | $0 (local) |
| YouTube Upload | YouTube Data API v3 | $0 (free) |

MONTHLY BUDGET: $7.00 USD (~520 INR)
ACTUAL ESTIMATE: ~$10.50/month (slightly over, can reduce videos)


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


# ============================================================
# 8. WHAT'S PENDING (NEXT STEPS)
# ============================================================

🔜 STEP 14: Get Replicate API Token
   - Go to https://replicate.com
   - Sign up with GitHub
   - Create API token
   - Update src/config.py: REPLICATE_API_TOKEN = "r8_..."

🔜 STEP 15: Update config.py with all real keys
   - REPLICATE_API_TOKEN (from Step 14)
   - GEMINI_API_KEY (already have)
   - All YouTube credentials (already hardcoded)

🔜 STEP 16: Push code to GitHub
   - git add .
   - git commit -m "Complete pipeline - ready to test"
   - git push

🔜 STEP 17: Test locally
   - python src/main_pipeline.py --test

🔜 STEP 18: Run full pipeline on GitHub Actions
   - Trigger workflow manually
   - Check if video uploads as Private

🔜 STEP 19: Manual publish on YouTube
   - Go to YouTube Studio
   - Find Private video
   - Click Publish

🔜 STEP 20: Create Channel 2 & 3 (separate accounts)
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

IF YOUTUBE UPLOAD FAILS:
- Check refresh token hasn't expired (lasts ~1 week)
- Re-authenticate if needed using OAuth flow
- Verify channel ID is correct

IF REPLICATE FAILS:
- Check API token is valid
- Check you have credits remaining
- Try smaller prompt

IF GEMINI FAILS:
- Check API key is valid
- Check free tier limits not exceeded

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
with all progress. Last status: Step 13 completed (all code written, 
.env removed). Next step: Get Replicate API token and test the pipeline. 
Continue from where we left off."


# ============================================================
# END OF MEMORY FILE
# ============================================================
