#!/usr/bin/env python3
"""Fetch research sources through Apify when the sandbox blocks Google/Reddit directly (stdlib only).

usage
  research_fetch.py google --queries-file q.txt --out google.json [--country eg] [--pages 1]
  research_fetch.py reddit --url <thread url> [--url ...] [--max-comments 15] --out reddit.json   (preferred)
  research_fetch.py reddit --search "..." --out reddit.json   (noisy, last resort)

Apify is the user's connected data service (the same path used for Instagram), so this is the
sanctioned route when `preflight.py` shows google.com / reddit.com blocked.

Measured prices (2026-11-04): Google SERP about $0.0045 per page; Reddit about $0.004 per post.
Quote the estimate before running.

Privacy: Reddit author names are dropped. Only titles, bodies (trimmed), community, date, url and
counts are kept, because the point is WHAT people ask, not WHO.
Actor schemas verified 2026-11-04: apify/google-search-scraper {queries, maxPagesPerQuery, countryCode},
trudax/reddit-scraper-lite {searches[], sort, maxItems, skipComments, searchPosts}.
"""
import argparse
import datetime as dt
import importlib.util
import json
import os

_spec = importlib.util.spec_from_file_location("fi", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                  "fetch_instagram.py"))
fi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fi)


def cmd_google(a):
    qs = [l.strip() for l in open(a.queries_file, encoding="utf-8") if l.strip() and not l.startswith("#")]
    inp = {"queries": "\n".join(qs), "maxPagesPerQuery": a.pages}
    if a.country:
        inp["countryCode"] = a.country
    items, _ = fi.run_actor("apify~google-search-scraper", inp)
    out = []
    for it in items:
        sq = it.get("searchQuery") or {}
        out.append({"query": sq.get("term"),
                    "organic": [{"title": r.get("title"), "url": r.get("url"), "snippet": r.get("description")}
                                for r in (it.get("organicResults") or [])],
                    "people_also_ask": [{"question": p.get("question"), "answer": (p.get("answer") or "")[:400],
                                         "url": p.get("url")} for p in (it.get("peopleAlsoAsk") or [])],
                    "related": [r.get("title") for r in (it.get("relatedQueries") or [])]})
    return {"queries": qs, "results": out}


def cmd_reddit(a):
    """Two modes. --url (preferred): specific threads found via Google `site:reddit.com`, with their
    comments, which is where people's real objections are. --search: Reddit keyword search; measured
    on 2026-11-04 it was mostly noise (3-4 relevant posts out of 77), so use it only as a last resort."""
    if a.url:
        inp = {"startUrls": [{"url": u} for u in a.url], "skipComments": False, "maxComments": a.max_comments,
               "maxItems": a.max_items, "maxPostCount": len(a.url), "includeNSFW": False}
    elif a.search:
        inp = {"searches": a.search, "searchPosts": True, "searchComments": False, "searchCommunities": False,
               "searchUsers": False, "skipComments": True, "sort": a.sort, "maxItems": a.max_items,
               "maxPostCount": a.max_items, "includeNSFW": False}
    else:
        raise SystemExit("give --url or --search")
    items, _ = fi.run_actor("trudax~reddit-scraper-lite", inp, wait_secs=900)
    posts, comments = [], []
    for it in items:
        if it.get("dataType") == "comment":
            comments.append({"post_url": it.get("postUrl") or it.get("url"), "body": (it.get("body") or "")[:1200],
                             "upvotes": it.get("upVotes"), "created": it.get("createdAt")})
        elif it.get("dataType") in (None, "post"):
            posts.append({"title": it.get("title"), "body": (it.get("body") or "")[:1500],
                          "community": it.get("communityName") or it.get("parsedCommunityName"),
                          "url": it.get("url"), "created": it.get("createdAt"),
                          "comments": it.get("numberOfComments"), "upvotes": it.get("upVotes")})
    return {"searches": a.search, "urls": a.url, "posts": posts, "comments": comments}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("google"); g.add_argument("--queries-file", required=True)
    g.add_argument("--country"); g.add_argument("--pages", type=int, default=1); g.add_argument("--out", required=True)
    r = sub.add_parser("reddit"); r.add_argument("--search", action="append")
    r.add_argument("--url", action="append"); r.add_argument("--max-comments", type=int, default=15)
    r.add_argument("--max-items", type=int, default=80); r.add_argument("--sort", default="relevance")
    r.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = dt.datetime.now(dt.timezone.utc)
    data = cmd_google(a) if a.cmd == "google" else cmd_reddit(a)
    data["fetched_at"] = t0.isoformat(timespec="seconds")
    data["cost_usd"] = fi.spend_since(t0)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    n = len(data.get("results", [])) or len(data.get("posts", [])) + len(data.get("comments", []))
    print(f"{a.cmd}: {n} items -> {a.out} | apify spend (upper bound) ~ {data['cost_usd']} USD")


if __name__ == "__main__":
    main()
