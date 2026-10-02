#!/usr/bin/env python3
"""Painted facades carry doors and shutters too (door pass of 02/10/2026): a wall that is not a whole number of bays
must not end through one of them.

Haussmann fronts (RF2_FAC1-3, RF01's 1940 street front): a 256-unit tile with two shop shutters and two doors on its
ground floor. A wall shows the tile from its left edge; when its right end falls inside a shutter or a door, that one
opening is replaced by the bare ground-floor masonry of the same family (the plain front RF2_FACU): the wall keeps its
whole shopfronts and ends on stone. Done as a composed TEXTURES definition (the tile itself, plus a small masonry
patch), so no large image is duplicated.

Fairground fronts (RF4_FAC1-3): one composition per 128-unit bay (a stall, a glazed bay, two doors). A wall gets as
many whole bays as fit, centred, between two piers made of the front's own corner post; a wall narrower than a bay
is all pier. A wall lower than the front gets the whole composition scaled to its height (pediment, doors and
plinth): the lower walls of the park showed the top of the image only and cut the doors' feet.
"""
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PATCHES = ROOT / 'src' / 'patches' / 'doors'

HAUSSMANN = {'RF2_FAC1': 'patches/rf02/RF2_FAC1.png', 'RF2_FAC2': 'patches/rf02/RF2_FAC2.png',
             'RF2_FAC3': 'patches/rf02/RF2_FAC3.png', 'RFSFACDA': 'patches/rf01_1940/RF2_SA_RFS_FACD.png'}
PLAIN = 'patches/rf02/RF2_FACU.png'
TILE_W, TILE_H = 256, 448
# ground-floor openings of the tile, in map units from its left edge (measured on the four images: the same layout)
OPENINGS = [(8.4, 95.1), (102.3, 126.6), (135.6, 221.7), (228.7, 253.3)]
COVER_TOP, COVER_BOTTOM, MARGIN = 108, 3, 3          # the masonry patch: up to the shop's head, down to the kerb line

LUNA = {'RF4_FAC1': 'patches/rf04/RF4_FAC1.png', 'RF4_FAC2': 'patches/rf04/RF4_FAC2.png', 'RF4_FAC3': 'patches/rf04/RF4_FAC3.png'}
BAY_W, BAY_H, POST = 128, 256, 8


def is_facade(tex):
    return tex.upper() in HAUSSMANN or tex.upper() in LUNA


def band_height():
    return COVER_TOP


def cut_openings(W):
    """Indices of the openings of the last, partial tile that a wall W units wide would cut at its right end."""
    r = W % TILE_W
    if r < 0.5 or TILE_W - r < 0.5:
        return []
    return [i for i, (a, b) in enumerate(OPENINGS) if a < r < b]


def spec_for(tex, W, H):
    """The variant a face needs, or None when the texture as it is shows nothing cut."""
    tex = tex.upper()
    W, H = int(round(W)), int(round(H))
    if tex in HAUSSMANN:
        cut = cut_openings(W)
        return dict(kind='facade', source=tex, w=W, masked=cut) if cut else None
    if tex in LUNA:
        H = min(H, BAY_H)
        if W % BAY_W == 0 and H == BAY_H:
            return None
        if W < 0.75 * BAY_W * H / BAY_H or W < 40:
            return dict(kind='luna', source=tex, w=W, h=H, mode='pier')     # a jamb, a reveal, a narrow return
        if H < 144:
            return None                               # a strip above an opening: the top of the front, as it was
        return dict(kind='luna', source=tex, w=W, h=H, mode='bays')
    return None


def _haussmann_px(tex):
    img = Image.open(ROOT / 'src' / HAUSSMANN[tex])
    ppu = img.size[0] / TILE_W
    return img, ppu, img.size[0], int(round(TILE_H * ppu))


