#!/usr/bin/env python3
"""
fetch_corpus.py — acquire Korean lyric text as *analysis input* for the
kpop-korean frequency study.

Architecture note (read before changing anything):
  - Output lands in corpus/ which is gitignored and never deployed.
  - The published app serves only (a) a short hook excerpt per song,
    (b) derived word-frequency tables, (c) official YouTube embeds.
  - Full text is never served. Keep it that way.

Idempotent: a song that already has corpus/<id>.txt is skipped unless --force.
Usage:
  python3 scripts/fetch_corpus.py                 # fill in what's missing
  python3 scripts/fetch_corpus.py --force         # redo everything
  python3 scripts/fetch_corpus.py --only b01,b07  # subset
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "work", "songs.json")
CORPUS = os.path.join(ROOT, "corpus")
MANIFEST = os.path.join(CORPUS, "MANIFEST.json")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
BASE_HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")
# every song in songs.json is a Korean-language release, so a page with
# (almost) no Hangul is the wrong page — a translation, romanisation or
# a Japanese/English re-recording.
MIN_HANGUL = 40
ALT_VERSION = re.compile(
    r"translation|romanization|romanized|japanese|chinese|-ver\b|-version\b"
    r"|instrumental|acappella|a-cappella|karaoke|live-at|demo\b|skit"
    r"|remix|mashup|extended|edit\b",
    re.I)
# A whole line wrapped in [ ... ] is always structural on these sites:
# "[Chorus: V, Jin, (All)]", '[방탄소년단 "제목" 가사]'. Inner parens and
# quotes are common, so do not forbid them.
SECTION_HEADER = re.compile(r"^\s*\[.{0,120}\]\s*$|^\s*\(.{0,80}\)\s*$")
BOILERPLATE = re.compile(
    r"(you might also like"
    r"|^\d*\s*embed$"
    r"|^see .* live$"
    r"|get tickets as low as"
    r"|^\d+\s*contributors?"
    r"|^translations?$"
    r"|^read more$"
    r"|^lyrics$"
    r"|가사\s*제공"
    r"|^작사"
    r"|^작곡"
    r"|^편곡"
    r")", re.I)

_print_lock = threading.Lock()


def log(*a):
    with _print_lock:
        print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- cleaning
def clean_lines(raw: str) -> list[str]:
    """Normalise fetched lyric text: one line per line, verse breaks kept."""
    txt = html.unescape(raw)
    txt = txt.replace("​", "").replace("\xa0", " ").replace("\r\n", "\n")
    out: list[str] = []
    for line in txt.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if SECTION_HEADER.match(line):
            # [Verse 1: RM] / [Chorus] / (Hook) -> drop
            continue
        if BOILERPLATE.search(line):
            continue
        out.append(line)
    # collapse 3+ blank lines to one, trim edges
    collapsed: list[str] = []
    for line in out:
        if not line and (not collapsed or not collapsed[-1]):
            continue
        collapsed.append(line)
    while collapsed and not collapsed[-1]:
        collapsed.pop()
    while collapsed and not collapsed[0]:
        collapsed.pop(0)
    return collapsed


def node_to_text(node) -> str:
    """Flatten a lyrics container, turning <br> and block divs into newlines."""
    frag = node.decode()
    frag = re.sub(r"<br\s*/?>", "\n", frag, flags=re.I)
    frag = re.sub(r"</(div|p)>", "\n", frag, flags=re.I)
    return BeautifulSoup(frag, "html.parser").get_text()


# ---------------------------------------------------------------- sources
def genius(session: requests.Session, song: dict):
    """Resolve slug via the public multi-search JSON, then scrape the page."""
    queries = [
        f"BTS {song['title_en']}",
        f"방탄소년단 {song['title_ko']}",
        f"BTS {song['title_ko']}",
    ]
    seen: list[tuple[str, str]] = []
    for q in queries:
        url = "https://genius.com/api/search/multi?q=" + urllib.parse.quote(q)
        try:
            r = session.get(url, timeout=20)
            if r.status_code != 200:
                continue
            payload = r.json()
        except Exception:
            continue
        for section in payload.get("response", {}).get("sections", []):
            for hit in section.get("hits", []):
                res = hit.get("result") or {}
                if hit.get("type") != "song" and res.get("_type") != "song":
                    continue
                purl = res.get("url") or ""
                artist = ((res.get("primary_artist") or {}).get("name") or "")
                title = res.get("title") or ""
                if not purl:
                    continue
                low = purl.lower()
                if ALT_VERSION.search(low):
                    continue
                if "bts" not in artist.lower() and "방탄" not in artist:
                    continue
                seen.append((purl, title))
        if seen:
            break

    # rank: prefer a slug that mentions the English title words
    def score(item):
        purl, title = item
        t = song["title_en"].lower()
        s = 0
        if re.sub(r"[^a-z0-9]", "", t) and re.sub(r"[^a-z0-9]", "", t) in \
                re.sub(r"[^a-z0-9]", "", purl.lower()):
            s -= 10
        if title.lower().strip() == song["title_en"].lower().strip():
            s -= 5
        s += len(purl)
        return s

    # fetch the top candidates and keep whichever yields the most Hangul:
    # Genius hosts romanised / Japanese-ver / translation pages under
    # sibling slugs, and those must never win over the Korean original.
    best = None
    for purl, _title in sorted(set(seen), key=score)[:4]:
        try:
            r = session.get(purl, timeout=25)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            boxes = soup.select('div[data-lyrics-container="true"]')
            if not boxes:
                continue
            text = "\n".join(node_to_text(b) for b in boxes)
            lines = clean_lines(text)
            if len(lines) < 8:
                continue
            han = len(HANGUL.findall("\n".join(lines)))
            if han < MIN_HANGUL:
                continue
            if best is None or han > best[0]:
                best = (han, lines, purl)
            if han > 150:            # clearly the Korean original; stop early
                break
        except Exception:
            continue
    if best:
        return best[1], best[2]
    return None, None


def bugs(session: requests.Session, song: dict):
    """music.bugs.co.kr: find a track id from the search page, read <xmp>."""
    for q in (f"{song['title_ko']} 방탄소년단",
              f"{song['title_en']} BTS",
              song["title_ko"]):
        surl = "https://music.bugs.co.kr/search/track?q=" + urllib.parse.quote(q)
        try:
            r = session.get(surl, timeout=20)
            if r.status_code != 200:
                continue
        except Exception:
            continue
        ids: list[str] = []
        # several id carriers appear in bugs markup; try them all, in order
        for pat in (r'track\|(\d+)',
                    r'/track/(\d+)',
                    r'trackId["\':=\s]+(\d+)',
                    r'data-trackid="(\d+)"',
                    r'name="trackId"\s+value="(\d+)"'):
            for m in re.finditer(pat, r.text):
                if m.group(1) not in ids:
                    ids.append(m.group(1))
            if ids:
                break
        for tid in ids[:4]:
            turl = f"https://music.bugs.co.kr/track/{tid}"
            try:
                tr = session.get(turl, timeout=20,
                                 headers={"Referer": surl})
                if tr.status_code != 200:
                    continue
                soup = BeautifulSoup(tr.text, "html.parser")
                # confirm it is the right artist before trusting the lyric
                page = soup.get_text(" ", strip=True)[:4000]
                if "방탄소년단" not in page and "BTS" not in page:
                    continue
                xmp = soup.find("xmp")
                if not xmp:
                    continue
                lines = clean_lines(xmp.get_text())
                if len(lines) >= 8:
                    return lines, turl
            except Exception:
                continue
    return None, None


def melon(session: requests.Session, song: dict):
    """melon: search for a songId, then read div#d_video_summary."""
    for q in (f"{song['title_ko']} 방탄소년단", f"{song['title_en']} BTS"):
        surl = ("https://www.melon.com/search/song/index.htm?q="
                + urllib.parse.quote(q) + "&section=&searchGnbYn=Y&kkoSpl=N")
        try:
            r = session.get(surl, timeout=20,
                            headers={"Referer": "https://www.melon.com/"})
            if r.status_code != 200:
                continue
        except Exception:
            continue
        ids: list[str] = []
        for pat in (r"goSongDetail\('(\d+)'\)",
                    r"songId=(\d+)",
                    r"playSong\('[^']*',\s*(\d+)\)"):
            for m in re.finditer(pat, r.text):
                if m.group(1) not in ids:
                    ids.append(m.group(1))
        for sid in ids[:4]:
            durl = f"https://www.melon.com/song/detail.htm?songId={sid}"
            try:
                dr = session.get(durl, timeout=20,
                                 headers={"Referer": "https://www.melon.com/"})
                if dr.status_code != 200:
                    continue
                soup = BeautifulSoup(dr.text, "html.parser")
                page = soup.get_text(" ", strip=True)[:4000]
                if "방탄소년단" not in page and "BTS" not in page:
                    continue
                box = soup.select_one("div#d_video_summary")
                if not box:
                    continue
                lines = clean_lines(node_to_text(box))
                if len(lines) >= 8:
                    return lines, durl
            except Exception:
                continue
    return None, None


