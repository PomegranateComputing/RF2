#!/usr/bin/env python3
"""RF04/RF05 material family: the Luna Park of the Porte Maillot, closed for ten years, 14 June 1940 (novel l. 451-707).

PROVISIONAL: procedural stand-ins by Opus under the names of Astra's request LUNA-V01
(incoming/astra/DEMANDES_OPUS_20260930/RF04_RF05_LUNA_PARK.md). Astra's files replace them under the same names; this
script is then no longer run for the replaced entries. Same method as the RF01/RF02 families (helpers imported from
materials.py and materials_rf02.py; neither is run from here, nothing of RF01/RF02 is rewritten). Every inscription is
the text of the novel composed with a real font, never generated.

The park dies by material (l. 521): wood splits, metal rusts at the joints, posters come off in strips, broken glass
stays clean under the awnings. Colours of a fete kept in its coolant (l. 461): faded red, cream, bottle green.

Output: src/patches/rf04/*.png, src/TEXTURES.rf04, src/sprites/rf04/*.png, src/sprites/items/RFKYC0.png
Usage: python scripts/mapkit/materials_rf04.py
"""
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from materials import fbm, grain, to_img, solid, tint, plaster, floor_grime, stone_blocks, planks, gravel, png_with_grab  # noqa: E402
from materials_rf02 import font, text_center, soot, stable, NARROW  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / 'src' / 'patches' / 'rf04'
SPRITES = ROOT / 'src' / 'sprites' / 'rf04'
ITEMS = ROOT / 'src' / 'sprites' / 'items'
PPU = 4
DEFS = []

RED = (150, 44, 36)
CREAM = (214, 202, 172)
GREEN = (46, 70, 52)
GREY_BOARD = (136, 134, 128)


# Files delivered by Astra (LUNA-V01, tranche 01, 30/09), imported into src/patches/rf04 under the same names: this
# script no longer draws them and only writes their definition, at the scale of the delivered file (pixels per unit).
DELIVERED = {'RF4_POIN': 8, 'RF4_CLE5': 8, 'RF4_CLE4': 8, 'RF4_NIAG': 8, 'RF4_C617': 8, 'RF4_C618': 8}


def delivered(kind, name):
    img = Image.open(PATCH / f'{name}.png')
    DEFS.append((kind, name, img.size[0], img.size[1], DELIVERED[name]))
    return img


def save(kind, name, arr, ppu=PPU):
    if name in DELIVERED:
        return delivered(kind, name)
    img = arr if isinstance(arr, Image.Image) else to_img(np.clip(arr, 0, 1))
    PATCH.mkdir(parents=True, exist_ok=True)
    img.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append((kind, name, img.size[0], img.size[1], ppu))
    return img


def masked(name, rgba, ppu=PPU):
    """RGBA patch drawn on a decor line or a masked middle (glass, signs, grilles)."""
    if name in DELIVERED:
        delivered('Texture', name)
        return
    PATCH.mkdir(parents=True, exist_ok=True)
    rgba.save(PATCH / f'{name}.png', optimize=True)
    DEFS.append(('Texture', name, rgba.size[0], rgba.size[1], ppu))


def weather(arr, seed, amount=0.25):
    """Damp, dust and flaking: blotchy darkening, lighter dry patches."""
    h, w = arr.shape[:2]
    n = fbm(h, w, seed, 2.2)[..., None]
    arr = arr * (1 - amount * np.clip(n - 0.45, 0, 1) * 1.6)
    return arr + grain(h, w, seed + 1, 0.02)[..., None]


def boards(h, w, seed, board_units=12, rgb=(120, 100, 76), vertical=True):
    """Weathered boards (sheds, hoardings, the back of a decor): vertical by default."""
    if not vertical:
        return planks(h, w, seed, board_units, rgb)
    arr = planks(w, h, seed, board_units, rgb)
    return np.transpose(arr, (1, 0, 2))[:h, :w]


def peel(arr, seed, paint_rgb, amount=0.55):
    """Old paint over wood: the paint survives in patches, the grey wood shows through."""
    h, w = arr.shape[:2]
    n = fbm(h, w, seed, 1.8)
    keep = (n > (1 - amount))[..., None]
    paint = solid(h, w, paint_rgb) * (0.9 + 0.2 * (fbm(h, w, seed + 5, 2.4)[..., None] - 0.5))
    return np.where(keep, paint, arr)


def painted_text(arr, text, box, rgb, size, seed, face=None, wear=0.35):
    """Letters painted on boards, worn away where the paint has flaked."""
    h, w = arr.shape[:2]
    img = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    text_center(d, box, text, font(size, face=face), 255)
    m = np.asarray(img).astype(float)[..., None] / 255.0
    m = m * np.clip(1 - wear * (fbm(h, w, seed, 1.4)[..., None] > 0.62), 0, 1)
    return arr * (1 - m) + np.array(rgb)[None, None, :] / 255.0 * m


# ----------------------------------------------------------------------------- walls and facades
def shed_wall(name, seed, wunits=128, hunits=128, rgb=(118, 104, 84)):
    H, W = hunits * PPU, wunits * PPU
    arr = boards(H, W, seed, 12, rgb)
    arr = floor_grime(weather(arr, seed + 3, 0.3), 0.35, 0.3)
    save('Texture', name, arr)


def guard_hut(name, seed):
    """The guard's hut: planks painted bottle green long ago, the paint in patches (l. 467)."""
    H, W = 128 * PPU, 64 * PPU
    arr = boards(H, W, seed, 8, (110, 96, 76))
    arr = peel(arr, seed + 1, GREEN, 0.6)
    arr = floor_grime(weather(arr, seed + 2, 0.25), 0.3, 0.25)
    save('Texture', name, arr)


