"""Write the sound-effect <audio> tags into index.html.

python3 tools/sfx.py   (from the project folder, after tools/cut.py)

Each cue is the moment the eye sees the hit; the clip starts early by the sample's own peak so the
sound lands on that frame. REC cues are times on the raw recording (the scenes timed before the pauses
were cut: ad, split) and go through assets/voice/cut-map.json; CUT cues are already on the cut.
"""
import json, subprocess
import numpy as np

peak = {"ping": .229, "whoosh": .162, "pop": .120, "impact": .073}
rate = {"a": 1.0, "b": 1.12, "c": 0.9, "": 1.0}
F = 1 / 30
REC = [  # (time on the recording, sound, take, volume, what): the ad and split scenes
    (10.45, "pop", "b", 0.35, "bills fan out of the phone"),
    (10.85, "whoosh", "a", 0.35, "the money flies off"), (11.2, "whoosh", "c", 0.25, ""),
    (11.7, "whoosh", "b", 0.2, "the phone steps back"),
] + [(t + 0.15, "pop", "abc"[k % 3], 0.22, "people pop up, nearest first" if k == 0 else "")
     for k, t in enumerate([11.85, 12.1, 12.35] + [13.5 + i * 0.22 for i in range(10)])] + [
    (18.9, "whoosh", "c", 0.25, "the crowd walks off"),
    (21.5, "whoosh", "a", 0.2, "the phone comes forward"),
    (23.95, "pop", "c", 0.28, "copies of the ad"), (24.11, "pop", "a", 0.28, ""), (24.27, "pop", "b", 0.28, ""), (24.43, "pop", "c", 0.28, ""),
    (25.0, "pop", "b", 0.4, "the doctor steps in, smiling"),
    (26.7, "whoosh", "b", 0.35, "the X"), (26.98, "pop", "a", 0.55, ""),
    (28.5, "ping", "a", 0.4, "haggling messages"), (29.7, "ping", "c", 0.4, ""), (31.45, "ping", "b", 0.4, ""), (31.9, "ping", "a", 0.4, ""),
    (33.5, "whoosh", "c", 0.35, "content phone whips in"),
    (41.75, "pop", "a", 0.45, "heart"),
    (43.75, "ping", "b", 0.5, "banner drops"),
    (45.6, "ping", "a", 0.6, "«عايز أحجز»"),
    (47.0, "whoosh", "a", 0.3, "split collapses"),
]
STAIRS, LENS, BASE, CLAIM, END = 39.584, 44.498, 54.30, 57.04, 64.58
ROOT_END = 73.04
CUT = [  # (time on the cut, sound, take, volume, what)
    (0.2, "pop", "b", 0.35, "more voices pile in"), (0.32, "pop", "c", 0.35, ""), (0.44, "pop", "a", 0.35, ""),
    (1.05, "whoosh", "b", 0.25, "the noise falls back"),
] + [(t + 0.13, "pop", "cab"[i % 3], 0.3, "the line slams in" if i == 0 else "") for i, t in enumerate([1.11, 1.39, 1.75, 2.23, 2.73])] + [
    (3.05, "whoosh", "a", 0.3, "the voices are blown out"),
    (4.07, "impact", "", 0.28, "«إعلان ممول» hits"), (4.07, "pop", "b", 0.5, ""),
    (4.22, "pop", "c", 0.35, "the doctor gasps"),
    (5.25, "pop", "a", 0.35, "he starts to think"),
    (5.95, "pop", "a", 0.65, "«صح؟» stamp"),
    (6.12, "whoosh", "b", 0.3, "«إعلان ممول» carried into the badge"),
    (STAIRS + 0.05, "whoosh", "b", 0.3, "the content phone whips out"),
    (STAIRS + 0.25, "whoosh", "c", 0.3, "the megaphone whips in"), (STAIRS + 0.5, "pop", "a", 0.4, ""),
    (STAIRS + 1.36, "pop", "a", 0.65, "«مهم» stamp"),
    (STAIRS + 1.85, "whoosh", "a", 0.22, "the megaphone drops to the ground"),
    (STAIRS + 2.0, "pop", "c", 0.4, "steps"), (STAIRS + 2.17, "pop", "b", 0.4, ""), (STAIRS + 2.5, "pop", "a", 0.45, "the ad step rises"),
    (STAIRS + 4.45, "whoosh", "b", 0.3, "ad block rounds into the lens"),
    (LENS + 1.47, "pop", "a", 0.45, "content stickers land"), (LENS + 2.27, "pop", "b", 0.45, ""), (LENS + 3.05, "pop", "c", 0.45, ""),
    (LENS + 3.8, "whoosh", "c", 0.3, "the glass swoops in"),
    (LENS + 4.4, "pop", "b", 0.5, "«هيكبّر»"),
    (LENS + 4.7, "whoosh", "b", 0.22, "follow the line"),
    (LENS + 5.15, "pop", "c", 0.4, "patient"), (LENS + 5.5, "ping", "a", 0.35, "«شكراً يا دكتور»"),
    (LENS + 5.75, "whoosh", "a", 0.4, "whip down to the offers"),
    (LENS + 6.85, "pop", "a", 0.45, "offer stickers land"), (LENS + 7.39, "pop", "b", 0.45, ""),
    (LENS + 7.9, "whoosh", "c", 0.3, "the glass again"),
    (LENS + 8.62, "pop", "c", 0.5, "«هيكبّر»"),
    (LENS + 8.72, "whoosh", "b", 0.22, "follow the line"),
    (LENS + 9.0, "pop", "a", 0.4, "patient"),
    (LENS + 9.1, "ping", "b", 0.3, "haggling"), (LENS + 9.23, "ping", "c", 0.3, ""), (LENS + 9.36, "ping", "a", 0.3, ""),
    (LENS + 9.55, "whoosh", "a", 0.35, "whip home"),
    (BASE + 0.47, "pop", "c", 0.4, "stickers set as bricks"), (BASE + 0.6, "pop", "b", 0.4, ""), (BASE + 0.73, "pop", "a", 0.4, ""),
    (BASE + 1.06, "pop", "c", 0.4, "bricks drop"), (BASE + 1.36, "pop", "b", 0.4, ""),
    (BASE + 2.44, "pop", "a", 0.5, "«الثقة» turns orange"),
    (CLAIM + 0.12, "whoosh", "a", 0.35, "orange flood out of the top brick"),
    (CLAIM + 0.2, "pop", "a", 0.4, "«واستمراريتك»"),
] + [(CLAIM + 0.62 + i * 0.24, "pop", "c", 0.16, "a tick a day" if i == 0 else "") for i in range(7)] + [
    (CLAIM + 2.3, "whoosh", "b", 0.3, "the week clears"),
    (CLAIM + 2.5, "impact", "", 0.32, "«أهم»"),
    (CLAIM + 3.27, "ping", "b", 0.3, "the million lands"),
    (CLAIM + 3.62, "whoosh", "a", 0.25, "the balance rises"),
    (CLAIM + 4.1, "pop", "a", 0.35, "content lands heavy"), (CLAIM + 4.29, "pop", "c", 0.35, "the ad lands"),
] + [(CLAIM + t + 0.26, "pop", "bcabc"[i], 0.3, "bills" if i == 0 else "") for i, t in enumerate([5.66, 5.98, 6.3, 6.6, 6.9])] + [
    (END + 0.1, "whoosh", "b", 0.3, "field contracts into the button"),
    (END + 0.9, "whoosh", "c", 0.3, "the hand whips in"),
    (END + 1.12, "pop", "a", 0.6, "tap: followed"),
    (END + 1.72, "pop", "c", 0.4, "arrow head lands"),
    (END + 2.26, "pop", "b", 0.6, "«يوسف»"),
    (END + 3.32, "pop", "b", 0.4, "stickers"), (END + 4.14, "pop", "c", 0.4, ""), (END + 5.46, "pop", "a", 0.4, ""),
    (END + 7.05, "ping", "a", 0.3, "the button asks once more"),
]

