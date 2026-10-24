# Clone Loop Day — run sheet

Event: Clone Loop Day, 2026-10-24, 15:00–18:00 KST, NAVER D2SF Gangnam.
Deliverable: an agentic GTM workflow run inside Clone, plus a first output you
could actually publish, plus the next task left queued in Clone.
Track chosen: **Instagram carousel and YouTube Shorts.**

Product link to bring: **https://sing-korean.vercel.app**

---

## 1. Context to paste into Clone first

> I have a free web app called Sing Korean: https://sing-korean.vercel.app
>
> It teaches Korean to international K-pop fans using BTS songs. 35 songs, every
> line with the official MV embedded, romanization of the real pronunciation, and
> a tap-any-word feature that breaks the word into its pieces with English
> grammar notes. 보고 싶다 is not one word meaning "I miss you" — it is 보 (see)
> plus 고 (and) plus 싶 (want to). It also ranks every word across all 35 songs
> by frequency: the top 100 words cover 51% of everything they sing, the top 400
> cover 78%.
>
> No signup, no login, works on a phone.
>
> The customer is an English-speaking K-pop fan, roughly 14 to 28, who has songs
> memorised phonetically and understands none of it. They have tried a Korean
> app like Duolingo and quit because the sentences were about buying apples.
>
> What makes this different from fan translation blogs: a blog gives you one
> translation of one song. This gives you the grammar, so you can read the next
> song yourself.
>
> Competitors I already know about: doolsetbangtan (translation blog, no app),
> btslyrictranslations.com (per-song grammar posts, no app), mirinae.io (Korean
> parser, not K-pop), @BTStranslation_ (sells paid classes).

## 2. Round one goal prompt

> Help me find the customers for this product on Instagram and YouTube, then
> draft the first thing I should post.
>
> I want two artifacts:
> 1. An Instagram carousel, 8 slides, with the exact text for each slide.
> 2. A YouTube Shorts script, 30 seconds, with on-screen text and timings.
>
> Both must teach one real thing in under 30 seconds, not advertise the app. The
> app link goes in the caption, not the content. Open on the single most famous
> Korean line in BTS's catalogue and show that it is three pieces, not one word.
>
> Also give me a list of the Instagram and YouTube accounts and hashtags where
> this audience already gathers, and tell me which single one you would post to
> first and why.

## 3. First output, already drafted

Use this as the thing to compare Clone's output against. If Clone beats it, use
Clone's. If it does not, feed this in and ask it to improve on it.

### Instagram carousel, 8 slides

1. You have screamed 보고 싶다 at a concert. Do you know what you said?
2. Most people think it means "I miss you". It does. But that is not what it says.
3. 보고 싶다 — bogo sipta. Three pieces.
4. 보 — to see. The same 보 in 보여 (it shows) and 봐 (look).
5. 고 — and. Glues two verbs together. Nothing more.
6. 싶 — to want to. Only ever attaches to a verb with 고 in front of it.
7. So "I miss you" in Korean is literally: I want to see you. Now you know a pattern, not a phrase. 먹고 싶다 — I want to eat. 가고 싶다 — I want to go.
8. Spring Day opens with it. Twice. 35 songs broken down like this, free, no signup. Link in bio.

Caption:
> Spring Day's first line is three grammar pieces in a trench coat. 보고 싶다 = 보 (see) + 고 (and) + 싶 (want to). Learn the pattern and you get 먹고 싶다, 가고 싶다, 하고 싶다 for free.
>
> I built a free site that does this for 35 BTS songs. Tap any word, it falls apart into its pieces. No signup. sing-korean.vercel.app
>
> #bts #learnkorean #korean #btsarmy #korea #koreanlanguage #springday #bangtan #studykorean #kpop

### YouTube Shorts, 30 seconds

| Time | On screen | Voice or caption |
|---|---|---|
| 0:00 | 보고 싶다 in huge type | "You have sung this. You do not know what it says." |
| 0:03 | "I miss you" appears, then a line strikes it out | "Everyone tells you it means I miss you. That is the translation, not the meaning." |
| 0:06 | The word splits into 보 / 고 / 싶 | "It is three pieces." |
| 0:09 | 보 highlighted, "to see" | "보. To see." |
| 0:13 | 고 highlighted, "and" | "고. And. That is all it does." |
| 0:17 | 싶 highlighted, "want to" | "싶. Want to." |
| 0:21 | 먹고 싶다 / 가고 싶다 appear below | "So you did not learn a phrase. You learned a pattern. I want to eat. I want to go." |
| 0:26 | Spring Day MV frame, site URL | "BTS opens Spring Day with it. 35 songs, broken down, free." |

Title: What 보고 싶다 actually says (it is not "I miss you")
Description first line: Free, no signup — sing-korean.vercel.app

## 4. Review rubric for the loop

Judge Clone's output against these, in order. This is the review step.

1. Does the first two seconds state a thing the viewer already half knows, so they feel caught out? If it opens by explaining the app, it failed.
2. Does it teach one transferable pattern, not one fact? The 먹고 싶다 / 가고 싶다 beat is the whole point.
3. Is the Korean correct? 보고 싶다 is bogo sipta, not bogo shipda. Check any romanization it produces.
4. Is the link in the caption rather than the content?
5. Would a fan send this to another fan? If it reads like marketing, no.

## 5. Round two prompt

> Here is what we published and what I noticed. [paste feedback from the room]
>
> Improve the loop itself, not just the post. Specifically:
> - Turn this into a repeatable format I can run for any of the 35 songs, where
>   the only input is a song title and one line, and the output is a carousel and
>   a Shorts script in this exact shape.
> - Pick the next three songs and lines that would work best in this format and
>   say why those lines.
> - Tell me what to measure to know whether it worked, given I cannot see who
>   watched.

## 6. Next task to leave queued in Clone

> Every week, take the next song from the frequency-ranked list, generate the
> carousel and the Shorts script in the format we settled on, and leave both in
> drafts for me to review before anything is posted.

## 7. Measurement, before anything goes out

Add `?utm_source=ig&utm_medium=carousel&utm_campaign=loopday` to the Instagram
link and `?utm_source=yt&utm_medium=shorts&utm_campaign=loopday` to the Shorts
link, so the two channels are separable. Full table in `launch-checklist.md`.

Nothing gets posted without the owner deciding. The event says the same.
