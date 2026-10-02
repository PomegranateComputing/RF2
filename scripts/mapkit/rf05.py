#!/usr/bin/env python3
"""RF05 - Les machines continuent. Production map source (authored, not generated).

Novel l. 551-707 (docs/production/maps/RF05_FICHE.md), in its order:

  A  The stair under the substation door (RF04's exit, in the north rocks of the park): dry steps, then damp; the
     bulb behind its grille and its circle of light (l. 555).
  B  The substation, a vault half cellar half workshop: marble switchboards, dials (GRAND HUIT too high, CHAMBRE DES
     GLACES at zero), the box NODE 0, the motor and its wheel, the lever MARCHE / ATTENTE / ARRET (l. 559-583). Stopped:
     the young woman of Sainte-Anne comes down (her words), the envelope of Cochin, ERREUR O under her palm (l. 587-655).
  C  The repair spread over the annexes (adaptation): the workshop (rags, oil can, spanner of 17), the cable galleries
     under the park (canvas and copper staples; a stretch under water, an air shaft, a store of old letters of the
     park's signs), the room of the transformers and of the Niagara's pumps (the spare fuse printed 22.12.2022); the
     bearing, the belt, the fuse JERMA; MARCHE (l. 659-689).
  D  The park lit again (the shared park, scripts/mapkit/luna_park.py): up in the lane behind the track, the empty
     train climbing the lift hill over it and its brake (l. 691-695); the dance hall by its side door, the juke-box
     playing and couples only in the mirrors (l. 697-701); behind the stage the service door: the music stops, waves
     (l. 703-707): exit toward RF06.

Owner's review of 01/10: RF05 must be lugubrious, dirty and much richer. The underground keeps the order of the text
and its machines; around them: damp, oil, a flooded stretch, the dark of the galleries, light only where a bulb or the
shaft gives it.

Enemies: the staff of Sainte-Anne come down after Viktor through the galleries, then hold the lit park (accepted
adaptation). The young woman, the dancers and the couple of the mirrors are never targets. The hall stays without
combat (the text is quiet there).

Underground floor UG = -192, north of the park (y > 2432, outside its plan). Sky 512 (the park's).
Usage: python scripts/mapkit/rf05.py   (writes src/maps/RF05.wad, build/RF05_plan.png, build/RF05_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT, texture_scales  # noqa: E402
import luna_park as lp  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

UG = -192
ENV_ROOM, ENV_CORR, ENV_VAULT = (30, 8), (13, 0), (30, 11)

# the park lit again: warmer, the colours of a fete; the underground: dirty, dim
STAIR = Cell(floor=0, ceil=120, ftex='RFF_WOOD', ctex='RFP_CEID', light=84, wall='RF5_ESCA', color=0xE8D8B8, env=ENV_ROOM)
SUB = Cell(floor=UG, ceil=UG + 160, ftex='RFF_CONC', ctex='RFP_CEID', light=104, wall='RF5_VOUT', color=0xF0D8A8, env=ENV_VAULT)
SHOP = Cell(floor=UG, ceil=UG + 112, ftex='RFF_WOOD', ctex='RFP_CEID', light=88, wall='RF4_ATEL', color=0xEAD0B0, env=ENV_ROOM)
GAL = Cell(floor=UG, ceil=UG + 88, ftex='RFF_CONC', ctex='RFP_CEID', light=64, wall='RF4_CABL', color=0xD8E0D8, env=ENV_CORR)
WET = replace(GAL, floor=UG - 8, ftex='RF4_FLAQ', light=58, color=0xC8D8D8)
TRANS = Cell(floor=UG, ceil=UG + 144, ftex='RFF_CONC', ctex='RFP_CEID', light=92, wall='RF5_VOUT', color=0xE4DCC8, env=ENV_VAULT)
STORE = Cell(floor=UG, ceil=UG + 104, ftex='RFF_GRAV', ctex='RFP_CEID', light=60, wall='RF4_HANG', color=0xE0D4C0, env=ENV_ROOM)

LAMP_GAIN = 0.55
DAY_GAIN = 0.45

T_START, T_MAG, T_9MM, T_DRESS = 1, 30101, 30103, 30201
T_WAVE = 30405
ORD, BRA, POR = 1, 2, 3
T_LAMP, T_FLICKER, T_AMB, T_LITTER, T_SIGNAL, T_SPOT = 30601, 30602, 30611, 30622, 30623, 30637
T_VIKTOR_MIRROR = 30651
T_DIALS, T_NODE, T_LEVER, T_MOTOR, T_FUSES, T_DRAWER, T_TOOLBOX, T_FUSEBOX, T_TRAIN, T_JUKEBOX = range(30670, 30680)
T_WP = 30902
AMB_PARK, AMB_MOTOR, AMB_ROOM, AMB_DRIP, AMB_WIND = 6, 7, 3, 2, 1

M_STAIR, M_HEAT, M_DIALS, M_NODE, M_LEVER, M_MOTOR, M_FUSES, M_DRAWER, M_TOOLBOX, M_FUSEBOX = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
M_PALM, M_WHEEL, M_PARK, M_TRAIN, M_HALL, M_WAVES, M_SIGN, M_ENVELOPE = 11, 12, 13, 14, 15, 16, 18, 19
SIGNAL_TID = 999
GALLERY_WAVE, GALLERY2_WAVE, FUSE_WAVE, PARK_WAVE, TRAIN_TID, BULB_TID = 510, 530, 540, 550, 560, 570

m = MapBuilder('RF05')


# --------------------------------------------------------------------------- helpers (as RF02, RF04)
def block(x0, y0, x1, y1, height, top, side, base=None):
    m.raise_block(x0, y0, x1, y1, height, top, side, base)


def lamp(x, y, z, r=255, g=206, b=150, radius=200, tid=0, dormant=False):
    m.thing(x, y, T_LAMP, args=(round(r * LAMP_GAIN), round(g * LAMP_GAIN), round(b * LAMP_GAIN), radius), z=z,
            tid=tid, dormant=dormant)


def daylight(x, y, z, radius=420):
    m.thing(x, y, T_LAMP, args=(round(206 * DAY_GAIN), round(208 * DAY_GAIN), round(214 * DAY_GAIN), radius), z=z)


SCALES = texture_scales(Path(__file__).resolve().parents[2] / 'src' / 'TEXTURES.rf04')


def sign(x0, y0, x1, y1, tex, zbottom, off=1, **flags):
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=SCALES.get(tex, 4), texwidth=L, **flags)
    return m.decor[-1]


def across(x0, y0, x1, y1, special, args=(), objective=0, fields=None, repeat=False):
    horiz = y0 == y1
    assert horiz or x0 == x1
    fixed = y0 if horiz else x0
    assert fixed % UNIT == 8, ('trigger on a grid line', fixed)
    a, b = (min(x0, x1), max(x0, x1)) if horiz else (min(y0, y1), max(y0, y1))
    runs, cur, start = [], None, None
    for k in range(a // UNIT, b // UNIT):
        c = m.cell_at(k * UNIT + 8, fixed) if horiz else m.cell_at(fixed, k * UNIT + 8)
        if c != cur:
            if cur is not None:
                runs.append((start, k * UNIT))
            cur, start = c, k * UNIT
    if cur is not None:
        runs.append((start, b))
    for (s, e) in runs:
        if m.cell_at((s + 8) if horiz else fixed, fixed if horiz else (s + 8)) is None:
            continue
        if horiz:
            m.trigger(s, fixed, e, fixed, special, args, repeat=repeat, objective=objective, fields=fields)
        else:
            m.trigger(fixed, s, fixed, e, special, args, repeat=repeat, objective=objective, fields=fields)


def wake(x0, y0, x1, y1, tid, code=0):
    across(x0, y0, x1, y1, 130, (tid,), objective=code)


def objective(x0, y0, x1, y1, code):
    across(x0, y0, x1, y1, 130, (SIGNAL_TID,), objective=code)


def scene(x0, y0, x1, y1, sc):
    across(x0, y0, x1, y1, 130, (SIGNAL_TID,), fields={'user_scene': sc})


def checkpoint(x0, y0, x1, y1):
    across(x0, y0, x1, y1, 15)


def spot(x, y, kind, tid, angle, skill='all'):
    m.thing(x, y, T_WAVE, angle=angle, tid=tid, args=(kind,), skill=skill)


def litter(points):
    for (x, y, a) in points:
        m.thing(x, y, T_LITTER, angle=a)


def puddle(x0, y0, x1, y1, base):
    """A black puddle on the floor (oil, seepage): the floor's flat changed, same height."""
    m.box(x0, y0, x1, y1, base, ftex='RF4_FLAQ', light=base.light - 6)


