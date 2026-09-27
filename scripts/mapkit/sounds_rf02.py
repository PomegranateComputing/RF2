#!/usr/bin/env python3
"""Synthesized place sounds for RF02 (numpy), same method as the RF01 set (scripts/mapkit/sounds.py, whose
helpers are imported; RF01 sounds are never rewritten from here). Original, no third-party samples, no music:
the radio voices, the march and the scratched waltz of the text stay out of the soundtrack (subtitled instead).
Provisional until Astra's RF02 sound request (docs/production/handoff/RF2-MAP-02/DEMANDE_ASSETS.md) is delivered
under the same file names.

Output: src/sounds/paris/{tsf_loop,fire_loop,street_loop}.wav, phone_ring.wav, phone_tone.wav, engines.wav,
        bell.wav, radio_burst.wav, fuse.wav
Usage: python scripts/mapkit/sounds_rf02.py
"""
from pathlib import Path
import wave
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sounds import SR, lowpass_fast, bandpass_fast, seamless, declick  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'src' / 'sounds' / 'paris'


def write_wav(name, data, peak=0.85):
    data = np.asarray(data, dtype=np.float64)
    data = data / (np.max(np.abs(data)) or 1.0) * peak
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((data * 32767).astype('<i2').tobytes())


def tsf_loop(seconds=10):
    """Shop full of wireless sets on different frequencies breathing the same hiss (l. 211), crackles, a far
    whistle of tuning; no words."""
    rng = np.random.default_rng(21)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    hiss = bandpass_fast(rng.normal(size=n), 300, 4200) * 0.5
    hiss *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.23 * t) * np.sin(2 * np.pi * 0.61 * t + 0.4)
    crack = (rng.random(n) < 0.0009).astype(float) * rng.normal(size=n) * 6
    crack = bandpass_fast(crack, 600, 7000)
    whistle = np.sin(2 * np.pi * (1800 + 400 * np.sin(2 * np.pi * 0.05 * t)) * t) * 0.03
    hum = np.sin(2 * np.pi * 50 * t) * 0.05
    return seamless(hiss + crack + whistle + hum, 1.0)


def fire_loop(seconds=8):
    """Forms burning badly in a galvanised bucket (l. 87): soft roar, paper crackle, occasional flutter."""
    rng = np.random.default_rng(22)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    roar = lowpass_fast(rng.normal(size=n), 400) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t) ** 2)
    pops = (rng.random(n) < 0.002).astype(float) * rng.normal(size=n) * 5
    pops = bandpass_fast(pops, 1500, 8000)
    flutter = bandpass_fast(rng.normal(size=n), 2000, 6000) * 0.12 * (np.sin(2 * np.pi * 0.9 * t) > 0.7)
    return seamless(roar * 0.5 + pops + flutter, 1.0)


def street_loop(seconds=14):
    """An open city in the morning without traffic: wide low wind between facades, a far cart, distant voices
    reduced to murmur (no intelligible speech)."""
    rng = np.random.default_rng(23)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    air = lowpass_fast(rng.normal(size=n), 350) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.06 * t))
    murmur = bandpass_fast(rng.normal(size=n), 250, 900) * 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 2))
    cart = np.zeros(n)
    for k in range(18):
        i0 = int((4.0 + k * 0.21 + rng.uniform(-0.02, 0.02)) * SR)
        dur = int(0.06 * SR)
        tt = np.arange(dur) / SR
        cart[i0:i0 + dur] += bandpass_fast(rng.normal(size=dur), 200, 1200) * np.exp(-tt * 60) * 0.25
    return seamless(air + murmur + lowpass_fast(cart, 1500), 1.5)


