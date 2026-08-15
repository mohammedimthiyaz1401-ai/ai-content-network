# ============================================================
# 🧠 AI CONTENT NETWORK - MEMORY FILE
# ============================================================
# LAST UPDATED: 2026-08-15 (SADTALKER ROOT CAUSE FOUND + FIXED: feed dedicated host PORTRAIT with real face; runner diag + local repro both confirmed)
# STATUS: IN PROGRESS
# CURRENT PHASE: Verifying SadTalker animated host on next run; deciding on GPU server for Ch.2
# ============================================================
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
- BUG FIXED 2026-08-15 (commit 9c800ec): SadTalker + XTTS + SDXL retries were
  crashing with "exceptions must derive from BaseException". Cause: tenacity
  does `raise retry_exc from fut.exception()` and replicate's stored error isn't
  a clean BaseException -> Python raises TypeError. FIX: added reraise=True to
  ALL tenacity @retry decorators in media_generator.py + sadtalker_host.py.
  Night run (18:00 UTC) is first live test of the fix.
- STATUS: morning run (09:10 UTC) STILL showed SadTalker FAILED (ran before fix
  was dispatched). Static portrait fallback used -> the "dull, no one talking"
  look the user complained about. Fix is now pushed + live for night run.

REPLICATE API:
- Status: ✅ WORKING (tested - SDXL image generated)
- URL: https://replicate.com/account/api-tokens
- Credit: $5 added (2026-08-14); EMAIL from Replicate 2026-08-15: ~$2.35 left,
  estimated 21h remaining at current burn (~$1/run). Top-up $5 for ~1 more week
  of daily runs, OR move to GPU server for $0 Replicate cost.
- Model: stability-ai/sdxl (must use version ID, NOT :latest tag)
- Working version: 7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc
- Rate limit: 6 req/min with <$5 credit (small delay between calls) - seen 429s


# ============================================================
# 4. GITHUB SECRETS (Already Added)
# ============================================================

| Secret Name | Status |
|-------------|--------|
| REPLICATE_API_TOKEN | ✅ Updated with real token |
| GEMINI_API_KEY | ✅ Updated by user (new AQ.Ab key) 2026-08-15 |
| YOUTUBE_CLIENT_ID | ✅ Added |
| YOUTUBE_CLIENT_SECRET | ✅ Added |
| YOUTUBE_REFRESH_TOKEN | ✅ Added |
| YOUTUBE_CHANNEL_ID | ✅ Added (name is actually YOUTUBE_CHANNEL_ID_CH1 - see note) |
| TELEGRAM_BOT_TOKEN | ✅ Added by user 2026-08-15 (8916953161:...TESTED working) |
| TELEGRAM_CHAT_ID | ✅ Added by user 2026-08-15 (798122743) |

IMPORTANT 2026-08-15: GitHub secret is named YOUTUBE_CHANNEL_ID_CH1, but the
workflow was reading YOUTUBE_CHANNEL_ID -> env var was EMPTY in the first run.
FIXED: daily_morning/night workflows map `secrets.YOUTUBE_CHANNEL_ID_CH1` to
env YOUTUBE_CHANNEL_ID. ALSO config.py now has fallback default
"UCd5yt5eiM97UDyWkt9mZGQw" so pipeline never runs with an empty channel id.

LOCAL SECRETS: scripts/load_secrets.ps1 (GITIGNORED) has ALL real values incl.
new GEMINI key (AQ.Ab...), REPLICATE, YOUTUBE creds, TG token + chat id 798122743.
Load via:  . .\scripts\load_secrets.ps1  (then run pipeline in SAME shell session)

GitHub Secrets URL: https://github.com/mohammedimthiyaz1401-ai/ai-content-network/settings/secrets/actions


# ============================================================
# 5. PROJECT STRUCTURE
# ============================================================