def hut_glass(name, seed, erreur=False):
    """The hut's window seen from the service path: dirty glass, mostly clear (masked), a film of grease and dust at
    the bottom; with erreur, ERREUR Ø traced with a greasy fingertip (l. 515-517)."""
    W, H = 48 * PPU, 40 * PPU
    film = fbm(H, W, seed, 1.9)
    yy = np.linspace(0, 1, H)[:, None]
    a = np.clip((film - 0.62) * 2.2 + (yy - 0.7) * 0.9, 0, 0.75)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (150, 146, 132)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    img = Image.fromarray(rgba)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(46, 40, 32, 255), width=2 * PPU)       # the frame
    d.line([(W // 2, 0), (W // 2, H)], fill=(46, 40, 32, 255), width=PPU)             # the glazing bar
    if erreur:
        layer = Image.new('L', (W, H), 0)
        ld = ImageDraw.Draw(layer)
        f = font(int(H * 0.26), bold=False)
        text_center(ld, (4 * PPU, H * 0.28, W - 4 * PPU, H * 0.62), 'ERREUR Ø', f, 255)
        m = np.asarray(layer.filter(ImageFilter.GaussianBlur(1.6))).astype(float) / 255.0
        smear = np.clip(m * (1.1 + 0.5 * fbm(H, W, seed + 4, 1.1)), 0, 1)
        arr = np.asarray(img).astype(float)
        arr[..., :3] = arr[..., :3] * (1 - smear[..., None]) + np.array((22, 18, 14)) * smear[..., None]
        arr[..., 3] = np.maximum(arr[..., 3], smear * 235)
        img = Image.fromarray(arr.astype(np.uint8))
    masked(name, img)


def time_clock(name):
    """The time clock fixed to the wall of the hut (l. 481): a round dial over a card slot, a rack of cards."""
    W, H = 32 * PPU, 48 * PPU
    arr = boards(H, W, 481, 8, (104, 90, 72))
    img = to_img(peel(arr, 482, GREEN, 0.5))
    d = ImageDraw.Draw(img)
    d.rectangle([5 * PPU, 4 * PPU, 27 * PPU, 30 * PPU], fill=(60, 58, 54), outline=(24, 22, 20), width=PPU)
    d.ellipse([8 * PPU, 6 * PPU, 24 * PPU, 22 * PPU], fill=(222, 214, 190), outline=(30, 28, 24), width=PPU)
    cx, cy = 16 * PPU, 14 * PPU
    for k in range(12):
        a = math.radians(k * 30)
        d.line([(cx + 6.4 * PPU * math.sin(a), cy - 6.4 * PPU * math.cos(a)), (cx + 7.2 * PPU * math.sin(a), cy - 7.2 * PPU * math.cos(a))], fill=(30, 28, 24), width=2)
    d.line([(cx, cy), (cx + 3 * PPU * math.sin(math.radians(180)), cy - 3 * PPU * math.cos(math.radians(180)))], fill=(20, 20, 20), width=PPU)   # 6 h
    d.line([(cx, cy), (cx + 5 * PPU * math.sin(math.radians(36)), cy - 5 * PPU * math.cos(math.radians(36)))], fill=(20, 20, 20), width=2)      # 06 min
    d.rectangle([11 * PPU, 24 * PPU, 21 * PPU, 26 * PPU], fill=(16, 16, 16))       # the card slot
    for i in range(4):                                                               # a rack of cards beside it
        y = 33 * PPU + i * 3 * PPU
        d.rectangle([7 * PPU, y, 25 * PPU, y + 2 * PPU], fill=(196, 186, 156), outline=(80, 70, 56))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def key_board(name, keys):
    """The hook of keys, each with a copper tag; the last, lighter, engraved JERMA (l. 495)."""
    W, H = 48 * PPU, 32 * PPU
    img = to_img(peel(boards(H, W, 495, 8, (104, 90, 72)), 496, GREEN, 0.5))
    d = ImageDraw.Draw(img)
    f = font(int(1.7 * PPU), face=NARROW)
    labels = ['ATELIER', 'PISTE', 'SOUS-STATION', 'CHAMBRE FROIDE', 'JERMA']
    for i, lab in enumerate(labels):
        x = int((4 + i * 9) * PPU)
        d.line([(x + 3 * PPU, 4 * PPU), (x + 3 * PPU, 7 * PPU)], fill=(70, 66, 60), width=PPU)     # the hook
        if lab not in keys:
            continue
        d.rectangle([x + 2 * PPU, 7 * PPU, x + 4 * PPU, 16 * PPU], fill=(150, 150, 146))            # the key
        tag = (214, 186, 140) if lab == 'JERMA' else (176, 110, 60)
        d.rectangle([x, 16 * PPU, x + 7 * PPU, 24 * PPU], fill=tag, outline=(90, 56, 30))
        tx = Image.new('L', (8 * PPU, 7 * PPU), 0)
        td = ImageDraw.Draw(tx)
        text_center(td, (0, 0, 8 * PPU, 7 * PPU), lab, f, 255)
        img.paste((50, 30, 16), (x, 16 * PPU), tx.rotate(0))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def brooklyn(name):
    """A painted decor of a suspension bridge on grey boards, BROOKLYN BRIDGE in red letters (l. 523)."""
    wunits, hunits, ppu = 256, 256, 2          # as tall as the park's sky (walls to the sky never repeat)
    W, H = wunits * ppu, hunits * ppu
    arr = boards(H, W, 523, 16, GREY_BOARD)
    arr = arr * 0.55 + solid(H, W, GREY_BOARD) * 0.45
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    ink = (70, 72, 78)
    for tx in (0.24, 0.76):                                           # towers
        x = int(W * tx)
        d.rectangle([x - 7 * ppu, int(H * 0.2), x + 7 * ppu, int(H * 0.86)], outline=ink, width=3 * ppu)
        d.polygon([(x - 5 * ppu, int(H * 0.3)), (x, int(H * 0.24)), (x + 5 * ppu, int(H * 0.3))], outline=ink)
    deck = int(H * 0.66)
    d.line([(0, deck), (W, deck)], fill=ink, width=3 * ppu)
    for (x0, x1) in ((-0.1, 0.24), (0.24, 0.76), (0.76, 1.1)):     # main cables and hangers
        pts = []
        for k in range(41):
            t = k / 40
            x = (x0 + (x1 - x0) * t) * W
            sag = 0.34 if x0 == 0.24 else 0.2
            y = H * (0.22 + sag * (1 - (2 * t - 1) ** 2)) if x0 == 0.24 else H * (0.22 + 0.44 * (t if x0 > 0.5 else 1 - t))
            pts.append((x, y))
        d.line(pts, fill=ink, width=2 * ppu)
        for (x, y) in pts[::3]:
            d.line([(x, y), (x, deck)], fill=ink, width=1)
    arr = np.asarray(img).astype(float) / 255.0
    arr = painted_text(arr, 'BROOKLYN BRIDGE', (int(W * 0.06), int(H * 0.02), int(W * 0.94), int(H * 0.2)), RED, int(H * 0.15), 524, wear=0.3)
    arr = floor_grime(weather(arr, 525, 0.3), 0.3, 0.25)
    save('Texture', name, arr, ppu)


def cables(name, seed):
    """Technical corridor behind the decor: raw boards, bundles of cables on cleats, porcelain insulators (l. 523)."""
    W, H = 128 * PPU, 96 * PPU
    arr = weather(boards(H, W, seed, 12, (86, 78, 66)), seed + 1, 0.35)
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for k in range(7):
        y = int((22 + k * 7 + rng.normal(0, 1.5)) * PPU)
        sag = rng.uniform(2, 6) * PPU
        pts = [(x, y + sag * math.sin(math.pi * (x % (32 * PPU)) / (32 * PPU))) for x in range(0, W + 1, 4)]
        d.line(pts, fill=(22, 20, 18), width=int(rng.uniform(0.6, 1.4) * PPU))
    for x in range(8 * PPU, W, 32 * PPU):
        for k in range(2):
            y = int((20 + k * 26) * PPU)
            d.ellipse([x - 2 * PPU, y - 2 * PPU, x + 2 * PPU, y + 2 * PPU], fill=(214, 208, 196), outline=(90, 86, 80))
    save('Texture', name, floor_grime(np.asarray(img).astype(float) / 255.0, 0.35, 0.25))


def basin_wall(name, seed):
    """Wall of the empty basin: rendered concrete, a line of dry algae at shoulder height (48 u from the bottom),
    stains below it (l. 523)."""
    W, H = 128 * PPU, 96 * PPU
    arr = plaster(H, W, seed, (156, 152, 142), rough=0.18, stains=0.2)
    line = H - 48 * PPU
    yy = np.arange(H)[:, None, None]
    band = np.exp(-((yy - line) / (2.2 * PPU)) ** 2) * (0.7 + 0.6 * fbm(H, W, seed + 3, 1.3)[..., None])
    arr = tint(arr, np.clip(band, 0, 1), (70, 78, 52), 0.8)
    below = np.clip((yy - line) / (H - line), 0, 1) * fbm(H, W, seed + 5, 2.0)[..., None]
    arr = tint(arr, np.clip(below * 1.2, 0, 1), (76, 80, 66), 0.45)
    save('Texture', name, floor_grime(arr, 0.3, 0.2))


def sign_board(name, text, wunits, hunits, bg, fg, seed, face=None):
    W, H = wunits * PPU, hunits * PPU
    arr = boards(H, W, seed, 8, bg, vertical=False) * 0.4 + solid(H, W, bg) * 0.6
    arr = painted_text(arr, text, (3 * PPU, 2 * PPU, W - 3 * PPU, H - 2 * PPU), fg, int(H * 0.5), seed + 1, face=face)
    arr = weather(arr, seed + 2, 0.3)
    save('Texture', name, arr)


def fake_rock(name, seed):
    """Painted staff rocks of the dry cascade: plaster on lath, flaking to the grey render."""
    W, H = 128 * PPU, 128 * PPU
    n1 = fbm(H, W, seed, 2.8)[..., None]
    n2 = fbm(H, W, seed + 1, 1.6)[..., None]
    arr = solid(H, W, (112, 100, 84)) * (0.6 + 0.7 * n1) * (0.9 + 0.2 * (n2 - 0.5))
    flake = (fbm(H, W, seed + 2, 1.5) > 0.66)[..., None]
    arr = np.where(flake, solid(H, W, (150, 146, 138)) * (0.85 + 0.2 * n2), arr)
    save('Texture', name, floor_grime(arr, 0.3, 0.3))


def trestle(name, seed):
    """Roller-coaster timber: posts and crossed braces, black with damp at the feet (l. 551)."""
    W, H = 64 * PPU, 128 * PPU
    img = to_img(np.clip(solid(H, W, (20, 18, 16)), 0, 1))
    wood = weather(boards(H, W, seed, 16, (104, 86, 62)), seed + 1, 0.25)
    wimg = to_img(np.clip(wood, 0, 1))
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for x in (4 * PPU, W - 4 * PPU):
        d.rectangle([x - 4 * PPU, 0, x + 4 * PPU, H], fill=255)
    for y0 in (8, 72):
        d.line([(4 * PPU, y0 * PPU), (W - 4 * PPU, (y0 + 56) * PPU)], fill=255, width=4 * PPU)
        d.line([(W - 4 * PPU, y0 * PPU), (4 * PPU, (y0 + 56) * PPU)], fill=255, width=4 * PPU)
    d.rectangle([0, 60 * PPU, W, 66 * PPU], fill=255)
    img = Image.composite(wimg, img, m)
    rgba = np.asarray(img.convert('RGBA')).copy()
    rgba[..., 3] = np.asarray(m)
    masked(name, Image.fromarray(rgba))


def turnstile_counter(name, number):
    """The mechanical counter on the turnstile (l. 531): 617, then 618."""
    W, H = 32 * PPU, 24 * PPU
    arr = solid(H, W, (88, 84, 78)) * (0.85 + 0.3 * (fbm(H, W, 531, 1.6)[..., None] - 0.5))
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    d.rectangle([5 * PPU, 7 * PPU, 27 * PPU, 17 * PPU], fill=(26, 24, 22), outline=(150, 146, 136), width=PPU)
    f = font(int(8 * PPU), face='C:/Windows/Fonts/cour.ttf')
    for i, ch in enumerate(str(number)):
        x = (6 + i * 7) * PPU
        d.rectangle([x, 8 * PPU, x + 6 * PPU, 16 * PPU], fill=(232, 226, 210))
        text_center(d, (x, 8 * PPU, x + 6 * PPU, 16 * PPU), ch, f, (20, 20, 20))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def turnstile_side(name):
    W, H = 32 * PPU, 40 * PPU
    arr = solid(H, W, (70, 68, 64)) * (0.8 + 0.4 * (fbm(H, W, 532, 1.6)[..., None] - 0.5))
    rust = (fbm(H, W, 533, 2.2) > 0.6)[..., None]
    arr = np.where(rust, arr * np.array([1.3, 0.9, 0.7]), arr)
    save('Texture', name, arr)


def mirror_pits(name, seed):
    """In front of a mirror line: the silver gone in spots and at the edges, the frame (l. 533). Masked."""
    W, H = 64 * PPU, 96 * PPU
    rgba = np.zeros((H, W, 4), np.uint8)
    n = fbm(H, W, seed, 1.3)
    yy, xx = np.mgrid[:H, :W]
    edge = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)) / (6 * PPU)
    lost = np.clip((n - 0.68) * 5 + np.clip(1 - edge, 0, 1) * 0.8, 0, 1)
    rgba[..., :3] = (58, 54, 48)
    rgba[..., 3] = (lost * 220).astype(np.uint8)
    img = Image.fromarray(rgba)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(120, 96, 52, 255), width=3 * PPU)
    d.rectangle([3 * PPU, 3 * PPU, W - 1 - 3 * PPU, H - 1 - 3 * PPU], outline=(70, 52, 28, 255), width=PPU)
    masked(name, img)


