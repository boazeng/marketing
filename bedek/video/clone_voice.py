# -*- coding: utf-8 -*-
"""
Build a Deepdub voice prompt out of a narration take we already own.

Why this exists: the voice in the finished films is right -- the timbre, the
pace, the register -- and the Hebrew accent is not. Those are separable. This
takes the existing take as a voice SAMPLE and hands it to Deepdub, which then
speaks the same voice with its own Hebrew pronunciation. The alternative,
picking a stranger out of a catalogue, changes both at once.

    python clone_voice.py sheket          from that film's existing take
    python clone_voice.py                 both films
    python clone_voice.py --from deepdub  sample a Deepdub take instead

    python clone_voice.py --file rec.mp4 --title "Boaz" [--text "..."]
                                          from any recording -- video or audio

The speaker's gender is classified by Deepdub, not assumed; --gender
MALE/FEMALE overrides it.

From a take, the sample is that film's beats concatenated: about 20 seconds of
clean speech with no music under it, which is what a voice prompt wants.

From a file, the audio is extracted, downmixed to mono and trimmed to
MAX_SAMPLE seconds. Deepdub caps the upload at 20 MB base64, which is about
three minutes of 44.1kHz mono -- but length past a minute or so buys nothing,
and whatever is in the recording goes into the voice, music and room included.

The printed voicePromptId goes into DEEPDUB_VOICE_BY_SLUG in scripts.py; nothing
here writes it back, because which voice a film uses is a decision and decisions
live in the script file where they can be read.

⚠️ The source take is ElevenLabs output. Re-voicing your own generated audio
through another vendor is a licence question, not a technical one -- it is worth
a look at the ElevenLabs terms before this ships to customers.
"""
import base64, io, json, os, subprocess, sys, unicodedata, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scripts import VIDEOS  # noqa: E402
from vo import parse, audio_dir  # noqa: E402

ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")
URL = "https://restapi.deepdub.ai/api/v1/voice"
GENDER_URL = "https://restapi.deepdub.ai/api/v1/gender-detection/classify"
TMP = os.path.join(HERE, "_tmp", "voice")

# Past this the upload approaches Deepdub's 20 MB base64 cap (~3 min of 44.1kHz
# mono) and stops improving the clone. 21s produced the narrator we shipped.
MAX_SAMPLE = 120


def env(*keys):
    lines = io.open(ENV, encoding="utf-8", errors="replace").read().splitlines()
    for key in keys:
        for raw in lines:
            l = raw.strip().lstrip("\ufeff")
            if l.startswith(key + "="):
                return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{' / '.join(keys)} not in the shared .env")


def strip_niqqud(s):
    """Transcript, not generation text.

    The scripts carry niqqud because the TTS engine needs it to pick a reading.
    A transcript describes audio that already exists, so it goes in as ordinary
    Hebrew -- Mn is the Unicode category the vowel points live in.
    """
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def sample(slug, src):
    """The film's beats, concatenated, 44.1kHz mono WAV."""
    os.makedirs(TMP, exist_ok=True)
    beats = [os.path.join(src, f"{slug}-{b['id']}.mp3")
             for b in next(v for v in VIDEOS if v["slug"] == slug)["beats"]]
    missing = [b for b in beats if not os.path.exists(b)]
    if missing:
        raise SystemExit(f"no take to sample -- {missing[0]} is not there.\n"
                         f"run make_vo.py for that engine first.")
    lst = os.path.join(TMP, f"{slug}.txt")
    io.open(lst, "w", encoding="utf-8").write(
        "".join(f"file '{b}'\n" for b in beats))
    wav = os.path.join(TMP, f"{slug}.wav")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ffmpeg failed:\n{r.stderr[-800:]}")
    return wav


def from_file(path):
    """Any recording -> a mono 44.1kHz WAV sample, trimmed to MAX_SAMPLE."""
    os.makedirs(TMP, exist_ok=True)
    wav = os.path.join(TMP, "from-file.wav")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vn",
                        "-t", str(MAX_SAMPLE), "-ac", "1", "-ar", "44100",
                        "-c:a", "pcm_s16le", wav], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ffmpeg could not read {path}:\n{r.stderr[-800:]}")
    return wav


def detect_gender(wav):
    """Ask Deepdub who is speaking.

    Not a default and not a guess: the field drives Hebrew diacritisation at
    generation time, so getting it wrong comes back as verbs inflected for the
    wrong speaker. The classifier is free and takes the same audio we are about
    to upload -- there is no reason to assume.
    """
    body = {"audio_base64": base64.b64encode(io.open(wav, "rb").read()).decode("ascii")}
    req = urllib.request.Request(GENDER_URL, data=json.dumps(body).encode("utf-8"),
                                 method="POST",
                                 headers={"x-api-key": env("DEEPDUB_API_KEY",
                                                           "DEEPDUV_API_KEY"),
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        j = json.loads(r.read().decode("utf-8"))
    g, conf = j.get("predicted_gender", ""), j.get("confidence") or 0.0
    print(f"  speaker: {g} ({conf:.1%})")
    if conf < 0.8:
        print("  ⚠️  low confidence -- pass --gender MALE/FEMALE to be sure")
    return g.upper() if g else "MALE"


def upload(wav, title, text, gender):
    body = {
        "filename": os.path.basename(wav),
        "data": base64.b64encode(io.open(wav, "rb").read()).decode("ascii"),
        "title": title,
        "text": text,
        "locale": "he-IL",
        "gender": gender,
        "speaking_style": "narrative",
        # Private. These are our films' voices, not a contribution to the
        # public catalogue.
        "publish": False,
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                                 method="POST",
                                 headers={"x-api-key": env("DEEPDUB_API_KEY",
                                                           "DEEPDUV_API_KEY"),
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


if __name__ == "__main__":
    argv = list(sys.argv[1:])

    def take(flag):
        if flag in argv:
            i = argv.index(flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    src_file = take("--file")
    title = take("--title")
    text = take("--text")
    src_engine = take("--from") or "elevenlabs"
    gender = (take("--gender") or "").upper() or None

    if src_file:
        wav = from_file(src_file)
        secs = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", wav],
            capture_output=True, text=True).stdout.strip())
        print(f"\n=== {os.path.basename(src_file)} · sample {secs:.2f}s ===")
        if secs < 15:
            print("  ⚠️  under 15s -- expect a thinner clone")
        try:
            res = upload(wav, title or os.path.basename(src_file), text or "",
                         gender or detect_gender(wav))
        except urllib.error.HTTPError as e:
            raise SystemExit(f"  FAILED {e.code}: "
                             f"{e.read().decode('utf-8','replace')[:400]}")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        raise SystemExit(0)

    only, _, _ = parse(argv)
    src = audio_dir(src_engine)
    for v in VIDEOS:
        if only and v["slug"] != only:
            continue
        wav = sample(v["slug"], src)
        secs = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                               "format=duration", "-of", "default=nw=1:nk=1", wav],
                              capture_output=True, text=True).stdout.strip()
        print(f"\n=== {v['slug']} · sample {secs}s from {src_engine} ===")
        try:
            res = upload(wav, f"TACT Bedek - {v['slug']} narrator",
                         strip_niqqud(" ".join(b["vo"] for b in v["beats"])),
                         gender or detect_gender(wav))
        except urllib.error.HTTPError as e:
            raise SystemExit(f"  FAILED {e.code}: "
                             f"{e.read().decode('utf-8','replace')[:400]}")
        print(json.dumps(res, ensure_ascii=False, indent=2))
