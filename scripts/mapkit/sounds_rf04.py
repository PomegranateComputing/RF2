#!/usr/bin/env python3
"""Synthesized place sounds for the Luna Park (RF04/RF05), same method as RF01/RF02 (helpers of sounds.py). Original,
no samples, no music. PROVISIONAL until Astra's S04-xx files (request LUNA-V01) replace them under the same names.

Output: src/sounds/luna/{park_loop,motor_loop}.wav, clock.wav, keys.wav, turnstile.wav, jukebox_key.wav,
        knocks.wav, lock.wav, rail.wav, tarp.wav
Usage: python scripts/mapkit/sounds_rf04.py
"""
from pathlib import Path
import wave
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sounds import SR, lowpass_fast, bandpass_fast, seamless, declick  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'src' / 'sounds' / 'luna'


def write_wav(name, data, peak=0.85):
    data = np.asarray(data, dtype=np.float64)
    data = data / (np.max(np.abs(data)) or 1.0) * peak
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((data * 32767).astype('<i2').tobytes())


def thump(n, at, freq=48, decay=9.0, amp=1.0, click=0.25, rng=None):
    """A heavy low pulse (motor, wheel) starting at sample `at`."""
    t = np.arange(n - at) / SR
    x = np.zeros(n)
    body = np.sin(2 * np.pi * freq * t * (1 - 0.15 * np.exp(-t * 20))) * np.exp(-t * decay)
    x[at:] += amp * body
    if rng is not None and click:
        k = min(n - at, int(0.02 * SR))
        x[at:at + k] += rng.normal(size=k) * click * np.exp(-np.arange(k) / (0.004 * SR))
    return x


def park_loop(seconds=16):
    """The closed park (l. 459-461): wet wood that works, a canvas that flaps, far engines turned into the rumble of
    a ride by the sheds, now and then a creak."""
    rng = np.random.default_rng(41)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    wind = bandpass_fast(rng.normal(size=n), 120, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t) ** 2)
    rumble = lowpass_fast(rng.normal(size=n), 70) * 6 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t + 1.0))
    x = wind * 0.5 + rumble
    for _ in range(9):                                        # creaks of wood
        at = rng.integers(0, n - SR)
        dur = rng.uniform(0.25, 0.7)
        k = int(dur * SR)
        tt = np.arange(k) / SR
        f = rng.uniform(180, 420) * (1 + 0.3 * np.sin(2 * np.pi * rng.uniform(3, 7) * tt))
        creak = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-((tt - dur / 2) / (dur / 3)) ** 2)
        x[at:at + k] += bandpass_fast(creak, 250, 2500) * 0.08
    for _ in range(5):                                        # the canvas
        at = rng.integers(0, n - SR)
        k = int(0.18 * SR)
        x[at:at + k] += bandpass_fast(rng.normal(size=k), 300, 3000) * np.exp(-np.arange(k) / (0.05 * SR)) * 0.15
    return seamless(x, 1.5)


def motor_loop(seconds=6.0):
    """The motor under the park (l. 529, 559): two pulses, a pause, a third longer; the belt slaps on an old repair.
    Heard through the ground: low-passed."""
    rng = np.random.default_rng(42)
    n = int(seconds * SR)
    x = np.zeros(n)
    cycle = 2.0
    for c in range(int(seconds / cycle)):
        base = int(c * cycle * SR)
        for (dt, amp, decay) in ((0.0, 1.0, 9.0), (0.32, 0.9, 9.0), (1.1, 1.2, 4.0)):
            at = base + int(dt * SR)
            if at < n:
                x += thump(n, at, 46, decay, amp, 0.4, rng)
                k = min(n - at, int(0.05 * SR))                   # the belt slapping on its repair
                x[at:at + k] += bandpass_fast(rng.normal(size=k), 400, 2500) * np.exp(-np.arange(k) / (0.01 * SR)) * 0.25
    hum = np.sin(2 * np.pi * 50 * np.arange(n) / SR) * 0.06
    return lowpass_fast(x + hum, 900)


def clock_punch(seconds=0.9):
    """The time clock (l. 481): a lever pressed, the mechanism claps, the ribbon, a spring back."""
    rng = np.random.default_rng(43)
    n = int(seconds * SR)
    x = np.zeros(n)
    for (dt, amp, lo, hi, dec) in ((0.0, 0.4, 800, 5000, 0.01), (0.18, 1.0, 300, 4000, 0.02), (0.22, 0.6, 1500, 8000, 0.005),
                                   (0.55, 0.35, 700, 3000, 0.02)):
        at = int(dt * SR)
        k = n - at
        x[at:] += bandpass_fast(rng.normal(size=k), lo, hi) * np.exp(-np.arange(k) / (dec * SR)) * amp
    return declick(x, 0.001, 0.05)


