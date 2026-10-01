#!/usr/bin/env python3
"""PROVISIONAL images and sounds of the boss bench (Opus, procedural): the surveillant-chef as a silhouette, one view,
the frames of every state; his register, stamp and whistle as plain synthesized sounds. Codex's candidate visual and
sounds replace them under the same names (FICHE_BOSS_SURVEILLANT.md). Nothing here is a final asset.

Usage: python bench/boss/materials_boss.py   (writes bench/boss/sprites/*.png, bench/boss/sounds/*.wav)
"""
import sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
from materials import png_with_grab  # noqa: E402

SPR = HERE / 'sprites'
SND = HERE / 'sounds'
SR = 48000
COAT, COLLAR, CAP, SKIN, TROUSERS = (58, 64, 72, 255), (214, 210, 198, 255), (24, 24, 28, 255), (190, 150, 124, 255), (34, 34, 38, 255)
BRASS, LEDGER, KEYS = (196, 160, 70, 255), (96, 30, 26, 255), (176, 150, 80, 255)


def figure(pose):
    """A big man in the grey coat of the head attendant, white collar band, cap; the ring of keys at his belt; the
    register under his arm or open; the brass stamp; the whistle. 128 x 176 canvas, soles at the bottom."""
    img = Image.new('RGBA', (128, 176), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lean = {'G': 6, 'I': 4, 'K': -4}.get(pose, 0)
    step = {'B': 4, 'C': 0, 'D': -4, 'E': 0}.get(pose, 0)
    if pose in 'LMNO':
        if pose == 'O':                                                       # lying, the register beside him
            d.rounded_rectangle([14, 150, 114, 170], 8, fill=COAT)
            d.ellipse([100, 146, 124, 168], fill=SKIN)
            d.rectangle([20, 162, 50, 172], fill=LEDGER)
            return img
        drop = {'L': 12, 'M': 40, 'N': 80}[pose]
        d.rounded_rectangle([34, 30 + drop, 94, 120 + drop // 2], 10, fill=COAT)
        d.ellipse([46, 6 + drop, 82, 40 + drop], fill=SKIN)
        return img
    d.rectangle([40 + step, 120, 58 + step, 170], fill=TROUSERS)              # legs
    d.rectangle([70 - step, 120, 88 - step, 170], fill=TROUSERS)
    d.rectangle([36 + step, 166, 60 + step, 176], fill=(18, 18, 18, 255))
    d.rectangle([68 - step, 166, 92 - step, 176], fill=(18, 18, 18, 255))
    d.rounded_rectangle([30 + lean, 40, 98 + lean, 132], 10, fill=COAT)       # the long coat, wide shoulders
    d.rectangle([52 + lean, 40, 76 + lean, 50], fill=COLLAR)                  # the white collar band
    d.ellipse([46 + lean, 8, 82 + lean, 44], fill=SKIN)                       # head
    d.rectangle([44 + lean, 6, 84 + lean, 18], fill=CAP)                      # cap and visor
    d.rectangle([40 + lean, 16, 70 + lean, 20], fill=CAP)
    d.rectangle([54 + lean, 32, 74 + lean, 35], fill=(120, 110, 100, 255))    # moustache
    d.ellipse([84 + lean, 100, 100 + lean, 116], outline=KEYS, width=3)       # the ring of keys
    if pose in 'AB CDE':
        d.rectangle([18 + lean, 64, 34 + lean, 104], fill=LEDGER)             # the register under his arm
    if pose == 'F':                                                           # stamp raised over his head
        d.rectangle([92, 0, 104, 30], fill=COAT)
        d.rectangle([86, 0, 110, 12], fill=BRASS)
    if pose == 'G':                                                           # stamp down at his feet
        d.rectangle([96, 100, 108, 160], fill=COAT)
        d.rectangle([90, 156, 114, 168], fill=BRASS)
    if pose in 'HI':                                                          # the register open / a register thrown
        d.rectangle([6, 60, 50, 90], fill=LEDGER)
        d.line([(28, 60), (28, 90)], fill=(220, 210, 190, 255), width=2)
        if pose == 'I':
            d.rectangle([100, 50, 124, 66], fill=LEDGER)
    if pose == 'J':                                                           # the whistle at his mouth
        d.rectangle([76, 30, 96, 36], fill=BRASS)
        d.rectangle([84 + lean, 34, 98 + lean, 70], fill=COAT)
    if pose == 'K':                                                           # struck: cap knocked aside
        d.rectangle([84, 2, 112, 12], fill=CAP)
    return img


def sprites():
    SPR.mkdir(parents=True, exist_ok=True)
    for pose in 'ABCDEFGHIJKLMNO':
        png_with_grab(figure(pose), 64, 174, SPR / f'BSSV{pose}0.png')
    for k, ang in enumerate((0, 25, 50)):                                    # the bound register in flight
        img = Image.new('RGBA', (48, 32), (0, 0, 0, 0))
        r = Image.new('RGBA', (34, 18), LEDGER)
        ImageDraw.Draw(r).line([(0, 9), (34, 9)], fill=(150, 120, 80, 255), width=2)
        img.paste(r.rotate(ang, expand=True).resize((34, 18)), (7, 7))
        png_with_grab(img, 24, 24, SPR / f'BSLG{"ABC"[k]}0.png')
    ring = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([8, 8, 120, 120], outline=(230, 220, 190, 200), width=6)
    png_with_grab(ring, 64, 64, SPR / 'BSWVA0.png')


def write(name, x, peak=0.85):
    SND.mkdir(parents=True, exist_ok=True)
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.max(np.abs(x)) or 1) * peak
    fade = min(len(x), int(0.004 * SR))
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(SND / name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode='same')


def sounds():
    rng = np.random.default_rng(901)
    t = lambda s: np.arange(int(s * SR)) / SR
    tt = t(0.6)
    write('stamp.wav', np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 9) + 0.6 * lp(rng.normal(size=tt.size), 6) * np.exp(-tt * 40), 0.95)
    tt = t(0.3)
    write('ink.wav', lp(rng.normal(size=tt.size), 30) * np.exp(-((tt - 0.12) / 0.06) ** 2), 0.5)
    tt = t(0.5)
    flutter = (np.sin(2 * np.pi * 18 * tt) > 0.2) * 1.0
    write('ledger_open.wav', lp(rng.normal(size=tt.size), 4) * flutter * np.exp(-tt * 4), 0.55)
    tt = t(0.35)
    write('throw.wav', lp(rng.normal(size=tt.size), 12) * np.sin(np.pi * tt / 0.35), 0.4)
    tt = t(0.25)
    write('ledger_hit.wav', np.sin(2 * np.pi * 120 * tt) * np.exp(-tt * 30) + 0.5 * rng.normal(size=tt.size) * np.exp(-tt * 60), 0.6)
    tt = t(1.3)
    trill = 1 + 0.03 * np.sin(2 * np.pi * 28 * tt)
    env = np.minimum(1, tt / 0.03) * np.where(tt < 0.55, 1, np.where(tt < 0.62, 0.1, 1)) * np.exp(-np.maximum(tt - 1.1, 0) * 30)
    write('whistle.wav', np.sin(2 * np.pi * 2900 * trill * tt) * env + 0.05 * rng.normal(size=tt.size) * env, 0.6)
    tt = t(0.4)
    write('whistle_short.wav', np.sin(2 * np.pi * 2900 * (1 + 0.03 * np.sin(2 * np.pi * 28 * tt)) * tt) * np.minimum(1, tt / 0.02) * np.exp(-tt * 3), 0.55)
    tt = t(0.5)
    write('pain.wav', lp(rng.normal(size=tt.size), 40) * np.exp(-tt * 6) + 0.3 * np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 8), 0.7)
    tt = t(1.2)
    jingle = sum(np.sin(2 * np.pi * f * tt) * np.exp(-(tt - a) * 12) * (tt > a) for f, a in ((2400, 0.4), (3100, 0.45), (2700, 0.52)))
    write('death.wav', np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 5) + 0.3 * jingle, 0.8)
    tt = t(0.3)
    write('step.wav', np.sin(2 * np.pi * 80 * tt) * np.exp(-tt * 25) + 0.2 * lp(rng.normal(size=tt.size), 8) * np.exp(-tt * 50), 0.5)


if __name__ == '__main__':
    sprites()
    sounds()
    print('boss bench materials:', len(list(SPR.glob('*.png'))), 'sprites,', len(list(SND.glob('*.wav'))), 'sounds')
