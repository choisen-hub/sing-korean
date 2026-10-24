# -*- coding: utf-8 -*-
"""Capture real screenshots of the running app at an exact phone size.

Headless Chrome lays a page out at a width that does not reliably match
--window-size, which silently produced clipped captures. The fix is to stop
depending on it: load the app inside an iframe of a fixed CSS width on a
wrapper page, give the window extra room, and crop the screenshot to the
iframe box. The iframe is a real viewport, so the app's mobile layout applies
exactly as it would on a phone.

Needs the app served locally:  cd app && python3 -m http.server 8799

  python3 scripts/capture_app.py
"""

import os
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.join(ROOT, "media", "shots")
BASE = "http://localhost:8799/"

PW, PH = 430, 932     # iPhone 15 Pro Max 논리 해상도
SCALE = 2             # 레티나

SHOTS = [
    ("app-tap",    "#/song/b01/0/0-0", "Spring Day, 보고 싶다 분해가 열린 상태"),
    ("app-lyrics", "#/song/b01",       "가사 줄별 보기"),
    ("app-words",  "#/words",          "빈도순 핵심 단어"),
    ("app-quiz",   "#/quiz",           "단어 퀴즈"),
    ("app-word",   "#/word/%EC%82%AC%EB%9E%91", "단어 상세, 실제 가사 예문"),
    ("app-home",   "#/",               "홈"),
]


def capture(name, route, scroll=0, js=""):
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    *{{margin:0;padding:0}} html,body{{background:#120B22}}
    iframe{{width:{PW}px;height:{PH}px;border:0;display:block}}
    </style></head><body>
    <iframe src="{BASE}{route}" id="f"></iframe>
    <script>
      const f=document.getElementById('f');
      f.addEventListener('load',()=>{{
        setTimeout(()=>{{
          try{{
            const d=f.contentDocument, w=f.contentWindow;
            {js}
            w.scrollTo(0,{scroll});
          }}catch(e){{}}
        }},1600);
      }});
    </script></body></html>"""
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        wrapper = f.name

    raw = os.path.join(OUT, f".raw-{name}.png")
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        f"--user-data-dir=/tmp/sk-cap-{name}",
        f"--force-device-scale-factor={SCALE}",
        f"--window-size={PW + 300},{PH + 300}",
        "--virtual-time-budget=16000",
        f"--screenshot={raw}", f"file://{wrapper}",
    ], capture_output=True)
    os.unlink(wrapper)

    if not os.path.exists(raw):
        print(f"  ! {name} failed")
        return None
    im = Image.open(raw).convert("RGB")
    box = (0, 0, PW * SCALE, PH * SCALE)
    if im.size[0] < box[2] or im.size[1] < box[3]:
        print(f"  ! {name} captured {im.size}, need {box[2]}x{box[3]}")
        os.unlink(raw)
        return None
    out = os.path.join(OUT, f"{name}.png")
    im.crop(box).save(out)
    os.unlink(raw)
    print(f"  {name}.png  {PW * SCALE}x{PH * SCALE}")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, route, desc in SHOTS:
        capture(name, route)
    print(f"\n{OUT}")


if __name__ == "__main__":
    main()
