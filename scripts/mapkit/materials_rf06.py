#!/usr/bin/env python3
"""RF06 material family: the corridor that should not fit in the building (novel l. 709-731).

PROVISIONAL procedural stand-ins by Opus (request to Astra to follow with the Jerma family). Inscriptions are the
text of the novel composed with real fonts: the stencilled room numbers 117, 404, 017, crossed out; ERREUR Ø in its
variants (black, red, engraved, a zero instead of the Ø, a bar that cuts the word in two). The graffiti are marks and
initials in several scripts, without words invented for the story.

Output: src/patches/rf06/*.png, src/TEXTURES.rf06
Usage: python scripts/mapkit/materials_rf06.py
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from materials import fbm, grain, to_img, solid, tint, plaster, floor_grime, stone_blocks  # noqa: E402
from materials_rf02 import font, text_center  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / 'src' / 'patches' / 'rf06'
PPU = 4
DEFS = []
# Files imported over the stand-ins (Codex RF05_RF06_MATERIALS_01, 01/10): never redrawn, their definition is read from
# the file in place.
DELIVERED = {'RF6_BETN', 'RF6_BETS', 'RF6_PEAU', 'RF6_PEA2'}


def save(kind, name, arr, ppu=PPU):
    if name in DELIVERED:
        img = Image.open(PATCH / f'{name}.png')
        DEFS.append((kind, name, img.size[0], img.size[1], ppu))
        return
    img = arr if isinstance(arr, Image.Image) else to_img(np.clip(arr, 0, 1))
    PATCH.mkdir(parents=True, exist_ok=True)
    img.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append((kind, name, img.size[0], img.size[1], ppu))


def masked(name, rgba, ppu=PPU):
    PATCH.mkdir(parents=True, exist_ok=True)
    rgba.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append(('Texture', name, rgba.size[0], rgba.size[1], ppu))


def concrete(h, w, seed, rgb=(128, 126, 120)):
    arr = plaster(h, w, seed, rgb, rough=0.25, stains=0.2)
    salt = fbm(h, w, seed + 7, 2.6)[..., None]
    return tint(arr, np.clip((salt - 0.6) * 3, 0, 1), (206, 204, 196), 0.35)      # salty damp (l. 709)


def corridor_wall(name, seed, pipes=True):
    """Raw concrete, pipes painted white along the top, damp salt blooms (l. 709). 128 x 96."""
    W, H = 128 * PPU, 96 * PPU
    img = to_img(np.clip(floor_grime(concrete(H, W, seed), 0.35, 0.25), 0, 1))
    d = ImageDraw.Draw(img)
    if pipes:
        for k, y in enumerate((6, 12)):
            d.rectangle([0, y * PPU, W, y * PPU + 3 * PPU], fill=(222, 220, 212))
            d.line([(0, y * PPU + 3 * PPU), (W, y * PPU + 3 * PPU)], fill=(150, 148, 140), width=1)
            for x in range(16 * PPU, W, 48 * PPU):
                d.rectangle([x, y * PPU - PPU, x + 2 * PPU, y * PPU + 4 * PPU], fill=(90, 88, 84))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def peeled_wall(name, seed):
    """Layers of paint lifting like burnt skins; under the newest, graffiti, signatures, dates, marks in several scripts
    (l. 713). 128 x 96."""
    W, H = 128 * PPU, 96 * PPU
    rng = np.random.default_rng(seed)
    base = concrete(H, W, seed, (120, 116, 110))
    img = to_img(np.clip(base, 0, 1))
    d = ImageDraw.Draw(img)
    faces = ['C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/times.ttf', 'C:/Windows/Fonts/cour.ttf', 'C:/Windows/Fonts/comic.ttf']
    marks = ['J.M. 98', 'K.', 'G + R', 'Т.В.', 'Л. 2001', 'VIVA', 'S.F.', 'M.C. 1974', 'ĦAŻ', 'P.', 'A.B.', 'Ж', '1987', 'EZ']
    for k in range(18):
        f = font(int(rng.uniform(5, 11) * PPU), face=faces[k % 4])
        col = tuple(int(c) for c in rng.choice([(20, 20, 24), (130, 30, 26), (30, 60, 110), (40, 90, 50)]))
        d.text((rng.uniform(0, W - 30 * PPU), rng.uniform(20 * PPU, H - 14 * PPU)), marks[k % len(marks)], font=f, fill=col)
    arr = np.asarray(img).astype(float) / 255.0
    paint = solid(H, W, (196, 194, 184)) * (0.92 + 0.1 * fbm(H, W, seed + 1, 2.0)[..., None])
    keep = (fbm(H, W, seed + 2, 1.5) > 0.52)[..., None]
    edge = (np.abs(fbm(H, W, seed + 2, 1.5) - 0.52) < 0.015)[..., None]
    arr = np.where(keep, paint, arr)
    arr = np.where(edge, arr * 0.45, arr)                                    # the lifting edges, dark
    save('Texture', name, floor_grime(arr, 0.35, 0.25))


def stencil_number(name, number):
    """A room number painted with a stencil, then crossed out (l. 709). Masked, 48 x 24."""
    W, H = 48 * PPU, 24 * PPU
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    text_center(d, (2 * PPU, 2 * PPU, W - 2 * PPU, H - 2 * PPU), number, font(int(H * 0.7), face='C:/Windows/Fonts/ARIALNB.TTF'), (24, 24, 26, 230))
    d.line([(3 * PPU, H - 4 * PPU), (W - 3 * PPU, 4 * PPU)], fill=(24, 24, 26, 240), width=2 * PPU)
    a = np.asarray(img).copy()
    a[..., 3] = (a[..., 3] * np.clip(0.7 + 0.5 * (fbm(H, W, len(number) + 3, 1.4) - 0.5), 0, 1)).astype(np.uint8)
    masked(name, Image.fromarray(a))


def erreur(name, kind, seed):
    """ERREUR Ø in its variants (l. 715-717): black paint, red paint, engraved in the concrete, a zero instead of the Ø,
    the bar running far enough to cut ERREUR in two. Masked, 64 x 24."""
    W, H = 64 * PPU * 2, 24 * PPU * 2
    layer = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(layer)
    text = 'ERREUR 0' if kind == 'zero' else 'ERREUR Ø'
    f = font(int(H * 0.46), face='C:/Windows/Fonts/arialbd.ttf' if kind != 'grave' else 'C:/Windows/Fonts/times.ttf')
    text_center(d, (4, H * 0.2, W - 4, H * 0.8), text, f, 255)
    if kind == 'barre':
        d.line([(W * 0.08, H * 0.85), (W * 0.95, H * 0.12)], fill=255, width=int(H * 0.05))
    m = np.asarray(layer.filter(ImageFilter.GaussianBlur(1.0))).astype(float) / 255.0
    m = np.clip(m * (0.8 + 0.4 * fbm(H, W, seed, 1.2)) - 0.05, 0, 1)
    rgba = np.zeros((H, W, 4), np.uint8)
    col = {'noir': (14, 14, 16), 'rouge': (150, 22, 20), 'grave': (70, 68, 64), 'zero': (18, 18, 20), 'barre': (14, 14, 16)}[kind]
    rgba[..., :3] = col
    rgba[..., 3] = (m * (170 if kind == 'grave' else 235)).astype(np.uint8)
    masked(name, Image.fromarray(rgba).resize((W // 2, H // 2), Image.LANCZOS))


def daylight_opening(name):
    """The rectangular opening that cuts the day at the end (l. 729): nearly white, a hint of sea and sky. 64 x 96."""
    W, H = 64 * PPU, 96 * PPU
    y = np.linspace(0, 1, H)[:, None, None]
    sky = np.array((226, 232, 238)) / 255.0
    sea = np.array((150, 170, 186)) / 255.0
    arr = np.where(y < 0.55, sky, sea) * np.ones((H, W, 3))
    arr = arr + 0.04 * (fbm(H, W, 790, 2.0)[..., None] - 0.5)
    save('Texture', name, arr)


def main():
    corridor_wall('RF6_BETN', 700)
    corridor_wall('RF6_BETS', 701, pipes=False)
    peeled_wall('RF6_PEAU', 702)
    peeled_wall('RF6_PEA2', 703)
    for num in ('117', '404', '017'):
        stencil_number(f'RF6_N{num}', num)
    for k, kind in enumerate(('noir', 'rouge', 'grave', 'zero', 'barre')):
        erreur(f'RF6_ER{k + 1}', kind, 710 + k)
    daylight_opening('RF6_JOUR')
    save('Flat', 'RF6_SOL', concrete(64 * PPU, 64 * PPU, 720, (112, 110, 104)))
    save('Flat', 'RF6_PLAF', concrete(64 * PPU, 64 * PPU, 721, (150, 148, 142)))
    lines = ['// Generated by scripts/mapkit/materials_rf06.py. RF06 (the corridor, l. 709-731). PROVISIONAL.', '']
    for kind, name, w, h, ppu in DEFS:
        lines.append(f'{kind} {name}, {w}, {h}\n{{\n    XScale {ppu}\n    YScale {ppu}\n    Patch "patches/rf06/{name}.png", 0, 0\n}}')
    (ROOT / 'src' / 'TEXTURES.rf06').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    print(f'materials rf06: {len(DEFS)} definitions written to src/TEXTURES.rf06')


if __name__ == '__main__':
    main()