# ============================================================================ THE PARK, LIT AGAIN (shared with RF04)
A = lp.build_park(m, sign)
dx0, dy0, dx1, dy1 = lp.SUB_DOOR
m.box(dx0, dy0 + 16, dx1, dy1, lp.VEST, ceil=104)                                    # the substation door, open
m.box(dx0 - 16, dy1, dx1 + 16, dy1 + 64, lp.VEST)
lp.walls(m, dx0 - 16, dy1, dx1 + 16, dy1 + 64, 'RF4_BASC')
sx0, sy0, sx1, sy1 = lp.SIDE_DOOR
m.box(sx0, sy0, sx1, sy0 + 16, lp.HALL, ceil=112)                                     # the side door, opened in RF04
ix0, iy0, ix1, iy1 = lp.HALL_IN
ox0, oy0, ox1, oy1 = A['orchestra']
m.box(ix1, 2160, ox0, 2208, lp.ATELIER, floor=24, ceil=24 + 96)                        # the curtain at the stage's end, open
vx0, vy0, vx1, vy1 = lp.SERVICE_DOOR
m.door(vx0, vy0, vx1, vy1, 46, 'RFD_OAKS', 'RF4_ATEL', replace(lp.ATELIER, floor=24))   # the service door (l. 703)

# ============================================================================ A. THE STAIR
m.thing(1568, 2400, T_START, angle=90)
m.thing(1550, 2390, T_SIGNAL, tid=SIGNAL_TID)
for k in range(12):                                                    # twelve steps of 16: from the park to -192
    y0 = 2432 + 16 * k
    f = -16 * (k + 1)
    m.box(1536, y0, 1600, y0 + 16, STAIR, floor=f, ceil=f + 120, light=84 - 3 * k,
          ftex='RFF_WOOD' if k < 5 else 'RF4_FLAQ' if k % 3 == 2 else 'RFF_CONC')     # dry steps, then damp (l. 555)
