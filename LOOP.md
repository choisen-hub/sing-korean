# The GTM Agentic Loop

Clone Loop Day in Seoul, 2026-10-24. Run window: today through 2026-10-31 18:00.

Product: **Sing Korean** — https://sing-korean.vercel.app
A free web app that teaches Korean to international K-pop fans using BTS songs.
No signup, works on a phone.

---

## The goal I am committing to

**Get 1,000 real people to open the app and have 100 of them mark at least one
word, by 2026-10-31 18:00.**

Two numbers, not one, because reach without a first action is a bounce and
proves nothing. Marking a word is the smallest act that means a person actually
engaged with the thing the product does.

Secondary, qualitative: at least one post picked up by an account I do not
control (a repost, a fan page sharing it, a mod approving it on r/bangtan).

Starting point is honest: **0 users, deployed today.**

---

## Why the loop is shaped the way it is

Most GTM loops are: pick a channel, write a post, measure, repeat. The content
is an input a human supplies and the loop just distributes it.

This product has something unusual: **it already contains a ranked list of what
its own content should be about.** The corpus analysis ranks all 1,323 Korean
words BTS sings by frequency, each with the real lyric lines it appears in, and
each with a note on anything a non-Korean listener would miss.

So the loop reads its own product data to decide what to make next. Content
selection is not a creative decision taken each week; it is a query.

```
          ┌─────────────────────────────────────────────┐
          │  freq.json  — 1,323 words, ranked, with      │
          │  example lines and culture notes             │
          └───────────────┬─────────────────────────────┘
                          │  pick next subject
                          ▼
   ┌──────────────────────────────────────────────────────┐
   │ 1. SELECT   a word or line not yet used, scored by    │
   │    frequency rank x surprise x song popularity        │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ 2. CAPTURE  drive the live app headless, screenshot    │
   │    the real screens for that word  (capture_app.py)    │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ 3. RENDER   carousel 1080x1350 + Reel 1080x1920 from   │
   │    those screens  (render_cards.py, reel_usage.py)     │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ 4. WRITE    channel-native copy: IG caption, Shorts    │
   │    title, r/Korean post, X reply  (gtm/*.md rules)     │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ 5. REVIEW   against the rubric in gtm/CLONE-LOOP.md.   │
   │    Fails go back to step 3 with the reason attached.   │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ 6. PUBLISH  human decision. Every link carries a UTM   │
   │    naming the channel and the subject word.            │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ 7. MEASURE  opens, and marks per UTM source            │
   └───────────────┬──────────────────────────────────────┘
                   │  which subjects converted
                   └──────────────► back to step 1, reweighted
```

**The feedback edge is the point.** Step 7 does not just report a number, it
changes the scoring function in step 1. If words that carry a cultural
double meaning convert better than high-frequency plain words, the selector
shifts toward them next cycle. The loop learns which *kind of subject* works,
which is a product-specific question no generic GTM loop can ask.

## What is automated and what is not

| Step | Who |
|---|---|
| Select the subject | script, from the product's own data |
| Capture real app screens | script, headless Chrome driving the live site |
| Render carousel and Reel | script |
| Draft channel copy | agent, against written per-channel rules |
| Review against the rubric | agent, then me |
| **Publish** | **me, always** |
| Collect and reweight | script |

Publishing stays human on purpose. Automated posting into fandom spaces is how
accounts get banned and how a tool gets read as spam, which would cost more
reach than it buys.

## Iterations already run, today

The loop has been through four passes before launch. Recording them because the
judging asks whether the loop actually improved on its own intermediate results,
and these are the real ones.

| Pass | What was produced | Why it failed review | What changed |
|---|---|---|---|
| 1 | Narrated slideshow, static cards | Synthetic voice read as cheap; no motion | Dropped narration, built a real CSS-timeline animation renderer |
| 2 | Animated motion graphics of 보고 싶다 splitting | Led with grammar, which competitors already ship | Repositioned: the product is a beginner path, not a parser |
| 3 | Culture decode of 포도 in MIC Drop | Clever but off-brand for a learning tool | Dropped the decode angle from the hook, kept it inside the app |
| 4 | Real app screens, captions, generated music bed | Shipped | Screens now auto-checked for loading states before they can enter a render |

Pass 4 added a guard that came directly from a failure: a screenshot captured
while a page was still loading made it into a render. The pipeline now rejects
any capture whose pixel variance says the screen is empty.

## Measurement

Every published link carries `?utm_source=<channel>&utm_medium=<format>&utm_campaign=<subject-word>`,
so a result is attributable to both the channel and the subject, which is what
step 1 needs back.

Counted: opens, and words marked. Both are visible without an account because
progress is stored in the browser; the marking count is reported in aggregate
only.

## Repo map

| Path | What |
|---|---|
| `LOOP.md` | this file, the loop and the goal |
| `gtm/CLONE-LOOP.md` | run sheet: goal prompt, first output, review rubric, next-pass prompt |
| `gtm/POSITIONING.md` | what the product is actually for, and the angle I got wrong first |
| `gtm/reddit.md` | per-subreddit drafts written to each sub's rules |
| `gtm/x-targets.md` | 53 verified accounts in action tiers |
| `gtm/tiktok-plan.md` | the repeatable 30-second format |
| `gtm/seo.md` | 30 queries mapped to the page that answers each |
| `gtm/launch-checklist.md` | 24-hour order with the UTM table |
| `scripts/capture_app.py` | drives the live app headless, exact phone-size screens |
| `scripts/render_cards.py` | carousel and frame renderer |
| `scripts/reel_usage.py` | Reel assembly with a generated music bed |
| `scripts/analyze.py` | the corpus ranking the selector reads |
| `media/` | what the loop has produced so far |

Product build details are in `README.md`. This file is the loop.
