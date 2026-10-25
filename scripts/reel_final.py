# -*- coding: utf-8 -*-
"""The whole reel: narration, real app footage, synced captions and music.

An earlier version put an animated presenter in front, copying the reference
format. It was wrong twice. A still photo with a stretched mouth sits squarely
in the uncanny valley, and more importantly the reference needs a presenter
because the presenter is the content there, a person reacting. What we have is
a product doing something, so the product should carry the frame and a face
pasted over it only reads as fake.

What the reference still gives us is everything else: caption style, the mix of
long explanation shots and sub-second punches, a label box naming the subject
in the opening, and adding nothing the format does not already have.

Narration is built first and its measured length sets each shot's duration, so
cuts and captions land on the words rather than on a guessed grid.

  python3 scripts/reel_final.py
  python3 scripts/reel_final.py --fast     # 15 fps puppet, for checking timing
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MEDIA = os.path.join(ROOT, "media")
REC = os.path.join(MEDIA, "recordings")
TMP = os.path.join(MEDIA, "_final")
HOST = os.path.join(MEDIA, "presenter", "presenter.png")
OUT = os.path.join(MEDIA, "sing-korean-final.mp4")

W, H, FPS = 1080, 1920, 30
TOPBAND = 640      # 자막이 앉을 조용한 띠. 앱 화면은 그 아래로 밀어 넣는다
SPLIT_HOST_W = 780
SPLIT_FACE_Y = 275
VOICE = "Samantha"
RATE = 170
TAIL = 0.34          # 말이 끝난 뒤 글자를 읽을 여유

sys.path.insert(0, HERE)

# narration 이 그 컷의 길이를 정한다. layout 과 clip 은 reel_hosted 와 같은 뜻.
SHOTS = [
    dict(say="You have sung this line a hundred times.", layout="plate",
         html='<div class="hero"><span class="ko">보고 싶다</span>'
              '<span class="rom">bogo sipta</span></div>'),
    dict(say="Everyone tells you it means, I miss you.", layout="clip",
         clip="lyrics", seg=(1.05, 1.70),
         html='<div class="cap">Everyone says<br>it means</div>'),
    dict(say="That is the translation.", layout="plate",
         html='<div class="cap"><s>I miss you</s></div>'),
    dict(say="It is not what the words say.", layout="clip",
         clip="lyrics", seg=(0.33, 1.67), speed=2.0,
         html='<div class="cap">not what<br>the words say</div>'),
    dict(say="Tap it, and it comes apart.", layout="clip",
         clip="lyrics", seg=(1.80, 3.27),
         html='<div class="cap">tap it</div>'),
    dict(say="Bo, to see. Go, and. Ship, want to.", layout="plate",
         html='<div class="cap"><span class="ko">보 + 고 + 싶</span><br>'
              '<span style="font-size:70px">see &nbsp;+&nbsp; and &nbsp;+&nbsp; want to</span></div>'),
    dict(say="So I miss you is really I want to see you.", layout="plate",
         html='<div class="cap">I want<br>to see you</div>'),
    dict(say="Learn the pattern and you get the rest for free.", layout="plate",
         html='<div class="cap"><span class="ko">먹고 싶다</span>'
              '<br><span style="font-size:62px">I want to eat</span><br><br>'
              '<span class="ko">가고 싶다</span>'
              '<br><span style="font-size:62px">I want to go</span></div>'),
    dict(say="Mark any word you do not know.", layout="clip",
         clip="words", seg=(2.30, 4.26),
         html='<div class="cap">mark what<br>you do not know</div>'),
    dict(say="Then the quiz asks you only those.", layout="clip",
         clip="quiz", seg=(0.40, 2.00),
         html='<div class="cap">quizzed on<br>exactly those</div>'),
    dict(say="Thirty five BTS songs. Free, no signup.", layout="plate",
         html='<div class="cap" style="font-size:86px">35 BTS songs<br>'
              'word by word</div><div class="url">sing-korean.vercel.app</div>'),
]

CAPTION_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent;width:%(W)dpx;height:%(H)dpx;
  font-family:-apple-system,"Helvetica Neue","Apple SD Gothic Neo",sans-serif}
.cap{position:absolute;left:60px;right:60px;top:130px;height:460px;
  display:flex;flex-direction:column;justify-content:center;text-align:center;
  font-weight:800;font-size:96px;line-height:1.14;letter-spacing:-.01em;
  color:#fff;-webkit-text-stroke:14px #000;paint-order:stroke fill}
.cap .ko{font-size:126px}
.cap s{text-decoration:none;position:relative;display:inline-block}
.cap s::after{content:"";position:absolute;left:-10px;right:-10px;top:52%%;
  height:13px;border-radius:7px;background:#FFD166}
.label{position:absolute;left:56px;bottom:290px;background:#1E9E9E;
  padding:26px 38px;border-radius:10px;text-align:left;font-weight:800;
  font-size:72px;line-height:1.2;color:#fff;-webkit-text-stroke:10px #000;
  paint-order:stroke fill}
.label small{display:block;font-size:46px;margin-top:8px}
.hero{position:absolute;left:0;right:0;top:46%%;transform:translateY(-50%%);
  text-align:center;color:#fff;-webkit-text-stroke:16px #000;paint-order:stroke fill}
.hero .ko{display:block;font-weight:800;font-size:172px;line-height:1.08}
.hero .rom{display:block;font-weight:700;font-size:62px;margin-top:22px;
  color:#D7BFFF;-webkit-text-stroke:12px #000;paint-order:stroke fill;font-style:italic}
.url{position:absolute;left:0;right:0;bottom:160px;text-align:center;
  font-weight:800;font-size:58px;color:#fff;-webkit-text-stroke:12px #000;
  paint-order:stroke fill}
"""
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def run(c):
    return subprocess.run(c, capture_output=True, text=True)


