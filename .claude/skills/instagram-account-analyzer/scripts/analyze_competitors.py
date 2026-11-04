#!/usr/bin/env python3
"""What won, and what keeps repeating, across a set of competitors (stdlib only).

usage: analyze_competitors.py --reels competitor_reels.json --out competitors_analysis.json
                              [--labels format_labels.json] [--tz Africa/Cairo]

Fairness rule: every reel is judged against the median of ITS OWN account
(index = views / own median), so a 7K-follower account does not drown a 400-follower one.
  winner  index >= 1.5      loser  index <= 0.5      accounts need >= 4 reels with views

Pattern rule: a feature value is called "repeated" only when
  >= 3 winners carry it  AND  winners come from >= 2 different accounts  AND  no single
  account supplies more than 60% of those winners  AND  lift >= 1.3
where lift = share of winners with the value / share of non-winners with the value.
Everything is reported as counts ("5 of 11 winners") with links, never as a bare claim.

Formats are an OPEN vocabulary. Claude watches the contact sheets and writes
format_labels.json: {"<shortCode>": {"format": "...", "topic": "...", "note": "..."}}.
The ten formats in references/content-formats-2026.md are suggested names, not a closed
list; use a new name whenever a reel does not fit. Labels are merged in when present.

Hook types are rule-based on the first caption line (Arabic + English) and are a rough
guide: they say what the words do, not whether the speaker said something else on camera.
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

WIN, LOSE, MIN_REELS = 1.5, 0.5, 4
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

HOOK_RULES = {
    "question": r"[?؟]|^(ازاي|إزاي|كيف|كام|كم|ليه|ليش|لماذا|هل|فين|امتى|متى|مين|من |ايه|إيه|what|why|how|when|do you|are you)",
    "number_or_list": r"[0-9٠-٩]|\b(ثلاث|خمس|سبع|عشر|three|five|seven|ten)\b",
    "direct_address": r"(يا دكتور|يا دكاترة|لو (انت|إنت|أنت|عندك|بتـ|بت)|انت |إنت |أنت |you |if you)",
    "tension_or_contrast": r"(بس |لكن|ومحدش|مش |ما |ليه ما|ليش ما|لا تـ|لا تخلي|but |stop |don't|never)",
    "loss_or_mistake": r"(غلط|خطأ|فخ|تخسر|خسارة|ضيع|ضيّع|بتضيع|مشكلة|mistake|wrong|lose|waste|trap)",
    "story_or_first_person": r"(^أنا|^انا|كنت |حصل|قصة|جربت|story|^i |i was|i tried)",
    "authority_claim": r"(سنة خبرة|سنين|خبرة|حققنا|وصلنا|ساعدت|عميل|clients|years|helped|generated)",
}
CTA_RULES = {
    "comment_keyword": r"(اكتب|علق|علّق|كومنت|comment)",
    "dm": r"(ابعت|ارسل|راسل|رسالة|dm|message me)",
    "follow": r"(تابع|فولو|follow)",
    "save_share": r"(احفظ|شير|شارك|save|share|send this)",
    "link": r"(لينك|الرابط|link in bio|bio)",
}


def parse_ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def bucket(v, edges, labels):
    for e, lab in zip(edges, labels):
        if v < e:
            return lab
    return labels[-1]


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 4) if xs else None


def features(r, tz, label):
    cap = r.get("caption") or ""
    first = cap.strip().split("\n")[0][:90]
    ts = parse_ts(r["timestamp"])
    local = ts.astimezone(tz) if (ts and tz) else ts
    f = {"hook_type": [k for k, rx in HOOK_RULES.items() if re.search(rx, first, re.I)] or ["plain_statement"],
         "cta": [k for k, rx in CTA_RULES.items() if re.search(rx, cap, re.I)] or ["none"],
         "duration": [bucket(r.get("duration") or 0, [15, 30, 45, 60, 90], ["<15s", "15-30s", "30-45s", "45-60s", "60-90s", "90s+"])],
         "caption_length": [bucket(len(cap), [100, 300, 600], ["<100", "100-300", "300-600", "600+"])],
         "hashtags": [bucket(len(r.get("hashtags") or []), [1, 4, 8], ["none", "1-3", "4-7", "8+"])],
         "audio": ["original" if r.get("audio_original") else "trending/other" if r.get("audio_original") is False else "unknown"],
         "weekday": [WEEKDAYS[local.weekday()]] if local else [],
         "hour_block": [f"{(local.hour // 4) * 4:02d}-{(local.hour // 4) * 4 + 3:02d}h"] if local else []}
    if label:
        if label.get("format"):
            f["format"] = [label["format"]]
        if label.get("topic"):
            f["topic"] = [label["topic"]]
    return first, f


def slim(r):
    return {k: r.get(k) for k in ("owner", "url", "views", "likes", "comments", "duration", "index", "view_rate",
                                  "eng_per_view", "hook", "hook_type", "cta", "format", "topic", "verdict", "timestamp")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reels", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--labels")
    ap.add_argument("--tz", default="Africa/Cairo")
    a = ap.parse_args()

    data = json.load(open(a.reels, encoding="utf-8"))
    labels = json.load(open(a.labels, encoding="utf-8")) if a.labels else {}
    tz = ZoneInfo(a.tz) if ZoneInfo else None

    pooled, accounts = [], []
    for c in data["competitors"]:
        p, rs = c["profile"], c["reels"]
        vs = [r["views"] for r in rs if r.get("views")]
        followers = p.get("followers")
        summary = {"username": p["username"], "url": f"https://www.instagram.com/{p['username']}/",
                   "followers": followers, "bio": p.get("biography"), "link": p.get("external_url"),
                   "reels_found": len(rs), "reels_with_views": len(vs), "median_views": med(vs),
                   "median_view_rate": med([v / followers for v in vs]) if followers else None,
                   "span": [rs[-1]["timestamp"][:10], rs[0]["timestamp"][:10]] if rs else None,
                   "scored": len(vs) >= MIN_REELS}
        if len(vs) >= MIN_REELS:
            m = st.median(vs)
            for r in rs:
                if not r.get("views"):
                    continue
                first, f = features(r, tz, labels.get(r["shortCode"]))
                r.update(owner=p["username"], index=round(r["views"] / m, 2),
                         view_rate=round(r["views"] / followers, 3) if followers else None,
                         eng_per_view=round(((r.get("likes") or 0) + (r.get("comments") or 0)) / r["views"], 4),
                         hook=first, hook_type=f["hook_type"], cta=f["cta"],
                         format=(f.get("format") or [None])[0], topic=(f.get("topic") or [None])[0],
                         verdict="win" if r["views"] / m >= WIN else "lose" if r["views"] / m <= LOSE else "normal")
                r["_f"] = f
                pooled.append(r)
            mine = sorted([r for r in rs if r.get("index") is not None], key=lambda r: -r["index"])
            summary["winners"] = [slim(r) for r in mine if r["verdict"] == "win"][:5]
            summary["losers"] = [slim(r) for r in reversed(mine) if r["verdict"] == "lose"][:3]
            summary["best_reel"] = slim(mine[0]) if mine else None
        accounts.append(summary)

    W = [r for r in pooled if r["verdict"] == "win"]
    R = [r for r in pooled if r["verdict"] != "win"]
    base = round(len(W) / len(pooled), 3) if pooled else None

    patterns = defaultdict(list)
    if W and R:
        for feat in ("hook_type", "format", "topic", "cta", "duration", "caption_length", "hashtags", "audio",
                     "weekday", "hour_block"):
            tot, win = Counter(), Counter()
            # labels (format/topic) only exist for the reels whose frames were viewed, usually the top
            # ones. Without labelled non-winners there is no baseline, so report counts, not lift.
            counts_only = feat in ("format", "topic") and sum(1 for r in R if r["_f"].get(feat)) < 3
            owners = defaultdict(set)
            by_owner = defaultdict(Counter)
            for r in pooled:
                for v in r["_f"].get(feat, []):
                    tot[v] += 1
                    if r["verdict"] == "win":
                        win[v] += 1
                        owners[v].add(r["owner"])
                        by_owner[v][r["owner"]] += 1
            for v, n in tot.items():
                nw = win[v]
                sw, sr = nw / len(W), (n - nw) / len(R)
                lift = None if counts_only else (round(sw / sr, 2) if sr > 0 else None)  # None = no baseline / only in winners
                dom = (by_owner[v].most_common(1)[0] if by_owner[v] else (None, 0))
                dominated = nw > 0 and dom[1] / nw > 0.6  # one account supplies most of the winners
                repeated = nw >= 3 and len(owners[v]) >= 2 and not dominated and (lift is None or lift >= 1.3)
                if counts_only:
                    sr = None
                ex = sorted([r for r in W if v in r["_f"].get(feat, [])], key=lambda r: -r["index"])[:5]
                patterns[feat].append({"value": v, "in_winners": nw, "of_winners": len(W), "in_all": n,
                                       "win_rate": None if counts_only else round(nw / n, 2), "lift": lift, "accounts_with_win": len(owners[v]),
                                       "repeated": repeated, "counts_only": counts_only, "dominated_by": dom[0] if dominated else None,
                                       "examples": [r["url"] for r in ex]})
            patterns[feat].sort(key=lambda x: (-x["repeated"], -(x["lift"] or 9), -x["in_winners"]))

    for r in pooled:
        r.pop("_f", None)
    top = lambda key, n=10: [slim(r) for r in sorted([x for x in pooled if x.get(key) is not None],
                                                      key=lambda x: -x[key])[:n]]
    queue = [slim(r) for c in accounts if c.get("winners") for r in c["winners"][:3] if not r.get("format")]

    out = {"meta": {"fetched_at": data.get("fetched_at"), "accounts": len(accounts),
                    "scored_accounts": sum(a["scored"] for a in accounts), "reels_scored": len(pooled),
                    "winners": len(W), "base_win_rate": base, "win_threshold": WIN, "lose_threshold": LOSE,
                    "min_reels_per_account": MIN_REELS, "timezone": a.tz, "labels_applied": len(labels),
                    "note": "index is vs each account's own median; patterns are counts with links, "
                            "'repeated' = >=3 winners, >=2 accounts, no single account supplying >60% of them, lift >= 1.3"},
           "accounts": accounts,
           "patterns": patterns,
           "top_by_index": top("index"), "top_by_view_rate": top("view_rate"), "top_by_views": top("views"),
           "labeling_queue": queue}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    rep = sum(1 for feat in patterns.values() for p in feat if p["repeated"])
    print(f"competitors -> {a.out} | {len(pooled)} reels scored, {len(W)} winners, {rep} repeated patterns")


if __name__ == "__main__":
    main()
