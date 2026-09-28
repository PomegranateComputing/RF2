#!/usr/bin/env python3
"""Viktor's HUD portrait: the six health states cut from the owner's sheet (RF2_VIKTOR_HUD_OPUS.md, 27/09/2026).

Source: art/rf2_hud_viktor_02/source/RF2_VIKTOR_HUD_SHEET.png, 1536x1024 RGBA, six cut-out portraits on a 3 x 2
layout (read left to right, top row first): intact, lightly injured, wounded, severely wounded, critical, dead.
The portraits do not sit on an exact 512 grid (head centres 496-500 px apart, skull tops 3 to 11 px apart): each one
is framed from its own silhouette so that the six states share the skull top, the head axis and the scale.

Framing: 512 x 512 (the size of the HUD slot's texture), skull top at y 9, head axis at x 256. The heads of the
sheet already share one scale (skull width 237-240 px at the same heights), so no scaling is applied. Pixels
nearer to a neighbouring portrait are cleared; the same soft fade closes the six silhouettes at the sides and the
bottom, so the hoodie's edge is identical in every state.

Output: src/graphics/hud/viktor/VIKTOR_H100.png, VIKTOR_H080.png, VIKTOR_H060.png, VIKTOR_H040.png, VIKTOR_H020.png,
VIKTOR_DEAD.png, and art/rf2_hud_viktor_02/manifest.json (state -> file, placement measured, sha256).
Usage: python scripts/ui/viktor_portraits.py
"""
import hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'art' / 'rf2_hud_viktor_02' / 'source' / 'RF2_VIKTOR_HUD_SHEET.png'
OUT = ROOT / 'src' / 'graphics' / 'hud' / 'viktor'
MANIFEST = ROOT / 'art' / 'rf2_hud_viktor_02' / 'manifest.json'
SIZE, TOP = 512, 9
STATES = [('VIKTOR_H100', 'intact', '> 80 %'), ('VIKTOR_H080', 'légèrement blessé', '61-80 %'),
          ('VIKTOR_H060', 'blessé', '41-60 %'), ('VIKTOR_H040', 'grièvement blessé', '21-40 %'),
          ('VIKTOR_H020', 'critique', '1-20 %'), ('VIKTOR_DEAD', 'mort', 'joueur mort')]


def head_centres(alpha, y0, y1):
    """Skull tops and head axes of the three portraits of one row: columns covered in the band 40-100 px below
    the highest skull (above the ears, below any hoodie)."""
    band = alpha[y0:y1] > 128
    rows = np.nonzero(band.any(axis=1))[0]
    top = y0 + rows.min()
    cols = (alpha[top + 40:top + 100] > 128).any(axis=0)
    runs, start = [], None
    for x, on in enumerate(list(cols) + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            if x - start > 150:
                runs.append((start, x - 1))
            start = None
    assert len(runs) == 3, runs
    out = []
    for (a, b) in runs:
        cx = (a + b) / 2
        col = alpha[y0:y1, a:b + 1] > 128
        out.append((cx, y0 + np.nonzero(col.any(axis=1))[0].min(), b - a + 1))
    return out


def main():
    sheet = np.asarray(Image.open(SRC).convert('RGBA')).astype(np.float64)
    H, W = sheet.shape[:2]
    alpha = sheet[..., 3]
    heads = head_centres(alpha, 0, H // 2) + head_centres(alpha, H // 2, H)
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = dict(source=str(SRC.relative_to(ROOT)).replace('\\', '/'),
                    source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
                    frame=[SIZE, SIZE], skull_top_y=TOP, head_axis_x=SIZE // 2, states=[])
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    side = np.clip((248 - np.abs(xx + 0.5 - SIZE / 2)) / 16, 0, 1)          # identical side fade
    bottom = np.clip((SIZE - 2 - yy) / 10, 0, 1)                             # identical bottom fade
    for k, ((cx, top, width), (name, label, rule)) in enumerate(zip(heads, STATES)):
        row = k // 3
        rh0, rh1 = (0, H // 2) if row == 0 else (H // 2, H)
        others = [h[0] for j, h in enumerate(heads) if j // 3 == row and j != k]
        x0, y0 = int(round(cx)) - SIZE // 2, top - TOP
        frame = np.zeros((SIZE, SIZE, 4))
        sx0, sy0 = max(0, x0), max(rh0, y0)
        sx1, sy1 = min(W, x0 + SIZE), min(rh1, y0 + SIZE)
        frame[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = sheet[sy0:sy1, sx0:sx1]
        # clear what is nearer to a neighbouring portrait of the same row
        gx = xx + x0
        nearer = np.zeros((SIZE, SIZE), bool)
        for ox in others:
            nearer |= np.abs(gx - ox) < np.abs(gx - cx)
        frame[nearer] = 0
        frame[..., 3] *= side * bottom
        img = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8), 'RGBA')
        path = OUT / f'{name}.png'
        img.save(path, optimize=True)
        manifest['states'].append(dict(state=k + 1, file=f'graphics/hud/viktor/{name}.png', label=label, health=rule,
                                       sheet_head_axis_x=round(float(cx), 1), sheet_skull_top_y=int(top),
                                       skull_width_px=int(width), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        print(f'{name}: axis {cx:.1f}, skull top {top}, skull width {width}px -> {path.name}')
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