ai-content-network/
├── .github/workflows/
│   ├── daily_morning.yml    ✅ (06:00 UTC, 1 long + 2 shorts)
│   └── daily_night.yml      ✅ (18:00 UTC, 1 long + 2 shorts)
│   (old daily_automation.yml DELETED - it ran BOTH halves in one go and timed out)
├── src/
│   ├── __init__.py
│   ├── config.py               ✅ DONE (API keys - NO .env; YOUTUBE_CHANNEL_ID fallback;
│   │                                LONGFORM_TARGET/SHORTS_TARGET env (default 2/4))
│   ├── main_pipeline.py        ✅ DONE (orchestrator; DAILY_TARGETS from config env)
│   ├── media_generator.py      ✅ DONE (SDXL+XTTS reraise=True; local→Replicate→fallback)
│   ├── trend_sniffer.py        ✅ REWRITTEN (Gemini brainstorm, NO YouTube scraping)
│   ├── scriptwriter.py         ✅ DONE (Gemini API, MODEL_NAME exported)
│   ├── video_assembler.py      ✅ DONE (MoviePy 2.x + PIL text + KEN BURNS + crossfade)
│   ├── shorts_clipper.py       ✅ NEW (clips 4 shorts from long-form, 9:16)
│   ├── validation.py           ✅ NEW (quality gates: 8min, thumbnail, audio, res)
│   ├── reporting.py            ✅ NEW (daily report vs targets + fallback log)
│   ├── diagnostics.py          ✅ NEW (error type/message/traceback + package versions)
│   ├── telegram_notifier.py    ✅ NEW (report + PER-UPLOAD PRIVATE-review alerts)
│   ├── sadtalker_host.py       ✅ NEW (talking host: SadTalker→static, reraise=True)
│   ├── subtitle_timing.py      ✅ NEW (whisper timed captions + fallback)
│   ├── local_models.py         ✅ NEW (local SDXL/XTTS/SadTalker for GPU server)
│   └── youtube_uploader.py     ✅ DONE (OAuth2 refresh token; upload notifications)
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
- Actual measured 2026-08-15: ~$1 per half-day run (SDXL 10x + XTTS + SadTalker
  fallback). Replicate email: ~$2.35 left (~21h). ~1 week of daily runs at ~$1/run.
- GPU server (Ch.2): $0 Replicate cost. Budget guidance given: RunPod 4090
  ~$20-30/mo, Vast.ai 4090 ~$15-25/mo, A100 ~$60-90/mo (overkill).

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
✅ Step 24: GitHub Secrets updated by user + voice sample swapped (2026-08-15)
   - User updated GEMINI_API_KEY / TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID on GitHub web
   - User pushed ElevenLabs Rachel voice sample directly to GitHub (19.2s, 44.1kHz).
   - Local synced to match (fetch/rebase). Remote master == local HEAD.
✅ Step 25: Cloud run #1 DISPATCHED on GitHub Actions (2026-08-15)
   - Manual workflow_dispatch (HTTP 204). Run #1 "Daily Content Generation" in progress.
   - Passed: checkout, python setup, deps install, FFmpeg install. Now in Run Pipeline.
   - Monitoring: https://github.com/mohammedimthiyaz1401-ai/ai-content-network/actions/runs/31869862758
✅ Step 25b: requisites.txt SLIMMED (2026-08-15)
   - REMOVED unused: yt-dlp, pydantic, youtube-transcript-api (trend sniffer no
     longer scrapes YouTube). KEPT openai-whisper (used for timed subtitles).
✅ Step 25c: TIMED SUBTITLES added (WhisperX-style) - subtitle_timing.py
   - Whisper base model transcribes the generated audio -> REAL timestamped captions
     (字幕 appear exactly when each phrase is spoken, vs old fixed 3s chunks).
   - FAILSAFE: falls back to evenly-spaced chunks if whisper unavailable/fails,
     so video assembly NEVER breaks. Shorts skip whisper (too short, keep fast).
   - video_assembler.add_subtitles() now accepts audio_path and uses it.
