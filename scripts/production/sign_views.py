#!/usr/bin/env python3
"""Engine views of the signs of any map script (decor lines drawn at a height, yscale= given, blocking rails left
out), for scripts/production/view_check_pk3.py. The map script is run in memory up to its main() (nothing is
written). Per sign: a front view, an oblique view (45 degrees) and a grazing view (75 degrees, which shows the gap
between a sign and its wall). Each camera stands on the side the sign faces, at eye height (41 units) on the floor in
front of the sign, and moves back only across open cells at that floor level (no wall, no door, no raised block,
16 units of clearance on each side): it never sees the sign through a wall.

Usage: python scripts/production/sign_views.py <map script> views.json [TEX1,TEX2,...] [face,biais,rasant]
"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
path = Path(sys.argv[1])
src = path.read_text(encoding='utf-8')
ns = {'__file__': str(path.resolve()), '__name__': 'sign_views'}
exec(compile(re.sub(r"\nif __name__ == '__main__':\n(    .*\n?)+", '\n', src), str(path), 'exec'), ns)
m = ns['m']
only = set(sys.argv[3].split(',')) if len(sys.argv) > 3 and sys.argv[3] else None
kinds = sys.argv[4].split(',') if len(sys.argv) > 4 else ['face', 'biais', 'rasant']
SETUP = {'face': (208, 0), 'biais': (136, 45), 'rasant': (136, 75)}
EYE = 41
views, n = [], 0
for dl in m.decor:
    if dl.get('yscale') is None or not dl.get('tex') or dl.get('zbottom') is None or dl.get('blocking'):
        continue
    n += 1
    if only and dl['tex'] not in only:
        continue
    x0, y0, x1, y1 = dl['x0'], dl['y0'], dl['x1'], dl['y1']
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L, -(x1 - x0) / L          # front side = right of v1 -> v2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    zc = dl['zbottom'] + 8
    fc = m.cell_at(cx + nx * 4, cy + ny * 4)
    if fc is None:
        continue
    f0 = fc.floor
    for kind in kinds:
        dist, turn = SETUP[kind]
        for sgn in ((1,) if turn == 0 else (1, -1)):
            a = math.radians(turn * sgn)
            dx, dy = nx * math.cos(a) - ny * math.sin(a), nx * math.sin(a) + ny * math.cos(a)

            def clear(px, py):
                c = m.cell_at(px, py)
                return c is not None and c.role != 'door' and c.ceil - c.floor >= 56 and abs(c.floor - f0) <= 24
            d, ok = 4, 0
            while d <= dist:
                px, py = cx + dx * d, cy + dy * d
                if not clear(px, py):
                    break
                if d >= 16 and all(clear(px + e * dy * 16, py - e * dx * 16) for e in (1, -1)):
                    ok = d
                d += 4
            if ok < 24:
                continue                                # no room on that side
            d = max(ok - 12, 16)
            px, py = cx + dx * d, cy + dy * d
            floor = m.cell_at(px, py).floor
            yaw = math.degrees(math.atan2(cy - py, cx - px)) % 360
            pitch = -math.degrees(math.atan2(zc - (floor + EYE), d))
            side = '' if turn == 0 else ('g' if sgn > 0 else 'd')
            views.append([f'{n:02d}_{dl["tex"]}_{kind}{side}_d{d}', round(px, 1), round(py, 1), 0, round(yaw, 1), round(pitch, 1)])
            break                                       # one side is enough for an oblique/grazing view
json.dump(views, open(sys.argv[2], 'w', encoding='utf-8'), indent=1)
print(len(views), 'views')
