"""
diagnostics.py
--------------
Collects the technical context needed to diagnose a failed run.
Purpose: the daily report (pushed to Telegram) is self-contained.
When you paste it to an AI assistant, it contains EVERYTHING needed
to identify the issue: exact error text, which stage failed, what
method fell back, package versions, system info, and file paths.
"""

import sys
import platform
import traceback
from datetime import datetime

DIAG_ERRORS = []  # list of {stage, error_type, message, traceback}


def record_error(stage: str, exc: Exception):
    """Capture a full exception (type, message, stack) for the report."""
    tb = traceback.format_exc()
    DIAG_ERRORS.append({
        "stage": stage,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "traceback": tb[-3000:],  # last 3000 chars of traceback (enough to diagnose)
        "time": datetime.now().strftime("%H:%M:%S"),
    })


def clear_errors():
    DIAG_ERRORS.clear()


def get_errors() -> list:
    return list(DIAG_ERRORS)


def get_system_info() -> dict:
    """Collect environment + key package versions for the report."""
    from importlib.metadata import version as pkg_version, PackageNotFoundError

    def ver(name):
        try:
            return pkg_version(name)
        except PackageNotFoundError:
            return "not-installed"

    info = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "machine": platform.machine(),
    }
    for pkg in ("moviepy", "google-genai", "replicate",
                "youtube-transcript-api", "Pillow", "yt-dlp",
                "google-api-python-client", "tenacity", "requests"):
        info[pkg] = ver(pkg)
    return info


def render_diagnostics(errors: list, system: dict) -> str:
    """Render a copy-paste-friendly diagnostics block for the report."""
    lines = []
    lines.append("=" * 56)
    lines.append("DIAGNOSTIC BLOCK (paste this to your AI assistant to fix)")
    lines.append("=" * 56)
    lines.append("SYSTEM:")
    for k, v in system.items():
        lines.append(f"  {k}: {v}")
    lines.append("ERRORS:")
    if not errors:
        lines.append("  (none recorded - run completed)")
    for e in errors:
        lines.append(f"  [{e.get('time','')}] STAGE: {e.get('stage','')}")
        lines.append(f"  TYPE: {e.get('error_type','')}")
        lines.append(f"  MESSAGE: {e.get('message','')}")
        tb = e.get('traceback', '')
        if tb:
            lines.append("  TRACEBACK (last lines):")
            for line in tb.strip().splitlines()[-12:]:
                lines.append(f"    {line}")
    lines.append("=" * 56)
    return "\n".join(lines)
