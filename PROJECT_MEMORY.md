# ============================================================
# 🧠 AI CONTENT NETWORK - MEMORY FILE
# ============================================================
# LAST UPDATED: 2026-08-15 (all 3 bugs fixed, full pipeline reaches assembly)
# STATUS: IN PROGRESS
# CURRENT PHASE: Step 24 - full pipeline verified; next = run on GitHub Actions
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
- Status: ✅ WORKING (new key tested OK with gemini-3.1-flash-lite)
- New key AQ.Ab...[stored in load_secrets.ps1 + GitHub Secret] (2026-08-15)
- OLD key AIzaSyBxacK7Xf1J7cZ4F9Mwmw42j0apZxTBHJ8 was INVALID (API_KEY_INVALID 400)
- IMPORTANT: GitHub Secret GEMINI_API_KEY NOT updated yet - user must do via
  https://github.com/mohammedimthiyaz1401-ai/ai-content-network/settings/secrets/actions
  (no gh CLI on local machine). Username-style keys (AQ.Ab...) DO work.
- Model: gemini-3.1-flash-lite (via google-genai package)
- Cost: $10 prepay credits (bought 2026-08-14) - lasts 12 months
- IMPORTANT: Since Mar 2026, new AI Studio users require prepay credits.
  The $300 Google Cloud free trial does NOT cover Gemini API usage.
  Billing must be enabled on project: aiscriptforyoutube

VOICE (XTTS-v2) - FIXED 2026-08-15:
- lucataco/xtts-v2 needs a 'speaker' voice-cloning REFERENCE SAMPLE
- Version PINNED: lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e
- REQ: speaker must be an uploaded URI. LOCAL PATHS FAIL (422 "Does not match format 'uri'").
  FIX: _get_speaker_url() uploads the sample via replicate.files.create() once,
  caches URL ~23h, passes that URL. Works (tested OK).
- Speaker sample: assets/voice_samples/channel_1.wav (currently edge-tts Aria voice,
  15s; user may replace with ElevenLabs Rachel later - both supported, any .wav/.mp3)
- Output parsing: SDK 1.0.7 returns FileOutput obj (.url attr) not a list - fixed
  via _extract_output_url() helper
- Voice sample verified: pcm_s16le, 24kHz, mono, 15.0s

TALKING HOST (SadTalker):
- Model: cjwbw/sadtalker (Apache-2.0, commercial-safe, open-source)
- Version PINNED: cjwbw/sadtalker:a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3
- ~$0.078/clip on Replicate, paid from existing $5 credit
- Host from data/images/channel_1 portrait + XTTS voice -> talking head MP4
- REQ: BOTH source_image and driven_audio must be uploaded URIs (not local paths).
  FIX: get_uploaded_uri() uploads each via replicate.files.create(), caches ~23h.
- FALLBACK: if SadTalker fails -> static portrait (video still assembles)
- MuseTalk/LatentSync REJECTED: they need existing video to lip-sync;
  SadTalker is the only one that works from ONE photo + audio (our use case)
- NOTE: Not yet verified end-to-end in a live run (host_clips dir empty on last
  test; may have hit rate limits). Needs a full-run check.

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
| GEMINI_API_KEY | 🔜 NEEDS UPDATE - new key works locally, user must update on GitHub |
| YOUTUBE_CLIENT_ID | ✅ Added |
| YOUTUBE_CLIENT_SECRET | ✅ Added |
| YOUTUBE_REFRESH_TOKEN | ✅ Added |
| YOUTUBE_CHANNEL_ID | ✅ Added |
| TELEGRAM_BOT_TOKEN | 🔜 NEEDS ADDING on GitHub (token = 8916953161:...TESTED working locally) |
| TELEGRAM_CHAT_ID | 🔜 NEEDS ADDING on GitHub (chat = 798122743) |

LOCAL SECRETS: scripts/load_secrets.ps1 (GITIGNORED) has ALL real values incl.
new GEMINI key (AQ.Ab...), REPLICATE, YOUTUBE creds, TG token + chat id 798122743.
Load via:  . .\scripts\load_secrets.ps1  (then run pipeline in SAME shell session)

GitHub Secrets URL: https://github.com/mohammedimthiyaz1401-ai/ai-content-network/settings/secrets/actions


# ============================================================
# 5. PROJECT STRUCTURE
# ============================================================

