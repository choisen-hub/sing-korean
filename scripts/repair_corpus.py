# -*- coding: utf-8 -*-
"""Strip Genius scraper junk from the corpus and shift every index that moved.

Genius pages open with a `<Title> Lyrics` heading and an editorial blurb ending
in "Read More". The fetcher kept both, so on 30 of the 35 songs index 0 and 1
are not lyrics at all. Every translation agent numbered lines over the file as
it stood, so the junk is baked into the indices they wrote.

Deleting the junk alone would silently misalign every translation by the number
of lines removed. So this does both halves in one pass: strip the junk, count
how many non-blank lines went, then subtract that offset from every index in
the matching data/ko/<id>.en.json — the keys of `lines`, the `hook` run, and
each vocab entry's `i`. Anything that would land below zero was pointing at the
junk itself and gets dropped.

Idempotent. Running it twice finds nothing to strip and shifts nothing.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "corpus")
KO = os.path.join(ROOT, "data", "ko")

TITLE_LINE = re.compile(r"^.{0,80}\bLyrics\s*$", re.I)
BLURB = re.compile(r"Read More|Contributor|^\s*\d+\s+Contributors", re.I)


def is_junk(line, pos):
    """앞쪽 두 줄에만 적용한다. 가사 본문을 지우면 복구가 안 된다."""
    if pos > 1:
        return False
    s = line.strip()
    if not s:
        return False
    if TITLE_LINE.match(s):
        return True
    if BLURB.search(s):
        return True
    # 지니어스 해설문: 길고 영어 산문이고 따옴표로 곡명을 감싼다
    if len(s) > 85 and re.search(r"[“\"'].+[”\"']", s) and not re.search(r"[가-힣]{6,}", s):
        return True
    return False


def shift_doc(path, off):
    doc = json.load(open(path, encoding="utf-8"))
    changed = False

    lines = doc.get("lines") or {}
    if lines:
        new = {}
        for k, v in lines.items():
            try:
                i = int(k) - off
            except ValueError:
                continue
            if i >= 0:
                new[str(i)] = v
        if new != lines:
            doc["lines"] = new
            changed = True

    hook = doc.get("hook") or []
    if hook:
        nh = [i - off for i in hook if isinstance(i, int) and i - off >= 0]
        if nh != hook:
            doc["hook"] = nh
            changed = True

    for v in doc.get("vocab") or []:
        if isinstance(v.get("i"), int):
            ni = v["i"] - off
            if ni != v["i"]:
                v["i"] = max(ni, 0)
                changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    return changed


def main():
    apply = "--dry-run" not in sys.argv
    total_removed = 0
    report = []

    for p in sorted(glob.glob(os.path.join(CORPUS, "b*.txt"))):
        sid = os.path.basename(p)[:3]
        raw = open(p, encoding="utf-8").read().split("\n")

        kept, removed, seen_nonblank = [], 0, 0
        for line in raw:
            if seen_nonblank <= 1 and is_junk(line, seen_nonblank):
                removed += 1
                seen_nonblank += 1
                continue
            if line.strip():
                seen_nonblank += 1
            kept.append(line)

        # 앞머리에 남은 빈 줄 정리
        while kept and not kept[0].strip():
            kept.pop(0)

        if not removed:
            report.append((sid, 0, "clean"))
            continue

        total_removed += removed
        if apply:
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(kept))
            ko = os.path.join(KO, f"{sid}.en.json")
            did = shift_doc(ko, removed) if os.path.exists(ko) else None
            note = "shifted" if did else ("no translation yet" if did is None else "nothing to shift")
        else:
            note = "would strip"
        report.append((sid, removed, note))

    print(f"{'song':<6}{'junk':>5}  action")
    for sid, n, note in report:
        print(f"{sid:<6}{n:>5}  {note}")
    print(f"\n{total_removed} junk lines removed across "
          f"{sum(1 for r in report if r[1])} songs"
          f"{' (dry run, nothing written)' if not apply else ''}")


if __name__ == "__main__":
    main()
