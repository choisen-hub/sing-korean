#!/usr/bin/env python3
"""Emit <id>.raw.json per song: metadata + resolved YouTube id + empty lines[].

The `lines` array is deliberately left empty. Song lyrics are copyrighted
works; they are not scraped here. Fill them from a licensed lyrics API
(see FETCH.md) by writing into the `lines` key of each file -- the schema and
every other field are already final, so the app can be built against these
files today.
"""
import json
import pathlib

WORK = pathlib.Path(__file__).resolve().parent
SONGS = json.loads((WORK / "songs.json").read_text())
YT = json.loads((WORK / "yt_ids.json").read_text())

# Manual corrections where ytsearch picked a non-official or wrong upload.
OVERRIDES = {
    # BANGTANTV official audio; ytsearch1 had landed on an MBC TV performance.
    "b34": {"yt": "AEm5O3VnKi8", "yt_title": "Go Go", "yt_channel": "BANGTANTV",
            "confident": True,
            "note": "No official MV exists; BANGTANTV official audio used. "
                    "XqYdxi16K7U is a duplicate re-upload (same 236s)."},
    # No official MV or BANGTANTV upload found; all hits were fan channels.
    "b30": {"yt": None, "yt_title": None, "yt_channel": None, "confident": False,
            "note": "No official HYBE/BANGTANTV video found for 00:00 "
                    "(Zero O'Clock) -- album track, never got an MV."},
}

NOTES = {
    "b08": "BANGTANTV official audio (no MV).",
    "b10": "Official 'Theme of LOVE YOURSELF 起 Wonder' film, not a single MV.",
    "b11": "Official comeback trailer (serves as the song's official video).",
    "b12": "Official comeback trailer.",
    "b13": "Official comeback trailer.",
    "b17": "Original ver. MV (an 'Explicit ver.' also exists).",
    "b19": "Steve Aoki Remix MV -- the only official MV for MIC Drop.",
    "b26": "Steve Aoki remix official audio (no MV for the album version).",
}

LYRICS_STATUS = (
    "not_fetched: song lyrics are copyrighted. Bugs/Melon/Genius all prohibit "
    "scraping in their terms of service, so no lyric text was extracted. "
    "Populate from a licensed lyrics API -- see FETCH.md."
)

count = 0
for song in SONGS:
    sid = song["id"]
    yt = OVERRIDES.get(sid) or YT.get(sid) or {}
    note = yt.get("note") or NOTES.get(sid)
    doc = {
        "id": sid,
        "title_ko": song["title_ko"],
        "title_en": song["title_en"],
        "album": song["album"],
        "year": song["year"],
        "source": None,
        "yt": yt.get("yt"),
        "yt_title": yt.get("yt_title"),
        "yt_channel": yt.get("yt_channel"),
        "lines": [],
        "lyrics_status": LYRICS_STATUS,
    }
    if note:
        doc["yt_note"] = note
    path = WORK / f"{sid}.raw.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    count += 1

print(f"wrote {count} files")
