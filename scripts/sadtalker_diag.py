"""Runner-side diagnostic: reproduce SadTalker exactly as the pipeline does,
capture FULL traceback + prediction error + env info."""
import os
import sys
import traceback
import glob
import httpx
import replicate
from replicate import files

print("PYTHON:", sys.version)
print("REPLICATE_VERSION:", getattr(replicate, "__version__", "n/a"))
print("HTTPX_VERSION:", httpx.__version__)

MODEL = "cjwbw/sadtalker:a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3"

imgs = sorted(glob.glob("data/images/*.png"))
print("images found:", len(imgs), imgs[:2])
if not imgs:
    print("NO IMAGES - cannot test")
    sys.exit(2)
img = imgs[0]

# voice sample from assets
voice = None
for cand in ["assets/voice_samples/channel_1.wav",
             "assets/voice_samples/channel_1_aria.wav",
             "assets/voice_samples/channel_1_jenny.wav"]:
    if os.path.exists(cand):
        voice = cand
        break
print("voice:", voice)

uri = files.create(img).urls["get"]
print("img uri ok:", uri[:30])
aud_uri = files.create(voice).urls["get"]
print("audio uri ok:", aud_uri[:30])

try:
    output = replicate.run(
        MODEL,
        input={
            "source_image": uri,
            "driven_audio": aud_uri,
            "still_mode": True,
            "preprocess": "crop",
            "facerender": "facevid2vid",
            "use_eyeblink": True,
            "use_enhancer": False,
            "pose_style": 0,
        },
    )
    print("OUTPUT:", output)
    print("SADTALKER_DIAG: SUCCESS")
except Exception as e:
    print("SADTALKER_DIAG: FAILED", type(e).__name__, repr(str(e)))
    traceback.print_exc()
