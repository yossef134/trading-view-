#!/usr/bin/env python3
"""Free local transcription of reels (faster-whisper large-v3-turbo, CPU) - replaces the Apify transcript
(about 0.10 USD per reel) when huggingface.co is reachable.

usage: transcribe.py --videos own_reels.json [--vocab "الحقن المجهري، التبويض، ..."] [--model large-v3-turbo]
  Reads `downloaded_video` links (use own_reels.py --cdn --no-transcript, or any {"videos":[...]} file),
  writes `local_transcript` into the same file.

Tested 2026-11-05 on an Egyptian OB/GYN reel (42 s): about 25 s per reel on CPU, quality close to Apify's.
Medical terms can still come out wrong (e.g. التوتر -> التوطر); `--vocab` primes the model with the
specialty's words, and Claude must correct obvious term errors from context when reading.
Needs: pip install faster-whisper; ffmpeg; huggingface.co allowed (first run downloads about 1.6 GB).
"""
import argparse
import json
import os
import subprocess
import tempfile
import urllib.request

import numpy as np
from faster_whisper import WhisperModel


def audio_of(url):
    with tempfile.TemporaryDirectory() as d:
        mp4 = os.path.join(d, "v.mp4")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(mp4, "wb") as f:
            f.write(r.read())
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                             capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True)
    ap.add_argument("--vocab", default="")
    ap.add_argument("--model", default="large-v3-turbo")
    a = ap.parse_args()
    data = json.load(open(a.videos, encoding="utf-8"))
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    for v in data["videos"]:
        if not v.get("downloaded_video"):
            continue
        audio = audio_of(v["downloaded_video"])
        segs, _ = m.transcribe(audio, language="ar", beam_size=5, vad_filter=True,
                               initial_prompt=a.vocab or None)
        txt = " ".join(s.text.strip() for s in segs).strip()
        dur = len(audio) / 16000
        v["local_transcript"] = txt if dur and len(txt.split()) / dur >= 0.5 else None  # no speech -> None
        print(v.get("shortCode"), round(dur), "s |", (txt or "(no speech)")[:90])
    json.dump(data, open(a.videos, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
