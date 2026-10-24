# -*- coding: utf-8 -*-
"""Import owner-supplied English translations into data/ko/<id>.en.json.

The translation files are plain text, one English line per Korean line, matching
`corpus/<id>.txt` counted over non-blank lines. Alignment is the only thing that
can go wrong and it fails silently if it does, so this refuses to write a song
whose line count does not match the corpus exactly.

Existing `notes`, `vocab` and `hook` are preserved. The `lines` map is replaced
wholesale rather than merged, so the whole song reads in one consistent voice
instead of switching register wherever an earlier partial fill stopped.

  python3 scripts/import_translations.py [source_dir] [--dry-run]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "corpus")
KO = os.path.join(ROOT, "data", "ko")
DEFAULT_SRC = os.path.expanduser("~/Downloads/BTS_35_Lyrics_English")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0] if args else DEFAULT_SRC
    dry = "--dry-run" in sys.argv

    if not os.path.isdir(src):
        sys.exit(f"source directory not found: {src}")

    os.makedirs(KO, exist_ok=True)
    ok = skipped = 0
    total_lines = 0
    problems = []

    for i in range(1, 36):
        sid = f"b{i:02d}"
        pe = os.path.join(src, f"{sid}.txt")
        pk = os.path.join(CORPUS, f"{sid}.txt")
        if not os.path.exists(pe):
            problems.append(f"{sid}: no translation file")
            skipped += 1
            continue
        if not os.path.exists(pk):
            problems.append(f"{sid}: no corpus file")
            skipped += 1
            continue

        en = [l.rstrip("\n").strip() for l in open(pe, encoding="utf-8")]
        en = [l for l in en if l]
        ko = [l.strip() for l in open(pk, encoding="utf-8") if l.strip()]

        if len(en) != len(ko):
            problems.append(f"{sid}: {len(en)} English lines against {len(ko)} Korean — not written")
            skipped += 1
            continue

        p = os.path.join(KO, f"{sid}.en.json")
        doc = {}
        if os.path.exists(p):
            try:
                doc = json.load(open(p, encoding="utf-8"))
            except Exception:
                doc = {}
        doc.setdefault("id", sid)
        before = len(doc.get("lines") or {})
        doc["lines"] = {str(n): t for n, t in enumerate(en)}

        if not dry:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)

        ok += 1
        total_lines += len(en)
        print(f"  {sid}  {len(en):>3} lines  (was {before})")

    print(f"\n{ok} songs imported, {total_lines:,} lines"
          f"{' (dry run, nothing written)' if dry else ''}")
    if problems:
        print(f"{skipped} skipped:")
        for x in problems:
            print(f"  ! {x}")


if __name__ == "__main__":
    main()