def poster(name, seed, kind):
    """Torn posters of the park inside the hoarding (l. 455): women diving into basins, cars on a banked track,
    acrobats, a boxing champion. Printed images, no invented slogan: the park's name only."""
    W, H = 48 * PPU, 64 * PPU
    bg = {'plonge': (60, 110, 150), 'piste': (190, 150, 60), 'acro': (150, 50, 50), 'boxe': (210, 196, 160)}[kind]
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    dark = (24, 22, 26)
    if kind == 'plonge':
        d.rectangle([0, int(H * 0.62), W, H], fill=(40, 80, 120))
        for k in range(3):
            x = int(W * (0.25 + 0.25 * k))
            d.line([(x, int(H * 0.2)), (x + 3 * PPU, int(H * 0.4))], fill=(236, 220, 200), width=2 * PPU)
            d.ellipse([x - 2 * PPU, int(H * 0.15), x + 2 * PPU, int(H * 0.2)], fill=(236, 220, 200))
    elif kind == 'piste':
        d.polygon([(0, int(H * 0.8)), (W, int(H * 0.45)), (W, int(H * 0.6)), (0, H)], fill=(120, 100, 70))
        d.rectangle([int(W * 0.35), int(H * 0.5), int(W * 0.65), int(H * 0.62)], fill=dark)
        for x in (0.4, 0.6):
            d.ellipse([int(W * x) - 2 * PPU, int(H * 0.6), int(W * x) + 2 * PPU, int(H * 0.66)], fill=dark)
    elif kind == 'acro':
        for k, (x, y) in enumerate(((0.3, 0.55), (0.5, 0.35), (0.7, 0.55))):
            cx, cy = int(W * x), int(H * y)
            d.ellipse([cx - 2 * PPU, cy - 9 * PPU, cx + 2 * PPU, cy - 5 * PPU], fill=(236, 220, 200))
            d.line([(cx, cy - 5 * PPU), (cx, cy + 6 * PPU)], fill=(236, 220, 200), width=2 * PPU)
            d.line([(cx - 5 * PPU, cy - 3 * PPU), (cx + 5 * PPU, cy - 3 * PPU)], fill=(236, 220, 200), width=PPU)
    else:
        d.ellipse([int(W * 0.38), int(H * 0.18), int(W * 0.62), int(H * 0.34)], fill=dark)
        d.rectangle([int(W * 0.34), int(H * 0.34), int(W * 0.66), int(H * 0.7)], fill=dark)
        d.ellipse([int(W * 0.18), int(H * 0.36), int(W * 0.36), int(H * 0.48)], fill=(160, 30, 30))
        d.ellipse([int(W * 0.64), int(H * 0.36), int(W * 0.82), int(H * 0.48)], fill=(160, 30, 30))
    text_center(d, (2 * PPU, int(H * 0.84), W - 2 * PPU, H - 2 * PPU), 'LUNA PARK', font(int(5 * PPU)), (240, 232, 210))
    arr = np.asarray(img).astype(float) / 255.0
    arr = arr * (0.8 + 0.3 * (fbm(H, W, seed, 2.0)[..., None] - 0.5))
    a = np.full((H, W), 255, np.uint8)
    edge = fbm(H, W, seed + 9, 1.4)
    yy, xx = np.mgrid[:H, :W] / np.array([H, W])[:, None, None]
    a[(yy * 0.6 + 0.35 * (edge - 0.5) + 0.5 * (1 - xx)) > 0.95] = 0              # strips torn from the lower left
    a[(edge > 0.8) & (yy < 0.3)] = 0
    rgba = np.dstack([(np.clip(arr, 0, 1) * 255).astype(np.uint8), a])
    masked(name, Image.fromarray(rgba))