def keys(seconds=0.8):
    """A key taken off its hook; copper tags against each other."""
    rng = np.random.default_rng(44)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for dt in (0.0, 0.07, 0.16, 0.3, 0.41):
        at = int(dt * SR)
        tt = t[at:] - dt
        f = rng.uniform(2200, 4200)
        x[at:] += (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.51 * tt)) * np.exp(-tt * rng.uniform(25, 45)) * rng.uniform(0.4, 1.0)
    return declick(x, 0.001, 0.05)


def turnstile(seconds=1.1):
    """The bar of a turnstile pushed round, the counter drum turning one notch (l. 531)."""
    rng = np.random.default_rng(45)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    grind = bandpass_fast(rng.normal(size=n), 200, 1800) * np.exp(-((t - 0.35) / 0.25) ** 2) * 0.6
    x = grind
    for dt in (0.62, 0.66):
        at = int(dt * SR)
        k = n - at
        x[at:] += bandpass_fast(rng.normal(size=k), 1000, 6000) * np.exp(-np.arange(k) / (0.006 * SR))
    return declick(x, 0.002, 0.08)


def jukebox_key(seconds=0.5):
    """A yellowed key of the juke-box pressed: a dead click, nothing behind it (l. 547)."""
    rng = np.random.default_rng(46)
    n = int(seconds * SR)
    x = bandpass_fast(rng.normal(size=n), 600, 4000) * np.exp(-np.arange(n) / (0.012 * SR))
    at = int(0.12 * SR)
    x[at:] += bandpass_fast(rng.normal(size=n - at), 400, 2500) * np.exp(-np.arange(n - at) / (0.01 * SR)) * 0.5
    return declick(x, 0.001, 0.05)


def knocks(seconds=4.0):
    """The motor answers by three knocks (l. 549), deep under the floor."""
    rng = np.random.default_rng(47)
    n = int(seconds * SR)
    x = np.zeros(n)
    for dt in (0.2, 1.0, 1.8):
        x += thump(n, int(dt * SR), 38, 5.0, 1.0, 0.6, rng)
    return declick(lowpass_fast(x, 400), 0.005, 0.4)


def lock(seconds=1.8):
    """A key turned hard with both hands; the lock gives way at once (l. 551)."""
    rng = np.random.default_rng(48)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    strain = bandpass_fast(rng.normal(size=n), 300, 2500) * np.exp(-((t - 0.6) / 0.35) ** 2) * 0.5
    at = int(1.05 * SR)
    snap = np.zeros(n)
    snap[at:] = bandpass_fast(rng.normal(size=n - at), 200, 5000) * np.exp(-np.arange(n - at) / (0.02 * SR)) * 1.2
    return declick(strain + snap, 0.002, 0.1)


def rail(seconds=2.5):
    """A light vibration in the rail under the hand (l. 463): a faint tone through the metal."""
    rng = np.random.default_rng(49)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 92 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t)) + bandpass_fast(rng.normal(size=n), 60, 300) * 0.4
    return declick(x * np.minimum(1, t / 0.4) * np.minimum(1, (seconds - t) / 0.6), 0.01, 0.1)


def tarp(seconds=1.0):
    """The tarpaulin pulled off the juke-box: heavy cloth, dust."""
    rng = np.random.default_rng(50)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = bandpass_fast(rng.normal(size=n), 250, 5000) * np.exp(-((t - 0.35) / 0.22) ** 2)
    return declick(x, 0.005, 0.1)


# ----------------------------------------------------------------------------- RF05
def motor_stop(seconds=4.0):
    """The lever pulled to ARRET (l. 583): the motor slows, the belt claps three more times, the wheel stops."""
    rng = np.random.default_rng(51)
    n = int(seconds * SR)
    x = np.zeros(n)
    for k, dt in enumerate((0.0, 0.7, 1.6)):
        x += thump(n, int(dt * SR), 46 - 6 * k, 6.0, 1.0 - 0.2 * k, 0.5, rng)
    t = np.arange(n) / SR
    whine = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t / 1.2)) / SR) * np.exp(-t / 1.4) * 0.2
    return declick(lowpass_fast(x + whine, 1200), 0.005, 0.5)


def motor_start(seconds=4.0):
    """The lever pushed to MARCHE (l. 681): a jolt, a quarter turn, a stop, then the rhythm steadies."""
    rng = np.random.default_rng(52)
    n = int(seconds * SR)
    x = np.zeros(n)
    for dt, amp in ((0.0, 1.2), (0.25, 0.5), (1.1, 1.0), (1.7, 0.9), (2.3, 0.9), (2.9, 0.9), (3.5, 0.9)):
        x += thump(n, int(dt * SR), 46, 7.0, amp, 0.5, rng)
    return declick(lowpass_fast(x, 1200), 0.005, 0.3)


