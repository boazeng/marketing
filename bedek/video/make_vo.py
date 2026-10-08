# -*- coding: utf-8 -*-
"""
Narration, per beat.

One file per beat rather than one long take, because the beat durations are
what the video clips have to match. Generating the voice FIRST and cutting
picture to it is the order that produces a film; the reverse produces a
slideshow with a voice rushing to keep up.

    python make_vo.py                       both videos, Deepdub
    python make_vo.py sheket                one
    python make_vo.py --engine elevenlabs   the first take, for comparison

Pacing lives in scripts.py (PACE / PACE_BY_BEAT) and reaches Deepdub as
`targetDuration`, but only on a model that honours one -- see PACED_MODELS.
`tempo` never works on any of them.

Two engines, both runnable, each writing into its own `audio/<engine>/` -- see
vo.py for why they are kept apart.

  deepdub     dd-etts-3.4 over the REST API. The current take.
  elevenlabs  eleven_v3 -- the only ElevenLabs model that speaks Hebrew at all.

A beat is generated only if its file is missing. Both engines bill per
generation, so re-running to add one line does not re-pay for the other six.
To replace a take, delete that one file.
"""
import io, json, os, subprocess, sys, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scripts import (VIDEOS, ELEVEN_VOICE_BY_SLUG,  # noqa: E402
                     DEEPDUB_VOICE_BY_SLUG, DEEPDUB_GENDER_BY_SLUG,
                     PACE, PACE_BY_BEAT, DEEPDUB_TAKES)
from vo import parse, audio_dir  # noqa: E402

# The shared secrets file. Override with TACT_ENV on a machine where it
# lives elsewhere -- nothing in this repo may ever contain a secret.
ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")


def env(*keys):
    """First of `keys` present in the shared .env.

    Parsed line by line and not grepped: the shared file has no trailing
    newline, so a grep for the last key silently finds nothing.
    """
    lines = io.open(ENV, encoding="utf-8", errors="replace").read().splitlines()
    for key in keys:
        for raw in lines:
            l = raw.strip().lstrip("\ufeff")
            if l.startswith(key + "="):
                return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{' / '.join(keys)} not in the shared .env")


def post(url, body, headers, path):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=180) as r:
        io.open(path, "wb").write(r.read())


# --- elevenlabs ------------------------------------------------------------

def speak_elevenlabs(text, path, slug):
    post(f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_BY_SLUG[slug]}",
         {"text": text, "model_id": "eleven_v3",
          "voice_settings": {"stability": 0.45, "similarity_boost": 0.8,
                             "speed": 0.95}},
         {"xi-api-key": env("ELEVENLABS_API_KEY"),
          "Content-Type": "application/json", "Accept": "audio/mpeg"},
         path)


# --- deepdub ---------------------------------------------------------------

# 48 kHz because build.py mixes everything at 48 kHz; asking for it here avoids
# a resample in the mix. Only 8000/16000/22050/24000/32000/36000/44100/48000 are
# accepted -- anything else is a 400.
DEEPDUB_URL = "https://restapi.deepdub.ai/api/v1/tts"
# 3.4, not the 3.0 the REST docs default to. It is what the playground hands
# out, and it was chosen by ear over a full read of both films.
DEEPDUB_MODEL = "dd-etts-3.4"

# Which models actually pace. 3.0 lands inside 0.05s of a `targetDuration`.
#
# ⚠️ 3.4 does NOT, and sending one is worse than sending nothing. One line,
# asked for 2.80s / 3.40s / 4.50s, came back 4.87 / 4.85 / 4.78 -- the target
# is ignored, and merely including the field pushes every generation to about
# 4.8s. Left alone, the same line reads 3.17-3.82s across three runs.
#
# So on 3.4 the pace multipliers do nothing and are not sent. Rhythm comes from
# TAIL instead, which is silence laid by ffmpeg and therefore exact. That is
# the better division anyway: a line lands because of the pause after it, not
# because the words were stretched.
PACED_MODELS = {"dd-etts-3.0"}
DEEPDUB_SAMPLE_RATE = 48000

# The key is spelled DEEPDUV in the shared .env -- a typo that is already in
# use elsewhere. Read both so fixing it later breaks nothing.
_DEEPDUB_KEYS = ("DEEPDUB_API_KEY", "DEEPDUV_API_KEY")


TAKE = None          # set from --take; None means the per-film voices


def _take(key, fallback):
    """A take overrides only what it names; everything else stays as shipped."""
    return DEEPDUB_TAKES[TAKE].get(key, fallback) if TAKE else fallback


def _voice(slug):
    return _take("voice", DEEPDUB_VOICE_BY_SLUG[slug])


def _gender(slug):
    return _take("gender", DEEPDUB_GENDER_BY_SLUG[slug])


def _model():
    return _take("model", DEEPDUB_MODEL)


