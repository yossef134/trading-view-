"""Assemble compositions/*.html from src/: fills /*COMMON*/ /*PHONE*/ /*PEOPLE*/ /*RETIME*/.

python3 tools/build.py   (from the project folder, after tools/cut.py; edit src/, never compositions/)
"""
import json, os
common = open("src/common.css").read(); phone = open("src/phone.css").read(); people = open("src/people.js").read()
knots = json.load(open("assets/voice/cut-map.json"))["knots"]
kn = ",".join(f"[{a:g},{b:g}]" for a, b in knots)
retime = f'''// timed on the raw recording; tools/cut.py shortened its pauses, so each tween moves onto the cut (assets/voice/cut-map.json)
      const CUT = [{kn}];
      const cut = (t) => {{
        let i = 1;
        while (i < CUT.length - 1 && CUT[i][0] < t) i++;
        const [a0, b0] = CUT[i - 1], [a1, b1] = CUT[i];
        return a1 === a0 ? b1 : b0 + ((b1 - b0) * (t - a0)) / (a1 - a0);
      }};
      const retime = (tl, from, to) => {{
        const s0 = cut(from), len = cut(to) - s0;
        tl.getChildren(false, true, true).forEach((c) => {{
          const a = c.startTime(), d = c.totalDuration();
          let na = cut(from + a) - s0, nd = cut(from + a + d) - s0 - na;
          if (d > 0) {{
            nd = Math.min(Math.max(nd, d * 0.5), len); // a pause can speed a move up, never past 2x
            na = Math.min(Math.max(na, 0), len - nd); // and nothing spills past the scene's ends
            c.timeScale(d / nd);
          }}
          c.startTime(na);
        }});
        // timeScale() renders a tween once, which records its start values too early (before the tweens
        // ahead of it have run); forget them so each tween reads its start when the playhead reaches it
        tl.invalidate();
      }};'''
for f in sorted(x for x in os.listdir("src") if x.endswith(".html")):
    s = open(f"src/{f}").read()
    s = s.replace("/*COMMON*/", common).replace("/*PHONE*/", phone).replace("/*PEOPLE*/", people).replace("/*RETIME*/", retime)
    open(f"compositions/{f}", "w").write(s)
    print("built", f)
