#!/usr/bin/env python3
"""Compute the numbers behind a Facebook page audit, mirroring analyze.py exactly so the
Instagram and Facebook sections of the report use the same method (stdlib only).

usage: analyze_facebook.py --facebook facebook.json --out analysis_facebook.json [--tz Africa/Cairo]

Performance model (same as Instagram)
  value   video post -> views (plays); photo/text/link post -> likes + comments + shares
  index   value / median value of the SAME post type (video vs non-video), posts < 48h excluded
  win     index >= 1.5      lose  index <= 0.5      else normal
A type is only scored with >= 3 mature posts AND a median of at least 10 (same guard as Instagram:
with a median of 1-2 likes, "11x the usual" is noise).

Comments count is sometimes missing (null) on Facebook's side, not zero; treated as missing, not 0.
"""
import argparse
import datetime as dt
import json
import re
import statistics as st
from collections import Counter

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

WIN, LOSE = 1.5, 0.5
IMMATURE_HOURS = 48
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
CTA_PATTERNS = {
    "follow": r"\b(follow|تابع|اتابع|فولو)\b", "comment": r"\b(comment|اكتب|علق|كومنت|قولي|قول لي)\b",
    "save": r"\b(save|احفظ|سيف)\b", "share": r"\b(share|شير|شارك|ابعت|ابعته)\b",
    "dm": r"\b(dm|رسالة|رسايل|راسلني|ابعتلي|انبوكس|اتواصل)\b", "link": r"(link in bio|لينك|الرابط|رابط)",
    "question": r"[?؟]", "phone_in_text": r"(\+?\d[\d ]{8,}\d)",
}
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆✅]")
HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 6) if xs else None


def parse_ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def bucket(v, edges, labels):
    for e, lab in zip(edges, labels):
        if v < e:
            return lab
    return labels[-1]


def hook_of(text, n=70):
    return (text or "").strip().split("\n")[0].strip()[:n]


def group_perf(posts, keyfn, min_n=1):
    g = {}
    for p in posts:
        k = keyfn(p)
        if k is not None and p.get("index") is not None:
            g.setdefault(k, []).append(p["index"])
    return {k: {"n": len(v), "median_index": med(v)} for k, v in g.items() if len(v) >= min_n}


def enrich(posts, followers, now, tz):
    for p in posts:
        p["format"] = "video" if p.get("is_video") else "photo_or_text"
        ts = parse_ts(p.get("time"))
        p["_dt"] = ts
        p["age_hours"] = round((now - ts).total_seconds() / 3600, 1) if ts else None
        local = ts.astimezone(tz) if (ts and tz) else ts
        p["weekday"] = WEEKDAYS[local.weekday()] if local else None
        p["hour"] = local.hour if local else None
        likes, comments, shares = p.get("likes"), p.get("comments"), p.get("shares")
        parts = [x for x in (likes, comments, shares) if x is not None]
        p["interactions"] = sum(parts) if parts else None
        p["er"] = round(p["interactions"] / followers, 5) if (followers and p["interactions"] is not None) else None
        p["immature"] = p["age_hours"] is not None and p["age_hours"] < IMMATURE_HOURS
        text = p.get("text") or ""
        p["value"] = p["views"] if (p["format"] == "video" and p.get("views") is not None) else p["interactions"]
        p["caption_len"] = len(text)
        p["hashtags"] = HASHTAG_RE.findall(text)
        p["hashtag_n"] = len(p["hashtags"])
        p["emoji_n"] = len(EMOJI_RE.findall(text))
        p["hook"] = hook_of(text)
        p["ctas"] = [k for k, rx in CTA_PATTERNS.items() if re.search(rx, text, re.I)]
    return posts


