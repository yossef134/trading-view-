#!/usr/bin/env python3
"""Compute the numbers behind an Instagram account audit (stdlib only).

usage: analyze.py --raw raw.json --out analysis.json [--tz Africa/Cairo]
                  [--niche niche_reels.json]

Everything here is descriptive statistics on PUBLIC data. It never invents
reach/saves/shares (Instagram does not expose them publicly). "Best time to post"
is inferred from how past posts performed, and is labelled with its sample size.

Performance model
  value   reel/video -> views (plays); image/carousel -> likes + comments
  index   value / median value of the same format (pinned + immature posts excluded)
  win     index >= 1.5      lose  index <= 0.5      else normal
Using the MEDIAN (not the mean) so one viral outlier does not hide everything else.
"""
import argparse
import datetime as dt
import json
import re
import statistics as st
from collections import Counter, defaultdict

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

WIN, LOSE = 1.5, 0.5
IMMATURE_HOURS = 48  # posts younger than this have not finished collecting engagement
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

CTA_PATTERNS = {
    "follow": r"\b(follow|تابع|اتابع|فولو)\b",
    "comment": r"\b(comment|اكتب|علق|كومنت|قولي|قول لي|رأيك|رايك)\b",
    "save": r"\b(save|احفظ|سيف)\b",
    "share": r"\b(share|شير|شارك|ابعت|ابعته|send this)\b",
    "dm": r"\b(dm|رسالة|رسايل|راسلني|ابعتلي)\b",
    "link": r"(link in bio|لينك|الرابط|رابط)",
    "question": r"[?؟]",
}
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆✅]")
ARABIC_RE = re.compile(r"[؀-ۿ]")
NUM_RE = re.compile(r"\d")

# rough rule-of-thumb bands for (likes+comments)/followers, by follower tier. HEURISTIC ONLY.
ER_BANDS = [  # (tier, max_followers, low, high)
    ("nano (<10k)", 10_000, 0.03, 0.08),
    ("micro (10k-100k)", 100_000, 0.015, 0.04),
    ("mid (100k-500k)", 500_000, 0.008, 0.025),
    ("macro (500k-1M)", 1_000_000, 0.005, 0.018),
    ("mega (1M+)", float("inf"), 0.003, 0.012),
]


# --------------------------------------------------------------------------- helpers
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


def hook_of(caption, n=70):
    first = (caption or "").strip().split("\n")[0].strip()
    return first[:n]


def group_perf(posts, keyfn, min_n=1):
    g = defaultdict(list)
    for p in posts:
        k = keyfn(p)
        if k is not None and p.get("index") is not None:
            g[k].append(p["index"])
    return {k: {"n": len(v), "median_index": med(v)} for k, v in g.items() if len(v) >= min_n}


# --------------------------------------------------------------------------- core
def enrich(posts, followers, now, tz):
    for p in posts:
        ts = parse_ts(p["timestamp"])
        p["_dt"] = ts
        p["age_hours"] = round((now - ts).total_seconds() / 3600, 1) if ts else None
        local = ts.astimezone(tz) if (ts and tz) else ts
        p["weekday"] = WEEKDAYS[local.weekday()] if local else None
        p["hour"] = local.hour if local else None
        likes, comments = p.get("likes"), p.get("comments")
        p["interactions"] = (likes or 0) + (comments or 0) if (likes is not None or comments is not None) else None
        p["er"] = round(p["interactions"] / followers, 5) if (followers and p["interactions"] is not None) else None
        p["view_rate"] = round(p["views"] / followers, 4) if (followers and p.get("views")) else None
        isvid = p["format"] in ("reel", "video")
        p["value"] = p["views"] if (isvid and p.get("views") is not None) else p["interactions"]
        p["immature"] = p["age_hours"] is not None and p["age_hours"] < IMMATURE_HOURS
        cap = p.get("caption") or ""
        p["caption_len"] = len(cap)
        p["hashtag_n"] = len(p.get("hashtags") or [])
        p["emoji_n"] = len(EMOJI_RE.findall(cap))
        p["hook"] = hook_of(cap)
        p["ctas"] = [k for k, rx in CTA_PATTERNS.items() if re.search(rx, cap, re.I)]
    return posts


def assign_index(posts):
    base = defaultdict(list)
    for p in posts:
        if p["value"] is not None and not p["is_pinned"] and not p["immature"]:
            base[p["format"]].append(p["value"])
    medians = {f: st.median(v) for f, v in base.items() if len(v) >= 3}
    for p in posts:
        m = medians.get(p["format"])
        p["index"] = round(p["value"] / m, 3) if (m and p["value"] is not None
                                                  and not p["is_pinned"] and not p["immature"]) else None
        p["verdict"] = ("win" if p["index"] >= WIN else "lose" if p["index"] <= LOSE else "normal") \
            if p["index"] is not None else None
    return medians