SOURCES = (("genius", genius), ("bugs", bugs), ("melon", melon))


# ---------------------------------------------------------------- driver
def fetch_one(song: dict, force: bool) -> dict:
    path = os.path.join(CORPUS, f"{song['id']}.txt")
    if os.path.exists(path) and not force:
        body = open(path, encoding="utf-8").read()
        lines = body.split("\n")
        return {"id": song["id"], "title_ko": song["title_ko"],
                "source_url": "(cached)", "source": "cache",
                "lines": len([l for l in lines if l.strip()]),
                "chars": len(HANGUL.findall(body)), "ok": True}

    session = requests.Session()
    session.headers.update(BASE_HEADERS)
    tried = []
    for name, fn in SOURCES:
        try:
            lines, url = fn(session, song)
        except Exception as e:  # keep one bad source from killing the song
            tried.append(f"{name}:err({type(e).__name__})")
            continue
        if lines and len(HANGUL.findall("\n".join(lines))) < MIN_HANGUL:
            tried.append(f"{name}:not-korean")
            lines = None
        if lines:
            body = "\n".join(lines) + "\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
            return {"id": song["id"], "title_ko": song["title_ko"],
                    "source_url": url, "source": name,
                    "lines": len([l for l in lines if l.strip()]),
                    "chars": len(HANGUL.findall(body)), "ok": True}
        tried.append(f"{name}:none")
        time.sleep(0.3)
    return {"id": song["id"], "title_ko": song["title_ko"], "ok": False,
            "reason": ", ".join(tried)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    os.makedirs(CORPUS, exist_ok=True)
    songs = json.load(open(SONGS, encoding="utf-8"))
    if args.only:
        keep = {s.strip() for s in args.only.split(",")}
        songs = [s for s in songs if s["id"] in keep]

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, s, args.force): s for s in songs}
        for fu in as_completed(futs):
            res = fu.result()
            results.append(res)
            log(("  ok " if res["ok"] else "FAIL ") + res["id"] + " "
                + res["title_ko"] + " | "
                + (f"{res['source']} {res['lines']}L {res['chars']}ch"
                   if res["ok"] else res["reason"]))

    results.sort(key=lambda r: r["id"])
    ok = [r for r in results if r["ok"]]
    # merge with any pre-existing manifest rows we did not touch this run
    prev = {}
    if os.path.exists(MANIFEST):
        try:
            prev = {r["id"]: r for r in json.load(open(MANIFEST, encoding="utf-8"))}
        except Exception:
            prev = {}
    for r in ok:
        row = {"id": r["id"], "title_ko": r["title_ko"],
               "source_url": r["source_url"], "lines": r["lines"],
               "chars": r["chars"]}
        if row["source_url"] == "(cached)" and r["id"] in prev:
            row["source_url"] = prev[r["id"]].get("source_url", "(cached)")
        prev[r["id"]] = row
    rows = [prev[k] for k in sorted(prev)
            if os.path.exists(os.path.join(CORPUS, f"{k}.txt"))]
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    log("")
    log(f"acquired {len(ok)}/{len(songs)}   "
        f"lines={sum(r['lines'] for r in ok)}  "
        f"hangul={sum(r['chars'] for r in ok)}")
    for r in results:
        if not r["ok"]:
            log(f"  missing {r['id']} {r['title_ko']}: {r['reason']}")


if __name__ == "__main__":
    main()