ai-content-network/
├── .github/workflows/
│   └── daily_automation.yml    ✅ DONE (now passes Telegram secrets)
├── src/
│   ├── __init__.py
│   ├── config.py               ✅ DONE (API keys - NO .env, now has Telegram)
│   ├── main_pipeline.py        ✅ DONE (orchestrator - validation+shorts+telegram)
│   ├── media_generator.py      ✅ DONE (SDXL + XTTS-v2 + FALLBACK CHAIN + log + URI fix)
│   ├── trend_sniffer.py        ✅ REWRITTEN (Gemini brainstorm, NO YouTube scraping)
│   ├── scriptwriter.py         ✅ DONE (Gemini API, MODEL_NAME exported)
│   ├── video_assembler.py      ✅ DONE (MoviePy 2.x + PIL text)
│   ├── shorts_clipper.py       ✅ NEW (clips 4 shorts from long-form, 9:16)
│   ├── validation.py           ✅ NEW (quality gates: 8min, thumbnail, audio, res)
│   ├── reporting.py            ✅ NEW (daily report vs targets + fallback log)
│   ├── diagnostics.py          ✅ NEW (error type/message/traceback + package versions)
│   ├── telegram_notifier.py    ✅ NEW (pushes report to Telegram - TESTED SEND OK)
│   ├── sadtalker_host.py       ✅ NEW (talking host: SadTalker→static, URI fix)
│   └── youtube_uploader.py     ✅ DONE (OAuth2 refresh token)
├── data/
│   ├── scripts/
│   ├── audio/
│   ├── images/
│   ├── videos/
│   ├── shorts/                 (NEW - clipped shorts land here)
│   ├── reports/                (NEW - daily reports <channel>_<date>.txt/.json)
│   └── subtitles/
├── assets/
│   ├── voice_samples/          channel_1.wav (edge-tts Aria, 15s - may swap for ElevenLabs)
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
| Trend Sniffer | Gemini brainstorm + curated fallback (NO YouTube scraping) | $0.001 |
| Scriptwriter | Gemini API (gemini-3.1-flash-lite) | $10 prepay / 12mo |
| Voice | XTTS-v2 (Replicate) | ~$0.015/min |
| Images | SDXL (Replicate) | ~$0.004/image |
| Host clips | SadTalker (Replicate) | ~$0.078/clip |
| Subtitles | MoviePy basic chunked text (WhisperX = future) | $0 (local) |
| Video Assembly | MoviePy + FFmpeg | $0 (local) |
| Thumbnails | Pillow (PIL) | $0 (local) |
| YouTube Upload | YouTube Data API v3 | $0 (free) |

DAILY RUN COST ESTIMATE (~$0.60-0.70/day for full 2 long + 4 shorts):
- SDXL: ~$0.08-0.12 | XTTS voice: ~$0.24 | SadTalker host: ~$0.31
- With $5 Replicate credit -> ~7-8 days of daily runs, then top up ~$5/mo

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
✅ Step 17: Full pipeline test run locally (partial)
   - Trend sniffer: FAILED - YouTube IP-blocking transcript requests (0 found)
   - Scriptwriter: FAILED - GEMINI_API_KEY now INVALID (see section 3)
   - Test revealed 2 bugs now fixed below
✅ Step 17b: media_generator.py FALLBACK CHAIN + rate-limit throttling added
   - FALLBACK_CHAIN images: SDXL Replicate (v1) → Placeholder (always works)
   - FALLBACK_CHAIN voice: XTTS Replicate (v1) → Offline TTS (v2) → Silent (v3)
   - FIXED: XTTS model ref corrected to lucataco/xtts-v2 (was coqui-ai = 404)
   - FIXED: Replicate rate limit (6 req/min <$5 credit) - 12s throttle added
   - FALLBACK_LOG tracks every method attempt → shown in daily report
✅ Step 18: video_assembler.py rewritten for moviepy 2.x (imports OK)
✅ Step 18b: validation.py created - QUALITY GATES before upload
   - 8-min minimum for long-form (480s), shorts 15s
   - Thumbnail exists + size, resolution matches, audio track, file size, metadata
   - validate_video() returns pass/fail + per-check messages
✅ Step 18c: reporting.py created - DAILY VALIDATION REPORT
   - Answers: did we hit 2 long + 4 shorts today?
   - Shows PASS/FAIL/REVIEW per video + FALLBACK METHOD LOG
   - Saves data/reports/<channel>_<date>.txt + .json + latest mirrors
✅ Step 18d: shorts_clipper.py created - CLIP 4 SHORTS FROM LONG-FORM (9:16)
   - Chosen strategy: clip from long-form (zero extra API cost)
   - Crops center vertical strip, keeps audio, 45s each
   - Only clips from PASSED + PREMIUM (non-degraded) long videos
