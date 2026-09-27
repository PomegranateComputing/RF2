#!/usr/bin/env python3
"""RF2-UI-01 title composition from an in-engine render, no text (the engine draws the title and menus).

Source: a clean capture of RF01 (HUD and weapon hidden, scripts/devrun.py +rf_dev_view): the west-pavilion
corridor where the game begins, the pavilion grille at its end. Grade: exposure brought down to a dawn
interior, shadows toward charcoal, the plaster toward dirty paper, colour pulled back; the menu side
(left) sinks to charcoal; vignette and fine grain. Proportions and framing are those of the capture.

Usage: python scripts/ui/title_compose.py <capture.png>
Writes src/graphics/ui/RFMENUBG.png and src/graphics/TITLEPIC.png (1920x1080, same image).
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]


def compose(src):
    shot = Image.open(src).convert('RGB')
    w, h = shot.size
    tw = min(w, int(h * 16 / 9))
    th = int(tw * 9 / 16)
    x0, y0 = (w - tw) // 2, (h - th) // 2
    img = shot.crop((x0, y0, x0 + tw, y0 + th)).resize((1920, 1080), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    a = np.asarray(img).astype(float) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    # colour pulled back, exposure down, shadows deepened (gamma), a touch of contrast
    a = a * 0.62 + lum[..., None] * 0.38
    a = np.clip(a * 0.60, 0, 1) ** 1.25
    # split toning: shadows toward charcoal-blue, highlights toward dirty paper
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    shadow = np.array([0.055, 0.050, 0.060])
    paper = np.array([0.91, 0.89, 0.85])
    t = np.clip(lum / 0.55, 0, 1)[..., None]
    a = a * 0.8 + (shadow * (1 - t) + paper * t * lum[..., None]) * 0.2
    yy, xx = np.mgrid[0:1080, 0:1920] / np.array([1080.0, 1920.0])[:, None, None]
    # menu side: charcoal over the left 55 %, eased
    left = np.clip((0.56 - xx) / 0.56, 0, 1) ** 1.2
    charcoal = np.array([14, 12, 14]) / 255.0
    a = a * (1 - 0.78 * left[..., None]) + charcoal * 0.78 * left[..., None]
    # vignette, stronger toward the bottom corners (the floor) and the ceiling
    v = (xx - 0.58) ** 2 * 1.1 + (yy - 0.5) ** 2 * 2.0
    a = a * np.clip(1.08 - 0.95 * v, 0.28, 1.0)[..., None]
    rng = np.random.default_rng(1940)
    grain = rng.normal(0, 0.012, a.shape[:2])[..., None]
    a = np.clip(a + grain, 0, 1)
    return Image.fromarray((a * 255 + 0.5).astype(np.uint8), 'RGB')


def main():
    out = compose(sys.argv[1])
    ui = ROOT / 'src' / 'graphics' / 'ui'
    ui.mkdir(parents=True, exist_ok=True)
    out.save(ui / 'RFMENUBG.png', optimize=True)   # not RFTITLE: that lump name would shadow the RFTitle font
    out.save(ROOT / 'src' / 'graphics' / 'TITLEPIC.png', optimize=True)
    print(ui / 'RFMENUBG.png', out.size)


if __name__ == '__main__':
    main()
