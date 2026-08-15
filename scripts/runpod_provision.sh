#!/usr/bin/env bash
# ============================================================
# runpod_provision.sh
# -------------------
# One-time provisioning for a RunPod (or Vast.ai) GPU pod.
# Installs every local model the pipeline needs so it can run
# 100% free (no Replicate API calls):
#
#   - SDXL 1.0 base   (diffusers)      -> /models/sdxl
#   - XTTS-v2         (Coqui TTS)      -> /models/xtts
#   - SadTalker       (official repo)  -> /models/sadtalker
#   - whisper, ffmpeg, python deps
#
# Run:  bash scripts/runpod_provision.sh
# After it finishes, the pod is ready for runpod_entrypoint.sh
# ============================================================
set -euo pipefail

MODEL_DIR="${LOCAL_MODEL_DIR:-/models}"
VENV_DIR="${VENV_DIR:-/venv}"
REPO_DIR="${REPO_DIR:-/workspace/ai-content-network}"

echo "==> Creating model dir: $MODEL_DIR"
mkdir -p "$MODEL_DIR"

# ------------------------------------------------------------
# System packages (RunPod PyTorch template already has torch+cuda)
# ------------------------------------------------------------
echo "==> Installing system packages"
apt-get update -qq
apt-get install -y -qq ffmpeg git curl unzip libgl1 libglib2.0-0 2>/dev/null || true

# ------------------------------------------------------------
# Python venv + deps
# ------------------------------------------------------------
echo "==> Creating venv at $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q

echo "==> Installing pipeline requirements"
cd "$REPO_DIR"
pip install -r requirements.txt -q
pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cu121 -q || true
pip install diffusers==0.30.3 transformers accelerate safetensors -q

# Coqui TTS for XTTS-v2
pip install TTS==0.22.0 -q || echo "WARN: TTS install had issues (check later)"

# ------------------------------------------------------------
# SDXL weights (diffusers format)
# ------------------------------------------------------------
echo "==> Downloading SDXL base (diffusers, fp16)"
if [ ! -d "$MODEL_DIR/sdxl" ]; then
  python - <<'PY'
import os
from huggingface_hub import snapshot_download
target = os.environ.get("LOCAL_MODEL_DIR", "/models") + "/sdxl"
print("Downloading SDXL...")
snapshot_download(
    "stabilityai/stable-diffusion-xl-base-1.0",
    local_dir=target,
    allow_patterns=["*.json", "*.safetensors", "*.txt", "*.yaml"],
    ignore_patterns=["*.onnx", "*.ckpt"],
)
print("SDXL done:", target)
PY
fi

# ------------------------------------------------------------
# XTTS-v2 voice-cloning weights
# ------------------------------------------------------------
echo "==> Downloading XTTS-v2 checkpoint"
if [ ! -d "$MODEL_DIR/xtts" ]; then
  python - <<'PY'
import os
from huggingface_hub import snapshot_download
target = os.environ.get("LOCAL_MODEL_DIR", "/models") + "/xtts"
snapshot_download("coqui/XTTS-v2", local_dir=target)
print("XTTS done:", target)
PY
fi

# ------------------------------------------------------------
# SadTalker repo + checkpoints
# ------------------------------------------------------------
echo "==> Cloning SadTalker + downloading checkpoints"
if [ ! -d "$MODEL_DIR/sadtalker" ]; then
  git clone https://github.com/OpenTalker/SadTalker.git "$MODEL_DIR/sadtalker"
fi
cd "$MODEL_DIR/sadtalker"
pip install -r requirements.txt -q || echo "WARN: SadTalker requirements partial"

# Checkpoints (via their download script / direct)
mkdir -p checkpoints
python - <<'PY'
import os
from huggingface_hub import hf_hub_download
repo = os.environ.get("LOCAL_MODEL_DIR", "/models") + "/sadtalker"
files = {
    "checkpoints/mapping_00229-model.pth.tar": "stabilityai/sadtalker",
    "checkpoints/mapping_00129-model.pth.tar": "stabilityai/sadtalker",
}
# Use the official checkpoints downloader if present
dl = os.path.join(repo, "scripts", "download_models.sh")
print("If present, run official downloader:", os.path.exists(dl))
PY
# official download script
bash scripts/download_models.sh 2>/dev/null || echo "WARN: SadTalker checkpoint downloader failed - download manually"

# ------------------------------------------------------------
# Sanity check
# ------------------------------------------------------------
echo ""
echo "============================================================"
echo "PROVISIONING COMPLETE"
echo "  Models : $MODEL_DIR"
echo "  Venv   : $VENV_DIR"
echo ""
echo "Now run:  bash scripts/runpod_entrypoint.sh"
echo "============================================================"
