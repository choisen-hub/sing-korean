# -*- coding: utf-8 -*-
"""Build the app payload from the corpus, the translations, and the glossaries.

Runs on partial input on purpose. Translation agents finish at different times,
so a song with no `.en.json` yet still ships, just without English. That lets
the site go live early and improve as files land, rather than waiting on the
slowest agent.

Outputs, all under app/data/:
  index.json      song list, small, loaded at boot
  song/<id>.json  one song with tokenized lines, loaded on demand
  freq.json       the frequency ranking with curated glosses merged in

Line indices are assigned over non-blank lines only, starting at 0, matching
what the translation spec told the agents. Blank lines survive as {"gap":1}
entries so verse breaks render, and they never consume an index.
"""

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kotoken import tokenize
from romanize import romanize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "corpus")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "app", "data")


def load_json(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def curated_glosses():
    """data/gloss/*.json 를 합쳐 {사전형: {en, note}} 로."""
    out = {}
    for p in sorted(glob.glob(os.path.join(DATA, "gloss", "*.json"))):
        rows = load_json(p, [])
        if not isinstance(rows, list):
            print(f"  ! {os.path.basename(p)} is not a list, skipped")
            continue
        for r in rows:
            w = (r or {}).get("w")
            en = (r or {}).get("en")
            if not w or not en:
                continue
            out[w] = {"en": en, "note": r.get("note") or None}
    return out


def main():
    songs = load_json(os.path.join(ROOT, "work", "songs.json"), [])
    yt = load_json(os.path.join(ROOT, "work", "yt_ids.json"), {})
    gloss = curated_glosses()

    os.makedirs(os.path.join(OUT, "song"), exist_ok=True)
    index = []
    stats = {"songs": 0, "lines": 0, "translated": 0, "vocab": 0, "notes": 0}

    for n, s in enumerate(songs, 1):
        sid = s["id"]
        raw = os.path.join(CORPUS, f"{sid}.txt")
        if not os.path.exists(raw):
            print(f"  ! no corpus for {sid}, skipped")
            continue

        en = load_json(os.path.join(DATA, "ko", f"{sid}.en.json"), {}) or {}
        tr = en.get("lines") or {}
        notes = en.get("notes") or {}
        vocab = en.get("vocab") or []
        hook = en.get("hook") or []

        # 뜻풀이 우선순위: 곡별 어휘 > 손으로 쓴 빈도 상위 글로스 > 역변환 사전.
        # 역변환 사전은 품사를 모르고 섞여 있어서(보다에 than이 붙는다) 팝업에
        # 그대로 내보내면 학습자가 틀린 뜻을 외운다.
        vmap = {w: g["en"] for w, g in gloss.items()}
        for v in vocab:
            if v.get("w") and v.get("en"):
                vmap[v["w"]] = v["en"]

        items, i = [], 0
        with open(raw, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n").strip()
                if not line:
                    if items and not items[-1].get("gap"):
                        items.append({"gap": 1})
                    continue
                e = {
                    "i": i,
                    "ko": line,
                    "r": romanize(line),
                    "tk": tokenize(line, vmap),
                }
                t = tr.get(str(i))
                if t:
                    e["en"] = t
                    stats["translated"] += 1
                items.append(e)
                i += 1
        while items and items[-1].get("gap"):
            items.pop()

        doc = {
            "id": sid,
            "n": n,
            "title_ko": s.get("title_ko"),
            "title_en": s.get("title_en"),
            "album": s.get("album"),
            "year": s.get("year"),
            "yt": (yt.get(sid) or {}).get("yt"),
            "hook": hook,
            "notes": notes,
            "vocab": vocab,
            "items": items,
        }
        with open(os.path.join(OUT, "song", f"{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))

        index.append({
            "id": sid,
            "n": n,
            "title_ko": s.get("title_ko"),
            "title_en": s.get("title_en"),
            "album": s.get("album"),
            "year": s.get("year"),
            "yt": doc["yt"],
            "lines": i,
            "vocabN": len(vocab),
            "done": bool(tr),
            "sum": notes.get("s") or "",
        })
        stats["songs"] += 1
        stats["lines"] += i
        stats["vocab"] += len(vocab)
        stats["notes"] += len(notes.get("k") or [])

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))

    # 빈도표에 손으로 쓴 뜻을 얹는다. 역변환 사전 값은 뒤로 밀린다.
    freq = load_json(os.path.join(DATA, "freq.json"), []) or []
    hit = 0
    for e in freq:
        g = gloss.get(e["w"])
        if g:
            e["en"] = [x.strip() for x in g["en"].split(",")][:3]
            if g.get("note"):
                e["note"] = g["note"]
            e["c"] = 1  # curated
            hit += 1
    with open(os.path.join(OUT, "freq.json"), "w", encoding="utf-8") as f:
        json.dump(freq, f, ensure_ascii=False, separators=(",", ":"))

    total_lines = stats["lines"] or 1
    print(f"songs {stats['songs']}  lines {stats['lines']:,}  "
          f"translated {stats['translated']:,} ({stats['translated']*100//total_lines}%)")
    print(f"vocab entries {stats['vocab']}  culture notes {stats['notes']}")
    print(f"frequency list {len(freq):,} words, {hit} with a hand written gloss")
    nd = [e["id"] for e in index if not e["done"]]
    if nd:
        print(f"awaiting translation: {' '.join(nd)}")
    sz = sum(os.path.getsize(p) for p in glob.glob(os.path.join(OUT, "song", "*.json")))
    print(f"payload: index {os.path.getsize(os.path.join(OUT,'index.json'))/1024:.0f} KB, "
          f"songs {sz/1024/1024:.1f} MB total, {sz/max(stats['songs'],1)/1024:.0f} KB per song")


if __name__ == "__main__":
    main()
