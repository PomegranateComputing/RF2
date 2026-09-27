#!/usr/bin/env python3
"""RF2-UI-01 menu sounds: short, dry, quiet paper and metal touches (no music, no loop).

Cut from CC0 recordings already kept with the RF2-ART-01 sources (Kenney, RPG Audio / Impact Sounds,
art/rf2_art_01/audio/sources, licence files alongside). Each cue: a window of the take, 4 ms fade-in,
a short exponential fade-out, a gentle high-pass for the paper cues, peak-normalised to a level under the
game's own sounds (menus are heard over silence or the paused game). Mono, 48 kHz, PCM16.

Provisional until an Astra UI sound batch replaces them (same file names).
Usage: python scripts/ui/ui_sounds.py   (writes src/sounds/ui/*.wav)
"""
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'art' / 'rf2_art_01' / 'audio' / 'sources'
OUT = ROOT / 'src' / 'sounds' / 'ui'
RATE = 48000

# name: (source, start s, length s, peak dBFS, high-pass Hz or 0, pitch ratio)
CUES = {
    'cursor':  ('rpg/Audio/bookFlip2.ogg', 0.00, 0.075, -26, 900, 1.00),
    'choose':  ('rpg/Audio/metalClick.ogg', 0.00, 0.140, -20, 200, 1.00),
    'change':  ('rpg/Audio/metalClick.ogg', 0.00, 0.090, -27, 400, 1.12),
    'backup':  ('rpg/Audio/bookPlace2.ogg', 0.00, 0.160, -24, 250, 1.00),
    'clear':   ('rpg/Audio/cloth2.ogg', 0.00, 0.200, -26, 200, 1.00),
    'invalid': ('impact/Audio/impactSoft_medium_000.ogg', 0.00, 0.110, -24, 0, 0.85),
    'prompt':  ('rpg/Audio/metalLatch.ogg', 0.00, 0.220, -22, 150, 1.00),
    'dismiss': ('rpg/Audio/bookFlip3.ogg', 0.00, 0.110, -27, 900, 1.00),
}


def load(rel):
    data, rate = sf.read(str(SRC / rel), always_2d=True)
    mono = data.mean(axis=1)
    if rate != RATE:
        g = np.gcd(rate, RATE)
        mono = resample_poly(mono, RATE // g, rate // g)
    return mono


def onset(x, threshold=0.02):
    idx = np.flatnonzero(np.abs(x) > threshold * np.abs(x).max())
    return int(idx[0]) if idx.size else 0


def cue(src, start, length, peak_db, hp, pitch):
    x = load(src)
    if pitch != 1.0:
        up, down = int(round(100 / pitch)), 100
        x = resample_poly(x, up, down)
    i0 = max(0, onset(x) - int(0.002 * RATE)) + int(start * RATE)
    n = int(length * RATE)
    y = x[i0:i0 + n].copy()
    if hp:
        y = sosfilt(butter(2, hp, 'highpass', fs=RATE, output='sos'), y)
    fade_in = int(0.004 * RATE)
    y[:fade_in] *= np.linspace(0, 1, fade_in)
    tail = np.exp(-np.linspace(0, 5, n))[:len(y)]
    y *= np.maximum(tail, 0) ** 0.6
    y[-int(0.006 * RATE):] *= np.linspace(1, 0, int(0.006 * RATE))
    y *= 10 ** (peak_db / 20) / max(np.abs(y).max(), 1e-9)
    return y


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in CUES.items():
        y = cue(*spec)
        sf.write(str(OUT / f'{name}.wav'), y, RATE, subtype='PCM_16')
        print(f'{name}: {len(y) / RATE * 1000:.0f} ms, peak {20 * np.log10(np.abs(y).max()):.1f} dBFS <- {spec[0]}')


if __name__ == '__main__':
    main()
