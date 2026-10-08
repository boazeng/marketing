# -*- coding: utf-8 -*-
"""
Where the narration for a given engine lives, and how every script here agrees
on it.

One directory per engine rather than one shared `audio/`, because both takes
have to survive. TTS is paid per generation: if switching engines overwrote the
other one's files, comparing them would cost money every time you changed your
mind, and the answer to "is the new voice better" would depend on whichever take
happened to be on disk. Separate directories make the comparison free and make
`--engine` a genuine switch rather than a destructive regeneration.

`bed.wav` -- the music -- stays in `audio/`. It is not narration and does not
change when the voice does.

    from vo import parse, audio_dir
    only, engine, take = parse(sys.argv[1:])
    AUDIO = audio_dir(engine, take)

A TAKE is the same engine with a different voice -- `--take noa` lands in
`audio/deepdub-noa/`. Trying a voice must never overwrite the one that was
approved, and a take that is only a scratch directory cannot be rebuilt later;
the voice behind each one is named in scripts.py.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ENGINES = ("deepdub", "elevenlabs")
DEFAULT = "deepdub"


def audio_dir(engine, take=None):
    return os.path.join(HERE, "audio", f"{engine}-{take}" if take else engine)


def cards_dir(engine, take=None):
    """Where make_cards.py puts its rendered mp4s.

    Default goes into `clips/` beside the fal footage, which is how build.py
    has always found it. A take goes into a subdirectory instead: card clips
    are cut to the narration length, so a take's cards are a different length
    from the approved take's, and writing them to the same names would
    silently desynchronise the cut that is already signed off.
    """
    return os.path.join(HERE, "clips", f"{engine}-{take}") if take \
        else os.path.join(HERE, "clips")


def out_dir(take=None):
    """Finished films. Flat for the approved cut -- ops/sharepoint.py reads
    `video/out/<slug>-<ratio>.mp4` and must keep finding it there."""
    return os.path.join(HERE, "out", take) if take else os.path.join(HERE, "out")


def music_path():
    return os.path.join(HERE, "audio", "bed.wav")


def parse(argv):
    """-> (slug or None, engine, take).

    Accepts `sheket`, `--engine elevenlabs`, `--take noa`.
    """
    only, engine, take, rest = None, DEFAULT, None, list(argv)
    while rest:
        a = rest.pop(0)
        if a in ("--engine", "-e"):
            if not rest:
                raise SystemExit(f"--engine needs one of {', '.join(ENGINES)}")
            engine = rest.pop(0)
        elif a.startswith("--engine="):
            engine = a.split("=", 1)[1]
        elif a == "--take":
            if not rest:
                raise SystemExit("--take needs a name")
            take = rest.pop(0)
        elif a.startswith("--take="):
            take = a.split("=", 1)[1]
        elif a.startswith("-"):
            raise SystemExit(f"unknown flag {a}")
        else:
            only = a
    if engine not in ENGINES:
        raise SystemExit(f"unknown engine {engine!r} -- pick {', '.join(ENGINES)}")
    return only, engine, take
