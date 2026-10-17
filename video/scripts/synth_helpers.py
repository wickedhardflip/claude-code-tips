"""Building blocks for a procedural soundtrack (numpy/scipy). Import into your own synth.py.
Every hit is placed at a time taken from the scene constants, so sound and picture share one clock.
RULE: fade every sound in/out (2 ms in, 8 ms out). Hard cuts cause audible ticking on kicks and bass."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 15.0                      # seconds; set per video
N = int(SR * DUR)
rs = np.random.default_rng(1)   # seeded: re-running gives the identical file
L = np.zeros(N)
R = np.zeros(N)


def t_(n):
    return np.arange(n) / SR


def declick(sig, fade_in=0.002, fade_out=0.008):
    sig = sig.copy()
    a, b = int(fade_in * SR), int(fade_out * SR)
    if len(sig) > a + b:
        sig[:a] *= np.linspace(0, 1, a)
        sig[-b:] *= np.linspace(1, 0, b)
    return sig


def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    s = declick(sig)[: N - i] * gain
    L[i:i + len(s)] += s * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(s)] += s * np.sqrt(0.5 * (1 + pan))


def note(name):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    pitch, octv = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] + 12 * (octv + 1) - 69) / 12)


def lp(x, hz, order=2):
    return sosfilt(butter(order, min(hz, SR / 2 - 100) / (SR / 2), "low", output="sos"), x)


def hp(x, hz, order=2):
    return sosfilt(butter(order, hz / (SR / 2), "high", output="sos"), x)


def kick(at, gain=1.0):
    t = t_(int(0.35 * SR))
    f = 45 + 110 * np.exp(-t * 30)
    place(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9), at, gain)


def click(at, gain=0.3):
    t = t_(int(0.03 * SR))
    place(hp(rs.standard_normal(len(t)), 3000) * np.exp(-t * 180), at, gain)


def whoosh(at, dur=0.6, gain=0.2):
    t = t_(int(dur * SR))
    place(lp(rs.standard_normal(len(t)), 2500) * np.sin(np.pi * t / dur) ** 2, at, gain)


def write(path="out/audio.wav", peak=0.89):
    x = np.stack([L, R], 1)
    x = x / max(np.abs(x).max(), 1e-9) * peak
    wavfile.write(path, SR, (x * 32767).astype(np.int16))
    # Final loudness (about -14 LUFS) is set in the ffmpeg delivery encode with loudnorm.
