#!/usr/bin/env python3
"""Doctor's Facebook page: page info + last N posts, through Apify (facebook.com is blocked directly).

usage: fetch_facebook.py --url https://www.facebook.com/<page> --out facebook.json [--limit 30]

Measured prices (2026-11-05): page info 0.012 USD, posts 0.005 USD each (30 posts about 0.17 USD total).
Use the page's normal URL; /share/ links may not open. Comment texts are not collected.
Schemas verified 2026-11-05: apify/facebook-pages-scraper {startUrls}, apify/facebook-posts-scraper {startUrls, resultsLimit}.
"""
import argparse
import importlib.util
import json
import os

_spec = importlib.util.spec_from_file_location(
    "fi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_instagram.py"))
fi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fi)

PAGE_KEYS = ("title", "pageName", "categories", "info", "likes", "followers", "followings", "email", "phone",
             "website", "websites", "address", "intro", "rating", "ratingOverall", "ratingCount", "pageUrl",
             "creation_date", "ad_status", "messenger")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=30)
    a = ap.parse_args()
    t0 = fi.dt.datetime.now(fi.dt.timezone.utc)
    pages, _ = fi.run_actor("apify~facebook-pages-scraper", {"startUrls": [{"url": a.url}]})
    page = {k: v for k, v in (pages[0] if pages else {}).items() if k in PAGE_KEYS}
    items, _ = fi.run_actor("apify~facebook-posts-scraper", {"startUrls": [{"url": a.url}], "resultsLimit": a.limit},
                            wait_secs=600)
    posts = []
    for p in items:
        if not p.get("postId") and not p.get("url"):
            continue
        posts.append({"url": p.get("url") or p.get("topLevelUrl"), "time": p.get("time"),
                      "text": (p.get("text") or "")[:600], "likes": p.get("likes"),
                      "comments": p.get("comments"), "shares": p.get("shares"),
                      "views": p.get("viewsCount") or p.get("videoViewCount"),
                      "is_video": bool(p.get("isVideo") or p.get("media") and any(
                          (m or {}).get("__typename") == "Video" for m in (p.get("media") or [])))})
    out = {"fetched_at": t0.isoformat(timespec="seconds"), "url": a.url, "page": page, "posts": posts,
           "cost_usd": fi.spend_since(t0)}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"facebook -> {a.out} | page: {bool(page)} | posts: {len(posts)} | spend ~ {out['cost_usd']} USD")


if __name__ == "__main__":
    main()
