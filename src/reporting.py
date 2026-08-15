"""
reporting.py
------------
Daily post-run validation report. Answers:
- Did we hit today's targets (2 long-form + N shorts)?
- What videos/thumbnails were produced and are they passing quality gates?
- Human-readable report + machine-readable JSON, saved to data/reports/

This is the *did it work today?* mechanism you asked for.
"""

import json
from pathlib import Path
from datetime import datetime, date

DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_DIR = DATA_DIR / "reports"

TARGETS = {
    "longform": 2,   # videos per day
    "shorts": 4,
}


def build_report(
    channel: str,
    videos: list,
    test_mode: bool = False,
    targets: dict = None,
    fallback_log: list = None,
) -> dict:
    """
    Build a structured daily report from the list of produced videos.
    Each video dict should contain: video_path, thumbnail_path, is_short,
    validation (result from validation.validate_video), word_count, title.
    Videos using a fallback method get "degraded": True -> flagged NEEDS REVIEW.
    """
    targets = targets or TARGETS
    today = date.today().isoformat()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    produced_long = [v for v in videos if not v.get("is_short")]
    produced_shorts = [v for v in videos if v.get("is_short")]

    passed_long = [v for v in produced_long if v.get("validation", {}).get("passed")]
    failed_long = [v for v in produced_long if not v.get("validation", {}).get("passed")]
    passed_shorts = [v for v in produced_shorts if v.get("validation", {}).get("passed")]
    failed_shorts = [v for v in produced_shorts if not v.get("validation", {}).get("passed")]

    # Videos that used a fallback method (SDXL/XTTS failed) - need human review
    needs_review = [
        v for v in videos
        if v.get("degraded") or not v.get("validation", {}).get("passed")
    ]

    report = {
        "channel": channel,
        "date": today,
        "generated_at": now,
        "test_mode": test_mode,
        "targets": targets,
        "counts": {
            "longform_produced": len(produced_long),
            "longform_passed": len(passed_long),
            "longform_failed": len(failed_long),
            "longform_target": targets.get("longform", 0),
            "shorts_produced": len(produced_shorts),
            "shorts_passed": len(passed_shorts),
            "shorts_failed": len(failed_shorts),
            "shorts_target": targets.get("shorts", 0),
            "needs_review": len(needs_review),
        },
        "targets_met": {
            "longform": len(passed_long) >= targets.get("longform", 0),
            "shorts": len(passed_shorts) >= targets.get("shorts", 0),
        },
        "fallback_log": fallback_log or [],
        "needs_review": [v.get("title", "Untitled") for v in needs_review],
        "videos": [],
    }

    for v in videos:
        validation = v.get("validation", {})
        metadata = validation.get("metadata", {})
        report["videos"].append({
            "title": v.get("title", "Untitled"),
            "video_path": v.get("video_path", ""),
            "thumbnail_path": v.get("thumbnail_path", ""),
            "is_short": v.get("is_short", False),
            "word_count": v.get("word_count", 0),
            "duration_s": metadata.get("duration", 0),
            "duration_ok": metadata.get("duration", 0) >= 480 if not v.get("is_short") else True,
            "resolution": f"{metadata.get('width', 0)}x{metadata.get('height', 0)}",
            "has_audio": metadata.get("has_audio", False),
            "checks": validation.get("checks", {}),
            "passed": validation.get("passed", False),
            "degraded": v.get("degraded", False),
            "uploaded": v.get("uploaded", False),
        })

    return report


def render_human(report: dict) -> str:
    """Render a readable text summary of the report."""
    counts = report["counts"]
    met = report["targets_met"]

    lines = []
    lines.append("=" * 56)
    lines.append(f"DAILY REPORT - {report['channel']}")
    lines.append(f"Date: {report['date']}  Generated: {report['generated_at']}")
    if report.get("test_mode"):
        lines.append("NOTE: TEST MODE - videos were NOT uploaded")
    lines.append("=" * 56)
    lines.append(f"Long-form: {counts['longform_passed']}/{counts['longform_target']} passed  "
                 f"({'MET' if met['longform'] else 'MISSED'})")
    lines.append(f"Shorts:    {counts['shorts_passed']}/{counts['shorts_target']} passed  "
                 f"({'MET' if met['shorts'] else 'MISSED'})")
    lines.append(f"Needs review: {counts['needs_review']}")
    lines.append("-" * 56)

    for v in report["videos"]:
        kind = "SHORT" if v["is_short"] else "LONG"
        if v.get("degraded"):
            status = "REVIEW"
        elif v["passed"]:
            status = "PASS"
        else:
            status = "FAIL"
        dur = v["duration_s"]
        dur_str = f"{int(dur // 60)}:{int(dur % 60):02d}" if dur else "--:--"
        lines.append(f"[{status:6s}] [{kind}] {v['title'][:40]}")
        lines.append(f"        dur {dur_str}  res {v['resolution']}  "
                     f"words {v['word_count']}  audio={'Y' if v['has_audio'] else 'N'}  "
                     f"uploaded={'Y' if v.get('uploaded') else 'N'}")
        if status == "REVIEW":
            lines.append("        ** USED FALLBACK METHOD - NEEDS MANUAL REVIEW **")
        if not v["passed"] and status != "REVIEW":
            for name, c in v["checks"].items():
                if not c["passed"]:
                    lines.append(f"        - {name}: {c['message']}")

    # Fallback method log - shows exactly WHAT failed and WHAT we used instead
    if report.get("fallback_log"):
        lines.append("-" * 56)
        lines.append("FALLBACK METHOD LOG (what failed -> what was used)")
        for entry in report["fallback_log"]:
            lines.append(f"  [{entry.get('time','')}] {entry.get('service','')} / "
                         f"{entry.get('method','')} -> {entry.get('status','')}"
                         + (f" ({entry.get('detail','')})" if entry.get('detail') else ""))

    lines.append("=" * 56)
    return "\n".join(lines)


def save_report(report: dict, channel: str) -> Path:
    """Save report to data/reports/<channel>_<date>.json and .txt."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    base = REPORTS_DIR / f"{channel}_{report['date']}"

    json_path = base.with_suffix(".json")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    txt_path = base.with_suffix(".txt")
    txt_path.write_text(render_human(report), encoding="utf-8")

    # Mirror as latest for easy reading
    latest_json = REPORTS_DIR / f"{channel}_latest.json"
    latest_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    latest_txt = REPORTS_DIR / f"{channel}_latest.txt"
    latest_txt.write_text(render_human(report), encoding="utf-8")

    return json_path


if __name__ == "__main__":
    sample_videos = [
        {
            "title": "Test Video",
            "video_path": "data/videos/test.mp4",
            "thumbnail_path": "data/videos/test_thumb.jpg",
            "is_short": False,
            "word_count": 1600,
            "validation": {"passed": True, "metadata": {"duration": 500,
                          "width": 1920, "height": 1080, "has_audio": True}},
        }
    ]
    rep = build_report("channel_1", sample_videos, test_mode=True)
    print(render_human(rep))
    saved = save_report(rep, "channel_1")
    print(f"Saved: {saved}")