✅ Step 25d: YOUTUBE_CHANNEL_ID env bug FIXED (2026-08-15)
   - First cloud run showed YOUTUBE_CHANNEL_ID empty in env (secret name mismatch).
   - Workflows now map secrets.YOUTUBE_CHANNEL_ID_CH1 -> env YOUTUBE_CHANNEL_ID;
     config.py also hardcodes fallback UCd5yt5eiM97UDyWkt9mZGQw.
   - Verified: CH1 channel id prints UCd5yt5eiM97UDyWkt9mZGQw locally.
✅ Step 25e: CHANNEL BRANDING created (2026-08-15)
   - scripts/generate_channel_branding.py (SDXL + PIL text): profile.png (800x800),
     banner.png (2560x1440) -> assets/branding/.
   - docs/CHANNEL_SETUP_GUIDE.md: full channel setup (name/handle @ariafuturetech,
     description w/ AI disclosure, SEO keywords, upload defaults, advanced settings).
   - USER REPLACED with own images: assets/branding/profile.jpg + openart banner.
✅ Step 25f: DAILY RUN SPLIT INTO MORNING + NIGHT (2026-08-15)
   - User: "post one video morning, one at night; 2 long + 4 shorts daily".
   - config.py: LONGFORM_TARGET + SHORTS_TARGET env (default 2/4).
   - daily_morning.yml (06:00 UTC) + daily_night.yml (18:00 UTC): each 1 long + 2 shorts.
   - Old daily_automation.yml DELETED (single-run approach timed out ~2h).
   - Both workflows get LONGFORM_TARGET=1, SHORTS_TARGET=2, 120-min timeout.
✅ Step 25g: FIRST FULL PRODUCTION RUN = MORNING RUN SUCCESS (2026-08-15, run 31876311262)
   - workflow_dispatch via API (JSON via --data-binary @file; PowerShell -d quoting fails).
   - SUCCESS in ~112 min. 1 long-form PASS ("Gemini 2.0 Flash vs GPT-4o: Is This Finally
     The AI Killer?", 10:42, 1920x1080, 1666 words, uploaded=Y) + 2 shorts PASS (0:45,
     1080x1920, uploaded=Y). targets_met true.
   - Fallback log: SDXL 10x used, XTTS used, SadTalker FAILED x4 -> static portrait
     (the "nobody talking" look). One 429 retried OK.
   - Artifact "morning-content-1" = 58.9MB (video + scripts + reports). Download NOTE:
     must re-list artifacts for a FRESH signed URL (old URL -> truncated/corrupt zip).
   - Local YouTube token is 401-stale vs GitHub's working refresh token: verify uploads
     via GitHub reports, not the local API.
✅ Step 25h: SADTALKER tenacity BUG FIXED (2026-08-15, commit 9c800ec)
   - "exceptions must derive from BaseException" -> tenacity `raise retry_exc from
     fut.exception()` when replicate stores a non-BaseException error.
   - FIX: reraise=True on ALL @retry decorators (media_generator.generate_image_sdxl,
     generate_voice_xtts, sadtalker_host.generate_talking_clip_sadtalker).
   - Verified via local simulation (real FakeModelError caught). Live test = night run.
   - ❗ SUPERSEEDED (see Step 25l): reraise=True was NOT the real fix. The error message
     was faithful to the actual Replicate prediction failure - see root cause below.
