"""
telegram_notifier.py
--------------------
Sends the daily pipeline report (including fallback method log) to Telegram.

Setup (one-time, ~2 min):
1. Message @BotFather -> /newbot -> get bot token (TELEGRAM_BOT_TOKEN)
2. Message your bot once (any text)
3. Message @userinfobot -> get your chat id (TELEGRAM_CHAT_ID)
4. Add both as GitHub Secrets

Silently no-ops if tokens aren't set (so local runs don't fail).
"""

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def telegram_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN) and bool(TELEGRAM_CHAT_ID)


def send_message(text: str) -> bool:
    """Send a plain text message to Telegram. Returns True on success."""
    if not telegram_configured():
        print("[TELEGRAM] Not configured (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID empty) - skipping")
        return False

    # Telegram limit is 4096 chars; split if needed
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]

    ok = True
    for chunk in chunks:
        try:
            resp = requests.post(
                TELEGRAM_API.format(token=TELEGRAM_BOT_TOKEN),
                json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "HTML"},
                timeout=30,
            )
            if resp.status_code != 200:
                print(f"[TELEGRAM] Failed: {resp.text[:200]}")
                ok = False
            else:
                print(f"[TELEGRAM] Sent {len(chunk)} chars")
        except Exception as e:
            print(f"[TELEGRAM] Error: {e}")
            ok = False

    return ok


def send_report(render_human: str) -> bool:
    """Send the rendered daily report (from reporting.render_human)."""
    header = "<b>AI Content Network - Daily Report</b>\n\n"
    return send_message(header + render_human)


def send_upload_notification(video: dict) -> bool:
    """
    Notify the owner when a video is uploaded to YouTube as PRIVATE.
    Message includes the title, type, duration, and the direct review URL
    so the owner can watch -> validate -> make public.
    """
    if not telegram_configured():
        return False

    title = video.get("title", "Untitled video")
    video_id = video.get("video_id", "")
    url = video.get("url", f"https://youtube.com/watch?v={video_id}") if video_id else ""
    kind = "SHORT" if video.get("is_short") else "LONG-FORM"
    dur = video.get("duration_s")
    dur_str = f"{int(dur//60)}:{int(dur%60):02d}" if dur else "?"

    lines = [
        "<b>📤 New video uploaded (PRIVATE - awaiting your review)</b>",
        f"\n🎬 <b>{title}</b>",
        f"\nType: {kind}",
        f"Duration: {dur_str}",
    ]
    if url:
        lines.append(f"\n🔗 <a href=\"{url}\">Review on YouTube Studio</a>")
    lines.append("\n<i>Video is PRIVATE. Watch, validate, then set to Public.</i>")

    return send_message("\n".join(lines))


if __name__ == "__main__":
    print("TELEGRAM NOTIFIER - self test")
    if telegram_configured():
        print("Configured - sending test message")
        ok = send_message("<b>Test</b> from AI Content Network - notifier works!")
        print(f"Result: {ok}")
    else:
        print("NOT configured - set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars")