# -*- coding: utf-8 -*-
"""
Music bed, synthesised in numpy.

Not ffmpeg oscillators: there you get no control over the envelope, and the
chord changes click. Here each note is a soft-attack pad with its own decay, so
the bed moves without ever pulling attention off the narration.

Am - F - C - G, eight seconds a bar, looped by build.py and ducked under the
voice. Deliberately unremarkable -- this audience distrusts a hard sell, and
the music should register only if it stopped.
"""
import numpy as np, sys, wave
sys.stdout.reconfigure(encoding="utf-8")

SR, BAR = 48000, 8.0
CHORDS = [(220.00, 261.63, 329.63),   # Am
          (174.61, 220.00, 261.63),   # F
          (261.63, 329.63, 392.00),   # C
          (196.00, 246.94, 293.66)]   # G

def pad(freqs, seconds):
    t = np.linspace(0, seconds, int(SR*seconds), endpoint=False)
    out = np.zeros_like(t)
    for i, f in enumerate(freqs):
        # a touch of detune per voice keeps it from sounding synthetic
        for d in (-0.6, 0.0, 0.6):
            out += np.sin(2*np.pi*(f+d)*t) / (3*(i+1.6))
        out += 0.10 * np.sin(2*np.pi*(f/2)*t) / (i+2)
    env = np.minimum(1.0, t/1.6) * np.minimum(1.0, (seconds-t)/1.8)
    return out * env

sig = np.concatenate([pad(c, BAR) for c in CHORDS])
sig = np.convolve(sig, np.ones(240)/240, mode="same")     # soften the top
sig /= np.max(np.abs(sig)) * 1.05
stereo = np.stack([sig, np.roll(sig, 380)], axis=1)       # gentle width
pcm = (stereo * 32767 * 0.55).astype(np.int16)

with wave.open("audio/bed.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"audio/bed.wav  {len(sig)/SR:.1f}s")
