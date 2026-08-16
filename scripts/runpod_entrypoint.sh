#!/usr/bin/env bash
# ============================================================
# runpod_entrypoint.sh
# --------------------
# Runs the daily pipeline on the GPU pod using LOCAL models
# (free - no Replicate). Reads secrets from a gitignored file
# (scripts/server_secrets.env) OR environment variables.
#
# Morning + night split is controlled by LONGFORM_TARGET/SHORTS_TARGET.
#
# Usage:
#   LONGFORM_TARGET=1 SHORTS_TARGET=2 bash scripts/runpod_entrypoint.sh
# ============================================================
set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/ai-content-network}"
VENV_DIR="${VENV_DIR:-/venv}"
MODEL_DIR="${LOCAL_MODEL_DIR:-/models}"

cd "$REPO_DIR"
source "$VENV_DIR/bin/activate"

# Load secrets if present (gitignored)
SECRETS="${SERVER_SECRETS:-$REPO_DIR/scripts/server_secrets.env}"
if [ -f "$SECRETS" ]; then
  echo "==> Loading secrets from $SECRETS"
  set -a
  # shellcheck disable=SC1090
  source "$SECRETS"
  set +a
fi

# Defaults to a full run unless overridden
export LONGFORM_TARGET="${LONGFORM_TARGET:-1}"
export SHORTS_TARGET="${SHORTS_TARGET:-2}"
export USE_LOCAL_MODELS="${USE_LOCAL_MODELS:-1}"
export LOCAL_MODEL_DIR="$MODEL_DIR"
# GPU box: whisper CPU cost is irrelevant here, real timed subtitles on
export WHISPER_SUBTITLES="${WHISPER_SUBTITLES:-1}"

export REPLICATE_API_TOKEN="${REPLICATE_API_TOKEN:-}"
export GEMINI_API_KEY="${GEMINI_API_KEY:-}"
export YOUTUBE_CLIENT_ID="${YOUTUBE_CLIENT_ID:-}"
export YOUTUBE_CLIENT_SECRET="${YOUTUBE_CLIENT_SECRET:-}"
export YOUTUBE_REFRESH_TOKEN="${YOUTUBE_REFRESH_TOKEN:-}"
export YOUTUBE_CHANNEL_ID="${YOUTUBE_CHANNEL_ID:-UCd5yt5eiM97UDyWkt9mZGQw}"
export YOUTUBE_CLIENT_ID_CH2="${YOUTUBE_CLIENT_ID_CH2:-}"
export YOUTUBE_CLIENT_SECRET_CH2="${YOUTUBE_CLIENT_SECRET_CH2:-}"
export YOUTUBE_REFRESH_TOKEN_CH2="${YOUTUBE_REFRESH_TOKEN_CH2:-}"
export YOUTUBE_CHANNEL_ID_CH2="${YOUTUBE_CHANNEL_ID_CH2:-}"
export YOUTUBE_CLIENT_ID_CH3="${YOUTUBE_CLIENT_ID_CH3:-}"
export YOUTUBE_CLIENT_SECRET_CH3="${YOUTUBE_CLIENT_SECRET_CH3:-}"
export YOUTUBE_REFRESH_TOKEN_CH3="${YOUTUBE_REFRESH_TOKEN_CH3:-}"
export YOUTUBE_CHANNEL_ID_CH3="${YOUTUBE_CHANNEL_ID_CH3:-}"
export TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
export TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

echo "============================================================"
echo "RUNPOD ENTRYPOINT - LOCAL MODELS"
echo "  Target: ${LONGFORM_TARGET} long + ${SHORTS_TARGET} shorts"
echo "  Models: $MODEL_DIR"
echo "============================================================"

python src/main_pipeline.py