m.box(1504, 2624, 1632, 2688, SUB, ceil=UG + 120, light=96, wall='RF5_ESCA')          # the landing
lamp(1568, 2656, 96, 255, 220, 120, 90)                                                # the bulb behind its grille
sign(1504, 2640, 1504, 2680, 'RF5_BLNK', UG + 36, off=1, user_scene=M_PALM)           # where her palm will leave ERREUR O
scene(1536, 2456, 1600, 2456, M_STAIR)
objective(1536, 2440, 1600, 2440, 1)
m.thing(1568, 2560, T_AMB, args=(AMB_DRIP, 45))
m.label(1500, 2380, 'A ESCALIER')

# ============================================================================ B. THE SUBSTATION (a vault)
m.box(1312, 2688, 1824, 3008, SUB)
for x0 in range(1440, 1696, 32):                                       # the nave higher than the aisles: a vault in
    m.box(x0, 2688, x0 + 32, 3008, SUB, ceil=UG + 176 + (16 if 1504 <= x0 < 1632 else 0))   # steps
for (x0, x1) in ((1312, 1536), (1600, 1824)):                          # marble switchboards on the north wall
    m.face(x0, 2992, x1, 3008, 'N', texture='RF5_MARB')                 # (not across the doorways)
for (y0, y1) in ((2688, 2784), (2848, 3008)):                          # and on the west wall
    m.face(1312, y0, 1328, y1, 'W', texture='RF5_MARB')
for (x, y) in ((1408, 2752), (1408, 2912), (1712, 2752), (1712, 2912)):   # the pillars of the vault
    m.carve(x, y, x + 32, y + 32)
    m.modify(x - 16, y - 16, x + 48, y + 48, wall='RF5_VOUT')
for (y0, y1) in ((2704, 2720), (2976, 2992)):                           # cable trays along the long walls
    m.slab(1328, y0, 1808, y1, UG + 120, UG + 126, 'RF4_CABL', top='RF4_CABL', bottom='RF4_CABL')
