# -*- coding: utf-8 -*-
"""Record the live app actually being used, frame by frame.

A headless browser cannot be screen captured, so this does the equivalent: the
app runs inside a fixed-size iframe on a wrapper page, each frame replays the
interaction script up to step N, and the result is screenshotted. Play the
frames in order and you have a real recording of real usage, not a slideshow of
stills.

Interactions are expressed as a timeline of scroll positions and clicks, so a
scroll renders as motion rather than a cut.

Needs the app served locally:  cd app && python3 -m http.server 8799

  python3 scripts/record_app.py            -> media/recordings/<name>.mp4
  python3 scripts/record_app.py --only words
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
OUTDIR = os.path.join(ROOT, "media", "recordings")
BASE = "http://localhost:8799/"

PW, PH = 430, 932
TALL = 5200   # iframe 을 페이지 전체가 들어갈 높이로 띄우고 잘라 쓴다
SCALE = 2
FPS = 15


def ease(a, b, t):
    """부드러운 스크롤. 선형이면 기계가 끈 것처럼 보인다."""
    t = max(0.0, min(1.0, t))
    k = t * t * (3 - 2 * t)
    return a + (b - a) * k


def scroll_run(a, b, frames):
    return [{"scroll": int(ease(a, b, i / max(frames - 1, 1)))} for i in range(frames)]


def hold(scroll, frames, js=""):
    return [{"scroll": scroll, "js": js}] * frames


def tap(scroll, el_js, frames_before=3, frames_ring=5, after_js="", frames_after=10):
    """탭 연출. 링이 퍼지는 프레임을 만들고 그다음 실제 결과를 보여 준다."""
    out = hold(scroll, frames_before)
    for i in range(frames_ring):
        g = 0.55 + (i / max(frames_ring - 1, 1)) * 1.1
        out.append({"scroll": scroll, "js": f"ring(d, {el_js}, grow);", "grow": round(g, 2)})
    out += hold(scroll, frames_after, after_js)
    return out


# 각 장면은 프레임 목록. js 는 캡처 직전에 iframe 안에서 실행된다.
TAKES = {
    # 단어 목록을 훑고, 카드를 펼치고, 모름 표시를 누른다
    "words": {
        "route": "#/words",
        "frames": (
            hold(0, 6)
            + scroll_run(0, 1150, 18)
            + tap(1150, "d.querySelectorAll('.wcard [data-exp]')[1]",
                  after_js="const c=d.querySelectorAll('.wcard [data-exp]')[1]; if(c) c.click();",
                  frames_after=12)
            + tap(1150, "d.querySelectorAll('.wcard')[1].querySelector('[data-known]')",
                  after_js="const cs=d.querySelectorAll('.wcard [data-exp]'); if(cs[1]) cs[1].click();"
                           "const b=d.querySelectorAll('.wcard')[1].querySelector('[data-known]'); if(b) b.click();",
                  frames_after=12)
        ),
    },
    # 가사를 내려 읽다가 단어를 눌러 분해를 띄운다
    "lyrics": {
        "route": "#/song/b01",
        "frames": (
            hold(0, 5)
            + scroll_run(0, 1500, 20)
            + tap(1500, "d.querySelectorAll('.lyrics .w')[3]",
                  after_js="const w=d.querySelectorAll('.lyrics .w')[3]; if(w) w.click();",
                  frames_after=16)
        ),
    },
    # 퀴즈에서 답을 고른다
    "quiz": {
        "route": "#/quiz",
        "frames": (
            hold(0, 8)
            + tap(0, "d.querySelectorAll('#opts .opt')[0]",
                  after_js="const o=d.querySelectorAll('#opts .opt'); if(o[0]) o[0].click();",
                  frames_after=14)
        ),
    },
}


def wrapper_html(route, scroll, js, grow=1.0):
    """프레임 하나. 스크롤은 iframe 안이 아니라 iframe 자체를 밀어서 만든다.

    contentWindow.scrollTo 로는 움직이지 않았다. 가상 시간이 끝나는 시점과
    내부 렌더링 타이밍이 어긋나 전 프레임이 동일하게 나왔다. 대신 iframe 을
    페이지 전체가 들어갈 만큼 길게 띄우고, 430x932 창으로 잘라낸 뒤 iframe 을
    위로 올린다. 렌더된 픽셀을 물리적으로 옮기는 것이라 타이밍을 타지 않는다.
    """
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0}} html,body{{background:#120B22}}
#view{{position:relative;width:{PW}px;height:{PH}px;overflow:hidden;background:#120B22}}
#f{{position:absolute;left:0;top:-{scroll}px;width:{PW}px;height:{TALL}px;border:0;display:block}}
</style></head><body>
<div id="view"><iframe src="{BASE}{route}" id="f" scrolling="no"></iframe></div>
<script>
const f=document.getElementById('f');
let tries=0;
/* 탭한 자리에 링을 남긴다. 없으면 팝업이 저절로 뜬 것처럼 보인다. */
function ring(d, el, grow){{
  if(!el) return;
  const r=el.getBoundingClientRect();
  const n=d.createElement('div');
  const size=Math.max(44, Math.min(r.width+26, 150));
  n.style.cssText=
    'position:absolute;z-index:9999;pointer-events:none;border-radius:999px;'
    +'border:4px solid rgba(255,209,102,.95);box-shadow:0 0 26px 8px rgba(255,209,102,.45);'
    +'left:'+(r.left+d.documentElement.scrollLeft+r.width/2-size/2)+'px;'
    +'top:'+(r.top+d.documentElement.scrollTop+r.height/2-size/2)+'px;'
    +'width:'+size+'px;height:'+size+'px;'
    +'transform:scale('+grow+');opacity:'+(1.05-grow*0.55)+';';
  d.body.appendChild(n);
}}
function go(){{
  let d;
  try{{ d=f.contentDocument; }}catch(e){{ return; }}
  const painted = d && d.querySelector('.wcard, .line, #opts .opt, .songrow');
  if(!painted && tries++ < 90) return setTimeout(go, 110);
  const grow = {grow};
  try{{ {js} }}catch(e){{}}
}}
f.addEventListener('load',()=>setTimeout(go,200));
</script></body></html>"""


