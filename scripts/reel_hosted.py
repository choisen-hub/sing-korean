# -*- coding: utf-8 -*-
"""Build the presenter-led reel, following the measured reference format.

Structure, caption style and cut rhythm come from
`media/reference/suga/BREAKDOWN.md`: a host who holds the opening alone while a
label box names the subject, evidence cut in underneath, captions split into
two or three word lines across consecutive shots, and long explanation shots
punctuated by sub-second punches.

The one substitution is the payoff. The reference lands its joke on the host's
face; we land it on the app, so the tap that opens the word breakdown sits
where the reaction shot sat.

Each shot renders as its own clip and they are concatenated, which keeps the
ffmpeg graph small enough to debug one shot at a time.

  python3 scripts/reel_hosted.py   ->  media/sing-korean-hosted.mp4
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MEDIA = os.path.join(ROOT, "media")
REC = os.path.join(MEDIA, "recordings")
TMP = os.path.join(MEDIA, "_hosted")
HOST = os.path.join(MEDIA, "presenter", "presenter.png")
OUT = os.path.join(MEDIA, "sing-korean-hosted.mp4")

W, H, FPS = 1080, 1920, 30
SPLIT_TOP = 880          # 분할 화면에서 진행자가 차지하는 높이
# 분할 화면에서는 얼굴 전체가 띠 안에 들어와야 한다. 전체 폭으로 확대하면
# 머리가 띠보다 커져서 눈만 보이거나 입이 분할선에 잘린다. 그래서 가로를
# 줄여 머리 전체를 띠 높이에 맞추고 좌우를 배경색으로 채운다.
SPLIT_HOST_W = 780
SPLIT_FACE_Y = 275

# 레퍼런스의 자막 규칙: 흰 글씨에 두꺼운 검정 테두리, 한 줄 2~3단어, 상단 1/3
CAPTION_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent;width:%(W)dpx;height:%(H)dpx;
  font-family:-apple-system,"Helvetica Neue","Apple SD Gothic Neo",sans-serif}
.cap{position:absolute;left:70px;right:70px;top:%(TOP)dpx;text-align:center;
  font-weight:800;font-size:%(SIZE)dpx;line-height:1.14;letter-spacing:-.01em;
  color:#fff;-webkit-text-stroke:14px #000;paint-order:stroke fill}
.cap .ko{font-size:%(KOSIZE)dpx}
.cap s{text-decoration:none;position:relative;display:inline-block}
.cap s::after{content:"";position:absolute;left:-10px;right:-10px;top:52%%;
  height:13px;border-radius:7px;background:#FFD166}
.label{position:absolute;left:56px;bottom:300px;background:#1E9E9E;
  padding:26px 38px;border-radius:10px;text-align:left;
  font-weight:800;font-size:72px;line-height:1.2;color:#fff;
  -webkit-text-stroke:10px #000;paint-order:stroke fill}
.label small{display:block;font-size:46px;margin-top:8px}
.url{position:absolute;left:0;right:0;bottom:170px;text-align:center;
  font-weight:800;font-size:58px;color:#fff;-webkit-text-stroke:12px #000;
  paint-order:stroke fill}
"""

# (길이, 레이아웃, 캡션 html, 클립, 클립 구간, 배속)
# 레퍼런스 컷 리듬을 따라 긴 설명과 1초 미만 펀치를 섞는다.
SHOTS = [
    dict(dur=3.4, layout="host",
         html='<div class="label">보고 싶다<small>bogo sipta</small></div>'),
    dict(dur=2.4, layout="split", clip="lyrics", seg=(1.05, 1.50), speed=1.0),
    dict(dur=1.8, layout="split", clip="lyrics", seg=(1.30, 1.70), speed=1.0,
         html='<div class="cap">Everyone says<br>it means</div>'),
    dict(dur=0.9, layout="host",
         html='<div class="cap"><s>I miss you</s></div>'),
    dict(dur=2.3, layout="split", clip="lyrics", seg=(0.33, 1.67), speed=2.2,
         html='<div class="cap">but that is not<br>what it says</div>'),
    dict(dur=4.0, layout="split", clip="lyrics", seg=(1.80, 3.27), speed=1.0),
    dict(dur=1.0, layout="plate",
         html='<div class="cap"><span class="ko">보 + 고 + 싶</span></div>'),
    dict(dur=2.6, layout="plate",
         html='<div class="cap">see &nbsp;+&nbsp; and<br>+ &nbsp;want to</div>'),
    dict(dur=0.7, layout="host",
         html='<div class="cap">so it is<br>I want to see you</div>'),
    dict(dur=2.6, layout="split", clip="words", seg=(2.40, 4.26), speed=1.0,
         html='<div class="cap">mark what<br>you do not know</div>'),
    dict(dur=2.2, layout="split", clip="quiz", seg=(0.40, 2.00), speed=1.0),
    dict(dur=2.4, layout="host",
         html='<div class="url">sing-korean.vercel.app</div>'),
]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def dur_of(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", p])
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def plate(i, html):
    """자막 한 장을 투명 PNG로. Chrome 은 알파 배경 스크린샷을 지원한다."""
    if not html:
        return None
    css = CAPTION_CSS % {"W": W, "H": H, "TOP": 190, "SIZE": 104, "KOSIZE": 132}
    page = (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style>"
            f"</head><body>{html}</body></html>")
    hp = os.path.join(TMP, f"cap{i:02d}.html")
    open(hp, "w", encoding="utf-8").write(page)
    png = os.path.join(TMP, f"cap{i:02d}.png")
    run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--user-data-dir=/tmp/sk-cap-{i}", "--default-background-color=00000000",
         f"--window-size={W},{H}", "--virtual-time-budget=2500",
         f"--screenshot={png}", f"file://{hp}"])
    return png if os.path.exists(png) else None


