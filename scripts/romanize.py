# -*- coding: utf-8 -*-
"""Revised Romanization of Korean, run on the actual pronunciation.

g2pkk applies the phonological rules (비음화, 유음화, 구개음화, 연음) and then
korean-romanizer transliterates the result. Two corrections are needed on top:

  lr -> ll        유음화 output: 신라 [실라] would come out as silra, RR says silla
  stop + tense    경음화 doubling reads badly in Latin: 싶다 [십따] -> sipta,
                  not siptta. One letter is enough to cue the tense sound.

Checked against the National Institute of Korean Language examples:
  국물 gungmul · 같이 gachi · 읽는 ingneun · 광한루 gwanghallu · 해돋이 haedoji
"""

import re
import functools

from g2pkk import G2p
from korean_romanizer.romanizer import Romanizer

_g2p = G2p()

_TENSE = {"kk": "k", "tt": "t", "pp": "p", "ss": "s", "jj": "j"}
_TENSE_AFTER_STOP = re.compile(r"([ktp])(kk|tt|pp|ss|jj)")

HANGUL = re.compile(r"[가-힣]")


def has_hangul(s):
    return bool(HANGUL.search(s))


@functools.lru_cache(maxsize=40000)
def romanize(text):
    """한 덩어리(줄 또는 어절)를 로마자로. 한글이 없으면 원문 그대로."""
    if not text or not has_hangul(text):
        return text
    try:
        spoken = _g2p(text)
    except Exception:
        spoken = text
    try:
        out = Romanizer(spoken).romanize()
    except Exception:
        return text
    out = out.replace("lr", "ll")
    out = _TENSE_AFTER_STOP.sub(lambda m: m.group(1) + _TENSE[m.group(2)], out)
    return out


@functools.lru_cache(maxsize=40000)
def pronounce(text):
    """발음 표기(한글). 가사 줄의 실제 소리를 보여줄 때 쓴다."""
    if not text or not has_hangul(text):
        return text
    try:
        return _g2p(text)
    except Exception:
        return text


def romanize_words(line):
    """어절 단위 로마자. UI에서 한국어 어절과 1:1로 붙여 쓰기 위한 것.

    줄 전체를 한 번에 돌리면 어절 경계를 넘는 음운 변화까지 반영되지만,
    어절마다 따로 돌려야 화면에서 짝이 맞는다. 가사는 어절 경계에서
    끊어 부르는 경우가 많아 이쪽이 학습용으로 더 정확하다.
    """
    return [romanize(w) for w in line.split(" ")]


if __name__ == "__main__":
    import sys

    cases = sys.argv[1:] or [
        "보고 싶다", "국물", "같이", "읽는", "광한루", "해돋이",
        "꽃잎이 떨어지고", "믿었던", "없을까", "어떻게",
    ]
    for c in cases:
        print(f"{c}  [{pronounce(c)}]  {romanize(c)}")
