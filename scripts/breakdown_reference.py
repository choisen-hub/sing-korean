# -*- coding: utf-8 -*-
"""Break a reference short down shot by shot, so its format can be reused.

What travels between a proven short and ours is the structure: how long each
shot runs, where the cuts fall, how big the captions are relative to the frame,
when the hook lands and when the call to action arrives. None of the reference's
footage or wording is reused; every shot gets replaced with our own content.

This produces the measurements. Reading the frames and writing what the captions
actually say is a human or model step afterwards, because no amount of pixel
analysis tells you why a hook worked.

  python3 scripts/breakdown_reference.py <file.mp4 | youtube-url> [--name tag]

Writes media/reference/<tag>/
  source.mp4            the clip, if it was downloaded
  shots.json            cut boundaries, durations, transition guesses
  audio.json            loudness over time, for speech and beat rhythm
  frames/sNN-*.png      first, middle and last frame of every shot
  contact-sheet.png     every shot on one page, for a first read
  BREAKDOWN.md          the template to fill in while looking at the frames
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "media", "reference")

SCENE_THRESHOLD = 0.28   # 낮추면 컷을 더 잘게, 올리면 크게 잡는다


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
             "-show_entries", "format=duration", "-of", "json", path])
    d = json.loads(r.stdout or "{}")
    st = (d.get("streams") or [{}])[0]
    num, _, den = (st.get("r_frame_rate") or "30/1").partition("/")
    fps = float(num) / float(den or 1)
    return {
        "w": st.get("width"), "h": st.get("height"), "fps": round(fps, 3),
        "duration": float((d.get("format") or {}).get("duration") or 0),
    }


def fetch(src, d):
    if os.path.exists(src):
        dst = os.path.join(d, "source.mp4")
        run(["ffmpeg", "-y", "-i", src, "-c", "copy", dst])
        return dst if os.path.exists(dst) else src
    dst = os.path.join(d, "source.mp4")
    r = run(["yt-dlp", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
             "-o", dst, "--no-playlist", src])
    if not os.path.exists(dst):
        sys.exit("download failed:\n" + (r.stderr or "")[-800:])
    return dst


def cuts(path, meta, threshold=None):
    """장면 전환 시각. showinfo 로 선택된 프레임의 pts 를 읽는다.

    하드컷이 아니라 디졸브나 페이드로 넘어가는 영상은 높은 임계값에서 한 덩어리로
    잡힌다. 그래서 컷이 너무 적게 나오면 임계값을 낮춰 다시 본다.
    """
    threshold = SCENE_THRESHOLD if threshold is None else threshold
    r = run(["ffmpeg", "-i", path, "-filter:v",
             f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    times = []
    for line in (r.stderr or "").splitlines():
        if "pts_time:" in line:
            try:
                times.append(round(float(line.split("pts_time:")[1].split()[0]), 3))
            except (IndexError, ValueError):
                pass
    bounds = [0.0] + [t for t in times if t > 0.12] + [round(meta["duration"], 3)]
    shots = []
    for i, (a, b) in enumerate(zip(bounds, bounds[1:]), 1):
        if b - a < 0.12:          # 너무 짧은 조각은 앞 shot 에 붙인다
            if shots:
                shots[-1]["out"] = b
                shots[-1]["dur"] = round(b - shots[-1]["in"], 3)
            continue
        shots.append({"shot": i, "in": a, "out": b, "dur": round(b - a, 3)})
    for i, s in enumerate(shots, 1):
        s["shot"] = i
    # 20초가 넘는데 컷이 두 개도 안 잡히면 부드러운 전환일 가능성이 크다
    if len(shots) < 3 and threshold > 0.06 and meta["duration"] > 6:
        lower = round(threshold / 2.5, 3)
        deeper = cuts(path, meta, lower)
        if len(deeper) > len(shots):
            for s in deeper:
                s["threshold"] = lower
            return deeper
    return shots


def loudness(path, d):
    """0.25초 간격 음량. 말의 박자와 비트 위치를 짚는 데 쓴다."""
    r = run(["ffmpeg", "-i", path, "-af",
             "astats=metadata=1:reset=6,ametadata=print:key=lavfi.astats.Overall.RMS_level",
             "-f", "null", "-"])
    vals = []
    for line in (r.stderr or "").splitlines():
        if "RMS_level=" in line:
            try:
                vals.append(round(float(line.split("RMS_level=")[1]), 1))
            except ValueError:
                pass
    out = {"rms_sequence_db": vals}
    with open(os.path.join(d, "audio.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


def grab(path, d, shots):
    fd = os.path.join(d, "frames")
    os.makedirs(fd, exist_ok=True)
    picks = []
    for s in shots:
        for tag, t in (("a", s["in"] + 0.05),
                       ("b", (s["in"] + s["out"]) / 2),
                       ("c", max(s["in"] + 0.05, s["out"] - 0.08))):
            p = os.path.join(fd, f"s{s['shot']:02d}-{tag}.png")
            run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", path,
                 "-frames:v", "1", "-q:v", "2", p])
            if os.path.exists(p):
                picks.append(p)
    mids = [os.path.join(fd, f"s{s['shot']:02d}-b.png") for s in shots]
    mids = [m for m in mids if os.path.exists(m)]
    if mids:
        sheet = os.path.join(d, "contact-sheet.png")
        lst = os.path.join(d, "_sheet.txt")
        with open(lst, "w") as f:
            for m in mids:
                f.write(f"file '{m}'\n")
        cols = min(5, len(mids))
        rows = (len(mids) + cols - 1) // cols
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
             "-vf", f"scale=320:-1,tile={cols}x{rows}:padding=8:color=#111111",
             "-frames:v", "1", sheet])
        os.unlink(lst)
    return picks


TEMPLATE = """# Reference breakdown: {tag}

