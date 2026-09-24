#!/usr/bin/env python3
"""Contact sheet of a dev screenshot folder (build/dev/shots/<name>) for quick review.

Usage: python scripts/shots_sheet.py rf01_tour [--cols 3] [--width 640]
Writes build/dev/shots/<name>_sheet.png (numbered in capture order).
"""
import argparse, os
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--cols', type=int, default=3)
    ap.add_argument('--width', type=int, default=640)
    a = ap.parse_args()
    folder = ROOT / 'build' / 'dev' / 'shots' / a.name
    files = sorted(folder.glob('*.png'), key=os.path.getmtime)
    if not files:
        raise SystemExit(f'no screenshots in {folder}')
    first = Image.open(files[0])
    w = a.width
    h = round(first.height * w / first.width)
    rows = (len(files) + a.cols - 1) // a.cols
    sheet = Image.new('RGB', (a.cols * w, rows * (h + 14)), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS)
        x, y = (i % a.cols) * w, (i // a.cols) * (h + 14)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + h + 1), str(i + 1), fill=(230, 230, 230))
    out = folder.parent / f'{a.name}_sheet.png'
    sheet.save(out)
    print(out, sheet.size, len(files))


if __name__ == '__main__':
    main()