def shot(i, s):
    """한 컷을 mp4 로. 레이아웃마다 입력 구성이 달라 분기한다."""
    out = os.path.join(TMP, f"shot{i:02d}.mp4")
    cap = plate(i, s.get("html"))
    d = s["dur"]
    ins, filt = [], []

    if s["layout"] == "host":
        # 느린 줌. 정지 이미지를 그대로 두면 영상이 멈춘 것처럼 보인다.
        ins += ["-loop", "1", "-t", f"{d}", "-i", HOST]
        filt.append(
            f"[0:v]scale={W*1.14:.0f}:-1,crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,"
            f"zoompan=z='min(zoom+0.0006,1.09)':d={int(d*FPS)}:s={W}x{H}:fps={FPS}[base]"
        )
    elif s["layout"] == "plate":
        filt.append(f"color=c=#120B22:s={W}x{H}:d={d}:r={FPS}[base]")
    else:
        a, b = s["seg"]
        clip = os.path.join(REC, f"{s['clip']}.mp4")
        ins += ["-loop", "1", "-t", f"{d}", "-i", HOST,
                "-ss", f"{a}", "-t", f"{(b-a)}", "-i", clip]
        sp = s.get("speed", 1.0)
        filt.append(
            f"[0:v]scale={SPLIT_HOST_W}:-1,"
            f"crop={SPLIT_HOST_W}:{SPLIT_TOP}:0:{SPLIT_FACE_Y},"
            f"pad={W}:{SPLIT_TOP}:(ow-iw)/2:0:color=#120B22,setsar=1[top]"
        )
        filt.append(
            f"[1:v]setpts=PTS/{sp},scale={W}:-1,"
            f"crop={W}:{H-SPLIT_TOP}:0:'min(max(ih-{H-SPLIT_TOP},0),ih*0.24)',"
            f"setsar=1,fps={FPS},tpad=stop_mode=clone:stop_duration=6[bot]"
        )
        filt.append(f"[top][bot]vstack=inputs=2,trim=duration={d},setpts=PTS-STARTPTS[base]")

    if cap:
        ins += ["-loop", "1", "-t", f"{d}", "-i", cap]
        idx = len(ins) // 3 - 1 if s["layout"] == "host" else 2
        idx = 1 if s["layout"] in ("host", "plate") else 2
        if s["layout"] == "plate":
            idx = 0
        filt.append(f"[base][{idx}:v]overlay=0:0:format=auto[v]")
        last = "[v]"
    else:
        last = "[base]"

    r = run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(filt),
             "-map", last, "-t", f"{d}", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", out])
    if not os.path.exists(out):
        print(f"  shot {i} failed:\n{r.stderr[-700:]}")
        return None
    print(f"  shot {i:02d}  {s['layout']:<5} {dur_of(out):.2f}s"
          f"{'  cap' if cap else ''}")
    return out


def music(total):
    bed = os.path.join(TMP, "bed.wav")
    f = (f"sine=frequency=110:duration={total}[a];"
         f"sine=frequency=164.81:duration={total}[b];"
         f"sine=frequency=261.63:duration={total}[c];"
         "[a]volume=0.5[a1];[b]volume=0.32[b1];[c]volume=0.18[c1];"
         "[a1][b1][c1]amix=inputs=3:normalize=0,lowpass=f=820,"
         "tremolo=f=0.25:d=0.28,"
         f"afade=t=in:st=0:d=1.6,afade=t=out:st={max(total-2.4,0):.1f}:d=2.4,"
         "volume=0.45[m]")
    run(["ffmpeg", "-y", "-filter_complex", f, "-map", "[m]",
         "-ar", "44100", "-ac", "2", bed])
    return bed if os.path.exists(bed) else None


def main():
    if not os.path.exists(HOST):
        sys.exit(f"presenter image missing: {HOST}\nSee media/presenter/README.md")
    os.makedirs(TMP, exist_ok=True)

    print(f"{len(SHOTS)} shots")
    clips = [shot(i, s) for i, s in enumerate(SHOTS, 1)]
    clips = [c for c in clips if c]
    if not clips:
        sys.exit("no shots rendered")

    lst = os.path.join(TMP, "concat.txt")
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    silent = os.path.join(TMP, "silent.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", silent])

    total = dur_of(silent)
    bed = music(total)
    if bed:
        run(["ffmpeg", "-y", "-i", silent, "-i", bed, "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT])
    else:
        run(["ffmpeg", "-y", "-i", silent, "-c", "copy", OUT])

    if not os.path.exists(OUT):
        sys.exit("final mux failed")
    print(f"\n{OUT}\n  {dur_of(OUT):.1f}s, {os.path.getsize(OUT)/1024/1024:.1f} MB, {W}x{H}")
    print("  presenter-led, format measured from media/reference/suga")


if __name__ == "__main__":
    main()
