#!/usr/bin/env python3
"""RF01 stand-in material family, item sprites, sky and menu graphics.

Everything is procedural (numpy/PIL) but calibrated on the legacy plaster and ceramic masters
so the level reads as one institution: painted plaster with dado, ceramic and checker floors,
limestone, painted wood and metal doors, iron grilles, enamel plaques. These are the textures used
until Codex Astra material batches are validated and promoted (scripts/promote_astra_batch.ps1).

Output (runtime):  src/patches/rf01/*.png, src/flats-less definitions in src/TEXTURES.rf01,
                   src/sprites/items/*.png, src/graphics/RFSELCT.png, src/textures/RFSKY.png
Usage: python scripts/mapkit/materials.py
"""
from pathlib import Path
import struct, zlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / 'src' / 'patches' / 'rf01'
SPRITES = ROOT / 'src' / 'sprites' / 'items'
GRAPHICS = ROOT / 'src' / 'graphics'
PPU = 4  # pixels per world unit

DEFS = []  # (kind, name, w, h, path)


# ----------------------------------------------------------------------------- helpers
def fbm(h, w, seed, beta=2.0):
    """Periodic 1/f^beta noise in [0,1]. Tileable by construction (spectral synthesis)."""
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1.0
    amp = 1.0 / f ** (beta / 2.0)
    amp[0, 0] = 0.0
    phase = np.exp(2j * np.pi * rng.random((h, w)))
    img = np.real(np.fft.ifft2(amp * phase))
    img -= img.min()
    return img / max(img.max(), 1e-9)


def grain(h, w, seed, amount=0.04):
    rng = np.random.default_rng(seed)
    return (rng.random((h, w)) - 0.5) * 2 * amount


def to_img(arr):
    return Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8), 'RGB')


def solid(h, w, rgb):
    return np.ones((h, w, 3)) * (np.array(rgb) / 255.0)


def tint(base, mask3, rgb, strength):
    """Blend base toward rgb where mask3 (h,w,1) is high."""
    col = np.array(rgb) / 255.0
    return base * (1 - mask3 * strength) + col * (mask3 * strength)


def save_patch(kind, name, arr_or_img, wunits=None, hunits=None, ppu=PPU):
    img = arr_or_img if isinstance(arr_or_img, Image.Image) else to_img(arr_or_img)
    PATCH.mkdir(parents=True, exist_ok=True)
    path = PATCH / f'{name}.png'
    img.save(path, optimize=True)
    w, h = img.size
    DEFS.append((kind, name, w, h, ppu))
    return img


def plaster(h, w, seed, rgb=(218, 210, 194), rough=0.10, stains=0.12):
    base = solid(h, w, rgb)
    n1 = fbm(h, w, seed, 2.6)[..., None]          # broad tonal drift
    n2 = fbm(h, w, seed + 7, 1.6)[..., None]      # fine trowel grain
    stain = fbm(h, w, seed + 13, 3.2)[..., None]
    img = base * (0.94 + 0.12 * (n1 - 0.5)) * (1 + rough * (n2 - 0.5))
    img = tint(img, np.clip((stain - 0.62) * 4, 0, 1), (140, 118, 92), stains)
    img += grain(h, w, seed + 3, 0.025)[..., None]
    # sparse chips
    rng = np.random.default_rng(seed + 99)
    for _ in range(int(h * w / 60000)):
        cy, cx = rng.integers(0, h), rng.integers(0, w)
        r = rng.integers(2, 6)
        yy, xx = np.ogrid[:h, :w]
        m = ((yy - cy) ** 2 + (xx - cx) ** 2) < r * r
        img[m] *= 0.72
    return np.clip(img, 0, 1)


def floor_grime(img, strength=0.35, height_frac=0.22):
    """Darken toward the floor (bottom rows) for wall textures."""
    h = img.shape[0]
    y = np.linspace(0, 1, h)[:, None, None]
    g = np.clip((y - (1 - height_frac)) / height_frac, 0, 1) ** 1.6
    return img * (1 - strength * g)


def dado_wall(name, dado_rgb, seed, plaster_rgb=(218, 210, 194), dado_units=44, molding=True):
    """256x256 unit wall: plaster above, painted dado below, thin molding between."""
    H = W = 256 * PPU
    img = plaster(H, W, seed, plaster_rgb)
    dh = dado_units * PPU
    # dado paint: flatter, glossier, scuffed
    dado = solid(dh, W, dado_rgb)
    n = fbm(dh, W, seed + 21, 2.2)[..., None]
    scuff = fbm(dh, W, seed + 31, 1.4)[..., None]
    dado = dado * (0.92 + 0.16 * (n - 0.5))
    dado = tint(dado, np.clip((scuff - 0.68) * 5, 0, 1), (200, 190, 170), 0.35)
    dado += grain(dh, W, seed + 5, 0.03)[..., None]
    img[H - dh:] = np.clip(dado, 0, 1)
    if molding:
        my = H - dh - 5 * PPU
        img[my:my + 2 * PPU] = np.array((190, 184, 172)) / 255.0
        img[my + 2 * PPU:my + 4 * PPU] = np.array((150, 144, 132)) / 255.0
        img[my + 4 * PPU:my + 5 * PPU] = np.array((100, 96, 88)) / 255.0
    img = floor_grime(img, 0.3, 0.12)
    save_patch('Texture', name, img)


def tile_wall(name, seed, tile_units=48):
    """256 unit wall: white ceramic tiles up to tile_units, plaster above (laundry / consultations)."""
    H = W = 256 * PPU
    img = plaster(H, W, seed, (214, 208, 194))
    th = tile_units * PPU
    tiles = ceramic(th, W, seed + 40, size_units=16, rgb=(226, 224, 214), grout=(150, 148, 140))
    img[H - th:] = tiles
    my = H - th - 3 * PPU
    img[my:my + 3 * PPU] = np.array((170, 166, 156)) / 255.0
    img = floor_grime(img, 0.25, 0.1)
    save_patch('Texture', name, img)


