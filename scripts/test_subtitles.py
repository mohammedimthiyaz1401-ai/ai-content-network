import sys
sys.path.insert(0, "src")
from subtitle_timing import get_timed_subtitles, _fixed_chunks

print("== fallback path ==")
for c in _fixed_chunks("This is a fallback test of evenly spaced subtitle chunks."):
    print("[%.1f-%.1f] %s" % (c["start"], c["end"], c["text"]))

print("== whisper path (needs audio file) ==")
import glob
audio = glob.glob("data/audio/*.wav")
print("audio files:", len(audio))
if audio:
    chunks = get_timed_subtitles(audio[0], "This is a test of timed subtitles with multiple words for alignment.")
    print("got", len(chunks), "segments")
    for c in chunks[:5]:
        print("[%.1f-%.1f] %s" % (c["start"], c["end"], c["text"][:60]))
else:
    print("no audio to transcribe - fallback verified")
