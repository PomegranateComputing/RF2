#!/usr/bin/env python3
"""RF07 material family: the Jerma Palace, Marsaskala, Malta, 22 December 2022 (novel l. 733-765).

PROVISIONAL: procedural stand-ins by Opus under the names Codex is asked for (docs/production/maps/RF07_RF12_DECOUPAGE.md).
Codex's files replace them under the same names (then list them in DELIVERED: never redrawn). Every inscription is the
text of the novel (NO FUTURE, l. 733) composed with a real font, never generated.

The hotel "retired from the world for non-payment" (l. 757): raw concrete, salt, wet plaster, graffiti that cover each
other without erasing; December light, hard and metallic over the sea.

Output: src/patches/rf07/*.png, src/TEXTURES.rf07, src/sprites/rf07/*.png
Usage: python scripts/mapkit/materials_rf07.py --only NAME,...   (or --force-all)
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from materials import fbm, grain, to_img, solid, tint, plaster, floor_grime, stone_blocks, planks, gravel, png_with_grab  # noqa: E402
from materials_rf02 import font, text_center  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / 'src' / 'patches' / 'rf07'
SPRITES = ROOT / 'src' / 'sprites' / 'rf07'
PPU = 4
DEFS = []
DELIVERED = {}
ONLY = set()


def save(kind, name, arr, ppu=PPU):
    if name in DELIVERED or (ONLY and name not in ONLY):
        img = Image.open(PATCH / f'{name}.png')
        DEFS.append((kind, name, img.size[0], img.size[1], DELIVERED.get(name, ppu)))
        return
    img = arr if isinstance(arr, Image.Image) else to_img(np.clip(arr, 0, 1))
    PATCH.mkdir(parents=True, exist_ok=True)
    img.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append((kind, name, img.size[0], img.size[1], ppu))


def save_sprite(img, name):
    if ONLY and name not in ONLY:
        return
    SPRITES.mkdir(parents=True, exist_ok=True)
    png_with_grab(img, img.size[0] // 2, img.size[1], SPRITES / f'{name}.png')


def concrete(h, w, seed, rgb=(150, 148, 140)):
    arr = plaster(h, w, seed, rgb, rough=0.25, stains=0.4)
    salt = (fbm(h, w, seed + 7, 2.6) > 0.7)[..., None]
    arr = np.where(salt, arr * 0.6 + solid(h, w, (226, 224, 214)) * 0.4, arr)    # salt blooms
    return floor_grime(arr, 0.35, 0.3)


def graffiti_layers(name, seed):
    """Graffiti that cover each other without erasing (l. 757): tags over tags, old ones coming back where new paint
    flakes. Abstract strokes and initials only (no invented words)."""
    W, H = 128 * PPU, 128 * PPU
    img = to_img(np.clip(concrete(H, W, seed), 0, 1)).convert('RGB')
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img)
    cols = [(40, 90, 170), (190, 40, 40), (30, 30, 30), (220, 200, 60), (60, 150, 80), (200, 200, 200)]
    for k in range(26):
        c = cols[k % len(cols)]
        x0, y0 = int(rng.uniform(0, W)), int(rng.uniform(H * 0.25, H * 0.95))
        pts = [(x0 + int(rng.normal(0, 40)) * j // 3, y0 + int(rng.normal(0, 18))) for j in range(6)]
        d.line(pts, fill=c, width=int(rng.uniform(4, 10)))
    for k, s in enumerate(('V', 'M', 'K', 'Z', 'A')):
        d.text((int(rng.uniform(20, W - 80)), int(rng.uniform(H * 0.3, H * 0.8))), s, font=font(int(H * 0.12)),
               fill=cols[(k + 2) % len(cols)])
    arr = np.asarray(img).astype(float) / 255.0
    flake = (fbm(H, W, seed + 3, 1.6) > 0.62)[..., None]
    arr = np.where(flake, concrete(H, W, seed + 9) * 0.95, arr)          # newer paint flaked off over older tags
    save('Texture', name, arr)


def facade(name, seed):
    """A wing of the hotel, open: concrete floors, balconies without glass, dark rooms behind (l. 733)."""
    W, H = 128 * PPU, 128 * PPU
    img = to_img(np.clip(concrete(H, W, seed, (196, 190, 176)), 0, 1)).convert('RGB')
    d = ImageDraw.Draw(img)
    for row in range(2):
        y0 = row * 64 * PPU
        d.rectangle([0, y0 + 50 * PPU, W, y0 + 56 * PPU], fill=(150, 146, 136))            # slab edge
        for col in range(2):
            x0 = col * 64 * PPU
            d.rectangle([x0 + 10 * PPU, y0 + 10 * PPU, x0 + 54 * PPU, y0 + 50 * PPU], fill=(28, 26, 26))   # empty bay
            for x in range(x0 + 12 * PPU, x0 + 54 * PPU, 6 * PPU):
                d.line([(x, y0 + 40 * PPU), (x, y0 + 50 * PPU)], fill=(90, 70, 52), width=PPU)          # rusted rail
            d.line([(x0 + 10 * PPU, y0 + 40 * PPU), (x0 + 54 * PPU, y0 + 40 * PPU)], fill=(90, 70, 52), width=PPU)
    save('Texture', name, floor_grime(np.asarray(img).astype(float) / 255.0, 0.4, 0.3))


def no_future(name):
    """NO FUTURE in blue, with the confidence of an old formula (l. 733): masked, the wall shows around it."""
    W, H = 128 * PPU, 32 * PPU
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    text_center(d, (2 * PPU, 2 * PPU, W - 2 * PPU, H - 2 * PPU), 'NO FUTURE', font(int(H * 0.62)), 255)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 36, 78, 168
    a = np.asarray(m).astype(float) * (0.75 + 0.25 * fbm(H, W, 733, 1.4))
    rgba[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    PATCH.mkdir(parents=True, exist_ok=True)
    if not (ONLY and name not in ONLY):
        Image.fromarray(rgba).save(PATCH / f'{name}.png', optimize=True)
    DEFS.append(('Texture', name, W, H, PPU))


def draw_elvis():
    """PROVISIONAL stand-in for Elvis (l. 735): tall, a dark beanie, a headlamp round his neck. A silhouette, three
    frames (standing, walking), until his figure (CAN-017, owner's references)."""
    for frame, step in (('A', 0), ('B', 1), ('C', -1)):
        img = Image.new('RGBA', (64, 128), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        jacket, trousers, skin = (52, 58, 64, 255), (40, 40, 46, 255), (196, 160, 132, 255)
        d.ellipse([24, 6, 40, 24], fill=skin)                                   # head
        d.chord([22, 2, 42, 20], 180, 360, fill=(26, 26, 30, 255))             # the beanie
        d.rectangle([22, 10, 42, 14], fill=(26, 26, 30, 255))
        d.rounded_rectangle([18, 26, 46, 70], 6, fill=jacket)                   # jacket
        d.ellipse([28, 28, 36, 34], fill=(220, 220, 210, 255))                  # the headlamp round his neck
        d.line([(22, 28), (42, 28)], fill=(20, 20, 20, 255), width=2)
        d.rectangle([20 + 2 * step, 70, 30 + 2 * step, 120], fill=trousers)     # legs
        d.rectangle([34 - 2 * step, 70, 44 - 2 * step, 120], fill=trousers)
        d.rectangle([18 + 2 * step, 118, 31 + 2 * step, 126], fill=(22, 22, 22, 255))
        d.rectangle([33 - 2 * step, 118, 46 - 2 * step, 126], fill=(22, 22, 22, 255))
        d.rectangle([12, 30, 18, 62], fill=jacket)                              # arms
        d.rectangle([46, 30, 52, 62], fill=jacket)
        save_sprite(img, f'R7EV{frame}0')


def draw_bedframe():
    """The rusted bedframe across the door (l. 761): standing on its side (A), then lifted aside (B)."""
    for frame, tilt in (('A', 0), ('B', 18)):
        img = Image.new('RGBA', (128, 112), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        rust = (120, 66, 40, 255)
        x0, x1, y0, y1 = 8 + tilt, 120 - tilt // 2, 8, 108
        d.rectangle([x0, y0, x1, y1], outline=rust, width=5)
        for x in range(x0 + 10, x1, 12):
            d.line([(x, y0 + 4), (x, y1 - 4)], fill=(90, 56, 38, 255), width=2)
        for y in range(y0 + 12, y1, 14):
            d.line([(x0 + 4, y), (x1 - 4, y)], fill=(100, 60, 40, 200), width=1)
        save_sprite(img, f'R7SB{frame}0')


def main():
    graffiti_layers('RF7_GRAF', 757)
    facade('RF7_FACA', 733)
    save('Texture', 'RF7_BETO', concrete(64 * PPU, 64 * PPU, 734))
    save('Flat', 'RF7_TERR', floor_grime(stone_blocks(64 * PPU, 64 * PPU, 735, 16, 16, (186, 176, 156), (120, 112, 98)), 0.4, 0.4))
    carpet = solid(64 * PPU, 64 * PPU, (92, 64, 58)) * (0.7 + 0.4 * fbm(64 * PPU, 64 * PPU, 739, 1.8)[..., None])
    save('Flat', 'RF7_MOQU', tint(carpet, (fbm(64 * PPU, 64 * PPU, 740, 2.2)[..., None] > 0.6) * 1.0, (40, 36, 34), 0.6))
    glass = gravel(64 * PPU, 64 * PPU, 761, (70, 70, 72))
    glass = glass + (fbm(64 * PPU, 64 * PPU, 762, 0.5)[..., None] > 0.9) * 0.4                 # shards catching light
    save('Flat', 'RF7_VERR', glass)
    no_future('RF7_NOFU')
    # the sea over the whole horizon, hard, metallic, worked by the wind (l. 733): grey steel, wind streaks, white caps
    h = w = 64 * PPU
    sea = solid(h, w, (78, 92, 104)) * (0.75 + 0.45 * fbm(h, w, 733, 1.2)[..., None])
    yy = np.arange(h)[:, None, None]
    sea = sea * (0.9 + 0.12 * np.sin(yy / (3.0 * PPU) + fbm(h, w, 734, 0.8)[..., None] * 4))
    sea = np.where((fbm(h, w, 735, 0.7) > 0.86)[..., None], solid(h, w, (206, 212, 214)), sea)
    save('Flat', 'RF7_MER', sea)
    draw_elvis()
    draw_bedframe()
    lines = ['// Generated by scripts/mapkit/materials_rf07.py. RF07 material family (Jerma Palace, 22 December 2022).',
             '// PROVISIONAL (Opus, procedural) until Codex\'s files replace them under the same names.', '']
    for kind, name, w, h, ppu in DEFS:
        lines.append(f'{kind} {name}, {w}, {h}\n{{\n    XScale {ppu}\n    YScale {ppu}\n    Patch "patches/rf07/{name}.png", 0, 0\n}}')
    (ROOT / 'src' / 'TEXTURES.rf07').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    print(f'materials rf07: {len(DEFS)} definitions written to src/TEXTURES.rf07')


if __name__ == '__main__':
    if '--only' in sys.argv:
        ONLY.update(sys.argv[sys.argv.index('--only') + 1].split(','))
    elif '--force-all' not in sys.argv:
        sys.exit('materials_rf07.py: nommer les images a dessiner (--only NOM,...) ou --force-all')
    main()