Source: `{src}`
{w}x{h}, {fps} fps, {duration:.2f}s, {n} shots detected at scene threshold {thr}.

Format is what gets reused. Footage and wording do not.

## Shots

| # | in | out | dur | what is on screen | caption text | caption bbox (x,y,w,h as 0-1) | text height / frame height | transition in |
|---|---|---|---|---|---|---|---|---|
{rows}

Fill the last five columns while looking at `frames/sNN-a|b|c.png`. Mark anything
you cannot confirm as `unknown` rather than guessing. Convert pixel measurements
to ratios against {w}x{h} so they survive a different output size.

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
{maprows}

Rules carried over from the editing contract: do not add an ending card, accent
colour, background box or transition the reference does not have. Strip all
source audio from screen recordings. Compute per-segment speed as
`source segment length / target length`, leaving reading time on the moments
that matter. Keep captions in the same phrase-sized units as the reference
rather than merging them into long lines.
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    src = args[0]
    tag = "ref"
    if "--name" in sys.argv:
        tag = sys.argv[sys.argv.index("--name") + 1]
    d = os.path.join(OUT, tag)
    os.makedirs(d, exist_ok=True)

    path = fetch(src, d)
    meta = probe(path)
    print(f"{meta['w']}x{meta['h']}  {meta['fps']} fps  {meta['duration']:.2f}s")

    shots = cuts(path, meta)
    with open(os.path.join(d, "shots.json"), "w") as f:
        json.dump({"meta": meta, "threshold": SCENE_THRESHOLD,
                   "effective_threshold": (shots[0].get("threshold") if shots else None) or SCENE_THRESHOLD,
                   "shots": shots}, f, indent=1)
    print(f"{len(shots)} shots")
    for s in shots:
        print(f"  {s['shot']:>2}  {s['in']:6.2f} -> {s['out']:6.2f}  {s['dur']:5.2f}s")

    loudness(path, d)
    grab(path, d, shots)

    rows = "\n".join(
        f"| {s['shot']} | {s['in']:.2f} | {s['out']:.2f} | {s['dur']:.2f} | | | | | |"
        for s in shots
    )
    maprows = "\n".join(f"| {s['shot']} | | | | | |" for s in shots)
    with open(os.path.join(d, "BREAKDOWN.md"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(tag=tag, src=src, n=len(shots), thr=SCENE_THRESHOLD,
                                rows=rows, maprows=maprows, **meta))
    print(f"\n{d}\n  shots.json, audio.json, frames/, contact-sheet.png, BREAKDOWN.md")


if __name__ == "__main__":
    main()
