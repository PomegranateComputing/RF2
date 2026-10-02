#!/usr/bin/env python3
"""The post of the attack station (bench only, procedural): a wooden post with a cross-bar and a painted ring, the
height of a man (56 u at Scale 0.25). Usage: python bench/familles/materials_famille.py"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
from materials import png_with_grab  # noqa: E402


def main():
    img = Image.new('RGBA', (128, 224), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wood, dark, white, red = (120, 92, 60, 255), (70, 52, 34, 255), (220, 214, 200, 255), (150, 44, 36, 255)
    d.rectangle([54, 24, 74, 223], fill=wood)                       # the post
    d.rectangle([54, 24, 58, 223], fill=dark)
    d.rectangle([20, 70, 108, 86], fill=wood)                       # the cross-bar, at the shoulders
    d.rectangle([20, 82, 108, 86], fill=dark)
    d.ellipse([40, 0, 88, 48], fill=white, outline=dark, width=3)    # the head: a painted disc
    d.ellipse([52, 12, 76, 36], fill=red)
    d.rectangle([36, 208, 92, 223], fill=dark)                      # its foot
    (HERE / 'sprites').mkdir(exist_ok=True)
    png_with_grab(img, 64, 224, HERE / 'sprites' / 'RFBDA0.png')
    print('RFBDA0.png')


if __name__ == '__main__':
    main()