def phone_ring(seconds=2.4):
    """Military field telephone (l. 333): a magneto bell, dry and authoritative, two bursts."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for start in (0.0, 1.2):
        mask = (t >= start) & (t < start + 0.8)
        tt = t[mask] - start
        strike = (np.sin(2 * np.pi * 19 * tt) > 0).astype(float)          # hammer at 19 Hz
        bell = np.sin(2 * np.pi * 1180 * tt) + 0.6 * np.sin(2 * np.pi * 2630 * tt) + 0.3 * np.sin(2 * np.pi * 3710 * tt)
        env = np.minimum(1, tt * 40) * np.minimum(1, (0.8 - tt) * 20)
        x[mask] = bell * (0.55 + 0.45 * strike) * env
    return declick(x, 0.003, 0.02)


def phone_tone(seconds=3.0):
    """The continuous tone after the line is cut, so pure it seems to cross the skull (l. 353)."""
    t = np.arange(int(seconds * SR)) / SR
    return declick(np.sin(2 * np.pi * 440 * t) * 0.6 + np.sin(2 * np.pi * 880 * t) * 0.05, 0.01, 0.3)


def engines(seconds=14):
    """Engines from the north (l. 325): regular, heavy, several columns; something domestic, lorries nearing a
    depot, generators, ventilation spooling up."""
    rng = np.random.default_rng(24)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, (f, ph) in enumerate(((31, 0.0), (37, 1.3), (44, 2.1), (27, 0.7))):
        wob = 1 + 0.03 * np.sin(2 * np.pi * (0.2 + 0.07 * k) * t + ph)
        x += np.sin(2 * np.pi * f * np.cumsum(wob) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t + ph) ** 2)
    x += lowpass_fast(rng.normal(size=n), 160) * 2.0
    x += bandpass_fast(rng.normal(size=n), 600, 1500) * 0.15                # track squeal, far
    env = np.minimum(1, t / 5.0) * np.minimum(1, (seconds - t) / 3.0)
    return declick(lowpass_fast(x, 500) * env, 0.02, 0.2)


def bell(seconds=9.0):
    """A bell from the west (l. 449): not a church; three strokes, a silence, three more."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    partials = ((620, 1.0, 1.4), (1240 * 1.01, 0.45, 2.2), (1710, 0.3, 3.0), (2380, 0.18, 4.5), (310, 0.35, 1.0))
    for start in (0.0, 0.9, 1.8, 5.0, 5.9, 6.8):
        i0 = int(start * SR)
        tt = t[i0:] - start
        stroke = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, a, d in partials)
        x[i0:] += stroke * np.minimum(1, tt * 300)
    return declick(lowpass_fast(x, 3000), 0.002, 0.5)


def radio_burst(seconds=2.2):
    """The repaired set switched on (l. 245): a crack, a surge of carrier and hiss that the voice will fill (the
    voice itself is subtitled)."""
    rng = np.random.default_rng(25)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    hiss = bandpass_fast(rng.normal(size=n), 400, 5000) * np.minimum(1, t * 3)
    carrier = np.sin(2 * np.pi * 1000 * t) * 0.08 * np.exp(-t * 2)
    x = hiss + carrier
    x[:int(0.03 * SR)] += rng.normal(size=int(0.03 * SR)) * 2
    return declick(x, 0.002, 0.3)


def fuse(seconds=0.35):
    """A fuse pushed into its holder: metal click and a small spring."""
    rng = np.random.default_rng(26)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    click = bandpass_fast(rng.normal(size=n), 1500, 7000) * np.exp(-t * 80)
    ring = np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 30) * 0.3
    return declick(click + ring, 0.001, 0.05)


def main():
    write_wav('tsf_loop.wav', tsf_loop(), 0.6)
    write_wav('fire_loop.wav', fire_loop(), 0.6)
    write_wav('street_loop.wav', street_loop(), 0.55)
    write_wav('phone_ring.wav', phone_ring(), 0.8)
    write_wav('phone_tone.wav', phone_tone(), 0.45)
    write_wav('engines.wav', engines(), 0.8)
    write_wav('bell.wav', bell(), 0.7)
    write_wav('radio_burst.wav', radio_burst(), 0.7)
    write_wav('fuse.wav', fuse(), 0.7)
    print('RF02 sounds written to', OUT)


if __name__ == '__main__':
    main()