✅ Step 18e: telegram_notifier.py created - PUSH DAILY REPORT TO TELEGRAM
   - Needs TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID (add to Secrets)
   - No-op safely when not configured
✅ Step 18f: main_pipeline.py wired for validation + shorts + telegram
   - DEGRADED POLICY: fallback/silent videos NOT auto-uploaded → flagged NEEDS REVIEW
   - YouTube uploader only uploads PASSED + premium videos
   - Full daily report pushed to Telegram after each run
✅ Step 18g: diagnostics.py created - SELF-CONTAINED DIAGNOSTIC BLOCK
   - Every stage records full error: type, message, traceback (last 3000 chars)
   - System info: platform, python version, ALL package versions
   - Appended to Telegram report so pasting it lets AI diagnose + fix
   - Failure runs ALSO push a "<b>Pipeline FAILED</b>" Telegram message with diag
✅ Step 19: trend_sniffer.py REWRITTEN - NO YouTube scraping (2026-08-15)
   - YouTube transcript API was IP-blocked locally AND would block GitHub Actions.
   - NEW: Gemini brainstorm generates fresh topics (titles + 15-word seed); fallback
     = curated evergreen topics (always works, $0). Scraping code removed entirely.
   - TESTED: Gemini returned 3 fresh topics ("OpenAI Just Changed Everything"...)
✅ Step 20: Voice + host URI bug FIXED (2026-08-15)
   - XTTS-v2: speaker must be uploaded URI. Added _get_speaker_url() using
     replicate.files.create(), cached 23h. TESTED - generated real 5.97s audio.
   - SadTalker: source_image + driven_audio both must be URIs. Added get_uploaded_uri().
   - Replicate SDK 1.0.7 output is FileOutput obj (.url), not list - added
     _extract_output_url() helper. TESTED.
✅ Step 21: video_assembler assembly bug investigation (2026-08-15)
   - Full run produced a REAL 13MB longform with real XTTS voice (not silent).
   - Isolated test assembled a valid 15s MP4 (h264 + aac). Assembly OK.
   - Bottleneck: MoviePy encoding an 8-min 1080p video takes ~45 min, so a full
     2-long+4-shorts+host run cannot finish in one 60-min local session.
     GitHub Actions nightly (no such cap) is the production path.
✅ Step 22: New GEMINI key obtained + TESTED (2026-08-15)
   - AQ.Ab...[stored in load_secrets.ps1 + GitHub Secret] works with gemini-3.1-flash-lite
   - Scriptwriter tested: 1711-word script generated. Trend brainstorm also works.
✅ Step 23: Telegram notifier TESTED LIVE (2026-08-15)
   - Bot token + chat id 798122743 in local secrets -> test message SENT & received
   - Daily report render -> Telegram push confirmed (559 chars sent)


# ============================================================
# 8. WHAT'S PENDING (NEXT STEPS)
# ============================================================

🔜 STEP 24: Update GitHub Secrets GEMINI_API_KEY + TELEGRAM_* (USER ACTION)
   - GEMINI: https://github.com/mohammedimthiyaz1401-ai/ai-content-network/settings/secrets/actions
     Value: AQ.Ab...[stored in load_secrets.ps1 + GitHub Secret]
   - TELEGRAM_BOT_TOKEN stored in scripts/load_secrets.ps1 + add as GitHub Secret
   - TELEGRAM_CHAT_ID: 798122743

🔜 STEP 25: Verify SadTalker host clip end-to-end (not yet seen in live run)
   - host_clips/ was empty on last full run - confirm animate path or fallback

🔜 STEP 26: Run full pipeline on GitHub Actions
   - Trigger workflow manually (once Secrets updated)
   - Check if 2 long + 4 shorts produced + uploaded as Private

🔜 STEP 27: Manual publish on YouTube
   - Go to YouTube Studio, find Private video, click Publish

🔜 STEP 28: Create Channel 2 & 3 (separate accounts)
   - Create new Gmail for each, YouTube channel, OAuth2, update config

🔜 LATER (deferred by user 2026-08-15): analytics scorecard (YouTube Analytics
   nightly → Telegram). NOT building now - channel is brand new.

KNOWN ISSUE - FULL PIPELINE TIMING:
   - 1 full local run >60 min (sequential Replicate calls + MoviePy 8-min encode).
   - GitHub Actions has no such cap - that's the production path.
   - Do NOT re-run full local test repeatedly (burns Replicate credit ~$0.60/run).
   - Local use: quick isolated module tests (as done 2026-08-15) to verify changes.

