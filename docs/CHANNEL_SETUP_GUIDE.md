# Aria Future - YouTube Channel Setup Guide

Handle: `@ariafuturetech`
Channel ID: `UCd5yt5eiM97UDyWkt9mZGQw`
URL: https://youtube.com/@ariafuturetech

---

## 1. Channel Name & Handle
- **Name:** Aria Future
- **Handle:** @ariafuturetech (already taken - you own it)
- **Description visibility:** Public

---

## 2. Channel Description (About section)

```
Welcome to ARIA FUTURE 👋

I'm Aria - your guide to the AI tools, tech lifehacks and passive income
strategies that are shaping tomorrow.

Every day I break down:
🤖 The latest AI tools (and how to actually use them)
💰 Side hustles & passive income that work
🧠 Future-tech insights you won't find anywhere else

New videos DAILY. Long-form deep dives + quick Shorts.

🔔 Subscribe so you don't miss the next money-making tool.

NOTE: This channel uses AI-generated content for education and
entertainment. Always do your own research before making decisions.

Let me break this down for you - trust me on this. 🚀
```

---

## 3. Links (External)
- Website: (leave empty for now)
- Instagram/Twitter: (add later as they grow)

---

## 4. Banner (2560x1440)
- File: `assets/branding/banner.png`
- Shows "ARIA FUTURE" + tagline "AI Tools | Passive Income | The Future of Tech"
- Safe area is 1546x423 in the center - text is placed well inside it.

**How to upload:** YouTube Studio -> Customization -> Branding -> Banner image

---

## 5. Profile Picture (800x800)
- File: `assets/branding/profile.png`
- Aria's consistent face (same seed as video host = 12345).

**How to upload:** YouTube Studio -> Customization -> Branding -> Picture

---

## 6. Video Watermark (optional)
- Use `profile.png` resized to 150x150 if desired
- Display: Entire video, End screen recommended

---

## 7. SEO / Keywords (Input your channel keywords)
```
AI, artificial intelligence, AI tools, future technology, passive income,
side hustle, make money online, AI automation, tech news, AI news,
tech lifehacks, future tech, self improvement, online business,
money making apps
```

---

## 8. Upload Defaults (Settings -> Upload defaults)
- **Title:** `{video title}`
- **Description:** (generated per-video; includes hashtags)
- **Language:** English (US)
- **Category:** Science & Technology (28)
- **Licence:** Standard YouTube Licence
- **Visibility:** PRIVATE (human-in-the-loop publishing on purpose)
- **Comments:** On (or restricted - your call)
- **AI disclosure (altered content):** Already set programmatically

---

## 9. Advanced Settings
- **Country:** (your country or leave default)
- **Kids content:** "No, set this channel as not made for kids" (set programmatically too)
- **Shorts preview button:** Enabled (videos are currently long-form + Shorts)
- **Playlists:** (optional - create later)

---

## 10. Channel Goals (YouTube Studio -> Goals)
Enrollment is optional but helps analytics. Recommended:
- **Goal:** Grow channel / Increase reach

---

## 11. Automation / AI Disclosure
Videos are uploaded PRIVATE with `alteredContent: true` - YouTube's
required AI-content disclosure flag is already applied by
`src/youtube_uploader.py` (line 95).

---

## 12. Important / Safe practices
- YouTube requires genuine long-term engagement; consistent daily uploads of
  quality content is the plan (2 long-form + 4 Shorts/day).
- All uploads remain PRIVATE until you review and publish manually.
- Keep recommended video length 8-12 min for long-form for early retention.

---

## 13. Config in code (`src/config.py`)
```python
CHANNELS = {
    "channel_1": {
        "name": "Aria Future",
        "youtube_channel_id": "UCd5yt5eiM97UDyWkt9mZGQw",
        "category_id": "28",
        "default_tags": ["AI", "artificial intelligence", "technology",
                         "future", "passive income", "tech tools"],
    },
}
```
- Persona: `src/scriptwriter.py` -> CHANNEL_PERSONAS["channel_1"]
- Face seed: 12345 (`src/media_generator.py` -> CHANNEL_SEEDS)
- Voice: ElevenLabs "Rachel" sample (`assets/voice_samples/channel_1.wav`)