knots = np.array(json.load(open("assets/voice/cut-map.json"))["knots"])
cues = [(float(np.interp(t, knots[:, 0], knots[:, 1])), *r) for t, *r in REC] + CUT
cues.sort(key=lambda c: c[0])
dur = {}
def d(src):
    if src not in dur:
        dur[src] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    return dur[src]
lanes, tags = [], []
for k, (t, s, take, v, what) in enumerate(cues):
    src = f"assets/sfx/{s}-{take}.mp3" if take else "assets/sfx/impact.mp3"
    start = max(0.0, round(t + F - peak[s] / rate[take], 3))
    L = round(min(d(src) - 0.01, ROOT_END - start), 3)
    for i, end in enumerate(lanes):
        if end <= start - 0.01:
            lanes[i] = start + L; lane = i; break
    else:
        lanes.append(start + L); lane = len(lanes) - 1
    c = f"  <!-- {what} -->" if what else ""
    tags.append(f'      <audio id="sfx-{k:02d}" class="clip" src="{src}" data-start="{start}" data-duration="{L}" data-track-index="{4 + lane}" data-volume="{v}"></audio>{c}')
idx = open("index.html").read()
a = idx.index("      <!-- sound on the visible actions")
b = idx.index("    </div>\n    <script>")
block = "      <!-- sound on the visible actions (bundled HyperFrames library; b/c takes are pitch-shifted copies) -->\n" + "\n".join(tags) + "\n"
open("index.html", "w").write(idx[:a] + block + idx[b:])
print(len(tags), "cues on", len(lanes), "lanes")
