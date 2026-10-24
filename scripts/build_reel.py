# -*- coding: utf-8 -*-
"""Assemble the vertical Reel: rendered frames + a spoken track, cut to the voice.

Each frame gets its own narration line. The frame is held for exactly as long as
its line takes to say, plus a short beat, so the cut always lands on the words
rather than on a guessed timing. macOS `say` does the voice; ffmpeg does the
rest.

  python3 scripts/build_reel.py  ->  media/sing-korean-reel.mp4
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES = os.path.join(ROOT, "media", "reel")
OUT = os.path.join(ROOT, "media", "sing-korean-reel.mp4")

VOICE = "Samantha"
TAIL = 0.45        # 말이 끝난 뒤 글자를 읽을 여유
LAST_HOLD = 2.2    # 링크가 붙은 마지막 장면은 더 오래

LINES = [
    "You have sung this. You don't know what it says.",
    "Everyone tells you it means, I miss you.",
    "That's the translation. It is not what the words say.",
    "It's three pieces.",
    "Bo. To see.",
    "Go. And. That's all it does.",
    "Ship. Want to.",
    "So you didn't learn a phrase. You learned a pattern. I want to eat. I want to go.",
    "B T S opens Spring Day with it. Twice. Thirty five songs, broken down, free.",
]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", path])
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 2.0


def main():
    frames = sorted(f for f in os.listdir(FRAMES) if f.startswith("f") and f.endswith(".png"))
    if len(frames) != len(LINES):
        sys.exit(f"{len(frames)} frames but {len(LINES)} narration lines — they must match")

    tmp = os.path.join(ROOT, "media", "_tmp")
    os.makedirs(tmp, exist_ok=True)

    # 1. 장면마다 음성
    clips, durs = [], []
    for i, line in enumerate(LINES, 1):
        aiff = os.path.join(tmp, f"v{i:02d}.aiff")
        r = run(["say", "-v", VOICE, "-o", aiff, line])
        if r.returncode != 0 or not os.path.exists(aiff):
            sys.exit(f"say failed on line {i}: {r.stderr.strip()[:200]}")
        d = duration(aiff) + TAIL + (LAST_HOLD if i == len(LINES) else 0)
        clips.append(aiff)
        durs.append(d)
        print(f"  scene {i}: {d:5.2f}s  {line[:48]}")

    # 2. 음성을 장면 길이에 맞춰 패딩하고 이어 붙인다
    padded = []
    for i, (a, d) in enumerate(zip(clips, durs), 1):
        p = os.path.join(tmp, f"p{i:02d}.wav")
        run(["ffmpeg", "-y", "-i", a, "-af", f"apad=whole_dur={d:.3f}",
             "-ar", "44100", "-ac", "2", p])
        padded.append(p)
    concat_a = os.path.join(tmp, "audio.txt")
    with open(concat_a, "w") as f:
        for p in padded:
            f.write(f"file '{p}'\n")
    voice = os.path.join(tmp, "voice.m4a")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_a,
         "-c:a", "aac", "-b:a", "160k", voice])

    # 3. 같은 길이로 프레임을 붙여 영상
    concat_v = os.path.join(tmp, "video.txt")
    with open(concat_v, "w") as f:
        for fr, d in zip(frames, durs):
            f.write(f"file '{os.path.join(FRAMES, fr)}'\nduration {d:.3f}\n")
        f.write(f"file '{os.path.join(FRAMES, frames[-1])}'\n")

    r = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_v,
             "-i", voice, "-map", "0:v", "-map", "1:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-r", "30",
             "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
                    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#120B22",
             "-c:a", "aac", "-b:a", "160k", "-shortest", OUT])
    if not os.path.exists(OUT):
        sys.exit("ffmpeg failed:\n" + r.stderr[-1200:])

    total = duration(OUT)
    size = os.path.getsize(OUT) / 1024 / 1024
    print(f"\n{OUT}\n  {total:.1f}s, {size:.1f} MB, 1080x1920, voice {VOICE}")


if __name__ == "__main__":
    main()
