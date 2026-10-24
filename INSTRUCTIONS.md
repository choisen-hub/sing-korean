# Content spec

Everything a translation or glossing agent writes must follow this file. The app
assembles its data straight from these outputs, so a schema slip breaks the
build rather than degrading gracefully.

## Who the reader is

An English speaking K-pop fan who has the song memorised phonetically and
understands none of it. They may never have studied Korean. They are motivated
and impatient. They came for this one song and will stay if the explanation
makes them feel like they could read the next song themselves.

So: explain, do not just translate. A translation tells them what this line
means. A grammar note tells them what the next line means too.

## Voice

Natural native English. Write the way a sharp friend who happens to know Korean
would explain it over a drink.

Banned because they read as machine written: "dive into", "unlock", "delve",
"it's worth noting", "a testament to", "whether you're a ... or a ...". No
em dash chains. No sentence that begins "In Korean, ...". No exclamation marks.
Do not open a note by restating the line.

In Korean commentary addressed to the owner, never use the nakaguro (·) or 「」.

## Files to write

One file per song: `data/ko/<id>.en.json`, UTF-8, exactly this shape.

```json
{
  "id": "b01",
  "hook": [12, 13, 14, 15],
  "notes": {
    "s": "One sentence on what the song is about. Under 90 characters.",
    "t": "Three to five sentences of context: who is singing, what happened, what the song meant to the fandom, what it is known for. Concrete. No plot summary padding.",
    "k": [
      ["꽃잎이 떨어지고", "What this phrase is doing and why a learner should notice it"],
      ["보고 싶다", "The idiom explained: literally want to see, used for I miss you"]
    ]
  },
  "lines": {
    "0": "I miss you",
    "1": "Saying it out loud makes me miss you more"
  },
  "vocab": [
    {
      "w": "그립다",
      "en": "to miss, to long for",
      "note": "Describes missing a thing or a time, where 보고 싶다 is for missing a person",
      "i": 7
    }
  ]
}
```

### `lines`

- Keys are **line indices as strings**, matching the line order in
  `corpus/<id>.txt` counting only non-blank lines, starting at 0.
- **Never renumber.** Indices are referenced by the vocabulary and the share
  cards. If a line looks wrong, translate it anyway and flag it in your report.
- Translate every non-blank line. A line that is already English in the original
  gets its own text repeated verbatim as the value.
- Aim literal enough that a learner can map Korean words to English words, but
  not so literal it stops being English. Idioms get a natural rendering, with
  the literal reading moved into `notes.k` or a vocab `note`.
- No line numbers, speaker labels, or section markers in the value.

### `hook`

The 4 to 8 line indices of the part everyone knows, usually the chorus. Pick a
contiguous run. This drives the shareable card, so choose the lines that would
make a fan stop scrolling.

### `notes.k`

Two to four entries. Each is the kind of thing a fan translation leaves out:
an idiom that is not literal, a cultural reference, a double meaning, a
grammatical pattern the song leans on. Not vocabulary definitions, those go in
`vocab`.

### `vocab`

Twelve to twenty entries per song. Pick words a learner would actually want:
frequent, reusable, or central to the song. Skip proper nouns and English
loanwords.

- `w` is the **dictionary form**. Verbs and adjectives end in 다 (그립다, not
  그리워). Nouns are bare.
- `en` is one to three English equivalents, comma separated, no article clutter.
- `note` is optional, one line, only when there is something worth saying: a
  near synonym contrast, a register warning, a false friend. Omit it rather than
  padding.
- `i` is the index of a line where the word appears, so the app can link to it.

## Glossary batches

A glossing agent gets a slice of `data/curate_todo.json` and writes
`data/gloss/<batch>.json`:

```json
[
  {"w": "내", "en": "my", "note": "Shortened form of 나의. Also means inside as a noun, context decides"},
  {"w": "날", "en": "day", "note": "Also the contracted object form of 나를, me"}
]
```

Every word in your slice gets an entry, in the same order. `dict_guess` in the
input comes from an inverted dictionary that is **unreliable** — 손 came out as
"donny", 밤 as "chestnut". Treat it as noise, not as a starting point.

Where a form is genuinely ambiguous in lyrics, lead with the sense that is most
common in song lyrics and put the other in `note`.
