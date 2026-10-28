"""Write src/captions.html from the cut-clock word stamps.

python3 tools/captions.py   (from the project folder, after tools/cut.py; then tools/build.py)
"""
import json, html
words = json.load(open("assets/voice/words-cut.json"))
OFFSET = 6.364  # the captions host starts with the ad scene (cut clock)
END = 57.04     # captions stop where the claim takes the frame
# (spoken text as said, corrected spelling; first and last whisper word index)
G = [
 ("وهقولك كمان ليه الإعلان لوحده", 16, 20), ("ممكن يضيّع فلوسك", 21, 23),
 ("الإعلان الممول هيوصّلك", 24, 27), ("لناس أكتر، أيوه", 28, 30),
 ("بس لو مش بتقدّم قيمة", 31, 35), ("ولا المريض حس إنك", 36, 39), ("فعلاً تستاهل الثقة دي", 40, 43),
 ("حتى لو صرفت مليون إعلان", 44, 48), ("هتلاقي النتيجة برضه مش عاجباك", 49, 53),
 ("اللي هيكلمك في الغالب", 54, 57), ("هيكون مش جاد", 58, 60), ("وهيركّز على السعر", 61, 64), ("والفصال وخلاص", 65, 67),
 ("إن المريض بيشوفك باستمرار", 73, 76), ("بيحس إنك فعلاً بتحل مشكلته", 77, 81), ("وإن الحل ده", 82, 85), ("بيكلمه هو بس", 86, 88),
 ("وده فعلاً اللي بيجيب لك", 89, 93), ("واحد عايز يكشف عندك", 94, 97), ("أو حتى يعمل معاك العملية", 98, 102),
 ("الإعلان الممول مهم", 103, 105),
 ("الإعلان هيكبّر ده للمريض", 121, 124),
 ("برضه هيكبّر ده للمريض", 130, 133),
]
rows = []
for k, (text, a, b) in enumerate(G):
    t_in = max(words[a]["start"] - 0.08, OFFSET + 0.1)
    t_out = words[b]["end"] + 0.35
    if k + 1 < len(G):
        nxt = words[G[k + 1][1]]["start"] - 0.08
        t_out = min(max(t_out, t_in + 0.9), nxt)  # never overlap the next group
    t_out = min(t_out, END - 0.05)
    rows.append((text, round(t_in - OFFSET, 3), round(t_out - OFFSET, 3)))
divs = "\n".join(f'    <div class="cap" id="cap-{k}" data-in="{i}" data-out="{o}">{html.escape(t)}</div>' for k, (t, i, o) in enumerate(rows))
out = f'''<template>
  <style>
/*COMMON*/
    #root .cap {{ position: absolute; left: 80px; top: 1196px; width: 860px; text-align: center; direction: rtl; white-space: nowrap; font-size: 58px; line-height: 1.3; color: var(--color-ink); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{divs}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      gsap.set(".cap", {{ opacity: 0 }});
      // one group at a time: in on its first word (blur 8 → 0), out with a hard kill at its end
      document.querySelectorAll(".cap").forEach((el) => {{
        const a = parseFloat(el.dataset.in), b = parseFloat(el.dataset.out);
        tl.fromTo(el, {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power4.out" }}, a);
        tl.to(el, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, b - 0.1);
        tl.set(el, {{ opacity: 0, visibility: "hidden" }}, b);
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
'''
open("src/captions.html", "w").write(out)
for r in rows: print(r)
