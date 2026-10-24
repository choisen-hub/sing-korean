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

## What the product is, briefly

Tens of millions of people can sing a BTS song from memory and understand none
of it. They install a language app, get taught how to buy apples, and quit. The
motivation already exists; nothing connects it to the language.

Sing Korean puts all 35 songs on screen with three things attached to every one
of the 2,250 lines: the Korean, a romanization of how it is actually pronounced
(국물 is gungmul, not the gukmul every lyrics site prints), and the English.
Tap any word and it comes apart into its pieces with the grammar named, so
보고 싶다 stops being one lump meaning "I miss you" and becomes 보 see, 고 and,
싶 want to. Mark a word you do not know and it is highlighted in every other
song it appears in, queued into a quiz, and counted toward your progress.

And because the whole catalogue was counted, the app knows which 1,323 words
BTS actually sings and how often. The first 100 cover half of every song. That
turns a reference site into a path a beginner can walk from number one.

## What decides what we publish

An earlier draft of this file had the selection step read the product's own word
ranking and make content about the next word down the list. That was wrong, and
worth recording as the mistake it was: it is inventory management dressed as
strategy. It answers "which word do we explain next", which is an internal
question nobody outside the team is asking.

What should decide a post is the same thing that decides any piece of
go-to-market: **which message, to which audience, on which platform, right now.**
The product's data is the raw material that carries the message once those are
chosen. It is not the thing that chooses.

So the loop listens first.

### The four audiences, and what each is told

The product can be described four ways and they are not interchangeable.

| Segment | Where they are | Message that fits |
|---|---|---|
| ARMY who never studied Korean | r/bangtan, X fan accounts, fan IG | You already know the song. Here is what you have been singing. |
| Korean learners who like K-pop | r/Korean, r/languagelearning, Discord study servers | A real frequency list and a parser, built on material you will actually finish. |
| General K-pop listeners, no fandom | TikTok, Shorts, Reels | One line, one surprise, in fifteen seconds. |
| People who searched a meaning | Google | The page that answers the exact query they typed. |

Treating all four as one audience is how a launch post gets ignored by all four.

### The loop

```
   ┌──────────────────────────────────────────────────────────┐
   │ 1. MONITOR    what the audience is asking and what just   │
   │    happened. Sources, checked daily:                      │
   │      new posts and questions on r/Korean, r/bangtan,      │
   │        r/kpophelp, r/languagelearning                     │
   │      the 53 accounts in gtm/x-targets.md                  │
   │      repeated questions under the official MVs            │
   │      search suggest for "bts ___ meaning"                 │
   │      the fandom calendar: comebacks, anniversaries,       │
   │        chart moments, a clip going round                  │
   └───────────────┬──────────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 2. FRAME      pick one segment, one message hypothesis,   │
   │    one platform, one moment. Written down as a claim      │
   │    that can be wrong.                                     │
   └───────────────┬──────────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 3. SOURCE     now go to the product for the material that │
   │    carries that message best: a song, a line, a word, a   │
   │    culture note, a screen. This is where the ranking and  │
   │    the 140 notes are useful, as supply, not as strategy.  │
   └───────────────┬──────────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 4. PRODUCE    drive the live app headless, capture the    │
   │    real screens, render the Reel and carousel, write the  │
   │    copy in that platform's register  (scripts/, gtm/)     │
   └───────────────┬──────────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 5. REVIEW     against the rubric. Failures return to 4    │
   │    with the reason, or to 2 if the message was the fault. │
   └───────────────┬──────────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 6. PUBLISH    my decision, every time.                    │
   │    utm_source=platform, utm_medium=format,                │
   │    utm_content=segment, utm_campaign=message              │
   └───────────────┬──────────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 7. READ       opens and first-marks, split by segment and │
   │    by message, not by subject                             │
   └───────────────┬──────────────────────────────────────────┘
                   │  which message reached which audience
                   └────────► back to 2: retire what missed,
                              press what landed, and let 1 keep
                              widening where to listen
```

**The arrow that matters runs from 7 back to 2, not back to 3.** What gets
updated is the belief about which message lands on which audience. Changing
which word to feature would just be reshuffling stock.

### Why this is worth building rather than doing by hand

Steps 4 through 6 are where a one-person GTM effort normally dies: producing a
platform-native Reel, a carousel and four different posts for one message is a
day of work, so you end up testing one message a week and learning nothing.

Here steps 3 and 4 are fully mechanical. The app is driven headless, the real
screens are captured, the video and the slides render, and the copy is drafted
against written per-channel rules. A message hypothesis goes from decided to
publishable in minutes, so step 2 can be run often enough for step 7 to actually
teach something inside a seven day window.

The product data earns its place here by making step 3 instant rather than a
research task. That is a real advantage, and a smaller claim than the one this
file made before.

## What is automated and what is not

| Step | Who |
|---|---|
| Monitor the channels | script gathers, I read |
| Frame segment, message, platform | me |
| Source the material for it | script, from the product's own data |
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

Every published link carries `?utm_source=<platform>&utm_medium=<format>&utm_content=<segment>&utm_campaign=<message>`,
so a result is attributable to the segment and the message, which is what
step 2 needs back. Subject is recorded too, but it is not what gets optimised.

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