def slim(p):
    keep = ("url", "format", "timestamp", "weekday", "hour", "hook", "caption_len", "hashtag_n",
            "likes", "comments", "views", "duration", "slides", "er", "view_rate", "index",
            "verdict", "ctas", "audio_original", "is_pinned")
    return {k: p.get(k) for k in keep}


def timing(posts):
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
                  "Link Supermetrics for real follower active hours.",
    }


def cadence(posts):
    ts = sorted(p["_dt"] for p in posts if p["_dt"])
    if len(ts) < 3:
        return {"note": "too few posts"}
    gaps = [(b - a).total_seconds() / 86400 for a, b in zip(ts, ts[1:])]
    span = max((ts[-1] - ts[0]).days, 1)
    per_week = round(len(ts) / span * 7, 2)
    return {
        "posts": len(ts), "span_days": span, "posts_per_week": per_week,
        "median_gap_days": round(st.median(gaps), 2), "longest_gap_days": round(max(gaps), 1),
        "gap_stdev_days": round(st.pstdev(gaps), 2),
        "consistency": "regular" if st.pstdev(gaps) <= st.median(gaps) * 1.0 + 0.5 else "irregular",
    }


def trend(posts):
    ok = sorted([p for p in posts if p["er"] is not None and not p["is_pinned"] and not p["immature"]],
                key=lambda p: p["timestamp"])
    if len(ok) < 10:
        return {"note": "need >=10 mature posts"}
    h = len(ok) // 2
    old, new = med([p["er"] for p in ok[:h]]), med([p["er"] for p in ok[h:]])
    chg = round((new - old) / old * 100, 1) if old else None
    return {"older_half_median_er": old, "newer_half_median_er": new, "change_pct": chg,
            "direction": None if chg is None else "up" if chg > 10 else "down" if chg < -10 else "flat"}


def content_patterns(posts):
    ok = [p for p in posts if p["index"] is not None]
    out = {}
    out["format"] = {}
    for f in sorted({p["format"] for p in posts}):
        fp = [p for p in posts if p["format"] == f]
        out["format"][f] = {"n": len(fp), "share_pct": round(100 * len(fp) / len(posts), 1),
                            "median_likes": med([p["likes"] for p in fp]),
                            "median_comments": med([p["comments"] for p in fp]),
                            "median_views": med([p["views"] for p in fp]),
                            "median_er": med([p["er"] for p in fp])}
    out["caption_length"] = group_perf(ok, lambda p: bucket(p["caption_len"], [100, 300], ["short<100", "mid100-300", "long>300"]))
    out["hashtag_count"] = group_perf(ok, lambda p: bucket(p["hashtag_n"], [1, 6, 16], ["none", "1-5", "6-15", "16+"]))
    out["has_cta"] = group_perf(ok, lambda p: "with_cta" if p["ctas"] else "no_cta")
    out["cta_types"] = dict(Counter(c for p in posts for c in p["ctas"]).most_common())
    out["has_question_in_caption"] = group_perf(ok, lambda p: "question" if "question" in p["ctas"] else "none")
    out["hook_has_number"] = group_perf(ok, lambda p: "number" if NUM_RE.search(p["hook"]) else "no_number")
    out["hook_length"] = group_perf(ok, lambda p: bucket(len(p["hook"]), [30, 55], ["short<30", "mid30-55", "long>55"]))
    out["emoji_use"] = group_perf(ok, lambda p: "emoji" if p["emoji_n"] else "no_emoji")
    out["paid_partnership"] = group_perf(ok, lambda p: "paid" if p["paid_partnership"] else "organic")
    reels = [p for p in ok if p["format"] == "reel"]
    out["reel_duration"] = group_perf(reels, lambda p: bucket(p["duration"] or 0, [8, 15, 30, 60],
                                                              ["<8s", "8-15s", "15-30s", "30-60s", "60s+"]))
    out["reel_original_audio"] = group_perf(reels, lambda p: None if p["audio_original"] is None
                                            else "original" if p["audio_original"] else "trending/other")
    out["carousel_slides"] = group_perf([p for p in ok if p["format"] == "carousel"],
                                        lambda p: bucket(p["slides"] or 0, [4, 7, 10], ["2-3", "4-6", "7-9", "10+"]))
    out["top_hashtags"] = [{"tag": t, "n": n} for t, n in Counter(
        h.lower() for p in posts for h in p["hashtags"]).most_common(15)]
    out["language"] = "arabic" if sum(bool(ARABIC_RE.search(p["caption"])) for p in posts) > len(posts) / 2 else "non-arabic/mixed"
    return out


