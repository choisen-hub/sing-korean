# Presenter slot

The reel format copied from `media/reference/suga/` is presenter-led. This folder
holds the face that occupies that role.

Drop a file named `presenter.png` here and `scripts/reel_hosted.py` will use it.
Portrait orientation, at least 1080 wide. A head-and-shoulders crop works best
because the format keeps the face in the upper half with captions over it.

## How to produce one

Nothing on this machine can generate a photoreal face: no local diffusion model,
no API key. Options, cheapest first.

1. **Replicate or fal.ai**, pay as you go, roughly one to four cents an image.
   Put the token in `.env` as `REPLICATE_API_TOKEN` and run
   `python3 scripts/make_presenter.py "<prompt>"`.
2. **A stock portrait** from Pexels or Unsplash. Free to use commercially, but
   these are real people and the licences do not cover implying that the person
   endorses a product. Using one as a recurring brand presenter is the wrong
   side of that line.
3. **An illustrated character**, which can be drawn here in SVG with no key, at
   the cost of not being photoreal.

## Two constraints

The face must not resemble any real person, and in particular must not resemble
a BTS member. Beyond the publicity-rights problem, a fandom audience spots it
immediately and reads the whole account as bait.

Keep the same image across every video. The reference's hold works because the
viewer recognises the host on sight; a face that changes each time buys nothing.
