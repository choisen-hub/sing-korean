# -*- coding: utf-8 -*-
"""Korean lyric line -> clickable tokens with morpheme level grammar notes.

The point of the whole app sits in this file. A fan translation gives a learner
one English sentence. What a learner actually needs is why 보고 싶다 means
"I miss you": 보- is see, -고 links, 싶- is want to. Korean is agglutinative, so
a word in a lyric is almost never the word in a dictionary, and that gap is the
reason most fans stall. mecab-ko closes it.

A line becomes a list of 어절 (space separated words). Each 어절 carries its
romanization and its morphemes. Content morphemes get an English gloss, from the
curated per-song vocabulary when one exists and from the inverted dictionary
otherwise. Grammar morphemes get a hand written explanation from ko_lex.
"""

import functools
import json
import os
import re

import mecab

import ko_lex
from romanize import romanize, has_hangul

_m = mecab.MeCab()

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_KODICT = None


def kodict():
    global _KODICT
    if _KODICT is None:
        p = os.path.join(ROOT, "app", "data", "kodict.json")
        try:
            _KODICT = json.load(open(p, encoding="utf-8"))
        except Exception:
            _KODICT = {}
    return _KODICT


def _en_for(lemma_, pos):
    """사전형의 영어 뜻. 용언은 다를 뗀 어간으로도 찾아본다.

    역변환 사전은 품사를 모르고 섞여 있다. 보다에는 동사 to see와 조사 than이
    같이 들어 있어서, 용언 자리에는 to로 시작하는 항목을 앞으로 보낸다.
    """
    d = kodict()
    hit = d.get(lemma_)
    if not hit and pos in ko_lex.VERBAL and lemma_.endswith("다"):
        hit = d.get(lemma_[:-1])
    if not hit:
        return None
    if pos in ko_lex.VERBAL:
        verbish = [x for x in hit if x.startswith("to ")]
        if verbish:
            hit = verbish + [x for x in hit if not x.startswith("to ")][:1]
    else:
        plain = [x for x in hit if not x.startswith("to ")]
        if plain:
            hit = plain
    return hit[:3]


def _XSV_BASE(surface):
    """활용된 접미사를 사전형 어간으로. 필요해 -> 필요하다 가 되게 한다."""
    c = surface[0]
    if c in "하해했한할함":
        return "하"
    if c in "되돼됐될됨":
        return "되"
    if surface.startswith("시키"):
        return "시키"
    if c in "스":
        return "스럽"
    if c in "답다":
        return "답"
    return surface


@functools.lru_cache(maxsize=60000)
def morphs(word):
    """어절 하나의 형태소 분석 결과. (surface, pos) 튜플 목록."""
    out = []
    for t in _m.parse(word):
        if not t.surface:
            continue
        out.append((t.surface, t.feature.pos or "NA"))
    return tuple(out)


def token(word, vocab_en=None):
    """어절 하나 -> UI가 그릴 수 있는 토큰 한 덩어리.

    vocab_en: {사전형: 영어뜻} 형태의 곡별 어휘. 있으면 사전보다 우선한다.
    """
    vocab_en = vocab_en or {}
    raw = list(morphs(word))
    # 말 + 하 처럼 명사에 하/되가 붙어 한 동사가 된 자리는 복합어로 묶어 뜻을 단다.
    merged = []
    i = 0
    while i < len(raw):
        surf, pos = raw[i]
        # mecab은 XSV+EF 처럼 합친 태그를 내놓기도 한다. 앞머리로 판단한다.
        if (
            pos.split("+")[0] in ("NNG", "NNP", "XR")
            and i + 1 < len(raw)
            and raw[i + 1][1].split("+")[0] in ("XSV", "XSA")
        ):
            nxt = raw[i + 1][0]
            merged.append((surf + nxt, pos, surf + _XSV_BASE(nxt) + "다"))
            i += 2
            continue
        merged.append((surf, pos, None))
        i += 1

    ms = []
    for surf, pos, compound in merged:
        lem = compound or ko_lex.lemma(surf, pos)
        item = {"t": surf, "p": pos}
        if lem != surf:
            item["l"] = lem
        # mecab이 EP+EP 처럼 합친 태그를 내놓는 경우가 있다
        label = ko_lex.POS_LABEL.get(pos) or ko_lex.POS_LABEL.get(pos.split("+")[0])
        if compound:
            label = "verb"
        if label:
            item["pl"] = label
        epos = "VV" if compound else pos
        g = ko_lex.gloss(surf, pos)
        if g:
            item["g"] = g
        if epos in ko_lex.CONTENT:
            en = vocab_en.get(lem) or _en_for(lem, epos)
            if en:
                item["en"] = en if isinstance(en, list) else [en]
        ms.append(item)
    return {"s": word, "r": romanize(word), "m": ms}


def tokenize(line, vocab_en=None):
    """가사 한 줄 -> 어절 토큰 목록. 한글이 없는 어절은 분석하지 않는다."""
    out = []
    for w in line.split(" "):
        if not w:
            continue
        if not has_hangul(w):
            out.append({"s": w, "r": w, "m": []})
        else:
            out.append(token(w, vocab_en))
    return out


def content_lemmas(line):
    """빈도 집계용. 내용어의 (사전형, 품사)만 뽑는다."""
    out = []
    for w in line.split(" "):
        if not has_hangul(w):
            continue
        for surf, pos in morphs(w):
            if pos not in ko_lex.CONTENT:
                continue
            if pos == "SL":
                continue
            lem = ko_lex.lemma(surf, pos)
            if len(lem) < 1:
                continue
            out.append((lem, pos))
    return out


if __name__ == "__main__":
    import sys

    for line in sys.argv[1:] or ["이렇게 말하니까 더 보고 싶다", "꽃잎이 떨어지고"]:
        print(line)
        for t in tokenize(line):
            parts = " + ".join(
                f"{x['t']}({x.get('pl','?')}"
                + (f", {x.get('g') or ', '.join(x.get('en', []))}" if (x.get("g") or x.get("en")) else "")
                + ")"
                for x in t["m"]
            )
            print(f"   {t['s']:10s} {t['r']:16s} {parts}")
