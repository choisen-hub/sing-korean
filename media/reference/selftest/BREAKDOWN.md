# Reference breakdown: selftest

Source: `media/sing-korean-usage.mp4`
1080x1920, 30.0 fps, 21.00s, 1 shots detected at scene threshold 0.28.

Format is what gets reused. Footage and wording do not.

## Shots

| # | in | out | dur | what is on screen | caption text | caption bbox (x,y,w,h as 0-1) | text height / frame height | transition in |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.00 | 21.00 | 21.00 | | | | | |

Fill the last five columns while looking at `frames/sNN-a|b|c.png`. Mark anything
you cannot confirm as `unknown` rather than guessing. Convert pixel measurements
to ratios against 1080x1920 so they survive a different output size.

## Hook

- First frame shows:
- First words:
- The question it plants:
- Seconds before the viewer learns what this is about:

## Call to action

- Appears at:
- Wording:
- Where the link lives:

## Our replacement, one to one

| ref shot | our shot | our source clip | our caption | speed | notes |
|---|---|---|---|---|---|
| 1 | | | | | |

Rules carried over from the editing contract: do not add an ending card, accent
colour, background box or transition the reference does not have. Strip all
source audio from screen recordings. Compute per-segment speed as
`source segment length / target length`, leaving reading time on the moments
that matter. Keep captions in the same phrase-sized units as the reference
rather than merging them into long lines.
