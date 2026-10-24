# Sing Korean

**https://sing-korean.vercel.app**

Learn Korean from the songs you already know by heart.

Built for Clone Loop Day, 2026-10-24. The product is a free web app with no
signup; the GTM half of the repo is in `gtm/`.

---

## The problem

Tens of millions of people worldwide can sing a BTS song phonetically from
memory and understand none of it. They download a Korean app, get taught how to
buy apples, and quit. The motivation is already there and nothing connects it to
the language.

## What this does

35 BTS songs, every line broken down.

- **The official MV**, embedded per song.
- **Romanization of the real pronunciation.** Not a letter swap. The text goes
  through a Korean grapheme-to-phoneme pass first, so 국물 shows as `gungmul`
  and not `gukmul`, 같이 as `gachi`, 읽는 as `ingneun`.
- **Tap any word and it falls apart.** 보고 싶다 is not one word meaning "I miss
  you". It is 보 (to see) + 고 (and) + 싶 (want to). The morphological analyser
  splits every word in every line and each piece carries an English note. This
  is the part a translation blog cannot give you: learn the pattern and 먹고
  싶다 and 가고 싶다 come free.
- **Every word ranked by frequency across all 35 songs.** The top 100 cover 51%
  of every content word they sing; the top 400 cover 78%. So the app can answer
  the question no per-song blog can: what should I learn first.
- Progress and known-word marking, stored in the browser. No account, nothing
  collected.

## Why it is different

| | per-song translation blogs | general Korean parsers | this |
|---|---|---|---|
| line by line English | yes | no | yes |
| grammar breakdown per word | sometimes, by hand | yes | yes, automatic |
| real pronunciation romanization | romanized spelling only | no | yes, phonological |
| corpus-wide frequency ranking | no | no | yes |
| the MV next to the lyric | no | no | yes |

The frequency layer is the one no competitor can copy without rebuilding the
corpus, and it is what turns a reference site into a curriculum.

## How it is built

Static site, no framework, no build step. One HTML file, JSON data, a service
worker. Deployed on Vercel.

The pipeline is Python and runs on partial input on purpose, so the site can go
live while content is still landing.

```
corpus/*.txt            lyrics, local only, analysis input, never deployed
  ↓ scripts/repair_corpus.py    strip scraper junk, shift affected indices
  ↓ scripts/analyze.py          morpheme frequency ranking → data/freq.json
  ↓ scripts/assemble.py         + translations + glossaries → app/data/
app/                    the deployed site
```

| script | what it does |
|---|---|
| `romanize.py` | Revised Romanization applied to the pronunciation, with two corrections the libraries get wrong (`lr`→`ll`, tense consonant after a stop) |
| `ko_lex.py` | hand written glossary of Korean particles, endings, suffixes and auxiliaries, plus POS labels in English |
| `kotoken.py` | a line → clickable 어절 → morphemes with glosses. Merges 명사+하 into one verb so 필요해 resolves to 필요하다 |
| `build_dict.py` | inverts an English→Korean dictionary into Korean→English as a long-tail fallback |
| `analyze.py` | frequency ranking, and emits the top 400 for hand glossing |
| `assemble.py` | builds `app/data/index.json`, `app/data/song/<id>.json`, `app/data/freq.json` |
| `repair_corpus.py` | idempotent cleanup that also shifts translation indices by the number of lines it removed |

Content specification for translation and glossing work: `INSTRUCTIONS.md`.

### Numbers

35 songs, 2,250 lines, 1,323 distinct dictionary forms, 711 per-song vocabulary
entries, 140 culture and idiom notes, 400 hand written glosses covering the most
frequent words. Payload is about 41 KB per song, loaded on demand.

## Run it

```bash
pip3 install g2pkk korean-romanizer
python3 scripts/build_dict.py
python3 scripts/analyze.py
python3 scripts/assemble.py
cd app && vercel --prod
```

`corpus/` is gitignored. The pipeline degrades gracefully without it: songs with
no corpus file are skipped, songs with no translation ship without English.

## GTM

`gtm/` holds the go-to-market half, which is the actual subject of Loop Day.

| file | what |
|---|---|
| `CLONE-LOOP.md` | the run sheet: context pack, round one goal prompt, the first output drafted, review rubric, round two prompt |
| `SHARE.md` | the 60 second share script, the numbers, and answers to the questions the room will ask |
| `x-targets.md` | 53 verified accounts, in action tiers, with competitors marked |
| `reddit.md` | per-subreddit drafts written to pass each sub's self-promotion rules |
| `tiktok-plan.md` | the repeatable 30 second teaching format, 10 concepts |
| `seo.md` | 30 search queries mapped to the page that should answer each |
| `launch-checklist.md` | 24 hour posting order with UTM parameters per channel |
| `dm-templates.md` | three outreach messages, under 60 words each |

The loop is: pick the next song from the frequency ranking → generate a carousel
and a Shorts script in a fixed shape → review against the rubric → publish or
revise → read the UTM split → let that pick the next song. The generation is
automated. The decision to publish is not, and should not be.

## Lyrics

Lyrics remain the property of their respective rights holders. Translations,
romanization, grammar notes and frequency data on the site are original work
produced for it. Takedown requests and corrections are handled same day:
cshsteven0205@gmail.com. The licensed path, if this grows, is Musixmatch or
LyricFind.