def iron_door(name, seed):
    """The substation door: riveted sheet iron, rust at the edges and the lock (l. 551)."""
    W, H = 64 * PPU, 96 * PPU
    arr = solid(H, W, (74, 72, 68)) * (0.85 + 0.3 * (fbm(H, W, seed, 1.8)[..., None] - 0.5))
    yy, xx = np.mgrid[:H, :W]
    edge = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)) < 3 * PPU
    rust = ((fbm(H, W, seed + 1, 2.2) > 0.55) | edge)[..., None]
    arr = np.where(rust, arr * np.array([1.45, 0.95, 0.7]), arr)
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    for y in range(4 * PPU, H, 12 * PPU):
        for x in (3 * PPU, W - 3 * PPU):
            d.ellipse([x - PPU, y - PPU, x + PPU, y + PPU], fill=(40, 38, 36))
    d.rectangle([W - 14 * PPU, 44 * PPU, W - 8 * PPU, 54 * PPU], fill=(34, 32, 30))       # the lock plate
    d.ellipse([W - 12 * PPU, 47 * PPU, W - 10 * PPU, 49 * PPU], fill=(8, 8, 8))
    save('Texture', name, floor_grime(np.asarray(img).astype(float) / 255.0, 0.3, 0.2))


def attraction_facade(name, seed, paint, trim, text=None):
    """Facades that still promise worlds (l. 521): painted boards in bands, the paint flaking, an old name."""
    wunits, hunits, ppu = 128, 256, 2          # as tall as the park's sky
    W, H = wunits * ppu, hunits * ppu
    arr = boards(H, W, seed, 16, (116, 100, 80))
    arr = peel(arr, seed + 1, paint, 0.62)
    yy = np.arange(H)[:, None, None]
    band = ((yy % (48 * ppu)) < 4 * ppu)
    arr = np.where(band, solid(H, W, trim), arr)
    if text:
        arr = painted_text(arr, text, (int(W * 0.06), int(H * 0.06), int(W * 0.94), int(H * 0.2)), (232, 222, 196), int(H * 0.1), seed + 2)
    save('Texture', name, floor_grime(weather(arr, seed + 3, 0.3), 0.3, 0.25), ppu)


# ----------------------------------------------------------------------------- flats
def herbs(h, w, seed):
    """The service path overgrown: gravel, mud, tufts of grass (l. 463)."""
    g = gravel(h, w, seed, (118, 112, 96))
    tuft = fbm(h, w, seed + 1, 2.4)[..., None]
    grass = solid(h, w, (78, 92, 52)) * (0.8 + 0.4 * fbm(h, w, seed + 2, 0.9)[..., None])
    return np.where(tuft > 0.5, grass, g)


def narrow_rails(h, w, seed):
    """Narrow rails across the path, rusty but still fixed to their sleepers (l. 463); rails along x."""
    arr = herbs(h, w, seed)
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    for x in range(4 * PPU, w, 16 * PPU):
        d.rectangle([x, 12 * PPU, x + 6 * PPU, 52 * PPU], fill=(78, 62, 44))
    for y in (22 * PPU, 42 * PPU):
        d.rectangle([0, y - PPU, w, y + PPU], fill=(96, 70, 52))
        d.line([(0, y), (w, y)], fill=(150, 140, 128), width=1)
    return np.asarray(img).astype(float) / 255.0


def slab_grass(h, w, seed):
    """Slabs with grass between them (l. 551)."""
    arr = stone_blocks(h, w, seed, 32, 32, (150, 144, 130), (70, 90, 50))
    return weather(arr, seed + 1, 0.2)