sign(1344, 3008, 1440, 3008, 'RF5_CAD0', UG + 40, off=1, user_scene=M_DIALS)
sign(1664, 3008, 1696, 3008, 'RF5_LEVM', UG + 40, off=1, user_scene=M_LEVER)
sign(1312, 2856, 1312, 2904, 'RF5_FUS0', UG + 32, off=1, user_scene=M_FUSES)
block(1312, 2736, 1344, 2784, 64, 'RFP_CEID', 'RF5_MOTR')         # the box without a plate, against the wall
sign(1344, 2736, 1344, 2784, 'RF5_NOD0', UG, off=1, user_scene=M_NODE)
block(1504, 2816, 1600, 2864, 40, 'RFF_CONC', 'RF5_MOTR', SUB)         # the motor
m.decor_line(1640, 2808, 1640, 2872, 'RF5_ROU0', UG + 2, yscale=4, texwidth=64, user_scene=M_WHEEL)   # wheel, belt
block(1760, 2704, 1808, 2768, 32, 'RFW_TOP', 'RF4_ATEL', SUB)          # the workbench
block(1680, 2944, 1712, 2976, 24, 'RFW_TOP', 'RF4_ATEL', SUB)          # a crate
block(1776, 2928, 1808, 2976, 40, 'RFW_TOP', 'RF4_ATEL')          # drums of oil
for (x0, y0, x1, y1) in ((1488, 2720, 1520, 2752), (1600, 2896, 1648, 2928), (1744, 2800, 1776, 2832)):
    puddle(x0, y0, x1, y1, SUB)                                        # oil and seepage under the machines
m.thing(1784, 2736, T_SPOT, args=(M_ENVELOPE,))
m.thing(1408, 2992, T_DIALS, args=(M_DIALS,), z=40)
m.thing(1680, 2992, T_LEVER, args=(M_LEVER,), z=40)
m.thing(1328, 2880, T_FUSES, args=(M_FUSES,), z=32)
m.thing(1376, 2760, T_NODE, args=(M_NODE,), z=24)
m.thing(1552, 2880, T_MOTOR, angle=270, args=(M_MOTOR,), z=16)
m.thing(1552, 2840, T_AMB, args=(AMB_MOTOR, 100))
for (x, y) in ((1440, 2720), (1696, 2720), (1440, 2960), (1696, 2960)):
    lamp(x, y, 140, 255, 214, 150, 170)
m.thing(1568, 2944, T_FLICKER, args=(255, 200, 130, 140, 50), z=150)
scene(1504, 2712, 1632, 2712, M_HEAT)
objective(1504, 2728, 1632, 2728, 2)
m.thing(1740, 2904, T_DRESS)
m.thing(1400, 2944, T_9MM)
litter([(1460, 2800, 30), (1660, 2760, 200), (1760, 2860, 120), (1380, 2960, 300)])
# doorways: east to the workshop, west to the galleries, north to the transformers and pumps
m.box(1824, 2784, 1840, 2848, SUB, ceil=UG + 96)
m.box(1296, 2784, 1312, 2848, SUB, ceil=UG + 88)
m.box(1536, 3008, 1600, 3040, SUB, ceil=UG + 104)
m.label(1320, 2700, 'B SOUS-STATION')

# ============================================================================ C. THE ANNEXES
# the workshop: a chest of drawers (rags, an oil can, a flat spanner of 17), shelves, a vice
m.box(1840, 2752, 2000, 2912, SHOP)
block(1984, 2800, 2000, 2864, 40, 'RFW_TOP', 'RF4_ATEL', SHOP)
block(1856, 2880, 1952, 2912, 56, 'RFW_TOP', 'RF4_ATEL', SHOP)          # shelves of tins and spare parts
block(1856, 2752, 1904, 2784, 32, 'RFW_TOP', 'RF4_ATEL', SHOP)          # the vice bench
puddle(1904, 2800, 1936, 2832, SHOP)
m.thing(1976, 2832, T_DRAWER, angle=0, args=(M_DRAWER,), z=24)
lamp(1920, 2832, 96, 255, 210, 150, 130)
m.thing(1880, 2864, T_MAG)
# the cable galleries under the park: west, north (a stretch under water), back east to the transformers (a loop)
m.box(736, 2784, 1296, 2848, GAL)
m.box(736, 2848, 800, 3232, GAL)
m.box(800, 3168, 1312, 3232, GAL)
m.box(736, 2976, 800, 3072, WET)                                         # seepage: the floor under black water
m.box(800, 2992, 816, 3056, WET)
m.box(1184, 2784, 1248, 2848, GAL, ceil=64, ctex='F_SKY1', light=120)    # an air shaft: grey daylight from the park
daylight(1216, 2816, 40, 220)
for (y0, y1) in ((2784, 2800), (2832, 2848)):                            # cable bundles along the walls
    m.slab(736, y0, 1184, y1, UG + 60, UG + 66, 'RF4_CABL', top='RF4_CABL', bottom='RF4_CABL')
