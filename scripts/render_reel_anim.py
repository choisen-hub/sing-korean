# -*- coding: utf-8 -*-
"""Render the Reel as a real animation, frame by frame.

A headless browser cannot be screen recorded, so the timeline is built as CSS
keyframes over the full duration and every element is paused with a negative
animation-delay set from a ?t= parameter. Asking for t=4.25 renders exactly what
the page looks like 4.25 seconds in. Capture that across the timeline and the
frames are a genuine animation rather than a slideshow.

Chrome launches dominate the runtime, so frames render in a process pool.

  python3 scripts/render_reel_anim.py          -> media/reel_anim/*.png + mp4
  python3 scripts/render_reel_anim.py --fps 15
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTDIR = os.path.join(ROOT, "media", "reel_anim")
HTML = os.path.join(ROOT, "media", "_reel.html")
MP4 = os.path.join(ROOT, "media", "sing-korean-reel.mp4")

W, H = 1080, 1920
DUR = 23.0

# 장면 시작 시각. 아래 CSS의 퍼센트는 이 값을 DUR로 나눈 것이다.
PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#120B22}
body{font-family:-apple-system,"Helvetica Neue","Apple SD Gothic Neo",sans-serif;color:#F4EFFF}
.stage{position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;
  background-image:radial-gradient(900px 620px at 82%% -8%%,#3A2270 0%%,transparent 62%%),
    radial-gradient(760px 560px at -12%% 104%%,#271650 0%%,transparent 58%%)}
.glow{position:absolute;inset:0;background:radial-gradient(620px 620px at 50%% 42%%,rgba(179,136,255,.16),transparent 70%%);
  animation:breathe %(DUR)ss linear infinite both}
@keyframes breathe{0%%{opacity:.35}50%%{opacity:.85}100%%{opacity:.35}}
.sc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:0 96px;text-align:center;opacity:0}
.ko{font-size:168px;font-weight:800;letter-spacing:-.03em;line-height:1.1}
.rom{font-size:58px;color:#D7BFFF;font-style:italic;margin-top:18px}
.say{font-size:58px;color:#B5A3DC;line-height:1.42;margin-top:54px}
.say b{color:#F4EFFF;font-weight:800}
h2{font-size:104px;font-weight:800;line-height:1.2;letter-spacing:-.02em}
h2 em{font-style:normal;color:#B388FF}
.strike{position:relative;display:inline-block;color:#7D6AA8}
.strike::after{content:"";position:absolute;left:-14px;right:-14px;top:52%%;height:10px;border-radius:6px;
  background:#B388FF;transform-origin:left center;transform:scaleX(0);
  animation:cut %(DUR)ss linear infinite both}
@keyframes cut{0%%,13%%{transform:scaleX(0)}19%%,100%%{transform:scaleX(1)}}
/* 단어가 갈라지는 장면 */
.split{display:flex;gap:0;align-items:flex-start;justify-content:center}
.pz{display:flex;flex-direction:column;align-items:center;animation:none}
.pz .g{font-size:190px;font-weight:800;line-height:1}
.pz .m{font-size:46px;color:#D7BFFF;margin-top:26px;opacity:0;white-space:nowrap}
.pz.a{animation:spA %(DUR)ss linear infinite both}
.pz.b{animation:spB %(DUR)ss linear infinite both}
.pz.c{animation:spC %(DUR)ss linear infinite both}
@keyframes spA{0%%,26%%{transform:translateX(0)}35%%,100%%{transform:translateX(-170px)}}
@keyframes spB{0%%,26%%{transform:translateX(0)}35%%,100%%{transform:translateX(0)}}
@keyframes spC{0%%,26%%{transform:translateX(0)}35%%,100%%{transform:translateX(170px)}}
.m1{animation:mi1 %(DUR)ss linear infinite both}
.m2{animation:mi2 %(DUR)ss linear infinite both}
.m3{animation:mi3 %(DUR)ss linear infinite both}
@keyframes mi1{0%%,37%%{opacity:0;transform:translateY(16px)}42%%,100%%{opacity:1;transform:none}}
@keyframes mi2{0%%,42%%{opacity:0;transform:translateY(16px)}47%%,100%%{opacity:1;transform:none}}
@keyframes mi3{0%%,47%%{opacity:0;transform:translateY(16px)}52%%,100%%{opacity:1;transform:none}}
.lift{animation:lift %(DUR)ss linear infinite both}
@keyframes lift{0%%,52%%{transform:translateY(0) scale(1)}60%%,100%%{transform:translateY(-150px) scale(.78)}}
.pattern{position:absolute;left:96px;right:96px;top:1080px;display:grid;gap:26px}
.pr{display:flex;align-items:baseline;gap:30px;border-left:9px solid #B388FF;padding:22px 0 22px 30px;
  background:rgba(179,136,255,.09);border-radius:0 20px 20px 0;opacity:0}
.pr .x{font-size:72px;font-weight:800}
.pr .y{font-size:44px;color:#B5A3DC}
.r1{animation:pin1 %(DUR)ss linear infinite both}
.r2{animation:pin2 %(DUR)ss linear infinite both}
.r3{animation:pin3 %(DUR)ss linear infinite both}
@keyframes pin1{0%%,61%%{opacity:0;transform:translateX(-50px)}65%%,100%%{opacity:1;transform:none}}
@keyframes pin2{0%%,65%%{opacity:0;transform:translateX(-50px)}69%%,100%%{opacity:1;transform:none}}
@keyframes pin3{0%%,69%%{opacity:0;transform:translateX(-50px)}73%%,100%%{opacity:1;transform:none}}
/* 장면 전환 */
.s1{animation:sh1 %(DUR)ss linear infinite both}
.s2{animation:sh2 %(DUR)ss linear infinite both}
.s3{animation:sh3 %(DUR)ss linear infinite both}
.s4{animation:sh4 %(DUR)ss linear infinite both}
@keyframes sh1{0%%{opacity:0;transform:scale(1.08)}3%%,11%%{opacity:1;transform:scale(1)}14%%,100%%{opacity:0}}
@keyframes sh2{0%%,12%%{opacity:0}15%%,22%%{opacity:1}25%%,100%%{opacity:0}}
@keyframes sh3{0%%,23%%{opacity:0}26%%,76%%{opacity:1}79%%,100%%{opacity:0}}
@keyframes sh4{0%%,78%%{opacity:0;transform:translateY(40px)}82%%,100%%{opacity:1;transform:none}}
.phone{width:620px;border-radius:52px;border:10px solid #452C7D;overflow:hidden;
  box-shadow:0 40px 120px rgba(0,0,0,.65);background:#120B22}
.phone img{display:block;width:100%%}
.url{margin-top:52px;font-size:52px;color:#D7BFFF;border:4px solid rgba(179,136,255,.5);
  border-radius:999px;padding:24px 48px}
.tag{position:absolute;bottom:92px;left:0;right:0;font-size:38px;color:#7D6AA8}
</style></head><body>
<div class="stage">
  <div class="glow"></div>

  <div class="sc s1">
    <div class="ko">보고 싶다</div>
    <div class="rom">bogo sipta</div>
    <div class="say">You have sung this.<br><b>You don't know what it says.</b></div>
  </div>

  <div class="sc s2">
    <h2>Everyone says<br>it means<br><span class="strike">I miss you</span></h2>
    <div class="say">That is the translation.<br><b>Not what the words say.</b></div>
  </div>

  <div class="sc s3">
    <div class="lift">
      <div class="split">
        <div class="pz a"><div class="g">보</div><div class="m m1">to see</div></div>
        <div class="pz b"><div class="g">고</div><div class="m m2">and</div></div>
        <div class="pz c"><div class="g">싶</div><div class="m m3">want to</div></div>
      </div>
    </div>
    <div class="pattern">
      <div class="pr r1"><span class="x">보고 싶다</span><span class="y">I want to see you</span></div>
      <div class="pr r2"><span class="x">먹고 싶다</span><span class="y">I want to eat</span></div>
      <div class="pr r3"><span class="x">가고 싶다</span><span class="y">I want to go</span></div>
    </div>
    <div class="tag">one word, three pieces, one pattern</div>
  </div>

  <div class="sc s4">
    <div class="phone"><img src="PHONE_SRC"></div>
    <div class="say" style="margin-top:46px">35 BTS songs.<br><b>Tap any word, it falls apart.</b></div>
    <div class="url">sing-korean.vercel.app</div>
  </div>
</div>
<script>
/* ?t=초 를 받아 모든 애니메이션을 그 시각에 정지시킨다. */
const t = parseFloat(new URLSearchParams(location.search).get('t') || '0');
document.querySelectorAll('*').forEach(el => {
  const cs = getComputedStyle(el);
  if (cs.animationName && cs.animationName !== 'none') {
    el.style.animationDelay = (-t) + 's';
    el.style.animationPlayState = 'paused';
  }
});
</script></body></html>"""