def ceramic(h, w, seed, size_units=32, rgb=(206, 200, 188), grout=(120, 116, 108), bevel=True):
    size = size_units * PPU
    img = solid(h, w, rgb)
    n = fbm(h, w, seed, 2.0)[..., None]
    img = img * (0.9 + 0.2 * (n - 0.5))
    # per-tile tonal variation
    rng = np.random.default_rng(seed)
    ty, tx = np.mgrid[:h, :w]
    tile_id = (ty // size) * 977 + (tx // size)
    var = (rng.random(int(tile_id.max()) + 1) - 0.5) * 0.12
    img = img * (1 + var[tile_id][..., None])
    gy = (ty % size) < 2 * PPU // 2 + 2
    gx = (tx % size) < 2 * PPU // 2 + 2
    g = (gy | gx)[..., None]
    img = img * (1 - g) + (np.array(grout) / 255.0) * g
    if bevel:
        by = ((ty % size) >= size - 3) | ((ty % size) < 6)
        bx = ((tx % size) >= size - 3) | ((tx % size) < 6)
        b = ((by | bx) & ~(gy | gx))[..., None]
        img = img * (1 - 0.12 * b)
    img += grain(h, w, seed + 1, 0.02)[..., None]
    return np.clip(img, 0, 1)


def checker(h, w, seed, size_units=32, a=(212, 202, 178), b=(56, 50, 46)):
    size = size_units * PPU
    ty, tx = np.mgrid[:h, :w]
    chk = (((ty // size) + (tx // size)) % 2)[..., None]
    img = solid(h, w, a) * (1 - chk) + solid(h, w, b) * chk
    n = fbm(h, w, seed, 2.0)[..., None]
    img = img * (0.9 + 0.2 * (n - 0.5))
    g = (((ty % size) < 3) | ((tx % size) < 3))[..., None]
    img = img * (1 - 0.5 * g)
    img += grain(h, w, seed + 1, 0.02)[..., None]
    return np.clip(img, 0, 1)


def planks(h, w, seed, plank_units=16, rgb=(122, 84, 50)):
    pw = plank_units * PPU
    img = solid(h, w, rgb)
    ty, tx = np.mgrid[:h, :w]
    rng = np.random.default_rng(seed)
    row = ty // pw
    var = (rng.random(int(row.max()) + 1) - 0.5) * 0.28
    img = img * (1 + var[row][..., None])
    # wood grain: stretched noise along x
    g = fbm(h, w, seed + 3, 1.2)
    g = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, max(1, h // 6))).resize((w, h), Image.BILINEAR)) / 255.0
    img = img * (0.85 + 0.3 * (g[..., None] - 0.5))
    seam = ((ty % pw) < 2)[..., None]
    img = img * (1 - 0.55 * seam)
    # staggered plank ends
    ends = (((tx + (row * 173) % w) % (pw * 8)) < 2)[..., None]
    img = img * (1 - 0.45 * ends)
    img += grain(h, w, seed + 1, 0.03)[..., None]
    return np.clip(img, 0, 1)


def stone_blocks(h, w, seed, bh_units=32, bw_units=64, rgb=(190, 180, 162), mortar=(120, 112, 100)):
    bh, bw = bh_units * PPU, bw_units * PPU
    img = solid(h, w, rgb)
    ty, tx = np.mgrid[:h, :w]
    row = ty // bh
    shift = (row % 2) * (bw // 2)
    col = (tx + shift) // bw
    rng = np.random.default_rng(seed)
    bid = row * 1009 + col
    var = (rng.random(int(bid.max()) + 1) - 0.5) * 0.16
    img = img * (1 + var[bid][..., None])
    n = fbm(h, w, seed + 2, 1.8)[..., None]
    img = img * (0.88 + 0.24 * (n - 0.5))
    m = (((ty % bh) < 3) | (((tx + shift) % bw) < 3))[..., None]
    img = img * (1 - m) + (np.array(mortar) / 255.0) * m
    img += grain(h, w, seed + 1, 0.03)[..., None]
    return np.clip(img, 0, 1)


def gravel(h, w, seed, rgb=(146, 136, 116)):
    img = solid(h, w, rgb)
    n1 = fbm(h, w, seed, 1.2)[..., None]
    n2 = fbm(h, w, seed + 5, 2.6)[..., None]
    img = img * (0.75 + 0.5 * (n1 - 0.5)) * (0.9 + 0.3 * (n2 - 0.5))
    img = tint(img, np.clip((n2 - 0.6) * 4, 0, 1), (96, 104, 70), 0.35)  # moss/damp
    img += grain(h, w, seed + 1, 0.05)[..., None]
    return np.clip(img, 0, 1)


def door_texture(name, wunits, hunits, seed, paint=(88, 98, 82), leaves=2, panels=2, metal=False):
    W, H = wunits * PPU, hunits * PPU
    img = solid(H, W, paint)
    n = fbm(H, W, seed, 2.0)[..., None]
    img = img * (0.92 + 0.16 * (n - 0.5))
    pil = to_img(img)
    d = ImageDraw.Draw(pil)
    dark = tuple(int(c * 0.55) for c in paint)
    light = tuple(min(255, int(c * 1.25)) for c in paint)
    frame = 6 * PPU
    lw = W // leaves
    for L in range(leaves):
        x0 = L * lw
        # leaf border
        d.rectangle([x0 + 1, 0, x0 + lw - 2, H - 1], outline=dark, width=2)
        # panels
        px0, px1 = x0 + frame + 2 * PPU, x0 + lw - frame - 2 * PPU
        top, bottom = 10 * PPU, H - 12 * PPU
        ph = (bottom - top) // panels
        for p in range(panels):
            py0 = top + p * ph + 3 * PPU
            py1 = top + (p + 1) * ph - 3 * PPU
            if not metal:
                d.rectangle([px0, py0, px1, py1], outline=dark, width=3)
                d.rectangle([px0 + 3, py0 + 3, px1 - 3, py1 - 3], outline=light, width=2)
                d.rectangle([px0 + 8, py0 + 8, px1 - 8, py1 - 8], fill=tuple(int(c * 0.9) for c in paint))
            else:
                d.rectangle([px0, py0, px1, py1], outline=dark, width=4)
        # handle at 40 units from the floor
        hy = H - 40 * PPU
        hx = x0 + lw - frame - 6 * PPU if L == 0 else x0 + frame + 6 * PPU
        d.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=(190, 160, 90) if not metal else (70, 70, 72))
        d.rectangle([hx - 3, hy - 14, hx + 3, hy + 14], fill=(160, 134, 76) if not metal else (60, 60, 62))
    if metal:
        # rivets along the frame
        for y in range(8 * PPU, H, 24 * PPU):
            for x in (5 * PPU, W - 5 * PPU):
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=dark)
    arr = np.asarray(pil).astype(float) / 255.0
    arr = floor_grime(arr, 0.35, 0.18)
    arr += grain(H, W, seed + 1, 0.025)[..., None]
    save_patch('Texture', name, np.clip(arr, 0, 1))


def grille_texture(name, wunits, hunits, seed):
    W, H = wunits * PPU, hunits * PPU
    img = solid(H, W, (34, 34, 36))
    n = fbm(H, W, seed, 2.4)[..., None]
    img = img * (0.8 + 0.5 * (n - 0.5))
    pil = to_img(img)
    d = ImageDraw.Draw(pil)
    bar = (92, 90, 86)
    for x in range(6 * PPU, W, 16 * PPU):
        d.rectangle([x, 0, x + 3 * PPU, H], fill=bar)
        d.rectangle([x, 0, x + PPU, H], fill=(130, 128, 122))
    for y in (8 * PPU, H // 2, H - 10 * PPU):
        d.rectangle([0, y, W, y + 4 * PPU], fill=(80, 78, 74))
        d.rectangle([0, y, W, y + PPU], fill=(120, 118, 112))
    save_patch('Texture', name, pil)


def window_texture(name, wunits, hunits, seed):
    """Masked window: painted frame, mullions, glass mostly transparent with grime."""
    W, H = wunits * PPU, hunits * PPU
    rng = np.random.default_rng(seed)
    rgba = np.zeros((H, W, 4))
    glass = fbm(H, W, seed, 2.2)
    rgba[..., 0] = 0.55 + 0.2 * glass
    rgba[..., 1] = 0.6 + 0.2 * glass
    rgba[..., 2] = 0.62 + 0.2 * glass
    rgba[..., 3] = 0.18 + 0.35 * np.clip((glass - 0.5) * 2, 0, 1)
    pil = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(pil)
    frame = (206, 200, 186)
    dark = (120, 114, 104)
    fw = 4 * PPU
    d.rectangle([0, 0, W - 1, H - 1], outline=frame, width=fw)
    d.rectangle([0, 0, W - 1, H - 1], outline=dark, width=PPU)
    d.rectangle([W // 2 - fw // 2, 0, W // 2 + fw // 2, H], fill=frame)
    for k in range(1, 3):
        y = k * H // 3
        d.rectangle([0, y - fw // 2, W, y + fw // 2], fill=frame)
    d.rectangle([0, H - 6 * PPU, W, H - 1], fill=(170, 164, 150))  # sill
    pil.save(PATCH / f'{name}.png')
    DEFS.append(('Texture', name, W, H))


def switch_textures(seed):
    for state in (0, 1):
        W = H = 64 * PPU
        img = solid(H, W, (96, 92, 84))
        n = fbm(H, W, seed + state, 2.0)[..., None]
        img = img * (0.9 + 0.2 * (n - 0.5))
        pil = to_img(img)
        d = ImageDraw.Draw(pil)
        d.rectangle([8 * PPU, 8 * PPU, W - 8 * PPU, H - 8 * PPU], fill=(60, 58, 54), outline=(30, 30, 30), width=4)
        cx, cy = W // 2, H // 2
        d.ellipse([cx - 12 * PPU, cy - 12 * PPU, cx + 12 * PPU, cy + 12 * PPU], fill=(120, 116, 108), outline=(40, 40, 40), width=3)
        ang = -50 if state == 0 else 50
        ex = cx + int(22 * PPU * math.sin(math.radians(ang)))
        ey = cy - int(22 * PPU * math.cos(math.radians(ang)))
        d.line([cx, cy, ex, ey], fill=(30, 30, 30), width=5 * PPU)
        d.line([cx, cy, ex, ey], fill=(150, 40, 40) if state else (150, 146, 138), width=3 * PPU)
        d.ellipse([ex - 4 * PPU, ey - 4 * PPU, ex + 4 * PPU, ey + 4 * PPU], fill=(40, 40, 40))
        save_patch('Texture', f'RFM_SW{state}', pil)


def sign(name, text, seed, wunits=64, hunits=16, bg=(30, 62, 118), fg=(236, 236, 230)):
    W, H = wunits * PPU, hunits * PPU
    pil = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, W - 1, H - 1], outline=fg, width=PPU)
    d.rectangle([PPU, PPU, W - PPU - 1, H - PPU - 1], outline=bg, width=PPU)
    font = None
    size = int(H * 0.5)
    while font is None or (size > 8 and d.textbbox((0, 0), text, font=font)[2] - d.textbbox((0, 0), text, font=font)[0] > W - 6 * PPU):
        font = None
        for f in ('C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/arial.ttf', 'DejaVuSans-Bold.ttf'):
            try:
                font = ImageFont.truetype(f, size)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()
            break
        size -= 1                                   # the text stays inside the enamel border (3 units each side)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((W - tw) / 2 - bbox[0], (H - th) / 2 - bbox[1]), text, font=font, fill=fg)
    arr = np.asarray(pil).astype(float) / 255.0
    n = fbm(H, W, seed, 2.2)[..., None]
    arr = arr * (0.9 + 0.2 * (n - 0.5))
    save_patch('Texture', name, np.clip(arr, 0, 1))


def sky():
    W, H = 1024, 256
    y = np.linspace(0, 1, H)[:, None]
    top = np.array((132, 142, 156)) / 255.0
    bottom = np.array((196, 198, 196)) / 255.0
    img = top * (1 - y)[..., None] + bottom * y[..., None]
    clouds = fbm(H, W, 4242, 2.4)
    detail = fbm(H, W, 4343, 1.6)
    c = np.clip((clouds - 0.45) * 2.2 + (detail - 0.5) * 0.4, 0, 1)[..., None]
    img = img * (1 - c * 0.35) + np.array((222, 220, 214)) / 255.0 * c * 0.35
    img = np.clip(img, 0, 1)
    (ROOT / 'src' / 'textures').mkdir(parents=True, exist_ok=True)
    to_img(img).save(ROOT / 'src' / 'textures' / 'RFSKY.png')


# ----------------------------------------------------------------------------- street (RF01 porch/exit)
def _draw_window(d, x0, y0, w, h, ppu, rng, shutters):
    """Tall French window seen from the street: stone surround, frame, dark glass, iron rail."""
    s = ppu
    d.rectangle([x0 - 3 * s, y0 - 4 * s, x0 + w + 3 * s, y0 + h + 3 * s], fill=(184, 172, 150))       # stone surround
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(48, 50, 54))                                           # glass
    for k in range(3):
        gy = y0 + int(h * (0.1 + 0.28 * k))
        d.line([(x0 + 2 * s, gy), (x0 + w - 2 * s, gy + 5 * s)], fill=(74, 78, 86), width=max(1, s))  # sky reflection
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=(206, 198, 180), width=max(1, s))                   # frame
    d.line([(x0 + w // 2, y0), (x0 + w // 2, y0 + h)], fill=(206, 198, 180), width=max(1, s))
    d.line([(x0, y0 + h // 3), (x0 + w, y0 + h // 3)], fill=(206, 198, 180), width=max(1, s))
    if shutters == 'closed':
        col = (96, 112, 118) if rng.random() < 0.6 else (112, 104, 92)
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=col)
        for yy in range(y0 + 2 * s, y0 + h, 3 * s):                                                   # persienne slats
            d.line([(x0 + s, yy), (x0 + w - s, yy)], fill=tuple(int(c * 0.72) for c in col), width=max(1, s // 2))
        d.line([(x0 + w // 2, y0), (x0 + w // 2, y0 + h)], fill=tuple(int(c * 0.6) for c in col), width=max(1, s))
    elif shutters == 'open':
        col = (96, 112, 118)
        for sx in (x0 - w // 2 - 3 * s, x0 + w + 3 * s):
            d.rectangle([sx, y0, sx + w // 2, y0 + h], fill=col)
            for yy in range(y0 + 2 * s, y0 + h, 3 * s):
                d.line([(sx + s, yy), (sx + w // 2 - s, yy)], fill=(70, 82, 88), width=max(1, s // 2))
    ry = y0 + h - 12 * s                                                                               # iron rail
    d.line([(x0 - 2 * s, ry), (x0 + w + 2 * s, ry)], fill=(30, 30, 32), width=max(1, s))
    for bx in range(x0, x0 + w + 1, 3 * s):
        d.line([(bx, ry), (bx, y0 + h)], fill=(34, 34, 36), width=max(1, s // 2))


def facade_paris(name, seed, wunits=256, hunits=448, ppu=2):
    """Parisian street facade, 1940: shop fronts shut for the exodus, four floors, zinc roof."""
    W, H = wunits * ppu, hunits * ppu
    rng = np.random.default_rng(seed)
    img = plaster(H, W, seed, (196, 186, 166), 0.12, 0.2)
    soot = fbm(H, W, seed + 4, 2.4)[..., None]
    yv = np.linspace(0, 1, H)[:, None, None]
    img = img * (1 - 0.18 * np.clip(1 - yv * 1.6, 0, 1) * soot)                                       # soot toward the top
    pil = to_img(img)
    d = ImageDraw.Draw(pil)

    def Y(u):                                                                                          # units above the pavement
        return H - int(u * ppu)
    d.rectangle([0, Y(8), W, H], fill=(96, 94, 90))                                                   # stone plinth
    # ground floor: two shop fronts per texture width, shutters down; an entrance door beside each
    bay = W // 2
    for b in range(2):
        x0 = b * bay + 10 * ppu
        x1 = x0 + bay - 44 * ppu
        paint = [(58, 74, 62), (92, 40, 36), (46, 52, 66)][int(rng.integers(0, 3))]
        d.rectangle([x0, Y(100), x1, Y(8)], fill=paint)                                                # wooden shopfront
        d.rectangle([x0 + 4 * ppu, Y(92), x1 - 4 * ppu, Y(12)], fill=(122, 124, 122))                 # roller shutter
        for yy in range(Y(92), Y(12), 3 * ppu):
            d.line([(x0 + 4 * ppu, yy), (x1 - 4 * ppu, yy)], fill=(92, 94, 94), width=max(1, ppu // 2))
        d.rectangle([x0 + 4 * ppu, Y(100), x1 - 4 * ppu, Y(94)], fill=tuple(min(255, int(c * 1.25)) for c in paint))  # blank fascia
        dx = x1 + 8 * ppu
        d.rectangle([dx, Y(92), dx + 24 * ppu, Y(8)], fill=(70, 54, 40))                               # entrance door
        d.rectangle([dx + 3 * ppu, Y(86), dx + 21 * ppu, Y(50)], outline=(52, 40, 30), width=ppu)
        d.rectangle([dx + 3 * ppu, Y(44), dx + 21 * ppu, Y(14)], outline=(52, 40, 30), width=ppu)
    d.rectangle([0, Y(112), W, Y(104)], fill=(176, 166, 146))                                          # stone band
    d.line([(0, Y(112)), (W, Y(112))], fill=(120, 112, 98), width=ppu)
    # four upper floors of French windows; many shutters closed (the city emptied on 13-14 June)
    for f in range(4):
        base = 124 + f * 70
        d.line([(0, Y(base - 4)), (W, Y(base - 4))], fill=(168, 158, 138), width=2 * ppu)             # floor band
        for k in range(4):
            wx = int((k + 0.5) * W / 4) - 13 * ppu
            state = 'closed' if rng.random() < 0.55 else ('open' if rng.random() < 0.5 else 'none')
            _draw_window(d, wx, Y(base + 52), 26 * ppu, 50 * ppu, ppu, rng, state)
    d.rectangle([0, Y(410), W, Y(402)], fill=(150, 142, 126))                                          # cornice
    d.line([(0, Y(402)), (W, Y(402))], fill=(80, 76, 70), width=2 * ppu)
    d.rectangle([0, 0, W, Y(410)], fill=(112, 120, 128))                                               # zinc roof
    for k in range(4):
        cx = int((k + 0.5) * W / 4)
        d.rectangle([cx - 9 * ppu, Y(440), cx + 9 * ppu, Y(412)], fill=(126, 132, 138))              # dormer
        d.rectangle([cx - 5 * ppu, Y(436), cx + 5 * ppu, Y(416)], fill=(44, 46, 50))
    arr = np.asarray(pil).astype(float) / 255.0
    arr = floor_grime(arr, 0.28, 0.06)
    save_patch('Texture', name, arr, ppu=ppu)


def facade_hospital(name, seed, wunits=256, hunits=320, ppu=2):
    """Hospital pavilion behind the enclosure wall: plain render, tall regular windows."""
    W, H = wunits * ppu, hunits * ppu
    rng = np.random.default_rng(seed)
    img = plaster(H, W, seed, (206, 198, 180), 0.1, 0.18)
    pil = to_img(img)
    d = ImageDraw.Draw(pil)

    def Y(u):
        return H - int(u * ppu)
    for f in range(3):
        base = 36 + f * 96
        d.line([(0, Y(base - 8)), (W, Y(base - 8))], fill=(176, 168, 150), width=2 * ppu)
        for k in range(3):
            wx = int((k + 0.5) * W / 3) - 15 * ppu
            _draw_window(d, wx, Y(base + 64), 30 * ppu, 62 * ppu, ppu, rng, 'none' if f else 'closed')
    arr = np.asarray(pil).astype(float) / 255.0
    save_patch('Texture', name, arr, ppu=ppu)


def cobbles(h, w, seed, bw_units=8, bh_units=12):
    """Sandstone setts in running rows, dark joints, worn highlights."""
    img = solid(h, w, (112, 108, 102))
    ty, tx = np.mgrid[:h, :w]
    bh, bw = bh_units * PPU, bw_units * PPU
    row = ty // bh
    shift = (row % 2) * (bw // 2)
    col = (tx + shift) // bw
    rng = np.random.default_rng(seed)
    bid = row * 4099 + col
    var = (rng.random(int(bid.max()) + 1) - 0.5) * 0.3
    img = img * (1 + var[bid][..., None])
    ly, lx = (ty % bh) / bh, ((tx + shift) % bw) / bw
    dome = (1 - (2 * ly - 1) ** 2) * (1 - (2 * lx - 1) ** 2)
    img = img * (0.78 + 0.3 * dome[..., None])
    joint = ((ty % bh) < PPU) | (((tx + shift) % bw) < PPU)
    img[joint] = np.array((54, 52, 48)) / 255.0
    img = img * (0.9 + 0.2 * (fbm(h, w, seed + 3, 2.0)[..., None] - 0.5))
    img += grain(h, w, seed + 1, 0.035)[..., None]
    return np.clip(img, 0, 1)


# ----------------------------------------------------------------------------- furniture sides
# Raised-block furniture keeps its geometry (safe collision); these side textures make the blocks
# read as beds, tables, shelving and vats. Lower textures are top-aligned on the block's top edge.
def _px(u):
    return int(round(u * PPU))


def bed_side(name, seed):
    """Hospital bed side, 64x32 u: mattress edge, grey wool blanket overhang, shadow, iron rail."""
    W, H = 64 * PPU, 32 * PPU
    img = solid(H, W, (22, 20, 20))
    n = fbm(H, W, seed, 2.0)[..., None]
    blanket = solid(_px(9), W, (104, 108, 96)) * (0.9 + 0.2 * (fbm(_px(9), W, seed + 1, 1.4)[..., None] - 0.5))
    ty, tx = np.mgrid[:_px(9), :W]
    folds = 0.08 * np.sin(tx / W * 2 * math.pi * 5 + np.sin(tx / 37.0)) * (ty / _px(9))
    blanket = blanket * (1 + folds[..., None])
    img[_px(3):_px(12)] = blanket
    img[:_px(3)] = np.array((206, 204, 196)) / 255.0 * (0.95 + 0.1 * n[:_px(3)])          # sheet/mattress edge
    img[_px(12):_px(13)] *= 0.5                                                              # hem shadow
    img[_px(17):_px(19)] = np.array((64, 66, 68)) / 255.0                                    # iron side rail
    for lx in (_px(2), W - _px(4)):                                                           # legs
        img[_px(13):, lx:lx + _px(2)] = np.array((58, 60, 62)) / 255.0
    img = img * (1 - 0.35 * (np.linspace(0, 1, H)[:, None, None] ** 2))                      # darker toward the floor
    save_patch('Texture', name, np.clip(img + grain(H, W, seed + 2, 0.02)[..., None], 0, 1))


def bed_head(name, seed):
    """Painted iron headboard, 64x48 u: cream enamel panel in a tube frame, chipped edges."""
    W, H = 64 * PPU, 48 * PPU
    img = solid(H, W, (196, 192, 176)) * (0.93 + 0.1 * (fbm(H, W, seed, 2.2)[..., None] - 0.5))
    pil = to_img(img)
    d = ImageDraw.Draw(pil)
    tube = (150, 148, 138)
    d.rectangle([0, 0, W - 1, _px(3)], fill=tube)
    d.rectangle([0, 0, _px(2), H], fill=tube)
    d.rectangle([W - _px(2), 0, W, H], fill=tube)
    d.rectangle([0, _px(30), W, _px(32)], fill=tube)
    for x in range(_px(8), W - _px(4), _px(8)):
        d.rectangle([x, _px(32), x + _px(1), H], fill=(120, 118, 110))                     # lower bars
    rng = np.random.default_rng(seed)
    for _ in range(12):                                                                      # enamel chips
        cx, cy = int(rng.integers(0, W)), int(rng.integers(0, H))
        r = int(rng.integers(1, 3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(122, 114, 102))
    save_patch('Texture', name, pil)


def table_side(name, seed, wood=(92, 64, 40)):
    """Table seen from the side, 64x32 u: top edge, apron, dark gap underneath, legs at both ends."""
    W, H = 64 * PPU, 32 * PPU
    img = solid(H, W, (16, 14, 13))
    grainw = planks(_px(8), W, seed, 8, wood)
    img[:_px(3)] = grainw[:_px(3)] * 1.15                                                     # top edge
    img[_px(3):_px(8)] = grainw[_px(3):_px(8)] * 0.8                                          # apron
    for lx in (0, W - _px(3)):
        img[_px(8):, lx:lx + _px(3)] = planks(H - _px(8), _px(3), seed + 1, 8, wood) * 0.85   # legs
    img[_px(8):_px(9)] *= 0.4
    save_patch('Texture', name, np.clip(img, 0, 1))


def shelf_front(name, seed):
    """Archive shelving, 64x64 u: dark wooden uprights and boards, rows of bound registers."""
    W, H = 64 * PPU, 64 * PPU
    rng = np.random.default_rng(seed)
    img = solid(H, W, (28, 22, 18))
    wood = planks(H, W, seed + 1, 8, (84, 58, 36))
    for y0 in range(0, H, _px(16)):                                                           # boards
        img[y0:y0 + _px(2)] = wood[y0:y0 + _px(2)]
    img[:, :_px(2)] = wood[:, :_px(2)]
    img[:, W - _px(2):] = wood[:, W - _px(2):]
    spines = [(96, 34, 32), (58, 44, 34), (30, 30, 34), (44, 58, 44), (110, 86, 60), (70, 28, 30)]
    for y0 in range(0, H, _px(16)):
        x = _px(2)
        base = y0 + _px(16)
        while x < W - _px(3):
            w = int(rng.integers(_px(2), _px(4)))
            h = int(rng.integers(_px(10), _px(13)))
            col = np.array(spines[int(rng.integers(0, len(spines)))]) / 255.0
            shade = 0.8 + 0.4 * rng.random()
            img[base - h:base, x:x + w - 1] = col * shade
            img[base - h + _px(2):base - h + _px(4), x + 1:x + w - 2] = np.array((168, 156, 128)) / 255.0 * shade  # label patch
            x += w
    img += grain(H, W, seed + 2, 0.02)[..., None]
    save_patch('Texture', name, np.clip(img, 0, 1))


def vat_side(name, seed):
    """Galvanised laundry vat, 64x48 u: mottled zinc, rolled rim, riveted bands."""
    W, H = 64 * PPU, 48 * PPU
    img = solid(H, W, (132, 136, 136))
    img = img * (0.82 + 0.3 * (fbm(H, W, seed, 1.8)[..., None] - 0.5))
    img = tint(img, np.clip((fbm(H, W, seed + 3, 2.6)[..., None] - 0.6) * 4, 0, 1), (96, 92, 80), 0.4)   # water stains
    img[:_px(3)] = np.array((176, 178, 176)) / 255.0                                          # rolled rim
    img[_px(3):_px(4)] *= 0.55
    for yb in (_px(8), H - _px(6)):
        img[yb:yb + _px(2)] = np.array((104, 106, 106)) / 255.0                               # bands
        for x in range(_px(3), W, _px(6)):
            img[yb + _px(0.5):yb + _px(1.5), x:x + _px(1)] = np.array((70, 72, 72)) / 255.0   # rivets
    img = floor_grime(img, 0.35, 0.2)
    save_patch('Texture', name, np.clip(img + grain(H, W, seed + 1, 0.02)[..., None], 0, 1))


# ----------------------------------------------------------------------------- chapel glass
def stained_glass(name, seed, wunits=64, hunits=64):
    """Chapel window: geometric quarries of coloured glass in lead cames under a pointed arch, no
    figures or text. A brightmap (GLDEFS) keeps the panes luminous against the dark nave."""
    W, H = wunits * PPU, hunits * PPU
    rng = np.random.default_rng(seed)
    pil = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pil)
    colours = [(38, 64, 150), (150, 30, 40), (196, 150, 54), (46, 110, 70), (222, 210, 150), (90, 50, 120)]
    cell = 8 * PPU
    step = cell * 0.62                                                 # rows at the vertical half-diagonal:
    for gy in range(-1, int(H / step) + 2):                            # the diamonds tessellate
        for gx in range(-1, W // cell + 2):
            cx = gx * cell + (cell // 2 if gy % 2 else 0)
            cy = gy * step
            poly = [(cx, cy - step), (cx + cell * 0.5, cy), (cx, cy + step), (cx - cell * 0.5, cy)]
            base = colours[int(rng.integers(0, len(colours)))]
            if abs(cx - W / 2) < cell * 0.8:
                base = colours[1 if gy % 3 else 2]                     # central ruby and amber column
            shade = 0.8 + 0.35 * rng.random()
            d.polygon(poly, fill=tuple(int(min(255, c * shade)) for c in base) + (255,), outline=(20, 18, 16, 255))
    lead = (22, 20, 18, 255)
    d.rectangle([0, 0, W - 1, H - 1], outline=lead, width=2 * PPU)    # frame
    d.line([(W // 2, 0), (W // 2, H)], fill=lead, width=PPU)           # mullion
    for y in (H // 3, 2 * H // 3):                                     # saddle bars
        d.line([(0, y), (W, y)], fill=lead, width=PPU)
    arr = np.asarray(pil).astype(float)
    arr[..., :3] = np.clip(arr[..., :3] * (0.85 + 0.3 * fbm(H, W, seed + 1, 1.6)[..., None]), 0, 255)
    # pointed head: each half is an arc centred on the springing line, meeting at the apex
    ys = H * 0.35
    c = (W * W / 4 + ys * ys) / W                                      # arc centre offset (and radius)
    yy, xx = np.mgrid[0:H, 0:W]
    inside_left = (xx - c) ** 2 + (yy - ys) ** 2 <= c * c
    inside_right = (xx - (W - 1 - c)) ** 2 + (yy - ys) ** 2 <= c * c
    keep = np.where(xx <= W / 2, inside_left, inside_right)
    arr[(yy < ys) & ~keep] = (0, 0, 0, 0)
    img = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    img.save(PATCH / f'{name}.png')
    DEFS.append(('Texture', name, W, H, PPU))
    bm = Image.new('RGB', (W, H), (0, 0, 0))
    bm.paste(Image.new('RGB', (W, H), (200, 200, 200)), (0, 0), img.split()[3])
    bm.save(PATCH / f'{name}_BM.png')


# ----------------------------------------------------------------------------- wear decals
DECALS = ROOT / 'src' / 'graphics' / 'decals'


def _mask_png(mask, name):
    """Grey mask saved as white RGBA with alpha = mask: DECALDEF 'shade' tints it."""
    a = (np.clip(mask, 0, 1) * 255).astype(np.uint8)
    rgba = np.dstack([a, a, a, a])
    DECALS.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, 'RGBA').save(DECALS / f'{name}.png', optimize=True)


def wear_decals():
    """Situated wear (ASSET_BIBLE): damp tide marks, hand grime by doors, rust/water streaks,
    trolley scuffs. Masks only; colour and strength come from DECALDEF."""
    S = 128
    yy, xx = np.mgrid[0:S, 0:S] / (S - 1.0)
    # damp patch: irregular blob, darker tide rim, rising from the floor (bottom edge)
    n = fbm(S, S, 501, 2.2)
    r = np.hypot((xx - 0.5) * 1.1, (yy - 0.8) * 0.9) + (n - 0.5) * 0.35
    blob = np.clip((0.55 - r) * 5, 0, 1)
    rim = np.exp(-((r - 0.52) / 0.035) ** 2) * 0.6
    _mask_png(np.clip(blob * 0.45 + rim, 0, 0.8) * np.clip((0.97 - yy) * 30, 0, 1), 'RFDSTN1')
    # hand grime: soft vertical smudge where hands push a door frame
    n = fbm(S, S, 502, 1.8)
    g = np.exp(-((xx - 0.5) / 0.16) ** 2 - ((yy - 0.5) / 0.3) ** 2) * (0.6 + 0.6 * n)
    _mask_png(np.clip(g, 0, 0.7), 'RFDSTN2')
    # streaks: drips from a ledge (top edge) fading downward
    rng = np.random.default_rng(503)
    st = np.zeros((S, S))
    for _ in range(9):
        x0 = rng.uniform(0.15, 0.85)
        w = rng.uniform(0.01, 0.035)
        length = rng.uniform(0.4, 0.95)
        st += np.exp(-((xx - x0) / w) ** 2) * np.clip(1 - yy / length, 0, 1) ** 1.5 * rng.uniform(0.4, 0.9)
    st += np.exp(-((yy - 0.02) / 0.04) ** 2) * 0.5
    _mask_png(np.clip(st, 0, 0.85), 'RFDSTN3')
    # scuffs: horizontal rubs at trolley height
    sc = np.zeros((S, S))
    for _ in range(14):
        y0 = rng.uniform(0.35, 0.65)
        x0, x1 = sorted(rng.uniform(0.0, 1.0, 2))
        sc += np.exp(-((yy - y0) / 0.012) ** 2) * ((xx > x0) & (xx < x1)) * rng.uniform(0.3, 0.8)
    _mask_png(np.clip(sc * (0.7 + 0.5 * fbm(S, S, 504, 1.5)), 0, 0.75), 'RFDSTN4')
    (ROOT / 'src' / 'DECALDEF').write_text(
        '// Situated wear decals (scripts/mapkit/materials.py). Placed by Decal things (9200) in the\n'
        '// map scripts, facing the wall they mark. Shade decals: the mask carries the shape only.\n\n'
        'decal RFDamp 11001\n{\n    pic RFDSTN1\n    shade "30 28 1e"\n    x-scale 0.6\n    y-scale 0.6\n    randomflipx\n}\n\n'
        'decal RFGrime 11002\n{\n    pic RFDSTN2\n    shade "22 1c 16"\n    x-scale 0.25\n    y-scale 0.3\n    randomflipx\n}\n\n'
        'decal RFStreak 11003\n{\n    pic RFDSTN3\n    shade "4a 32 1e"\n    x-scale 0.45\n    y-scale 0.6\n    randomflipx\n}\n\n'
        'decal RFScuff 11004\n{\n    pic RFDSTN4\n    shade "1e 1a 16"\n    x-scale 0.6\n    y-scale 0.25\n    randomflipx\n}\n',
        encoding='utf-8')


# ----------------------------------------------------------------------------- sprites
def png_with_grab(img, xoff, yoff, path):
    """Save RGBA PNG and insert a grAb chunk (sprite offsets) after IHDR."""
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, 'PNG')
    data = buf.getvalue()
    sig, rest = data[:8], data[8:]
    # first chunk is IHDR: length(4) type(4) data(13) crc(4)
    ihdr_len = struct.unpack('>I', rest[:4])[0]
    ihdr = rest[:8 + ihdr_len + 4]
    body = rest[8 + ihdr_len + 4:]
    grab_data = struct.pack('>ii', xoff, yoff)
    grab = struct.pack('>I', 8) + b'grAb' + grab_data + struct.pack('>I', zlib.crc32(b'grAb' + grab_data) & 0xffffffff)
    path.write_bytes(sig + ihdr + grab + body)


def sprite_canvas(w, h):
    return Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))


def finish_sprite(img, name, yoff_extra=0):
    w, h = img.size
    img = img.resize((w // 2, h // 2), Image.LANCZOS)
    SPRITES.mkdir(parents=True, exist_ok=True)
    png_with_grab(img, img.size[0] // 2, img.size[1] + yoff_extra, SPRITES / f'{name}.png')


def draw_key(name, tag_rgb):
    img = sprite_canvas(28, 14)
    d = ImageDraw.Draw(img)
    steel = (176, 178, 176, 255)
    dark = (90, 92, 92, 255)
    d.ellipse([2, 6, 20, 24], outline=steel, width=5)
    d.rectangle([18, 12, 52, 17], fill=steel)
    d.rectangle([44, 17, 48, 24], fill=steel)
    d.rectangle([36, 17, 40, 22], fill=steel)
    d.ellipse([4, 8, 18, 22], outline=dark, width=1)
    d.rectangle([22, 3, 34, 11], fill=tag_rgb + (255,))
    finish_sprite(img, name)


def draw_ammo_box(name):
    img = sprite_canvas(24, 16)
    d = ImageDraw.Draw(img)
    d.polygon([(2, 12), (24, 4), (46, 12), (46, 30), (24, 31), (2, 30)], fill=(122, 96, 62, 255))
    d.polygon([(2, 12), (24, 4), (46, 12), (24, 20)], fill=(150, 122, 82, 255))
    d.rectangle([12, 14, 34, 22], fill=(226, 222, 206, 255))
    d.rectangle([14, 16, 32, 17], fill=(60, 50, 40, 255))
    d.rectangle([14, 19, 28, 20], fill=(60, 50, 40, 255))
    d.line([(2, 12), (2, 30), (46, 30), (46, 12)], fill=(70, 54, 36, 255), width=1)
    finish_sprite(img, name)


def draw_magazine(name):
    img = sprite_canvas(20, 22)
    d = ImageDraw.Draw(img)
    body = (54, 56, 58, 255)
    edge = (120, 122, 124, 255)
    d.polygon([(8, 2), (32, 2), (36, 40), (12, 44)], fill=body)
    d.polygon([(8, 2), (32, 2), (36, 40), (12, 44)], outline=edge)
    d.rectangle([10, 4, 30, 8], fill=(180, 150, 80, 255))
    for y in range(12, 40, 6):
        d.line([(12, y), (33, y)], fill=(80, 82, 84, 255))
    finish_sprite(img, name)


def draw_dressing(name):
    img = sprite_canvas(22, 14)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 4, 42, 26], radius=6, fill=(214, 206, 180, 255), outline=(120, 110, 90, 255))
    d.rectangle([18, 4, 26, 26], fill=(150, 40, 40, 255))
    d.rectangle([2, 12, 42, 18], fill=(150, 40, 40, 255))
    d.rectangle([20, 12, 24, 18], fill=(230, 230, 220, 255))
    finish_sprite(img, name)


def draw_fal_pickup(name):
    img = sprite_canvas(96, 30)
    d = ImageDraw.Draw(img)
    black = (34, 34, 36, 255)
    grey = (96, 96, 98, 255)
    wood = (92, 62, 40, 255)
    d.rectangle([20, 20, 150, 30], fill=black)          # receiver
    d.rectangle([150, 22, 190, 27], fill=grey)          # barrel
    d.rectangle([186, 20, 192, 29], fill=black)         # flash hider
    d.polygon([(0, 18), (22, 16), (24, 40), (6, 46)], fill=wood)  # stock
    d.rectangle([60, 30, 90, 36], fill=black)           # handguard
    d.polygon([(96, 30), (112, 30), (116, 54), (100, 56)], fill=black)  # magazine
    d.polygon([(40, 30), (52, 30), (48, 48), (36, 48)], fill=black)     # grip
    d.rectangle([60, 14, 64, 20], fill=grey)            # rear sight
    d.rectangle([176, 12, 179, 20], fill=grey)          # front sight
    finish_sprite(img, name, yoff_extra=0)


def draw_pistol_pickup(name):
    img = sprite_canvas(40, 26)
    d = ImageDraw.Draw(img)
    black = (40, 40, 42, 255)
    grey = (110, 110, 112, 255)
    d.rectangle([6, 14, 70, 24], fill=black)     # slide
    d.rectangle([8, 16, 68, 18], fill=grey)
    d.polygon([(12, 24), (34, 24), (30, 50), (12, 50)], fill=(78, 54, 34, 255))  # grip
    d.rectangle([36, 24, 48, 34], fill=black)   # trigger guard
    d.rectangle([40, 27, 44, 32], fill=(0, 0, 0, 0))
    finish_sprite(img, name)


def _paper(w, h, seed, rgb=(224, 216, 192)):
    """Aged paper: fbm grain, darker edges, no text (illegible marks only)."""
    base = np.ones((h, w, 3)) * np.array(rgb) / 255.0
    n = fbm(h, w, seed)[..., None]
    base = base * (0.92 + 0.10 * n)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / max(4.0, min(w, h) * 0.12)
    base = base * (0.86 + 0.14 * np.clip(edge, 0, 1)[..., None])
    return base


def _marks(d, x0, y0, x1, rows, step, rng, ink=(58, 52, 60, 255), width=2):
    """Rows of typed/handwritten-looking strokes: dashes of random length, never letters."""
    for r in range(rows):
        y = y0 + r * step
        x = x0 + rng.integers(0, 6)
        end = x1 - rng.integers(0, (x1 - x0) // 3 + 1)
        while x < end:
            seg = int(rng.integers(6, 22))
            d.line([(x, y + int(rng.integers(-1, 2))), (min(end, x + seg), y + int(rng.integers(-1, 2)))], fill=ink, width=width)
            x += seg + int(rng.integers(4, 9))


def draw_note_sheet(name):
    """Loose report sheet, drawn flat on desks and floors (FLATSPRITE, centred offsets)."""
    rng = np.random.default_rng(301)
    w, h = 64, 88
    img = to_img(_paper(w * 2, h * 2, 302)).convert('RGBA')
    d = ImageDraw.Draw(img)
    _marks(d, 16, 26, w * 2 - 16, 13, 10, rng)
    d.ellipse([w * 2 - 52, h * 2 - 50, w * 2 - 18, h * 2 - 16], outline=(118, 58, 92, 200), width=3)   # rubber stamp ring
    img = img.resize((w, h), Image.LANCZOS)
    SPRITES.mkdir(parents=True, exist_ok=True)
    png_with_grab(img, w // 2, h // 2, SPRITES / f'{name}.png')


def draw_note_register(name):
    """Open admission register: two ruled pages in a dark oxblood binding."""
    rng = np.random.default_rng(311)
    w, h = 120, 84
    W, H = w * 2, h * 2
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=8, fill=(74, 30, 28, 255))
    for k, (x0, x1) in enumerate(((8, W // 2 - 3), (W // 2 + 3, W - 9))):
        page = to_img(_paper(x1 - x0, H - 14, 312 + k, (222, 212, 184))).convert('RGBA')
        img.alpha_composite(page, (x0, 7))
    d = ImageDraw.Draw(img)
    for x in (8 + 34, W // 2 + 3 + 34):
        d.line([(x, 10), (x, H - 10)], fill=(150, 70, 60, 200), width=2)                # margin rule
    for y in range(22, H - 10, 11):
        d.line([(10, y), (W - 11, y)], fill=(120, 132, 150, 150), width=1)             # ruling
    _marks(d, 46, 18, W // 2 - 8, 11, 11, rng, ink=(46, 44, 70, 255))
    _marks(d, W // 2 + 40, 18, W - 14, 6, 11, rng, ink=(46, 44, 70, 255))
    d.line([(W // 2, 6), (W // 2, H - 6)], fill=(60, 36, 30, 255), width=3)             # gutter
    img = img.resize((w, h), Image.LANCZOS)
    SPRITES.mkdir(parents=True, exist_ok=True)
    png_with_grab(img, w // 2, h // 2, SPRITES / f'{name}.png')


def draw_selector():
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 2), (20, 12), (2, 22)], fill=(150, 34, 40, 255), outline=(230, 220, 210, 255))
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    img.resize((12, 12), Image.LANCZOS).save(GRAPHICS / 'RFSELCT.png')


# ----------------------------------------------------------------------------- title background
def title_background():
    """Main-menu background (TITLEPIC), no text: the porch arcade of Sainte-Anne at dawn seen
    from the dark vestibule. The left half stays dark and quiet for the engine-drawn menu."""
    W, H = 1920, 1080
    rng = np.random.default_rng(401)
    wall = plaster(H, W, 402, (72, 68, 66), 0.16, 0.25)
    yy, xx = np.mgrid[0:H, 0:W]
    # cold dawn light pooling from the arches on the right, falling off to the left
    glow = np.exp(-((xx - W * 0.74) / (W * 0.30)) ** 2 - ((yy - H * 0.62) / (H * 0.55)) ** 2)
    img = wall * (0.28 + 0.55 * glow[..., None])
    sky_top, sky_low = np.array((150, 164, 184)) / 255.0, np.array((214, 204, 188)) / 255.0
    for cx in (0.62, 0.86):                                       # two arches onto the street
        ax0, ax1 = int(W * cx - W * 0.075), int(W * cx + W * 0.075)
        top, base = int(H * 0.30), int(H * 0.92)
        r = (ax1 - ax0) / 2
        for x in range(ax0, ax1):
            dx = (x - (ax0 + ax1) / 2) / r
            y_arc = int(top + r * (1 - math.sqrt(max(0.0, 1 - dx * dx))))
            t = np.linspace(0, 1, base - y_arc)[:, None]
            img[y_arc:base, x] = sky_top * (1 - t) + sky_low * t
        # far facade across the street inside each arch (shut windows, soft)
        fy0 = int(H * 0.58)
        img[fy0:base, ax0:ax1] = img[fy0:base, ax0:ax1] * 0.55 + np.array((120, 112, 104)) / 255.0 * 0.45
        for wx in range(ax0 + 18, ax1 - 30, 46):
            for wy in range(fy0 + 20, base - 60, 70):
                img[wy:wy + 42, wx:wx + 18] = np.array((84, 94, 100)) / 255.0
        img[base - 40:base, ax0:ax1] = np.array((96, 92, 88)) / 255.0   # street and kerb
    # the vestibule floor: slab reflections of the arches
    fl = int(H * 0.92)
    img[fl:, :] = img[fl:, :] * 0.6 + np.array((40, 38, 36)) / 255.0 * 0.4
    for cx in (0.62, 0.86):
        x0, x1 = int(W * (cx - 0.07)), int(W * (cx + 0.07))
        img[fl:, x0:x1] += 0.08
    # vignette and grain
    v = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2
    img = img * np.clip(1.1 - 0.55 * v, 0.25, 1.0)[..., None]
    img += grain(H, W, 403, 0.02)[..., None]
    pil = to_img(np.clip(img, 0, 1))
    d = ImageDraw.Draw(pil)
    d.rectangle([int(W * 0.064), int(H * 0.11), int(W * 0.064) + 12, int(H * 0.89)], fill=(110, 28, 34))   # oxblood bar
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    pil.save(GRAPHICS / 'TITLEPIC.png', optimize=True)


# ----------------------------------------------------------------------------- main
def main():
    PATCH.mkdir(parents=True, exist_ok=True)
    # Walls (256 units, dado bottom-aligned with dontpegbottom)
    dado_wall('RFP_DADB', (52, 84, 122), 101)                       # admissions / corridors: blue dado
    dado_wall('RFP_DADG', (86, 118, 92), 102, (214, 212, 196))       # wards: green dado
    dado_wall('RFP_DADR', (112, 52, 46), 103, (222, 212, 196))       # registres / lodge: oxblood dado
    tile_wall('RFP_TILE', 104)                                        # laundry / consultations: tiled dado
    save_patch('Texture', 'RFP_PLN', plaster(128 * PPU, 128 * PPU, 105))            # plain plaster 128
    save_patch('Texture', 'RFP_DRK', plaster(128 * PPU, 128 * PPU, 106, (150, 142, 128), 0.16, 0.3))  # dim service plaster
    save_patch('Texture', 'RFS_LIME', stone_blocks(128 * PPU, 128 * PPU, 107))      # chapel / porch limestone
    save_patch('Texture', 'RFS_BASE', floor_grime(stone_blocks(64 * PPU, 128 * PPU, 108, 16, 48, (150, 142, 128), (96, 90, 82)), 0.4, 0.3))
    save_patch('Texture', 'RFS_REND', floor_grime(plaster(256 * PPU, 128 * PPU, 109, (184, 176, 160), 0.14, 0.3), 0.45, 0.2))  # facade render
    save_patch('Texture', 'RFW_PANL', planks(128 * PPU, 128 * PPU, 110, 24, (104, 74, 46)))   # wood panelling / shelving
    save_patch('Texture', 'RFM_PANL', floor_grime(plaster(128 * PPU, 128 * PPU, 111, (110, 114, 112), 0.08, 0.2), 0.3, 0.2))  # painted metal
    door_texture('RFD_DBL', 128, 128, 112, (88, 98, 82), leaves=2, panels=2)
    door_texture('RFD_SGL', 64, 128, 113, (88, 98, 82), leaves=1, panels=2)
    door_texture('RFD_OAK', 128, 128, 114, (110, 76, 46), leaves=2, panels=3)
    door_texture('RFM_DOOR', 64, 128, 115, (104, 108, 106), leaves=1, panels=1, metal=True)
    grille_texture('RFM_GRIL', 128, 128, 116)
    window_texture('RFG_WIN', 64, 64, 117)
    window_texture('RFG_WINT', 64, 96, 118)
    switch_textures(119)
    # Flats (128 units)
    save_patch('Flat', 'RFF_CER', ceramic(128 * PPU, 128 * PPU, 120))
    save_patch('Flat', 'RFF_CERD', ceramic(128 * PPU, 128 * PPU, 121, 32, (150, 146, 140), (90, 88, 84)))
    save_patch('Flat', 'RFF_CHK', checker(128 * PPU, 128 * PPU, 122))
    save_patch('Flat', 'RFF_WOOD', planks(128 * PPU, 128 * PPU, 123))
    save_patch('Flat', 'RFF_LINO', plaster(128 * PPU, 128 * PPU, 124, (62, 80, 66), 0.06, 0.25))
    save_patch('Flat', 'RFF_GRAV', gravel(128 * PPU, 128 * PPU, 125))
    save_patch('Flat', 'RFF_SLAB', stone_blocks(128 * PPU, 128 * PPU, 126, 64, 64, (150, 144, 132), (100, 96, 88)))
    save_patch('Flat', 'RFF_CONC', plaster(128 * PPU, 128 * PPU, 127, (138, 134, 126), 0.12, 0.3))
    save_patch('Flat', 'RFP_CEIL', plaster(128 * PPU, 128 * PPU, 128, (226, 222, 212), 0.06, 0.08))
    save_patch('Flat', 'RFP_CEID', plaster(128 * PPU, 128 * PPU, 129, (160, 154, 144), 0.1, 0.25))
    save_patch('Flat', 'RFW_TOP', planks(128 * PPU, 128 * PPU, 130, 32, (96, 66, 40)))
    save_patch('Flat', 'RFT_BED', plaster(64 * PPU, 64 * PPU, 131, (204, 200, 190), 0.08, 0.12))
    save_patch('Flat', 'RFT_MAT', plaster(64 * PPU, 64 * PPU, 132, (150, 132, 104), 0.12, 0.25))
    save_patch('Flat', 'RFM_TOP', plaster(64 * PPU, 64 * PPU, 133, (98, 100, 98), 0.08, 0.2))
    # Enamel plaques (64x16 units)
    for i, text in enumerate(['ADMISSIONS', 'CONSULTATIONS', 'PAVILLON EST', 'LINGERIE', 'REGISTRES', 'CHAPELLE', 'SORTIE', 'LOGE DU PORTIER', 'PAVILLON OUEST', 'GALERIE NORD']):
        sign(f'RFSIGN{i}', text, 200 + i)
    sky()
    # Street outside the porch (exit): Parisian facades, hospital pavilion behind the wall, setts
    facade_paris('RFS_FACD', 140)
    facade_hospital('RFS_HOSP', 141)
    save_patch('Flat', 'RFF_PAVE', cobbles(128 * PPU, 128 * PPU, 142))
    # Furniture block sides: beds, headboards, tables, archive shelving, laundry vats
    bed_side('RFT_BEDS', 150)
    bed_head('RFT_HEAD', 151)
    table_side('RFW_TBLS', 152)
    shelf_front('RFW_SHLF', 153)
    vat_side('RFM_VATS', 154)
    stained_glass('RFG_VITR', 155)                              # chapel windows (+ brightmap, GLDEFS)
    wear_decals()                                               # DECALDEF + graphics/decals masks
    # Sprites and menu graphics
    draw_key('RFKYA0', (70, 110, 200))
    draw_key('RFKYB0', (200, 160, 60))
    draw_ammo_box('RF9MA0')
    draw_magazine('RFRMA0')
    draw_dressing('RFMDA0')
    draw_fal_pickup('MGUNA0')
    draw_pistol_pickup('PISTA0')
    draw_note_sheet('RFNPA0')
    draw_note_register('RFNPB0')
    draw_selector()
    title_background()
    # TEXTURES lump
    lines = ['// Generated by scripts/mapkit/materials.py. RF01 stand-in material family (4 px per unit).', '']
    for kind, name, w, h, *rest in DEFS:
        ppu = rest[0] if rest else PPU   # facades read from a distance use 2 px per unit
        lines.append(f'{kind} {name}, {w}, {h}\n{{\n    XScale {ppu}\n    YScale {ppu}\n    Patch "patches/rf01/{name}.png", 0, 0\n}}')
    (ROOT / 'src' / 'TEXTURES.rf01').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'materials: {len(DEFS)} definitions written to src/TEXTURES.rf01')


if __name__ == '__main__':
    main()
