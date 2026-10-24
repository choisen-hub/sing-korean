# kpop-korean: lyrics acquisition

Status as of 2026-10-24.

## What is done

- `songs.json` — the 35-song master list (id, Korean title, English title, album, year, YouTube search string). Add rows here to extend the set.
- `fetch_yt.py` — resolves the official HYBE LABELS / BANGTANTV video id for each song. Idempotent: re-running only fills in songs missing from `yt_ids.json`. `--force` redoes everything.
- `yt_ids.json` — raw resolver output, kept so you can see the matched video title and channel, not just the id.
- `build_raw.py` — writes `b01.raw.json` … `b35.raw.json` with final metadata, the resolved video id, and `"lines": []`.
- 35 `*.raw.json` files, schema-final.

## What is NOT done, and why

**`lines` is empty in all 35 files. No lyric text was fetched.**

Song lyrics are copyrighted works, and copying a song's complete lyrics into a
file is reproducing the whole work — not a quotation or a snippet. That holds
whichever site the text is copied from. Concretely, for the four sources that
were suggested:

| Source | Why not |
| --- | --- |
| Bugs (`music.bugs.co.kr`) | Lyrics are licensed to Bugs by the rights holders (KOMCA et al.). Bugs' terms prohibit automated collection and redistribution. |
| Melon (`www.melon.com`) | Same — licensed text, terms prohibit crawling. Melon also serves lyrics behind a `Referer` check specifically to deter off-site use. |
| Genius | Genius does not own the lyrics it hosts; it sub-licenses them (Musixmatch/LyricFind deals). Its terms forbid scraping, and its public API deliberately does *not* return lyric text. |
| NetEase | BTS catalogue is delisted; lyric fields come back empty regardless. |

So the scraper that was requested is not something I built. Technical
reachability was not the blocker — permission is.

## The licensed path (this is the part to action)

These give you the same Korean originals, legally, with per-line text:

1. **Musixmatch Developer API** — <https://developer.musixmatch.com/>
   Has BTS with Korean originals. Free tier returns a 30% excerpt only; the
   full-lyrics right needs a commercial plan. `track.lyrics.get` and
   `track.subtitle.get` (the latter is time-synced, which is what you actually
   want for a line-by-line learning UI — it gives you timestamps for free).
2. **LyricFind** — <https://www.lyricfind.com/> — the licensor most Korean and
   global services sit on. Contact sales; they do line-level and synced
   delivery. This is the one to use if the app is going anywhere public.
