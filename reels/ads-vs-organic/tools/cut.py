"""Cut the pauses out of the voiceover and write the time map the scenes use.

python3 tools/cut.py   (from the project folder)

in : assets/voice/voice-norm.wav            the loudness-normalised recording ("recording clock")
     assets/voice/transcript-whisper.json   word stamps on the recording clock
out: assets/voice/voice-cut.wav             the recording with every pause shortened ("cut clock")
     assets/voice/cut-map.json              knots (recording time, cut time), linear in between
     assets/voice/words-cut.json            word stamps snapped to the speech and given on both clocks
"""
import json, re, subprocess, wave
import numpy as np

SRC, OUT = "assets/voice/voice-norm.wav", "assets/voice/voice-cut.wav"
# scene seams on the recording clock: the pause around each keeps room for the hand-off
SEAMS = [7.5, 33.4, 49.0, 54.2, 65.1, 68.4, 76.8]
TAIL = 2.0  # the end card holds this long after the last word


def keep(a, b, first, last):
    L = b - a
    if first:
        return min(L, 0.05)
    if last:
        return min(L, 0.25)
    if any(a - 0.15 <= s <= b + 0.15 for s in SEAMS):
        return min(L, 0.4)
    return min(L, 0.12 if L < 0.4 else 0.16 if L < 0.8 else 0.22)


log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", SRC, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]

with wave.open(SRC) as w:
    sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
    raw = w.readframes(w.getnframes())
dtype = {2: np.int16, 4: np.int32}[sw]
x = np.frombuffer(raw, dtype=dtype).reshape(-1, ch).astype(np.float64)
dur = len(x) / sr

sil = list(zip(starts, ends[: len(starts)]))
segs, knots, pos, t_new = [], [(0.0, 0.0)], 0.0, 0.0
for a, b in sil:
    K = keep(a, b, a <= 0.01, b >= dur - 0.01)
    # keep the speech, then the first and last K/2 of the pause
    segs.append((pos, a + K / 2))
    pos = b - K / 2
    t_new += a - knots[-1][0]
    knots.append((a, round(t_new, 4)))
    t_new += K
    knots.append((b, round(t_new, 4)))
segs.append((pos, dur))
t_new += dur - knots[-1][0]
knots.append((dur, round(t_new, 4)))
knots.append((dur + TAIL, round(t_new + TAIL, 4)))  # the hold after the voice keeps 2 s

fade = int(0.01 * sr)
r = np.linspace(0, 1, fade)[:, None]
y = x[int(segs[0][0] * sr): int(segs[0][1] * sr)]
for s0, s1 in segs[1:]:
    # 10 ms crossfade at every cut, drawn from the pause so the length stays exact
    nxt = x[int(s0 * sr) - fade: int(s1 * sr)]
    y = np.concatenate([y[:-fade], y[-fade:] * (1 - r) + nxt[:fade] * r, nxt[fade:]])

with wave.open(OUT, "wb") as w:
    w.setnchannels(ch); w.setsampwidth(sw); w.setframerate(sr)
    w.writeframes(np.clip(y, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype).tobytes())

ko, kn = np.array([k[0] for k in knots]), np.array([k[1] for k in knots])
M = lambda t: float(np.interp(t, ko, kn))
json.dump({"recording_end": round(dur, 3), "cut_end": round(len(y) / sr, 3), "knots": knots}, open("assets/voice/cut-map.json", "w"))

# whisper often starts a word inside the pause before it: snap starts to the end of that pause
words = json.load(open("assets/voice/transcript-whisper.json"))
out = []
for i, wd in enumerate(words):
    s, e = wd["start"], wd["end"]
    for a, b in sil:
        if a <= s < b: s = b
        if a < e <= b: e = a
    e = max(e, s + 0.08)
    out.append({"i": i, "start": round(M(s), 3), "end": round(M(e), 3), "start_rec": round(s, 3), "end_rec": round(e, 3)})
json.dump(out, open("assets/voice/words-cut.json", "w"), indent=0)
print(f"recording {dur:.2f} s -> cut {len(y) / sr:.2f} s, {len(sil)} pauses")
