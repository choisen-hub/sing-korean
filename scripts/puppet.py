# -*- coding: utf-8 -*-
"""Animate the presenter still: head sway, blinking, and a mouth that opens with
the narration.

A real talking head needs a lip-sync service and there is no keyless one, so this
does the honest alternative. The still is treated as a 2.5D puppet: the whole
frame drifts and tilts slightly, the eyes close for a few frames at intervals,
and the mouth region is stretched open in proportion to the narration's loudness
at that moment. It is not lip sync, the shapes do not match phonemes, but the
face moves and it opens when words are being said.

Region coordinates are ratios of the image, so a different portrait only needs
the four numbers retuned.

  python3 scripts/puppet.py --audio media/_tmp/voice.wav --seconds 6
  python3 scripts/puppet.py --check          # draws the regions and exits
"""

import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MEDIA = os.path.join(ROOT, "media")
SRC = os.path.join(MEDIA, "presenter", "presenter.png")
OUTDIR = os.path.join(MEDIA, "_puppet")

FPS = 30

# 얼굴 부위. 이미지 비율 기준이라 다른 초상으로 바꾸면 이 넷만 다시 잡으면 된다.
MOUTH = dict(x=0.40, y=0.705, w=0.22, h=0.075)
EYES = dict(x=0.26, y=0.485, w=0.50, h=0.075)

BLINK_EVERY = 3.1      # 초. 사람은 3~5초에 한 번 깜빡인다
BLINK_FRAMES = 3


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def envelope(audio, n, fps=FPS):
    """프레임마다 음량 0~1. 입이 얼마나 열릴지를 정한다."""
    if not audio or not os.path.exists(audio):
        # 음성이 없으면 말하지 않는 얼굴. 입은 닫아 둔다.
        return [0.0] * n
    raw = os.path.join(OUTDIR, "_env.pcm")
    run(["ffmpeg", "-y", "-i", audio, "-ac", "1", "-ar", str(fps * 400),
         "-f", "s16le", raw])
    if not os.path.exists(raw):
        return [0.0] * n
    import array
    a = array.array("h")
    with open(raw, "rb") as f:
        a.frombytes(f.read())
    os.unlink(raw)
    win = 400
    out = []
    for i in range(n):
        chunk = a[i * win:(i + 1) * win]
        if not chunk:
            out.append(0.0)
            continue
        rms = math.sqrt(sum(float(v) * v for v in chunk) / len(chunk)) / 32768.0
        out.append(rms)
    peak = max(out) or 1.0
    # 제곱근을 씌워 작은 소리에도 입이 조금 열리게 한다
    return [min(1.0, (v / peak) ** 0.55) for v in out]


def feather(size, pad):
    """가장자리를 흐리게 한 마스크. 늘린 조각을 그대로 붙이면 사각 이음매가
    드러나므로, 경계를 녹여서 합성한다."""
    w, h = size
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rectangle([pad, pad, w - pad, h - pad], fill=255)
    return m.filter(ImageFilter.GaussianBlur(pad * 0.75))


def open_mouth(im, amount):
    """입 영역을 세로로 늘려 벌어진 것처럼 보이게 한다."""
    if amount <= 0.02:
        return im
    W, H = im.size
    x0, y0 = int(MOUTH["x"] * W), int(MOUTH["y"] * H)
    x1, y1 = x0 + int(MOUTH["w"] * W), y0 + int(MOUTH["h"] * H)
    bw, bh = x1 - x0, y1 - y0
    # 여백을 두고 넓게 떠서 늘려야 턱 경계가 영역 밖에서 녹는다
    px, py = int(bw * 0.28), int(bh * 0.55)
    cx0, cy0 = max(0, x0 - px), max(0, y0 - py)
    cx1, cy1 = min(W, x1 + px), min(H, y1 + py)
    patch = im.crop((cx0, cy0, cx1, cy1))
    pw, ph = patch.size
    grow = 1.0 + 0.55 * amount
    patch = patch.resize((pw, int(ph * grow)), Image.LANCZOS).crop((0, 0, pw, ph))
    im.paste(patch, (cx0, cy0), feather((pw, ph), max(10, int(min(pw, ph) * 0.18))))
    return im


