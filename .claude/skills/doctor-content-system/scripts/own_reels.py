#!/usr/bin/env python3
"""Pick the doctor's 2 best and 1 weakest reel and fetch their script (transcript) + video copy.

usage: own_reels.py --analysis analysis.json --out own_reels.json [--best 2] [--worst 1] [--no-video]

Best/weakest are judged against the doctor's OWN reel median (`index` in analysis.json).
One Apify run does both: includeTranscript (about 0.10 USD per reel, measured 2026-11-05)
and includeDownloadedVideo (about 0.07 USD per reel). 3 reels = about 0.5 USD. Quote before running.
Output keeps the `videos` shape that media.py sheets reads (owner, shortCode, downloaded_video).
"""
import argparse
import importlib.util
import json
import os

_spec = importlib.util.spec_from_file_location(
    "fi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_instagram.py"))
fi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--best", type=int, default=2)
    ap.add_argument("--worst", type=int, default=1)
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--no-transcript", action="store_true",
                    help="skip the paid Apify transcript (use scripts/transcribe.py locally instead)")
    ap.add_argument("--cdn", action="store_true",
                    help="free video: use Instagram's CDN link instead of the Apify copy (needs *.fbcdn.net / *.cdninstagram.com allowed)")
    a = ap.parse_args()

    an = json.load(open(a.analysis, encoding="utf-8"))
    owner = an["profile"]["username"]
    reels = sorted([p for p in an["posts"] if p["format"] == "reel" and p.get("index") is not None],
                   key=lambda p: -p["index"])
    if not reels:
        raise SystemExit("No scored reels (needs at least 3 mature reels). Nothing to fetch.")
    picks = [("best", r) for r in reels[: a.best]]
    picks += [("weakest", r) for r in reels[::-1][: a.worst] if r not in [p for _, p in picks]]
    inp = {"username": [r["url"] for _, r in picks], "resultsLimit": 1, "includeTranscript": not a.no_transcript}
    if not a.no_video and not a.cdn:
        inp["includeDownloadedVideo"] = True
    t0 = fi.dt.datetime.now(fi.dt.timezone.utc)
    items, _ = fi.run_actor("apify~instagram-reel-scraper", inp, wait_secs=600)
    got = {i.get("shortCode"): i for i in items}
    videos = []
    for role, r in picks:
        code = r["url"].rstrip("/").split("/")[-1]
        it = got.get(code, {})
        tx = (it.get("transcript") or "").strip()
        dur = r.get("duration") or 0
        # Under ~0.5 words per second the reel is music/text only; the "transcript" is noise.
        speech = bool(tx) and dur > 0 and len(tx.split()) / dur >= 0.5
        videos.append({"role": role, "owner": owner, "shortCode": code, "url": r["url"], "views": r.get("views"),
                       "has_speech": speech,
                       "index": r.get("index"), "duration": r.get("duration"), "hook_caption": r.get("hook"),
                       "transcript": tx if speech else None, "raw_transcript": tx,
                       "downloaded_video": it.get("videoUrl") if a.cdn else it.get("downloadedVideo")})
    out = {"fetched_at": t0.isoformat(timespec="seconds"), "cost_usd": fi.spend_since(t0), "videos": videos}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"own reels -> {a.out} | {sum(1 for v in videos if v['transcript'])} transcripts, "
          f"{sum(1 for v in videos if v['downloaded_video'])} videos | spend ~ {out['cost_usd']} USD")


if __name__ == "__main__":
    main()