def warped_parquet(h, w, seed):
    """The dance floor: long strips, warped (bands of light and shade across the strips), worn (l. 533)."""
    arr = planks(h, w, seed, 6, (128, 92, 58))
    yy, xx = np.mgrid[:h, :w]
    warp = 0.12 * np.sin(xx / (22 * PPU) * math.pi * 2 + fbm(h, w, seed + 1, 1.2) * 3)[..., None]
    arr = arr * (1 + warp)
    wear = fbm(h, w, seed + 2, 2.2)[..., None]
    return tint(arr, np.clip((wear - 0.55) * 3, 0, 1), (150, 132, 108), 0.4)


def basin_floor(h, w, seed):
    arr = plaster(h, w, seed, (128, 126, 116), rough=0.2, stains=0.3)
    moss = fbm(h, w, seed + 1, 2.4)[..., None]
    return tint(arr, np.clip((moss - 0.5) * 3, 0, 1), (60, 68, 48), 0.6)


def black_puddle(h, w, seed):
    """A black puddle at the bottom of the basin (l. 523)."""
    arr = solid(h, w, (14, 14, 16)) * (0.8 + 0.4 * fbm(h, w, seed, 1.6)[..., None])
    return arr + (fbm(h, w, seed + 1, 0.6)[..., None] > 0.93) * 0.18