m.thing(768, 3200, T_TOOLBOX, args=(M_TOOLBOX,), z=0)                    # canvas, copper staples
for (x, y) in ((1100, 2816), (768, 3004), (1000, 3200)):
    m.thing(x, y, T_FLICKER, args=(230, 214, 170, 110, 70), z=70)
m.thing(1020, 2816, T_AMB, args=(AMB_DRIP, 45))
m.thing(768, 3020, T_AMB, args=(AMB_DRIP, 55))
m.thing(768, 2904, T_DRESS)
m.thing(1150, 3200, T_MAG)
litter([(900, 2800, 80), (768, 3120, 10), (1180, 3210, 260)])
# the store of the park: old letters of its signs, a carousel horse without its pole, crates (off the north gallery)
m.box(928, 3232, 1056, 3328, STORE)
block(944, 3248, 1008, 3280, 32, 'RFW_TOP', 'RF4_ATEL', STORE)
block(1024, 3248, 1056, 3296, 48, 'RFW_TOP', 'RF4_ATEL', STORE)
sign(928, 3328, 1056, 3328, 'RF4_NIAG', UG + 40, off=1)                  # an old NIAGARA board (128 u), stored
lamp(992, 3280, 80, 230, 210, 170, 90)
m.thing(960, 3260, T_9MM)
m.thing(1040, 3310, T_DRESS)
# the room of the transformers and of the Niagara's pumps; the spare fuse box on the east wall
m.box(1312, 3040, 1696, 3296, TRANS)
block(1360, 3088, 1424, 3152, 56, 'RFF_CONC', 'RF5_MOTR', TRANS)
block(1488, 3200, 1552, 3264, 56, 'RFF_CONC', 'RF5_MOTR', TRANS)
block(1328, 3216, 1392, 3280, 72, 'RFF_CONC', 'RF5_MOTR', TRANS)          # the pumps of the Niagara
block(1440, 3216, 1472, 3280, 72, 'RFF_CONC', 'RF5_MOTR', TRANS)
block(1664, 3136, 1696, 3200, 48, 'RFW_TOP', 'RF4_ATEL', TRANS)
m.slab(1328, 3280, 1696, 3296, UG + 88, UG + 104, 'RF4_BASC', top='RF4_BASC', bottom='RF4_BASC')   # the pipes to the basin
puddle(1424, 3152, 1488, 3200, TRANS)
m.thing(1656, 3168, T_FUSEBOX, angle=0, args=(M_FUSEBOX,), z=32)
for (x, y) in ((1440, 3104), (1600, 3244)):
    lamp(x, y, 130, 230, 214, 180, 190)
m.thing(1500, 3164, T_AMB, args=(AMB_ROOM, 55))
m.thing(1640, 3064, T_9MM)
m.thing(1340, 3184, T_DRESS)
# E1: after her, the staff come along the galleries; E2 at their bend; E3 when the fuse is taken
spot(1000, 2816, ORD, GALLERY_WAVE, 0)
spot(880, 2816, ORD, GALLERY_WAVE, 0)
spot(768, 2954, ORD, GALLERY_WAVE, 270, skill='hard')
spot(1100, 3200, ORD, GALLERY2_WAVE, 180)
spot(1200, 3200, POR, GALLERY2_WAVE, 180)
wake(736, 2920, 800, 2920, GALLERY2_WAVE)
spot(900, 3200, ORD, FUSE_WAVE, 0)
spot(840, 3200, ORD, FUSE_WAVE, 0)
spot(768, 3104, POR, FUSE_WAVE, 270, skill='normal+')
m.label(740, 2790, 'C GALERIES')
m.label(1320, 3280, 'TRANSFORMATEURS ET POMPES')

