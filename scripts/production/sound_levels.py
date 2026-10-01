#!/usr/bin/env python3
"""Signal measures of sound files (no listening): format, duration, peak and RMS in dBFS, attack time to the peak.

Reads WAV files from folders or from a pk3 (zip), for the routing tables handed to the sound authors: they say where
each existing sound stands, so that a replacement keeps or corrects its level on purpose. Measures only; a level is
not a verdict on how the sound reads in the game.

Usage: python scripts/production/sound_levels.py <folder|file.pk3> [prefix filter ...] > table.md
"""
import io, math, struct, sys, wave, zipfile
from pathlib import Path


def measure(data):
    with wave.open(io.BytesIO(data)) as w:
        ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if width == 2:
        vals = struct.unpack(f'<{len(raw) // 2}h', raw)
        full = 32768.0
    elif width == 3:
        vals = [int.from_bytes(raw[i:i + 3], 'little', signed=True) for i in range(0, len(raw), 3)]
        full = 8388608.0
    elif width == 1:
        vals = [b - 128 for b in raw]
        full = 128.0
    else:
        vals = struct.unpack(f'<{len(raw) // 4}i', raw)
        full = 2147483648.0
    mono = [sum(vals[i:i + ch]) / ch for i in range(0, len(vals), ch)] if ch > 1 else list(vals)
    if not mono:
        return dict(rate=rate, ch=ch, bits=width * 8, ms=0, peak=-120.0, rms=-120.0, attack_ms=0)
    peak_i = max(range(len(mono)), key=lambda i: abs(mono[i]))
    peak = abs(mono[peak_i]) / full
    rms = math.sqrt(sum(v * v for v in mono) / len(mono)) / full
    db = lambda x: 20 * math.log10(x) if x > 0 else -120.0
    return dict(rate=rate, ch=ch, bits=width * 8, ms=round(1000 * len(mono) / rate), peak=round(db(peak), 1),
                rms=round(db(rms), 1), attack_ms=round(1000 * peak_i / rate))


def files(src):
    p = Path(src)
    if p.suffix.lower() == '.pk3':
        z = zipfile.ZipFile(p)
        for name in sorted(z.namelist()):
            if name.lower().endswith('.wav'):
                yield name, z.read(name)
    else:
        for f in sorted(p.rglob('*.wav')):
            yield f.relative_to(p).as_posix(), f.read_bytes()


def main():
    src, filters = sys.argv[1], sys.argv[2:]
    print('| Fichier | Format | Durée (ms) | Crête (dBFS) | RMS (dBFS) | Crête à (ms) |')
    print('|---|---|---|---|---|---|')
    for name, data in files(src):
        if filters and not any(f in name for f in filters):
            continue
        try:
            r = measure(data)
        except Exception as e:      # noqa: BLE001 - a broken file is reported, not fatal
            print(f'| `{name}` | illisible ({e}) | | | | |')
            continue
        print(f"| `{name}` | {r['rate']} Hz, {r['bits']} bits, {'mono' if r['ch'] == 1 else str(r['ch']) + ' canaux'} | "
              f"{r['ms']} | {r['peak']} | {r['rms']} | {r['attack_ms']} |")


if __name__ == '__main__':
    main()