def canvas(h, w, seed):
    """The gutted marquee's canvas, stained and torn (flat and side)."""
    arr = solid(h, w, (170, 150, 116)) * (0.8 + 0.35 * fbm(h, w, seed, 1.8)[..., None])
    stripe = ((np.arange(w)[None, :, None] // (16 * PPU)) % 2 == 0)
    return np.where(stripe, arr * np.array([1.05, 0.62, 0.55]), arr)


# ----------------------------------------------------------------------------- sprites (provisional)
def sprite_rgba(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def save_sprite(img, name, yoff_extra=0, folder=SPRITES):
    folder.mkdir(parents=True, exist_ok=True)
    png_with_grab(img, img.size[0] // 2, img.size[1] + yoff_extra, folder / f'{name}.png')


def draw_guard():
    """PROVISIONAL stand-in for F04-01: the guard seen through dirty glass, a dark seated mass with a cap and a pale
    moustache, a register on the knees. Only a silhouette; Astra's figure replaces it."""
    for state, look_up in (('A', False), ('B', True)):
        img = sprite_rgba(96, 112)
        d = ImageDraw.Draw(img)
        body = (40, 38, 36, 255)
        d.rounded_rectangle([22, 44, 74, 100], 14, fill=body)                   # shoulders and trunk, wide
        hy = 20 if look_up else 26
        d.ellipse([34, hy, 62, hy + 30], fill=(58, 50, 46, 255))                 # head, in the shade of the hut
        d.rectangle([30, hy - 2, 66, hy + 8], fill=(30, 30, 34, 255))           # the cap
        d.rectangle([38, hy + 5, 70, hy + 9], fill=(26, 26, 30, 255))           # its peak
        d.rectangle([40, hy + 20, 56, hy + 23], fill=(176, 172, 164, 255))      # white moustache, dimmed by the glass
        d.rectangle([26, 78, 70, 88], fill=(120, 108, 84, 255))                 # the register on the knees
        d.line([(48, 78), (48, 88)], fill=(90, 70, 50, 255), width=2)
        d.rectangle([28, 100, 40, 112], fill=body)
        d.rectangle([56, 100, 68, 112], fill=body)
        save_sprite(img, f'R4G1{state}0')


def draw_shoe():
    """A child's shoe: white leather, side buckle, sole almost new (l. 525). Flat sprite seen from above."""
    img = sprite_rgba(48, 28)
    d = ImageDraw.Draw(img)
    d.ellipse([4, 6, 44, 24], fill=(40, 36, 32, 255))                           # sole
    d.ellipse([6, 7, 42, 22], fill=(232, 228, 216, 255))                         # upper
    d.ellipse([10, 10, 22, 19], fill=(60, 56, 50, 255))                          # opening
    d.rectangle([26, 8, 30, 21], fill=(214, 208, 196, 255))                      # strap
    d.rectangle([27, 7, 31, 11], fill=(180, 170, 120, 255))                      # buckle
    save_sprite(img, 'R4SHA0', yoff_extra=-12)


def draw_jukebox():
    """PROVISIONAL stand-in for M04-10: the juke-box under a tarpaulin (A), uncovered (B) with the cracked glass,
    yellowed keys and the only readable label THE SKY IS EMPTY (l. 541-545)."""
    W, H = 96, 150
    img = sprite_rgba(W, H)
    d = ImageDraw.Draw(img)
    d.polygon([(8, H), (4, 40), (20, 8), (48, 2), (76, 8), (92, 40), (88, H)], fill=(96, 92, 80, 255))
    for k in range(6):
        d.line([(12 + k * 14, 10), (8 + k * 15, H)], fill=(78, 74, 64, 255), width=2)
    save_sprite(img, 'R4JBA0')
    img = sprite_rgba(W, H)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 10, 88, H - 1], 30, fill=(120, 70, 40, 255))           # cabinet
    d.rounded_rectangle([18, 20, 78, 70], 20, fill=(70, 90, 96, 255))               # the glass dome
    d.line([(24, 30), (50, 62)], fill=(200, 210, 214, 255), width=1)                # the crack
    d.line([(50, 62), (70, 44)], fill=(200, 210, 214, 255), width=1)
    d.rectangle([18, 76, 78, 100], fill=(214, 206, 176, 255))                       # the list, rubbed out
    for k in range(5):
        d.line([(22, 80 + k * 4), (74, 80 + k * 4)], fill=(186, 176, 146, 255))
    d.rectangle([22, 86, 74, 92], fill=(236, 230, 214, 255))
    f = font(6, bold=False)
    text_center(d, (22, 86, 74, 92), 'THE SKY IS EMPTY', f, (30, 28, 26))
    for k in range(8):                                                             # yellowed keys
        d.rectangle([20 + k * 7, 106, 25 + k * 7, 112], fill=(222, 206, 150, 255))
    d.rectangle([14, 120, 82, H - 6], fill=(90, 50, 30, 255))                      # speaker grille
    for k in range(6):
        d.line([(18, 124 + k * 4), (78, 124 + k * 4)], fill=(60, 34, 22, 255))
    save_sprite(img, 'R4JBB0')


def draw_substation_key():
    """RFKYC0: the key of the substation, its copper tag (l. 495)."""
    img = sprite_rgba(56, 28)
    d = ImageDraw.Draw(img)
    steel = (150, 146, 136, 255)
    d.ellipse([2, 6, 20, 24], outline=steel, width=5)
    d.rectangle([18, 12, 52, 17], fill=steel)
    d.rectangle([44, 17, 48, 26], fill=steel)
    d.rectangle([36, 17, 40, 23], fill=steel)
    d.rectangle([20, 2, 36, 12], fill=(176, 110, 60, 255), outline=(90, 56, 30, 255))
    img = img.resize((28, 14), Image.LANCZOS)
    save_sprite(img, 'RFKYC0', folder=ITEMS)


# ----------------------------------------------------------------------------- RF05: the substation (l. 555-683)
def marble_panel(name, seed):
    """Marble switchboard panels: knife switches on porcelain bases, porcelain fuses, a copper bar (l. 559)."""
    W, H = 128 * PPU, 128 * PPU
    n = fbm(H, W, seed, 2.4)
    arr = solid(H, W, (206, 204, 198)) * (0.9 + 0.12 * n[..., None])
    veins = np.abs(np.sin((np.arange(W)[None, :] * 0.03 + n * 9))) < 0.05
    arr[veins] = arr[veins] * 0.72
    img = to_img(np.clip(floor_grime(arr, 0.3, 0.25), 0, 1))
    d = ImageDraw.Draw(img)
    for col in range(4):
        x = (10 + col * 30) * PPU
        d.rectangle([x, 20 * PPU, x + 12 * PPU, 30 * PPU], fill=(232, 228, 216), outline=(120, 116, 108), width=2)
        d.line([(x + 2 * PPU, 25 * PPU), (x + 14 * PPU, 12 * PPU)], fill=(176, 110, 60), width=2 * PPU)       # the blade
        d.ellipse([x + 13 * PPU, 10 * PPU, x + 16 * PPU, 13 * PPU], fill=(30, 28, 26))
        for k in range(3):
            y = (48 + k * 12) * PPU
            d.rounded_rectangle([x, y, x + 12 * PPU, y + 7 * PPU], 6, fill=(236, 232, 220), outline=(120, 116, 108))
    d.rectangle([0, 92 * PPU, W, 95 * PPU], fill=(150, 96, 52))
    for x in range(6 * PPU, W, 20 * PPU):                                                                  # tarred cables down
        d.line([(x, 0), (x, 8 * PPU)], fill=(16, 14, 12), width=3 * PPU)
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def dials(name, state):
    """The dials (l. 561, 683): GRAND HUIT, CHAMBRE DES GLACES, SALLE DE DANSE, POMPES, ECLAIRAGE EXTERIEUR, JERMA.
    state 0: before (GRAND HUIT too high, CHAMBRE DES GLACES at zero, JERMA at zero); 1: after (the lines up, the
    JERMA needle stopped on a value that is not on the scale)."""
    W, H = 96 * PPU, 48 * PPU
    arr = solid(H, W, (196, 194, 188)) * (0.92 + 0.1 * fbm(H, W, 570, 2.2)[..., None])
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    labels = ['GRAND HUIT', 'CHAMBRE DES GLACES', 'SALLE DE DANSE', 'POMPES', 'ÉCLAIRAGE EXTÉRIEUR', 'JERMA']
    before = [0.92, 0.0, 0.1, 0.05, 0.08, 0.0]
    after = [0.62, 0.0, 0.58, 0.55, 0.6, 1.18]
    f = font(int(2.0 * PPU), face=NARROW)
    for i, lab in enumerate(labels):
        cx, cy = (9 + (i % 3) * 30) * PPU, (13 + (i // 3) * 23) * PPU
        r = 8 * PPU
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 232, 218), outline=(40, 38, 34), width=PPU)
        for k in range(11):
            a = math.radians(-135 + k * 27)
            d.line([(cx + 0.8 * r * math.sin(a), cy - 0.8 * r * math.cos(a)), (cx + r * math.sin(a), cy - r * math.cos(a))], fill=(40, 38, 34), width=1)
        v = (after if state else before)[i]
        a = math.radians(-135 + 270 * min(v, 1.2))
        d.line([(cx, cy), (cx + 0.85 * r * math.sin(a), cy - 0.85 * r * math.cos(a))], fill=(150, 20, 16), width=max(1, PPU // 2))
        text_center(d, (cx - 14 * PPU, cy + r + PPU, cx + 14 * PPU, cy + r + 4 * PPU), lab, f, (30, 28, 24))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def node_box(name, state):
    """The box without a plate, its black paint newer than the rest (l. 561); open (l. 565): thin cards in a row,
    green diodes, 40 mm fans, NODE 0 in white marker on a tab; state 2: the diodes red (l. 677)."""
    W, H = 48 * PPU, 64 * PPU
    arr = solid(H, W, (22, 22, 24)) * (0.9 + 0.2 * fbm(H, W, 571, 1.8)[..., None])
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    if state == 0:
        d.rectangle([2 * PPU, 2 * PPU, W - 2 * PPU, H - 2 * PPU], outline=(46, 46, 50), width=PPU)
        d.rectangle([W - 8 * PPU, 30 * PPU, W - 6 * PPU, 36 * PPU], fill=(70, 70, 74))
    else:
        d.rectangle([3 * PPU, 3 * PPU, W - 3 * PPU, H - 3 * PPU], fill=(34, 36, 38))
        for k in range(8):                                                                                   # the cards
            x = (6 + k * 4) * PPU
            d.rectangle([x, 8 * PPU, x + 2 * PPU, 40 * PPU], fill=(28, 70, 40))
            led = (40, 220, 90) if state == 1 else (230, 40, 30)
            d.ellipse([x, 42 * PPU, x + 2 * PPU, 44 * PPU], fill=led)
        for k in range(2):                                                                                   # fans
            cx = (14 + k * 20) * PPU
            d.ellipse([cx - 6 * PPU, 48 * PPU, cx + 6 * PPU, 60 * PPU], outline=(90, 90, 94), width=PPU)
            d.line([(cx - 5 * PPU, 54 * PPU), (cx + 5 * PPU, 54 * PPU)], fill=(90, 90, 94), width=1)
        d.rectangle([6 * PPU, 3 * PPU, 22 * PPU, 7 * PPU], fill=(40, 40, 44))
        text_center(d, (6 * PPU, 3 * PPU, 22 * PPU, 7 * PPU), 'NODE 0', font(int(3 * PPU), bold=False), (236, 236, 236))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def lever_panel(name, position):
    """The main switch: bakelite lever, MARCHE and ARRET, and between them ATTENTE engraved with a point (l. 571)."""
    W, H = 32 * PPU, 48 * PPU
    arr = solid(H, W, (58, 60, 58)) * (0.9 + 0.2 * fbm(H, W, 572, 1.8)[..., None])
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    f = font(int(2.6 * PPU))
    text_center(d, (0, 3 * PPU, W, 7 * PPU), 'MARCHE', f, (220, 216, 200))
    text_center(d, (0, 21 * PPU, W, 25 * PPU), 'ATTENTE', font(int(2.2 * PPU), bold=False), (150, 148, 140))
    text_center(d, (0, 40 * PPU, W, 44 * PPU), 'ARRÊT', f, (220, 216, 200))
    d.line([(W // 2, 9 * PPU), (W // 2, 38 * PPU)], fill=(30, 30, 30), width=2 * PPU)                      # the slot
    y = {'marche': 11, 'arret': 36}[position] * PPU
    d.rounded_rectangle([W // 2 - 5 * PPU, y - 2 * PPU, W // 2 + 5 * PPU, y + 2 * PPU], 6, fill=(60, 30, 20))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def fuse_board(name, jerma):
    """Fuse holders: GRAND HUIT, SALLE DE DANSE, and a third on no plan, JERMA, its holder empty (l. 669); jerma:
    the white porcelain fuse printed 22.12.2022 in place."""
    W, H = 48 * PPU, 32 * PPU
    arr = solid(H, W, (200, 198, 190)) * (0.92 + 0.1 * fbm(H, W, 573, 2.2)[..., None])
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    f = font(int(2.2 * PPU), face=NARROW)
    for i, lab in enumerate(['GRAND HUIT', 'SALLE DE DANSE', 'JERMA']):
        x = (4 + i * 15) * PPU
        d.rectangle([x, 8 * PPU, x + 10 * PPU, 24 * PPU], fill=(60, 58, 54))
        if i < 2 or jerma:
            d.rounded_rectangle([x + 2 * PPU, 10 * PPU, x + 8 * PPU, 22 * PPU], 6, fill=(238, 236, 228))
        text_center(d, (x - 2 * PPU, 25 * PPU, x + 12 * PPU, 29 * PPU), lab, f, (30, 28, 24))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def vault(name, seed):
    """The vaulted substation: bricks with damp, a band of tar where the cables run."""
    W, H = 128 * PPU, 128 * PPU
    arr = stone_blocks(H, W, seed, 8, 24, (132, 96, 78), (86, 80, 72))
    return save('Texture', name, floor_grime(weather(arr, seed + 1, 0.35), 0.4, 0.3))


def stair_wall(name, seed):
    """The stair: wooden handrails swollen by damp, copper pipes gone green (l. 555)."""
    W, H = 64 * PPU, 128 * PPU
    arr = plaster(H, W, seed, (150, 146, 136), rough=0.2, stains=0.35)
    img = to_img(np.clip(floor_grime(arr, 0.4, 0.3), 0, 1))
    d = ImageDraw.Draw(img)
    for k, y in enumerate((40, 48)):
        d.rectangle([0, y * PPU, W, y * PPU + 2 * PPU], fill=(70, 120, 96) if k else (84, 130, 104))
    d.rectangle([0, 36 * PPU, W, 38 * PPU], fill=(100, 72, 46))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def motor_side(name, seed):
    """Cast-iron motor, painted grey-green, fins, a brass plate without text."""
    W, H = 64 * PPU, 48 * PPU
    arr = solid(H, W, (74, 86, 78)) * (0.85 + 0.3 * fbm(H, W, seed, 1.8)[..., None])
    img = to_img(np.clip(arr, 0, 1))
    d = ImageDraw.Draw(img)
    for x in range(4 * PPU, W, 6 * PPU):
        d.line([(x, 4 * PPU), (x, H - 4 * PPU)], fill=(50, 58, 52), width=PPU)
    d.rectangle([24 * PPU, 18 * PPU, 40 * PPU, 28 * PPU], fill=(176, 146, 80))
    save('Texture', name, np.asarray(img).astype(float) / 255.0)


def wheel(name, turn):
    """The heavy wheel and its leather belt (masked): spokes turned by `turn` degrees (two frames when it runs)."""
    W = H = 64 * PPU
    img = sprite_rgba(W, H)
    d = ImageDraw.Draw(img)
    c = W // 2
    d.ellipse([2 * PPU, 2 * PPU, W - 2 * PPU, H - 2 * PPU], outline=(60, 62, 60, 255), width=5 * PPU)
    for k in range(6):
        a = math.radians(turn + k * 60)
        d.line([(c, c), (c + 28 * PPU * math.cos(a), c + 28 * PPU * math.sin(a))], fill=(60, 62, 60, 255), width=3 * PPU)
    d.ellipse([c - 5 * PPU, c - 5 * PPU, c + 5 * PPU, c + 5 * PPU], fill=(40, 40, 40, 255))
    d.line([(c - 30 * PPU, 3 * PPU), (0, H)], fill=(90, 58, 30, 255), width=3 * PPU)                   # the belt going down
    masked(name, img)


def palm_erreur(name):
    """ERREUR Ø where her palm was, humid, black (l. 655): masked, on the stair wall."""
    W, H = 48 * PPU, 24 * PPU
    layer = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(layer)
    text_center(d, (2 * PPU, 2 * PPU, W - 2 * PPU, H - 2 * PPU), 'ERREUR Ø', font(int(H * 0.5), bold=False), 255)
    m = np.asarray(layer.filter(ImageFilter.GaussianBlur(2.2))).astype(float) / 255.0
    m = np.clip(m * (0.9 + 0.4 * fbm(H, W, 574, 1.2)), 0, 1)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (14, 12, 12)
    rgba[..., 3] = (m * 230).astype(np.uint8)
    masked(name, Image.fromarray(rgba))


def luna_bulbs(name, lit):
    """The name of the park in bulbs over the plaza (l. 691): LUNA PARK, unlit, or lit through cracked globes."""
    W, H = 128 * PPU, 32 * PPU
    img = sprite_rgba(W, H)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], fill=(40, 34, 30, 255), outline=(20, 18, 16, 255), width=PPU)
    layer = Image.new('L', (W, H), 0)
    ld = ImageDraw.Draw(layer)
    text_center(ld, (4 * PPU, 4 * PPU, W - 4 * PPU, H - 4 * PPU), 'LUNA  PARK', font(int(H * 0.6)), 255)
    m = np.asarray(layer)
    ys, xs = np.nonzero(m[::2 * PPU, ::2 * PPU])
    rng = np.random.default_rng(575)
    for (y, x) in zip(ys * 2 * PPU, xs * 2 * PPU):
        on = lit and rng.random() > 0.12
        col = (255, 226, 140, 255) if on else (96, 90, 78, 255)
        d.ellipse([x - PPU // 2 - 1, y - PPU // 2 - 1, x + PPU // 2 + 1, y + PPU // 2 + 1], fill=col)
    masked(name, img)


def draw_envelope():
    """The white envelope of Cochin, his name behind the window; the address now Waukegan, Illinois, 117 (l. 619)."""
    img = sprite_rgba(56, 36)
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, 54, 34], fill=(236, 232, 222, 255), outline=(170, 166, 156, 255))
    d.rectangle([8, 14, 40, 24], fill=(214, 220, 222, 255), outline=(150, 150, 150, 255))
    save_sprite(img, 'R5ENA0', yoff_extra=-18)


def draw_train():
    """PROVISIONAL stand-in for M05-09: a train of three cars, empty, seen from the side (billboard)."""
    img = sprite_rgba(300, 70)
    d = ImageDraw.Draw(img)
    for k in range(3):
        x = 6 + k * 98
        d.rounded_rectangle([x, 18, x + 90, 52], 8, fill=(150, 40, 34, 255), outline=(60, 20, 16, 255), width=2)
        d.rectangle([x + 8, 8, x + 82, 20], fill=(120, 30, 26, 255))
        d.ellipse([x + 10, 50, x + 26, 66], fill=(40, 40, 40, 255))
        d.ellipse([x + 64, 50, x + 80, 66], fill=(40, 40, 40, 255))
        d.line([(x + 90, 40), (x + 98, 40)], fill=(40, 40, 40, 255), width=3)
    save_sprite(img, 'R5TRA0')


# ----------------------------------------------------------------------------- main
def main():
    PATCH.mkdir(parents=True, exist_ok=True)
    # walls, facades, signs
    shed_wall('RF4_HANG', 461)
    shed_wall('RF4_ATEL', 462, rgb=(96, 84, 68))
    guard_hut('RF4_GUER', 467)
    hut_glass('RF4_VIT0', 468)
    hut_glass('RF4_VIT1', 468, erreur=True)
    time_clock('RF4_POIN')
    key_board('RF4_CLE5', ['ATELIER', 'PISTE', 'SOUS-STATION', 'CHAMBRE FROIDE', 'JERMA'])
    key_board('RF4_CLE4', ['ATELIER', 'PISTE', 'CHAMBRE FROIDE', 'JERMA'])
    brooklyn('RF4_BROO')
    cables('RF4_CABL', 526)
    basin_wall('RF4_BASS', 527)
    sign_board('RF4_NIAG', 'LES CHUTES DU NIAGARA', 128, 32, (40, 60, 90), (232, 222, 196), 528)
    sign_board('RF4_SING', 'PALAIS DES SINGES', 128, 24, (90, 40, 30), (232, 214, 170), 529)
    sign_board('RF4_DANS', 'SALLE DE DANSE', 128, 24, (40, 40, 44), (220, 190, 120), 530)
    fake_rock('RF4_ROCH', 531)
    trestle('RF4_BOIS', 551)
    turnstile_counter('RF4_C617', 617)
    turnstile_counter('RF4_C618', 618)
    turnstile_side('RF4_TOUR')
    mirror_pits('RF4_PIQU', 533)
    for i, kind in enumerate(('plonge', 'piste', 'acro', 'boxe')):
        poster(f'RF4_AFF{i + 1}', 455 + i, kind)
    iron_door('RF4_PSST', 552)
    attraction_facade('RF4_FAC1', 540, (150, 44, 36), (214, 202, 172))
    attraction_facade('RF4_FAC2', 541, (46, 70, 52), (190, 160, 90))
    attraction_facade('RF4_FAC3', 542, (180, 160, 110), (120, 40, 34))
    save('Texture', 'RF4_COLN', floor_grime(weather(solid(128 * PPU, 32 * PPU, (178, 168, 146)) * (0.9 + 0.2 * (fbm(128 * PPU, 32 * PPU, 534, 2.0)[..., None] - 0.5)), 535, 0.25), 0.3, 0.2))
    save('Texture', 'RF4_MARQ', canvas(64 * PPU, 64 * PPU, 536))
    save('Texture', 'RF4_BASC', floor_grime(stone_blocks(64 * PPU, 64 * PPU, 537, 16, 64, (150, 146, 136), (100, 98, 92)), 0.2, 0.3))
    # flats
    save('Flat', 'RF4_HERB', herbs(64 * PPU, 64 * PPU, 560))
    save('Flat', 'RF4_DECA', narrow_rails(64 * PPU, 64 * PPU, 561))
    save('Flat', 'RF4_DALH', slab_grass(64 * PPU, 64 * PPU, 562))
    save('Flat', 'RF4_PARQ', warped_parquet(64 * PPU, 64 * PPU, 563))
    save('Flat', 'RF4_BASF', basin_floor(64 * PPU, 64 * PPU, 564))
    save('Flat', 'RF4_FLAQ', black_puddle(64 * PPU, 64 * PPU, 565))
    save('Flat', 'RF4_MARF', canvas(64 * PPU, 64 * PPU, 566))
    save('Flat', 'RF4_VOIE', narrow_rails(64 * PPU, 64 * PPU, 567))
    # sprites
    draw_guard()
    draw_shoe()
    draw_jukebox()
    draw_substation_key()
    # RF05: the substation and the park lit again
    marble_panel('RF5_MARB', 580)
    dials('RF5_CAD0', 0)
    dials('RF5_CAD1', 1)
    for s in (0, 1, 2):
        node_box(f'RF5_NOD{s}', s)
    lever_panel('RF5_LEVM', 'marche')
    lever_panel('RF5_LEVA', 'arret')
    fuse_board('RF5_FUS0', False)
    fuse_board('RF5_FUS1', True)
    vault('RF5_VOUT', 581)
    stair_wall('RF5_ESCA', 582)
    motor_side('RF5_MOTR', 583)
    wheel('RF5_ROU0', 0)
    wheel('RF5_ROU1', 30)
    wheel('RF5_ROUS', 0)                                   # the wheel stopped (not animated)
    masked('RF5_BLNK', sprite_rgba(16 * PPU, 16 * PPU))    # a bare wall before her palm (fully transparent)
    palm_erreur('RF5_PAUM')
    luna_bulbs('RF5_LUN0', False)
    luna_bulbs('RF5_LUN1', True)
    draw_envelope()
    draw_train()
    lines = ['// Generated by scripts/mapkit/materials_rf04.py. RF04/RF05 material family (Luna Park, 14 June 1940).',
             '// PROVISIONAL (Opus, procedural) until Astra\'s LUNA-V01 files replace them under the same names.', '']
    for kind, name, w, h, ppu in DEFS:
        lines.append(f'{kind} {name}, {w}, {h}\n{{\n    XScale {ppu}\n    YScale {ppu}\n    Patch "patches/rf04/{name}.png", 0, 0\n}}')
    (ROOT / 'src' / 'TEXTURES.rf04').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    print(f'materials rf04: {len(DEFS)} definitions written to src/TEXTURES.rf04')


if __name__ == '__main__':
    main()
