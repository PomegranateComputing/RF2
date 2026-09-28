#!/usr/bin/env python3
"""The 13 wall plaques of RF01 as the map script places them (scripts/mapkit/rf01.py rebuilt in memory, nothing is
written): one front view and one oblique view (45 degrees) each, for scripts/production/view_check_pk3.py.
Each camera stands in front of the plaque it looks at, on the side the plaque faces, at eye height (41 units) on the
floor of the room the plaque faces, and moves back from the plaque (up to 208 units, 136 for the oblique view) only
across open cells at that floor level (no wall, no door, no furniture, 16 units of clearance on each side): it never
sees the plaque through a wall and never stands against one.
The same list is used on the accepted build (plaques under the floor) and on the candidate.

Usage: python scripts/production/rf01_sign_views.py views.json [rf01.py]
"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'scripts' / 'mapkit' / 'rf01.py'
src = path.read_text(encoding='utf-8')
ns = {'__file__': str(path), '__name__': 'rf01_views'}
exec(compile(src.replace("if __name__ == '__main__':\n    main()", ''), 'rf01_views', 'exec'), ns)
m = ns['m']
TEXTS = ['ADMISSIONS', 'CONSULTATIONS', 'PAVILLON_EST', 'LINGERIE', 'REGISTRES', 'CHAPELLE', 'SORTIE',
         'LOGE_DU_PORTIER', 'PAVILLON_OUEST', 'GALERIE_NORD']
EYE = 41
views = []
n = 0
for dl in m.decor:
    if not str(dl['tex']).startswith('RFSIGN'):
        continue
    n += 1
    x0, y0, x1, y1 = dl['x0'], dl['y0'], dl['x1'], dl['y1']
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L, -(x1 - x0) / L          # front side = right of v1 -> v2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    zc = dl['zbottom'] + 8
    f0 = m.cell_at(cx + nx * 4, cy + ny * 4).floor
    for kind, dist, turn in (('face', 208, 0), ('biais', 136, 45)):
        a = math.radians(turn)
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
        d = max(ok - 12, 16)                        # keep the camera clear of whatever stopped it
        px, py = cx + dx * d, cy + dy * d
        floor = m.cell_at(px, py).floor
        yaw = math.degrees(math.atan2(cy - py, cx - px)) % 360
        pitch = -math.degrees(math.atan2(zc - (floor + EYE), d))
        label = f'{n:02d}_{dl["tex"]}_{TEXTS[int(dl["tex"][-1])]}_{kind}_d{d}'
        views.append([label, round(px, 1), round(py, 1), 0, round(yaw, 1), round(pitch, 1)])
json.dump(views, open(sys.argv[1], 'w', encoding='utf-8'), indent=1)
print(len(views), 'views')
