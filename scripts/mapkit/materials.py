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


def save_patch(kind, name, arr_or_img, wunits=None, hunits=None):
    img = arr_or_img if isinstance(arr_or_img, Image.Image) else to_img(arr_or_img)
    PATCH.mkdir(parents=True, exist_ok=True)
    path = PATCH / f'{name}.png'
    img.save(path, optimize=True)
    w, h = img.size
    DEFS.append((kind, name, w, h))
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
    for f in ('C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/arial.ttf', 'DejaVuSans-Bold.ttf'):
        try:
            font = ImageFont.truetype(f, int(H * 0.5))
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
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


def draw_selector():
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 2), (20, 12), (2, 22)], fill=(150, 34, 40, 255), outline=(230, 220, 210, 255))
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    img.resize((12, 12), Image.LANCZOS).save(GRAPHICS / 'RFSELCT.png')


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
    # Sprites and menu graphics
    draw_key('RFKYA0', (70, 110, 200))
    draw_key('RFKYB0', (200, 160, 60))
    draw_ammo_box('RF9MA0')
    draw_magazine('RFRMA0')
    draw_dressing('RFMDA0')
    draw_fal_pickup('MGUNA0')
    draw_pistol_pickup('PISTA0')
    draw_selector()
    # TEXTURES lump
    lines = ['// Generated by scripts/mapkit/materials.py. RF01 stand-in material family (4 px per unit).', '']
    for kind, name, w, h in DEFS:
        lines.append(f'{kind} {name}, {w}, {h}\n{{\n    XScale {PPU}\n    YScale {PPU}\n    Patch "patches/rf01/{name}.png", 0, 0\n}}')
    (ROOT / 'src' / 'TEXTURES.rf01').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'materials: {len(DEFS)} definitions written to src/TEXTURES.rf01')


if __name__ == '__main__':
    main()