✅ Step 25l: SADTALKER ROOT CAUSE FOUND + FIXED (2026-08-15, commits 03a17bc/a11f196/9cfc4d3)
   - Night run (31882911455) completed SUCCESS (~121 min, 3/3 uploaded) but SadTalker STILL
     failed -> static portrait fallback again. Full log saved %TEMP%\opencode\night_run_log.txt.
   - Dispatched .github/workflows/sadtalker_diag.yml (id 335051067) -> REAL traceback:
     replicate/run.py:81 raise ModelError(prediction) ->
     "replicate.exceptions.ModelError: exceptions must derive from BaseException".
     So the prediction genuinely FAILED server-side; the SDK faithfully reported prediction.error.
   - KEY EXPERIMENT: same ModelError reproduces LOCALLY with a synthetic faceless image.
     But assets/branding/profile.jpg (real face) + channel_1_aria.wav -> SUCCESS (real out.mp4).
     => ROOT CAUSE: pipeline fed SadTalker a TOPIC image (image_paths[0]/[3], e.g. "apartment
     interior") with NO detectable face. SadTalker face detection fails -> model raises a string
     error server-side -> SDK shows "exceptions must derive from BaseException". Local repros
     earlier "succeeded" only because those data/images/*.png happened to contain faces.
   - FIX (commit 9cfc4d3): src/sadtalker_host.py adds PORTRAIT_CANDIDATES +
     get_host_portrait() returning a dedicated REAL-FACE portrait (assets/branding/profile.jpg
     first). src/main_pipeline.py now passes host_portrait to generate_host_intro instead of
     topic images. compile OK + get_host_portrait resolves correctly. Pushed to master.
   - NEXT VERIFY: next run should show SadTalker "used" (animated host) for the first time.
✅ Step 25i: KEN BURNS + CROSSFADE (2026-08-15, commit a3763f5)
   - video_assembler._ken_burns(): slow zoom (in/out alternating) centered on a fixed
     output canvas (fixes off-size bug). create_video_from_images adds CrossFadeOut(0.5).
   - Tested: 3 images -> 15s video at exact (1920,1080).
✅ Step 25j: LOCAL GPU MODELS + RUNPOD SCRIPTS (2026-08-15, commit a3763f5)
   - src/local_models.py: generate_image_local (diffusers SDXL), generate_voice_local
     (Coqui TTS), generate_host_clip_local (SadTalker inference.py subprocess).
     Enabled by USE_LOCAL_MODELS=1 + /models. Local takes priority over Replicate.
   - scripts/runpod_provision.sh (apt ffmpeg, venv, torch cu121, model weights to /models)
     + scripts/runpod_entrypoint.sh (sources server_secrets.env, runs pipeline).
   - scripts/server_secrets.env.example + .gitignore entries added.
✅ Step 25k: PER-UPLOAD TELEGRAM ALERT (2026-08-15, commit 8abd236)
   - telegram_notifier.send_upload_notification(): "<b>📤 New video uploaded (PRIVATE -
     awaiting your review)</b>" + title, SHORT/LONG-FORM, duration, watch link, private note.
   - youtube_uploader.batch_upload fires it after each successful private upload.
   - Tested locally: message SENT (311 chars, True).


# ============================================================
# 8. WHAT'S PENDING (NEXT STEPS)
# ============================================================

🔜 STEP 26: NEXT RUN = FIRST VERIFY OF THE REAL SADTALKER FIX (18:00 UTC night run)
   - The fix (commit 9cfc4d3) feeds a dedicated real-face portrait. Watch fallback log:
     does SadTalker finally show "used" (animated host) instead of static fallback?
   - If still failing: check that profile.jpg is committed (it is) + runner has it
     (assets/branding/profile.jpg). Diagnostic workflow id 335051067 available to re-run.

🔜 STEP 27: Review + publish tonight's uploads on YouTube Studio
   - User validates PRIVATE videos, then makes public manually.

🔜 STEP 28: Decide GPU server for Channel 2
   - Option A (recommended): rent 4090 GPU (~$15-25/mo) + USE_LOCAL_MODELS=1 ->
     $0 Replicate for Ch.2. Scripts ready (runpod_provision.sh + entrypoint).
   - Option B: keep Replicate (~$1/run, ~$2.35 credit left).

🔜 STEP 29: Create Channel 2 & 3 (separate accounts)
   - New Gmail per channel, YouTube channel, OAuth2, update config ACTIVE_CHANNELS.

🔜 LATER (deferred): analytics scorecard, Instagram Reels posting (user said
   "not required as of now, future task").

DECLINED 2026-08-15: mobile/Telegram -> opencode fix bridge (opencode serve +
   bridge bot, or opencode web + Tailscale). User SKIPPED: laptop not always-on
   (only ~1-2h evenings), no cheap VPS. Pipeline continues as-is: owner opens
   laptop in the evening and reviews/pastes Telegram errors manually.

KNOWN ISSUE - FULL PIPELINE TIMING:
   - Split solved this: each half-day run is 1 long + 2 shorts, still ~100+ min
     on GitHub Actions (sequential Replicate calls + MoviePy 8-min encode).
     Morning run finished in ~112 min (under the 120-min timeout, barely).
   - If runs keep approaching the cap: reduce to 1 long + 1 short per run, or
     move to GPU server (local models are much faster, no per-call throttle).

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

DELIVERY SPLIT (per channel, since 2026-08-15):
- MORNING run (06:00 UTC): 1 long + 2 shorts
- NIGHT run (18:00 UTC): 1 long + 2 shorts
- = 2 long + 4 shorts per channel per day (user's chosen cadence)

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
- LOCAL refresh token is STALE (401) as of 2026-08-15 - the GitHub one works;
  verify production uploads via the GitHub artifact reports instead.

IF GITHUB RUN FAILS WITH EMPTY YOUTUBE_CHANNEL_ID:
- The GitHub secret is named YOUTUBE_CHANNEL_ID_CH1 (not YOUTUBE_CHANNEL_ID).
- Workflows map it: `YOUTUBE_CHANNEL_ID: ${{ secrets.YOUTUBE_CHANNEL_ID_CH1 }}`
- config.py also has the channel id as fallback default, so it never breaks.

IF ARTIFACT DOWNLOAD IS CORRUPT/TRUNCATED:
- The signed zip URL expires. RE-LIST the artifacts first (GET .../artifacts)
  to get a FRESH URL, then download. Old URL -> BadZipFile/142-byte file.

IF SADTALKER ERRORS "exceptions must derive from BaseException":
- ❗ REAL ROOT CAUSE (2026-08-15): the source_image has NO detectable face.
  SadTalker face detection fails server-side -> model raises a string error ->
  SDK faithfully reports it as prediction.error (replicate/run.py:81 ModelError).
  This reproduces LOCALLY too (verified with synthetic faceless image).
- FIX: feed a DEDICATED real-face portrait, NOT a topic/screenshot image.
  src/sadtalker_host.py get_host_portrait() returns assets/branding/profile.jpg
  (verified SUCCESS -> real out.mp4). Commit 9cfc4d3 wires it into the pipeline.
- The tenacity reraise=True change (commit 9c800ec) was harmless but NOT the fix.

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
with all progress. Last status: Cloud runs are LIVE and SUCCESSFUL. Morning
run 31876311262 produced 1 long + 2 shorts (all uploaded PRIVATE, uploaded=Y).
Pipeline split into daily_morning (06:00) + daily_night (18:00), 1 long + 2
shorts each. YOUTUBE_CHANNEL_ID_CH1 secret + config fallback fixed. SadTalker
tenacity reraise=True bug fixed (commit 9c800ec) - night run is the first
LIVE test of the talking host. Per-upload Telegram PRIVATE-review alerts
added. Ken Burns + crossfade in. Local GPU models + RunPod scripts ready for
Channel 2 (~$15-25/mo, $0 Replicate). Replicate balance ~$2.35.
Next step: check night run result (did SadTalker animate the host?), have the
user review/publish the PRIVATE uploads, then decide GPU server vs Replicate."


# ============================================================
# END OF MEMORY FILE
# ============================================================