def close_eyes(im, strength):
    """눈 영역을 눌러 감은 것처럼. 위아래 피부를 끌어와 덮는다."""
    if strength <= 0:
        return im
    W, H = im.size
    x0, y0 = int(EYES["x"] * W), int(EYES["y"] * H)
    x1, y1 = x0 + int(EYES["w"] * W), y0 + int(EYES["h"] * H)
    h = y1 - y0
    keep = max(2, int(h * (1.0 - 0.8 * strength)))
    region = im.crop((x0, y0, x1, y1)).resize((x1 - x0, keep), Image.LANCZOS)
    lid = im.crop((x0, max(0, y0 - h // 2), x1, y0)).resize((x1 - x0, h - keep), Image.LANCZOS)
    band = Image.new("RGB", (x1 - x0, h))
    band.paste(lid, (0, 0))
    band.paste(region, (0, h - keep))
    im.paste(band, (x0, y0), feather(band.size, max(6, int(h * 0.3))))
    return im


def sway(im, t, W, H):
    """고개 흔들림. 아주 작게 해야 사람처럼 보인다."""
    ang = 0.75 * math.sin(t * 0.9) + 0.3 * math.sin(t * 2.3)
    dx = 7 * math.sin(t * 0.7)
    dy = 5 * math.sin(t * 1.15)
    big = im.rotate(ang, resample=Image.BICUBIC, center=(W / 2, H * 0.62))
    return big.transform(big.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy),
                         resample=Image.BICUBIC)


def check():
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    for name, r, col in (("mouth", MOUTH, (255, 80, 80)), ("eyes", EYES, (90, 200, 255))):
        d.rectangle([r["x"] * W, r["y"] * H,
                     (r["x"] + r["w"]) * W, (r["y"] + r["h"]) * H],
                    outline=col, width=7)
    p = os.path.join(OUTDIR, "regions.png")
    os.makedirs(OUTDIR, exist_ok=True)
    im.save(p)
    print(f"{p}  — 빨강 입, 파랑 눈. 어긋나면 MOUTH/EYES 비율을 고친다")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    if "--check" in sys.argv:
        return check()

    audio = None
    if "--audio" in sys.argv:
        audio = sys.argv[sys.argv.index("--audio") + 1]
    seconds = 6.0
    if "--seconds" in sys.argv:
        seconds = float(sys.argv[sys.argv.index("--seconds") + 1])
    out = os.path.join(MEDIA, "presenter", "presenter-talking.mp4")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]

    base = Image.open(SRC).convert("RGB")
    W, H = base.size
    n = int(seconds * FPS)
    env = envelope(audio, n)

    fd = os.path.join(OUTDIR, "frames")
    os.makedirs(fd, exist_ok=True)
    blink_period = int(BLINK_EVERY * FPS)
    for i in range(n):
        t = i / FPS
        im = base.copy()
        im = open_mouth(im, env[i])
        phase = i % blink_period
        if phase < BLINK_FRAMES:
            im = close_eyes(im, 1.0 - abs(phase - (BLINK_FRAMES - 1) / 2) / ((BLINK_FRAMES - 1) / 2 + 1e-6))
        im = sway(im, t, W, H)
        im.save(os.path.join(fd, f"{i:05d}.png"))
        if i and i % 60 == 0:
            print(f"  {i}/{n}")

    # 1915 처럼 홀수 높이면 yuv420p 인코딩이 통째로 실패한다. 짝수로 맞춘다.
    r = run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(fd, "%05d.png"),
             "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-pix_fmt", "yuv420p", out])
    # 빈 파일이 남을 수 있어 존재만 보지 않고 크기까지 확인한다
    if not os.path.exists(out) or os.path.getsize(out) < 1024:
        sys.exit("encode failed:\n" + r.stderr[-900:])
    print(f"\n{out}  {seconds:.1f}s, {os.path.getsize(out)/1024/1024:.1f} MB")
    json.dump({"mouth": MOUTH, "eyes": EYES, "fps": FPS,
               "audio": audio, "seconds": seconds},
              open(os.path.join(OUTDIR, "puppet.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
