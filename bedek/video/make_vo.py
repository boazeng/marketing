# -*- coding: utf-8 -*-
"""
Narration, per beat, with ElevenLabs.

One file per beat rather than one long take, because the beat durations are
what the video clips have to match. Generating the voice FIRST and cutting
picture to it is the order that produces a film; the reverse produces a
slideshow with a voice rushing to keep up.

    python make_vo.py            both videos
    python make_vo.py sheket     one

Model is eleven_v3 -- it is the only one that speaks Hebrew.
"""
import io, json, os, subprocess, sys, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scripts import VIDEOS, VOICE_BY_SLUG  # noqa: E402

OUT = os.path.join(HERE, "audio")
# The shared secrets file. Override with TACT_ENV on a machine where it
# lives elsewhere -- nothing in this repo may ever contain a secret.
ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")


def env(key):
    for raw in io.open(ENV, encoding="utf-8", errors="replace").read().splitlines():
        l = raw.strip().lstrip("\ufeff")
        if l.startswith(key + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{key} not in the shared .env")


KEY = env("ELEVENLABS_API_KEY")


def speak(text, path, voice):
    body = json.dumps({
        "text": text,
        "model_id": "eleven_v3",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "speed": 0.95},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        data=body, method="POST",
        headers={"xi-api-key": KEY, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r:
        io.open(path, "wb").write(r.read())


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True)
    return float(out.stdout.strip())


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(OUT, exist_ok=True)
    timing = {}

    for v in VIDEOS:
        if only and v["slug"] != only:
            continue
        print(f"\n=== {v['slug']} · {v['title']} ===")
        total = 0.0
        beats = []
        for b in v["beats"]:
            path = os.path.join(OUT, f"{v['slug']}-{b['id']}.mp3")
            if not os.path.exists(path):
                try:
                    speak(b["vo"], path, VOICE_BY_SLUG[v["slug"]])
                except urllib.error.HTTPError as e:
                    raise SystemExit(f"  {b['id']} FAILED {e.code}: "
                                     f"{e.read().decode('utf-8','replace')[:300]}")
            d = duration(path)
            total += d
            beats.append({"id": b["id"], "vo": b["vo"], "sec": round(d, 2),
                          "card": b.get("card")})
            print(f"  {b['id']}  {d:5.2f}s  {b['vo']}")
        timing[v["slug"]] = {"beats": beats, "total": round(total, 2)}
        print(f"  {'':6}{total:5.2f}s TOTAL")

    path = os.path.join(OUT, "timing.json")
    existing = json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {}
    existing.update(timing)
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(existing, ensure_ascii=False, indent=2))
    print(f"\n-> {path}")
