#!/usr/bin/env python3
"""Resolve the official HYBE LABELS / BANGTANTV YouTube video id for each song.

Only touches YouTube search metadata (ids, titles, channel names) -- no media
is downloaded and no lyric text is involved.

Usage:  python3 fetch_yt.py            # fill in missing ids
        python3 fetch_yt.py --force    # redo every song
"""
import json
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

WORK = pathlib.Path(__file__).resolve().parent
SONGS = json.loads((WORK / "songs.json").read_text())
OUT = WORK / "yt_ids.json"

OFFICIAL = ("HYBE LABELS", "BANGTANTV", "BTS", "ibighit", "Big Hit")


def probe(song):
    """Return (id, dict) for one song, or (id, None) if nothing confident found."""
    query = f"ytsearch5:{song['search']}"
    cmd = [
        "yt-dlp", "--no-playlist", "--flat-playlist", "--no-warnings",
        "--print", "%(id)s\t%(title)s\t%(channel)s",
        query,
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return song["id"], None
    rows = [l.split("\t") for l in res.stdout.strip().splitlines() if l.count("\t") == 2]
    if not rows:
        return song["id"], None
    # Prefer a result from an official channel; else take the first hit.
    for vid, title, channel in rows:
        if any(o.lower() in (channel or "").lower() for o in OFFICIAL):
            return song["id"], {"yt": vid, "yt_title": title, "yt_channel": channel,
                                "confident": True}
    vid, title, channel = rows[0]
    return song["id"], {"yt": vid, "yt_title": title, "yt_channel": channel,
                        "confident": False}


def main():
    force = "--force" in sys.argv
    have = json.loads(OUT.read_text()) if OUT.exists() and not force else {}
    todo = [s for s in SONGS if s["id"] not in have]
    print(f"resolving {len(todo)} song(s)")
    with ThreadPoolExecutor(max_workers=6) as pool:
        for sid, info in pool.map(probe, todo):
            have[sid] = info
            print(sid, info)
    OUT.write_text(json.dumps(have, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
