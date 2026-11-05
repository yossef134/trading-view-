#!/usr/bin/env python3
"""Fetch Instagram data through Apify (stdlib only).

Sub-commands
  account   <username> [--limit 60]        profile + recent posts/reels   -> raw.json
  profiles  <username> [<username> ...]    lightweight profile cards      -> competitors.json
  reels     <username> [<username> ...]    last N reels per account       -> competitor_reels.json
            [--limit 20]
  videos    --reels competitor_reels.json  mp4 links for the top reels per competitor -> videos.json
            [--top 5] [--cdn]              default = Apify-hosted copy, COSTS ~$0.07 PER VIDEO.
                                           --cdn = free, needs fbcdn.net reachable (see "Video")
  comments  --reels competitor_reels.json  public comment TEXT on the top reels, anonymised
            [--top 5] [--limit 60]                                          -> comments.json
  hashtag   <tag> [<tag> ...] [--limit 25] OPTIONAL. Noisy and the most expensive step; prefer
                                           competitors. Kept for niche sanity checks only.

Auth: reads APIFY_API_TOKEN from the environment when present. In environments
where an Apify proxy injects credentials, no token is needed.

Privacy
  * Post/reel actors return `latestComments` / `firstComment` regardless; the whitelist
    in norm_post() drops them, so account/reels files hold comment COUNTS only.
  * `comments` is the one command that keeps comment text, because audience questions
    and objections are the point. It keeps ONLY: text, comment likes, timestamp, post url.
    Author names, ids and avatars are dropped, @mentions, links, e-mails and phone-like
    numbers are masked, and the competitor's own replies are removed.

Video
  Instagram's CDN host (fbcdn.net) is blocked by some sandboxes. `videos` then asks the reel
  actor to store a copy on Apify (includeDownloadedVideo) and downloads it from api.apify.com,
  which is allowed wherever Apify is. MEASURED: that costs about $0.07 per video (24 videos
  = about $1.6), roughly 20x the reel metadata. Always quote the price and get a yes first;
  prefer `--cdn` after the user allows the CDN hosts, and keep --top small (2-3).

Actor input schemas were verified against the live builds on 2026-11-04:
  apify/instagram-profile-scraper  {usernames[]}
  apify/instagram-scraper          {directUrls[], resultsType, resultsLimit, onlyPostsNewerThan}
  apify/instagram-reel-scraper     {username[] (names or reel URLs), resultsLimit, skipPinnedPosts,
                                    includeDownloadedVideo}
  apify/instagram-comment-scraper  {directUrls[], resultsLimit}
  apify/instagram-hashtag-scraper  {hashtags[], resultsType, resultsLimit}
Measured costs: reels about $0.003 each, profile cards $0.0026, comments see `comments`.
Keyword->account discovery through Apify search returns ONE account, so it is not used.
Re-check schemas (GET /v2/acts/<id>/builds/default) if a run fails on validation.
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.apify.com/v2"
PROFILE_ACTOR = "apify~instagram-profile-scraper"
SCRAPER_ACTOR = "apify~instagram-scraper"
HASHTAG_ACTOR = "apify~instagram-hashtag-scraper"
REEL_ACTOR = "apify~instagram-reel-scraper"
COMMENT_ACTOR = "apify~instagram-comment-scraper"


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


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _code(url):
    m = re.search(r"/(?:p|reel|reels|tv)/([\w-]+)", url or "")
    return m.group(1) if m else None


def scrub(text):
    """Mask personal identifiers inside comment text."""
    t = text or ""
    t = re.sub(r"https?://\S+", "[link]", t)
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", t)
    t = re.sub(r"@[\w.]+", "@user", t)
    t = re.sub(r"\+?\d[\d\s\-()]{7,}\d", "[number]", t)
    return t.strip()


def select_top(competitors, k):
    """Top-k reels per competitor by views relative to THAT account's median."""
    chosen = []
    for c in competitors:
        rs = [r for r in c["reels"] if r.get("views")]
        if len(rs) < 3:
            continue
        m = statistics.median(r["views"] for r in rs)
        ranked = sorted(rs, key=lambda r: -r["views"] / m)[:k]
        chosen += [{"owner": c["profile"]["username"], "shortCode": r["shortCode"], "url": r["url"],
                    "views": r["views"], "index": round(r["views"] / m, 2)} for r in ranked]
    return chosen


