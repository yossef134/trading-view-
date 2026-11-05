#!/usr/bin/env python3
"""Check which hosts this environment can reach BEFORE spending on research (stdlib only).

usage: preflight.py [--extra host ...]

Why: the deep-research step needs Reddit, Quora, YouTube, Google and the audience's own forums, and
cover/video downloads need Instagram's CDN. Some sandboxes block them (HTTP 403 on CONNECT). When they are
blocked, research agents only get search-engine snippets and return thin, unverified results, so do not
launch them: report the blocked hosts and ask the user to allow them in the environment's network
settings (Allowed domains). Never route around the block.
"""
import argparse
import socket
import ssl
import sys
import urllib.error
import urllib.request

HOSTS = {
    "research": ["www.reddit.com", "old.reddit.com", "www.quora.com", "www.youtube.com", "www.facebook.com",
                 "www.google.com", "html.duckduckgo.com"],
    "instagram media": ["scontent.cdninstagram.com", "instagram.fbcdn.net"],
    "apify": ["api.apify.com"],
}


def reachable(host):
    try:
        req = urllib.request.Request(f"https://{host}/", headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        urllib.request.urlopen(req, timeout=10, context=ssl.create_default_context())
        return True, "ok"
    except urllib.error.HTTPError as e:  # the host answered, so the network path is open
        return True, f"http {e.code}"
    except (urllib.error.URLError, socket.timeout, OSError) as e:
        return False, str(getattr(e, "reason", e))[:60]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    groups = dict(HOSTS)
    if a.extra:
        groups["extra"] = a.extra
    blocked = []
    for g, hosts in groups.items():
        print(f"[{g}]")
        for h in hosts:
            ok, why = reachable(h)
            print(f"  {'OK     ' if ok else 'BLOCKED'} {h} ({why})")
            if not ok:
                blocked.append(h)
    if blocked:
        print("\nBlocked: " + ", ".join(blocked))
        print("Ask the user to allow these under Allowed domains (environment settings), then rerun.")
        sys.exit(2)
    print("\nAll reachable.")


if __name__ == "__main__":
    main()
