#!/usr/bin/env python3
"""Door images fitted to the openings that carry them (door pass of 02/10/2026).

A door, a gate or a shutter is one object: its image must cover its opening exactly once. The maps ask for a fitted
image with fit(): the name of a variant of a catalogued door image for a face of W x H map units, recomposed from the
source image rather than stretched:

  - the source is scaled uniformly by the larger of the two ratios (target / source), so that hardware (handles,
    locks, mouldings, rivets) keeps its proportions and never grows;
  - what is then left over in the other direction is taken out of the plain zones of the image only (columns or rows
    along which the image does not change: the flat of a panel, the run of a bar), never through a handle or a moulding;
  - images made of repeating members (bars, shutter slats) are tiled to the width instead;
  - an image without plain zones (rust blotches) is only scaled, and only within 10 % of its proportions;
  - a static door set in a taller wall gets that wall's material above its head, in one image for the whole face;
  - the opposite face of a single door is mirrored (FlipX), so that the handle stays on the same edge of the leaf.

The variants are named from a hash of their specification (stable across builds) and listed in door_variants.json next
to this file. `python scripts/mapkit/doors.py` (re)draws every listed variant into src/patches/doors/ and writes
src/TEXTURES.doors. Source images are only read; no shared texture is rescaled.
"""
import hashlib, json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(__file__).with_name('door_variants.json')
PATCHES = ROOT / 'src' / 'patches' / 'doors'

# name: (source file under src/, world width, world height, pixels per unit, kind, mirror the opposite face)
# kind: panel = recomposed through its plain zones; bars = tiled across, plain zones up; rigid = scaled only
CATALOG = {
    'RFD_SGL': ('patches/rf01/RFD_SGL.png', 64, 128, 4, 'panel', True),
    'RFD_DBL': ('patches/rf01/RFD_DBL.png', 128, 128, 4, 'panel', False),
    'RFD_OAK': ('patches/rf01/RFD_OAK.png', 128, 128, 4, 'panel', False),
    'RFD_OAKS': ('patches/rf01/RFD_OAK.png', 64, 128, 4, 'panel', True),      # one leaf of the oak double door
    'RFM_DOOR': ('patches/rf01/RFM_DOOR.png', 64, 128, 4, 'panel', True),
    'RFM_GRIL': ('patches/rf01/RFM_GRIL.png', 128, 128, 4, 'bars', False),
    'RFDSGLA': ('patches/rf01_1940/RF2_SA_RFD_SGL.png', 64, 128, 4, 'panel', True),
    'RFDDBLA': ('patches/rf01_1940/RF2_SA_RFD_DBL.png', 128, 128, 4, 'panel', False),
    'RFMDOORA': ('patches/rf01_1940/RF2_SA_RFM_DOOR.png', 64, 128, 4, 'panel', True),
    'RFMGRILA': ('patches/rf01_1940/RF2_SA_RFM_GRIL.png', 128, 128, 4, 'bars', False),
    'RF2_RIDO': ('patches/rf02/RF2_RIDO.png', 128, 128, 4, 'bars', False),
    'RF4_PSST': ('patches/rf04/RF4_PSST.png', 64, 96, 4, 'rigid', True),
    'RFDOORB': ('textures/RFDOORB.png', 128, 128, 1, 'rigid', False),
    'RFEXIT': ('textures/RFEXIT.png', 64, 128, 1, 'rigid', False),
    'RF6_JOUR': ('patches/rf06/RF6_JOUR.png', 64, 96, 4, 'plain', False),
}


def is_door(tex):
    return tex.upper() in CATALOG


def natural(tex):
    _, w, h, _, _, _ = CATALOG[tex.upper()]
    return w, h


def load_registry():
    return json.loads(REGISTRY.read_text(encoding='utf-8')) if REGISTRY.exists() else {}


_registry = None


def fit(tex, W, H, mirrored=False, wall=None, total=None):
    """Name of the image of door `tex` for a face W x H (map units). wall/total: a static face `total` units high whose
    door head is at H, the rest above it showing the wall texture `wall`. Registers the variant; the source image
    itself is returned when it already fits and nothing is asked of it."""
    global _registry
    tex = tex.upper()
    src, w, h, ppu, kind, mirror = CATALOG[tex]
    W, H = int(round(W)), int(round(H))
    mirrored = bool(mirrored and mirror)
    if (W, H) == (w, h) and not mirrored and not (wall and total and total > H):
        return tex
    spec = dict(source=tex, w=W, h=H, mirrored=mirrored)
    if wall and total and total > H:
        spec.update(wall=wall.upper(), total=int(round(total)))
    key = json.dumps(spec, sort_keys=True)
    name = 'RD' + hashlib.sha1(key.encode()).hexdigest()[:6].upper()
    if _registry is None:
        _registry = load_registry()
    if _registry.get(name) != spec:
        _registry[name] = spec
        REGISTRY.write_text(json.dumps(dict(sorted(_registry.items())), indent=1) + '\n', encoding='utf-8')
    return name