def build_html():
    shot = os.path.join(ROOT, "media", "shots", "app-tap.png")
    src = f"file://{shot}" if os.path.exists(shot) else ""
    html = PAGE % {"W": W, "H": H, "DUR": DUR}
    html = html.replace("PHONE_SRC", src)
    os.makedirs(os.path.dirname(HTML), exist_ok=True)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)


def frame(args, _tries=3):
    """한 프레임. Chrome이 간헐적으로 빈손으로 끝나므로 재시도한다.
    프레임이 하나라도 비면 ffmpeg의 image2 입력이 거기서 끊긴다."""
    i, t = args
    out = os.path.join(OUTDIR, f"{i:04d}.png")
    raw = os.path.join(OUTDIR, f".r{i:04d}.png")
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        f"--user-data-dir=/tmp/sk-anim-{i % 8}", "--force-device-scale-factor=1",
        "--allow-file-access-from-files",
        f"--window-size={W + 400},{H + 400}", "--virtual-time-budget=1800",
        f"--screenshot={raw}", f"file://{HTML}?t={t:.3f}",
    ], capture_output=True)
    if not os.path.exists(raw):
        if _tries > 1:
            return frame(args, _tries - 1)
        return None
    Image.open(raw).convert("RGB").crop((0, 0, W, H)).save(out)
    os.unlink(raw)
    return out