# ============================================================================ D. THE PARK LIT AGAIN
lx0, ly0, lx1, ly1 = lp.LANE_BOX
# the train of three cars, empty, climbing the lift hill over the lane; its brake claps (l. 693-695)
m.thing(352, 1632, T_TRAIN, angle=90, args=(768, 240), tid=TRAIN_TID, z=128)
# LUNA PARK in bulbs on the rocks over the lane, between two sheds (unlit, then lit: M_SIGN)
s1, s2, s3 = lp.SHEDS
sign(s2[1] + 16, ly1, s3[0] - 16, ly1, 'RF5_LUN0', 150, off=1, user_scene=M_SIGN)
# the bulbs that come on one after the other (dormant lamps, tid 570): the lane, the hall's porch, the attractions
for (x, y, z, r, g, b) in ((1500, 2300, 120, 255, 200, 110), (1200, 2300, 120, 255, 120, 90), (900, 2300, 120, 120, 220, 120),
                           (600, 2300, 120, 255, 210, 120), (704, 1890, 120, 255, 200, 110), (1280, 1744, 200, 255, 120, 90),
                           (1296, 1392, 120, 110, 210, 120), (1088, 1920, 380, 255, 210, 120), (1344, 1000, 420, 255, 200, 110),
                           (1480, 704, 200, 255, 120, 90), (496, 1408, 180, 255, 214, 160), (960, 300, 200, 255, 200, 110),
                           (560, 2150, 170, 255, 214, 160), (850, 2050, 170, 255, 214, 160)):
    lamp(x, y, z, r, g, b, 200, tid=BULB_TID, dormant=True)
for (x, y) in ((1300, 2288), (700, 2288), (1000, 1200)):
    daylight(x, y, 220, 600)
m.thing(1000, 2288, T_AMB, args=(AMB_PARK, 45))
m.thing(704, 2080, T_AMB, args=(AMB_ROOM, 50))
scene(dx0, dy0 + 8, dx1, dy0 + 8, M_PARK)                                              # out of the door: the park lit
objective(dx0, ly1 - 8, dx1, ly1 - 8, 7)
checkpoint(dx0, ly1 - 24, dx1, ly1 - 24)
across(760, ly0, 760, ly1, 130, (SIGNAL_TID,), fields={'user_scene': M_TRAIN})       # the train over the lane
m.thing(1180, 2300, T_9MM)
m.thing(800, 2260, T_MAG)
m.thing(1600, 2260, T_DRESS)
# E4: the lit park, the staff out of the sheds dug into the rocks
spot(s1[0] + 48, ly1 + 16, BRA, PARK_WAVE, 180, skill='normal+')
spot(s2[0] + 24, ly1 + 32, ORD, PARK_WAVE, 180)
spot(s2[0] + 72, ly1 + 32, POR, PARK_WAVE, 180)
spot(s3[0] + 22, ly1 + 32, ORD, PARK_WAVE, 180)
spot(s3[0] + 60, ly1 + 32, ORD, PARK_WAVE, 180, skill='hard')
# the hall: the juke-box plays, couples only in the mirrors (Viktor's reflection follows him; no figure in the room)
for (x, y) in ((592, 2032), (800, 2032), (592, 2112), (800, 2112)):
    m.carve(x, y, x + 32, y + 32)
    m.modify(x - 16, y - 16, x + 48, y + 48, wall='RF4_COLN')
for (y0, y1) in ((2000, 2032), (2048, 2080), (2096, 2128)):
    m.face(ix0, y0, ix0 + 16, y1, 'W', texture='RFP_PLN', special=182)
    m.carve(ix0 - 16, y0, ix0, y1)                       # a mirror (Line_Mirror) must be a one-sided wall: void behind
    sign(ix0, y0, ix0, y1, 'RF4_PIQU', 0, off=2)
for (y0, y1) in ((1984, 2064), (2096, 2144)):
    m.face(ix1 - 16, y0, ix1, y1, 'E', texture='RFP_PLN', special=182)
    m.carve(ix1, y0, ix1 + 16, y1)
    sign(ix1, y1, ix1, y0, 'RF4_PIQU', 0, off=2)