def assign_index(posts):
    base = {}
    for p in posts:
        if p["value"] is not None and not p["immature"]:
            base.setdefault(p["format"], []).append(p["value"])
    medians = {f: st.median(v) for f, v in base.items() if len(v) >= 3 and st.median(v) >= 10}
    for p in posts:
        m = medians.get(p["format"])
        p["index"] = round(p["value"] / m, 3) if (m and p["value"] is not None and not p["immature"]) else None
        p["verdict"] = ("win" if p["index"] >= WIN else "lose" if p["index"] <= LOSE else "normal") \
            if p["index"] is not None else None
    return medians


def slim(p):
    keep = ("url", "format", "time", "weekday", "hour", "hook", "caption_len", "hashtag_n",
            "likes", "comments", "shares", "views", "er", "index", "verdict", "ctas")
    return {k: p.get(k) for k in keep}


def timing(posts):
    """Best posting day/time from past post performance (same method as analyze.py)."""
    ok = [p for p in posts if p["index"] is not None and p["hour"] is not None]
    by_day = group_perf(ok, lambda p: p["weekday"])
    block = lambda p: f"{(p['hour']//3)*3:02d}-{(p['hour']//3)*3+2:02d}h"
    by_block = group_perf(ok, block)
    best = lambda d, k=2: sorted(((a, b) for a, b in d.items() if b["n"] >= k),
                                 key=lambda x: -x[1]["median_index"])
    win_hours = Counter(block(p) for p in ok if p["verdict"] == "win")
    return {
        "by_weekday": {d: by_day[d] for d in WEEKDAYS if d in by_day},
        "by_hour_block": dict(sorted(by_block.items())),
        "best_weekdays": [{"day": a, **b} for a, b in best(by_day)[:3]],
        "best_hour_blocks": [{"block": a, **b} for a, b in best(by_block)[:3]],
        "winners_posted_in": dict(win_hours.most_common()),
        "confidence": "low" if len(ok) < 25 else "medium" if len(ok) < 60 else "decent",
        "sample_size": len(ok),
        "caveat": "Inferred from past post performance, NOT audience-activity data. "
                  "The doctor's Insights screenshot (active times) overrides this when available.",
    }


def cadence(posts):
    ts = sorted(p["_dt"] for p in posts if p["_dt"])
    if len(ts) < 3:
        return {"note": "too few posts"}
    gaps = [(b - a).total_seconds() / 86400 for a, b in zip(ts, ts[1:])]
    span = max((ts[-1] - ts[0]).days, 1)
    per_week = round(len(ts) / span * 7, 2)
    return {"posts": len(ts), "span_days": span, "posts_per_week": per_week,
            "median_gap_days": round(st.median(gaps), 2), "longest_gap_days": round(max(gaps), 1),
            "gap_stdev_days": round(st.pstdev(gaps), 2),
            "consistency": ("rare" if per_week < 0.5 else
                            "regular" if (st.median(gaps) <= 7 and st.pstdev(gaps) <= st.median(gaps) + 0.5)
                            else "irregular")}


def trend(posts):
    ok = sorted([p for p in posts if p["er"] is not None and not p["immature"]], key=lambda p: p["time"] or "")
    if len(ok) < 10:
        return {"note": "need >=10 mature posts"}
    h = len(ok) // 2
    old, new = med([p["er"] for p in ok[:h]]), med([p["er"] for p in ok[h:]])
    chg = round((new - old) / old * 100, 1) if old else None
    return {"older_half_median_er": old, "newer_half_median_er": new, "change_pct": chg,
            "direction": None if chg is None else "up" if chg > 10 else "down" if chg < -10 else "flat"}