def dur_of(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", p])
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def narration():
    """컷마다 음성을 만들고, 그 길이로 컷 길이를 정한다."""
    parts = []
    for i, s in enumerate(SHOTS):
        aiff = os.path.join(TMP, f"n{i:02d}.aiff")
        run(["say", "-v", VOICE, "-r", str(RATE), "-o", aiff, s["say"]])
        wav = os.path.join(TMP, f"n{i:02d}.wav")
        # 합성음 특유의 날카로움을 약간 깎고 레벨을 맞춘다
        run(["ffmpeg", "-y", "-i", aiff, "-af",
             "highpass=f=95,lowpass=f=7600,"
             "acompressor=threshold=-18dB:ratio=3:attack=6:release=180,volume=1.5",
             "-ar", "44100", "-ac", "1", wav])
        d = dur_of(wav) + TAIL
        s["dur"] = round(max(d, 0.8), 3)
        parts.append(wav)
        print(f"  {i:02d} {s['dur']:5.2f}s  {s['say'][:46]}")
    # 컷 시작 시각에 맞춰 한 트랙으로
    ins, filt, t = [], [], 0.0
    for k, wav in enumerate(parts):
        ins += ["-i", wav]
        filt.append(f"[{k}:a]adelay={int(t*1000)}[d{k}]")
        t += SHOTS[k]["dur"]
    mix = "".join(f"[d{k}]" for k in range(len(parts)))
    filt.append(f"{mix}amix=inputs={len(parts)}:normalize=0[v]")
    voice = os.path.join(TMP, "voice.wav")
    run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(filt),
         "-map", "[v]", "-t", f"{t}", "-ar", "44100", "-ac", "1", voice])
    return voice, t


def puppet(voice, total, fps):
    """전체 길이만큼 얼굴을 한 번에 렌더한다. 컷마다 따로 만들면 경계에서
    입이 어긋난다."""
    out = os.path.join(TMP, "host.mp4")
    r = run([sys.executable, os.path.join(HERE, "puppet.py"),
             "--audio", voice, "--seconds", f"{total:.2f}", "--out", out])
    if not os.path.exists(out) or os.path.getsize(out) < 2048:
        print(r.stdout[-400:], r.stderr[-600:])
        sys.exit("puppet render failed")
    print(f"  host.mp4 {dur_of(out):.1f}s")
    return out


def plate(i, html):
    if not html:
        return None
    css = CAPTION_CSS % {"W": W, "H": H}
    page = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{html}</body></html>"
    hp = os.path.join(TMP, f"cap{i:02d}.html")
    open(hp, "w", encoding="utf-8").write(page)
    png = os.path.join(TMP, f"cap{i:02d}.png")
    run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--user-data-dir=/tmp/sk-f-{i}", "--default-background-color=00000000",
         f"--window-size={W},{H}", "--virtual-time-budget=2500",
         f"--screenshot={png}", f"file://{hp}"])
    return png if os.path.exists(png) else None


