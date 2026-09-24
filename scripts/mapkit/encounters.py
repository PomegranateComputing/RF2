#!/usr/bin/env python3
"""Encounter sight check for mapkit maps.

For every enemy that waits for a cue (a thing flagged dormant with a tid, woken by a
Thing_Activate line or pickup), find the first point of the player route (RFDevWaypoint order)
from which the enemy is in plain sight BEFORE the route reaches its cue. A waiting enemy that is
visible early stands idle in view and invites a pre-emptive shot, which spoils the encounter.

Sight is a 2D ray over the 16-unit cell grid: missing cells (walls) block it, doors block it until
the route has passed through them (then they count as open), windows and furniture do not.
Distance limit 1000 units.

Usage: python scripts/mapkit/encounters.py [rf01]
Also reports wall leaks (see-through ledges between two rooms that are not doors, windows,
furniture or open-sky terraces), actors embedded in walls/doors/furniture, and Decal things
without a plain wall behind them.
"""
import importlib.util, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from udmf import UNIT, DIRS, STEP  # noqa: E402

T_WP = 30902
ENEMIES = {30401: 'Orderly', 30402: 'Brancardier', 30403: 'Porte-Registre'}
RADIUS = {1: 16, 30401: 18, 30402: 40, 30403: 22}
SPOT, SPOT_RADIUS = 30405, {1: 18, 2: 40, 3: 22}   # RFWaveSpot: radius of what it spawns


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.m


def sees(m, a, b, limit=1000.0, open_tags=()):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist > limit:
        return False
    steps = max(1, int(dist / 4))
    for k in range(1, steps):
        x = x0 + dx * k / steps
        y = y0 + dy * k / steps
        c = m.cells.get((math.floor(x / UNIT), math.floor(y / UNIT)))
        if c is None or (c.role == 'door' and c.tag not in open_tags):
            return False
    return True


def segments_cross(p1, p2, q1, q2):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(q1, q2, p1), orient(q1, q2, p2)
    d3, d4 = orient(p1, p2, q1), orient(p1, p2, q2)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)


