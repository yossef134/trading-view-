#!/usr/bin/env python3
"""Verify a delivered /multicam prompt against the frozen template."""
import argparse
import re
import sys
from pathlib import Path

CUT_RE = re.compile(r"^\* At \[(\d+\.\d)s\]:$")
FIRST_HOLD = 0.8
MIN_SPACING = 0.7
TAIL_GUARD = 1.0
BACK_MARK = "back to the original camera position"


def fail(msg: str):
    print(f"FAIL: {msg}")
    sys.exit(1)


def norm(text: str) -> str:
    t = " ".join(text.split())
    t = re.sub(r"\b(?:man|woman|subject)\b", "SUBJ", t)
    t = re.sub(r"\b(?:his|her|their)\b", "POSS", t)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", type=Path)
    ap.add_argument("--duration", type=float, default=None)
    args = ap.parse_args()

    skill_md = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"## The canonical template \(FROZEN\).*?\n```\n(.*?)\n```", skill_md, re.S)
    if not m:
        sys.exit("could not extract the canonical template from SKILL.md")
    template = m.group(1).replace("\r\n", "\n").strip()

    delivered = args.prompt.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()

    marker_head = "Shot sequence:\n\n"
    marker_tail = "\n\nCritical requirements:"
    t_head = template.split(marker_head)[0] + marker_head
    t_tail = marker_tail + template.split(marker_tail)[1]

    if not delivered.startswith(t_head):
        for i, (a, b) in enumerate(zip(t_head.split("\n"), delivered.split("\n")), 1):
            if a != b:
                fail(f"head diverges from the template at line {i}:\n"
                     f"  template : {a!r}\n  delivered: {b!r}")
        fail("head is truncated")
    if not delivered.endswith(t_tail):
        fail("tail (Critical requirements list) diverges from the template")

    middle = delivered[len(t_head):len(delivered) - len(t_tail)].strip()
    chunks = [c for c in re.split(r"\n\n+", middle) if c.strip()]
    if not chunks:
        fail("no shot blocks found after 'Shot sequence:'")

    allowed = set()
    for blk in re.split(r"\n\n+", template.split(marker_head)[1].split(marker_tail)[0].strip()):
        lines = blk.split("\n")
        allowed.add(norm(" ".join(lines[1:])))
    allowed |= {norm(w) for w in re.findall(r"\| `([^`]+)` \|", skill_md)}

    cuts = []
    for i, chunk in enumerate(chunks, 1):
        lines = chunk.split("\n")
        head_line = lines[0]
        cm = CUT_RE.match(head_line)
        if not cm:
            if re.match(r"^\* At \d", head_line):
                fail(f"block {i}: square brackets stripped from {head_line!r}")
            if "[Xs]" in head_line:
                fail(f"block {i}: placeholder not filled: {head_line!r}")
            fail(f"block {i} does not start with `* At [<n.n>s]:`: {head_line!r}")
        body = lines[1:]
        if not body:
            fail(f"block {i} ({head_line}) has no angle description")
        cuts.append((float(cm.group(1)), " ".join(s.strip() for s in body)))

    if "[Xs]" in delivered:
        fail("a `[Xs]` placeholder is still present")

    times = [c[0] for c in cuts]
    for i in range(len(times) - 1):
        if not times[i] < times[i + 1]:
            fail(f"timestamps must ascend: [{times[i]}s] then [{times[i + 1]}s]")
    if args.duration is not None and times[-1] >= args.duration:
        fail(f"last cut [{times[-1]}s] not inside {args.duration:.1f}s clip")

    warnings = []
    if len(cuts) != 4:
        warnings.append(f"{len(cuts)} cuts instead of 4")
    if times[0] < FIRST_HOLD - 0.05:
        warnings.append(f"opening shot holds only {times[0]:.1f}s (min {FIRST_HOLD}s)")
    for a, b in zip(times, times[1:]):
        if b - a < MIN_SPACING - 0.05:
            warnings.append(f"cuts at {a}s and {b}s are {b - a:.1f}s apart (min {MIN_SPACING}s)")
    if args.duration and times[-1] > args.duration - TAIL_GUARD + 0.05:
        warnings.append(f"last cut [{times[-1]}s] within {TAIL_GUARD:.0f}s of end")
    if BACK_MARK not in cuts[-1][1]:
        warnings.append("last shot does not return to original camera")

    print("PASS: template intact outside the mutable zones")
    print(f"cuts: {len(cuts)} -> {times}")
    for i, (t, body) in enumerate(cuts, 1):
        print(f"  {i}. [{t}s]  {body[:70]}")
    for w in warnings:
        print(f"WARNING: {w}")
    sys.exit(0)


if __name__ == "__main__":
    main()
