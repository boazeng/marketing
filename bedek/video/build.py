# -*- coding: utf-8 -*-
"""
Assembles each film: picture cut to the narration, music under it, then the
social crops.

Order of operations matters. Every beat's picture is trimmed to that beat's
narration length plus a small tail, so the cut breathes with the voice instead
of the voice chasing the cut. Music is ducked under the narration by
sidechain compression rather than a fixed level, because a fixed level is
either too loud under speech or inaudible between lines.

    python build.py            both
    python build.py sheket     one

Outputs, per video:
    out/<slug>-16x9.mp4    master, for Facebook feed and the site
    out/<slug>-1x1.mp4     square, feed
    out/<slug>-9x16.mp4    vertical, reels and stories
"""
import io, json, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scripts import VIDEOS  # noqa: E402

CLIPS, AUDIO, OUT = (os.path.join(HERE, d) for d in ("clips", "audio", "out"))
W, H = 1280, 720
# 30, not the 32 the source clips happen to be. A non-standard rate plus sparse
# keyframes is what makes basic players stall a few seconds in -- they cannot
# find a sync point. ffmpeg converts on the way through.
FPS = 30
GOP = FPS * 2          # a keyframe every 2s, so seeking and streaming behave
TAIL = 0.45          # air after each line before the cut
XF = 0.35            # cross-dissolve between beats


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ffmpeg failed:\n{' '.join(args[:9])}...\n{r.stderr[-1500:]}")
    return r


def build(v, timing):
    slug = v["slug"]
    secs = {b["id"]: b["sec"] for b in timing[slug]["beats"]}
    tmp = os.path.join(HERE, "_tmp", slug)
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    # ---- 1. one picture segment per beat, trimmed to its narration ---------
    segs, vo_parts, t = [], [], 0.0
    for b in v["beats"]:
        dur = secs[b["id"]] + TAIL
        src = os.path.join(CLIPS, f"{slug}-{b['id']}.mp4")
        seg = os.path.join(tmp, f"{b['id']}.mp4")
        # The generated clips are 5.03s. Longer beats are slowed to fit rather
        # than looped -- a visible loop point reads as a mistake, a slightly
        # slower move reads as intent.
        src_len = 5.03
        speed = min(1.0, src_len / dur) if dur > src_len else 1.0
        vf = (f"setpts={1/speed:.4f}*PTS," if speed < 1.0 else "") + \
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-t", f"{dur:.3f}",
             "-vf", vf, "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-crf", "18", seg])
        segs.append((seg, dur))
        # Each cross-dissolve OVERLAPS its two beats, so the finished picture is
        # XF shorter per transition. The narration has to sit on that same
        # shortened timeline -- placing it on the naive sum leaves the last line
        # hanging past the end of picture, where `-shortest` silently cuts it.
        vo_parts.append((os.path.join(AUDIO, f"{slug}-{b['id']}.mp3"),
                         t - len(segs[:-1]) * XF))
        t += dur

    total = t - (len(segs) - 1) * XF

    # ---- 2. picture, cross-dissolved -------------------------------------
    inputs, filt, prev, offset = [], [], None, 0.0
    for i, (seg, dur) in enumerate(segs):
        inputs += ["-i", seg]
        if i == 0:
            prev, offset = "0:v", dur
            continue
        offset -= XF
        run_lbl = f"x{i}"
        filt.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:"
                    f"offset={offset:.3f}[{run_lbl}]")
        prev, offset = run_lbl, offset + dur
    picture = os.path.join(tmp, "picture.mp4")
    run(["ffmpeg", "-y", "-v", "error", *inputs,
         *(["-filter_complex", ";".join(filt), "-map", f"[{prev}]"] if filt else []),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", picture])

    # ---- 3. narration laid on a silent bed at the right offsets ----------
    a_in, a_filt, mix = [], [], []
    for i, (mp3, at) in enumerate(vo_parts):
        a_in += ["-i", mp3]
        a_filt.append(f"[{i}:a]adelay={int(at*1000)}|{int(at*1000)},"
                      f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[v{i}]")
        mix.append(f"[v{i}]")
    vo = os.path.join(tmp, "vo.wav")
    run(["ffmpeg", "-y", "-v", "error", *a_in, "-filter_complex",
         ";".join(a_filt) + ";" + "".join(mix) + f"amix=inputs={len(mix)}:normalize=0[a]",
         "-map", "[a]", "-t", f"{total:.3f}", vo])

    # ---- 4. music, ducked under the voice --------------------------------
    music = os.path.join(AUDIO, "bed.wav")
    final_a = os.path.join(tmp, "mix.wav")
    if os.path.exists(music):
        run(["ffmpeg", "-y", "-v", "error", "-i", vo, "-stream_loop", "-1", "-i", music,
             "-filter_complex",
             f"[1:a]atrim=0:{total:.3f},volume=0.20[m];"
             f"[m][0:a]sidechaincompress=threshold=0.02:ratio=12:attack=8:release=320[md];"
             f"[md][0:a]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]",
             "-map", "[a]", "-t", f"{total:.3f}", final_a])
    else:
        final_a = vo

    master = os.path.join(OUT, f"{slug}-16x9.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", picture, "-i", final_a,
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-level", "4.0",
         "-g", str(GOP), "-keyint_min", str(GOP), "-sc_threshold", "0",
         "-r", str(FPS), "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", "-shortest", master])

    # ---- 5. social crops -------------------------------------------------
    for name, (cw, ch) in {"1x1": (720, 720), "9x16": (720, 1280)}.items():
        run(["ffmpeg", "-y", "-v", "error", "-i", master,
             "-vf", f"scale={cw}:{ch}:force_original_aspect_ratio=increase,"
                    f"crop={cw}:{ch}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-profile:v", "high", "-level", "4.0",
             "-g", str(GOP), "-keyint_min", str(GOP), "-sc_threshold", "0",
             "-r", str(FPS), "-crf", "19",
             "-c:a", "copy", "-movflags", "+faststart",
             os.path.join(OUT, f"{slug}-{name}.mp4")])

    print(f"  {slug}  {total:5.2f}s  ->  16x9 · 1x1 · 9x16")
    return total


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    timing = json.load(io.open(os.path.join(AUDIO, "timing.json"), encoding="utf-8"))
    for v in VIDEOS:
        if only and v["slug"] != only:
            continue
        build(v, timing)
    print(f"\n-> {OUT}")