def main():
    fps = 12
    if "--fps" in sys.argv:
        fps = int(sys.argv[sys.argv.index("--fps") + 1])
    os.makedirs(OUTDIR, exist_ok=True)
    build_html()

    n = int(DUR * fps)
    jobs = [(i, i / fps) for i in range(n)]
    print(f"rendering {n} frames at {fps} fps ({DUR}s)")
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(frame, jobs):
            done += 1 if r else 0
            if done % 24 == 0:
                print(f"  {done}/{n}")
    print(f"  {done}/{n} frames")

    # 그래도 빠진 자리가 있으면 직전 프레임으로 메운다. 12 fps에서 한 장은
    # 눈에 띄지 않고, 비워 두면 영상이 그 지점에서 잘린다.
    filled = 0
    last = None
    for i in range(n):
        p_i = os.path.join(OUTDIR, f"{i:04d}.png")
        if os.path.exists(p_i):
            last = p_i
        elif last:
            Image.open(last).save(p_i)
            filled += 1
    if filled:
        print(f"  filled {filled} dropped frames from their neighbour")

    r = subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(OUTDIR, "%04d.png"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "30", MP4,
    ], capture_output=True, text=True)
    if not os.path.exists(MP4):
        sys.exit("ffmpeg failed:\n" + r.stderr[-1000:])
    size = os.path.getsize(MP4) / 1024 / 1024
    print(f"\n{MP4}\n  {DUR}s, {size:.1f} MB, {W}x{H}, no narration "
          f"(add platform audio at upload)")


if __name__ == "__main__":
    main()
