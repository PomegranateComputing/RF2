#!/usr/bin/env python3
"""RF07 - Jerma, facade maritime. Production map source (authored, not generated).

Novel l. 733-765 (docs/production/maps/RF07_FICHE.md, RF07_RF12_DECOUPAGE.md), Malta, 22 December 2022, 14:58:

  A  The terrace covered with rubble; the sea over the whole horizon, hard, metallic; palms bending round an empty pool
     below (it is RF09's); the wings of concrete open on both sides, balconies without glass; NO FUTURE in blue (l. 733).
     Elvis waits by a broken bay window (l. 735). Behind Viktor no corridor any more: a gutted room, wet carpet, a
     bedframe overturned, ERREUR O at shoulder height, the black recent (l. 739-743).
  B  Across the terrace into the hotel: corridors of salt and wet plaster, graffiti that cover each other without
     erasing (l. 757); gutted rooms on the way.
  C  The service stair, crushed glass and ashes; on the landing a rusted bedframe across the door, lifted together
     (l. 761). "C'est la." (l. 763): exit, the room full of cold smoke (RF08).

No combat (owner's decision of 01/10 for the Jerma chapter). Elvis is a guide, never a target (src/zscript/rf/jerma.zs).
Resources: Opus's provisional stand-ins (scripts/mapkit/materials_rf07.py) until Codex's.
Usage: python scripts/mapkit/rf07.py   (writes src/maps/RF07.wad, build/RF07_plan.png, build/RF07_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT, texture_scales  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SKY = 512
OUT = Cell(floor=0, ceil=SKY, ftex='RF7_TERR', ctex='F_SKY1', light=184, wall='RF7_FACA', color=0xF0F0F4, env=(32, 0),
           lower='RF7_BETO')
DECK = replace(OUT, floor=-128, light=176)
POOL = replace(OUT, floor=-224, ftex='RF7_BETO', wall='RF7_BETO', lower='RF7_BETO', light=170)
SEAWALL = replace(OUT, floor=-96, ftex='RF7_BETO', lower='RF7_BETO')
SEA = replace(OUT, floor=-320, ftex='RF7_MER', light=176, lower='RF7_BETO')
HALL = Cell(floor=0, ceil=104, ftex='RF7_TERR', ctex='RF7_BETO', light=124, wall='RF7_GRAF', color=0xE8E4DC, env=(13, 0))
ROOM = replace(HALL, ceil=112, ftex='RF7_MOQU', light=116, wall='RF7_BETO', env=(30, 8))
STAIR = replace(HALL, ftex='RF7_VERR', light=100)

T_START, T_SIGNAL, T_SPOT, T_AMB, T_LAMP, T_WP, T_LITTER = 1, 30623, 30637, 30611, 30601, 30902, 30622
T_ELVIS, T_EPOINT, T_BED = 30700, 30701, 30702
J_BEHIND, J_HALLS, J_STAIR, J_BED = 1, 2, 3, 4
SIGNAL_TID = 999
AMB_WIND, AMB_WAVES = 1, 9

m = MapBuilder('RF07')
SCALES = {**texture_scales(ROOT / 'src' / 'TEXTURES.rf07'), **texture_scales(ROOT / 'src' / 'TEXTURES.rf06')}


def sign(x0, y0, x1, y1, tex, zbottom, off=1, **flags):
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=SCALES.get(tex, 4), texwidth=L, **flags)


def mass(x0, y0, x1, y1, top, side, base=OUT):
    """A closed building mass (floor and ceiling at its top, sky above): rooms carved in it draw no wall above it."""
    m.box(x0, y0, x1, y1, base, floor=top, ceil=top, ftex='RF7_BETO', lower=side, wall=side)


def opening(x0, y0, x1, y1, base, lintel, top, side):
    """A breach in a mass onto the open sky: capped at the mass's height, the lintel a slab (no wall above the mass)."""
    m.box(x0, y0, x1, y1, base, ceil=top, ctex='F_SKY1')
    m.slab(x0, y0, x1, y1, base.floor + lintel, top, side, top='RF7_BETO', bottom='RF7_BETO')