# ----------------------------------------------------------------------------------------------- recomposition
def plain_lines(img, axis, reach=(6, 14, 26), tol=9.0):
    """Indices of the columns (axis 1) or rows (axis 0) along which the image does not change: the image there looks
    the same `reach` pixels before and after, over its whole other dimension (95th percentile of the difference of
    the blurred luminance under tol). The flat of a panel qualifies; a moulding, a handle and its surroundings do not."""
    lum = np.asarray(img.convert('L').filter(ImageFilter.GaussianBlur(2.0))).astype(float)
    if axis == 0:
        lum = lum.T
    n = lum.shape[1]
    ok = np.ones(n, bool)
    for d in reach:
        for sgn in (-1, 1):
            j = np.clip(np.arange(n) + sgn * d, 0, n - 1)
            diff = np.percentile(np.abs(lum - lum[:, j]), 95, axis=0)
            ok &= diff < tol
    ok[:8] = False
    ok[-8:] = False
    return np.flatnonzero(ok)


def remove_lines(img, axis, count):
    """Take `count` columns or rows out of the plain zones, spread evenly over them. None when they cannot give that
    much (more than 60 % of them would go)."""
    if count <= 0:
        return img
    plain = plain_lines(img, axis)
    if len(plain) * 0.6 < count:
        return None
    pick = plain[np.linspace(0, len(plain) - 1, count).round().astype(int)]
    pick = np.unique(pick)
    k = 0
    while len(pick) < count:                       # rounding collisions: take neighbours
        cand = np.setdiff1d(plain, pick)
        pick = np.unique(np.append(pick, cand[k % len(cand)]))
        k += 7
    arr = np.asarray(img)
    keep = np.setdiff1d(np.arange(arr.shape[1 if axis == 1 else 0]), pick)
    return Image.fromarray(arr[:, keep] if axis == 1 else arr[keep])


def add_lines(img, axis, count):
    """Lengthen the image by `count` columns or rows, repeated in its plain zones (the bars of a gate drawn longer).
    None when it has no plain zone."""
    if count <= 0:
        return img
    plain = plain_lines(img, axis)
    if len(plain) < 8:
        return None
    pick = plain[np.linspace(0, len(plain) - 1, count).round().astype(int)]
    arr = np.asarray(img)
    n = arr.shape[1 if axis == 1 else 0]
    order = np.sort(np.concatenate([np.arange(n), pick]), kind='stable')
    return Image.fromarray(arr[:, order] if axis == 1 else arr[order])


def tile_width(img, width):
    """Repeat a seamless image of repeating members across `width` pixels, centred on the opening."""
    w, h = img.size
    out = Image.new(img.mode, (width, h))
    x = -((w - width % w) % w) // 2 if width % w else 0
    while x < width:
        out.paste(img, (x, 0))
        x += w
    return out


# images that are a part of another image: (left, top) of the part, in pixels
CROPS = {'RFD_OAKS': (0, 0)}


def source_image(tex):
    src, w, h, ppu, kind, _ = CATALOG[tex]
    img = Image.open(ROOT / 'src' / src).convert('RGBA')
    if tex in CROPS:
        x, y = CROPS[tex]
        img = img.crop((x, y, x + w * ppu, y + h * ppu))
    assert img.size == (w * ppu, h * ppu), (tex, img.size)
    return img, ppu, kind


def door_image(tex, W, H):
    """The door image recomposed to W x H map units, and how it was done."""
    img, ppu, kind = source_image(tex)
    tw, th = W * ppu, H * ppu
    sw, sh = img.size
    if (tw, th) == (sw, sh):
        return img, 'source'
    if kind == 'plain':
        return img.resize((tw, th), Image.LANCZOS), 'etendue (image sans motif)'
    if kind == 'bars':
        how = []
        if th != sh:
            cut = remove_lines(img, 0, sh - th) if th < sh else add_lines(img, 0, th - sh)
            if cut is None:
                s = th / sh
                cut = img.resize((max(1, round(sw * s)), th), Image.LANCZOS)
                how.append(f'echelle {s:.2f}')
            else:
                how.append(f'{abs(sh - th)} lignes {"retirees des" if th < sh else "ajoutees dans les"} zones unies')
            img = cut
        if img.size[0] != tw:
            img = tile_width(img, tw)
            how.append('membres repetes sur la largeur')
        return img, ', '.join(how)
    s = max(tw / sw, th / sh)
    how = []
    if abs(s - 1) > 1e-6:
        img = img.resize((max(tw, round(sw * s)), max(th, round(sh * s))), Image.LANCZOS)
        how.append(f'echelle uniforme {s:.3f}')
    for axis, target in ((1, tw), (0, th)):
        cur = img.size[0] if axis == 1 else img.size[1]
        if cur == target:
            continue
        cut = remove_lines(img, axis, cur - target) if kind == 'panel' else None
        if cut is None:
            ratio = target / cur
            if kind != 'panel' and abs(ratio - 1) > 0.10:
                raise ValueError(f'{tex} {W}x{H}: image rigide, proportions hors tolerance ({ratio:.2f})')
            cut = img.resize((tw, img.size[1]) if axis == 1 else (img.size[0], th), Image.LANCZOS)
            how.append(f'{"largeur" if axis == 1 else "hauteur"} ajustee de {abs(1 - ratio) * 100:.0f} %')
        else:
            how.append(f'{cur - target} {"colonnes" if axis == 1 else "lignes"} retirees des zones unies')
        img = cut
    assert img.size == (tw, th), (tex, W, H, img.size)
    return img, ', '.join(how)