def route_points(m):
    wps = sorted((t for t in m.things if t['type'] == T_WP), key=lambda t: t.get('arg0', 0))
    pts = [m.start] + [(t['x'], t['y']) for t in wps]
    samples = []   # (segment index, x, y)
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 16))
        for k in range(n):
            samples.append((i, x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    return pts, samples


def doors_opened(m, samples):
    """Door tag -> first route segment whose samples pass through that door (it is open then)."""
    opened = {}
    for (i, x, y) in samples:
        c = m.cells.get((math.floor(x / UNIT), math.floor(y / UNIT)))
        if c is not None and c.role == 'door' and c.tag not in opened:
            opened[c.tag] = i
    return opened


def cue_segment(m, pts, tid):
    """Index of the first route segment that crosses a wake line of `tid` or touches a pickup cueing it."""
    for i in range(len(pts) - 1):
        for dl in m.decor:
            if dl.get('special') == 130 and dl.get('args', [0])[0] == tid:
                if segments_cross(pts[i], pts[i + 1], (dl['x0'], dl['y0']), (dl['x1'], dl['y1'])):
                    return i
        for t in m.things:
            if t.get('special') == 130 and t.get('arg0') == tid:
                if math.hypot(pts[i + 1][0] - t['x'], pts[i + 1][1] - t['y']) < 48:
                    return i
    return None


def leaks(m):
    sectors, sector_of = m._sectors()
    found = {}
    for p, c in m.cells.items():
        for d, (dx, dy) in DIRS.items():
            q = (p[0] + dx, p[1] + dy)
            cq = m.cells.get(q)
            if cq is None or sector_of[p] >= sector_of[q] or c.role != 'floor' or cq.role != 'floor':
                continue
            if abs(c.floor - cq.floor) <= STEP or min(c.ceil, cq.ceil) - max(c.floor, cq.floor) < 56:
                continue
            if c.wall == cq.wall and c.ctex == cq.ctex:
                continue   # same room: furniture, dais, basin, stair
            if c.ctex == 'F_SKY1' and cq.ctex == 'F_SKY1':
                continue   # outdoor ledge under open sky (enclosure wall top, kerb, terrace)
            found.setdefault((sector_of[p], sector_of[q]), []).append(p)
    return [(min(x for x, _ in ps) * UNIT, min(y for _, y in ps) * UNIT, max(x for x, _ in ps) * UNIT + UNIT,
             max(y for _, y in ps) * UNIT + UNIT, len(ps)) for ps in found.values()]


def embedded(m):
    """Player start, enemies and wave spots whose collision box overlaps a wall, a door or a
    raised block (furniture) — such actors cannot move or pop out of the geometry."""
    out = []
    for t in m.things:
        r = RADIUS.get(t['type']) or (SPOT_RADIUS.get(t.get('arg0', 1)) if t['type'] == SPOT else None)
        if r is None:
            continue
        home = m.cell_at(t['x'], t['y'])
        bad = home is None
        for x in range(math.floor((t['x'] - r + 0.5) / UNIT), math.floor((t['x'] + r - 0.5) / UNIT) + 1):
            for y in range(math.floor((t['y'] - r + 0.5) / UNIT), math.floor((t['y'] + r - 0.5) / UNIT) + 1):
                c = m.cells.get((x, y))
                if c is None or c.role != 'floor' or (home is not None and c.floor - home.floor > STEP):
                    bad = True
        if bad:
            out.append(t)
    return out


def door_problems(m):
    """A door leaf must sit in a wall: both ends of its long axis against solid cells. A leaf whose
    ends touch floor protrudes into a room or corridor (usable from its sides, odd to look at)."""
    by_tag = {}
    for p, c in m.cells.items():
        if c.role == 'door':
            by_tag.setdefault(c.tag, []).append(p)
    out = []
    for tag, cells in sorted(by_tag.items()):
        xs = [p[0] for p in cells]
        ys = [p[1] for p in cells]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if x1 - x0 >= y1 - y0:      # leaf along X: its ends are west of x0 and east of x1
            ends = [(x0 - 1, y) for y in range(y0, y1 + 1)] + [(x1 + 1, y) for y in range(y0, y1 + 1)]
        else:
            ends = [(x, y0 - 1) for x in range(x0, x1 + 1)] + [(x, y1 + 1) for x in range(x0, x1 + 1)]
        open_ends = [e for e in ends if e in m.cells and m.cells[e].role != 'door']
        if open_ends:
            out.append(f'DOOR END       tag {tag} at x {x0 * UNIT}..{(x1 + 1) * UNIT} y {y0 * UNIT}..{(y1 + 1) * UNIT}: '
                       f'leaf ends touch floor ({len(open_ends)} cells) - it protrudes out of the wall')
    return out


def decal_problems(m):
    """Decal things (9200) must have a plain wall within 64 units behind them (engine rule)."""
    out = []
    for t in m.things:
        if t['type'] != 9200:
            continue
        a = math.radians(t['angle'] + 180)
        hit = None
        for k in range(1, 65):
            c = m.cells.get((math.floor((t['x'] + math.cos(a) * k) / UNIT), math.floor((t['y'] + math.sin(a) * k) / UNIT)))
            if c is None or c.role in ('door', 'window'):
                hit = 'wall' if c is None else c.role
                break
        if hit != 'wall':
            out.append(f"DECAL          at ({t['x']:.0f},{t['y']:.0f}) angle {t['angle']}: {hit or 'no wall within 64 units'} behind it")
    return out


def analyze(m):
    """All problems of a built MapBuilder as printable lines (empty list = clean)."""
    pts, samples = route_points(m)
    opened = doors_opened(m, samples)
    problems = []
    for t in m.things:
        if t['type'] not in ENEMIES or not t.get('dormant') or not t.get('id'):
            continue
        tid = t['id']
        cue = cue_segment(m, pts, tid)
        seen = next(((i, x, y) for (i, x, y) in samples if (cue is None or i < cue) and
                     sees(m, (x, y), (t['x'], t['y']), open_tags={tag for tag, j in opened.items() if j <= i})), None)
        if seen:
            problems.append(f"VISIBLE EARLY  {ENEMIES[t['type']]:14} tid={tid:3} at ({t['x']:.0f},{t['y']:.0f}) "
                            f"seen from route segment {seen[0] + 1} ({seen[1]:.0f},{seen[2]:.0f}); cue at segment "
                            f"{'never' if cue is None else cue + 1}")
    for t in embedded(m):
        problems.append(f"EMBEDDED       type={t['type']} tid={t.get('id', 0)} at ({t['x']:.0f},{t['y']:.0f}): "
                        "box overlaps a wall, door or furniture")
    for (x0, y0, x1, y1, n) in leaks(m):
        problems.append(f'WALL LEAK      x {x0}..{x1} y {y0}..{y1} ({n} cells): see-through ledge between two rooms')
    problems += door_problems(m)
    problems += decal_problems(m)
    return problems


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else 'rf01'
    m = load(name)
    m.build()
    problems = analyze(m)
    for line in problems:
        print(line)
    print(f'{name}: {len(problems)} problem(s)')
    return len(problems)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