def waves(seconds=10.0):
    """In the silence, a sound of waves (l. 707): surf on a shore, far, then nearer."""
    rng = np.random.default_rng(53)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    surf = bandpass_fast(rng.normal(size=n), 150, 2500)
    env = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 5.5 - 1.5)) ** 2
    return seamless(surf * env * np.minimum(1, t / 2.5), 1.5)


def bulbs(seconds=3.0):
    """The bulbs come on one by one, each with its small delay (l. 687): clicks and a rising hum."""
    rng = np.random.default_rng(54)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 100 * t) * np.minimum(1, t / 2.0) * 0.15
    for k in range(18):
        at = int((0.08 + k * 0.14 + rng.uniform(0, 0.05)) * SR)
        m = min(n - at, int(0.02 * SR))
        x[at:at + m] += bandpass_fast(rng.normal(size=m), 2000, 8000) * np.exp(-np.arange(m) / (0.003 * SR)) * 0.6
    return declick(x, 0.002, 0.3)


def brake(seconds=0.8):
    """The automatic brake of the roller coaster claps as the train passes (l. 693)."""
    rng = np.random.default_rng(55)
    n = int(seconds * SR)
    x = bandpass_fast(rng.normal(size=n), 500, 6000) * np.exp(-np.arange(n) / (0.03 * SR))
    t = np.arange(n) / SR
    x += np.sin(2 * np.pi * 820 * t) * np.exp(-t * 18) * 0.3
    return declick(x, 0.001, 0.1)


def fans(seconds=6.0):
    """The modern box: 40 mm fans and the hum of its supplies (l. 565)."""
    rng = np.random.default_rng(56)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = bandpass_fast(rng.normal(size=n), 1500, 7000) * 0.3 + np.sin(2 * np.pi * 180 * t) * 0.08 + np.sin(2 * np.pi * 7200 * t) * 0.02
    return seamless(x, 1.0)


# ----------------------------------------------------------------------------- RF06
def vent(seconds=10.0):
    """The ventilation of a hotel (l. 713): a steady low air, a fan's hum, a faint rattle of a grille."""
    rng = np.random.default_rng(57)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    air = lowpass_fast(rng.normal(size=n), 400) * 2.0
    hum = np.sin(2 * np.pi * 58 * t) * 0.25 + np.sin(2 * np.pi * 116 * t) * 0.1
    rattle = bandpass_fast(rng.normal(size=n), 1800, 3500) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) * 0.05
    return seamless(air + hum + rattle, 1.5)


def rumble(seconds=7.0):
    """The train of the roller coaster passes once more behind him; the rumble goes on under the corridor and becomes
    the ventilation of a hotel (l. 713)."""
    rng = np.random.default_rng(58)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    train = lowpass_fast(rng.normal(size=n), 120) * 6 * np.exp(-((t - 1.5) / 1.2) ** 2)
    clack = np.zeros(n)
    for k in range(10):
        at = int((0.5 + k * 0.22) * SR)
        m = min(n - at, int(0.03 * SR))
        clack[at:at + m] += bandpass_fast(rng.normal(size=m), 300, 2500) * np.exp(-np.arange(m) / (0.006 * SR)) * 0.4
    fan = (lowpass_fast(rng.normal(size=n), 400) * 2.0 + np.sin(2 * np.pi * 58 * t) * 0.25) * np.clip((t - 2.5) / 3.0, 0, 1)
    return declick(train + clack + fan, 0.01, 0.8)


def main():
    write_wav('park_loop.wav', park_loop(), 0.55)
    write_wav('motor_loop.wav', motor_loop(), 0.8)
    write_wav('clock.wav', clock_punch(), 0.8)
    write_wav('keys.wav', keys(), 0.6)
    write_wav('turnstile.wav', turnstile(), 0.7)
    write_wav('jukebox_key.wav', jukebox_key(), 0.6)
    write_wav('knocks.wav', knocks(), 0.9)
    write_wav('lock.wav', lock(), 0.8)
    write_wav('rail.wav', rail(), 0.5)
    write_wav('tarp.wav', tarp(), 0.6)
    write_wav('motor_stop.wav', motor_stop(), 0.9)
    write_wav('motor_start.wav', motor_start(), 0.9)
    write_wav('waves_loop.wav', waves(), 0.6)
    write_wav('bulbs.wav', bulbs(), 0.6)
    write_wav('brake.wav', brake(), 0.7)
    write_wav('fans_loop.wav', fans(), 0.35)
    write_wav('vent_loop.wav', vent(), 0.5)
    write_wav('rumble.wav', rumble(), 0.85)
    print('RF04 sounds written to', OUT)


if __name__ == '__main__':
    main()
