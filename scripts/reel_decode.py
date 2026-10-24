# -*- coding: utf-8 -*-
"""The decode Reel: one line nobody outside Korea understood, revealed.

Positioning second pass. The hook is not the grammar, it is the gap: a line the
fan has sung for years that says something they could not see. 포도 in MIC Drop
is the cleanest example, self contained and provably invisible in every English
translation.

Built the same way as the animated reel: a CSS timeline frozen at ?t= and
captured frame by frame. On top of that this one mixes audio, because a bare
synthetic voice reads as cheap while the same voice sitting on a music bed reads
as an ordinary social video. The bed is generated here, so there is nothing to
licence.

  python3 scripts/reel_decode.py            -> media/sing-korean-decode.mp4
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
FRAMES = os.path.join(ROOT, "media", "decode_frames")
TMP = os.path.join(ROOT, "media", "_tmp")
HTML = os.path.join(ROOT, "media", "_decode.html")
OUT = os.path.join(ROOT, "media", "sing-korean-decode.mp4")
SHOT = os.path.join(ROOT, "media", "shots", "app-lyrics.png")

W, H, FPS = 1080, 1920, 12
DUR = 23.0

# (장면 시작, 끝, 내레이션). 끝 시각은 CSS 퍼센트와 맞춰 둔다.
SCRIPT = [
    (0.0, 3.6, "MIC Drop has a line about grapes."),
    (3.6, 7.2, "Every English translation says: grape."),
    (7.2, 12.4, "In Korea, grape is ticketing slang. Unsold seats show up as purple dots on the seat map."),
    (12.4, 16.6, "So a chart full of grapes is a show that did not sell."),
    (16.6, 19.6, "The line is a brag. Our concerts never have grapes."),
    (19.6, 23.0, "Thirty five songs, decoded the way a Korean hears them."),
]

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#120B22}
body{font-family:-apple-system,"Helvetica Neue","Apple SD Gothic Neo",sans-serif;color:#F4EFFF}
.stage{position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;
  background-image:radial-gradient(940px 640px at 80%% -8%%,#3A2270 0%%,transparent 62%%),
    radial-gradient(780px 560px at -12%% 104%%,#271650 0%%,transparent 58%%)}
.sc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:0 90px;text-align:center;opacity:0}
.lyric{font-size:66px;font-weight:700;line-height:1.35}
.lyric em{font-style:normal;color:#FFD166}
.rom{font-size:40px;color:#D7BFFF;font-style:italic;margin-top:18px}
h2{font-size:96px;font-weight:800;line-height:1.18;letter-spacing:-.02em}
h2 em{font-style:normal;color:#B388FF}
.say{font-size:50px;color:#B5A3DC;line-height:1.45;margin-top:46px}
.say b{color:#F4EFFF;font-weight:800}
.big{font-size:230px;font-weight:800;line-height:1;color:#FFD166}
.strike{position:relative;display:inline-block;color:#7D6AA8}
.strike::after{content:"";position:absolute;left:-14px;right:-14px;top:52%%;height:10px;border-radius:6px;
  background:#FFD166;transform-origin:left center;transform:scaleX(0);
  animation:cut %(DUR)ss linear infinite both}
@keyframes cut{0%%,20%%{transform:scaleX(0)}27%%,100%%{transform:scaleX(1)}}
/* 좌석도: 빈자리가 보라색 점으로 차오른다 */
.map{width:720px;padding:34px;border-radius:28px;border:4px solid #452C7D;background:rgba(18,11,34,.72)}
.seats{display:grid;grid-template-columns:repeat(16,1fr);gap:11px}
.seats i{width:100%%;aspect-ratio:1;border-radius:4px;background:#2F1C5C}
.seats i.p{background:#B388FF;box-shadow:0 0 12px rgba(179,136,255,.7);
  animation:pop %(DUR)ss linear infinite both}
@keyframes pop{0%%,34%%{opacity:0;transform:scale(.4)}40%%,100%%{opacity:1;transform:none}}
.maplab{font-size:34px;color:#B5A3DC;margin-top:26px}
.maplab b{color:#B388FF}
.eq{font-size:56px;font-weight:800;line-height:1.3}
.eq .a{color:#FFD166}.eq .b{color:#B388FF}
.phone{width:560px;border-radius:48px;border:10px solid #452C7D;overflow:hidden;
  box-shadow:0 40px 110px rgba(0,0,0,.7);background:#120B22}
.phone img{display:block;width:100%%}
.url{margin-top:44px;font-size:48px;color:#D7BFFF;border:4px solid rgba(179,136,255,.5);
  border-radius:999px;padding:22px 44px}
.s1{animation:a1 %(DUR)ss linear infinite both}
.s2{animation:a2 %(DUR)ss linear infinite both}
.s3{animation:a3 %(DUR)ss linear infinite both}
.s4{animation:a4 %(DUR)ss linear infinite both}
.s5{animation:a5 %(DUR)ss linear infinite both}
.s6{animation:a6 %(DUR)ss linear infinite both}
@keyframes a1{0%%{opacity:0;transform:scale(1.07)}3%%,13%%{opacity:1;transform:none}16%%,100%%{opacity:0}}
@keyframes a2{0%%,14%%{opacity:0}17%%,29%%{opacity:1}32%%,100%%{opacity:0}}
@keyframes a3{0%%,30%%{opacity:0}33%%,51%%{opacity:1}54%%,100%%{opacity:0}}
@keyframes a4{0%%,52%%{opacity:0}55%%,70%%{opacity:1}73%%,100%%{opacity:0}}
@keyframes a5{0%%,71%%{opacity:0}74%%,83%%{opacity:1}86%%,100%%{opacity:0}}
@keyframes a6{0%%,84%%{opacity:0;transform:translateY(40px)}88%%,100%%{opacity:1;transform:none}}
</style></head><body><div class="stage">

  <div class="sc s1">
    <div class="lyric">우리 콘서트 절대 없어 <em>포도</em></div>
    <div class="rom">uri konseoteu jeoldae eopseo podo</div>
    <div class="say">MIC Drop, 2017.<br><b>There is a line about grapes.</b></div>
  </div>

  <div class="sc s2">
    <div class="big">포도</div>
    <h2 style="margin-top:30px"><span class="strike">grape</span></h2>
    <div class="say">That is what every English version says.</div>
  </div>

  <div class="sc s3">
    <div class="map">
      <div class="seats">%(SEATS)s</div>
      <div class="maplab">Korean ticket sites show an <b>unsold seat</b> as a purple dot</div>
    </div>
    <div class="say">Fans called a seat map full of them <b>a bunch of grapes</b>.</div>
  </div>

  <div class="sc s4">
    <div class="eq">포도 <span class="a">=</span> empty seats<br><span class="b">no grapes</span> = sold out</div>
    <div class="say">So the line is not about fruit.</div>
  </div>

  <div class="sc s5">
    <div class="lyric">우리 콘서트 절대 없어 <em>포도</em></div>
    <div class="say"><b>Our concerts never have empty seats.</b><br>You have been singing a brag you could not see.</div>
  </div>

  <div class="sc s6">
    <div class="phone"><img src="PHONE_SRC"></div>
    <div class="say" style="margin-top:40px">35 BTS songs, decoded<br><b>the way a Korean hears them.</b></div>
    <div class="url">sing-korean.vercel.app</div>
  </div>

</div><script>
const t=parseFloat(new URLSearchParams(location.search).get('t')||'0');
document.querySelectorAll('*').forEach(el=>{const cs=getComputedStyle(el);
  if(cs.animationName&&cs.animationName!=='none'){el.style.animationDelay=(-t)+'s';el.style.animationPlayState='paused';}});
</script></body></html>"""


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path])
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def build_html():
    import random
    random.seed(7)
    seats = "".join(
        f'<i class="p" style="animation-delay:{-0 + random.random() * 0.9:.2f}s"></i>'
        if random.random() < 0.42 else "<i></i>"
        for _ in range(16 * 9)
    )
    html = PAGE % {"W": W, "H": H, "DUR": DUR, "SEATS": seats}
    html = html.replace("PHONE_SRC", f"file://{SHOT}" if os.path.exists(SHOT) else "")
    open(HTML, "w", encoding="utf-8").write(html)


