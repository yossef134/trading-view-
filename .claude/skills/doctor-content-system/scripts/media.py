#!/usr/bin/env python3
"""Turn reels and covers into contact sheets that can be looked at (needs ffmpeg + Pillow).

usage
  media.py sheets --videos videos.json --out-dir sheets/ [--frames 8]
      Downloads each reel (videos.json -> downloaded_video, or --cdn to use video_url from the
      reels file), grabs frames and writes one JPG per reel: <owner>_<shortCode>.jpg
      (4 columns, time stamp on every frame). The mp4 itself is NOT kept.
  media.py grid --raw raw.json --out grid.jpg [--n 18]
      Contact sheet of the account's own post covers, for the visual-identity check.

Why a sheet: Claude cannot play video, but it can read a sheet of frames. That is how the
FORMAT of a reel (split screen, talking head, text-on-screen, b-roll...) is judged.

Network note: Instagram's CDN (fbcdn.net / cdninstagram.com) is blocked in some sandboxes
(HTTP 403 on CONNECT). The Apify-hosted copy from `fetch_instagram.py videos` is the fallback,
but it costs about $0.07 per video. Allowing the CDN hosts in the environment's network
settings makes both `sheets --cdn` and `grid` free.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw


def _get(url, dest, timeout=90):
    token = os.environ.get("APIFY_API_TOKEN")
    if token and "api.apify.com" in url:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({"token": token})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def _duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def _frame(path, t, dest, width):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                    "-vf", f"scale={width}:-1", dest], check=False)
    return os.path.exists(dest)


def _sheet(images, labels, out, cols=4, pad=4):
    if not images:
        return False
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(images):
        x, y = pad + (i % cols) * (w + pad), pad + (i // cols) * (h + pad)
        sheet.paste(im.resize((w, h)), (x, y))
        if labels:
            d.rectangle([x, y, x + 46, y + 14], fill=(0, 0, 0))
            d.text((x + 3, y + 1), labels[i], fill=(255, 255, 255))
    sheet.save(out, quality=82)
    return True


def cmd_sheets(a):
    data = json.load(open(a.videos, encoding="utf-8"))["videos"]
    os.makedirs(a.out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="reel_")
    made = failed = 0
    for v in data:
        src = v.get("downloaded_video")
        if not src:
            failed += 1
            continue
        mp4 = os.path.join(tmp, "v.mp4")
        try:
            _get(src, mp4)
        except Exception as e:  # noqa: BLE001
            print(f"download failed for {v['shortCode']}: {e}", file=sys.stderr)
            failed += 1
            continue
        dur = _duration(mp4)
        if dur <= 0:
            failed += 1
            continue
        k = a.frames
        times = sorted({min(max(t, 0.1), dur - 0.2) for t in
                        [0.2, 1.0, 2.5, 4.5] + [dur * f for f in (0.3, 0.5, 0.7)] + [dur - 0.5]})[:k]
        imgs, labs = [], []
        for t in times:
            fp = os.path.join(tmp, f"f{t:.2f}.jpg")
            if _frame(mp4, t, fp, a.width):
                imgs.append(Image.open(fp).convert("RGB"))
                labs.append(f"{t:.1f}s")
        out = os.path.join(a.out_dir, f"{v['owner']}_{v['shortCode']}.jpg")
        if _sheet(imgs, labs, out):
            made += 1
        else:
            failed += 1
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"sheets: {made} written to {a.out_dir}, {failed} failed")


def cmd_grid(a):
    posts = json.load(open(a.raw, encoding="utf-8"))["posts"][: a.n]
    tmp = tempfile.mkdtemp(prefix="cover_")
    imgs = []
    blocked = None
    for i, p in enumerate(posts):
        if not p.get("thumbnail"):
            continue
        fp = os.path.join(tmp, f"{i}.jpg")
        try:
            _get(p["thumbnail"], fp, timeout=40)
            im = Image.open(fp).convert("RGB")
            side = min(im.size)
            im = im.crop(((im.width - side) // 2, (im.height - side) // 2, (im.width + side) // 2, (im.height + side) // 2))
            imgs.append(im.resize((200, 200)))
        except Exception as e:  # noqa: BLE001
            blocked = blocked or f"{urllib.parse.urlparse(p['thumbnail']).hostname}: {e}"
    shutil.rmtree(tmp, ignore_errors=True)
    if not imgs:
        sys.exit("No covers downloaded. " + (f"Blocked/failed -> {blocked}. Allow Instagram's CDN hosts "
                                            "(fbcdn.net, cdninstagram.com) in the environment network settings."
                                            if blocked else ""))
    _sheet(imgs, None, a.out, cols=6)
    print(f"grid: {len(imgs)} covers -> {a.out}" + (f" (some failed: {blocked})" if blocked else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheets"); s.add_argument("--videos", required=True); s.add_argument("--out-dir", required=True)
    s.add_argument("--frames", type=int, default=8); s.add_argument("--width", type=int, default=180)
    g = sub.add_parser("grid"); g.add_argument("--raw", required=True); g.add_argument("--out", required=True)
    g.add_argument("--n", type=int, default=18)
    a = ap.parse_args()
    {"sheets": cmd_sheets, "grid": cmd_grid}[a.cmd](a)


if __name__ == "__main__":
    main()
