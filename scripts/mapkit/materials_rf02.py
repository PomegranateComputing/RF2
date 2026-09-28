#!/usr/bin/env python3
"""RF02 material family: Paris, 14 June 1940, from the boulevard Arago to the Porte Maillot.

Same procedural method and calibration as the RF01 family (scripts/mapkit/materials.py, whose pure helpers are
imported; it is never run from here, so no RF01 texture is rewritten). Slightly darker and dirtier than RF01,
because the place asks for it: smoke over the city, soot on the facades, paper tape across the shop windows.
Every inscription is composed with a real font from the text of the novel (docs/production/maps/RF02_FICHE.md),
never generated.

Output: src/patches/rf02/*.png, src/TEXTURES.rf02, src/textures/RFSKY2.png, src/sprites/rf02/*.png
Usage: python scripts/mapkit/materials_rf02.py
"""
import math
import zlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from materials import fbm, grain, to_img, solid, tint, plaster, floor_grime, stone_blocks, cobbles, planks, _draw_window, png_with_grab  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / 'src' / 'patches' / 'rf02'
SPRITES = ROOT / 'src' / 'sprites' / 'rf02'
PPU = 4
DEFS = []


def save(kind, name, arr, ppu=PPU, masked=False):
    img = arr if isinstance(arr, Image.Image) else to_img(arr)
    PATCH.mkdir(parents=True, exist_ok=True)
    img.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append((kind, name, img.size[0], img.size[1], ppu))
    return img


def font(size, bold=True, face=None):
    for f in ([face] if face else []) + (['C:/Windows/Fonts/arialbd.ttf'] if bold else ['C:/Windows/Fonts/arial.ttf']) + ['C:/Windows/Fonts/arial.ttf']:
        try:
            return ImageFont.truetype(f, size)
        except (OSError, TypeError):
            continue
    return ImageFont.load_default()


NARROW = 'C:/Windows/Fonts/ARIALNB.TTF'


def fitted(d, text, fnt, width):
    """The same face, smaller until the text fits the width (an inscription never runs off its panel)."""
    while fnt.size > 6 and d.textbbox((0, 0), text, font=fnt)[2] - d.textbbox((0, 0), text, font=fnt)[0] > width:
        fnt = ImageFont.truetype(fnt.path, int(fnt.size * 0.93))
    return fnt


def text_center(d, box, text, fnt, fill):
    x0, y0, x1, y1 = box
    if hasattr(fnt, 'path'):
        fnt = fitted(d, text, fnt, (x1 - x0) * 0.94)
    b = d.textbbox((0, 0), text, font=fnt)
    d.text(((x0 + x1 - (b[2] - b[0])) / 2 - b[0], (y0 + y1 - (b[3] - b[1])) / 2 - b[1]), text, font=fnt, fill=fill)


def soot(arr, seed, amount=0.22, top=True):
    """Soot and smoke deposit: darker toward the top of a facade, blotchy."""
    h, w = arr.shape[:2]
    n = fbm(h, w, seed, 2.3)[..., None]
    yv = np.linspace(0, 1, h)[:, None, None]
    grad = np.clip(1 - yv * 1.4, 0, 1) if top else np.ones_like(yv)
    return arr * (1 - amount * grad * (0.5 + n))


# ----------------------------------------------------------------------------- sky
def sky_smoke():
    """Overcast morning under the smoke of the burnt fuel depots: low brown-grey, heavier to the north."""
    W, H = 1024, 256
    y = np.linspace(0, 1, H)[:, None]
    top = np.array((88, 86, 84)) / 255.0
    bottom = np.array((162, 156, 146)) / 255.0
    img = top * (1 - y)[..., None] + bottom * y[..., None]
    c1 = fbm(H, W, 7101, 2.6)
    c2 = fbm(H, W, 7102, 1.8)
    smoke = np.clip((c1 - 0.42) * 2.0 + (c2 - 0.5) * 0.5, 0, 1)[..., None]
    img = img * (1 - smoke * 0.42) + np.array((58, 52, 48)) / 255.0 * smoke * 0.42
    light = np.clip((fbm(H, W, 7103, 3.0) - 0.6) * 3, 0, 1)[..., None] * (y[..., None] ** 0.5)
    img = img + light * np.array((40, 36, 28)) / 255.0
    img = np.clip(img + grain(H, W, 7104, 0.01)[..., None], 0, 1)
    (ROOT / 'src' / 'textures').mkdir(parents=True, exist_ok=True)
    to_img(img).save(ROOT / 'src' / 'textures' / 'RFSKY2.png')


