#!/usr/bin/env python3
"""Remove start/end clicks from imported one-shot sounds (technical fix, not auditioned).

Measured on 2026-09-24: browning/fire.wav starts on sample -0.35 (instant step) and
items/pickup.wav stops while still ringing (0.14 in its last 10 ms). Short linear fades remove
the steps without changing the character: 0.5 ms in on the shot keeps its crack.
Idempotent enough to re-run after a re-import (a faded edge stays faded).

Usage: python scripts/mapkit/declick_legacy.py
"""
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FIXES = {  # file: (fade in seconds, fade out seconds)
    'src/sounds/browning/fire.wav': (0.0005, 0.005),
    'src/sounds/items/pickup.wav': (0.0, 0.015),
}


def main():
    for rel, (fin, fout) in FIXES.items():
        path = ROOT / rel
        with wave.open(str(path), 'rb') as w:
            params = w.getparams()
            data = np.frombuffer(w.readframes(params.nframes), '<i2').astype(np.float64)
        ch = params.nchannels
        x = data.reshape(-1, ch)
        a, b = int(fin * params.framerate), int(fout * params.framerate)
        if a:
            x[:a] *= np.linspace(0, 1, a)[:, None]
        if b:
            x[-b:] *= np.linspace(1, 0, b)[:, None]
        with wave.open(str(path), 'wb') as w:
            w.setparams(params)
            w.writeframes(np.round(x).astype('<i2').tobytes())
        print(f'{rel}: first {x[0, 0] / 32768:+.3f} last {x[-1, 0] / 32768:+.3f}')


if __name__ == '__main__':
    main()