def cmd_reels(usernames, limit):
    profiles, usd1 = cmd_profiles(usernames)
    ok = [p["username"] for p in profiles if not p.get("private")]
    items, usd2 = run_actor(REEL_ACTOR, {"username": ok, "resultsLimit": limit, "skipPinnedPosts": True})
    by = {}
    for i in items:
        if i.get("shortCode"):
            r = norm_post(i)
            r["video_url"] = i.get("videoUrl")  # short-lived CDN link; only usable where the CDN is reachable
            by.setdefault((i.get("ownerUsername") or "").lower(), []).append(r)
    comps = []
    for p in profiles:
        rs = sorted(by.get((p["username"] or "").lower(), []), key=lambda r: r["timestamp"] or "", reverse=True)
        comps.append({"profile": {k: p.get(k) for k in ("username", "full_name", "biography", "followers",
                      "following", "posts_count", "verified", "private", "category", "external_url")},
                      "reels": rs})
    return {"fetched_at": _now(), "cost_usd": round((usd1 or 0) + (usd2 or 0), 4),
            "per_account_limit": limit, "competitors": comps}


def cmd_videos(reels_file, top, cdn=False):
    data = json.load(open(reels_file, encoding="utf-8"))
    chosen = select_top(data["competitors"], top)
    if cdn:  # free path: link straight to Instagram's CDN (needs fbcdn.net reachable, links expire)
        urls = {r["shortCode"]: r.get("video_url") for c in data["competitors"] for r in c["reels"]}
        for c in chosen:
            c["downloaded_video"] = urls.get(c["shortCode"])
        return {"fetched_at": _now(), "cost_usd": 0.0, "source": "cdn", "videos": chosen}
    items, usd = run_actor(REEL_ACTOR, {"username": [c["url"] for c in chosen], "resultsLimit": 1,
                                        "includeDownloadedVideo": True})
    got = {i.get("shortCode"): i.get("downloadedVideo") for i in items if i.get("shortCode")}
    for c in chosen:
        c["downloaded_video"] = got.get(c["shortCode"])
    return {"fetched_at": _now(), "cost_usd": round(usd or 0, 4), "videos": chosen}


def cmd_comments(reels_file, top, limit):
    data = json.load(open(reels_file, encoding="utf-8"))
    chosen = select_top(data["competitors"], top)
    owner_of = {c["shortCode"]: c["owner"].lower() for c in chosen}
    items, usd = run_actor(COMMENT_ACTOR, {"directUrls": [c["url"] for c in chosen], "resultsLimit": limit})
    out, dropped_owner = [], 0
    for c in items:
        code = _code(c.get("postUrl"))
        if (c.get("ownerUsername") or "").lower() == owner_of.get(code):
            dropped_owner += 1  # the competitor answering their own audience
            continue
        text = scrub(c.get("text"))
        if len(text) < 3:
            continue
        out.append({"post": code, "owner": owner_of.get(code), "text": text,
                    "likes": _num(c.get("likesCount")), "timestamp": c.get("timestamp")})
    return {"fetched_at": _now(), "cost_usd": round(usd or 0, 4),
            "anonymised": "author names/ids/avatars dropped; mentions, links, e-mails, numbers masked",
            "dropped_owner_replies": dropped_owner, "posts": chosen, "comments": out}


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
    r = sub.add_parser("reels"); r.add_argument("usernames", nargs="+")
    r.add_argument("--limit", type=int, default=20); r.add_argument("--out", required=True)
    v = sub.add_parser("videos"); v.add_argument("--reels", required=True)
    v.add_argument("--top", type=int, default=5); v.add_argument("--out", required=True)
    v.add_argument("--cdn", action="store_true", help="free: use CDN links from the reels file (no Apify run)")
    c = sub.add_parser("comments"); c.add_argument("--reels", required=True)
    c.add_argument("--top", type=int, default=5); c.add_argument("--limit", type=int, default=60)
    c.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = dt.datetime.now(dt.timezone.utc)

    if args.cmd == "account":
        data = cmd_account(args.username, args.limit, args.since)
        n = len(data["posts"])
    elif args.cmd == "hashtag":
        data = cmd_hashtag(args.tags, args.limit)
        n = len(data["reels"])
    elif args.cmd == "reels":
        data = cmd_reels([u.lstrip("@") for u in args.usernames], args.limit)
        n = sum(len(x["reels"]) for x in data["competitors"])
    elif args.cmd == "videos":
        data = cmd_videos(args.reels, args.top, args.cdn)
        n = sum(1 for x in data["videos"] if x["downloaded_video"])
    elif args.cmd == "comments":
        data = cmd_comments(args.reels, args.top, args.limit)
        n = len(data["comments"])
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
