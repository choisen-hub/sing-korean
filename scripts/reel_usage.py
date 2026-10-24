# -*- coding: utf-8 -*-
"""The real-usage Reel: the actual app doing the actual thing, with a caption.

Three earlier attempts led with an idea I invented (static cards, motion
graphics, a culture decode) and all three read as an advert. This one shows the
screens a user really sees, captured from the running app, and lets the captions
stay out of the way.

Same frozen-timeline trick: CSS keyframes over the whole duration, paused at
?t=, captured frame by frame. Music is generated here so there is nothing to
licence; the BTS track goes on inside the Instagram or TikTok editor at upload,
where the platform already holds the rights.

  python3 scripts/reel_usage.py   ->  media/sing-korean-usage.mp4
"""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOTS = os.path.join(ROOT, "media", "shots")
FRAMES = os.path.join(ROOT, "media", "usage_frames")
TMP = os.path.join(ROOT, "media", "_tmp")
HTML = os.path.join(ROOT, "media", "_usage.html")
OUT = os.path.join(ROOT, "media", "sing-korean-usage.mp4")

W, H, FPS = 1080, 1920, 12
DUR = 21.0

# (스크린샷, 캡션, 보조문구)
BEATS = [
    ("r1-words.png",    "Never studied Korean?",            "Start at word number one."),
    ("r1-words.png",    "Every word BTS sings,",            "ranked by how often it is actually sung."),
    ("r2-expand.png",   "Tap one.",                         "The real lyric line it comes from is right there."),
    ("r4-lyrics.png",   "Mark what you don't know.",        "It highlights in every song it appears in."),
    ("r5-quiz.png",     "Then get quizzed on those.",       "Not on buying apples."),
    ("r6-progress.png", "Watch how much you can hear.",     "35 songs. 2,250 lines. Free, no signup."),
]

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#0D0719}
body{font-family:-apple-system,"Helvetica Neue","Apple SD Gothic Neo",sans-serif;color:#F4EFFF}
.stage{position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;
  background-image:radial-gradient(900px 700px at 78%% -6%%,#35205F 0%%,transparent 60%%),
   radial-gradient(760px 600px at -14%% 102%%,#241546 0%%,transparent 56%%)}
.cap{position:absolute;left:72px;right:72px;top:118px;text-align:center;opacity:0}
.cap h3{font-size:72px;font-weight:800;line-height:1.16;letter-spacing:-.02em}
.cap p{font-size:40px;color:#B5A3DC;margin-top:18px;line-height:1.38}
.ph{position:absolute;left:50%%;top:430px;width:640px;margin-left:-320px;
  border-radius:54px;border:9px solid #4A3080;overflow:hidden;background:#120B22;
  box-shadow:0 46px 120px rgba(0,0,0,.72);opacity:0}
.ph img{display:block;width:100%%}
.foot{position:absolute;left:0;right:0;bottom:78px;text-align:center;font-size:40px;color:#D7BFFF}
%(KEYS)s
</style></head><body><div class="stage">
%(BODY)s
<div class="foot">sing-korean.vercel.app</div>
</div><script>
const t=parseFloat(new URLSearchParams(location.search).get('t')||'0');
document.querySelectorAll('*').forEach(el=>{const cs=getComputedStyle(el);
 if(cs.animationName&&cs.animationName!=='none'){el.style.animationDelay=(-t)+'s';el.style.animationPlayState='paused';}});
</script></body></html>"""


def run(c):
    return subprocess.run(c, capture_output=True, text=True)


def dur(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p])
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def build_html():
    n = len(BEATS)
    span = 100.0 / n
    keys, body = [], []
    for i, (shot, head, sub) in enumerate(BEATS):
        a = i * span
        b = a + span
        fi, fo = a + span * .14, b - span * .12
        # 캡션과 폰이 조금 어긋나게 들어와야 슬라이드처럼 보이지 않는다
        keys.append(
            f"@keyframes cap{i}{{0%,{a:.2f}%{{opacity:0;transform:translateY(26px)}}"
            f"{fi:.2f}%,{fo:.2f}%{{opacity:1;transform:none}}{b:.2f}%,100%{{opacity:0}}}}"
            f".cap{i}{{animation:cap{i} {DUR}s linear infinite both}}"
        )
        keys.append(
            f"@keyframes ph{i}{{0%,{a:.2f}%{{opacity:0;transform:scale(.97) translateY(30px)}}"
            f"{fi+1:.2f}%,{fo:.2f}%{{opacity:1;transform:none}}{b:.2f}%,100%{{opacity:0}}}}"
            f".ph{i}{{animation:ph{i} {DUR}s linear infinite both}}"
        )
        p = os.path.join(SHOTS, shot)
        src = f"file://{p}" if os.path.exists(p) else ""
        body.append(
            f'<div class="cap cap{i}"><h3>{head}</h3><p>{sub}</p></div>'
            f'<div class="ph ph{i}"><img src="{src}"></div>'
        )
    html = PAGE % {"W": W, "H": H, "KEYS": "\n".join(keys), "BODY": "\n".join(body)}
    open(HTML, "w", encoding="utf-8").write(html)


def frame(args, tries=3):
    i, t = args
    out = os.path.join(FRAMES, f"{i:04d}.png")
    raw = os.path.join(FRAMES, f".r{i:04d}.png")
    run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--user-data-dir=/tmp/sk-use-{i % 8}", "--force-device-scale-factor=1",
         "--allow-file-access-from-files",
         f"--window-size={W + 400},{H + 400}", "--virtual-time-budget=2600",
         f"--screenshot={raw}", f"file://{HTML}?t={t:.3f}"])
    if not os.path.exists(raw):
        return frame(args, tries - 1) if tries > 1 else None
    Image.open(raw).convert("RGB").crop((0, 0, W, H)).save(out)
    os.unlink(raw)
    return out


def music():
    """자작 음악 베드. 느린 패드 화음에 가벼운 펄스."""
    bed = os.path.join(TMP, "bed_usage.wav")
    # 노이즈 펄스는 지지직거려서 뺐다. 화음 패드만 느리게 움직인다.
    f = (
        f"sine=frequency=110:duration={DUR}[a];"        # A2
        f"sine=frequency=164.81:duration={DUR}[b];"     # E3
        f"sine=frequency=261.63:duration={DUR}[c];"     # C4
        f"sine=frequency=329.63:duration={DUR}[d];"     # E4
        "[a]volume=0.5[a1];[b]volume=0.34[b1];"
        "[c]volume=0.20[c1];[d]volume=0.13[d1];"
        "[a1][b1][c1][d1]amix=inputs=4:normalize=0,"
        "lowpass=f=900,tremolo=f=0.22:d=0.30,"
        f"afade=t=in:st=0:d=2.0,afade=t=out:st={DUR-2.6:.1f}:d=2.6,"
        "volume=0.5[m]"
    )
    run(["ffmpeg", "-y", "-filter_complex", f, "-map", "[m]", "-ar", "44100", "-ac", "2", bed])
    return bed if os.path.exists(bed) else None


def main():
    os.makedirs(FRAMES, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    build_html()
    n = int(DUR * FPS)
    print(f"rendering {n} frames from real app screens")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(frame, [(i, i / FPS) for i in range(n)]))
    last, filled = None, 0
    for i in range(n):
        p = os.path.join(FRAMES, f"{i:04d}.png")
        if os.path.exists(p):
            last = p
        elif last:
            Image.open(last).save(p)
            filled += 1
    print(f"  {n-filled} rendered, {filled} filled")

    silent = os.path.join(TMP, "usage_silent.mp4")
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "%04d.png"),
         "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
         "-r", "30", silent])
    bed = music()
    if bed:
        run(["ffmpeg", "-y", "-i", silent, "-i", bed, "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT])
    else:
        run(["ffmpeg", "-y", "-i", silent, "-c", "copy", OUT])
    if not os.path.exists(OUT):
        sys.exit("encode failed")
    print(f"\n{OUT}\n  {dur(OUT):.1f}s, {os.path.getsize(OUT)/1024/1024:.1f} MB, {W}x{H}, "
          f"generated music bed. Swap in a BTS track inside the platform editor.")


if __name__ == "__main__":
    main()