def wall_patch(tex):
    """(image, pixels per unit) of a wall texture, from the TEXTURES lumps or src/textures."""
    for tf in sorted((ROOT / 'src').glob('TEXTURES.*')):
        t = tf.read_text(encoding='utf-8', errors='replace')
        m = re.search(r'(?:Texture|WallTexture)\s+"?%s"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{(.*?)\n\}' % re.escape(tex), t, re.S | re.I)
        if m:
            xs = re.search(r'XScale\s+([\d.]+)', m.group(3))
            p = re.search(r'Patch\s+"([^"]+)"', m.group(3)).group(1)
            f = ROOT / 'src' / p
            if not f.exists():
                f = f.with_suffix('.png')
            return Image.open(f).convert('RGBA'), float(xs.group(1)) if xs else 1.0
    f = ROOT / 'src' / 'textures' / f'{tex}.png'
    return Image.open(f).convert('RGBA'), 1.0


def variant_image(spec):
    img, how = door_image(spec['source'], spec['w'], spec['h'])
    ppu = CATALOG[spec['source']][3]
    if spec.get('total'):
        wall, wppu = wall_patch(spec['wall'])
        if wppu != ppu:
            wall = wall.resize((round(wall.size[0] * ppu / wppu), round(wall.size[1] * ppu / wppu)), Image.LANCZOS)
        W, T = spec['w'] * ppu, spec['total'] * ppu
        canvas = Image.new('RGBA', (W, T))
        y = T - wall.size[1]                       # the wall's own image anchored at the floor, as the walls beside it
        while y > -wall.size[1]:
            for x in range(0, W, wall.size[0]):
                canvas.paste(wall, (x, y))
            y -= wall.size[1]
        canvas.paste(img, (0, T - img.size[1]))
        img = canvas
        how += f' ; mur {spec["wall"]} au-dessus de la tete de porte'
    return img, how


def names_in_maps():
    """The variant names the maps as shipped actually use (src/maps and the bench maps)."""
    used = set()
    for wad in list((ROOT / 'src' / 'maps').glob('*.wad')) + list((ROOT / 'bench').glob('*/maps/*.wad')):
        used |= {m.decode() for m in re.findall(rb'"(RD[0-9A-F]{6})"', wad.read_bytes())}
    return used


def main():
    reg = load_registry()
    if '--keep-unused' not in sys.argv:
        used = names_in_maps()
        dropped = sorted(set(reg) - used)
        if dropped:
            reg = {k: v for k, v in reg.items() if k in used}
            REGISTRY.write_text(json.dumps(dict(sorted(reg.items())), indent=1) + '\n', encoding='utf-8')
            print(f'doors: {len(dropped)} variants no map uses any more dropped from the registry')
    PATCHES.mkdir(parents=True, exist_ok=True)
    wanted = set()
    lines = ['// Generated by scripts/mapkit/doors.py from door_variants.json: door, gate and shutter images fitted to their',
             '// openings (door pass of 02/10/2026). Do not edit by hand.', '']
    report = {}
    for tex, (x, y) in sorted(CROPS.items()):
        src, w, h, ppu, _, _ = CATALOG[tex]
        lines.append(f'Texture {tex}, {w * ppu}, {h * ppu}\n{{\n    XScale {ppu}\n    YScale {ppu}\n'
                     f'    Patch "{src}", {-x}, {-y}\n}}')
    for name, spec in sorted(reg.items()):
        ppu = CATALOG[spec['source']][3]
        base = dict(spec, mirrored=False)
        base_name = 'RD' + hashlib.sha1(json.dumps(base, sort_keys=True).encode()).hexdigest()[:6].upper()
        img, how = variant_image(base)
        f = PATCHES / f'{base_name}.png'
        img.save(f, optimize=True)
        wanted.add(f.name)
        flip = '\n    {\n        FlipX\n    }' if spec['mirrored'] else ''
        lines.append(f'Texture {name}, {img.size[0]}, {img.size[1]}\n{{\n    XScale {ppu}\n    YScale {ppu}\n'
                     f'    Patch "patches/doors/{base_name}.png", 0, 0{flip}\n}}')
        report[name] = dict(spec, how=how + (' ; face opposee en miroir' if spec['mirrored'] else ''))
    for old in PATCHES.glob('*.png'):
        if old.name not in wanted:
            old.unlink()
    (ROOT / 'src' / 'TEXTURES.doors').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'door_variants_report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'doors: {len(reg)} variants, {len(wanted)} images -> src/patches/doors, src/TEXTURES.doors')


if __name__ == '__main__':
    sys.exit(main())
