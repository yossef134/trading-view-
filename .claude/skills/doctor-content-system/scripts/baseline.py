#!/usr/bin/env python3
"""Baseline snapshot for case studies, and the before/after comparison (stdlib only).

usage
  baseline.py snapshot --raw raw.json --analysis analysis.json --out baseline.json
  baseline.py compare  --before baseline.json --after baseline_day30.json --out compare.md

Take the snapshot on audit day. At day 30/60 re-run fetch_instagram.py account + analyze.py, snapshot
again, then compare. The comparison only states measured differences; it does not claim causes.
"""
import argparse
import datetime as dt
import json
import statistics as st


def snapshot(raw, an):
    p = raw["profile"]
    reels = [x for x in raw["posts"] if x["format"] == "reel" and x.get("views")]
    reels.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    last10 = reels[:10]
    ts = sorted(x["timestamp"] for x in raw["posts"] if x.get("timestamp"))
    now = dt.datetime.fromisoformat(raw["fetched_at"].replace("Z", "+00:00"))
    last30 = [t for t in ts if (now - dt.datetime.fromisoformat(t.replace("Z", "+00:00"))).days <= 30]
    return {
        "username": p["username"], "taken_at": raw["fetched_at"],
        "followers": p.get("followers"), "following": p.get("following"), "posts_total": p.get("posts_count"),
        "posts_last_30d": len(last30),
        "median_views_last10_reels": st.median([x["views"] for x in last10]) if last10 else None,
        "reels_counted": len(last10),
        "median_er": an["health"].get("median_er"),
        "stage": an.get("stage", {}).get("code"),
        "best_reel": max(reels, key=lambda x: x["views"])["url"] if reels else None,
        "bio": p.get("biography"), "external_url": p.get("external_url"),
    }


def pct(a, b):
    if a in (None, 0) or b is None:
        return "n/a"
    return f"{(b - a) / a * 100:+.0f}%"


def compare(b, a):
    rows = [("المتابعين", "followers"), ("بوستات آخر 30 يوم", "posts_last_30d"),
            ("وسيط مشاهدات آخر 10 ريلز", "median_views_last10_reels"), ("معدل التفاعل (وسيط)", "median_er"),
            ("إجمالي البوستات", "posts_total")]
    out = [f"# قبل / بعد: @{b['username']}", "",
           f"من {b['taken_at'][:10]} إلى {a['taken_at'][:10]}", "",
           "| المؤشر | قبل | بعد | التغير |", "|---|---|---|---|"]
    for label, k in rows:
        out.append(f"| {label} | {b.get(k)} | {a.get(k)} | {pct(b.get(k), a.get(k))} |")
    out += ["", f"- المرحلة: {b.get('stage')} ← {a.get('stage')}",
            f"- البايو اتغير: {'أيوه' if b.get('bio') != a.get('bio') else 'لأ'}",
            "", "> أرقام مقاسة فقط. التغير ممكن يكون له أسباب غير المحتوى (إعلانات، موسم، ترند)."]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot"); s.add_argument("--raw", required=True); s.add_argument("--analysis", required=True)
    s.add_argument("--out", required=True)
    c = sub.add_parser("compare"); c.add_argument("--before", required=True); c.add_argument("--after", required=True)
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "snapshot":
        snap = snapshot(json.load(open(a.raw, encoding="utf-8")), json.load(open(a.analysis, encoding="utf-8")))
        json.dump(snap, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(snap, ensure_ascii=False))
    else:
        md = compare(json.load(open(a.before, encoding="utf-8")), json.load(open(a.after, encoding="utf-8")))
        open(a.out, "w", encoding="utf-8").write(md)
        print(md)


if __name__ == "__main__":
    main()
