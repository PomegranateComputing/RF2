#!/usr/bin/env python3
"""Survey of the RF01 wall plaques against the map geometry (scripts/mapkit/rf01.py rebuilt in memory, nothing is
written). For each call to sign(): where the plaque line is, which way it faces, what stands 1 unit behind it and
1 unit in front of it over its whole length and height.

A plaque is held when, 1 unit behind it and from its lower to its upper edge, there is a wall (no cell), an upper
wall (a cell whose ceiling is at or below the lower edge: lintel, door frame) or a door whose open height (lowest
neighbouring ceiling - 4, Door_Open/Raise/LockedRaise) is at or below the lower edge. It is readable when, 1 unit in
front, there is an open cell (not a door) whose floor is below the lower edge and whose ceiling is above the upper
edge.

Usage: python scripts/production/rf01_sign_survey.py [rf01.py]      (exit code 1 if a plaque is not held/readable)
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'scripts' / 'mapkit' / 'rf01.py'
src = path.read_text(encoding='utf-8')
ns = {'__file__': str(path), '__name__': 'rf01_survey'}
exec(compile(src.replace("if __name__ == '__main__':\n    main()", ''), 'rf01_survey', 'exec'), ns)
m = ns['m']
import udmf

TEXTS = ['ADMISSIONS', 'CONSULTATIONS', 'PAVILLON EST', 'LINGERIE', 'REGISTRES', 'CHAPELLE', 'SORTIE',
         'LOGE DU PORTIER', 'PAVILLON OUEST', 'GALERIE NORD']      # materials.py, RFSIGN0..9
H = 16                                                              # plaque height (64 x 16 units)


def open_height(p, c):
    """Height a door cell opens to: lowest ceiling of the neighbouring non-door cells, minus 4."""
    seen, todo, ceils = {p}, [p], []
    while todo:
        q = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            r = (q[0] + dx, q[1] + dy)
            n = m.cells.get(r)
            if n is None or r in seen:
                continue
            if n.role == 'door' and n.tag == c.tag:
                seen.add(r)
                todo.append(r)
            else:
                ceils.append(n.ceil)
    return min(ceils) - 4


def behind(x, y, zb):
    p = (int(x // udmf.UNIT), int(y // udmf.UNIT))
    c = m.cells.get(p)
    if c is None:
        return True, 'mur'
    if c.role == 'door':
        h = open_height(p, c)
        return h <= zb, f'porte {c.tag} (ouverte a {h})'
    if c.ceil <= zb:
        return True, f'linteau (plafond {c.ceil})'
    return False, f'vide (sol {c.floor}, plafond {c.ceil})'


def front(x, y, zb):
    c = m.cell_at(x, y)
    if c is None:
        return False, 'mur'
    if c.role == 'door':
        return False, f'porte {c.tag}'
    ok = c.floor < zb and c.ceil >= zb + H
    return ok, f'sol {c.floor}, plafond {c.ceil}'


rows, bad = [], 0
for dl in m.decor:
    if not str(dl['tex']).startswith('RFSIGN'):
        continue
    x0, y0, x1, y1 = dl['x0'], dl['y0'], dl['x1'], dl['y1']
    L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = uy, -ux                                  # front side = right of v1 -> v2
    rows.append((dl, nx, ny, L, ux, uy))

# the sign() calls as written, in the same order as the decor lines they produce
calls = [(int(a), int(b), s, t, int(z or 92)) for a, b, s, t, z in
         re.findall(r"^sign\((-?\d+), (-?\d+), '([NSEW])', '(\w+)'(?:, (\d+))?\)", src, re.M)]
assert len(calls) == len(rows), (len(calls), len(rows))
assert all(dl['zbottom'] == c[4] for (dl, *_), c in zip(rows, calls))
FACING = {(1, 0): 'est', (-1, 0): 'ouest', (0, 1): 'nord', (0, -1): 'sud'}
print(f'{"#":>2} {"texture":8} {"texte":16} {"appel sign()":26} {"ligne":22} {"face":6} {"bas-haut":9} support / devant')
for i, ((dl, nx, ny, L, ux, uy), (x, y, s, t, zb)) in enumerate(zip(rows, calls), 1):
    held, readable, why_b, why_f = True, True, set(), set()
    for k in range(2, int(L) - 1, 4):
        px, py = dl['x0'] + ux * k, dl['y0'] + uy * k
        hb, wb = behind(px - nx * 1.5, py - ny * 1.5, zb)
        hf, wf = front(px + nx * 1.5, py + ny * 1.5, zb)
        held &= hb
        readable &= hf
        why_b.add(wb)
        why_f.add(wf)
    ok = held and readable
    bad += not ok
    face = FACING[(round(nx), round(ny))]
    line = f'({dl["x0"]},{dl["y0"]})-({dl["x1"]},{dl["y1"]})'
    txt = TEXTS[int(t[-1])]
    print(f'{i:2d} {t:8} {txt:16} {f"({x},{y},{s!r},{zb})":26} {line:22} {face:6} {zb}-{zb + H:<5} '
          f'{"OK" if ok else "NON"}  derriere: {"; ".join(sorted(why_b))}  |  devant: {"; ".join(sorted(why_f))}')
print(f'{len(rows)} plaques, {len(rows) - bad} tenues et lisibles, {bad} en defaut')
sys.exit(1 if bad else 0)