def bio_signals(profile):
    bio = profile.get("biography") or ""
    lines = [l for l in bio.split("\n") if l.strip()]
    ctas = [k for k, rx in CTA_PATTERNS.items() if k not in ("question",) and re.search(rx, bio, re.I)]
    return {
        "length": len(bio), "lines": len(lines),
        "length_ok": 40 <= len(bio) <= 150,
        "has_link": bool(profile.get("external_url")),
        "has_cta": bool(ctas) or ("👇" in bio or "⬇" in bio or "📩" in bio),
        "cta_types": ctas,
        "emoji_count": len(EMOJI_RE.findall(bio)),
        "has_number_proof": bool(NUM_RE.search(bio)),
        "category_set": bool(profile.get("category")),
        "business_account": profile.get("business_account"),
        "highlights": profile.get("highlights"),
        "name_field": profile.get("full_name"),
        "bio_text": bio,
        "note": "Mechanical checks only. Judge clarity, who-it's-for and promise by reading bio_text.",
    }


def niche_summary(niche, account_posts):
    reels = [r for r in niche.get("reels", []) if r.get("views")]
    if not reels:
        return {"note": "no niche reels"}
    views = sorted(r["views"] for r in reels)
    p90 = views[int(len(views) * 0.9) - 1] if len(views) >= 10 else views[-1]
    top = sorted(reels, key=lambda r: -r["views"])[:10]
    mine = [p["views"] for p in account_posts if p["format"] == "reel" and p.get("views")]
    return {
        "n_reels": len(reels), "median_views": med(views), "p90_views": p90,
        "median_duration": med([r["duration"] for r in reels]),
        "top_hashtags": [{"tag": t, "n": n} for t, n in Counter(
            h.lower() for r in reels for h in r["hashtags"]).most_common(15)],
        "your_median_reel_views": med(mine),
        "top_reels": [{"url": r["url"], "owner": r["owner"], "views": r["views"], "likes": r["likes"],
                       "comments": r["comments"], "duration": r["duration"], "hook": hook_of(r["caption"]),
                       "ctas": [k for k, rx in CTA_PATTERNS.items() if re.search(rx, r["caption"], re.I)]}
                      for r in top],
        "caveat": "Hashtag results mix account sizes; absolute views favour big accounts. "
                  "Use for hooks/length/format patterns, not as a target.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tz", default="Africa/Cairo")
    ap.add_argument("--niche")
    a = ap.parse_args()

    raw = json.load(open(a.raw, encoding="utf-8"))
    prof, posts = raw["profile"], raw["posts"]
    followers = prof.get("followers")
    now = parse_ts(raw["fetched_at"]) or dt.datetime.now(dt.timezone.utc)
    tz = ZoneInfo(a.tz) if ZoneInfo else None

    enrich(posts, followers, now, tz)
    medians = assign_index(posts)
    mature = [p for p in posts if p["index"] is not None]
    ranked = sorted(mature, key=lambda p: -p["index"])

    tier = next(t for t in ER_BANDS if (followers or 0) < t[1])
    acct_er = med([p["er"] for p in posts if p["er"] is not None and not p["immature"]])
    ratio = round(followers / prof["following"], 1) if followers and prof.get("following") else None

    result = {
        "meta": {"username": prof["username"], "fetched_at": raw["fetched_at"], "timezone": a.tz,
                 "posts_analysed": len(posts), "mature_posts_scored": len(mature),
                 "apify_cost_usd": raw.get("cost_usd"), "win_threshold": WIN, "lose_threshold": LOSE},
        "profile": {k: prof.get(k) for k in ("username", "full_name", "followers", "following",
                    "posts_count", "verified", "category", "external_url", "profile_pic")},
        "health": {"median_er": acct_er, "tier": tier[0], "benchmark_low": tier[2], "benchmark_high": tier[3],
                   "er_vs_benchmark": None if acct_er is None else
                   "below" if acct_er < tier[2] else "above" if acct_er > tier[3] else "within",
                   "followers_to_following": ratio, "format_medians": {k: round(v) for k, v in medians.items()},
                   "benchmark_note": "Rule-of-thumb bands, not official Instagram figures."},
        "bio": bio_signals(prof),
        "cadence": cadence(posts),
        "trend": trend(posts),
        "timing": timing(posts),
        "patterns": content_patterns(posts),
        "winners": [slim(p) for p in ranked if p["verdict"] == "win"][:10],
        "losers": [slim(p) for p in reversed(ranked) if p["verdict"] == "lose"][:10],
        "top5": [slim(p) for p in ranked[:5]],
        "bottom5": [slim(p) for p in reversed(ranked[-5:])],
        "excluded": {"pinned": sum(p["is_pinned"] for p in posts), "immature": sum(p["immature"] for p in posts)},
        "related_profiles": prof.get("related_profiles", []),
    }
    if a.niche:
        result["niche"] = niche_summary(json.load(open(a.niche, encoding="utf-8")), posts)

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"analysis -> {a.out} | scored {len(mature)}/{len(posts)} posts | "
          f"wins {len(result['winners'])} losses {len(result['losers'])} | median ER {acct_er}")


if __name__ == "__main__":
    main()
