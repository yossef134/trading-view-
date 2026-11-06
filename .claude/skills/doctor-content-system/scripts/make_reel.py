"""make_reel.py SRC START END WORDS.json TITLE OUT.mp4 [FIXES.json]
Cut a vertical clip, upscale to 1080x1920, burn Arabic word-chunk captions + an on-screen title."""
import json, subprocess, sys
src, t0, t1, wj, title, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
fixes = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else {}
W = json.load(open(wj))
off = float(W[0].get("base", 0)) if W and "base" in W[0] else 0
words = [w for w in W if w["s"] >= t0 - 0.05 and w["e"] <= t1 + 0.3]
def ts(x):
    x = max(x, 0); h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Cairo ExtraBold,78,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,2,2,60,60,190,1
Style: Title,Cairo ExtraBold,66,&H00000000,&H00FFFFFF,&H0000E1FF,&H0000E1FF,1,0,0,0,100,100,0,0,3,22,0,8,70,70,150,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
dur = t1 - t0
ev.append(f"Dialogue: 1,{ts(0)},{ts(min(dur, 4.0))},Title,,0,0,0,,{title}")
chunk = []
for w in words:
    chunk.append(w)
    if len(chunk) == 3 or w["w"].endswith(("؟", ".", "،")):
        a, b = chunk[0]["s"] - t0, chunk[-1]["e"] - t0
        txt = " ".join(fixes.get(c["w"], c["w"]) for c in chunk)
        ev.append(f"Dialogue: 0,{ts(a)},{ts(b + 0.05)},Cap,,0,0,0,,{txt}")
        chunk = []
if chunk:
    a, b = chunk[0]["s"] - t0, chunk[-1]["e"] - t0
    ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,," + " ".join(fixes.get(c["w"], c["w"]) for c in chunk))
ass = out.rsplit(".", 1)[0] + ".ass"
open(ass, "w").write(hdr + "\n".join(ev) + "\n")
crop = sys.argv[8] if len(sys.argv) > 8 else ""
if crop:  # zoom on the call window, dark bands for title (top) and captions (bottom)
    vf = (f"scale=1080:1920:flags=lanczos,crop={crop},scale=1080:-2:flags=lanczos,eq=contrast=1.05:saturation=1.1,unsharp=5:5:0.6,"
          f"pad=1080:1920:0:(oh-ih)/2:color=0x101418,ass={ass}")
else:
    vf = f"scale=1080:1920:flags=lanczos,eq=contrast=1.05:saturation=1.1,unsharp=5:5:0.6,ass={ass}"
af = "highpass=f=80,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5:LRA=11"
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t0 + off), "-to", str(t1 + off), "-i", src,
                "-vf", vf, "-af", af, "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
print("->", out)