def speak_deepdub(text, path, slug, seconds=None):
    """One line. `seconds`, if given, is how long it should take.

    ⚠️ Do not reach for `tempo` here. It is accepted, it is silently ignored,
    and two generations of one line at 0.95 and 0.85 came back identical in
    length to the millisecond. `targetDuration` is the parameter that works,
    and the two are mutually exclusive -- never send both.

    `superStretch` is what lets a long target actually be reached: asking for
    3.0s on a 2.04s line landed at 2.78s without it and 3.02s with it.
    """
    body = {"model": _model(), "targetText": text, "locale": "he-IL",
            "voicePromptId": _voice(slug),
            # Deepdub re-points Hebrew with its own diacritiser and uses the
            # speaker's gender to do it. It overrules the niqqud we send, so
            # this field is not cosmetic -- see the note in scripts.py.
            "targetGender": _gender(slug),
            "format": "mp3", "sampleRate": DEEPDUB_SAMPLE_RATE}
    if seconds:
        body["targetDuration"] = round(seconds, 2)
        body["superStretch"] = True
    post(DEEPDUB_URL, body,
         {"x-api-key": env(*_DEEPDUB_KEYS), "Content-Type": "application/json"},
         path)


def pace_of(beat_id):
    return PACE_BY_BEAT.get(beat_id, PACE)


def natural_length(text, slug, beat_id, out, cache):
    """How long this line takes at Deepdub's own pace.

    Measured, not guessed -- `targetDuration` is absolute seconds, so a pace
    multiplier needs a baseline. Cached, because the measurement costs a
    generation and the answer does not change unless the line does.
    """
    if beat_id in cache:
        return cache[beat_id]
    probe = os.path.join(out, f".natural-{slug}-{beat_id}.mp3")
    speak_deepdub(text, probe, slug)
    cache[beat_id] = round(duration(probe), 3)
    os.remove(probe)
    return cache[beat_id]


SPEAK = {"elevenlabs": speak_elevenlabs, "deepdub": speak_deepdub}


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True)
    return float(out.stdout.strip())


if __name__ == "__main__":
    only, engine, TAKE = parse(sys.argv[1:])
    if TAKE and TAKE not in DEEPDUB_TAKES:
        raise SystemExit(f"unknown take {TAKE!r} -- "
                         f"add it to DEEPDUB_TAKES in scripts.py")
    OUT = audio_dir(engine, TAKE)
    os.makedirs(OUT, exist_ok=True)
    timing = {}

    # Deepdub is paced by absolute duration, so it needs to know what each line
    # costs unpaced. The cache survives between runs; a line that is edited
    # should be dropped from it, the same way its mp3 is.
    nat_path = os.path.join(OUT, "natural.json")
    natural = (json.load(io.open(nat_path, encoding="utf-8"))
               if engine == "deepdub" and os.path.exists(nat_path) else {})

    for v in VIDEOS:
        if only and v["slug"] != only:
            continue
        print(f"\n=== {v['slug']} · {v['title']} · "
              f"{engine}{'-' + TAKE if TAKE else ''} ===")
        total = 0.0
        beats = []
        for b in v["beats"]:
            path = os.path.join(OUT, f"{v['slug']}-{b['id']}.mp3")
            want = None
            if not os.path.exists(path):
                try:
                    if engine == "deepdub":
                        if _model() in PACED_MODELS:
                            want = natural_length(b["vo"], v["slug"], b["id"],
                                                  OUT, natural) * pace_of(b["id"])
                        speak_deepdub(b["vo"], path, v["slug"], want)
                    else:
                        speak_elevenlabs(b["vo"], path, v["slug"])
                except urllib.error.HTTPError as e:
                    raise SystemExit(f"  {b['id']} FAILED {e.code}: "
                                     f"{e.read().decode('utf-8','replace')[:300]}")
            d = duration(path)
            total += d
            beats.append({"id": b["id"], "vo": b["vo"], "sec": round(d, 2),
                          "card": b.get("card")})
            # Asked-for vs got, because targetDuration is a request and the
            # engine can miss it. timing.json always records what is on disk,
            # so build.py stays in sync either way.
            ask = f"  (asked {want:.2f}s, x{pace_of(b['id']):.2f})" if want else ""
            print(f"  {b['id']}  {d:5.2f}s  {b['vo']}{ask}")
        timing[v["slug"]] = {"beats": beats, "total": round(total, 2)}
        print(f"  {'':6}{total:5.2f}s TOTAL")

    if engine == "deepdub":
        io.open(nat_path, "w", encoding="utf-8").write(
            json.dumps(natural, ensure_ascii=False, indent=2, sort_keys=True))

    path = os.path.join(OUT, "timing.json")
    existing = json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {}
    existing.update(timing)
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(existing, ensure_ascii=False, indent=2))
    print(f"\n-> {path}")
