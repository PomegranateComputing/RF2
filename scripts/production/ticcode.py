"""Read the game tic that the bench draws in the top-left corner of every picture (RFBenchHandler.DrawTicCode):
a red start cell, 16 cells for the bits of Level.maptime (lowest first, white = 1), a green end cell, 8x8 pixels
each, from x = 2, y = 2. Returns None when the strip is not there or not readable (scaled or compressed picture)."""
from PIL import Image


def read(path_or_image):
    im = path_or_image if isinstance(path_or_image, Image.Image) else Image.open(path_or_image)
    im = im.convert('RGB')
    if im.width < 160 or im.height < 12:
        return None
    px = lambda k: im.getpixel((6 + 8 * k, 6))
    r, g = px(0), px(17)
    if not (r[0] > 180 and r[1] < 80 and r[2] < 80 and g[1] > 180 and g[0] < 80 and g[2] < 80):
        return None
    value = 0
    for i in range(16):
        c = px(i + 1)
        lum = sum(c) / 3
        if 60 < lum < 190:
            return None
        if lum >= 190:
            value |= 1 << i
    return value