def shoot(args):
    name, i, step = args
    import tempfile
    html = wrapper_html(step["route"], step.get("scroll", 0), step.get("js", ""), step.get("grow", 1.0))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        wrap = f.name
    raw = os.path.join(OUTDIR, name, f".r{i:04d}.png")
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        f"--user-data-dir=/tmp/sk-rec-{i % 8}", f"--force-device-scale-factor={SCALE}",
        f"--window-size={PW + 300},{PH + 300}", "--virtual-time-budget=11000",
        f"--screenshot={raw}", f"file://{wrap}",
    ], capture_output=True)
    os.unlink(wrap)
    if not os.path.exists(raw):
        return None
    out = os.path.join(OUTDIR, name, f"{i:04d}.png")
    Image.open(raw).convert("RGB").crop((0, 0, PW * SCALE, PH * SCALE)).save(out)
    os.unlink(raw)
    return out


def record(name, take):
    d = os.path.join(OUTDIR, name)
    os.makedirs(d, exist_ok=True)
    frames = take["frames"]
    jobs = [(name, i, dict(fr, route=take["route"])) for i, fr in enumerate(frames)]
    print(f"{name}: {len(jobs)} frames")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(shoot, jobs))
    last, filled = None, 0
    for i in range(len(jobs)):
        p = os.path.join(d, f"{i:04d}.png")
        if os.path.exists(p):
            last = p
        elif last:
            Image.open(last).save(p)
            filled += 1
    mp4 = os.path.join(OUTDIR, f"{name}.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(d, "%04d.png"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", "30", mp4,
    ], capture_output=True)
    ok = os.path.exists(mp4)
    print(f"  {'wrote' if ok else 'FAILED'} {mp4}"
          f"{f', {filled} frames filled' if filled else ''}")
    return mp4 if ok else None


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    os.makedirs(OUTDIR, exist_ok=True)
    for name, take in TAKES.items():
        if only and name != only:
            continue
        record(name, take)


if __name__ == "__main__":
    main()