# ----------------------------------------------------------------------------- facades
def taped_window(d, x0, y0, w, h, s, rng, lit=False):
    """Shop window glass with the paper tape crosses meant to hold the splinters."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 42, 44) if not lit else (70, 64, 50))
    for k in range(3):
        gy = y0 + int(h * (0.12 + 0.3 * k))
        d.line([(x0 + 2 * s, gy), (x0 + w - 2 * s, gy + 6 * s)], fill=(64, 68, 72), width=max(1, s))
    tape = (206, 196, 168)
    tw = max(2, int(2.2 * s))
    d.line([(x0, y0), (x0 + w, y0 + h)], fill=tape, width=tw)
    d.line([(x0 + w, y0), (x0, y0 + h)], fill=tape, width=tw)
    if rng.random() < 0.5:
        d.line([(x0 + w // 2, y0), (x0 + w // 2, y0 + h)], fill=tape, width=tw)


def facade(name, seed, shops='mixed', wunits=256, hunits=448, ppu=2):
    """Parisian street facade, 14 June 1940, sootier than the RF01 street: ground floor of shop fronts (iron
    shutters down, or taped windows), four floors of French windows, most shutters closed, zinc roof."""
    W, H = wunits * ppu, hunits * ppu
    rng = np.random.default_rng(seed)
    img = plaster(H, W, seed, (184, 174, 154), 0.14, 0.26)
    img = soot(img, seed + 4, 0.26)
    pil = to_img(img)
    d = ImageDraw.Draw(pil)

    def Y(u):
        return H - int(u * ppu)
    d.rectangle([0, Y(8), W, H], fill=(84, 82, 78))
    bay = W // 2
    for b in range(2):
        x0 = b * bay + 10 * ppu
        x1 = x0 + bay - 44 * ppu
        paint = [(52, 66, 56), (84, 36, 32), (42, 46, 60), (70, 58, 44)][int(rng.integers(0, 4))]
        d.rectangle([x0, Y(100), x1, Y(8)], fill=paint)
        if shops == 'shutters' or (shops == 'mixed' and rng.random() < 0.5):
            d.rectangle([x0 + 4 * ppu, Y(92), x1 - 4 * ppu, Y(12)], fill=(112, 114, 112))
            for yy in range(Y(92), Y(12), 3 * ppu):
                d.line([(x0 + 4 * ppu, yy), (x1 - 4 * ppu, yy)], fill=(84, 86, 86), width=max(1, ppu // 2))
        else:
            taped_window(d, x0 + 4 * ppu, Y(92), x1 - x0 - 8 * ppu, 76 * ppu, ppu, rng)
        d.rectangle([x0 + 4 * ppu, Y(100), x1 - 4 * ppu, Y(94)], fill=tuple(min(255, int(c * 1.2)) for c in paint))
        dx = x1 + 8 * ppu
        d.rectangle([dx, Y(92), dx + 24 * ppu, Y(8)], fill=(62, 48, 36))
        d.rectangle([dx + 3 * ppu, Y(86), dx + 21 * ppu, Y(50)], outline=(46, 36, 28), width=ppu)
        d.rectangle([dx + 3 * ppu, Y(44), dx + 21 * ppu, Y(14)], outline=(46, 36, 28), width=ppu)
    d.rectangle([0, Y(112), W, Y(104)], fill=(160, 150, 132))
    for f in range(4):
        base = 124 + f * 70
        d.line([(0, Y(base - 4)), (W, Y(base - 4))], fill=(150, 142, 124), width=2 * ppu)
        for k in range(4):
            wx = int((k + 0.5) * W / 4) - 13 * ppu
            state = 'closed' if rng.random() < 0.7 else ('open' if rng.random() < 0.5 else 'none')
            _draw_window(d, wx, Y(base + 52), 26 * ppu, 50 * ppu, ppu, rng, state)
    d.rectangle([0, Y(410), W, Y(402)], fill=(132, 126, 112))
    d.line([(0, Y(402)), (W, Y(402))], fill=(70, 66, 62), width=2 * ppu)
    d.rectangle([0, 0, W, Y(410)], fill=(96, 102, 108))
    for k in range(4):
        cx = int((k + 0.5) * W / 4)
        d.rectangle([cx - 9 * ppu, Y(440), cx + 9 * ppu, Y(412)], fill=(108, 112, 118))
        d.rectangle([cx - 5 * ppu, Y(436), cx + 5 * ppu, Y(416)], fill=(38, 40, 44))
    arr = np.asarray(pil).astype(float) / 255.0
    arr = floor_grime(arr, 0.34, 0.08)
    save('Texture', name, arr, ppu=ppu)


def upper_facade(name, seed, wunits=256, hunits=448, ppu=2):
    """Same facade without a ground floor: over real shop fronts built in geometry (the openings are cells)."""
    W, H = wunits * ppu, hunits * ppu
    rng = np.random.default_rng(seed)
    img = plaster(H, W, seed, (180, 170, 150), 0.14, 0.28)
    img = soot(img, seed + 5, 0.28)
    pil = to_img(img)
    d = ImageDraw.Draw(pil)

    def Y(u):
        return H - int(u * ppu)
    d.rectangle([0, Y(128), W, Y(0)], fill=(150, 140, 122))                 # stone band over the shop fronts
    d.line([(0, Y(128)), (W, Y(128))], fill=(110, 104, 92), width=ppu)
    for f in range(4):
        base = 140 + f * 66
        d.line([(0, Y(base - 4)), (W, Y(base - 4))], fill=(146, 138, 120), width=2 * ppu)
        for k in range(4):
            wx = int((k + 0.5) * W / 4) - 13 * ppu
            state = 'closed' if rng.random() < 0.7 else ('open' if rng.random() < 0.5 else 'none')
            _draw_window(d, wx, Y(base + 50), 26 * ppu, 48 * ppu, ppu, rng, state)
    d.rectangle([0, Y(410), W, Y(402)], fill=(128, 122, 108))
    d.rectangle([0, 0, W, Y(410)], fill=(94, 100, 106))
    arr = np.asarray(pil).astype(float) / 255.0
    save('Texture', name, arr, ppu=ppu)


def prison_wall(name, seed, wunits=256, hunits=384, ppu=2):
    """Enclosure wall of the Santé: tall millstone and limestone, a coping, rain streaks, no window."""
    W, H = wunits * ppu, hunits * ppu
    arr = stone_blocks(H, W, seed, 24, 56, (150, 140, 124), (98, 92, 84))
    arr = soot(arr, seed + 1, 0.3, top=False)
    streak = fbm(H, W, seed + 2, 1.2)[..., None]
    xs = np.linspace(0, 1, W)[None, :, None]
    lines = (np.sin(xs * 90 + streak[..., :1] * 6) > 0.92).astype(float)
    arr = arr * (1 - 0.12 * lines * np.linspace(1, 0.2, H)[:, None, None])
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W, 10 * ppu], fill=(118, 112, 102))                   # coping
    d.line([(0, 10 * ppu), (W, 10 * ppu)], fill=(70, 66, 60), width=2 * ppu)
    save('Texture', name, np.asarray(pil).astype(float) / 255.0, ppu=ppu)


def prison_gate(name, seed, wunits=128, hunits=192, ppu=4):
    """The great gate of the Santé, closed: studded iron-strapped wood, a wicket door, a stone arch."""
    W, H = wunits * ppu, hunits * ppu
    rng = np.random.default_rng(seed)
    arr = stone_blocks(H, W, seed, 32, 48, (160, 150, 134), (100, 94, 86))
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)
    gx0, gx1, gy0 = 12 * ppu, W - 12 * ppu, 20 * ppu
    d.rectangle([gx0, gy0, gx1, H], fill=(46, 40, 34))
    wood = to_img(planks(H - gy0, gx1 - gx0, seed + 3, 10, (70, 54, 40)))
    pil.paste(wood, (gx0, gy0))
    d = ImageDraw.Draw(pil)
    for yy in range(gy0 + 18 * ppu, H, 36 * ppu):
        d.rectangle([gx0, yy, gx1, yy + 4 * ppu], fill=(38, 38, 40))
        for xx in range(gx0 + 4 * ppu, gx1, 10 * ppu):
            d.ellipse([xx - ppu, yy + ppu, xx + ppu, yy + 3 * ppu], fill=(88, 86, 82))
    mid = (gx0 + gx1) // 2
    d.line([(mid, gy0), (mid, H)], fill=(26, 22, 20), width=2 * ppu)
    d.rectangle([mid + 10 * ppu, H - 70 * ppu, mid + 34 * ppu, H - 2 * ppu], outline=(26, 22, 20), width=ppu)   # wicket
    d.ellipse([mid + 28 * ppu, H - 38 * ppu, mid + 31 * ppu, H - 35 * ppu], fill=(120, 110, 80))
    arr = np.asarray(pil).astype(float) / 255.0
    arr = floor_grime(arr, 0.3, 0.12)
    save('Texture', name, arr)


# ----------------------------------------------------------------------------- composed inscriptions
def stable(name):
    """Noise seed from a texture name, the same in every run (Python's hash() of a string changes from one
    process to the next: before 28/09 the plaques and fascias got a different grain at each generation)."""
    return zlib.crc32(name.encode('utf-8'))


def paris_plaque(name, text, arrondissement=0, wunits=64, hunits=24):
    """Paris street plaque: dark blue enamel, white condensed capitals, green frame; the arrondissement on top
    as on the real plaques ("13e Arrt", the e and the t raised)."""
    W, H = wunits * PPU, hunits * PPU
    pil = Image.new('RGB', (W, H), (26, 46, 86))
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 96, 62), width=2 * PPU)
    d.rectangle([3 * PPU, 3 * PPU, W - 3 * PPU - 1, H - 3 * PPU - 1], outline=(222, 224, 220), width=max(1, PPU // 2))
    ink = (236, 238, 234)
    if arrondissement:
        big, small = font(int(H * 0.2), face=NARROW), font(int(H * 0.12), face=NARROW)
        parts = [(str(arrondissement), big, 0), ('er' if arrondissement == 1 else 'e', small, -1), (' Arr', big, 0), ('t', small, -1)]
        widths = [d.textlength(s, font=f) for s, f, _ in parts]
        x, base = (W - sum(widths)) / 2, H * 0.30
        for (s, f, up), w in zip(parts, widths):
            d.text((x, base - (H * 0.07 if up else 0)), s, font=f, fill=ink, anchor='ls')
            x += w
        text_center(d, (5 * PPU, H * 0.34, W - 5 * PPU, H - 4 * PPU), text, font(int(H * 0.4), face=NARROW), ink)
    else:
        text_center(d, (5 * PPU, 0, W - 5 * PPU, H), text, font(int(H * 0.44), face=NARROW), ink)
    arr = np.asarray(pil).astype(float) / 255.0
    arr = arr * (0.92 + 0.14 * (fbm(H, W, stable(name) % 1000, 2.2)[..., None] - 0.5))
    save('Texture', name, np.clip(arr, 0, 1))


def fascia(name, text, bg, fg, wunits=128, hunits=16, gold=False):
    """Painted shop fascia lettering over a shop front."""
    W, H = wunits * PPU, hunits * PPU
    pil = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W - 1, H - 1], outline=tuple(int(c * 0.6) for c in bg), width=PPU)
    fnt = font(int(H * 0.62))
    if gold:
        text_center(d, (2, 2, W + 2, H + 2), text, fnt, (40, 30, 10))
    text_center(d, (0, 0, W, H), text, fnt, fg)
    arr = np.asarray(pil).astype(float) / 255.0
    arr = soot(arr, stable(name) % 997, 0.2, top=False)
    arr = arr * (0.9 + 0.2 * (fbm(H, W, stable(name) % 991, 2.0)[..., None] - 0.5))
    save('Texture', name, np.clip(arr, 0, 1))


def masked(name, img):
    """RGBA patch (paper, paint, stencil on a wall): masked middle texture on a decor line."""
    PATCH.mkdir(parents=True, exist_ok=True)
    img.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append(('Texture', name, img.size[0], img.size[1], PPU))


def torn_poster(name, lines, wunits=48, hunits=64, seed=1, bg=(222, 214, 190), ink=(24, 22, 22), torn=0.45):
    """Paper poster half torn off, glue marks around (INTERDICTION DE STATIONNER, mobilisation, ANNULÉ)."""
    W, H = wunits * PPU, hunits * PPU
    rng = np.random.default_rng(seed)
    paper = np.asarray(to_img(solid(H, W, bg) * (0.9 + 0.15 * (fbm(H, W, seed, 2.0)[..., None] - 0.5)))).copy()
    pil = Image.fromarray(paper).convert('RGBA')
    d = ImageDraw.Draw(pil)
    y = 8 * PPU
    for (txt, rel) in lines:
        f = font(int(rel * PPU))
        b = d.textbbox((0, 0), txt, font=f)
        while b[2] - b[0] > W - 8 * PPU and rel > 4:
            rel -= 1
            f = font(int(rel * PPU))
            b = d.textbbox((0, 0), txt, font=f)
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), txt, font=f, fill=ink + (255,))
        y += (b[3] - b[1]) + 4 * PPU
    a = np.full((H, W), 255, np.uint8)
    edge = fbm(H, W, seed + 9, 1.4)
    yy, xx = np.mgrid[:H, :W] / np.array([H, W])[:, None, None]
    tear = (yy + 0.35 * (edge - 0.5) + 0.25 * xx) > (1 - torn)                # the upper right part is torn away
    a[tear] = 0
    a[:, :2] = a[:, -2:] = 0
    out = np.asarray(pil).copy()
    out[..., 3] = a
    glue = (tear & (edge > 0.55))
    out[glue] = (150, 138, 110, 120)
    masked(name, Image.fromarray(out))


def brush_erreur(name, wunits=64, hunits=24, seed=7):
    """ERREUR Ø painted with a black brush at shoulder height on a grey iron shutter, fresh: one drop still
    runs under the R; the barred circle over-traced (novel l. 151-155)."""
    W, H = wunits * PPU * 2, hunits * PPU * 2
    rng = np.random.default_rng(seed)
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    f = font(int(H * 0.46))
    x = int(W * 0.05)
    base = int(H * 0.2)
    for i, ch in enumerate('ERREUR'):
        layer = Image.new('L', (W, H), 0)
        ld = ImageDraw.Draw(layer)
        ld.text((x, base + int(rng.normal(0, H * 0.012))), ch, font=f, fill=255)
        layer = layer.rotate(float(rng.normal(0, 2.5)), center=(x + H * 0.15, base + H * 0.25), resample=Image.BICUBIC)
        img = Image.fromarray(np.maximum(np.asarray(img), np.asarray(layer)))
        x += int(d.textlength(ch, font=f) * 0.98)
        if ch == 'R' and i == 5:
            rx = x - int(H * 0.12)
    d = ImageDraw.Draw(img)
    cx, cy, r = x + int(H * 0.36), base + int(H * 0.27), int(H * 0.2)
    for k in range(3):                                                        # the circle traced several times
        o = rng.normal(0, H * 0.012, 2)
        d.ellipse([cx - r + o[0], cy - r + o[1], cx + r + o[0], cy + r + o[1]], outline=255, width=int(H * 0.055))
    d.line([(cx - r * 1.25, cy + r * 1.25), (cx + r * 1.25, cy - r * 1.25)], fill=255, width=int(H * 0.06))
    d.line([(rx, base + int(H * 0.55)), (rx + 2, H - int(H * 0.06))], fill=255, width=int(H * 0.03))   # the running drop
    d.ellipse([rx - H * 0.02, H - int(H * 0.09), rx + H * 0.035, H - int(H * 0.03)], fill=255)
    m = np.asarray(img.filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255.0
    rough = fbm(H, W, seed + 3, 1.2)
    m = np.clip(m * (0.85 + 0.3 * rough) - 0.08, 0, 1)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (12, 12, 13)
    rgba[..., 3] = (m * 245).astype(np.uint8)
    masked(name, Image.fromarray(rgba).resize((W // 2, H // 2), Image.LANCZOS))


def stencil(name, text, arrow='left', wunits=64, hunits=24, col=(236, 232, 220)):
    """Civil-defence stencil on a wall: capitals and an arrow (CAVE, POSTE DE SECOURS, EAU)."""
    W, H = wunits * PPU, hunits * PPU
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(int(H * 0.42))
    text_center(d, (0, 0, W, H * 0.62), text, f, col + (230,))
    y = int(H * 0.8)
    x0, x1 = int(W * 0.2), int(W * 0.8)
    d.line([(x0, y), (x1, y)], fill=col + (230,), width=int(H * 0.08))
    tip = x0 if arrow == 'left' else x1
    s = 1 if arrow == 'left' else -1
    d.polygon([(tip - s * H * 0.04, y), (tip + s * H * 0.16, y - H * 0.13), (tip + s * H * 0.16, y + H * 0.13)], fill=col + (230,))
    a = np.asarray(img).copy()
    a[..., 3] = (a[..., 3] * np.clip(0.75 + 0.4 * (fbm(H, W, len(text), 1.5) - 0.5), 0, 1)).astype(np.uint8)
    masked(name, Image.fromarray(a))


# ----------------------------------------------------------------------------- street surfaces
def asphalt(h, w, seed, rgb=(78, 76, 74)):
    img = solid(h, w, rgb)
    img = img * (0.88 + 0.24 * (fbm(h, w, seed, 2.2)[..., None] - 0.5))
    wet = np.clip((fbm(h, w, seed + 1, 2.8) - 0.62) * 3, 0, 1)[..., None]
    img = img * (1 - 0.25 * wet)
    img += grain(h, w, seed + 2, 0.05)[..., None]
    return np.clip(img, 0, 1)


def rails(h, w, seed):
    """Setts with the two grooved tram rails running along X."""
    img = cobbles(h, w, seed, 8, 12)
    for yc in (0.3, 0.7):
        y0 = int(h * yc)
        img[y0 - 3 * PPU:y0 + 3 * PPU] = np.array((96, 92, 86)) / 255.0
        img[y0 - PPU:y0 + PPU] = np.array((138, 136, 132)) / 255.0
        img[y0 + PPU:y0 + 2 * PPU] = np.array((28, 26, 24)) / 255.0
    return np.clip(img + grain(h, w, seed + 4, 0.02)[..., None], 0, 1)


def water(h, w, seed):
    """The Seine under a smoky sky: olive-brown water, pale streaks of reflected sky, fine ripples."""
    img = solid(h, w, (52, 58, 44))
    img = img * (0.8 + 0.4 * (fbm(h, w, seed, 2.0)[..., None] - 0.5))
    streak = fbm(h, w, seed + 1, 1.0)[..., None]
    img = img + np.array((70, 76, 78)) / 255.0 * np.clip((streak - 0.62) * 2.5, 0, 1)
    yy = np.arange(h)[:, None, None]
    ripple = (np.sin(yy * 0.9 + fbm(h, w, seed + 2, 3.0)[..., None] * 6) > 0.85).astype(float)
    img = img + ripple * 0.05
    return np.clip(img, 0, 1)


# ----------------------------------------------------------------------------- vehicles and objects
def tram_side(name, seed, wunits=128, hunits=128):
    """Tram body, 1930s Paris colours: dark green lower panels, cream window band, rivets, number 1117."""
    W, H = wunits * PPU, hunits * PPU
    arr = solid(H, W, (38, 62, 48)) * (0.9 + 0.2 * (fbm(H, W, seed, 2.0)[..., None] - 0.5))
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)

    def Y(u):
        return H - int(u * PPU)
    d.rectangle([0, Y(128), W, Y(96)], fill=(196, 186, 156))                 # upper band (cream)
    d.rectangle([0, Y(96), W, Y(92)], fill=(24, 30, 26))
    d.rectangle([0, Y(56), W, Y(52)], fill=(160, 146, 108))                  # belt line
    for xx in range(0, W, 16 * PPU):
        d.line([(xx, Y(52)), (xx, Y(8))], fill=(28, 44, 34), width=max(1, PPU // 2))
        for yy in (Y(48), Y(12)):
            d.ellipse([xx + 2 * PPU - 2, yy - 2, xx + 2 * PPU + 2, yy + 2], fill=(70, 88, 74))
    text_center(d, (W // 2 - 20 * PPU, Y(48), W // 2 + 20 * PPU, Y(34)), '1117', font(int(10 * PPU)), (196, 180, 120))
    d.rectangle([0, Y(8), W, H], fill=(22, 22, 22))
    arr = np.asarray(pil).astype(float) / 255.0
    arr = floor_grime(arr, 0.3, 0.12)
    save('Texture', name, arr)


def vehicle_side(name, seed, body, band=None, cross=False, wunits=128, hunits=96):
    """Generic 1930s vehicle side (ambulance, bus, taxi): body colour, window band, wheels drawn low."""
    W, H = wunits * PPU, hunits * PPU
    arr = solid(H, W, body) * (0.88 + 0.24 * (fbm(H, W, seed, 2.0)[..., None] - 0.5))
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)

    def Y(u):
        return H - int(u * PPU)
    d.rectangle([6 * PPU, Y(84), W - 6 * PPU, Y(58)], fill=(34, 36, 38))
    for k in range(1, 4):
        xx = int(W * k / 4)
        d.line([(xx, Y(84)), (xx, Y(58))], fill=tuple(int(c * 0.7) for c in body), width=2 * PPU)
    if band:
        d.rectangle([0, Y(56), W, Y(50)], fill=band)
    if cross:
        cx, cy, s = W // 2, Y(34), 8 * PPU
        d.rectangle([cx - s, cy - s // 3, cx + s, cy + s // 3], fill=(170, 30, 30))
        d.rectangle([cx - s // 3, cy - s, cx + s // 3, cy + s], fill=(170, 30, 30))
    for wx in (22 * PPU, W - 22 * PPU):
        d.ellipse([wx - 13 * PPU, Y(26), wx + 13 * PPU, H + 4 * PPU], fill=(18, 18, 18))
        d.ellipse([wx - 6 * PPU, Y(19), wx + 6 * PPU, Y(7)], fill=(64, 62, 58))
    arr = np.asarray(pil).astype(float) / 255.0
    save('Texture', name, floor_grime(arr, 0.35, 0.2))


def sandbags(name, seed, wunits=64, hunits=48):
    """Stacked hessian sandbags, bonded rows, sagging fronts."""
    W, H = wunits * PPU, hunits * PPU
    img = solid(H, W, (132, 116, 86))
    ty, tx = np.mgrid[:H, :W]
    bh, bw = 12 * PPU, 24 * PPU
    row = ty // bh
    shift = (row % 2) * (bw // 2)
    ly, lx = (ty % bh) / bh, ((tx + shift) % bw) / bw
    dome = np.clip((1 - (2 * ly - 1) ** 4) * (1 - (2 * lx - 1) ** 6), 0, 1)
    rng = np.random.default_rng(seed)
    var = (rng.random(4096) - 0.5) * 0.25
    bid = (row * 64 + (tx + shift) // bw) % 4096
    img = img * (0.45 + 0.65 * dome[..., None]) * (1 + var[bid][..., None])
    weave = (np.sin(tx * 1.3) * np.sin(ty * 1.3) > 0.6).astype(float)[..., None]
    img = img * (1 - 0.08 * weave)
    img += grain(H, W, seed + 1, 0.04)[..., None]
    save('Texture', name, np.clip(img, 0, 1))


def book_barricade(name, seed, wunits=128, hunits=64):
    """Books piled flat as a barricade in front of the bookshop; four titles from the novel on the spines."""
    W, H = wunits * PPU, hunits * PPU
    rng = np.random.default_rng(seed)
    pil = Image.new('RGB', (W, H), (40, 34, 28))
    d = ImageDraw.Draw(pil)
    titles = ['HISTOIRE DE FRANCE', 'ANNUAIRE DES CHEMINS DE FER', 'TRAITÉ DE PATHOLOGIE MENTALE', 'ATLAS DES COLONIES']
    y = H
    k = 0
    while y > 0:
        th = int(rng.integers(5, 10)) * PPU
        x = int(rng.integers(-20, 8)) * PPU
        while x < W:
            tw = int(rng.integers(40, 90)) * PPU
            col = [(110, 34, 30), (38, 56, 88), (60, 76, 50), (150, 128, 90), (84, 60, 40), (30, 30, 34)][int(rng.integers(0, 6))]
            d.rectangle([x, y - th, x + tw, y - 1], fill=col, outline=tuple(int(c * 0.6) for c in col))
            d.line([(x + 2, y - th + 2), (x + tw - 2, y - th + 2)], fill=tuple(min(255, int(c * 1.3)) for c in col))
            if rng.random() < 0.35:
                t = titles[k % 4]
                k += 1
                f = font(max(8, int(th * 0.55)))
                b = d.textbbox((0, 0), t, font=f)
                if b[2] - b[0] < tw - 6:
                    d.text((x + (tw - (b[2] - b[0])) / 2, y - th + (th - (b[3] - b[1])) / 2 - b[1]), t, font=f, fill=(214, 196, 140))
            x += tw + int(rng.integers(0, 3)) * PPU
        y -= th
    arr = np.asarray(pil).astype(float) / 255.0
    save('Texture', name, floor_grime(arr, 0.3, 0.15))


def radio_shelf(name, seed, wunits=128, hunits=64):
    """Shelves of 1930s wireless sets: veneer cases, cloth speaker grilles, dials (some lit)."""
    W, H = wunits * PPU, hunits * PPU
    rng = np.random.default_rng(seed)
    base = planks(H, W, seed, 16, (70, 50, 34))
    pil = to_img(base)
    d = ImageDraw.Draw(pil)
    for shelf in range(2):
        y1 = H - shelf * (H // 2) - 2 * PPU
        d.rectangle([0, y1 - PPU, W, y1 + PPU], fill=(46, 34, 24))
        x = 3 * PPU
        while x < W - 20 * PPU:
            w = int(rng.integers(20, 30)) * PPU
            h = int(rng.integers(18, 26)) * PPU
            veneer = [(98, 64, 36), (122, 82, 46), (62, 42, 30), (36, 30, 26)][int(rng.integers(0, 4))]
            d.rounded_rectangle([x, y1 - h, x + w, y1 - PPU], radius=4 * PPU, fill=veneer, outline=(30, 22, 16))
            d.rounded_rectangle([x + 3 * PPU, y1 - h + 3 * PPU, x + w - 3 * PPU, y1 - h // 2], radius=2 * PPU, fill=(150, 130, 96))
            for gx in range(x + 4 * PPU, x + w - 4 * PPU, 2 * PPU):
                d.line([(gx, y1 - h + 4 * PPU), (gx, y1 - h // 2 - PPU)], fill=(120, 100, 72))
            lit = rng.random() < 0.6
            d.rectangle([x + 4 * PPU, y1 - h // 2 + 2 * PPU, x + w - 4 * PPU, y1 - h // 2 + 6 * PPU], fill=(230, 196, 120) if lit else (90, 80, 60))
            for kx in (x + 6 * PPU, x + w - 6 * PPU):
                d.ellipse([kx - 2 * PPU, y1 - 7 * PPU, kx + 2 * PPU, y1 - 3 * PPU], fill=(24, 20, 16))
            x += w + int(rng.integers(2, 5)) * PPU
    save('Texture', name, np.asarray(pil).astype(float) / 255.0)


def apothecary_window(name, seed, wunits=64, hunits=64):
    """Pharmacy side window: apothecary jars on glass shelves, a fortifying tonic advertisement card."""
    W, H = wunits * PPU, hunits * PPU
    rng = np.random.default_rng(seed)
    img = Image.new('RGBA', (W, H), (34, 38, 40, 0))
    d = ImageDraw.Draw(img)
    for shelf in (0.42, 0.78):
        y = int(H * shelf)
        d.line([(0, y), (W, y)], fill=(150, 170, 170, 255), width=PPU)
        x = 4 * PPU
        while x < W - 10 * PPU:
            jw, jh = 9 * PPU, int(rng.integers(12, 17)) * PPU
            glass = [(200, 206, 196), (120, 90, 50), (60, 90, 120)][int(rng.integers(0, 3))]
            d.rounded_rectangle([x, y - jh, x + jw, y - PPU], radius=2 * PPU, fill=glass + (220,))
            d.rectangle([x + 2 * PPU, y - jh - 3 * PPU, x + jw - 2 * PPU, y - jh], fill=(30, 30, 30, 255))
            d.rectangle([x + PPU, y - jh // 2 - 2 * PPU, x + jw - PPU, y - jh // 2 + 2 * PPU], fill=(230, 222, 200, 255))
            x += jw + 3 * PPU
    d.rectangle([W - 26 * PPU, 4 * PPU, W - 4 * PPU, 18 * PPU], fill=(210, 190, 120, 255))
    text_center(d, (W - 26 * PPU, 4 * PPU, W - 4 * PPU, 18 * PPU), 'FORTIFIANT', font(4 * PPU), (80, 30, 26))
    masked(name, img)


def luna_sign(name, wunits=256, hunits=64):
    """LUNA PARK monumental letters, lights dead; the U hangs (l. 453)."""
    W, H = wunits * PPU, hunits * PPU
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f = font(int(H * 0.8))
    probe = ImageDraw.Draw(img)
    total = lambda f: sum(probe.textlength(c, font=f) + H * 0.06 for c in 'LUNAPARK') + H * 0.35
    while total(f) > W * 0.92:
        f = ImageFont.truetype(f.path, int(f.size * 0.95))
    x = int((W - total(f)) / 2)
    for ch in 'LUNA PARK':
        if ch == ' ':
            x += int(H * 0.35)
            continue
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((x, int(H * 0.02)), ch, font=f, fill=(196, 178, 140, 255), stroke_width=PPU, stroke_fill=(70, 60, 48, 255))
        cw = int(ld.textlength(ch, font=f))
        for bx in range(x + 6, x + cw - 4, 3 * PPU):                        # dead bulbs along the letters
            for by in range(int(H * 0.15), int(H * 0.85), 4 * PPU):
                if layer.getpixel((min(W - 1, bx), by))[3] > 0:
                    ld.ellipse([bx - PPU // 2, by - PPU // 2, bx + PPU // 2, by + PPU // 2], fill=(90, 84, 74, 255))
        if ch == 'U':
            layer = layer.rotate(-14, center=(x + cw, int(H * 0.05)), resample=Image.BICUBIC)
        img = Image.alpha_composite(img, layer)
        x += cw + int(H * 0.06)
    masked(name, img)


def closure_panel(name, wunits=96, hunits=32):
    """FERMETURE DÉFINITIVE, the second word crossed out with charcoal (l. 453)."""
    W, H = wunits * PPU, hunits * PPU
    pil = Image.new('RGB', (W, H), (214, 206, 184))
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 36, 32), width=PPU)
    f = font(int(H * 0.3))
    text_center(d, (0, 0, W, H * 0.5), 'FERMETURE', f, (24, 22, 22))
    text_center(d, (0, H * 0.45, W, H), 'DÉFINITIVE', f, (24, 22, 22))
    # Charcoal: two quick dry strokes through the word, grainy and uneven; the word stays legible under them.
    b = d.textbbox((0, 0), 'DÉFINITIVE', font=fitted(d, 'DÉFINITIVE', f, W * 0.94))
    wx0, wx1 = (W - (b[2] - b[0])) / 2 - PPU, (W + (b[2] - b[0])) / 2 + PPU
    stroke = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(stroke)
    rng = np.random.default_rng(3)
    for k, (ya, yb) in enumerate(((0.70, 0.75), (0.78, 0.71))):
        pts = [(wx0 + (wx1 - wx0) * s, H * (ya + (yb - ya) * s) + rng.normal(0, H * 0.008)) for s in np.linspace(0, 1, 24)]
        sd.line(pts, fill=200 - 40 * k, width=max(2, int(H * 0.035)))
    grainmask = (np.random.default_rng(4).random((H, W)) > 0.35).astype(float)
    alpha = np.asarray(stroke).astype(float) / 255.0 * grainmask
    arr = np.asarray(pil).astype(float) / 255.0
    arr = arr * (1 - alpha[..., None]) + np.array([0.09, 0.09, 0.09]) * alpha[..., None]
    save('Texture', name, soot(arr, 11, 0.2, top=False))


def morris(name, state, wunits=64, hunits=128):
    """Morris column (l. 437-443), three states of the same face.
    luna: revues, an operetta, a lecture on the future of Europe, white ANNULÉ bands pasted across the faces; below
          them the older Luna Park poster almost covered (roller coaster, pool, a woman in a bathing suit raising her
          arms) and the one sentence that survives, LA VILLE ENCHANTÉE DE LA PORTE MAILLOT; a lifted corner.
    jerma: the paper torn at that corner shows, for a heartbeat, a print in impossible colours: an aerial photograph
          of a massive seaside hotel, wings open around an empty pool, JERMA PALACE in white letters on the facade.
    dentifrice: what the lower paper is afterwards, an ordinary tooth powder advertisement."""
    W, H = wunits * PPU, hunits * PPU
    pil = Image.new('RGB', (W, H), (58, 62, 52))
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W, 12 * PPU], fill=(40, 44, 38))                  # cast-iron crown and base rings
    d.rectangle([0, H - 10 * PPU, W, H], fill=(40, 44, 38))
    y = 14 * PPU
    for (title, col) in (('REVUE', (180, 60, 50)), ('OPÉRETTE', (60, 80, 140)), ("L'AVENIR DE L'EUROPE", (150, 140, 110))):
        d.rectangle([3 * PPU, y, W - 3 * PPU, y + 18 * PPU], fill=(220, 210, 186))
        d.ellipse([W // 2 - 5 * PPU, y + 6 * PPU, W // 2 + 5 * PPU, y + 17 * PPU], fill=(196, 180, 150))   # a face
        text_center(d, (3 * PPU, y + 0.5 * PPU, W - 3 * PPU, y + 6.5 * PPU), title, font(int(5 * PPU)), col)
        d.polygon([(3 * PPU, y + 12 * PPU), (W - 3 * PPU, y + 9 * PPU), (W - 3 * PPU, y + 14 * PPU), (3 * PPU, y + 17 * PPU)],
                  fill=(246, 244, 238))                                  # the band across the face, pasted askew
        text_center(d, (3 * PPU, y + 10.5 * PPU, W - 3 * PPU, y + 15.5 * PPU), 'ANNULÉ', font(int(4 * PPU)), (20, 20, 20))
        y += 20 * PPU
    x0, x1, y0, y1 = 3 * PPU, W - 3 * PPU, y, H - 12 * PPU
    if state == 'luna':
        d.rectangle([x0, y0, x1, y1], fill=(188, 170, 128))
        d.arc([x0 + 3 * PPU, y0 + 3 * PPU, x1 - 3 * PPU, y0 + 22 * PPU], 180, 360, fill=(120, 50, 40), width=2 * PPU)   # roller coaster
        d.rectangle([x0 + 4 * PPU, y0 + 14 * PPU, x1 - 4 * PPU, y0 + 19 * PPU], fill=(90, 120, 140))                   # the pool
        cx = W // 2 + 12 * PPU                                           # the woman raising her arms
        d.ellipse([cx - PPU, y0 + 6 * PPU, cx + PPU, y0 + 8 * PPU], fill=(90, 40, 30))
        d.line([(cx, y0 + 8 * PPU), (cx, y0 + 13 * PPU)], fill=(90, 40, 30), width=PPU)
        d.line([(cx - 3 * PPU, y0 + 5 * PPU), (cx, y0 + 9 * PPU), (cx + 3 * PPU, y0 + 5 * PPU)], fill=(90, 40, 30), width=PPU // 2 + 1)
        text_center(d, (x0, y0 + 20 * PPU, x1, y0 + 26 * PPU), 'LA VILLE ENCHANTÉE', font(int(3.4 * PPU)), (90, 40, 30))
        text_center(d, (x0, y0 + 26 * PPU, x1, y0 + 32 * PPU), 'DE LA PORTE MAILLOT', font(int(3.4 * PPU)), (90, 40, 30))
        # the newer paper pasted over most of it, and the lifted corner Viktor scratches
        d.polygon([(x0, y0), (x1, y0), (x1, y0 + 4 * PPU), (x0 + 20 * PPU, y0 + 2 * PPU), (x0, y0 + 5 * PPU)], fill=(214, 204, 180))
        d.polygon([(x1 - 7 * PPU, y1), (x1, y1 - 7 * PPU), (x1, y1)], fill=(236, 230, 214))
        d.line([(x1 - 7 * PPU, y1), (x1, y1 - 7 * PPU)], fill=(120, 110, 90), width=1)
    elif state == 'jerma':
        # Impossible colours for 1940: a saturated modern colour print, hard sun, deep turquoise sea.
        ph = y1 - y0
        yy = np.linspace(0, 1, ph)[:, None, None]
        base = np.array([0.02, 0.42, 0.55]) + yy * np.array([0.05, 0.2, 0.15])
        sea = base * np.ones((ph, x1 - x0, 3)) * (0.85 + 0.3 * (fbm(ph, x1 - x0, 5, 3.0)[..., None] - 0.5))
        pil.paste(to_img(np.clip(sea, 0, 1)), (x0, y0))
        d = ImageDraw.Draw(pil)
        d.polygon([(x0, y0 + ph * 0.62), (x1, y0 + ph * 0.52), (x1, y1), (x0, y1)], fill=(196, 170, 120))   # rocky shore
        cx, cy = W // 2, y0 + int(ph * 0.66)
        wing = [(cx - 2 * PPU, cy - 10 * PPU), (cx - 25 * PPU, cy - 2 * PPU), (cx - 24 * PPU, cy + 4 * PPU), (cx - 1 * PPU, cy - 4 * PPU)]
        d.polygon(wing, fill=(240, 236, 226))
        d.polygon([(2 * cx - x, y) for x, y in wing], fill=(226, 222, 212))
        d.rectangle([cx - 9 * PPU, cy - 14 * PPU, cx + 9 * PPU, cy - 4 * PPU], fill=(246, 244, 238))       # main block
        for row in range(3):                                            # balconies, sharp shadows
            d.line([(cx - 9 * PPU, cy - 12 * PPU + row * 3 * PPU), (cx + 9 * PPU, cy - 12 * PPU + row * 3 * PPU)], fill=(120, 116, 110), width=1)
        d.rectangle([cx - 6 * PPU, cy - 1 * PPU, cx + 6 * PPU, cy + 6 * PPU], fill=(150, 196, 206))         # the empty pool
        d.rectangle([cx - 6 * PPU, cy - 1 * PPU, cx + 6 * PPU, cy], fill=(90, 120, 128))
        text_center(d, (x0, cy - 22 * PPU, x1, cy - 15 * PPU), 'JERMA PALACE', font(int(4.6 * PPU)), (255, 255, 255))
        rng = np.random.default_rng(22)                                  # torn edge of the upper paper
        edge = [(x0 + k * (x1 - x0) / 12, y0 + rng.uniform(0, 3) * PPU) for k in range(13)]
        d.polygon([(x0, y0)] + edge + [(x1, y0)], fill=(214, 204, 180))
    else:
        d.rectangle([x0, y0, x1, y1], fill=(214, 208, 190))
        d.ellipse([W // 2 - 10 * PPU, y0 + 4 * PPU, W // 2 + 10 * PPU, y0 + 14 * PPU], fill=(170, 160, 140))   # the round tin
        d.ellipse([W // 2 - 9 * PPU, y0 + 5 * PPU, W // 2 + 9 * PPU, y0 + 12 * PPU], fill=(206, 200, 184))
        text_center(d, (x0, y0 + 16 * PPU, x1, y0 + 22 * PPU), 'POUDRE', font(int(4.4 * PPU)), (60, 90, 120))
        text_center(d, (x0, y0 + 22 * PPU, x1, y0 + 28 * PPU), 'DENTIFRICE', font(int(4.4 * PPU)), (60, 90, 120))
        text_center(d, (x0, y0 + 28 * PPU, x1, y0 + 32 * PPU), 'EN VENTE CHEZ VOTRE PHARMACIEN', font(int(2.2 * PPU), bold=False), (70, 64, 56))
    arr = np.asarray(pil).astype(float) / 255.0
    arr = arr * (0.9 + 0.2 * (fbm(H, W, 30, 2.0)[..., None] - 0.5))
    save('Texture', name, np.clip(arr, 0, 1))


def cochin_portal(name, wunits=128, hunits=192):
    """Stone gateway of the Hôpital Cochin, carved name, iron gates open back against the piers."""
    W, H = wunits * PPU, hunits * PPU
    arr = stone_blocks(H, W, 331, 24, 48, (170, 160, 142), (110, 104, 94))
    arr = soot(arr, 332, 0.25)
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)
    d.rectangle([10 * PPU, 18 * PPU, W - 10 * PPU, 34 * PPU], fill=(150, 140, 124))
    text_center(d, (10 * PPU, 18 * PPU, W - 10 * PPU, 34 * PPU), 'HÔPITAL COCHIN', font(int(9 * PPU)), (60, 54, 48))
    save('Texture', name, np.asarray(pil).astype(float) / 255.0)


def tram_bench(name, seed):
    arr = planks(32 * PPU, 64 * PPU, seed, 6, (120, 84, 48))
    save('Texture', name, floor_grime(arr, 0.3, 0.3))


def leather(h, w, seed, rgb):
    img = solid(h, w, rgb) * (0.85 + 0.3 * (fbm(h, w, seed, 1.6)[..., None] - 0.5))
    return np.clip(img + grain(h, w, seed + 1, 0.03)[..., None], 0, 1)


def suitcase_side(name, seed):
    """Suitcases stacked on the benches: leather and fibre cases, straps, labels."""
    W, H = 64 * PPU, 32 * PPU
    rng = np.random.default_rng(seed)
    pil = Image.new('RGB', (W, H), (40, 30, 24))
    d = ImageDraw.Draw(pil)
    x = 0
    while x < W:
        w = int(rng.integers(18, 30)) * PPU
        h = int(rng.integers(14, 30)) * PPU
        col = [(104, 70, 40), (70, 50, 34), (130, 110, 80), (50, 56, 60)][int(rng.integers(0, 4))]
        d.rounded_rectangle([x, H - h, x + w - PPU, H - 1], radius=2 * PPU, fill=col, outline=tuple(int(c * 0.6) for c in col))
        for sx in (x + w // 4, x + 3 * w // 4):
            d.rectangle([sx - PPU, H - h, sx + PPU, H - 1], fill=(50, 34, 22))
        d.rectangle([x + w // 2 - 3 * PPU, H - h + 2 * PPU, x + w // 2 + 3 * PPU, H - h + 6 * PPU], fill=(220, 210, 180))
        x += w
    save('Texture', name, np.asarray(pil).astype(float) / 255.0)


def mattress_skin():
    """Striped ticking of a spring mattress, soaked with dirty water, ash along the edge (l. 131)."""
    W, H = 128, 64
    img = np.ones((H, W, 3)) * np.array((196, 190, 172)) / 255.0
    xs = np.arange(W)
    stripes = ((xs // 6) % 3 == 0)[None, :]
    img[np.broadcast_to(stripes, (H, W))] = np.array((70, 84, 118)) / 255.0
    dirt = fbm(H, W, 91, 2.0)[..., None]
    img = img * (0.7 + 0.35 * dirt)
    img[:, :, :] *= np.linspace(0.75, 1.0, H)[:, None, None]
    return to_img(np.clip(img, 0, 1))


# ----------------------------------------------------------------------------- sprites (objects of the novel)
def sprite_rgba(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def save_sprite(img, name, yoff_extra=0):
    SPRITES.mkdir(parents=True, exist_ok=True)
    w, h = img.size
    png_with_grab(img, w // 2, h - 1 + yoff_extra, SPRITES / f'{name}.png')


def draw_ticket():
    """Tram ticket, punched: an incomplete circle barred by the bite of the pliers (l. 127)."""
    img = sprite_rgba(64, 40)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 6, 60, 34], fill=(214, 196, 150, 255), outline=(120, 100, 70, 255))
    d.text((8, 8), 'T.C.R.P.', fill=(60, 40, 30, 255))
    d.line([(8, 22), (38, 22)], fill=(80, 60, 40, 255))
    d.arc([42, 14, 54, 26], 40, 330, fill=(30, 26, 22, 255), width=2)
    d.line([(41, 27), (55, 13)], fill=(30, 26, 22, 255), width=2)
    save_sprite(img, 'RFTKA0')


def draw_reader_card():
    """Library reader card, damp, stamp of 12 December 2022; the pencilled back: JERMA - ERREUR Ø (l. 315)."""
    img = sprite_rgba(72, 48)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 6, 68, 44], fill=(222, 214, 190, 255), outline=(150, 136, 110, 255))
    d.ellipse([46, 10, 64, 26], outline=(120, 40, 60, 255), width=2)
    d.text((48, 14), '12', fill=(120, 40, 60, 255))
    for y in (14, 20, 26):
        d.line([(8, y), (40, y)], fill=(150, 150, 170, 255))
    d.text((8, 30), 'JERMA - ERREUR 0', fill=(60, 60, 70, 255))
    d.line([(96 // 2 + 16, 38), (96 // 2 + 22, 30)], fill=(60, 60, 70, 255))
    save_sprite(img, 'RFTKB0')


def draw_bag():
    """Leather satchel of the fare collector hanging on its hook (tickets, pliers, coins, timetable)."""
    img = sprite_rgba(48, 56)
    d = ImageDraw.Draw(img)
    d.line([(24, 2), (24, 14)], fill=(40, 30, 20, 255), width=3)
    d.rounded_rectangle([8, 14, 40, 50], radius=6, fill=(96, 62, 34, 255), outline=(50, 32, 18, 255))
    d.rectangle([8, 14, 40, 26], fill=(84, 54, 30, 255))
    d.rectangle([22, 24, 26, 30], fill=(170, 150, 100, 255))
    save_sprite(img, 'RFBGA0')


def draw_bucket():
    """Galvanised bucket where forms burn badly (l. 87): grey zinc, papers standing out of it."""
    img = sprite_rgba(48, 48)
    d = ImageDraw.Draw(img)
    d.polygon([(8, 14), (40, 14), (36, 46), (12, 46)], fill=(104, 108, 108, 255), outline=(60, 62, 62, 255))
    for x in range(12, 38, 6):
        d.line([(x, 16), (x - 1, 44)], fill=(88, 90, 90, 255))
    d.polygon([(8, 14), (40, 14), (39, 22), (9, 22)], fill=(40, 34, 30, 255))                  # soot at the rim
    d.ellipse([12, 11, 36, 18], fill=(170, 70, 30, 255))                                      # embers
    for k, (x, a) in enumerate(((16, -20), (24, 5), (31, 25))):
        d.polygon([(x - 5, 16), (x + 5, 16), (x + 4 + a // 10, 2), (x - 4 + a // 10, 4)], fill=(220, 212, 190, 255) if k != 1 else (60, 50, 44, 255))
    d.arc([6, 8, 42, 24], 180, 360, fill=(80, 84, 86, 255), width=2)
    save_sprite(img, 'RFBKA0')


def draw_phone():
    """Military field telephone on its folding table (l. 333): wooden box, crank, handset."""
    img = sprite_rgba(48, 40)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 12, 38, 36], fill=(74, 70, 50, 255), outline=(40, 38, 28, 255))
    d.rectangle([12, 6, 36, 12], fill=(24, 24, 24, 255))
    d.line([(38, 22), (44, 18)], fill=(40, 40, 40, 255), width=2)
    d.ellipse([42, 15, 46, 19], fill=(40, 40, 40, 255))
    save_sprite(img, 'RFPHA0')


def draw_shoes_case():
    """The brown suitcase of the young woman, open on the overturned table: women's shoes wrapped in paper,
    court shoes, sandals, ankle boots, worn soles (l. 391)."""
    img = sprite_rgba(96, 48)
    d = ImageDraw.Draw(img)
    d.rectangle([6, 20, 90, 44], fill=(104, 70, 42, 255), outline=(60, 40, 24, 255))
    d.polygon([(6, 20), (90, 20), (84, 4), (12, 4)], fill=(120, 82, 50, 255), outline=(60, 40, 24, 255))
    rng = np.random.default_rng(5)
    for k in range(6):
        x = 12 + k * 13
        d.rounded_rectangle([x, 22, x + 11, 38], radius=3, fill=(226, 218, 196, 255), outline=(170, 160, 136, 255))
        col = [(30, 26, 24), (110, 60, 40), (150, 120, 90)][k % 3]
        d.ellipse([x + 2, 28, x + 9, 34], fill=col + (255,))
    save_sprite(img, 'RFSHA0')



# ----------------------------------------------------------------------------- map pieces added with the map
def amiga_reflection(name, seed, wunits=128, hunits=64):
    """The TSF window seen in its reflection (l. 213): among the wireless sets a flat grey case with an integrated
    keyboard and coloured letters on the keys, AMIGA; a blue screen with a pointer; diskettes lined up in a shoe box;
    a man bent over a hotel plan whose corridors do not close. Reflection values: low contrast, cold, the radios
    still showing through. Procedural stand-in until Astra's master (CAN-002) replaces this file."""
    W, H = wunits * PPU, hunits * PPU
    radios = Image.open(PATCH / 'RF2_TSFS.png').convert('RGB')
    base = np.asarray(radios).astype(float) / 255.0
    base = base * 0.45 + np.array([0.10, 0.12, 0.16]) * 0.55                  # ghosted radios under the reflection
    pil = to_img(np.clip(base, 0, 1))
    d = ImageDraw.Draw(pil)
    # monitor with the blue screen and a pointer
    mx0, my0 = 10 * PPU, 8 * PPU
    d.rectangle([mx0, my0, mx0 + 40 * PPU, my0 + 30 * PPU], fill=(150, 146, 136))
    d.rectangle([mx0 + 3 * PPU, my0 + 3 * PPU, mx0 + 37 * PPU, my0 + 25 * PPU], fill=(0, 85, 170))
    d.rectangle([mx0 + 3 * PPU, my0 + 3 * PPU, mx0 + 37 * PPU, my0 + 6 * PPU], fill=(230, 230, 230))
    d.polygon([(mx0 + 22 * PPU, my0 + 12 * PPU), (mx0 + 22 * PPU, my0 + 18 * PPU), (mx0 + 24 * PPU, my0 + 16 * PPU),
               (mx0 + 26 * PPU, my0 + 19 * PPU), (mx0 + 27 * PPU, my0 + 18 * PPU), (mx0 + 25 * PPU, my0 + 15 * PPU),
               (mx0 + 27 * PPU, my0 + 14 * PPU)], fill=(230, 60, 40))
    d.rectangle([mx0 + 16 * PPU, my0 + 30 * PPU, mx0 + 24 * PPU, my0 + 34 * PPU], fill=(120, 116, 108))
    # the computer: flat case, integrated keyboard, coloured letters, AMIGA
    kx0, ky0 = 8 * PPU, 40 * PPU
    d.polygon([(kx0, ky0 + 14 * PPU), (kx0 + 4 * PPU, ky0), (kx0 + 50 * PPU, ky0), (kx0 + 54 * PPU, ky0 + 14 * PPU)], fill=(196, 192, 180))
    for row in range(3):
        for k in range(12):
            x = kx0 + 6 * PPU + k * 3.6 * PPU + row * PPU
            y = ky0 + 2 * PPU + row * 3.6 * PPU
            d.rectangle([x, y, x + 2.8 * PPU, y + 2.6 * PPU], fill=(226, 222, 212))
    for k, col in enumerate(((200, 40, 40), (230, 140, 30), (230, 210, 40), (60, 160, 60), (40, 90, 200))):
        d.rectangle([kx0 + 6 * PPU + k * 3.6 * PPU, ky0 + 2 * PPU, kx0 + 8.8 * PPU + k * 3.6 * PPU, ky0 + 4.6 * PPU], fill=col)
    text_center(d, (kx0 + 36 * PPU, ky0 + 9 * PPU, kx0 + 52 * PPU, ky0 + 13 * PPU), 'AMIGA', font(int(3 * PPU)), (60, 60, 64))
    # shoe box of diskettes
    bx0, by0 = 70 * PPU, 44 * PPU
    d.rectangle([bx0, by0, bx0 + 22 * PPU, by0 + 14 * PPU], fill=(150, 120, 80))
    for k in range(7):
        x = bx0 + 2 * PPU + k * 2.8 * PPU
        d.rectangle([x, by0 - 5 * PPU, x + 2.2 * PPU, by0 + 2 * PPU], fill=[(40, 40, 44), (140, 30, 30), (40, 40, 44)][k % 3])
    # a man bent over a hotel plan whose corridors do not close
    px0, py0 = 96 * PPU, 40 * PPU
    d.rectangle([px0, py0, px0 + 28 * PPU, py0 + 16 * PPU], fill=(210, 206, 190))
    for (a, b, c, e) in ((2, 4, 26, 4), (2, 4, 2, 13), (8, 4, 8, 10), (14, 8, 26, 8), (20, 8, 20, 14), (2, 13, 12, 13)):
        d.line([(px0 + a * PPU, py0 + b * PPU), (px0 + c * PPU, py0 + e * PPU)], fill=(60, 60, 90), width=max(1, PPU // 2))
    d.ellipse([px0 + 10 * PPU, py0 - 20 * PPU, px0 + 18 * PPU, py0 - 12 * PPU], fill=(30, 32, 36))
    d.polygon([(px0 + 6 * PPU, py0 - 12 * PPU), (px0 + 22 * PPU, py0 - 12 * PPU), (px0 + 26 * PPU, py0), (px0 + 2 * PPU, py0)], fill=(30, 32, 36))
    arr = np.asarray(pil).astype(float) / 255.0
    arr = arr * 0.8 + np.array([0.12, 0.14, 0.18]) * 0.2                       # glass
    save('Texture', name, np.clip(arr, 0, 1))


def tram_panel(name, seed, part):
    """Tram body pieces for the solid 3D floors of the tram (their sides are aligned to their top).
    lower: dark green panel 48 high, rivets, fleet number 1117; upper: cream band 32 high, dark roof edge."""
    W = 128 * PPU
    H = (48 if part == 'lower' else 32) * PPU
    if part == 'lower':
        arr = solid(H, W, (38, 62, 48)) * (0.9 + 0.2 * (fbm(H, W, seed, 2.0)[..., None] - 0.5))
        pil = to_img(arr)
        d = ImageDraw.Draw(pil)
        d.rectangle([0, 0, W, 4 * PPU], fill=(160, 146, 108))
        for xx in range(0, W, 16 * PPU):
            d.line([(xx, 4 * PPU), (xx, H - 8 * PPU)], fill=(28, 44, 34), width=max(1, PPU // 2))
            d.ellipse([xx + 2 * PPU - 2, 8 * PPU - 2, xx + 2 * PPU + 2, 8 * PPU + 2], fill=(70, 88, 74))
        text_center(d, (W // 2 - 20 * PPU, 12 * PPU, W // 2 + 20 * PPU, 30 * PPU), '1117', font(int(10 * PPU)), (196, 180, 120))
        d.rectangle([0, H - 6 * PPU, W, H], fill=(22, 22, 22))
    else:
        arr = solid(H, W, (196, 186, 156)) * (0.9 + 0.2 * (fbm(H, W, seed, 2.0)[..., None] - 0.5))
        pil = to_img(arr)
        d = ImageDraw.Draw(pil)
        d.rectangle([0, 0, W, 8 * PPU], fill=(40, 42, 40))
        d.rectangle([0, H - 4 * PPU, W, H], fill=(24, 30, 26))
    arr = np.asarray(pil).astype(float) / 255.0
    save('Texture', name, floor_grime(arr, 0.3, 0.12))


def departures_board(name, seed, wunits=128, hunits=64):
    """Station board (l. 207): hours without departures, platforms without trains; the destination column blank."""
    W, H = wunits * PPU, hunits * PPU
    pil = Image.new('RGB', (W, H), (22, 24, 26))
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W - 1, H - 1], outline=(70, 60, 44), width=2 * PPU)
    f = font(int(4 * PPU))
    for (x, txt) in ((6, 'DÉPART'), (40, 'DESTINATION'), (100, 'VOIE')):
        d.text((x * PPU, 4 * PPU), txt, font=f, fill=(210, 190, 120))
    d.line([(4 * PPU, 10 * PPU), (W - 4 * PPU, 10 * PPU)], fill=(90, 80, 60), width=PPU // 2 + 1)
    for k, hour in enumerate(('06 H 12', '06 H 40', '07 H 05', '07 H 50', '08 H 15', '09 H 02')):
        y = (13 + k * 8) * PPU
        d.text((6 * PPU, y), hour, font=f, fill=(226, 222, 206))
        d.rectangle([40 * PPU, y + PPU, 94 * PPU, y + 5 * PPU], fill=(34, 36, 38))
        d.text((102 * PPU, y), '—', font=f, fill=(150, 146, 136))
    arr = np.asarray(pil).astype(float) / 255.0
    save('Texture', name, floor_grime(arr, 0.2, 0.2))


def carved_panel(name, text, wunits=128, hunits=16):
    """Carved stone name over a gateway."""
    W, H = wunits * PPU, hunits * PPU
    arr = stone_blocks(H, W, 441, 16, 128, (160, 150, 132), (120, 112, 100))
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)
    text_center(d, (0, 0, W, H), text, font(int(H * 0.62)), (70, 64, 56))
    save('Texture', name, np.asarray(pil).astype(float) / 255.0)


def palisade(name, seed, wunits=128, hunits=128):
    """Luna Park hoarding (l. 451): grey vertical boards, old poster strips, bill stickers peeling."""
    W, H = wunits * PPU, hunits * PPU
    arr = planks(W, H, seed, 12, (86, 80, 70))
    arr = np.transpose(arr, (1, 0, 2))                                        # vertical boards
    arr = soot(arr, seed + 1, 0.25, top=False)
    pil = to_img(arr)
    d = ImageDraw.Draw(pil)
    rng = np.random.default_rng(seed)
    for k in range(4):
        x0 = int(rng.integers(0, W - 40 * PPU))
        y0 = int(rng.integers(H // 3, H - 40 * PPU))
        w, h = int(rng.integers(24, 40)) * PPU, int(rng.integers(20, 36)) * PPU
        col = [(190, 170, 130), (170, 60, 50), (200, 196, 180), (80, 100, 140)][k]
        d.polygon([(x0, y0), (x0 + w, y0 + PPU), (x0 + w - 3 * PPU, y0 + h), (x0 + 2 * PPU, y0 + h - 2 * PPU)], fill=col)
    arr = np.asarray(pil).astype(float) / 255.0
    save('Texture', name, floor_grime(arr, 0.3, 0.3))


def tarp(name, seed, kind):
    """Canvas tarpaulin over the machine gun (l. 333)."""
    n = 64 * PPU
    img = solid(n, n, (84, 86, 62)) * (0.8 + 0.4 * (fbm(n, n, seed, 1.4)[..., None] - 0.5))
    folds = np.sin(np.linspace(0, 18, n))[None, :, None] * 0.06
    save(kind, name, np.clip(img + folds + grain(n, n, seed + 1, 0.03)[..., None], 0, 1))


def draw_radio():
    """The wireless set on the counter whose dial lamp stays dark (l. 229): veneer case, cloth grille, dial."""
    img = sprite_rgba(64, 48)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 6, 60, 46], radius=8, fill=(110, 72, 40, 255), outline=(50, 32, 18, 255))
    d.rounded_rectangle([10, 10, 54, 28], radius=4, fill=(156, 136, 100, 255))
    for x in range(12, 54, 3):
        d.line([(x, 11), (x, 27)], fill=(126, 106, 76, 255))
    d.rectangle([14, 32, 50, 38], fill=(70, 62, 48, 255))
    for x in (16, 48):
        d.ellipse([x - 3, 39, x + 3, 45], fill=(24, 20, 16, 255))
    save_sprite(img, 'RFRDA0')
    lit = img.copy()
    ImageDraw.Draw(lit).rectangle([14, 32, 50, 38], fill=(236, 204, 120, 255))
    save_sprite(lit, 'RFRDB0')


def draw_mattress():
    """The striped spring mattress dragged along the street (l. 131), as a flat sprite on the ground; only its
    reflection moves by itself in the pharmacy window (l. 157)."""
    skin = mattress_skin().resize((112, 56))
    img = sprite_rgba(112, 56)
    img.paste(skin.convert('RGBA'), (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 111, 55], outline=(90, 86, 76, 255), width=2)
    d.line([(0, 28), (-4, 30)], fill=(60, 50, 40, 255))
    SPRITES.mkdir(parents=True, exist_ok=True)
    png_with_grab(img, 56, 28, SPRITES / 'RFMTA0.png')


def railing(name, wunits=64, hunits=40):
    """Cast-iron railing of the bridge: top and bottom rails, balusters, a ring between them. See-through."""
    W, H = wunits * PPU, hunits * PPU
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    iron = (38, 40, 38, 255)
    d.rectangle([0, 0, W, 4 * PPU], fill=iron)
    d.rectangle([0, H - 3 * PPU, W, H], fill=iron)
    for x in range(0, W, 8 * PPU):
        d.rectangle([x + 3 * PPU, 4 * PPU, x + 5 * PPU, H - 3 * PPU], fill=iron)
    for x in range(4 * PPU, W, 16 * PPU):
        d.ellipse([x + 2 * PPU, 14 * PPU, x + 10 * PPU, 22 * PPU], outline=iron, width=PPU)
    masked(name, img)


def wine_setts(seed):
    """Setts in the gutter where the wine runs, dark red with dust (l. 293)."""
    n = 64 * PPU
    arr = soot(cobbles(n, n, seed), seed + 1, 0.2, top=False)
    stain = np.clip((fbm(n, n, seed + 2, 1.2) - 0.25) * 2.5, 0, 1)[..., None]
    wine = np.array([0.26, 0.04, 0.06])
    arr = arr * (1 - 0.75 * stain) + wine * 0.75 * stain
    save('Flat', 'RF2_VIN1', np.clip(arr, 0, 1))


def morris_model():
    """The Morris column as a model (it is round): a 16-sided drum 22 units in radius, the posters around it
    twice, the dark crown ring and a small dome. Three skins for the three states of the face (l. 437-443).
    OBJ, Y up, map units (MODELDEF scales Z by 1.2 with CorrectPixelStretch, as the RF01 bodies)."""
    out = ROOT / 'src' / 'models' / 'rf02'
    out.mkdir(parents=True, exist_ok=True)
    R, H, N = 22.0, 128.0, 16
    v, vt, f = [], [], []
    for k in range(N + 1):                                   # drum: u around, v up (the poster height)
        a = 2 * math.pi * k / N
        for (y, tv) in ((0.0, 0.0), (H, 0.92)):
            v.append((math.cos(a) * R, y, math.sin(a) * R))
            vt.append((k / N, tv))
    for k in range(N):
        b0, t0, b1, t1 = 2 * k + 1, 2 * k + 2, 2 * k + 3, 2 * k + 4
        f.append(((b0, b0), (b1, b1), (t1, t1)))
        f.append(((b0, b0), (t1, t1), (t0, t0)))
    base = len(v)
    for k in range(N + 1):                                   # crown ring, a little wider
        a = 2 * math.pi * k / N
        v.append((math.cos(a) * (R + 3), H, math.sin(a) * (R + 3)))
        vt.append((k / N, 0.95))
        v.append((math.cos(a) * (R + 3), H + 8, math.sin(a) * (R + 3)))
        vt.append((k / N, 0.99))
    for k in range(N):
        b0, t0, b1, t1 = base + 2 * k + 1, base + 2 * k + 2, base + 2 * k + 3, base + 2 * k + 4
        f.append(((b0, b0), (b1, b1), (t1, t1)))
        f.append(((b0, b0), (t1, t1), (t0, t0)))
    apex = len(v) + 1                                        # the dome
    v.append((0.0, H + 26, 0.0))
    vt.append((0.5, 0.995))
    for k in range(N):
        f.append(((base + 2 * k + 2, base + 2 * k + 2), (base + 2 * k + 4, base + 2 * k + 4), (apex, apex)))
    lines = ['# RF02 Morris column: generated by scripts/mapkit/materials_rf02.py. Map units, Y up.', 'o morris']
    lines += [f'v {x:.4f} {y:.4f} {z:.4f}' for (x, y, z) in v]
    lines += [f'vt {a:.4f} {b:.4f}' for (a, b) in vt]
    lines += ['f ' + ' '.join(f'{a}/{b}' for (a, b) in face) for face in f]
    (out / 'morris.obj').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    for state in ('luna', 'jerma', 'dentifrice'):
        face = Image.open(PATCH / ({'luna': 'RF2_MORR', 'jerma': 'RF2_MORJ', 'dentifrice': 'RF2_MORD'}[state] + '.png')).convert('RGB')
        plain = Image.open(PATCH / 'RF2_MORR.png').convert('RGB')
        w, h = face.size
        skin = Image.new('RGB', (w * 2, int(h / 0.92)), (40, 44, 38))
        skin.paste(face, (0, skin.height - h))               # the scratched face: once around the drum
        skin.paste(plain, (w, skin.height - h))
        skin.save(out / f'morris_{state}.png', optimize=True)
    SPRITES.mkdir(parents=True, exist_ok=True)
    for fr in 'ABC':                                         # sprite lumps behind the model frames
        png_with_grab(Image.new('RGBA', (4, 4), (0, 0, 0, 0)), 2, 3, SPRITES / f'RFMC{fr}0.png')


# ----------------------------------------------------------------------------- main
def main():
    PATCH.mkdir(parents=True, exist_ok=True)
    sky_smoke()
    # facades and walls
    facade('RF2_FAC1', 401, 'shutters')
    facade('RF2_FAC2', 402, 'mixed')
    facade('RF2_FAC3', 403, 'taped')
    upper_facade('RF2_FACU', 404)
    prison_wall('RF2_SANT', 405)
    prison_gate('RF2_SGAT', 406)
    cochin_portal('RF2_COCH')
    save('Texture', 'RF2_RIDO', floor_grime(np.clip(solid(128 * PPU, 128 * PPU, (118, 120, 118)) *
         (1 - 0.18 * (np.arange(128 * PPU) % (3 * PPU) < PPU)[:, None, None]) *
         (0.9 + 0.2 * (fbm(128 * PPU, 128 * PPU, 407, 2.0)[..., None] - 0.5)), 0, 1), 0.3, 0.2))     # iron shutter
    save('Texture', 'RF2_SHOP', floor_grime(planks(128 * PPU, 128 * PPU, 408, 32, (54, 66, 56)), 0.3, 0.2))  # shop front panelling
    save('Texture', 'RF2_PARA', floor_grime(stone_blocks(64 * PPU, 128 * PPU, 409, 32, 64, (164, 156, 140), (110, 104, 94)), 0.25, 0.3))
    save('Texture', 'RF2_QUAI', soot(stone_blocks(128 * PPU, 128 * PPU, 410, 32, 64, (136, 128, 112), (88, 84, 76)), 411, 0.3, top=False))
    # inscriptions
    for name, text, arr in (('RF2_PL01', 'BOULEVARD ARAGO', 13), ('RF2_PL02', 'RUE DE LA SANTÉ', 14),
                            ('RF2_PL03', 'BOULEVARD DE PORT-ROYAL', 5), ('RF2_PL04', 'RUE DE RENNES', 6),
                            ('RF2_PL05', "QUAI D'ORSAY", 7), ('RF2_PL06', 'AVENUE DE LA GRANDE ARMÉE', 17),
                            ('RF2_PL07', 'BOULEVARD DU MONTPARNASSE', 6)):
        paris_plaque(name, text, arr, wunits=64 if len(text) < 18 else 80)
    fascia('RF2_FPHA', 'PHARMACIE', (26, 60, 40), (226, 214, 170), gold=True)
    fascia('RF2_FTSF', 'T. S. F.  -  RÉPARATIONS', (24, 24, 26), (222, 212, 186))
    fascia('RF2_FLIB', 'LIBRAIRIE', (90, 30, 28), (226, 214, 170), wunits=112, gold=True)
    fascia('RF2_FEPI', 'ÉPICERIE  -  VINS', (60, 50, 34), (230, 206, 150), wunits=112, gold=True)
    fascia('RF2_FCAF', 'CAFÉ', (32, 52, 40), (224, 210, 160), wunits=64, gold=True)
    torn_poster('RF2_AFST', [('INTERDICTION', 11), ('DE', 8), ('STATIONNER', 11)], seed=31, torn=0.5)
    torn_poster('RF2_AFMO', [('ORDRE DE', 8), ('MOBILISATION', 9), ('GÉNÉRALE', 9)], seed=32, torn=0.3, bg=(232, 226, 210))
    brush_erreur('RF2_ERPH')
    stencil('RF2_STCA', 'CAVE', 'left')
    stencil('RF2_STPS', 'POSTE DE SECOURS', 'right', wunits=96)
    stencil('RF2_STEA', 'EAU', 'left')
    luna_sign('RF2_LUNA')
    closure_panel('RF2_LUNF')
    morris('RF2_MORR', 'luna')
    morris('RF2_MORJ', 'jerma')
    morris('RF2_MORD', 'dentifrice')
    apothecary_window('RF2_PHVI', 412)
    # vehicles, furniture sides
    tram_side('RF2_TRAM', 420)
    save('Texture', 'RF2_TROF', floor_grime(stone_blocks(64 * PPU, 64 * PPU, 421, 16, 64, (60, 64, 60), (40, 42, 40)), 0.2, 0.2))
    vehicle_side('RF2_AMBU', 422, (176, 170, 150), band=(120, 116, 100), cross=True)
    vehicle_side('RF2_BUSV', 423, (48, 74, 58), band=(196, 184, 150))
    vehicle_side('RF2_TAXI', 424, (40, 40, 42), band=(150, 110, 40), wunits=96)
    sandbags('RF2_SABL', 425)
    book_barricade('RF2_LIVR', 426)
    radio_shelf('RF2_TSFS', 427)
    tram_bench('RF2_BNCH', 428)
    suitcase_side('RF2_VALI', 429)
    save('Texture', 'RF2_TYRE', np.clip(solid(32 * PPU, 64 * PPU, (26, 26, 26)) * (0.8 + 0.4 * (np.sin(np.arange(64 * PPU)[None, :, None] * 0.6) > 0)), 0, 1))
    # flats
    save('Flat', 'RF2_ASPH', asphalt(128 * PPU, 128 * PPU, 430))
    save('Flat', 'RF2_ASPW', floor_grime(asphalt(128 * PPU, 128 * PPU, 431, (70, 66, 62)), 0.2, 1.0))
    save('Flat', 'RF2_RAIL', rails(128 * PPU, 128 * PPU, 432))
    save('Flat', 'RF2_SETT', soot(cobbles(128 * PPU, 128 * PPU, 433), 434, 0.2, top=False))
    save('Flat', 'RF2_EAU1', water(128 * PPU, 128 * PPU, 435))
    save('Flat', 'RF2_TFLR', planks(64 * PPU, 64 * PPU, 436, 8, (92, 70, 48)))
    save('Flat', 'RF2_SABT', np.clip(solid(64 * PPU, 64 * PPU, (126, 110, 82)) * (0.85 + 0.3 * (fbm(64 * PPU, 64 * PPU, 437, 1.6)[..., None] - 0.5)), 0, 1))
    save('Flat', 'RF2_ZINC', np.clip(solid(64 * PPU, 64 * PPU, (150, 150, 146)) * (0.85 + 0.3 * (fbm(64 * PPU, 64 * PPU, 438, 1.4)[..., None] - 0.5)), 0, 1))
    # added with the map (rf02.py)
    amiga_reflection('RF2_AMIG', 450)
    tram_panel('RF2_TRML', 451, 'lower')
    tram_panel('RF2_TRMU', 452, 'upper')
    departures_board('RF2_TABL', 453)
    carved_panel('RF2_COCP', 'HÔPITAL COCHIN')
    palisade('RF2_PALI', 454)
    tarp('RF2_BACH', 455, 'Flat')
    tarp('RF2_BACS', 456, 'Texture')
    wine_setts(457)
    railing('RF2_RAMB')
    draw_radio()
    draw_mattress()
    morris_model()
    # sprites and model skin
    draw_ticket()
    draw_reader_card()
    draw_bag()
    draw_bucket()
    draw_phone()
    draw_shoes_case()
    # TEXTURES lump
    lines = ['// Generated by scripts/mapkit/materials_rf02.py. RF02 material family (Paris, 14 June 1940).', '']
    for kind, name, w, h, ppu in DEFS:
        lines.append(f'{kind} {name}, {w}, {h}\n{{\n    XScale {ppu}\n    YScale {ppu}\n    Patch "patches/rf02/{name}.png", 0, 0\n}}')
    (ROOT / 'src' / 'TEXTURES.rf02').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'materials rf02: {len(DEFS)} definitions written to src/TEXTURES.rf02')


if __name__ == '__main__':
    main()
