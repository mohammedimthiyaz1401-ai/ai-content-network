"""Runner-side diagnostic v2: self-contained - generates its own test image
from the committed voice sample + a local PIL image so it doesn't need data/.
Captures FULL traceback + prediction error."""
import os
import sys
import traceback
import httpx
import replicate
from replicate import files
from PIL import Image, ImageDraw

print("PYTHON:", sys.version)
print("HTTPX_VERSION:", httpx.__version__)

# Build a test portrait (a face-ish image is NOT required to reproduce the
# SDK error - SadTalker needs any valid image + audio URI to start a prediction).
test_img = "diag_portrait.png"
img = Image.new("RGB", (512, 512), (40, 40, 90))
d = ImageDraw.Draw(img)
d.ellipse([156, 80, 356, 280], fill=(224, 190, 170))  # face
d.rectangle([100, 260, 412, 512], fill=(30, 30, 60))   # body
img.save(test_img)

voice = "assets/voice_samples/channel_1.wav"
print("voice exists:", os.path.exists(voice))

MODEL = "cjwbw/sadtalker:a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3"

uri = files.create(test_img).urls["get"]
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
