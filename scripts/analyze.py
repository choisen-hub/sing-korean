# -*- coding: utf-8 -*-
"""Corpus frequency analysis: which Korean words BTS actually sings.

Reads corpus/*.txt, runs every line through the morphological analyser, and
ranks dictionary forms by how often they appear. The ranking is the spine of the
app: a learner who works down this list in order is learning the vocabulary of
the songs they already know, in the order that pays off fastest.

Three counts per word, same shape the 告五人 app used:
  n   total occurrences across the corpus
  ns  how many songs it appears in
  in  which songs (ids, capped)

Output: data/freq.json  (full ranking, build input)
        data/curate_todo.json  (top N with no trustworthy gloss yet)
"""

import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ko_lex
from kotoken import content_lemmas, kodict
from romanize import romanize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "corpus")
DATA = os.path.join(ROOT, "data")

# 기능어에 가까워 어휘 목록에 올릴 가치가 없는 것들
SKIP = {
    "것", "거", "수", "줄", "때", "이", "그", "저", "들", "등", "me", "나다",
    "하다", "되다", "있다", "없다", "이다", "아니다",
    # mecab이 가사 조각에서 어미/조사를 명사나 부사로 잘못 붙이는 것들
    "다", "의", "게", "지", "요", "죠", "군", "네요",
}
# 빈도 집계에서 제외할 품사: 감탄사(oh, yeah 류)와 외국어
SKIP_POS = {"IC", "SL", "SH", "SN"}

CURATE_TOP = 400


def main():
    songs = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "work", "songs.json"), encoding="utf-8"))}

    n = Counter()
    in_songs = defaultdict(set)
    pos_of = {}
    lines_total = 0

    for sid in sorted(songs):
        p = os.path.join(CORPUS, f"{sid}.txt")
        if not os.path.exists(p):
            print(f"  missing corpus: {sid}", file=sys.stderr)
            continue
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            lines_total += 1
            for lem, pos in content_lemmas(line):
                if pos in SKIP_POS or lem in SKIP or len(lem) < 1:
                    continue
                key = lem
                n[key] += 1
                in_songs[key].add(sid)
                # 같은 사전형이 여러 품사로 나오면 가장 먼저 본 품사를 쓴다
                pos_of.setdefault(key, pos)

    d = kodict()
    ranked = []
    for rank, (w, cnt) in enumerate(n.most_common(), 1):
        ids = sorted(in_songs[w])
        ranked.append({
            "w": w,
            "r": romanize(w),
            "p": ko_lex.POS_LABEL.get(pos_of[w], "word"),
            "n": cnt,
            "ns": len(ids),
            "in": ids[:8],
            "rank": rank,
            "en": d.get(w) or None,
        })

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "freq.json"), "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, separators=(",", ":"))

    # 역변환 사전은 핵심 어휘에서 신뢰할 수 없다. 상위권은 전부 손으로 쓴다.
    todo = [{"w": e["w"], "r": e["r"], "p": e["p"], "n": e["n"], "ns": e["ns"],
             "dict_guess": e["en"]} for e in ranked[:CURATE_TOP]]
    with open(os.path.join(DATA, "curate_todo.json"), "w", encoding="utf-8") as f:
        json.dump(todo, f, ensure_ascii=False, indent=1)

    covered = sum(1 for e in ranked[:CURATE_TOP] if e["en"])
    print(f"corpus: {lines_total:,} lines, {len(songs)} songs")
    print(f"distinct dictionary forms: {len(ranked):,}")
    print(f"total content tokens: {sum(n.values()):,}")
    print(f"top {CURATE_TOP} needing hand written glosses "
          f"({covered} have a dictionary guess, {CURATE_TOP - covered} have nothing)")
    print()
    print(f"{'rank':>4}  {'word':<10} {'rom':<16} {'pos':<14} {'n':>4} {'songs':>5}  dict guess")
    for e in ranked[:40]:
        g = ", ".join(e["en"]) if e["en"] else "—"
        print(f"{e['rank']:>4}  {e['w']:<10} {e['r']:<16} {e['p']:<14} {e['n']:>4} {e['ns']:>5}  {g}")


if __name__ == "__main__":
    main()
