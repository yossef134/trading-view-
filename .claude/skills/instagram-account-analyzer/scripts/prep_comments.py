#!/usr/bin/env python3
"""Sort anonymised audience comments into questions, objections and requests (stdlib only).

usage: prep_comments.py --comments comments.json --out audience_signals.json

This does NOT decide what the audience wants. It removes noise (praise, emoji, duplicates)
and tags what is left so Claude can read the questions and objections, cluster them by theme,
and turn them into video ideas. The rules are keyword-based (Arabic + English) and will miss
some and over-catch others, so read the `other` bucket's top items too.

  question    asks something (? / ؟ or a question word)
  objection   pushes back (too expensive, does not work, scam, I disagree, not realistic)
  request     asks for a resource ("send the sheet", "link please") - a lead-magnet signal
  praise      thanks / compliments only, dropped from the ranked lists
  other       everything else
Identical comments are merged and counted (duplicates are the signal for requests).
"""
import argparse
import json
import re
from collections import Counter, defaultdict

Q = re.compile(r"[?؟]|^(ازاي|إزاي|كيف|كام|كم|ليه|ليش|لماذا|هل|فين|امتى|متى|مين|ايه|إيه|بكام|ينفع|يعني|what|why|how|when|where|can |do )", re.I)
OBJ = re.compile(r"(غالي|مبالغ|مش بيجيب|مش شغال|مش واقعي|مستحيل|نصب|فاضي|كلام نظري|ماينفعش|ما ينفعش|مش هينفع|مش معقول|"
                 r"بس انا|بس أنا|لكن|عكس|مش متفق|too expensive|doesn't work|scam|not realistic|disagree|but )", re.I)
REQ = re.compile(r"(شيت|sheet|لينك|رابط|link|ابعت|ارسل|ممكن (ال)?(ملف|نسخة|قالب|كورس)|plz|please|pdf|template|قالب|نسخة)", re.I)
PRAISE = re.compile(r"^(ما شاء الله|ماشاء الله|بالتوفيق|شكرا|شكراً|جزاك|تسلم|رائع|ممتاز|حلو|مجهود|بارك|الله يعطيك|great|thanks|thank you|nice|amazing|love)", re.I)
EMOJI_ONLY = re.compile(r"^[\W\d_]+$")


def norm(t):
    t = re.sub(r"[ًٌٍَُِّْـ]", "", t)  # diacritics and tatweel
    t = re.sub(r"[أإآ]", "ا", t)
    t = re.sub(r"\s+", " ", t.lower()).strip(" .!؟?،,")
    return t


def kind(t):
    if EMOJI_ONLY.match(t):
        return "praise"
    if REQ.search(t) and not Q.search(t.replace("ممكن", "")):
        return "request"
    if OBJ.search(t) and len(t) > 25:
        return "objection"
    if Q.search(t) and len(t) > 8:
        return "question"
    if REQ.search(t):
        return "request"
    if PRAISE.search(t) and len(t) < 60:
        return "praise"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comments", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = json.load(open(a.comments, encoding="utf-8"))
    groups = {}
    for c in data["comments"]:
        key = (c["post"], norm(c["text"]))
        g = groups.setdefault(key, {"text": c["text"], "post": c["post"], "owner": c["owner"], "count": 0, "likes": 0})
        g["count"] += 1
        g["likes"] += c.get("likes") or 0
    buckets = defaultdict(list)
    for g in groups.values():
        g["kind"] = kind(g["text"])
        g["url"] = f"https://www.instagram.com/p/{g['post']}/"
        buckets[g["kind"]].append(g)
    for k in buckets:
        buckets[k].sort(key=lambda g: (-g["count"], -g["likes"], -len(g["text"])))
    by_owner = Counter(c["owner"] for c in data["comments"])
    out = {"meta": {"comments": len(data["comments"]), "unique": len(groups), "by_account": dict(by_owner),
                    "by_kind": {k: sum(g["count"] for g in v) for k, v in buckets.items()},
                    "note": "keyword rules; Claude must read and cluster. praise is excluded from the lists."},
           "questions": buckets["question"], "objections": buckets["objection"], "requests": buckets["request"],
           "other": buckets["other"][:60]}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"signals -> {a.out} | {out['meta']['by_kind']}")


if __name__ == "__main__":
    main()