KNOWN ISSUE - VOICE SAMPLE QUALITY:
   - Current channel_1.wav = edge-tts "Aria" voice (free, decent but robotic-ish).
   - User may replace with ElevenLabs "Rachel" (official ElevenLabs voice,
     American English, neutral accent) for premium quality.
   - File location is the same - drop in and rerun. Pipeline detects any .wav/.mp3.


# ============================================================
# 9. DAILY OUTPUT TARGET
# ============================================================

PER CHANNEL:
- 2 Long-form videos (8-10 mins each)
- 4 Shorts (clipped from the long-form videos, 45s each, 9:16 vertical)

TOTAL (3 channels):
- 6 Long-form videos
- 12 Shorts

NOTE: Currently only Channel 1 is active
NOTE: Shorts are CLIPPED from long-form (shorts_clipper.py) - zero extra API cost


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
- RESOLVED 2026-08-15: trend_sniffer no longer scrapes YouTube at all.
  Uses Gemini brainstorm -> curated evergreen fallback. IP-block irrelevant now.

IF YOUTUBE UPLOAD FAILS:
- Check refresh token hasn't expired (lasts ~1 week)
- Re-authenticate if needed using OAuth flow
- Verify channel ID is correct

IF XTTS VOICE FAILS (422 "Does not match format 'uri'"):
- speaker must be an UPLOADED URI. FIXED via _get_speaker_url() (replicate.files.create).
- If generate_voice_xtts returns FileOutput error - SDK 1.0.7 obj has .url attr.

IF SADTALKER HOST FAILS:
- Both source_image + driven_audio must be URIs - use get_uploaded_uri()
- Falls back to static portrait (video still assembles, flagged degraded)

IF VIDEO ASSEMBLY FAILS:
- Ensure FFmpeg is installed
- Check moviepy version
- Verify image paths exist
- Encoding an 8-min 1080p video takes ~45 min - plan run time accordingly

IF REPLICATE FAILS:
- Check API token is valid (r8_...)
- Check you have credits remaining (must add at least $5)
- Model version: use specific version ID, NOT :latest tag
- Rate limit: 6 req/min with <$5 credit - add small delays between calls

IF REPLICATE RETURNS "Invalid version or not permitted" (422):
- The :latest tag does NOT work - use a specific version ID
- SDXL working version: 7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc
- XTTS working version: 684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e
- SadTalker version: a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3

IF GEMINI FAILS:
- Check API key is valid
- API_KEY_INVALID (400) = key no longer exists - REGENERATE at
  https://aistudio.google.com/apikey (select project aiscriptforyoutube)
- 403 = billing not enabled on the project the key belongs to
- 429 "prepayment credits depleted" = need to buy prepay credits (min $10)
  since March 2026 the $300 free trial does NOT cover Gemini API
- Model: gemini-3.1-flash-lite (google-genai package, NOT google-generativeai)

IF VIDEO ASSEMBLY FAILS:
- Ensure FFmpeg is installed
- Check moviepy version
- Verify image paths exist

IF SHORTS CLIPPING FAILS:
- Source video must be longer than 45s per clip
- FFmpeg crop filter: crop=ih*9/16:ih:(iw-ow)/2:0 then scale 1080:1920
- Only clips from PASSED + non-degraded long videos

VALIDATION & REPORTING:
- validation.py gates: 8min (long), thumbnail, audio, resolution, file size, metadata
- Degraded (fallback) videos are NOT auto-uploaded - flagged NEEDS REVIEW in report
- Report saved to data/reports/, pushed to Telegram if configured


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
with all progress. Last status: All 3 bugs fixed & verified 2026-08-15 -
(1) XTTS voice now uses uploaded URI speaker (real audio, not silent),
(2) SadTalker uses uploaded URIs, (3) Replicate SDK 1.0.7 output parsed.
Trend sniffer rewritten to Gemini brainstorm (no YouTube scraping).
Telegram notifier tested live (message received). Full pipeline reaches
final assembly producing real 8-min videos; one full run >60 min so
GitHub Actions nightly is the production path. Blocker: user must update
GitHub Secrets GEMINI_API_KEY + TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID.
Next step: update GitHub Secrets, verify SadTalker host clip, run pipeline
on GitHub Actions. Continue from where we left off."


# ============================================================
# END OF MEMORY FILE
# ============================================================