def shot(i, s, offset):
    """한 컷. 앱 녹화를 화면에 가득 채우거나, 배경 플레이트 위에 자막만 둔다."""
    out = os.path.join(TMP, f"s{i:02d}.mp4")
    cap = plate(i, s.get("html"))
    d = s["dur"]
    ins, filt = [], []

    if s["layout"] == "clip":
        a, b = s["seg"]
        sp = s.get("speed", 1.0)
        ins += ["-ss", f"{a}", "-t", f"{b-a}", "-i", os.path.join(REC, f"{s['clip']}.mp4")]
        # 녹화는 세로지만 비율이 달라서, 덮도록 키운 뒤 아래쪽을 보여 준다.
        # 자막이 상단 1/3 을 쓰므로 화면 아래쪽에 본문이 오게 잡는다.
        # 앱 화면 위에 자막을 바로 얹으면 가사 글자와 겹쳐 둘 다 안 읽힌다.
        # 레퍼런스에서는 그 자리가 얼굴이라 조용했다. 여기서는 띠를 비워 둔다.
        body = H - TOPBAND
        filt.append(
            f"[0:v]setpts=PTS/{sp},scale={W}:-2,"
            f"crop={W}:min({body}\,ih):0:min(ih*0.30\,max(ih-{body}\,0)),"
            f"pad={W}:{H}:0:{TOPBAND}:color=#160C2B,"
            f"setsar=1,fps={FPS},tpad=stop_mode=clone:stop_duration=10,"
            f"trim=duration={d},setpts=PTS-STARTPTS[base]"
        )
        capidx = 1
    else:
        filt.append(f"color=c=#160C2B:s={W}x{H}:d={d}:r={FPS}[bg]")
        filt.append(f"[bg]gradients=s={W}x{H}:c0=#2A1850:c1=#160C2B:d={d}:r={FPS}[ignore];"
                    if False else f"[bg]null[base]")
        capidx = 0

    if cap:
        ins += ["-loop", "1", "-t", f"{d}", "-i", cap]
        filt.append(f"[base][{capidx}:v]overlay=0:0:format=auto[v]")
        last = "[v]"
    else:
        last = "[base]"

    r = run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(filt),
             "-map", last, "-t", f"{d}", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", out])
    if not os.path.exists(out) or os.path.getsize(out) < 1024:
        print(f"  shot {i} failed:\n{r.stderr[-700:]}")
        return None
    print(f"  s{i:02d} {s['layout']:<5} {dur_of(out):5.2f}s{'  cap' if cap else ''}")
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    if not os.path.exists(HOST):
        sys.exit(f"presenter image missing: {HOST}")

    print("narration")
    voice, total = narration()
    print(f"  total {total:.1f}s")

    print("music")
    bed = os.path.join(TMP, "bed.wav")
    run([sys.executable, os.path.join(HERE, "music.py"),
         "--seconds", f"{total:.2f}", "--out", bed])

    print("shots")
    clips, off = [], 0.0
    for i, s in enumerate(SHOTS):
        c = shot(i, s, off)
        if c:
            clips.append(c)
        off += s["dur"]
    if not clips:
        sys.exit("no shots")

    lst = os.path.join(TMP, "concat.txt")
    open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    silent = os.path.join(TMP, "silent.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])

    # 음악을 내레이션 밑으로 눌러 깐다
    args = ["ffmpeg", "-y", "-i", silent, "-i", voice]
    if os.path.exists(bed):
        args += ["-i", bed, "-filter_complex",
                 "[2:a][1:a]sidechaincompress=threshold=0.04:ratio=9:attack=6:release=300[duck];"
                 "[1:a]volume=1.25[vx];[vx][duck]amix=inputs=2:normalize=0,"
                 "alimiter=limit=0.95[a]", "-map", "0:v", "-map", "[a]"]
    else:
        args += ["-map", "0:v", "-map", "1:a"]
    args += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT]
    run(args)

    if not os.path.exists(OUT) or os.path.getsize(OUT) < 2048:
        sys.exit("final mux failed")
    print(f"\n{OUT}\n  {dur_of(OUT):.1f}s, {os.path.getsize(OUT)/1024/1024:.1f} MB, {W}x{H}")
    print("  app footage led, narration-timed cuts, sequenced music")


if __name__ == "__main__":
    main()
