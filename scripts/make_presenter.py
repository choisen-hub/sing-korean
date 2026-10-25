# -*- coding: utf-8 -*-
"""Generate the presenter still through Replicate, and keep it reproducible.

The reel format is presenter-led, so one face has to occupy that role in every
video. Consistency matters more than the particular face: the reference's long
opening hold works because the viewer recognises the host on sight.

So this records the exact prompt, seed and model alongside the image. Rerunning
with the same seed reproduces it, and later videos reuse the saved file rather
than generating a new face each time.

  export REPLICATE_API_TOKEN=...        (or put it in .env)
  python3 scripts/make_presenter.py
  python3 scripts/make_presenter.py --prompt "..." --seed 12345
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "media", "presenter")

MODEL = "black-forest-labs/flux-schnell"

# 얼굴은 매번 같아야 하므로 프롬프트도 기록해 둔다. 실존 인물을 닮게 하지 않는다.
DEFAULT_PROMPT = (
    "photorealistic portrait of a friendly Korean woman in her mid twenties, "
    "warm natural smile, looking straight at the camera, shoulder-up framing, "
    "soft indoor lighting, plain lilac wall behind her, casual knit sweater, "
    "shot on a 50mm lens, shallow depth of field, no text, no logos"
)
NEGATIVE = "celebrity, famous person, idol, k-pop star, watermark, text, deformed hands"


def token():
    t = os.environ.get("REPLICATE_API_TOKEN")
    if t:
        return t.strip()
    env = os.path.join(ROOT, ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.strip().startswith("REPLICATE_API_TOKEN"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def post(url, payload, tok):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {tok}",
                 "Content-Type": "application/json",
                 "Prefer": "wait"},
        method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def get(url, tok):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main():
    tok = token()
    if not tok:
        sys.exit(
            "REPLICATE_API_TOKEN not set.\n"
            "  replicate.com -> Account -> API tokens, then either\n"
            "    export REPLICATE_API_TOKEN=r8_...\n"
            "  or add a line to .env:  REPLICATE_API_TOKEN=r8_...\n"
            "  .env is gitignored."
        )

    prompt = DEFAULT_PROMPT
    if "--prompt" in sys.argv:
        prompt = sys.argv[sys.argv.index("--prompt") + 1]
    seed = 73519
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])

    os.makedirs(OUT, exist_ok=True)
    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": "9:16",
            "output_format": "png",
            "num_outputs": 1,
            "seed": seed,
        }
    }
    print(f"model {MODEL}  seed {seed}")
    try:
        r = post(f"https://api.replicate.com/v1/models/{MODEL}/predictions", payload, tok)
    except urllib.error.HTTPError as e:
        sys.exit(f"replicate rejected the request ({e.code}):\n{e.read().decode()[:500]}")

    for _ in range(90):
        if r.get("status") in ("succeeded", "failed", "canceled"):
            break
        time.sleep(2)
        r = get(r["urls"]["get"], tok)

    if r.get("status") != "succeeded":
        sys.exit(f"generation {r.get('status')}: {r.get('error')}")

    out = r.get("output")
    url = out[0] if isinstance(out, list) else out
    img = os.path.join(OUT, "presenter.png")
    with urllib.request.urlopen(url, timeout=120) as src, open(img, "wb") as f:
        f.write(src.read())

    with open(os.path.join(OUT, "presenter.json"), "w", encoding="utf-8") as f:
        json.dump({"model": MODEL, "prompt": prompt, "negative_note": NEGATIVE,
                   "seed": seed, "source_url": url,
                   "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, f,
                  ensure_ascii=False, indent=1)

    kb = os.path.getsize(img) / 1024
    print(f"{img}  ({kb:.0f} KB)")
    print("prompt and seed saved to presenter.json so the same face can be remade")


if __name__ == "__main__":
    main()