def frame(args, tries=3):
    i, t = args
    out = os.path.join(FRAMES, f"{i:04d}.png")
    raw = os.path.join(FRAMES, f".r{i:04d}.png")
    run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--user-data-dir=/tmp/sk-dec-{i % 8}", "--force-device-scale-factor=1",
         "--allow-file-access-from-files",
         f"--window-size={W + 400},{H + 400}", "--virtual-time-budget=2200",
         f"--screenshot={raw}", f"file://{HTML}?t={t:.3f}"])
    if not os.path.exists(raw):
        return frame(args, tries - 1) if tries > 1 else None
    Image.open(raw).convert("RGB").crop((0, 0, W, H)).save(out)
    os.unlink(raw)
    return out


def narration():
    """장면마다 음성을 만들고 지정된 시작 시각에 배치한다."""
    parts = []
    for i, (t0, t1, line) in enumerate(SCRIPT):
        aiff = os.path.join(TMP, f"n{i}.aiff")
        run(["say", "-v", "Samantha", "-r", "178", "-o", aiff, line])
        if not os.path.exists(aiff):
            continue
        wav = os.path.join(TMP, f"n{i}.wav")
        # 살짝 낮추면 합성음 특유의 날카로움이 줄어든다
        run(["ffmpeg", "-y", "-i", aiff, "-af",
             "asetrate=22050*0.96,aresample=44100,atempo=1.04,highpass=f=90,"
             "acompressor=threshold=-18dB:ratio=3,volume=1.6",
             "-ar", "44100", "-ac", "2", wav])
        parts.append((t0, wav))
    if not parts:
        return None
    # 각 음성을 시작 시각만큼 지연시켜 한 트랙으로 합친다
    ins, filt = [], []
    for k, (t0, wav) in enumerate(parts):
        ins += ["-i", wav]
        filt.append(f"[{k}:a]adelay={int(t0*1000)}|{int(t0*1000)}[d{k}]")
    mix = "".join(f"[d{k}]" for k in range(len(parts)))
    filt.append(f"{mix}amix=inputs={len(parts)}:normalize=0[v]")
    voice = os.path.join(TMP, "voice.wav")
    run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[v]",
         "-t", str(DUR), voice])
    return voice if os.path.exists(voice) else None