def haussmann_def(name, spec):
    """(TEXTURES definition, {file name: image} of the masonry patches it needs)."""
    tex = spec['source']
    img, ppu, w_px, h_px = _haussmann_px(tex)
    W = spec['w']
    files = {}
    lines = [f'Texture {name}, {int(round(W * ppu))}, {h_px}', '{', f'    XScale {ppu!r}', f'    YScale {ppu!r}']
    for k in range(int(math.ceil(W / TILE_W))):
        lines.append(f'    Patch "{HAUSSMANN[tex]}", {k * w_px}, 0')
    plain = None
    k = W // TILE_W
    top = h_px - int(round(COVER_TOP * ppu))
    for i in spec['masked']:
        a, b = OPENINGS[i]
        fname = f'F_{tex}_{i}.png'
        c0, c1 = int((a - MARGIN) * ppu), int(math.ceil((b + MARGIN) * ppu))
        if plain is None:
            plain = Image.open(ROOT / 'src' / PLAIN).convert('RGB')
            if plain.size != (w_px, h_px):
                plain = plain.resize((w_px, h_px), Image.LANCZOS)
        files[fname] = plain.crop((c0, top, min(c1, w_px), h_px - int(round(COVER_BOTTOM * ppu))))
        lines.append(f'    Patch "patches/doors/{fname}", {k * w_px + c0}, {top}')
    lines.append('}')
    how = 'ouverture coupee en bout de mur remplacee par le mur nu du rez-de-chaussee (' + ', '.join(
        ('rideau' if OPENINGS[i][1] - OPENINGS[i][0] > 60 else 'porte') + f' {OPENINGS[i][0]:g}-{OPENINGS[i][1]:g} u' for i in spec['masked']) + ')'
    return '\n'.join(lines), files, how


def luna_image(spec):
    """A fairground front for a wall W x H: the whole composition of a bay (pediment, doors, plinth) scaled uniformly
    to the wall's height, as many whole bays as fit, the rest shared between two piers made of the front's own corner
    post repeated (never stretched)."""
    src = Image.open(ROOT / 'src' / LUNA[spec['source']]).convert('RGBA')
    ppu = src.size[0] / BAY_W
    W, H = spec['w'], spec['h']
    if spec.get('mode') == 'pier':
        post = src.crop((0, 0, int(POST * ppu), src.size[1]))
        flip = post.transpose(Image.FLIP_LEFT_RIGHT)
        w_px, h_px = int(round(W * ppu)), int(round(H * ppu))
        strip = Image.new('RGBA', (w_px, src.size[1]))
        x, k = 0, 0
        while x < w_px:
            strip.paste(post if k % 2 == 0 else flip, (x, 0))
            x += post.size[0]
            k += 1
        top = 0 if H < 64 else src.size[1] - h_px      # a strip above an opening: the top; a wall from the ground: its foot
        return strip.crop((0, top, w_px, top + h_px)), ppu, 'trumeau (poteau de la facade repete) : aucune porte sur un retour de mur'
    s = H / BAY_H
    bay = src if s == 1 else src.resize((max(1, round(src.size[0] * s)), round(H * ppu)), Image.LANCZOS)
    bw, h_px, w_px = bay.size[0], bay.size[1], int(round(W * ppu))
    n = w_px // bw
    rest = w_px - n * bw
    if n >= 1 and rest / w_px <= 0.07:
        bays = Image.new('RGBA', (n * bw, h_px))
        for k in range(n):
            bays.paste(bay, (k * bw, 0))
        out = bays.resize((w_px, h_px), Image.LANCZOS)
        how = f"{n} travee(s) entiere(s) a l'echelle {s:.2f}, elargies de {rest / w_px * 100:.0f} %"
    else:
        post = bay.crop((0, 0, max(2, int(POST * ppu * s)), h_px))
        flip = post.transpose(Image.FLIP_LEFT_RIGHT)
        out = Image.new('RGBA', (w_px, h_px))
        left = rest // 2

        def pier(x0, x1):
            x, k = x0, 0
            while x < x1:
                out.paste(post if k % 2 == 0 else flip, (x, 0))
                x += post.size[0]
                k += 1
        pier(0, left)
        pier(left + n * bw, w_px)
        for k in range(n):
            out.paste(bay, (left + k * bw, 0))
        how = (f"{n} travee(s) entiere(s) a l'echelle {s:.2f} entre deux trumeaux" if n
               else "trumeau seul (mur plus etroit qu'une travee)")
    return out, ppu, how
