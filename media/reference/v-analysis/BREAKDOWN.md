# Reference breakdown: v-analysis

Source: `https://www.youtube.com/shorts/t0qElwr-Lqc`
1080x1920, 29.97 fps, 29.09s, 4 shots detected at scene threshold 0.28.

Format is what gets reused. Footage and wording do not.

## Shots

| # | in | out | dur | what is on screen | caption text | caption bbox (x,y,w,h as 0-1) | text height / frame height | transition in |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.00 | 8.07 | 8.07 | | | | | |
| 2 | 8.07 | 19.39 | 11.31 | | | | | |
| 3 | 19.39 | 26.66 | 7.27 | | | | | |
| 4 | 26.66 | 29.09 | 2.43 | | | | | |

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
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |

Rules carried over from the editing contract: do not add an ending card, accent
colour, background box or transition the reference does not have. Strip all
source audio from screen recordings. Compute per-segment speed as
`source segment length / target length`, leaving reading time on the moments
that matter. Keep captions in the same phrase-sized units as the reference
rather than merging them into long lines.