def music():
    """생성한 음악 베드. 낮은 패드 두 겹에 네 박자 펄스."""
    bed = os.path.join(TMP, "bed.wav")
    f = (
        "sine=frequency=110:duration=%0.1f[a];"
        "sine=frequency=164.81:duration=%0.1f[b];"
        "sine=frequency=220:duration=%0.1f[c];"
        "anoisesrc=d=%0.1f:c=pink:a=0.06[n];"
        "[a][b][c]amix=inputs=3:normalize=0,lowpass=f=420,"
        "tremolo=f=0.5:d=0.35,volume=0.16[pad];"
        "[n]bandpass=f=1800:w=900,tremolo=f=2:d=0.9,volume=0.5[tick];"
        "[pad][tick]amix=inputs=2:normalize=0,"
        "afade=t=in:st=0:d=1.2,afade=t=out:st=%0.1f:d=1.8,volume=0.5[m]"
    ) % (DUR, DUR, DUR, DUR, DUR - 1.8)
    run(["ffmpeg", "-y", "-filter_complex", f, "-map", "[m]", "-ar", "44100", "-ac", "2", bed])
    return bed if os.path.exists(bed) else None


def main():
    os.makedirs(FRAMES, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    build_html()

    n = int(DUR * FPS)
    print(f"rendering {n} frames")
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
    print(f"  {n - filled} rendered, {filled} filled from neighbours")

    voice = narration()
    bed = music()
    print(f"  voice {'ok' if voice else 'missing'}, music {'ok' if bed else 'missing'}")

    silent = os.path.join(TMP, "silent.mp4")
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "%04d.png"),
         "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
         "-r", "30", silent])

    if voice and bed:
        # 음악은 내레이션 밑으로 깔리게 사이드체인으로 눌러 준다
        run(["ffmpeg", "-y", "-i", silent, "-i", voice, "-i", bed,
             "-filter_complex",
             "[2:a][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=8:release=320[duck];"
             "[1:a][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", OUT])
    else:
        run(["ffmpeg", "-y", "-i", silent, "-c", "copy", OUT])

    if not os.path.exists(OUT):
        sys.exit("encode failed")
    print(f"\n{OUT}\n  {dur(OUT):.1f}s, {os.path.getsize(OUT)/1024/1024:.1f} MB, "
          f"{W}x{H}, narration + generated music bed")


if __name__ == "__main__":
    main()
