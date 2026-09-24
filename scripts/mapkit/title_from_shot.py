#!/usr/bin/env python3
"""Main-menu background (TITLEPIC) from an in-engine render, no text.

Takes a clean screenshot (HUD hidden: +screenblocks 12) of the porch arches opening onto the
street at dawn, crops it to 16:9, darkens and cools the left side where the engine draws the menu,
adds a vignette, grain and the oxblood bar of the RF2 identity.

Usage: python scripts/mapkit/title_from_shot.py <screenshot.png>
Writes src/graphics/TITLEPIC.png (1920x1080).
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]


def main():
    shot = Image.open(sys.argv[1]).convert('RGB')
    w, h = shot.size
    tw = min(w, int(h * 16 / 9))
    th = int(tw * 9 / 16)
    x0, y0 = (w - tw) // 2, (h - th) // 2
    img = shot.crop((x0, y0, x0 + tw, y0 + th)).resize((1920, 1080), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    a = np.asarray(img).astype(float) / 255.0
    yy, xx = np.mgrid[0:1080, 0:1920] / np.array([1080.0, 1920.0])[:, None, None]
    left = np.clip((0.62 - xx) / 0.62, 0, 1) ** 1.3                      # menu side
    a = a * (1 - 0.72 * left[..., None])
    grey = a.mean(axis=2, keepdims=True)
    a = a * 0.8 + grey * 0.2                                            # slightly desaturated
    a = a * np.array([0.94, 0.97, 1.03])                                # cool dawn
    v = (xx - 0.5) ** 2 * 1.4 + (yy - 0.5) ** 2 * 1.8
    a = a * np.clip(1.05 - 0.9 * v, 0.3, 1.0)[..., None]
    rng = np.random.default_rng(7)
    a = np.clip(a + (rng.random(a.shape[:2])[..., None] - 0.5) * 0.025, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(out)
    d.rectangle([123, 119, 135, 961], fill=(110, 28, 34))                # oxblood bar
    dst = ROOT / 'src' / 'graphics' / 'TITLEPIC.png'
    out.save(dst, optimize=True)
    print(dst, out.size)


if __name__ == '__main__':
    main()
