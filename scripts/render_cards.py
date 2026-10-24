# -*- coding: utf-8 -*-
"""Render Instagram carousel slides and Reel frames as real image files.

Headless Chrome lays a page out at a width that does not match --window-size
reliably, so nothing here depends on that. Each card is drawn inside a div of
an exact pixel size at the top left, the window is given extra room, and the
screenshot is cropped to the exact box afterwards. That makes the output size
guaranteed rather than hopeful.

  python3 scripts/render_cards.py carousel   -> media/carousel/01..08.png  1080x1350
  python3 scripts/render_cards.py reel       -> media/reel/f01..fNN.png    1080x1920
"""

import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BG = "#120B22"
PUR = "#B388FF"
PUR2 = "#D7BFFF"
INK = "#F4EFFF"
MUT = "#B5A3DC"
DIM = "#7D6AA8"
OK = "#7FDB8E"

CSS = f"""
@font-face{{font-family:x}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#000}}
.card{{position:relative;overflow:hidden;background:{BG};color:{INK};
  font-family:-apple-system,"Helvetica Neue","Apple SD Gothic Neo",sans-serif;
  background-image:radial-gradient(900px 600px at 80% -10%,#331F63 0%,transparent 62%),
    radial-gradient(700px 520px at -10% 100%,#241546 0%,transparent 58%);
  display:flex;flex-direction:column;justify-content:center;padding:96px 84px}}
.kicker{{font-size:30px;letter-spacing:.18em;text-transform:uppercase;color:{DIM};margin-bottom:34px}}
h1{{font-size:88px;line-height:1.16;font-weight:800;letter-spacing:-.01em}}
h1 em{{font-style:normal;color:{PUR}}}
.ko{{font-size:124px;line-height:1.2;font-weight:700;letter-spacing:-.02em}}
.rom{{font-size:46px;color:{PUR2};font-style:italic;margin-top:14px}}
p{{font-size:44px;line-height:1.5;color:{MUT};margin-top:30px}}
p b{{color:{INK};font-weight:700}}
.pieces{{display:flex;gap:22px;margin-top:46px;flex-wrap:wrap}}
.pc{{background:rgba(179,136,255,.13);border:3px solid rgba(179,136,255,.5);
  border-radius:26px;padding:26px 34px;min-width:190px}}
.pc .p1{{font-size:70px;font-weight:700}}
.pc .p2{{font-size:32px;color:{PUR2};margin-top:8px}}
.rows{{margin-top:44px;display:grid;gap:22px}}
.rw{{display:flex;gap:26px;align-items:baseline;border-left:7px solid {PUR};
  padding:18px 0 18px 26px;background:rgba(179,136,255,.07);border-radius:0 18px 18px 0}}
.rw .a{{font-size:60px;font-weight:700;min-width:170px}}
.rw .b{{font-size:38px;color:{MUT}}}
.big{{font-size:150px;font-weight:800;color:{PUR};line-height:1}}
.foot{{position:absolute;left:84px;right:84px;bottom:66px;display:flex;
  justify-content:space-between;align-items:center;font-size:30px;color:{DIM}}}
.foot b{{color:{PUR2}}}
.pill{{display:inline-block;border:3px solid rgba(179,136,255,.45);border-radius:999px;
  padding:14px 30px;font-size:32px;color:{PUR2};margin-top:34px}}
.strike{{position:relative;display:inline-block;color:{DIM}}}
.strike::after{{content:"";position:absolute;left:-8px;right:-8px;top:52%;height:7px;
  background:{PUR};border-radius:4px;transform:rotate(-2deg)}}
"""