def walls(x0, y0, x1, y1, tex):
    """The ring of mass cells round a carved room shows the room's texture (a riser shows the higher cell's)."""
    room = m.cells[(x0 // UNIT, y0 // UNIT)]
    for cx in range(x0 // UNIT - 1, x1 // UNIT + 1):
        for cy in range(y0 // UNIT - 1, y1 // UNIT + 1):
            c = m.cells.get((cx, cy))
            if c is not None and (c.ceil <= c.floor or c.floor >= room.ceil) and c.role != 'door':
                m.cells[(cx, cy)] = replace(c, lower=tex)


def across(x0, y0, x1, y1, fields):
    horiz = y0 == y1
    fixed = y0 if horiz else x0
    assert fixed % UNIT == 8, fixed
    a, b = (min(x0, x1), max(x0, x1)) if horiz else (min(y0, y1), max(y0, y1))
    runs, cur, start = [], None, None
    for k in range(a // UNIT, b // UNIT):
        c = m.cell_at(k * UNIT + 8, fixed) if horiz else m.cell_at(fixed, k * UNIT + 8)
        if c != cur:
            if cur is not None:
                runs.append((start, k * UNIT))
            cur, start = c, k * UNIT
    runs.append((start, b))
    for (s, e) in runs:
        if horiz and m.cell_at(s + 8, fixed) is not None:
            m.trigger(s, fixed, e, fixed, 130, (SIGNAL_TID,), fields=fields)
        elif not horiz and m.cell_at(fixed, s + 8) is not None:
            m.trigger(fixed, s, fixed, e, 130, (SIGNAL_TID,), fields=fields)


# ============================================================================ A. THE TERRACE, THE SEA, THE GUTTED ROOM
mass(-512, -768, 2304, 0, 320, 'RF7_FACA')                       # the main building, behind the terrace
mass(-512, 0, 0, 1408, 320, 'RF7_FACA')                          # the west wing
mass(1536, 0, 2304, 1408, 320, 'RF7_FACA')                       # the east wing
m.box(0, 0, 1536, 512, OUT)                                      # the terrace
m.box(0, 512, 1536, 1408, DECK)                                  # the pool deck, below
m.box(448, 704, 1088, 1152, POOL)                                # the empty pool (RF09)
m.box(-512, 1408, 2304, 1472, SEAWALL)                           # the sea wall
m.box(-512, 1472, 2304, 3072, SEA)                               # the sea, to the horizon
for (x0, y0, x1, y1, side) in ((-512, 3056, 2304, 3072, 'N'), (-512, 1408, -496, 3072, 'W'), (2288, 1408, 2304, 3072, 'E')):
    m.face(x0, y0, x1, y1, side, special=9)                      # Line_Horizon: the sea and the sky meet far away
m.decor_line(0, 510, 1536, 510, 'RF4_BALU', 0, blocking=True, yscale=4)       # the terrace's parapet, moulded concrete
for (x, y) in ((384, 640), (1152, 640), (384, 1216), (1152, 1216), (768, 1296), (256, 960), (1280, 960)):
    m.slab(x, y, x + 16, y + 16, -128, 176, 'RF4_ATEL', top='RF4_ATEL', bottom='RF4_ATEL')        # palms (stand-ins)
    m.slab(x - 32, y - 32, x + 48, y + 48, 176, 184, 'RF4_HERB', top='RF4_HERB', bottom='RF4_HERB')
sign(0, 168, 0, 296, 'RF7_NOFU', 120, off=1)                     # NO FUTURE, blue, on the west wing (l. 733)
for (x0, y0, x1, y1, h) in ((96, 64, 192, 128, 24), (1184, 352, 1280, 448, 16), (400, 288, 464, 320, 32),
                            (1376, 96, 1440, 160, 24)):          # rubble
    m.raise_block(x0, y0, x1, y1, h, 'RF7_TERR', 'RF7_BETO', OUT)
# the gutted room behind him, where the corridor was (l. 739-743)
m.box(640, -192, 832, -16, ROOM)
walls(640, -192, 832, -16, 'RF7_BETO')
opening(672, -16, 800, 0, ROOM, 112, 320, 'RF7_FACA')
m.raise_block(704, -176, 816, -128, 16, 'RF7_MOQU', 'RF4_ATEL', ROOM)          # the overturned bedframe
sign(768, -192, 704, -192, 'RF6_ER5', 40, off=1)                # ERREUR O (64 u), at shoulder height, the black recent
m.thing(736, -110, T_SPOT, args=(J_BEHIND,), z=40)
m.thing(736, -60, T_LAMP, args=(150, 150, 156, 220), z=60)                    # the day through the breach
# the broken bay window where Elvis waits, and a dark lobby behind it
m.box(960, -128, 1088, -16, replace(ROOM, light=60))
walls(960, -128, 1088, -16, 'RF7_BETO')
opening(960, -16, 1088, 0, ROOM, 96, 320, 'RF7_FACA')
m.thing(736, 24, T_START, angle=90)
m.thing(720, 12, T_SIGNAL, tid=SIGNAL_TID)
m.thing(1024, 48, T_ELVIS, angle=180)
for (x, y) in ((736, 300), (300, 300), (1200, 300)):
    m.thing(x, y, T_AMB, args=(AMB_WIND, 50))
m.thing(768, 1440, T_AMB, args=(AMB_WAVES, 90))                  # the sea against the wall, doors closing (l. 827)
for (x, y, a) in ((300, 100, 30), (560, 220, 160), (900, 380, 300), (1260, 140, 80), (1100, 460, 200)):
    m.thing(x, y, T_LITTER, angle=a)

# ============================================================================ B. INTO THE HOTEL
opening(1536, 192, 1600, 256, HALL, 112, 320, 'RF7_FACA')       # a breach in the east wing
m.box(1600, 192, 2048, 256, HALL)
walls(1600, 192, 2048, 256, 'RF7_GRAF')
for x0 in (1664, 1856):                                          # gutted rooms off the corridor
    m.box(x0, 272, x0 + 128, 448, ROOM)
    walls(x0, 272, x0 + 128, 448, 'RF7_BETO')
    m.box(x0 + 48, 256, x0 + 80, 272, HALL, ceil=96)             # their doorways (the doors gone)
    m.raise_block(x0 + 16, 384, x0 + 112, 432, 16, 'RF7_MOQU', 'RF4_ATEL', ROOM)
m.box(1984, -320, 2048, 192, HALL)                               # the corridor south
walls(1984, -320, 2048, 192, 'RF7_GRAF')
across(1608, 192, 1608, 256, {'user_scene': J_HALLS})
for (x, y) in ((1700, 224), (1920, 224), (2016, 0), (2016, -200), (1728, 360), (1920, 360)):
    m.thing(x, y, T_LAMP, args=(140, 138, 132, 210), z=80)        # grey day through the broken windows

# ============================================================================ C. THE SERVICE STAIR AND THE BEDFRAME
for k in range(8):                                               # crushed glass and ashes, down to -128
    y1 = -320 - 32 * k
    m.box(1984, y1 - 32, 2048, y1, STAIR, floor=-16 * (k + 1), ceil=-16 * (k + 1) + 120)
m.box(1920, -704, 2112, -576, STAIR, floor=-128, ceil=-128 + 112)               # the landing
walls(1920, -704, 2112, -320, 'RF7_GRAF')
across(1984, -328, 2048, -328, {'user_scene': J_STAIR})
m.box(1792, -704, 1904, -576, replace(ROOM, floor=-128, ceil=-128 + 112, light=50, ftex='RF7_MOQU'))   # the room
m.box(1904, -672, 1920, -608, replace(ROOM, floor=-128, ceil=-128 + 96, light=50))                    # its door, open
walls(1792, -704, 1904, -576, 'RF7_BETO')
m.decor_line(1921, -670, 1921, -610, 'RF5_BLNK', -128, blocking=True, yscale=4, user_scene=J_BED)   # held by the bedframe
m.thing(1944, -640, T_BED, angle=0)
m.thing(2016, -640, T_LAMP, args=(140, 124, 104, 180), z=80)
m.thing(2016, -440, T_LAMP, args=(120, 116, 110, 160), z=80)
m.thing(1840, -640, T_LAMP, args=(150, 100, 60, 90), z=40)                 # the cold smoke's glow
m.trigger(1840, -702, 1840, -578, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(1824 // UNIT, y // UNIT) for y in range(-704, -576, 16)}

# Elvis's way (RFElvisPoint, in order)
for k, (x, y) in enumerate(((1024, 64), (1300, 200), (1560, 224), (1760, 224), (2016, 224), (2016, 40), (2016, -300),
                            (2016, -560), (1984, -640))):
    m.thing(x, y, T_EPOINT, args=(k + 1,))
m.label(8, 8, 'A TERRASSE')
m.label(1600, 270, 'B HOTEL')
m.label(1920, -720, 'C ESCALIER DE SERVICE')

route = [(736, 60, 0, 120, 0, 90),
         (736, 80, 0, 60, 0, 270),             # he turns round: the gutted room, ERREUR O
         (900, 120, 0, 900, 0, 0),             # Elvis, the watch, the water, the room behind the kitchens
         (1300, 200, 0, 0, 0, 0), (1560, 224, 0, 0, 0, 0), (1760, 224, 0, 0, 0, 0), (2016, 224, 0, 0, 0, 0),
         (2016, 40, 0, 0, 0, 0), (2016, -300, 0, 0, 0, 0), (2016, -560, 0, 0, 0, 0),
         (2000, -620, 0, 400, 0, 180),         # Elvis comes to the bedframe
         (2000, -630, 1, 60, 0, 180),          # they lift it together
         (1960, -640, 0, 240, 0, 180),         # "C'est la."
         (1880, -640, 0, 0, 0, 180), (1830, -640, 0, 0, 0, 180)]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF07.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF07_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF07_plan.png', scale=0.25)
    report = m.check({}, m.exit_cells, decor_types=(T_SPOT, T_LAMP, T_EPOINT, T_ELVIS, T_BED))
    print('RF07 built:', m.stats)
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
