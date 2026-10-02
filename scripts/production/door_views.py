#!/usr/bin/env python3
"""Views of every door-like surface of the audit (door_audit.py), at the player's height: one from the front and one
at an angle, taken from the side the surface is seen from. With --open, mechanisms are also shot open (Door_Open on
their tag, as view_check_pk3.py does) so that the jambs, the lintel and what the panel reveals can be judged.

Usage: python scripts/production/door_views.py <build.pk3> <out_dir> [--audit build/door_audit.json] [--maps RF01,RF02]
                                               [--only-defects] [--open] [--wads <dir of the build's maps>]
Writes <out_dir>/<MAP>/NN_<label>.png, the view lists and <out_dir>/index.json (label -> audit record).
The cameras are placed from the map geometry of --wads (default src/maps): use the maps the build was made from.
"""
import argparse, json, math, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import door_audit  # noqa: E402

EYE = 41.0


def inside_open(m, x, y):
    """Index of an open sector (56 units of headroom) containing the point, or None (even-odd rule on its lines)."""
    for s, lines in m.lines_of.items():
        sec = m.SE[s]
        if sec['heightceiling'] - sec['heightfloor'] < 56:
            continue
        n = 0
        for li in lines:
            l = m.L[li]
            if l.get('sideback', -1) >= 0 and m.S[l['sidefront']]['sector'] == m.S[l['sideback']]['sector']:
                continue
            (x0, y0), (x1, y1) = m.xy(l['v1']), m.xy(l['v2'])
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                n += 1
        if n % 2 == 1:
            return s
    return None


def camera(m, rec, turn):
    """Walk away from the surface (along its normal turned by `turn` degrees) while the point stays in an open sector
    whose floor is about the surface's foot: the camera stands on the floor the surface is seen from, with the
    surface in sight. Returns ([x, y, z above floor, angle, pitch], distance) or (None, 0)."""
    mx, my = rec['mid']
    nx, ny = rec['normal']
    a = math.radians(turn)
    dx, dy = nx * math.cos(a) - ny * math.sin(a), nx * math.sin(a) + ny * math.cos(a)
    want = min(max(rec['W'] * 1.1, rec['H'] * 1.25, 150.0), 420.0)
    best, d = None, 8.0
    while d <= want:
        x, y = mx + dx * d, my + dy * d
        s = inside_open(m, x, y)
        ok = s is not None and abs(m.SE[s]['heightfloor'] - rec['z0']) <= 40 if rec['part'] != 'bottom' else s is not None
        if ok:
            best = (d, x, y, m.SE[s]['heightfloor'])
        elif best is not None and d - best[0] > 24:
            break                                      # left the room: keep the last point inside it
        d += 8.0
    if best is None or best[0] < 40:
        return None, 0
    d, x, y, floor = best
    zc = rec['z0'] + min(rec['H'], 200) / 2.0
    pitch = -math.degrees(math.atan2(zc - (floor + EYE), d)) if d < rec['H'] * 1.2 else 0.0
    ang = math.degrees(math.atan2(-dy, -dx)) % 360
    return [round(x, 1), round(y, 1), 0, round(ang, 1), round(max(-45.0, min(30.0, pitch)), 1)], round(d)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pk3')
    ap.add_argument('out')
    ap.add_argument('--audit', default=str(ROOT / 'build' / 'door_audit.json'))
    ap.add_argument('--wads', default=str(ROOT / 'src' / 'maps'))
    ap.add_argument('--maps', default='')
    ap.add_argument('--only-defects', action='store_true')
    ap.add_argument('--open', action='store_true')
    ap.add_argument('--dry', action='store_true', help='write the view lists only')
    a = ap.parse_args()
    recs = json.loads(Path(a.audit).read_text(encoding='utf-8'))
    names = {n.strip().upper() for n in a.maps.split(',') if n.strip()}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    db = door_audit.texture_db()
    index = {}
    for mp in sorted({r['map'] for r in recs}):
        if names and mp not in names:
            continue
        wad = Path(a.wads) / f'{mp}.wad'
        m = door_audit.Map(mp, dict(door_audit.lumps(wad))['TEXTMAP'].decode('utf-8', 'replace'), db, {})
        views = []
        for r in recs:
            if r['map'] != mp or r['kind'] in ('track', 'polyobject') or r['H'] <= 0:
                continue
            if a.only_defects and not r['defects']:
                continue
            base = f"{r['kind'][0]}{r['sector']}_l{r['lines'][0]}{'b' if r.get('side') == 'back' else ''}_{r['part'][0]}_{r['tex']}_{r['W']:g}x{r['H']:g}"
            tag = 0
            if a.open and r['kind'] == 'mechanism':
                tag = m.SE[r['sector']].get('id', 0)
            for turn, suffix in ((0, 'face'), (40, 'biais')):
                cam, d = camera(m, r, turn)
                if cam is None:
                    continue
                label = f'{base}_{suffix}'
                views.append([label] + cam)
                index[f'{mp}/{label}'] = dict(r, camera=cam, distance=d)
                if tag and suffix == 'face':
                    views.append([f'{base}_ouverte'] + cam + [tag])
                    index[f'{mp}/{base}_ouverte'] = dict(r, camera=cam, distance=d, opened_tag=tag)
        if not views:
            continue
        vdir = out / mp
        vdir.mkdir(exist_ok=True)
        vjson = vdir / 'vues_demandees.json'
        vjson.write_text(json.dumps(views, indent=0) + '\n', encoding='utf-8')
        if a.dry:
            print(mp, len(views), 'vues')
            continue
        r = subprocess.run([sys.executable, str(HERE / 'capture_views.py'), a.pk3, mp, str(vjson), str(vdir), '--hide',
                            '--size', '1280x720', '--name', f'dv_{out.name}_{mp}'[:60]], cwd=ROOT, capture_output=True, text=True,
                           errors='replace')
        print((r.stdout + r.stderr).strip().splitlines()[-1], flush=True)
    (out / 'index.json').write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