def render(cards, outdir, w, h, prefix):
    os.makedirs(outdir, exist_ok=True)
    made = []
    for i, body in enumerate(cards, 1):
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}
        .card{{width:{w}px;height:{h}px}}</style></head><body>
        <div class="card">{body}</div></body></html>"""
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html)
            path = f.name
        raw = os.path.join(outdir, f".raw{i:02d}.png")
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            f"--user-data-dir=/tmp/sk-card-{i}", "--force-device-scale-factor=1",
            f"--window-size={w + 420},{h + 420}", "--virtual-time-budget=3000",
            f"--screenshot={raw}", f"file://{path}",
        ], capture_output=True)
        os.unlink(path)
        if not os.path.exists(raw):
            print(f"  ! slide {i} failed to render")
            continue
        im = Image.open(raw).convert("RGB")
        if im.size[0] < w or im.size[1] < h:
            im = im.resize((max(im.size[0], w), max(im.size[1], h)))
        out = os.path.join(outdir, f"{prefix}{i:02d}.png")
        im.crop((0, 0, w, h)).save(out)
        os.unlink(raw)
        made.append(out)
        print(f"  {os.path.basename(out)}  {w}x{h}")
    return made


def piece(a, b):
    return f'<div class="pc"><div class="p1">{a}</div><div class="p2">{b}</div></div>'


FOOT = '<div class="foot"><span>sing-korean.vercel.app</span><span><b>Sing Korean</b></span></div>'

CAROUSEL = [
    f'<div class="kicker">Spring Day</div><h1>You have screamed <em>보고 싶다</em> at a concert.<br>Do you know what you said?</h1>{FOOT}',
    f'<h1>Everyone says it means<br><span class="strike">I miss you</span></h1><p>That is the translation. It is not what the words say.</p>{FOOT}',
    f'<div class="ko">보고 싶다</div><div class="rom">bogo sipta</div><p>Three pieces, not one word.</p>'
    f'<div class="pieces">{piece("보","to see")}{piece("고","and")}{piece("싶","want to")}</div>{FOOT}',
    f'<div class="kicker">Piece 1</div><div class="ko">보</div><div class="rom">bo</div>'
    f'<p><b>to see, to look.</b> The same 보 you already know from 보여 (it shows) and 봐 (look).</p>{FOOT}',
    f'<div class="kicker">Piece 2</div><div class="ko">고</div><div class="rom">go</div>'
    f'<p><b>and.</b> It glues two verbs together. That is the entire job.</p>{FOOT}',
    f'<div class="kicker">Piece 3</div><div class="ko">싶</div><div class="rom">sip</div>'
    f'<p><b>want to.</b> It only ever shows up after a verb with 고 in front of it.</p>{FOOT}',
    f'<h1>So in Korean,<br><em>I miss you</em> is literally<br>I want to see you.</h1>'
    f'<div class="rows">'
    f'<div class="rw"><span class="a">먹고 싶다</span><span class="b">I want to eat</span></div>'
    f'<div class="rw"><span class="a">가고 싶다</span><span class="b">I want to go</span></div>'
    f'<div class="rw"><span class="a">하고 싶다</span><span class="b">I want to do it</span></div>'
    f'</div><p>You did not learn a phrase. You learned a pattern.</p>{FOOT}',
    f'<h1>35 BTS songs,<br>broken down <em>like this</em>.</h1>'
    f'<p>Tap any word and it falls apart into its pieces, with the grammar spelled out. '
    f'Free, no signup, works on your phone.</p><div class="pill">sing-korean.vercel.app</div>{FOOT}',
]

REEL = [
    f'<div class="ko" style="font-size:168px">보고 싶다</div><div class="rom" style="font-size:54px">bogo sipta</div>'
    f'<p style="font-size:52px;margin-top:60px">You have sung this.<br>You do not know what it says.</p>',
    f'<h1 style="font-size:104px">Everyone tells you<br>it means<br><span class="strike">I miss you</span></h1>',
    f'<h1 style="font-size:96px">That is the translation.<br><em>Not what the words say.</em></h1>',
    f'<div class="ko" style="font-size:150px">보고 싶다</div>'
    f'<div class="pieces" style="margin-top:70px">{piece("보","")}{piece("고","")}{piece("싶","")}</div>'
    f'<p style="font-size:56px;margin-top:60px">Three pieces.</p>',
    f'<div class="big">보</div><div class="rom" style="font-size:56px">bo</div>'
    f'<h1 style="font-size:96px;margin-top:30px">to see</h1>',
    f'<div class="big">고</div><div class="rom" style="font-size:56px">go</div>'
    f'<h1 style="font-size:96px;margin-top:30px">and</h1>'
    f'<p style="font-size:46px">that is all it does</p>',
    f'<div class="big">싶</div><div class="rom" style="font-size:56px">sip</div>'
    f'<h1 style="font-size:96px;margin-top:30px">want to</h1>',
    f'<h1 style="font-size:92px">So you did not learn<br>a phrase.<br><em>You learned a pattern.</em></h1>'
    f'<div class="rows">'
    f'<div class="rw"><span class="a" style="font-size:66px">먹고 싶다</span><span class="b" style="font-size:42px">I want to eat</span></div>'
    f'<div class="rw"><span class="a" style="font-size:66px">가고 싶다</span><span class="b" style="font-size:42px">I want to go</span></div>'
    f'</div>',
    f'<h1 style="font-size:100px">BTS opens Spring Day<br>with it. <em>Twice.</em></h1>'
    f'<p style="font-size:50px">35 songs broken down like this.<br>Free. No signup.</p>'
    f'<div class="pill" style="font-size:46px;padding:22px 44px">sing-korean.vercel.app</div>',
]

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "carousel"
    if what == "carousel":
        print("carousel 1080x1350")
        render(CAROUSEL, os.path.join(ROOT, "media", "carousel"), 1080, 1350, "slide")
    else:
        print("reel frames 1080x1920")
        render(REEL, os.path.join(ROOT, "media", "reel"), 1080, 1920, "f")
