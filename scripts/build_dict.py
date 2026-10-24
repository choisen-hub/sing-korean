# -*- coding: utf-8 -*-
"""Korean -> English dictionary, built by inverting the English -> Korean one.

musical-study already ships `dict.json` with 64k English headwords mapped to
Korean glosses (kengdic). This app needs the other direction, so we invert it:
every Korean gloss becomes a key pointing back at the English headwords that
produced it.

Inversion is lossy in a predictable way. A Korean key can collect English words
that are only loosely related, so entries are ranked to put the likely core
sense first: short, common, single-word English beats long rare phrases. The
curated per-song vocabulary is what carries accuracy; this file is the fallback
for when a learner taps a word nobody wrote a note for.

Output: app/data/kodict.json  { "사랑": ["love", "affection"], ... }
"""

import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.expanduser("~/Desktop/3 언어/영어/musical-study/app/data/dict.json")
OUT = os.path.join(ROOT, "app", "data", "kodict.json")

HANGUL_ONLY = re.compile(r"^[가-힣]+$")
# 영어 쪽에서 버릴 것: 대문자 고유명사, 숫자, 기호
BAD_EN = re.compile(r"[^a-z' -]")
# 한국어 뜻풀이에서 자주 붙는 꼬리말
TRIM = re.compile(r"\s*\([^)]*\)\s*|\s*[~…·]+\s*")

# 흔한 영어 단어를 앞으로 보내기 위한 가산점 목록
COMMON = set("""
love like want need know think feel say tell see look hear listen go come
leave stay run walk stand sit sleep wake eat drink live die kill give take
make do work play start stop end begin finish win lose find lose keep hold
open close read write speak talk call meet wait help try use turn move
turn put get have be can will may must day night time year month week
morning evening today tomorrow yesterday now then here there home house
room door window road street city town country world sky sun moon star
cloud rain snow wind flower tree water fire air light dark color red blue
white black green yellow heart mind body hand head eye face hair mouth
voice word song music dance dream hope fear pain joy smile tear laugh cry
friend family mother father brother sister child baby man woman person
people name life death money food rain spring summer autumn winter cold
hot warm cool new old young big small long short high low fast slow
good bad happy sad angry tired hungry beautiful pretty ugly easy hard
true false right wrong same different many few all some none again still
always never often sometimes very really just only also even more most
less least first last next other another every each both
""".split())


def score(en):
    """작을수록 앞. 짧고 흔하고 한 단어인 영어를 핵심 뜻으로 본다."""
    s = len(en)
    if " " in en:
        s += 25
    if en in COMMON:
        s -= 40
    return s


def main():
    if not os.path.exists(SRC):
        sys.exit(f"source dictionary not found: {SRC}")
    src = json.load(open(SRC, encoding="utf-8"))
    ko2en = defaultdict(set)

    for en, glosses in (src.get("ko") or {}).items():
        en = en.strip().lower()
        if not en or BAD_EN.search(en) or len(en) > 28:
            continue
        for g in glosses:
            g = TRIM.sub("", g or "").strip()
            if not g or not HANGUL_ONLY.match(g) or not (1 <= len(g) <= 8):
                continue
            ko2en[g].add(en)
            # 산책하다 -> 산책 도 같은 뜻으로 쓸 수 있게 한 번 더
            if len(g) > 2 and g.endswith(("하다", "되다", "시키다")):
                stem = g[: -2 if g.endswith(("하다", "되다")) else -3]
                if len(stem) >= 1:
                    ko2en[stem].add(en)

    out = {}
    for ko, ens in ko2en.items():
        ranked = sorted(ens, key=score)[:4]
        out[ko] = ranked

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(OUT) / 1024
    print(f"{len(out):,} Korean headwords -> {OUT} ({size:.0f} KB)")
    for probe in ["사랑", "봄", "꽃", "눈물", "보다", "싶다", "말", "꿈", "믿다"]:
        print(f"  {probe}: {', '.join(out.get(probe, ['(none)']))}")


if __name__ == "__main__":
    main()