def content_patterns(posts):
    ok = [p for p in posts if p["index"] is not None]
    out = {"format": {}}
    for f in sorted({p["format"] for p in posts}):
        fp = [p for p in posts if p["format"] == f]
        out["format"][f] = {"n": len(fp), "share_pct": round(100 * len(fp) / len(posts), 1),
                            "median_likes": med([p["likes"] for p in fp]), "median_comments": med([p["comments"] for p in fp]),
                            "median_shares": med([p["shares"] for p in fp]), "median_views": med([p["views"] for p in fp]),
                            "median_er": med([p["er"] for p in fp])}
    out["caption_length"] = group_perf(ok, lambda p: bucket(p["caption_len"], [100, 300], ["short<100", "mid100-300", "long>300"]))
    out["has_cta"] = group_perf(ok, lambda p: "with_cta" if p["ctas"] else "no_cta")
    out["cta_types"] = dict(Counter(c for p in posts for c in p["ctas"]).most_common())
    out["has_question"] = group_perf(ok, lambda p: "question" if "question" in p["ctas"] else "none")
    out["hashtag_use"] = group_perf(ok, lambda p: "with_hashtags" if p["hashtag_n"] else "none")
    out["emoji_use"] = group_perf(ok, lambda p: "emoji" if p["emoji_n"] else "no_emoji")
    out["top_hashtags"] = [{"tag": t, "n": n} for t, n in Counter(
        h.lower() for p in posts for h in p["hashtags"]).most_common(15)]
    return out


def page_signals(page):
    return {"title": page.get("title"), "intro": page.get("intro"), "address": page.get("address"),
            "phone": page.get("phone"), "email": page.get("email"), "rating": page.get("rating"),
            "rating_count": page.get("ratingCount"), "followers": page.get("followers"),
            "ad_status": page.get("ad_status"), "has_phone": bool(page.get("phone")),
            "has_address": bool(page.get("address")), "has_intro": bool(page.get("intro")),
            "note": "Mechanical checks only; judge clarity and booking path by reading intro/address."}


def detect_stage(page, posts, now):
    f = page.get("followers") or 0
    recent = sum(1 for p in posts if p["_dt"] and (now - p["_dt"]).days <= 90)
    reasons = []
    if f < 1000:
        reasons.append(f"{f} followers (< 1,000)")
    if recent < 6:
        reasons.append(f"{recent} posts in the last 90 days (< 6)")
    code = "zero" if (f < 1000 or len(posts) < 15) else "early" if (f < 10000 or recent < 12) else "working"
    return {"code": code, "followers": f, "posts_last_90d": recent, "reasons": reasons}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facebook", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tz", default="Africa/Cairo")
    a = ap.parse_args()
    raw = json.load(open(a.facebook, encoding="utf-8"))
    page, posts = raw["page"], raw["posts"]
    followers = page.get("followers")
    now = parse_ts(raw["fetched_at"]) or dt.datetime.now(dt.timezone.utc)
    tz = ZoneInfo(a.tz) if ZoneInfo else None

    enrich(posts, followers, now, tz)
    medians = assign_index(posts)
    mature = [p for p in posts if p["index"] is not None]
    ranked = sorted(mature, key=lambda p: -p["index"])

    result = {
        "meta": {"url": raw.get("url"), "fetched_at": raw["fetched_at"], "timezone": a.tz,
                 "posts_analysed": len(posts), "mature_posts_scored": len(mature),
                 "apify_cost_usd": raw.get("cost_usd"), "win_threshold": WIN, "lose_threshold": LOSE},
        "page": {"followers": followers, "title": page.get("title")},
        "stage": detect_stage(page, posts, now),
        "page_signals": page_signals(page),
        "cadence": cadence(posts),
        "trend": trend(posts),
        "timing": timing(posts),
        "patterns": content_patterns(posts),
        "winners": [slim(p) for p in ranked if p["verdict"] == "win"][:10],
        "losers": [slim(p) for p in reversed(ranked) if p["verdict"] == "lose"][:10],
        "format_medians": {k: round(v) for k, v in medians.items()},
        "posts": [slim(p) for p in sorted(posts, key=lambda p: p["time"] or "")],
    }
    acc_er = med([p["er"] for p in posts if p["er"] is not None and not p["immature"]])
    result["health"] = {"median_er": acc_er}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"facebook analysis -> {a.out} | scored {len(mature)}/{len(posts)} | "
          f"wins {len(result['winners'])} losses {len(result['losers'])} | median ER {acc_er}")


if __name__ == "__main__":
    main()