m.thing(704, 2080, T_VIKTOR_MIRROR)
block(672, 2160, ix1, iy1, 24, 'RF4_PARQ', 'RFW_PANL', lp.HALL)          # the orchestra stage
m.thing(648, 2188, T_JUKEBOX, angle=270)
lamp(648, 2170, 40, 255, 170, 90, 120)
m.thing(704, 1890, T_DRESS)
sc0, sc_y0, sc1, sc_y1 = lp.SERVICE
scene(sx0, sy0 - 8, sx1, sy0 - 8, M_HALL)
m.trigger(1080, sc_y0 + 2, 1080, sc_y1 - 2, 130, (SIGNAL_TID,), fields={'user_scene': M_WAVES})
m.trigger(1176, sc_y0 + 2, 1176, sc_y1 - 2, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(1184 // UNIT, y // UNIT) for y in range(sc_y0, sc_y1, 16)}
m.thing(1200, 2184, T_AMB, args=(AMB_WIND, 60))                          # waves, behind the service door
m.label(lx0 + 16, ly0 + 8, 'D PARC ALLUME')
m.label(ix0 + 8, iy0 + 8, 'SALLE DE DANSE')

# --------------------------------------------------------------------------- autopilot route (dev)
route = [
    (1568, 2400, 0, 0, 1, 90),
    (1568, 2600, 0, 0, 0, 90),               # down the stair
    (1568, 2704, 0, 0, 0, 0),
    (1552, 2896, 1, 60, 0, 270),             # the motor, running: the bearing hot, the belt split
    (1384, 2760, 1, 200, 0, 180),            # the box: NODE 0
    (1408, 2976, 1, 60, 0, 90),              # the dials
    (1680, 2976, 1, 2240, 0, 90),            # the lever: ARRET; the young woman; her palm
    (1780, 2816, 0, 0, 0, 0),
    (1950, 2832, 0, 0, 0, 0),
    (1960, 2832, 1, 60, 0, 0),               # the drawer: rags, oil can, spanner of 17
    (1780, 2816, 0, 0, 0, 0),
    (1680, 2720, 0, 0, 0, 0),
    (1440, 2720, 0, 0, 0, 0),                # round the motor
    (1280, 2816, 0, 60, 0, 0),               # E1 along the gallery
    (768, 2816, 0, 0, 0, 0),
    (768, 2944, 0, 0, 0, 0),
    (768, 3184, 0, 60, 0, 0),                # E2 at the bend (through the black water)
    (768, 3200, 1, 60, 0, 180),              # the toolbox: canvas, copper staples
    (1300, 3200, 0, 0, 0, 0),
    (1500, 3120, 0, 0, 0, 0),
    (1640, 3168, 1, 60, 0, 0),               # the spare fuse, 22.12.2022 (E3)
    (1570, 3104, 0, 120, 0, 0),
    (1568, 3024, 0, 0, 0, 0),
    (1552, 2896, 1, 220, 0, 270),            # the bearing cleaned
    (1552, 2896, 1, 40, 0, 270),             # the belt reinforced
    (1340, 2880, 1, 440, 0, 180),            # the fuse JERMA
    (1680, 2976, 1, 640, 0, 90),             # MARCHE: the park lights up
    (1568, 2704, 0, 0, 0, 0),
    (1568, 2464, 0, 0, 0, 0),                # up the stair
    (1568, 2400, 0, 0, 0, 0),
    (1568, 2300, 0, 60, 0, 0),               # the lane: E4
    (1300, 2288, 0, 60, 0, 0),
    (700, 2288, 0, 0, 0, 0),                 # the train over the lane
    (560, 2288, 0, 0, 0, 0),
    (560, 2216, 0, 0, 0, 0),                 # in by the side door
    (560, 2184, 0, 420, 0, 0),               # the hall: the juke-box, the mirrors
    (560, 2090, 0, 0, 0, 0),
    (720, 2090, 0, 0, 0, 0),                 # round the column (the juke-box narrows the way by it)
    (720, 2184, 0, 0, 0, 0),                 # up on the stage
    (880, 2184, 0, 0, 0, 0),
    (960, 2184, 0, 0, 0, 0),                 # the orchestra's box
    (992, 2184, 1, 40, 0, 0),                # the service door
    (1100, 2184, 0, 0, 0, 0),                # waves
    (1200, 2184, 0, 0, 0, 0),                # exit
]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF05.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF05_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF05_plan.png', scale=0.25)
    report = m.check({}, m.exit_cells, decor_types=(T_SPOT, T_TRAIN, T_LAMP))
    print('RF05 built:', m.stats)
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