3. **KOMCA** (한국음악저작권협회, <https://www.komca.or.kr/>) — the Korean
   collecting society. Relevant if you need Korean-territory clearance
   specifically.
4. **Hackathon-scale alternative:** ship the app with 3–5 songs whose lyrics
   you enter by hand from a copy you own, flagged as fair-use excerpts for
   demo, and keep the loader reading the same `*.raw.json` schema. Nothing in
   the app code has to change — swap the data source later.

### Wiring a licensed source in

Everything downstream is ready. A fetcher only has to fill `lines` and `source`:

```python
import json, pathlib
p = pathlib.Path("b01.raw.json")
doc = json.loads(p.read_text())
doc["lines"] = [...]            # one entry per line; "" for a verse break
doc["source"] = "musixmatch:track/12345678"
doc.pop("lyrics_status", None)
p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
```

Conventions the app should assume for `lines`, once populated:

- one array entry per lyric line, in published order;
- `""` preserves a verse break;
- no section headers (`[Chorus]`), no credits, no HTML entities;
- English lines in the original stay English — BTS lyrics code-switch, and that
  mixing is pedagogically useful, so never normalise it away;
- never reconstruct a line from memory or from a translation. An empty `lines`
  is a correct state; an invented line is a silent data defect.

## The YouTube resolver (working recipe)

This part needed no licensing and works today. `yt-dlp` 2026.10.21, no 403s —
no `brew upgrade` was necessary.

```
yt-dlp --no-playlist --flat-playlist --no-warnings \
       --print "%(id)s\t%(title)s\t%(channel)s" \
       "ytsearch5:BTS Spring Day Official MV"
```

Notes learned while doing it:

- Search **5** results, not 1, and then prefer a row whose channel matches
  `HYBE LABELS | BANGTANTV | ibighit | Big Hit`. `ytsearch1` picked a TV
  performance for 고민보다 Go and a TinyTAN cartoon for 00:00.
- Album tracks with no MV live on **BANGTANTV** as bare-titled official audio
  (`Magic Shop`, `Friends`, `병`, `뱁새`). Searching the English title plus
  "Official MV" misses these; search the plain title.
- The Love Yourself solo tracks are **comeback trailers**, not MVs
  (Serendipity, Singularity, Epiphany), and Euphoria is a short film. Those
  are the canonical official videos; they are what the app should embed.
- MIC Drop's only official MV is the Steve Aoki Remix.
- I NEED U has both an "Original ver." and an "Explicit ver." — `b17` uses the
  original.
- BANGTANTV sometimes has duplicate uploads (Go Go: `AEm5O3VnKi8` 2018-05-02
  and `XqYdxi16K7U` 2018-08-24, both 236s). Dedupe by duration.
- 6 parallel workers is fine; no rate limiting hit across 35 queries.

A desktop User-Agent was not needed for `yt-dlp`. If you add any HTTP fetching
later, use:
`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36`

## Table

`lines` is 0 for every song, for the licensing reason above. `source` is unset
pending a licensed provider.

| id | title | source used | lines | yt | problem |
| --- | --- | --- | --- | --- | --- |
| b01 | 봄날 / Spring Day | — | 0 | `xEeFrLSkMm8` | lyrics pending licence |
| b02 | DNA | — | 0 | `MBdVXkSdhwU` | lyrics pending licence |
| b03 | FAKE LOVE | — | 0 | `7C2z4GqqS5E` | lyrics pending licence |
| b04 | 피 땀 눈물 / Blood Sweat & Tears | — | 0 | `hmE9f-TEutc` | lyrics pending licence |
| b05 | IDOL | — | 0 | `pBuZEGYXA6E` | lyrics pending licence |
| b06 | 작은 것들을 위한 시 / Boy With Luv | — | 0 | `XsX3ATc3FbA` | lyrics pending licence |
| b07 | ON | — | 0 | `mPVDGOVjRQ0` | lyrics pending licence |
| b08 | Blue & Grey | — | 0 | `amnspvOH-EE` | BANGTANTV audio, no MV |
| b09 | Life Goes On | — | 0 | `-5q5mZbe3V8` | lyrics pending licence |
| b10 | Euphoria | — | 0 | `kX0vO4vlJuU` | official short film, not an MV |
| b11 | Serendipity | — | 0 | `BEMaH9Sm3lQ` | comeback trailer |
| b12 | Singularity | — | 0 | `p8npDG2ulKQ` | comeback trailer |
| b13 | Epiphany | — | 0 | `fIkZOLsnoqY` | comeback trailer |
| b14 | Save ME | — | 0 | `GZjt_sA2eso` | lyrics pending licence |
| b15 | 불타오르네 / FIRE | — | 0 | `4ujQOR2DMFM` | lyrics pending licence |
| b16 | RUN | — | 0 | `wKysONrSmew` | lyrics pending licence |
| b17 | I NEED U | — | 0 | `jjskoRh8GTE` | original ver. chosen over explicit ver. |
| b18 | 쩔어 / Dope | — | 0 | `H8lYMWZD5P8` | lyrics pending licence |
| b19 | MIC Drop | — | 0 | `kTlv5_Bs8aw` | Aoki remix is the only official MV |
| b20 | 상남자 / Boy In Luv | — | 0 | `LHHjp3IMjMk` | lyrics pending licence |
| b21 | No More Dream | — | 0 | `rBG5L7UsUxA` | lyrics pending licence |
| b22 | 하루만 / Just One Day | — | 0 | `dzAwJW107nk` | lyrics pending licence |
| b23 | 둘! 셋! / 2! 3! | — | 0 | `E30APZxHh4c` | BANGTANTV audio, no MV |
| b24 | Magic Shop | — | 0 | `38k5zr1e0HI` | BANGTANTV audio, no MV |
| b25 | Answer: Love Myself | — | 0 | `9mwRYgMmSGE` | BANGTANTV audio, no MV |
| b26 | 전하지 못한 진심 / The Truth Untold | — | 0 | `ITc-om9SVr4` | Aoki remix audio |
| b27 | 소우주 / Mikrokosmos | — | 0 | `Fw7C6IsDYgI` | BANGTANTV audio, no MV |
| b28 | Black Swan | — | 0 | `0lapF4DQPKQ` | lyrics pending licence |
| b29 | Dis-ease / 병 | — | 0 | `rSi4UIWbtM0` | BANGTANTV audio, no MV |
| b30 | 00:00 (Zero O'Clock) | — | 0 | **null** | no official video exists; all hits were fan uploads |
| b31 | Friends / 친구 | — | 0 | `h7mZX8INIYI` | BANGTANTV audio, no MV |
| b32 | Jamais Vu | — | 0 | `G3x17KyNJtg` | BANGTANTV audio, no MV |
| b33 | 뱁새 / Silver Spoon | — | 0 | `UsyiBESROnQ` | BANGTANTV audio, no MV |
| b34 | 고민보다 Go / Go Go | — | 0 | `AEm5O3VnKi8` | no MV; BANGTANTV audio, deduped from a re-upload |
| b35 | Yet To Come | — | 0 | `kXpOEzNZ8hQ` | lyrics pending licence |

Video ids: 34 / 35 resolved, all from HYBE LABELS or BANGTANTV. 1 unresolved
(b30). Lyric lines: 0 / 35, pending a licensed source.
