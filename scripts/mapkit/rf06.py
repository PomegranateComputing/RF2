#!/usr/bin/env python3
"""RF06 - La sortie du personnel. Production map source (authored, not generated).

The corridor that should not fit in the building (novel l. 709-731; docs/production/maps/RF06_FICHE.md). Owner's
mandate of 01/10: more complex, at least five spatial moments and two side explorations, no combat (decided 01/10:
the text has none; the tension is sound, light and geometry). In the order of the text:

  1  the service door shut behind him, the waves (l. 705-707)
  2  the corridor of rooms: raw concrete, low ceiling, pipes painted white, the slope almost imperceptible; numbered
     doors, the numbers stencilled then crossed out, 117, 404, 017, in an order neither rising nor random (l. 709);
     the rumble of the train behind turning into the ventilation of a hotel (l. 713)
  3  a wider hall where the paint lifts like burnt skin over graffiti in five scripts (l. 713)
  4  the descent: the slope steepens, the air warms (l. 719)
  5  the junction of the voices: "Tu l'as vu ou ?" "Dans l'autre aile." "Il n'y a pas d'autre aile." A laugh; the beam
     of a lamp sweeps the wall ahead and is gone (l. 719-727)
  6  the two turns, the second not wide enough for the length walked; an opening cuts the day (l. 729)
ERREUR O every twenty or thirty metres (640-960 u), never twice the same (l. 715-717); the bare bulbs light ahead of
him and go out behind (l. 713, RFCorridor).

Side explorations (declared adaptation, no text added): door 404 ajar on an empty room (an iron bedstead without a
mattress, the number crossed out on the inside too); at the junction, a passage toward "the other wing" that ends at a
railing over a stairwell going down into the dark.

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
ROOM = replace(COR, ceil=104, light=36, wall='RF6_PEA2', env=(30, 8))
T_START, T_SIGNAL, T_SPOT, T_AMB, T_WP, T_LAMP, T_FLICKER = 1, 30623, 30637, 30611, 30902, 30601, 30602
C_PIECE = 600               # piece i of the corridor: its lamps have the tid 600 + i (RFCorridor lights them)
C_VOICES, C_BEAM, C_RUMBLE, C_DAY, C_ERREUR, C_PAINT = 1, 2, 3, 4, 5, 6
SIGNAL_TID = 999
BEAM_TID = 690
W = 96                      # the corridor's width
PIECE = 128

m = MapBuilder('RF06')


def sign(x0, y0, x1, y1, tex, zbottom, off=1, **flags):
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=4, texwidth=L, **flags)


pieces = []                 # (x0, y0, x1, y1, floor)


def across(x0, y, x1, y_, scene):
    """A walk line of a scene across the corridor, one line per sector it crosses (pipes make their own)."""
    assert y == y_ and y % UNIT == 8, y
    runs, cur, start = [], None, None
    for k in range(x0 // UNIT, x1 // UNIT):
        c = m.cell_at(k * UNIT + 8, y)
        if c != cur:
            if cur is not None:
                runs.append((start, k * UNIT))
            cur, start = c, k * UNIT
    runs.append((start, x1))
    for (s, e) in runs:
        if m.cell_at(s + 8, y) is not None:
            m.trigger(s, y, e, y, 130, (SIGNAL_TID,), fields={'user_scene': scene})


def piece(x0, y0, x1, y1, floor, extra=0, wall='RF6_BETN', light=40):
    i = len(pieces)
    pieces.append((x0, y0, x1, y1, floor))
    m.box(x0, y0, x1, y1, COR, floor=floor, ceil=floor + 88 + extra, wall=wall, light=light,
          extra=(('user_piece', i + 1),))                         # RFCorridor reads it (the tags are the slabs')
    return i


def pipes(x0, y0, x1, y1, z):
    """Pipes painted white under the ceiling (l. 709): a slab along a wall."""
    m.slab(x0, y0, x1, y1, z, z + 8, 'RFP_PLN', top='RFP_PLN', bottom='RFP_PLN')


# ---------------------------------------------------------------- 1. the service door shut behind him
m.box(0, 0, W, 64, COR, light=110)
m.face(16, 0, 80, 16, 'S', texture='RFD_SGL')
m.thing(48, 24, T_START, angle=90)
m.thing(70, 20, T_SIGNAL, tid=SIGNAL_TID)
m.thing(48, 40, T_AMB, args=(9, 60))                                   # waves behind the door (kind 9)

# ---------------------------------------------------------------- 2. the corridor of rooms (north, 8 pieces)
floor = 0
room_doors = []                                                        # (x wall, y0, side) for the numbered doors
for k in range(8):
    if k % 2 == 1:
        floor -= 8                                                     # the slope, almost imperceptible
    i = piece(0, 64 + k * PIECE, W, 64 + (k + 1) * PIECE, floor, wall='RF6_PEAU' if k in (3, 6) else 'RF6_BETN')
    pipes(W - 16, 64 + k * PIECE, W, 64 + (k + 1) * PIECE, floor + 72)
    room_doors.append((0, 64 + k * PIECE + 32, 'W', floor))
    if k != 4:
        room_doors.append((W, 64 + k * PIECE + 64, 'E', floor))
order = ['117', '404', '017', '117', '017', '404', '404', '117', '017', '117', '404', '017', '117', '017', '404']
for n, (xw, y, side, f) in enumerate(room_doors):                      # doors shut, their numbers crossed out
    if side == 'W':
        m.face(xw, y, xw + 16, y + 48, 'W', texture='RFD_SGL')
        sign(xw, y, xw, y + 48, f'RF6_N{order[n % len(order)]}', f + 52)           # stencilled across the door (48 u)
    else:
        m.face(xw - 16, y, xw, y + 48, 'E', texture='RFD_SGL')
        sign(xw, y + 48, xw, y, f'RF6_N{order[n % len(order)]}', f + 52)
across(0, 584, W, 584, C_RUMBLE)                                       # the train becomes a hotel's air
m.thing(48, 900, T_AMB, args=(10, 70))                                 # the ventilation of a hotel (kind 10)

# side exploration A: door 404 ajar (piece 4, east wall), an empty room
y404 = 64 + 4 * PIECE
m.box(W, y404 + 32, W + 16, y404 + 80, COR, floor=pieces[4][4], ceil=pieces[4][4] + 80, light=34)   # the doorway
m.box(W + 16, y404 - 16, W + 160, y404 + 128, ROOM, floor=pieces[4][4], ceil=pieces[4][4] + 104)
m.raise_block(W + 80, y404 + 48, W + 144, y404 + 112, 16, 'RFF_WOOD', 'RF4_ATEL')                 # the iron bedstead
sign(W, y404 + 80, W, y404 + 32, 'RF6_N404', pieces[4][4] + 62)                                   # 404, crossed out, by its door
m.thing(W + 88, y404 + 24, T_FLICKER, args=(150, 140, 120, 90, 40), z=80)

# ---------------------------------------------------------------- 3. the hall of skins (graffiti under lifting paint)
hall_y0, hall_y1 = 64 + 8 * PIECE, 64 + 8 * PIECE + 192
floor -= 8
hall = piece(-48, hall_y0, W + 48, hall_y1, floor, extra=40, wall='RF6_PEAU', light=46)
for (x, y) in ((-16, hall_y0 + 48), (W + 0, hall_y0 + 48), (-16, hall_y0 + 128), (W + 0, hall_y0 + 128)):
    m.carve(x, y, x + 16, y + 16)
pipes(-48, hall_y0, W + 48, hall_y0 + 16, floor + 112)
pipes(-48, hall_y1 - 16, W + 48, hall_y1, floor + 112)
for (x0, y0, x1, y1) in ((-48, hall_y0 + 32, -48, hall_y0 + 80), (-48, hall_y0 + 112, -48, hall_y0 + 160)):
    m.face(-48, y0, -32, y1, 'W', texture='RF6_PEA2')                  # the skins lifted off a second layer
across(-48, hall_y0 + 40, W + 48, hall_y0 + 40, C_PAINT)

# ---------------------------------------------------------------- 4. the descent (the slope steepens, warmer)
y = hall_y1
for k in range(7):
    floor -= 16
    piece(0, y, W, y + PIECE, floor, wall='RF6_PEA2' if k in (2, 5) else 'RF6_BETN', light=44 + 2 * k)
    pipes(0, y, 16, y + PIECE, floor + 72)
    y += PIECE
descent_end = y

# ---------------------------------------------------------------- 5. the junction of the voices
j_y0, j_y1 = descent_end, descent_end + W
jun = piece(0, j_y0, W, j_y1, floor, light=52)
across(0, j_y0 - 40, W, j_y0 - 40, C_VOICES)
# side exploration B: the passage toward "the other wing", a railing over a stairwell going down into the dark
m.box(-384, j_y0 + 16, 0, j_y1 - 16, COR, floor=floor, ceil=floor + 88, light=34, wall='RF6_BETN')
m.box(-544, j_y0 - 96, -384, j_y1 + 96, COR, floor=floor - 448, ceil=floor + 160, light=24, wall='RF6_BETN')
for k in range(6):                                                    # the stair down along the well's walls
    m.box(-544, j_y1 + 96 - 32 * (k + 1), -512, j_y1 + 96 - 32 * k, COR, floor=floor - 64 * (k + 1), ceil=floor + 160, light=24)
m.box(-400, j_y0 + 16, -384, j_y1 - 16, COR, floor=floor, ceil=floor + 88, light=30)              # the landing's edge
m.decor_line(-399, j_y0 + 18, -399, j_y1 - 18, 'RF2_RAMB', floor, blocking=True, yscale=4)       # the railing
m.thing(-464, j_y0 + 48, T_AMB, args=(10, 50))
m.thing(-200, j_y0 + 48, T_FLICKER, args=(150, 140, 120, 80, 30), z=70)

# ---------------------------------------------------------------- 6. the two turns, the day
y = j_y0
x = W
for k in range(5):                                                    # first turn: east
    floor -= 8
    piece(x, y, x + PIECE, y + W, floor, wall='RF6_PEAU' if k == 2 else 'RF6_BETN', light=48)
    pipes(x, y + W - 16, x + PIECE, y + W, floor + 72)
    x += PIECE
east_end = x
turn2 = piece(east_end, y, east_end + W, y + W, floor, light=52)        # the second turn
yy = y
for k in range(4):                                                    # south again, toward the day
    floor -= 8
    piece(east_end, yy - PIECE, east_end + W, yy, floor, light=56 + 8 * k)
    yy -= PIECE
end_floor = floor
m.box(east_end, yy - 32, east_end + W, yy, COR, floor=end_floor, ceil=end_floor + 96, light=200, wall='RF6_BETS')
m.face(east_end, yy - 32, east_end + W, yy - 16, 'S', texture='RF6_JOUR')
m.trigger(east_end + 2, yy - 8, east_end + W - 2, yy - 8, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(x0 // UNIT, (yy - 24) // UNIT) for x0 in range(east_end, east_end + W, 16)}
# the beam of a lamp ahead, sweeping across the east stretch (l. 727)
m.thing(east_end - 192, j_y0 + W - 4, T_LAMP, args=(240, 236, 220, 72), z=48, tid=BEAM_TID, dormant=True)

# ERREUR O every twenty or thirty metres, never the same (l. 715-717): five along the way, 640-960 u apart
for (k, x0, y0, x1, y1) in ((1, W, 64 + 2 * PIECE + 96, W, 64 + 2 * PIECE + 32),                   # rooms: east wall
                            (2, -48, hall_y0 + 104, -48, hall_y0 + 168),                         # the hall: west wall
                            (3, W, hall_y1 + 4 * PIECE + 96, W, hall_y1 + 4 * PIECE + 32),       # the descent
                            (5, W + 3 * PIECE + 96, j_y0, W + 3 * PIECE + 32, j_y0),             # first turn: south wall
                            (4, east_end, yy + 2 * PIECE + 32, east_end, yy + 2 * PIECE + 96)):  # toward the day: west wall
    side = 1 if y1 > y0 else -1 if x0 == x1 else 0                    # the face is on the right of x0,y0 -> x1,y1
    ix = x0 + 8 * side if x0 == x1 else (x0 + x1) / 2
    iy = (y0 + y1) / 2 if x0 == x1 else y0 + (8 if x1 < x0 else -8)
    sign(x0, y0, x1, y1, f'RF6_ER{k}', m.cell_at(ix, iy).floor + 30)

# the bulbs: a lamp per piece, lit ahead and put out behind by RFCorridor (dormant lamps, tid = 600 + piece)
for i, (x0, y0, x1, y1, f) in enumerate(pieces):
    m.thing((x0 + x1) / 2, (y0 + y1) / 2, T_LAMP, args=(140, 132, 110, 150), z=80, tid=C_PIECE + i, dormant=True)
m.label(4, 70, 'RF06 COULOIR')

route = [(48, 100, 0, 0, 1, 90),
         (48, y404 + 56, 0, 0, 0, 0), (W + 60, y404 + 56, 0, 60, 0, 0), (48, y404 + 56, 0, 0, 0, 0),   # room 404
         (48, hall_y0 + 96, 0, 120, 0, 0),                                                           # the skins
         (48, j_y0 + 48, 0, 0, 0, 0),
         (-360, j_y0 + 48, 0, 120, 0, 180), (48, j_y0 + 48, 0, 0, 0, 0),                             # the other wing
         (east_end + 48, j_y0 + 48, 0, 0, 0, 0),
         (east_end + 48, yy + 40, 0, 0, 0, 270), (east_end + 48, yy - 24, 0, 0, 0, 270)]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF06.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF06_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF06_plan.png', scale=0.5)
    report = m.check({}, m.exit_cells, decor_types=(T_SPOT, T_LAMP, T_FLICKER))
    length = sum(max(x1 - x0, y1 - y0) for (x0, y0, x1, y1, f) in pieces)
    print('RF06 built:', m.stats, 'pieces:', len(pieces), 'length:', length, 'floor at the end:', end_floor)
    print('check:', {k: v for k, v in report.items() if k != 'unreachable_things'})
    if report['unreachable_things']:
        print('UNREACHABLE THINGS:', report['unreachable_things'])
    from encounters import analyze
    problems = analyze(m, spawn_view=True)
    print('encounters/walls:', 'clean' if not problems else f'{len(problems)} problem(s)')
    for line in problems:
        print('  ' + line)
    return report


if __name__ == '__main__':
    main()
