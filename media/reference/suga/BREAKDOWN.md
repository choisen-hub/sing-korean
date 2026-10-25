# Reference breakdown: Suga Can't Be Bothered

Source: https://www.youtube.com/shorts/EAzTCt52JIw (GoBillyKorean)
1080x1920, 29.97 fps, 36.79s, 12 shots. 21,200 views.
Companion reference: `../v-analysis/` (V's Korean Analysis, 29.09s, 4 shots, 24,813 views).

Format is what gets reused. Footage and wording do not.

## What this format actually is

A presenter reaction. The host sits in frame the whole time and the BTS footage
is cut in underneath him as evidence, carrying its own broadcast subtitles
untouched. The joke lands on his face, not on the clip.

Worth stating plainly because it contradicts an assumption made earlier in this
project: the top performers in this niche are presenter-led, not screen-and-
caption. Both references checked are built on a human face. Any plan that
removes the presenter is departing from the reference, not copying it.

## Shots

Durations are measured. Layout and caption readings are from the frames in
`frames/`, so they are eye-read rather than pixel-exact; the automated white
pixel scan was contaminated by the bright purple set behind the host.

| # | in | out | dur | layout | caption |
|---|---|---|---|---|---|
| 1 | 0.00 | 7.17 | 7.17 | host full frame | teal label box lower left: `Suga (민윤기)` |
| 2 | 7.17 | 12.75 | 5.58 | evidence clip lower half, set visible above | none |
| 3 | 12.75 | 14.81 | 2.06 | evidence clip lower half | `Today I ate an eraser...` upper third |
| 4 | 14.81 | 15.68 | 0.87 | host, caption over him | `and it tastes good!` |
| 5 | 15.68 | 17.72 | 2.04 | evidence clip lower half | original broadcast subtitle only |
| 6 | 17.72 | 19.25 | 1.53 | evidence clip lower half | original broadcast subtitle only |
| 7 | 19.25 | 24.42 | 5.17 | host with tablet, clip as small inset | none |
| 8 | 24.42 | 25.69 | 1.27 | evidence clip | `[I have words for you]` from the source |
| 9 | 25.69 | 31.13 | 5.44 | host reacting, inset lower right | none |
| 10 | 31.13 | 31.73 | 0.60 | host laughing, head tilted back | none |
| 11 | 31.73 | 36.04 | 4.31 | evidence clip lower portion | none |
| 12 | 36.04 | 36.79 | 0.75 | host, final beat | none |

## Measured rhythm

Shot lengths: 0.60, 0.76, 0.87, 1.27, 1.53, 1.60, 2.04, 4.30, 5.17, 5.44, 6.04, 7.17

- median 2.04s
- three shots under one second, used as punches between explanations
- longest 7.17s, the opening, where the subject is introduced and nothing else happens
- the pattern alternates long explanation and short punch rather than running at one pace

## Caption style

- White fill, heavy black outline, rounded handwriting-weight face.
- Two to three words per line, two to three lines, centred, in the upper third.
- A sentence is split across consecutive shots rather than shown whole. `Today I
  ate an eraser...` then `and it tastes good!` on the next cut.
- Line height is roughly a fourteenth of the frame height, eye-read.
- The label box in shot 1 is a solid teal rectangle in the lower left with the
  same outlined white text, naming the subject in English and Korean.
- Nothing else is added. No end card, no accent colour, no background panel
  behind the body captions, no transition effects between cuts.

## Hook

- First frame: host mid-sentence, looking at camera, nothing else on screen.
- The label box tells you the subject within the first second.
- Seven seconds pass before any evidence appears, which is unusually patient for
  a Short and only works because the subject name does the holding.

## Call to action

None. No link, no follow prompt, no end card. The video ends on a laugh.

## Our replacement, one to one

The presenter is the part we cannot reproduce. The substitution that keeps the
structure intact is to let the app be the reaction: the host's payoff beat
becomes the moment a tap opens the breakdown. The app is the thing that knows
the answer, so it occupies the role the face occupied.

| ref shot | ref role | ours | source | speed |
|---|---|---|---|---|
| 1 | subject introduced, held long | title card, teal label box: `보고 싶다 (bogo sipta)` | rendered plate | static, 3.0s |
| 2 | evidence appears, no caption | lyric line on screen, Spring Day | `recordings/lyrics.mp4` 0.0-1.2s | 1.0x |
| 3 | caption part one | `Everyone says it means` | plate over clip | 1.4s |
| 4 | caption part two, short punch | `I miss you` struck through | plate over clip | 0.8s |
| 5-6 | evidence with source subtitle | scroll through the lyric, romanization visible | `recordings/lyrics.mp4` scroll run | 2.2x |
| 7 | host explains, long | the tap lands, breakdown opens | `recordings/lyrics.mp4` tap beat | 1.0x, hold |
| 8 | short punch | `보 + 고 + 싶` | plate | 0.9s |
| 9 | host reacts, long | the pattern generalises | plate: `먹고 싶다 / 가고 싶다` | 2.4s |
| 10 | shortest punch | marking a word, highlight appears | `recordings/words.mp4` tap beat | 0.6s |
| 11 | evidence again | quiz answered | `recordings/quiz.mp4` | 1.0x |
| 12 | final beat | url | plate | 1.0s |

Deviations to record: the reference has no call to action and we add a url in
shot 12, because the reference's host has a channel and we have nothing else to
convert with. The reference's evidence is broadcast footage and ours is our own
screen, which also means we do not carry over the untouched-source-subtitle
rule; our captions are ours to set.
