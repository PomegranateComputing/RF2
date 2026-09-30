#!/usr/bin/env python3
"""RF06 - La sortie du personnel. Production map source (authored, not generated).

The corridor that should not fit in the building (novel l. 709-731; docs/production/maps/RF06_FICHE.md): out of the
service door of the dance hall (RF05's exit), raw concrete, low ceiling, pipes painted white, a slope almost
imperceptible, salt on the walls; room numbers stencilled then crossed out (117, 404, 017, in an order neither rising nor
random); graffiti in several scripts under paint that lifts like burnt skin; ERREUR Ø every twenty or thirty metres,
never twice the same; bare bulbs that light ahead of him and go out behind; the roller-coaster's rumble turning into the
ventilation of a hotel; voices ahead and the beam of a lamp (the explorers of the Jerma, never hostile); two turns, the
second too narrow for the length walked: he should be back under the dance hall; instead, an opening cuts the day.

No combat (proposal (a) of the fiche: the text has none; the tension is sound, light and geometry).
Usage: python scripts/mapkit/rf06.py   (writes src/maps/RF06.wad, build/RF06_plan.png, build/RF06_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ENV = (13, 0)
COR = Cell(floor=0, ceil=88, ftex='RF6_SOL', ctex='RF6_PLAF', light=40, wall='RF6_BETN', color=0xE8ECEC, env=ENV)
T_START, T_SIGNAL, T_SPOT, T_AMB, T_WP = 1, 30623, 30637, 30611, 30902
C_PIECE = 600               # piece i of the corridor carries the sector tag 600 + i (RFCorridor lights it)
C_VOICES, C_BEAM, C_RUMBLE, C_DAY = 1, 2, 3, 4
SIGNAL_TID = 999
PIECE = 128

m = MapBuilder('RF06')


def sign(x0, y0, x1, y1, tex, zbottom, off=1, **flags):
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=4, texwidth=L, **flags)


# The corridor as pieces of 128: (x0, y0, x1, y1). North, then east, then back south.
pieces = []
for k in range(10):                                  # north: x 0..80
    pieces.append((0, 64 + k * PIECE, 80, 64 + (k + 1) * PIECE))
turn1 = (0, 1344, 80, 1424)
pieces.append(turn1)
for k in range(5):                                   # east: y 1344..1424
    pieces.append((80 + k * PIECE, 1344, 80 + (k + 1) * PIECE, 1424))
turn2 = (720, 1344, 800, 1424)
pieces.append(turn2)
for k in range(6):                                   # south again: x 720..800
    pieces.append((720, 1344 - (k + 1) * PIECE, 800, 1344 - k * PIECE))
floor = 0
for i, (x0, y0, x1, y1) in enumerate(pieces):
    if i % 2 == 0 and i > 0:
        floor -= 8                                   # the slope, almost imperceptible, then steeper (l. 719)
    if i > 17:
        floor -= 8
    wall = 'RF6_PEAU' if i in (3, 4, 9, 12, 13, 19) else ('RF6_PEA2' if i in (7, 15, 20) else 'RF6_BETN')
    m.box(x0, y0, x1, y1, COR, floor=floor, ceil=floor + 88, tag=C_PIECE + i, wall=wall)
LAST = len(pieces) - 1
end_floor = floor
# the start: the service door shut behind him
m.box(0, 0, 80, 64, COR, tag=C_PIECE + 99, light=120)
m.face(0, 0, 80, 16, 'S', texture='RFD_SGL')
m.thing(40, 24, T_START, angle=90)
m.thing(60, 20, T_SIGNAL, tid=SIGNAL_TID)
# the opening that cuts the day, at the end of the south stretch
x0, y0, x1, y1 = pieces[LAST]
m.box(720, y0 - 32, 800, y0, COR, floor=end_floor, ceil=end_floor + 96, light=200, tag=C_PIECE + 98, wall='RF6_BETS')
m.face(720, y0 - 32, 800, y0 - 16, 'S', texture='RF6_JOUR')
m.trigger(722, y0 - 8, 798, y0 - 8, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(x // UNIT, (y0 - 24) // UNIT) for x in range(720, 800, 16)}

# stencilled numbers, crossed out: 117, 404, 017, in an order neither rising nor random (l. 709)
order = ['117', '404', '017', '117', '017', '404', '404', '117', '017', '117']
stencil_pieces = [1, 2, 4, 6, 8, 12, 14, 18, 20, 21]
for num, i in zip(order, stencil_pieces):
    x0, y0, x1, y1 = pieces[i]
    f = m.cells[(x0 // UNIT, y0 // UNIT)].floor
    if x1 - x0 == 80:                               # north or south stretch: on the west wall
        sign(x0, y0 + 40, x0, y0 + 88, f'RF6_N{num}', f + 40)
    else:                                           # east stretch: on the north wall
        sign(x0 + 40, y1, x0 + 88, y1, f'RF6_N{num}', f + 40)
# ERREUR Ø every twenty or thirty metres, never the same (l. 715-717)
for (i, k) in ((2, 1), (7, 2), (12, 3), (18, 4), (21, 5)):          # never on the two turns (80 long)
    x0, y0, x1, y1 = pieces[i]
    f = m.cells[(x0 // UNIT, y0 // UNIT)].floor
    if x1 - x0 == 80:
        sign(x1, y0 + 96, x1, y0 + 32, f'RF6_ER{k}', f + 30)      # east wall, facing west
    else:
        sign(x0 + 96, y0, x0 + 32, y0, f'RF6_ER{k}', f + 30)      # south wall, facing north

# the bulbs: a lamp per piece, lit ahead and put out behind by RFCorridor (dormant lamps, tid = 600 + piece)
for i, (x0, y0, x1, y1) in enumerate(pieces):
    f = m.cells[(x0 // UNIT, y0 // UNIT)].floor
    m.thing((x0 + x1) / 2, (y0 + y1) / 2, 30601, args=(140, 132, 110, 150), z=80, tid=C_PIECE + i, dormant=True)
# sounds: waves behind the door, the rumble that becomes a hotel's ventilation, voices ahead
m.thing(40, 40, T_AMB, args=(9, 60))                 # waves (RFAmbientLoop kind 9)
m.thing(760, 1100, T_AMB, args=(10, 70))             # ventilation of a hotel (kind 10)
m.trigger(2, 520, 78, 520, 130, (SIGNAL_TID,), fields={'user_scene': C_RUMBLE})
x0, y0, x1, y1 = pieces[19]
m.trigger(722, y1 - 40, 798, y1 - 40, 130, (SIGNAL_TID,), fields={'user_scene': C_VOICES})
m.thing(760, y0 + 60, 30601, args=(240, 236, 220, 72), z=48, tid=690, dormant=True)     # the beam of a lamp (l. 727)
C_ERREUR, C_PAINT = 5, 6
m.trigger(2, pieces[2][1] + 40, 78, pieces[2][1] + 40, 130, (SIGNAL_TID,), fields={'user_scene': C_ERREUR})
m.trigger(2, pieces[3][1] + 40, 78, pieces[3][1] + 40, 130, (SIGNAL_TID,), fields={'user_scene': C_PAINT})
m.label(4, 70, 'RF06 COULOIR')

route = [(40, 100, 0, 0, 1, 90), (40, 1380, 0, 0, 0, 0), (760, 1384, 0, 0, 0, 0), (760, pieces[19][3] - 60, 0, 200, 0, 270),
         (760, pieces[LAST][1] - 20, 0, 0, 0, 270)]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF06.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF06_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF06_plan.png', scale=0.5)
    report = m.check({}, m.exit_cells, decor_types=(T_SPOT, 30601))
    print('RF06 built:', m.stats, 'pieces:', len(pieces), 'floor at the end:', end_floor)
    print('check:', {k: v for k, v in report.items() if k != 'unreachable_things'})
    if report['unreachable_things']:
        print('UNREACHABLE THINGS:', report['unreachable_things'])
    return report


if __name__ == '__main__':
    main()
