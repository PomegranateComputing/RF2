#!/usr/bin/env python3
"""RF05 - Les machines continuent. Production map source (authored, not generated).

Novel l. 551-707 (docs/production/maps/RF05_FICHE.md), in its order:

  A  The stair under the substation door (RF04's exit): dry steps, then damp; the bulb behind its grille and its
     circle of light (l. 555).
  B  The substation: vault, marble switchboards, dials (GRAND HUIT too high, CHAMBRE DES GLACES at zero), the box
     NODE 0, the motor and its wheel, the lever MARCHE / ATTENTE / ARRET (l. 559-583). Stopped: the young woman of
     Sainte-Anne comes down (her words; her figure is requested from Astra), the envelope of Cochin, ERREUR Ø under
     her palm (l. 587-655).
  C  The repair spread over the annexes (adaptation): the workshop (rags, oil can, spanner of 17), the cable
     galleries under the park (canvas and copper staples), the transformer room and its pumps (the spare fuse printed
     22.12.2022); the bearing, the belt, the fuse JERMA; MARCHE (l. 659-689).
  D  The park lit again: the lane behind the track, the empty train and its brake (l. 691-695), the dance hall where
     the juke-box plays and couples dance only in the mirrors (l. 697-701), the service door: the music stops, waves
     (l. 703-707): exit toward RF06, the corridor.

Enemies: the staff of Sainte-Anne come down after Viktor through the galleries, then hold the lit park (accepted
adaptation). The young woman, the dancers and the couple of the mirrors are never targets. The hall stays without
combat (the text is quiet there).

Surface coordinates are those of RF04 (same park). Underground floor: -192. Sky 256.
Usage: python scripts/mapkit/rf05.py   (writes src/maps/RF05.wad, build/RF05_plan.png, build/RF05_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

SKY = 256
UG = -192
ENV_PARK, ENV_ROOM, ENV_CORR, ENV_HALL, ENV_VAULT = (32, 0), (30, 8), (13, 0), (30, 3), (30, 11)

PARK = Cell(floor=0, ceil=SKY, ftex='RFF_GRAV', ctex='F_SKY1', light=168, wall='RF4_FAC1', color=0xF0D8B0,
            env=ENV_PARK, lower='RF4_BASC')        # the park lit again: warmer, the colours of a fete
LANE = replace(PARK, ftex='RF4_DALH', wall='RF4_HANG', light=156)
POSTS = replace(PARK, ftex='RF4_HERB', wall='RF4_ATEL', light=150)
PLAZA = replace(PARK, ftex='RFF_GRAV', wall='RF4_FAC3', light=164)
HALL = Cell(floor=0, ceil=192, ftex='RF4_PARQ', ctex='RFP_CEID', light=132, wall='RFP_PLN', color=0xF8DCB0, env=ENV_HALL)
VEST = Cell(floor=0, ceil=112, ftex='RFF_CONC', ctex='RFP_CEID', light=80, wall='RF4_BASC', color=0xE0D8C8, env=ENV_ROOM)
SERV = Cell(floor=0, ceil=96, ftex='RFF_CONC', ctex='RFP_CEID', light=70, wall='RF4_BASC', color=0xD8E0E4, env=ENV_CORR)
STAIR = Cell(floor=0, ceil=120, ftex='RFF_WOOD', ctex='RFP_CEID', light=84, wall='RF5_ESCA', color=0xE8D8B8, env=ENV_ROOM)
SUB = Cell(floor=UG, ceil=UG + 160, ftex='RFF_CONC', ctex='RFP_CEID', light=112, wall='RF5_VOUT', color=0xF4DCB0, env=ENV_VAULT)
SHOP = Cell(floor=UG, ceil=UG + 112, ftex='RFF_WOOD', ctex='RFP_CEID', light=96, wall='RF4_ATEL', color=0xEAD8C0, env=ENV_ROOM)
GAL = Cell(floor=UG, ceil=UG + 88, ftex='RFF_CONC', ctex='RFP_CEID', light=76, wall='RF4_CABL', color=0xE0E4E0, env=ENV_CORR)
TRANS = Cell(floor=UG, ceil=UG + 144, ftex='RFF_CONC', ctex='RFP_CEID', light=100, wall='RF5_VOUT', color=0xE8E0D0, env=ENV_VAULT)

LAMP_GAIN = 0.55
DAY_GAIN = 0.45

T_START, T_MAG, T_9MM, T_DRESS = 1, 30101, 30103, 30201
T_WAVE = 30405
ORD, BRA, POR = 1, 2, 3
T_LAMP, T_FLICKER, T_AMB, T_LITTER, T_SIGNAL, T_SPOT = 30601, 30602, 30611, 30622, 30623, 30637
T_VIKTOR_MIRROR = 30651
T_DIALS, T_NODE, T_LEVER, T_MOTOR, T_FUSES, T_DRAWER, T_TOOLBOX, T_FUSEBOX, T_TRAIN, T_JUKEBOX = range(30670, 30680)
T_WP = 30902
AMB_PARK, AMB_MOTOR, AMB_ROOM, AMB_DRIP = 6, 7, 3, 2

M_STAIR, M_HEAT, M_DIALS, M_NODE, M_LEVER, M_MOTOR, M_FUSES, M_DRAWER, M_TOOLBOX, M_FUSEBOX = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
M_PALM, M_WHEEL, M_PARK, M_TRAIN, M_HALL, M_WAVES, M_SIGN, M_ENVELOPE = 11, 12, 13, 14, 15, 16, 18, 19
SIGNAL_TID = 999
GALLERY_WAVE, GALLERY2_WAVE, FUSE_WAVE, PARK_WAVE, TRAIN_TID, BULB_TID = 510, 530, 540, 550, 560, 570

m = MapBuilder('RF05')


# --------------------------------------------------------------------------- helpers (as RF02, RF04)
def door(x0, y0, x1, y1, tag, tex, base, frame_side, lintel=112, track='RFP_DRK', **kw):
    if frame_side in ('N', 'S'):
        assert y1 - y0 == 32
        fy0, fy1, dy0, dy1 = (y1 - 16, y1, y0, y1 - 16) if frame_side == 'N' else (y0, y0 + 16, y0 + 16, y1)
        m.box(x0, fy0, x1, fy1, base, ceil=base.floor + lintel, wall=track, upper='', mid='', lower='')
        m.door(x0, dy0, x1, dy1, tag, tex, track, base, **kw)
    else:
        assert x1 - x0 == 32
        fx0, fx1, dx0, dx1 = (x1 - 16, x1, x0, x1 - 16) if frame_side == 'E' else (x0, x0 + 16, x0 + 16, x1)
        m.box(fx0, y0, fx1, y1, base, ceil=base.floor + lintel, wall=track, upper='', mid='', lower='')
        m.door(dx0, y0, dx1, y1, tag, tex, track, base, **kw)


def block(x0, y0, x1, y1, height, top, side, base=None):
    m.raise_block(x0, y0, x1, y1, height, top, side, base)


def lamp(x, y, z, r=255, g=206, b=150, radius=200, tid=0, dormant=False):
    m.thing(x, y, T_LAMP, args=(round(r * LAMP_GAIN), round(g * LAMP_GAIN), round(b * LAMP_GAIN), radius), z=z,
            tid=tid, dormant=dormant)


def sign(x0, y0, x1, y1, tex, zbottom, off=1, **flags):
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=4, texwidth=L, **flags)
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


# ============================================================================ A. THE STAIR
m.box(-880, 2432, -784, 2528, VEST)
m.thing(-832, 2456, T_START, angle=90)
m.thing(-850, 2446, T_SIGNAL, tid=SIGNAL_TID)
for k in range(12):                                                    # twelve steps of 16: from the park to -192
    y0 = 2528 + 16 * k
    f = -16 * (k + 1)
    m.box(-864, y0, -800, y0 + 16, STAIR, floor=f, ceil=f + 120, light=84 - 2 * k)
m.box(-896, 2720, -768, 2784, SUB, ceil=UG + 120, light=96, wall='RF5_ESCA')     # the landing
lamp(-832, 2752, 96, 255, 220, 120, 90)                               # the bulb behind its grille: a precise circle
sign(-896, 2736, -896, 2776, 'RF5_BLNK', UG + 36, off=1, user_scene=M_PALM)       # where her palm will leave ERREUR Ø
scene(-864, 2552, -800, 2552, M_STAIR)
objective(-864, 2536, -800, 2536, 1)
m.thing(-832, 2600, T_AMB, args=(AMB_DRIP, 45))
m.label(-880, 2440, 'A ESCALIER')

# ============================================================================ B. THE SUBSTATION
m.box(-1088, 2784, -576, 3104, SUB)
m.modify(-1088, 3088, -576, 3104, wall='RF5_MARB')                    # marble switchboards on the north wall
m.modify(-1088, 2784, -1072, 3104, wall='RF5_MARB')
sign(-1040, 3104, -944, 3104, 'RF5_CAD0', UG + 40, off=1, user_scene=M_DIALS)
sign(-736, 3104, -704, 3104, 'RF5_LEVM', UG + 40, off=1, user_scene=M_LEVER)
sign(-1088, 2952, -1088, 3000, 'RF5_FUS0', UG + 32, off=1, user_scene=M_FUSES)
block(-1088, 2832, -1056, 2880, 64, 'RFP_CEID', 'RF5_MOTR', SUB)      # the box without a plate, against the wall
sign(-1056, 2832, -1056, 2880, 'RF5_NOD0', UG, off=1, user_scene=M_NODE)
block(-896, 2912, -800, 2960, 40, 'RFF_CONC', 'RF5_MOTR', SUB)        # the motor
m.decor_line(-760, 2904, -760, 2968, 'RF5_ROU0', UG + 2, yscale=4, texwidth=64, user_scene=M_WHEEL)   # wheel, belt
block(-640, 2800, -592, 2864, 32, 'RFW_TOP', 'RF4_ATEL', SUB)         # the workbench
block(-720, 3040, -688, 3072, 24, 'RFW_TOP', 'RF4_ATEL', SUB)         # a crate
m.thing(-616, 2832, T_SPOT, args=(M_ENVELOPE,))
m.thing(-992, 3088, T_DIALS, args=(M_DIALS,), z=40)
m.thing(-720, 3088, T_LEVER, args=(M_LEVER,), z=40)
m.thing(-1072, 2976, T_FUSES, args=(M_FUSES,), z=32)
m.thing(-1024, 2856, T_NODE, args=(M_NODE,), z=24)
m.thing(-848, 2976, T_MOTOR, angle=270, args=(M_MOTOR,), z=16)
m.thing(-848, 2936, T_AMB, args=(AMB_MOTOR, 100))
for (x, y) in ((-960, 2860), (-700, 2860), (-960, 3040), (-700, 3040)):
    lamp(x, y, 140, 255, 214, 150, 180)
scene(-896, 2808, -768, 2808, M_HEAT)
objective(-896, 2824, -768, 2824, 2)
m.thing(-660, 3000, T_DRESS)
m.thing(-1000, 3040, T_9MM)
# doorways: east to the workshop, west to the galleries, north to the transformer room
m.box(-576, 2880, -560, 2944, SUB, ceil=UG + 96)
m.box(-1104, 2880, -1088, 2944, SUB, ceil=UG + 88)
m.box(-864, 3104, -800, 3136, SUB, ceil=UG + 104)
m.label(-1080, 2800, 'B SOUS-STATION')

# ============================================================================ C. THE ANNEXES
# the workshop: a chest of drawers (rags, an oil can, a flat spanner of 17)
m.box(-560, 2848, -400, 3008, SHOP)
block(-416, 2896, -400, 2960, 40, 'RFW_TOP', 'RF4_ATEL', SHOP)
m.thing(-424, 2928, T_DRAWER, angle=0, args=(M_DRAWER,), z=24)
lamp(-480, 2928, 96, 255, 210, 150, 140)
m.thing(-520, 2980, T_MAG)
# the cable galleries under the park: west, north, back east to the transformer room (a loop)
m.box(-1664, 2880, -1104, 2944, GAL)
m.box(-1664, 2944, -1600, 3328, GAL)
m.box(-1600, 3264, -1088, 3328, GAL)
m.thing(-1632, 3296, T_TOOLBOX, args=(M_TOOLBOX,), z=0)              # canvas, copper staples
for (x, y) in ((-1300, 2912), (-1632, 3100), (-1400, 3296)):
    m.thing(x, y, T_FLICKER, args=(230, 214, 170, 110, 70), z=70)
m.thing(-1380, 2912, T_AMB, args=(AMB_DRIP, 45))
m.thing(-1632, 3000, T_DRESS)
m.thing(-1250, 3296, T_MAG)
# the transformer room: the pumps of the Niagara, the spare fuse box on the east wall
m.box(-1088, 3136, -704, 3392, TRANS)
block(-1040, 3184, -976, 3248, 56, 'RFF_CONC', 'RF5_MOTR', TRANS)
block(-912, 3296, -848, 3360, 56, 'RFF_CONC', 'RF5_MOTR', TRANS)
block(-736, 3232, -704, 3296, 48, 'RFW_TOP', 'RF4_ATEL', TRANS)
m.thing(-744, 3264, T_FUSEBOX, angle=0, args=(M_FUSEBOX,), z=32)
for (x, y) in ((-960, 3200), (-800, 3340)):
    lamp(x, y, 130, 230, 214, 180, 200)
m.thing(-900, 3260, T_AMB, args=(AMB_ROOM, 55))
m.thing(-760, 3160, T_9MM)
m.thing(-1060, 3360, T_DRESS)
# E1: after her, the staff come along the galleries; E2 at their bend; E3 when the fuse is taken
spot(-1400, 2912, ORD, GALLERY_WAVE, 0)
spot(-1520, 2912, ORD, GALLERY_WAVE, 0)
spot(-1632, 3050, ORD, GALLERY_WAVE, 270, skill='hard')
spot(-1300, 3296, ORD, GALLERY2_WAVE, 180)
spot(-1200, 3296, POR, GALLERY2_WAVE, 180)
wake(-1664, 3016, -1600, 3016, GALLERY2_WAVE)
spot(-1500, 3296, ORD, FUSE_WAVE, 0)
spot(-1560, 3296, ORD, FUSE_WAVE, 0)
spot(-1632, 3200, POR, FUSE_WAVE, 270, skill='normal+')
m.label(-1660, 2890, 'C GALERIES')
m.label(-1080, 3380, 'TRANSFORMATEURS')

# ============================================================================ D. THE PARK LIT AGAIN
m.box(-864, 2400, -800, 2432, LANE, ceil=104, ctex='RFP_CEID')       # the substation door, open
m.box(-896, 2304, 96, 2400, LANE)
m.box(-640, 2400, -528, 2496, LANE, ceil=120, ctex='RFP_CEID', light=118)
m.box(-320, 2400, -224, 2464, LANE, ceil=120, ctex='RFP_CEID', light=118)
# the track behind the fence, the train of three cars
m.box(-768, 2048, 48, 2304, POSTS)
m.slab(-752, 2176, -128, 2208, 144, 160, 'RF4_ATEL', top='RF4_VOIE', bottom='RF4_ATEL')
for x in range(-752, -127, 96):
    m.slab(x, 2176, x + 16, 2192, 0, 144, 'RF4_ATEL')
for x in range(-752, -224, 96):
    m.decor_line(x + 17, 2184, x + 95, 2184, 'RF4_BOIS', 0, yscale=4, texwidth=78)
m.decor_line(-768, 2296, 48, 2296, 'RFM_GRIL', 0, blocking=True, yscale=4)
m.thing(-160, 2192, T_TRAIN, args=(560,), tid=TRAIN_TID, z=160)
# the plaza, the marquee, the turnstiles (the counter at 618, the bar lifted), the bulbs over the plaza
m.box(64, 1920, 624, 2048, PLAZA)
m.slab(176, 1968, 560, 2048, 136, 144, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
m.box(336, 1984, 400, 2032, PLAZA)
m.box(464, 1968, 560, 2000, PLAZA)
sign(336, 2048, 496, 2048, 'RF4_DANS', 152, off=1)
m.box(240, 2048, 496, 2080, HALL, ceil=128, ftex='RFF_SLAB')
for (x0, x1) in ((240, 288), (336, 384), (432, 496)):
    block(x0, 2048, x1, 2080, 40, 'RFM_TOP', 'RF4_TOUR', m.cells[(x0 // UNIT, 2048 // UNIT)])
sign(256, 2048, 288, 2048, 'RF4_C618', 14, off=1)
m.decor_line(386, 2064, 430, 2064, 'RF2_RAMB', 0, blocking=True, yscale=4)
sign(560, 1920, 432, 1920, 'RF5_LUN0', 150, off=1, user_scene=M_SIGN)    # LUNA PARK in bulbs over the plaza
# the hall: parquet, mirrors, columns, the stage; the juke-box plays; the side door open; the service door
m.box(128, 2080, 624, 2432, HALL)
for x in (256, 480):
    for y in (2176, 2320):
        m.carve(x, y, x + 32, y + 32)
        m.modify(x - 16, y - 16, x + 48, y + 48, wall='RF4_COLN')
for (x, y0, y1) in ((128, 2112, 2176), (128, 2208, 2288)):
    m.face(x, y0, x + 16, y1, 'W', texture='RFP_PLN', special=182)
    sign(x, y0, x, y1, 'RF4_PIQU', 0, off=2)
for (x, y0, y1) in ((624, 2112, 2208), (624, 2240, 2336)):
    m.face(x - 16, y0, x, y1, 'E', texture='RFP_PLN', special=182)
    sign(x, y1, x, y0, 'RF4_PIQU', 0, off=2)
m.thing(200, 2200, T_VIKTOR_MIRROR)
block(352, 2384, 624, 2432, 24, 'RF4_PARQ', 'RFW_PANL', HALL)
m.thing(300, 2404, T_JUKEBOX, angle=270)
lamp(300, 2380, 40, 255, 170, 90, 120)
m.box(96, 2304, 128, 2368, HALL, ceil=112)                             # the side door, opened in RF04
door(192, 2432, 256, 2464, 46, 'RFD_SGL', HALL, 'N', lintel=104, track='RFP_PLN')     # the service door
m.box(176, 2464, 272, 2576, SERV)
# the bulbs that come on one after the other (dormant lamps, tid 570), in the lane, over the plaza, in the hall
for (x, y, z, r, g, b) in ((-700, 2350, 120, 255, 200, 110), (-500, 2350, 120, 255, 120, 90), (-300, 2350, 120, 120, 220, 120),
                           (-100, 2350, 120, 255, 210, 120), (40, 2350, 120, 240, 110, 90), (200, 1980, 130, 255, 200, 110),
                           (400, 1960, 130, 110, 210, 120), (560, 1980, 130, 255, 120, 90), (200, 2150, 170, 255, 214, 160),
                           (560, 2150, 170, 255, 214, 160), (200, 2350, 170, 255, 214, 160), (560, 2350, 170, 255, 214, 160)):
    lamp(x, y, z, r, g, b, 180, tid=BULB_TID, dormant=True)
m.thing(-400, 2352, T_AMB, args=(AMB_PARK, 45))
m.thing(376, 2250, T_AMB, args=(AMB_ROOM, 50))
scene(-864, 2408, -800, 2408, M_PARK)
across(-600, 2304, -600, 2400, 130, (SIGNAL_TID,), fields={'user_scene': M_TRAIN})
objective(-856, 2304, -856, 2400, 7)
checkpoint(-872, 2304, -872, 2400)
scene(120, 2304, 120, 2368, M_HALL)
m.trigger(178, 2488, 270, 2488, 130, (SIGNAL_TID,), fields={'user_scene': M_WAVES})
m.trigger(178, 2552, 270, 2552, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(x // UNIT, 2560 // UNIT) for x in range(176, 272, 16)}
m.thing(-700, 2330, T_9MM)
m.thing(-100, 2380, T_MAG)
m.thing(60, 2320, T_DRESS)
# E4: the lit park: the staff out of the lean-to sheds
spot(-584, 2448, BRA, PARK_WAVE, 270, skill='normal+')
spot(-600, 2424, ORD, PARK_WAVE, 270)
spot(-272, 2440, ORD, PARK_WAVE, 270)
spot(-252, 2424, POR, PARK_WAVE, 270)
spot(-560, 2476, ORD, PARK_WAVE, 270, skill='hard')
m.label(-880, 2310, 'D PARC ALLUME')
m.label(140, 2100, 'SALLE DE DANSE')

# --------------------------------------------------------------------------- autopilot route (dev)
route = [
    (-832, 2500, 0, 0, 1, 90),
    (-832, 2700, 0, 0, 0, 90),               # down the stair
    (-832, 2800, 0, 0, 0, 0),
    (-848, 2992, 1, 60, 0, 270),             # the motor, running: the bearing hot, the belt split
    (-1016, 2856, 1, 200, 0, 180),           # the box: NODE 0
    (-992, 3072, 1, 60, 0, 90),              # the dials
    (-720, 3072, 1, 2240, 0, 90),            # the lever: ARRET; the young woman; her palm
    (-600, 2912, 0, 0, 0, 0),
    (-450, 2928, 0, 0, 0, 0),
    (-440, 2928, 1, 60, 0, 0),               # the drawer: rags, oil can, spanner of 17
    (-600, 2912, 0, 0, 0, 0),
    (-700, 2860, 0, 0, 0, 0),
    (-960, 2860, 0, 0, 0, 0),                # round the motor
    (-1120, 2912, 0, 60, 0, 0),              # E1 along the gallery
    (-1632, 2912, 0, 0, 0, 0),
    (-1632, 3040, 0, 0, 0, 0),
    (-1632, 3280, 0, 60, 0, 0),              # E2 at the bend
    (-1632, 3296, 1, 60, 0, 180),            # the toolbox: canvas, copper staples
    (-1100, 3296, 0, 0, 0, 0),
    (-900, 3240, 0, 0, 0, 0),
    (-760, 3264, 1, 60, 0, 0),               # the spare fuse, 22.12.2022 (E3)
    (-830, 3200, 0, 120, 0, 0),
    (-832, 3120, 0, 0, 0, 0),
    (-848, 2992, 1, 220, 0, 270),            # the bearing cleaned
    (-848, 2992, 1, 40, 0, 270),             # the belt reinforced
    (-1060, 2976, 1, 440, 0, 180),           # the fuse JERMA
    (-720, 3072, 1, 640, 0, 90),             # MARCHE: the park lights up
    (-832, 2800, 0, 0, 0, 0),
    (-832, 2560, 0, 0, 0, 0),                # up the stair
    (-832, 2350, 0, 60, 0, 0),               # E4 in the lane
    (-400, 2352, 0, 0, 0, 0),
    (60, 2336, 0, 0, 0, 0),
    (160, 2336, 0, 420, 0, 0),               # the hall: the juke-box, the mirrors
    (224, 2420, 1, 40, 0, 90),               # the service door
    (224, 2500, 0, 0, 0, 0),
    (224, 2560, 0, 0, 0, 0),                 # exit
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
