# -*- coding: utf-8 -*-
"""Write an actual music bed: chords, bass, kick and hats on a grid.

The earlier version layered three held sine tones and called it music. It was a
drone. Music needs notes that change and a pulse you can count, which a filter
graph cannot sequence, so the waveform is synthesised sample by sample here.

Lo-fi room: Am - F - C - G at 78 bpm, plucked chord tones with a short decay, a
bass on the root, a soft kick on one and three, closed hats on the eighths, and
a gentle low-pass so it sits under narration rather than fighting it.

  python3 scripts/music.py --seconds 27 --out media/_tmp/bed.wav
"""

import math
import os
import struct
import sys
import wave

SR = 44100
BPM = 78
BEAT = 60.0 / BPM

# A minor, four bars. Root plus the two chord tones used for the pluck pattern.
PROGRESSION = [
    ("Am", 220.00, [220.00, 261.63, 329.63]),
    ("F",  174.61, [174.61, 220.00, 261.63]),
    ("C",  130.81, [261.63, 329.63, 392.00]),
    ("G",  196.00, [196.00, 246.94, 293.66]),
]


def env_pluck(t, dur, attack=0.006, decay=0.55):
    if t < 0 or t > dur:
        return 0.0
    if t < attack:
        return t / attack
    return math.exp(-(t - attack) / decay)


def env_perc(t, dur, decay):
    if t < 0 or t > dur:
        return 0.0
    return math.exp(-t / decay)


def render(seconds):
    n = int(seconds * SR)
    buf = [0.0] * n
    bar = BEAT * 4

    def add(start, dur, fn, gain):
        a = int(start * SR)
        b = min(n, a + int(dur * SR))
        for i in range(max(0, a), b):
            buf[i] += gain * fn((i - a) / SR)

    bars = int(seconds / bar) + 1
    for b in range(bars):
        name, root, tones = PROGRESSION[b % len(PROGRESSION)]
        t0 = b * bar

        # 베이스: 마디 머리에 길게
        def bass(tt, f=root / 2):
            return math.sin(2 * math.pi * f * tt) * env_pluck(tt, bar, decay=0.9)
        add(t0, bar, bass, 0.30)

        # 아르페지오: 8분음표로 코드음을 훑는다
        pattern = [0, 1, 2, 1, 0, 2, 1, 2]
        for k, idx in enumerate(pattern):
            f = tones[idx]
            st = t0 + k * BEAT / 2

            def pluck(tt, f=f):
                # 배음을 조금 섞어야 사인파 특유의 밋밋함이 줄어든다
                return (math.sin(2 * math.pi * f * tt)
                        + 0.35 * math.sin(4 * math.pi * f * tt)
                        + 0.12 * math.sin(6 * math.pi * f * tt)) * env_pluck(tt, 1.2)
            add(st, 1.2, pluck, 0.085 if k % 2 else 0.11)

        # 킥: 1박과 3박. 피치가 떨어지는 사인
        for beat in (0, 2):
            def kick(tt):
                f = 110 * math.exp(-tt * 28) + 46
                return math.sin(2 * math.pi * f * tt) * env_perc(tt, 0.35, 0.075)
            add(t0 + beat * BEAT, 0.35, kick, 0.5)

        # 하이햇: 8분음표, 짧은 노이즈
        import random
        rnd = random.Random(b)
        for k in range(8):
            def hat(tt, r=rnd):
                return (r.random() * 2 - 1) * env_perc(tt, 0.07, 0.016)
            add(t0 + k * BEAT / 2, 0.07, hat, 0.055 if k % 2 else 0.085)

    # 원펄 저역통과. 내레이션 아래로 깔리게 고역을 깎는다.
    out = [0.0] * n
    alpha = 0.26
    prev = 0.0
    for i in range(n):
        prev = prev + alpha * (buf[i] - prev)
        out[i] = prev

    # 페이드와 리미팅
    fin, fout = int(1.8 * SR), int(2.4 * SR)
    peak = max(1e-6, max(abs(v) for v in out))
    for i in range(n):
        v = out[i] / peak * 0.72
        if i < fin:
            v *= i / fin
        if i > n - fout:
            v *= max(0.0, (n - i) / fout)
        out[i] = max(-1.0, min(1.0, v))
    return out


def main():
    seconds = 27.0
    if "--seconds" in sys.argv:
        seconds = float(sys.argv[sys.argv.index("--seconds") + 1])
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "media", "_tmp", "bed.wav")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(os.path.dirname(out), exist_ok=True)

    samples = render(seconds)
    with wave.open(out, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for v in samples:
            s = struct.pack("<h", int(v * 32000))
            frames += s + s
        w.writeframes(bytes(frames))
    print(f"{out}  {seconds:.1f}s  {BPM} bpm  "
          f"{' - '.join(c[0] for c in PROGRESSION)}  "
          f"{os.path.getsize(out)/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
