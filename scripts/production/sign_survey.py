#!/usr/bin/env python3
"""Survey of the signs of any map script (decor lines drawn at a height: yscale= given), against the map geometry.
The map script is run in memory up to its main() (nothing is written). For each sign: distance to what holds it
behind (wall, upper wall at or below its lower edge, raised block or roofline whose top is at or above its upper
edge, door that opens below it), open space in front over its height,
and whether the whole texture is shown on the line (line length compared with the texture width in map units read
from src/TEXTURES.*; decor lines are 2 units shorter at each end than asked, texwidth= fits the texture on them).

Held: support at most 1.5 units behind over the whole length. Readable: open cell in front, floor below the lower
edge, ceiling above the upper edge. Whole: texwidth given, or line at least as long as the texture.

Usage: python scripts/production/sign_survey.py scripts/mapkit/rf02.py      (exit code 1 if a sign fails)
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
path = Path(sys.argv[1])
src = path.read_text(encoding='utf-8')
ns = {'__file__': str(path.resolve()), '__name__': 'sign_survey'}
exec(compile(re.sub(r"\nif __name__ == '__main__':\n(    .*\n?)+", '\n', src), str(path), 'exec'), ns)
m = ns['m']
import udmf

TEX = {}                                             # name -> (width, height) in map units
for tf in sorted(f for f in (ROOT / 'src').glob('TEXTURES*') if f.is_file()):
    for name, w, h, body in re.findall(r'Texture\s+"?(\w+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{([^}]*)\}', tf.read_text(encoding='utf-8', errors='replace'), re.I):
        xs = re.search(r'XScale\s+([\d.]+)', body, re.I)
        ys = re.search(r'YScale\s+([\d.]+)', body, re.I)
        TEX[name.upper()] = (int(w) / float(xs.group(1) if xs else 1), int(h) / float(ys.group(1) if ys else 1))


def open_height(p, c):
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


def support(x, y, zb, top):
    p = (int(x // udmf.UNIT), int(y // udmf.UNIT))
    c = m.cells.get(p)
    if c is None:
        return 'mur'
    if c.role == 'door':
        return 'porte' if open_height(p, c) <= zb else None
    if c.role == 'window':
        return 'fenetre' if c.floor >= zb + 16 or c.ceil <= zb else None
    if c.ceil <= zb:
        return 'linteau'
    if c.floor >= top:
        return 'massif'
    return None


rows, bad = 0, 0
print(f'{"texture":9} {"ligne":34} {"face":5} {"bas":>4} {"haut":>4}  {"derriere":>8}  {"devant":24} {"texture (u)":12} verdict')
for dl in m.decor:
    if dl.get('yscale') is None or not dl.get('tex') or dl.get('zbottom') is None or dl.get('blocking'):
        continue
    rows += 1
    x0, y0, x1, y1 = dl['x0'], dl['y0'], dl['x1'], dl['y1']
    L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = uy, -ux
    zb = dl['zbottom']
    tw, th = TEX.get(dl['tex'].upper(), (None, None))
    top = zb + (th or 16)
    # distance behind: smallest d (0.5 steps up to 32) where every sample along the line meets a support
    dist, kinds = None, set()
    for d2 in range(1, 65):
        d = d2 / 2
        ks = [support(x0 + ux * k - nx * d, y0 + uy * k - ny * d, zb, top) for k in [2 + i * 4 for i in range(int((L - 4) // 4) + 1)]]
        if all(ks):
            dist, kinds = d, set(ks)
            break
    fc = m.cell_at(x0 + ux * L / 2 + nx * 1.5, y0 + uy * L / 2 + ny * 1.5)
    front = 'mur' if fc is None else f'sol {fc.floor} plafond {fc.ceil}'
    readable = fc is not None and fc.role != 'door' and fc.floor < zb and fc.ceil >= top
    whole = bool(dl.get('texwidth')) or (tw is not None and L >= tw - 0.01)
    held = dist is not None and dist <= 1.5
    ok = held and readable and whole
    bad += not ok
    face = {(1, 0): 'est', (-1, 0): 'ouest', (0, 1): 'nord', (0, -1): 'sud'}.get((round(nx), round(ny)), f'{nx:.1f},{ny:.1f}')
    line = f'({x0:g},{y0:g})-({x1:g},{y1:g})'
    texs = f'{tw:g}x{th:g}' if tw else '?'
    why = [] if ok else [w for w, c in (('decolle', not held), ('devant', not readable), ('coupee', not whole)) if c]
    print(f'{dl["tex"]:9} {line:34} {face:5} {zb:4g} {top:4g}  {("-" if dist is None else f"{dist:g}"):>8}  {front:24} '
          f'{texs + (" L=%g" % L):12} {"OK" if ok else "NON " + ",".join(why)} {"/".join(sorted(kinds))}')
print(f'{rows} enseignes, {rows - bad} tenues, lisibles et entieres, {bad} en defaut')
sys.exit(1 if bad else 0)
