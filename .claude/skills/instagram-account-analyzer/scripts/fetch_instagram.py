#!/usr/bin/env python3
"""Fetch Instagram data through Apify (stdlib only).

Sub-commands
  account   <username> [--limit 60]       profile + recent posts/reels  -> raw.json
  hashtag   <tag> [<tag> ...] [--limit 40] viral reels for a niche       -> niche_reels.json
  profiles  <username> [<username> ...]    lightweight profile cards (competitors)

Auth: reads APIFY_API_TOKEN from the environment when present. In environments
where an Apify proxy injects credentials, no token is needed.

Privacy: the Apify post/reel actors return `latestComments` / `firstComment`
whether or not they are wanted. Only the whitelisted fields below are kept;
comment bodies are dropped in memory and never written to disk. Only the
aggregate comment COUNT is analysed.

Actor input schemas were verified against the live builds on 2026-11-03:
  apify/instagram-profile-scraper  {usernames[]}
  apify/instagram-scraper          {directUrls[], resultsType, resultsLimit, onlyPostsNewerThan}
  apify/instagram-hashtag-scraper  {hashtags[], resultsType, resultsLimit}
Re-check them (GET /v2/acts/<id>/builds/default) if a run fails on validation.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.apify.com/v2"
PROFILE_ACTOR = "apify~instagram-profile-scraper"
SCRAPER_ACTOR = "apify~instagram-scraper"
HASHTAG_ACTOR = "apify~instagram-hashtag-scraper"


# --------------------------------------------------------------------------- HTTP
def _url(path, **params):
    token = os.environ.get("APIFY_API_TOKEN")
    if token:
        params["token"] = token
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{API}{path}" + (f"?{q}" if q else "")


def _req(method, url, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        sys.exit(f"Apify HTTP {e.code} on {method} {url.split('?')[0]}: {detail}")


def run_actor(actor, run_input, wait_secs=420):
    """Start an actor run, poll until done, return (items, usage_usd)."""
    run = _req("POST", _url(f"/acts/{actor}/runs"), run_input)["data"]
    run_id, ds_id = run["id"], run["defaultDatasetId"]
    deadline = time.time() + wait_secs
    status = run["status"]
    while status in ("READY", "RUNNING") and time.time() < deadline:
        time.sleep(4)
        run = _req("GET", _url(f"/actor-runs/{run_id}"))["data"]
        status = run["status"]
    if status != "SUCCEEDED":
        sys.exit(f"Actor {actor} ended with status {status} (run {run_id})")
    items = _req("GET", _url(f"/datasets/{ds_id}/items", clean="true", format="json"), timeout=120)
    return items or [], run.get("usageTotalUsd")


def spend_since(t0):
    """Real Apify spend: sum usage of every run on the account started since t0.

    The hashtag actor reports $0 on its own run and bills child runs, so the
    per-run figure under-reports. Usage is finalised a few seconds after a run
    ends, hence the short wait. If other jobs run on the same account at the same
    time they are counted too, so treat the number as an upper bound.
    """
    time.sleep(8)
    runs = _req("GET", _url("/actor-runs", desc="true", limit=50))["data"]["items"]
    cut = t0 - dt.timedelta(seconds=3)
    total = 0.0
    for r in runs:
        started = dt.datetime.fromisoformat(r["startedAt"].replace("Z", "+00:00"))
        if started >= cut:
            total += r.get("usageTotalUsd") or 0
    return round(total, 4)


# --------------------------------------------------------------------------- normalisation
def _num(v):
    """Instagram uses -1 for hidden likes; treat as missing."""
    if v is None:
        return None
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    return None if v < 0 else v


def norm_post(p):
    """Whitelist projection. Deliberately omits latestComments / firstComment."""
    music = p.get("musicInfo") or {}
    ptype = p.get("type")  # Image | Video | Sidecar
    product = p.get("productType")  # clips (reel) | feed | igtv | carousel_container
    if product == "clips":
        fmt = "reel"
    elif ptype == "Sidecar":
        fmt = "carousel"
    elif ptype == "Video":
        fmt = "video"  # non-reel feed video
    else:
        fmt = "image"
    return {
        "shortCode": p.get("shortCode"),
        "url": p.get("url"),
        "format": fmt,
        "timestamp": p.get("timestamp"),
        "caption": p.get("caption") or "",
        "hashtags": p.get("hashtags") or [],
        "mentions": p.get("mentions") or [],
        "likes": _num(p.get("likesCount")),
        "comments": _num(p.get("commentsCount")),
        "views": _num(p.get("videoPlayCount")) if p.get("videoPlayCount") is not None
                 else _num(p.get("videoViewCount")),
        "duration": p.get("videoDuration"),
        "slides": len(p.get("childPosts") or []) or None,
        "is_pinned": bool(p.get("isPinned")),
        "paid_partnership": bool(p.get("paidPartnership")),
        "comments_disabled": bool(p.get("isCommentsDisabled")),
        "coauthors": len(p.get("coauthorProducers") or []),
        "tagged_users": len(p.get("taggedUsers") or []),
        "audio_original": music.get("uses_original_audio") if isinstance(music, dict) else None,
        "audio_artist": music.get("artist_name") if isinstance(music, dict) else None,
        "audio_title": music.get("song_name") if isinstance(music, dict) else None,
        "thumbnail": p.get("displayUrl"),
        "owner": p.get("ownerUsername"),
    }


def norm_profile(p):
    urls = p.get("externalUrls") or []
    related = [{"username": r.get("username"), "full_name": r.get("full_name"),
                "verified": r.get("is_verified")} for r in (p.get("relatedProfiles") or [])]
    return {
        "username": p.get("username"),
        "full_name": p.get("fullName"),
        "biography": p.get("biography") or "",
        "followers": p.get("followersCount"),
        "following": p.get("followsCount"),
        "posts_count": p.get("postsCount"),
        "verified": p.get("verified"),
        "private": p.get("private"),
        "business_account": p.get("isBusinessAccount"),
        "category": p.get("businessCategoryName"),
        "external_url": p.get("externalUrl"),
        "external_urls": [u.get("externalUrl") or u.get("lynx_url") for u in urls if isinstance(u, dict)],
        "highlights": p.get("highlightReelCount"),
        "igtv_count": p.get("igtvVideoCount"),
        "related_profiles": related,
        "profile_pic": p.get("profilePicUrlHD") or p.get("profilePicUrl"),
    }


# --------------------------------------------------------------------------- commands
def cmd_profiles(usernames):
    items, usd = run_actor(PROFILE_ACTOR, {"usernames": usernames})
    return [norm_profile(i) for i in items if i.get("username")], usd


def cmd_account(username, limit, since):
    username = username.lstrip("@").strip("/").split("/")[-1]
    profiles, usd1 = cmd_profiles([username])
    if not profiles:
        sys.exit(f"No profile returned for @{username} (private, banned or misspelled?)")
    prof = profiles[0]
    if prof.get("private"):
        sys.exit(f"@{username} is private - nothing public to analyse.")
    run_input = {"directUrls": [f"https://www.instagram.com/{username}/"],
                 "resultsType": "posts", "resultsLimit": limit}
    if since:
        run_input["onlyPostsNewerThan"] = since
    items, usd2 = run_actor(SCRAPER_ACTOR, run_input)
    posts = [norm_post(i) for i in items if i.get("shortCode")]
    posts.sort(key=lambda p: p["timestamp"] or "", reverse=True)
    return {
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": {"profile_actor": PROFILE_ACTOR, "posts_actor": SCRAPER_ACTOR,
                   "comment_bodies": "dropped (counts only)"},
        "cost_usd": round((usd1 or 0) + (usd2 or 0), 4),
        "profile": prof,
        "posts": posts,
    }


def cmd_hashtag(tags, limit):
    items, usd = run_actor(HASHTAG_ACTOR, {"hashtags": [t.lstrip("#") for t in tags],
                                           "resultsType": "reels", "resultsLimit": limit})
    reels = []
    for i in items:
        if not i.get("shortCode"):
            continue
        r = norm_post(i)
        r["query_hashtags"] = tags
        reels.append(r)
    return {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "cost_usd": round(usd or 0, 4), "hashtags": tags, "reels": reels}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("account"); a.add_argument("username")
    a.add_argument("--limit", type=int, default=60)
    a.add_argument("--since", help="YYYY-MM-DD or '3 months'")
    a.add_argument("--out", required=True)
    h = sub.add_parser("hashtag"); h.add_argument("tags", nargs="+")
    h.add_argument("--limit", type=int, default=25); h.add_argument("--out", required=True)
    p = sub.add_parser("profiles"); p.add_argument("usernames", nargs="+"); p.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = dt.datetime.now(dt.timezone.utc)

    if args.cmd == "account":
        data = cmd_account(args.username, args.limit, args.since)
        n = len(data["posts"])
    elif args.cmd == "hashtag":
        data = cmd_hashtag(args.tags, args.limit)
        n = len(data["reels"])
    else:
        profs, usd = cmd_profiles([u.lstrip("@") for u in args.usernames])
        data = {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "cost_usd": round(usd or 0, 4), "profiles": profs}
        n = len(profs)

    data["cost_usd"] = max(data.get("cost_usd") or 0, spend_since(t0))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"saved {n} items -> {args.out} | apify spend (upper bound) ~ ${data['cost_usd']}")


if __name__ == "__main__":
    main()
