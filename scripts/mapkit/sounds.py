#!/usr/bin/env python3
"""Synthesized ambience and one-shots for RF01 (numpy). Original, no third-party samples.

Output: src/sounds/world/{wind_loop,drip_loop,room_loop}.wav, paper.wav, winch.wav
Usage: python scripts/mapkit/sounds.py
"""
from pathlib import Path
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'src' / 'sounds' / 'world'
SR = 44100


def write_wav(name, data, peak=0.85):
    data = np.asarray(data, dtype=np.float64)
    m = np.max(np.abs(data)) or 1.0
    data = data / m * peak
    pcm = (data * 32767).astype('<i2')
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def lowpass(x, cutoff):
    """One-pole IIR low-pass."""
    rc = 1.0 / (2 * np.pi * cutoff)
    dt = 1.0 / SR
    a = dt / (rc + dt)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def lowpass_fast(x, cutoff):
    # FFT brick-wall-ish with soft knee; adequate for ambience
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    gain = 1.0 / (1.0 + (f / cutoff) ** 4)
    return np.fft.irfft(X * gain, n=len(x))


def bandpass_fast(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    gain = 1.0 / (1.0 + (lo / np.maximum(f, 1)) ** 4) / (1.0 + (f / hi) ** 4)
    return np.fft.irfft(X * gain, n=len(x))


def seamless(x, fade_s=1.0):
    n = int(fade_s * SR)
    head = x[:n].copy()
    tail = x[-n:].copy()
    ramp = np.linspace(0, 1, n)
    x = x[:-n]
    x[:n] = head * ramp + tail * (1 - ramp)
    return x


def wind_loop(seconds=12):
    rng = np.random.default_rng(1)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    noise = rng.normal(size=n)
    body = lowpass_fast(noise, 600)
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * t + 1.0) * np.sin(2 * np.pi * 0.19 * t)
    whistle = bandpass_fast(noise, 900, 1600) * (0.15 + 0.15 * np.sin(2 * np.pi * 0.11 * t))
    x = body * gust + whistle * 0.35
    return seamless(x, 1.5)


def drip_loop(seconds=14):
    rng = np.random.default_rng(2)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = lowpass_fast(rng.normal(size=n), 300) * 0.08
    for _ in range(11):
        start = rng.uniform(0.3, seconds - 0.6)
        i0 = int(start * SR)
        dur = int(0.22 * SR)
        tt = np.arange(dur) / SR
        f0 = rng.uniform(1400, 2600)
        sweep = f0 * np.exp(-tt * 9)
        env = np.exp(-tt * 22)
        drip = np.sin(2 * np.pi * np.cumsum(sweep) / SR) * env
        # pipe resonance tail
        tail = np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 12) * 0.35
        x[i0:i0 + dur] += (drip + tail) * rng.uniform(0.5, 1.0)
    return seamless(x, 1.0)


def room_loop(seconds=10):
    rng = np.random.default_rng(3)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = lowpass_fast(rng.normal(size=n), 110)
    x = x * (0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t))
    x += np.sin(2 * np.pi * 50 * t) * 0.15 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.31 * t))
    return seamless(x, 1.0)


def paper(seconds=0.7):
    rng = np.random.default_rng(4)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = bandpass_fast(rng.normal(size=n), 1200, 6000)
    env = np.exp(-((t - 0.18) ** 2) / 0.02) * 0.8 + np.exp(-((t - 0.45) ** 2) / 0.015) * 0.6
    crackle = (rng.random(n) < 0.004).astype(float) * rng.normal(size=n)
    return x * env + lowpass_fast(crackle, 4000) * env * 0.6


def winch(seconds=2.6):
    rng = np.random.default_rng(5)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    motor = np.sin(2 * np.pi * 42 * t) * 0.35 + np.sin(2 * np.pi * 85 * t) * 0.15
    motor *= np.minimum(1, t * 6) * np.minimum(1, (seconds - t) * 3)
    x = motor.copy()
    period = 1 / 7.0
    k = 0
    while k * period < seconds - 0.3:
        i0 = int(k * period * SR)
        dur = int(0.05 * SR)
        tt = np.arange(dur) / SR
        click = rng.normal(size=dur) * np.exp(-tt * 140)
        click = bandpass_fast(click, 800, 5000)
        x[i0:i0 + dur] += click * 0.9
        k += 1
    creak = bandpass_fast(rng.normal(size=n), 300, 900) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t))
    x += creak
    # final clank
    i0 = int((seconds - 0.28) * SR)
    dur = n - i0
    tt = np.arange(dur) / SR
    x[i0:] += np.sin(2 * np.pi * 320 * tt) * np.exp(-tt * 9) * 0.9 + np.sin(2 * np.pi * 1150 * tt) * np.exp(-tt * 20) * 0.5
    return declick(x, 0.005, 0.03)


def declick(x, fade_in_s, fade_out_s):
    """Short linear fades so a one-shot never starts or stops on a non-zero sample (audible click)."""
    x = np.array(x, dtype=np.float64)
    a, b = int(fade_in_s * SR), int(fade_out_s * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def main():
    write_wav('wind_loop.wav', wind_loop(), 0.7)
    write_wav('drip_loop.wav', drip_loop(), 0.75)
    write_wav('room_loop.wav', room_loop(), 0.6)
    write_wav('paper.wav', paper(), 0.7)
    write_wav('winch.wav', winch(), 0.85)
    print('sounds written to', OUT)


if __name__ == '__main__':
    main()
