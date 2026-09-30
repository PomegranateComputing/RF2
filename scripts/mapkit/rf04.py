#!/usr/bin/env python3
"""RF04 - Luna Park, personnel technique. Production map source (authored, not generated).

The first passage of the Luna Park in the novel (l. 451-551; docs/production/maps/RF04_FICHE.md), in its order:

  A  Chemin de service (start, south-east): inside the service door of RF02's exit, the path overgrown with grass
     along the hoarding, narrow rails across it (the warm rail), sheds; the workshop behind a loose board (secret).
  B  The guard's hut and the staff barrier: "Tu es en retard.", the card in the clock (06:06), the hook of keys
     (SOUS-STATION); the barrier lifts; looked back at, the hut is empty and ERREUR Ø is on the glass.
  C  The main alley: facades that still promise worlds; the Palais des Singes (l. 455), the decor of BROOKLYN BRIDGE
     (l. 523) with the technical corridor full of cables behind it; a hangar (loot, optional).
  D  The Niagara: the empty basin, the line of dry algae at shoulder height, LES CHUTES DU NIAGARA, the child's shoe
     in a black puddle (l. 523-527).
  E  The roller coaster: posts and braces under the track, the loading platform (a view over the basin and the
     alley), a length of track to walk.
  F  The dance hall: the gutted marquee, the turnstiles (617 -> 618), warped parquet, pitted mirrors (the reflections,
     the badge), the silent juke-box and the motor's three knocks (l. 531-549).
  G  The lane behind the roller-coaster track, grass between the slabs, the substation door (l. 551): exit.

Enemies continue the accepted adaptation: the staff of Sainte-Anne come in behind Viktor ("Celui ou ils entrent.",
"Toujours les memes.", l. 489-493). The guard, the park's people and every figure of the text are never targets.
Resources are Opus's PROVISIONAL stand-ins under the names of Astra's request LUNA-V01.

Units: 1 cell = 16. Sky at 256 (the facades of the park are 256 high). North = +y.
Usage: python scripts/mapkit/rf04.py   (writes src/maps/RF04.wad, build/RF04_plan.png, build/RF04_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT, texture_scales  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- materials
SKY = 256
ENV_PARK, ENV_ROOM, ENV_CORR, ENV_HALL = (32, 0), (30, 8), (13, 0), (30, 3)

PARK = Cell(floor=0, ceil=SKY, ftex='RFF_GRAV', ctex='F_SKY1', light=160, wall='RF4_FAC1', color=0xE2DED4,
            env=ENV_PARK, lower='RF4_BASC')
PATH = replace(PARK, ftex='RF4_HERB', wall='RF4_HANG', light=152)
RAILS = replace(PATH, ftex='RF4_DECA')
FORE = replace(PARK, ftex='RFF_GRAV', wall='RF4_HANG', light=156)
ALLEY = replace(PARK, ftex='RFF_GRAV', wall='RF4_FAC2', light=162)
RIM = replace(PARK, ftex='RFF_SLAB', wall='RF4_FAC3', lower='RF4_BASS', light=158)
BASIN = replace(PARK, floor=-96, ftex='RF4_BASF', wall='RF4_BASS', lower='RF4_BASS', light=150, env=(30, 1))
PUDDLE = replace(BASIN, ftex='RF4_FLAQ')
POSTS = replace(PARK, ftex='RF4_HERB', wall='RF4_ATEL', light=146)
LANE = replace(PARK, ftex='RF4_DALH', wall='RF4_HANG', light=144)
PLAZA = replace(PARK, ftex='RFF_GRAV', wall='RF4_FAC3', light=158)
CORR = Cell(floor=0, ceil=104, ftex='RFF_WOOD', ctex='RFP_CEID', light=92, wall='RF4_CABL', color=0xEADCC4, env=ENV_CORR)
HANGAR = Cell(floor=0, ceil=176, ftex='RFF_GRAV', ctex='RFP_CEID', light=104, wall='RF4_HANG', color=0xEAE0CC, env=ENV_ROOM)
ATELIER = Cell(floor=0, ceil=120, ftex='RFF_WOOD', ctex='RFP_CEID', light=88, wall='RF4_ATEL', color=0xEAD8C0, env=ENV_ROOM)
HALL = Cell(floor=0, ceil=192, ftex='RF4_PARQ', ctex='RFP_CEID', light=122, wall='RFP_PLN', color=0xF0E2C8, env=ENV_HALL)
VEST = Cell(floor=0, ceil=112, ftex='RFF_CONC', ctex='RFP_CEID', light=72, wall='RF4_BASC', color=0xE0D8C8, env=ENV_ROOM)

LAMP_GAIN = 0.55
DAY_GAIN = 0.45

# Thing types (MAPINFO DoomEdNums)
T_START, T_MAG, T_9MM, T_DRESS = 1, 30101, 30103, 30201
T_CHAIR, T_CABINET, T_BENCH = 30302, 30303, 30306
T_WAVE = 30405
ORD, BRA, POR = 1, 2, 3
T_LAMP, T_FLICKER, T_AMB, T_NOTE, T_LITTER, T_SIGNAL, T_SPOT = 30601, 30602, 30611, 30621, 30622, 30623, 30637
T_VIKTOR_MIRROR = 30651
T_CLOCK, T_KEYHOOK, T_RAIL, T_SHOE, T_TURN, T_MIRROR, T_JUKEBOX, T_GUARD = 30660, 30661, 30662, 30663, 30664, 30665, 30666, 30667
T_TOUR, T_WP = 30901, 30902
AMB_PARK, AMB_MOTOR, AMB_ROOM, AMB_DRIP, AMB_WIND = 6, 7, 3, 2, 1

# Scenes (RFLuna, src/zscript/rf/luna.zs)
L_HUT, L_CLOCK, L_KEYS, L_BARRIER, L_GLASS, L_RAIL, L_BROOKLYN, L_NIAGARA = 1, 2, 3, 4, 5, 6, 7, 8
L_SHOE, L_MOTOR, L_TURNSTILE, L_COUNTER, L_MIRROR, L_JUKEBOX, L_HALL, L_GLASSLOOK = 9, 10, 11, 12, 13, 14, 15, 16
SIGNAL_TID = 999
BARRIER_WAVE, JUKEBOX_WAVE = 100, 500
LOCK_SUBSTATION, LOCK_FROM_INSIDE = 6, 7

m = MapBuilder('RF04')


# --------------------------------------------------------------------------- helpers (as RF02)
def door(x0, y0, x1, y1, tag, tex, base, frame_side, lintel=112, track='RFP_DRK', **kw):
    """32-deep door strip: frame (lintel) cell on frame_side, door cell on the other side."""
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


def roofline(x0, y0, x1, y1, top, side, base):
    """A wall lower than the sky: a strip whose floor and ceiling are its top (the side texture is its riser)."""
    m.box(x0, y0, x1, y1, base, floor=top, ceil=top, ftex='RF2_ZINC', lower=side, wall=side)


def lamp(x, y, z, r=255, g=206, b=150, radius=200):
    m.thing(x, y, T_LAMP, args=(round(r * LAMP_GAIN), round(g * LAMP_GAIN), round(b * LAMP_GAIN), radius), z=z)


def daylight(x, y, z, radius=420):
    m.thing(x, y, T_LAMP, args=(round(206 * DAY_GAIN), round(208 * DAY_GAIN), round(214 * DAY_GAIN), radius), z=z)


SCALES = texture_scales(Path(__file__).resolve().parents[2] / 'src' / 'TEXTURES.rf04')


def sign(x0, y0, x1, y1, tex, zbottom, off=1, **flags):
    """Masked sign on a decor line, the visible face on the right of (x0,y0)->(x1,y1), `off` units from the wall."""
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=SCALES.get(tex, 4), texwidth=L, **flags)
    return m.decor[-1]


def across(x0, y0, x1, y1, special, args=(), objective=0, fields=None, repeat=False):
    """Walk-over trigger across several sectors: one line per run of identical cells (constant coordinate n*16+8)."""
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
    """Wave spot: the enemy appears out of sight when its line is crossed."""
    m.thing(x, y, T_WAVE, angle=angle, tid=tid, args=(kind,), skill=skill)


def litter(points):
    for (x, y, a) in points:
        m.thing(x, y, T_LITTER, angle=a)


def posts(x0, y0, x1, y1, step, base):
    """Roller-coaster posts: 16 x 16 solid timbers on a grid, the braces between them are decor lines."""
    xs = list(range(x0, x1 + 1, step))
    ys = list(range(y0, y1 + 1, step))
    for x in xs:
        for y in ys:
            m.carve(x, y, x + 16, y + 16)
    return xs, ys


# ============================================================================ A. CHEMIN DE SERVICE
m.box(768, 0, 896, 1056, PATH)
m.box(768, 384, 896, 448, RAILS)                                    # the narrow rails across the path (l. 463)
roofline(896, 0, 912, 1232, 176, 'RF2_PALI', PATH)                   # the hoarding, lower than the sky
m.face(800, 0, 864, 16, 'S', texture='RFD_SGL')                      # the service door Viktor came through (RF02)
m.thing(832, 72, T_START, angle=90)
m.thing(848, 40, T_SIGNAL, tid=SIGNAL_TID)
m.thing(832, 416, T_RAIL, args=(L_RAIL,))                            # the rail, warm, a light vibration
m.face(768, 384, 784, 448, 'W', texture='RFD_DBL')                  # the rails run under a shed door, shut
# the workshop, behind a loose board (secret; its key ATELIER stays on the hook)
m.box(640, 576, 752, 752, ATELIER, special=1024)
m.door(752, 624, 768, 672, 41, 'RF4_HANG', 'RF4_HANG', replace(PATH, ctex='RFP_CEID'), speed=24)   # doors under the sky get a
# ceiling of their own: a door sector with the sky's ceiling is not drawn when shut (the sky shows through)
block(656, 592, 736, 624, 32, 'RFW_TOP', 'RF4_ATEL', ATELIER)       # workbench
m.thing(700, 700, T_MAG)
m.thing(672, 720, T_9MM)
m.thing(720, 660, T_DRESS)
lamp(696, 664, 96, 230, 200, 160, 120)
m.thing(832, 640, T_AMB, args=(AMB_PARK, 50))
litter([(820, 180, 30), (860, 300, 140), (800, 560, 250), (850, 820, 70), (810, 960, 200)])
daylight(832, 300, 220)
daylight(832, 800, 220)
m.thing(860, 700, T_9MM)
checkpoint(768, 200, 896, 200)
m.label(780, 100, 'A CHEMIN DE SERVICE')

# ============================================================================ B. THE HUT AND THE STAFF BARRIER
m.box(640, 1056, 896, 1216, FORE)
# the hut: walls, roof and window are solid 3D floors under the open sky (l. 467): 80 x 96, in the north-east
HX0, HY0, HX1, HY1 = 816, 1120, 896, 1216
m.box(HX0, HY0, HX1, HY1, FORE, ftex='RFF_WOOD')
for (x0, y0, x1, y1) in ((HX0, HY1 - 16, HX1, HY1), (HX0, HY0, HX0 + 16, HY1)):                 # north and west walls
    m.slab(x0, y0, x1, y1, 0, 104, 'RF4_GUER')
m.slab(HX0 + 16, HY0, HX0 + 16 + 16, HY0 + 16, 0, 104, 'RF4_GUER')                                # beside the window
m.slab(HX1 - 16, HY0, HX1, HY0 + 16, 0, 104, 'RF4_GUER')
m.slab(HX0 + 32, HY0, HX1 - 16, HY0 + 16, 0, 40, 'RF4_GUER')                                      # sill
m.slab(HX0 + 32, HY0, HX1 - 16, HY0 + 16, 80, 104, 'RF4_GUER')                                    # lintel
m.slab(HX0 + 16, HY0 + 16, HX1, HY1 - 16, 104, 116, 'RF4_GUER', top='RF2_ZINC', bottom='RFP_CEID')  # the roof
m.slab(HX0, HY0, HX0 + 16, HY0 + 16, 104, 116, 'RF4_GUER', top='RF2_ZINC')
# the glass (L_GLASS: ERREUR Ø appears on it) between sill and lintel; the clock and the hook
sign(HX0 + 32, HY0, HX1 - 16, HY0, 'RF4_VIT0', 40, off=-8, blocking=True, user_scene=L_GLASS)
sign(HX0 + 36, HY1 - 16, HX1 - 20, HY1 - 16, 'RF4_POIN', 36, off=1)                               # clock on the inner north wall
sign(HX0, HY0 + 72, HX0, HY0 + 24, 'RF4_CLE5', 40, off=1, user_scene=L_KEYS)                       # hook on the outer west wall
m.thing(HX0 + 56, HY0 + 44, T_GUARD, angle=270)                                                   # seated, the register on his knees
m.thing(HX0 + 56, HY0 - 18, T_CLOCK, angle=90, args=(L_CLOCK,), z=40)                              # at the window: the card
m.thing(HX0 - 16, HY0 + 48, T_KEYHOOK, angle=0, args=(L_KEYS,), z=40)                              # at the hook
m.thing(HX0 + 40, HY0 + 16, T_SPOT, args=(L_GLASSLOOK,), z=60)                                      # the glass, looked back at
lamp(HX0 + 56, HY0 + 60, 90, 255, 214, 160, 90)
scene(768, 1016, 896, 1016, L_HUT)                                                                # "Tu es en retard."
objective(768, 1000, 896, 1000, 1)
# the staff barrier: a railing across the way west, lifted by the scene when the key is taken
m.box(320, 1056, 640, 1152, PATH)
sign(632, 1056, 632, 1152, 'RF2_RAMB', 0, off=0, blocking=True, user_scene=L_BARRIER)
roofline(320, 1040, 640, 1056, 176, 'RF2_PALI', PATH)                                              # the south hoarding
m.thing(760, 1100, T_AMB, args=(AMB_PARK, 40))
m.thing(700, 1180, T_DRESS)
daylight(720, 1120, 220)
# E1: they come in by the service door behind him ("Celui ou ils entrent", l. 489)
spot(832, 96, ORD, BARRIER_WAVE, 90)
spot(816, 140, ORD, BARRIER_WAVE, 90)
spot(856, 150, ORD, BARRIER_WAVE, 90, skill='hard')
checkpoint(600, 1056, 600, 1152)
m.label(660, 1180, 'B GUERITE')

# ============================================================================ C. THE MAIN ALLEY
m.box(64, 896, 320, 1920, ALLEY)
roofline(64, 880, 320, 896, 176, 'RF2_PALI', ALLEY)                                                # the entrance gate, from inside
roofline(128, 880, 256, 896, 176, 'RFM_GRIL', ALLEY)                                               # its padlocked gate
# west: the Palais des Singes (closed), then the decor of BROOKLYN BRIDGE; the gap of a missing board between them
m.modify(64, 896, 80, 1168, wall='RF4_FAC1')
sign(64, 1000, 64, 1112, 'RF4_SING', 120, off=1)
m.modify(64, 1168, 80, 1472, wall='RF4_BROO')
m.modify(64, 1472, 80, 1920, wall='RF4_FAC2')
# east: facades of shut attractions, the hangar's front and its doorway
m.modify(304, 896, 320, 1920, wall='RF4_FAC3')
for (x, y, a) in ((110, 980, 20), (280, 1130, 160), (140, 1300, 270), (250, 1540, 45), (100, 1700, 200), (290, 1820, 320)):
    m.thing(x, y, T_LITTER, angle=a)
sign(320, 1072, 320, 1024, 'RF4_AFF1', 80, off=1)                                                  # torn posters (l. 455)
sign(64, 1592, 64, 1640, 'RF4_AFF2', 80, off=1)
sign(64, 1712, 64, 1760, 'RF4_AFF3', 80, off=1)
sign(320, 1848, 320, 1800, 'RF4_AFF4', 80, off=1)
for y in (1100, 1500, 1800):
    daylight(192, y, 220)
m.thing(192, 1200, T_AMB, args=(AMB_PARK, 45))
m.thing(200, 1650, T_9MM)
m.thing(120, 1850, T_MAG)
scene(64, 1336, 320, 1336, L_MOTOR)                                                                # the motor beats under the park
m.label(80, 930, 'C ALLEE')

# the technical corridor behind the decor (l. 523): in through the gap of a missing board
m.box(32, 1168, 64, 1232, CORR, ceil=104)
m.box(-48, 1184, 32, 1504, CORR)
m.box(-128, 1440, -48, 1504, CORR)
block(-48, 1296, -16, 1328, 24, 'RFW_TOP', 'RF4_ATEL', CORR)
block(0, 1392, 32, 1424, 32, 'RFW_TOP', 'RF4_ATEL', CORR)
lamp(-8, 1260, 90, 255, 200, 140, 110)
m.thing(-8, 1350, T_FLICKER, args=(255, 196, 130, 120, 60), z=90)
m.thing(-8, 1450, T_AMB, args=(AMB_ROOM, 50))
# secret: a niche behind the Palais des Singes, through a loose board in the corridor's south wall
m.box(-48, 1072, 32, 1168, ATELIER, special=1024, light=76)
m.door(-32, 1168, 16, 1184, 42, 'RF4_CABL', 'RF4_CABL', CORR, speed=24)
m.thing(-8, 1110, T_MAG)
m.thing(-32, 1090, T_DRESS)
m.thing(16, 1090, T_9MM)
scene(32, 1208, 64, 1208, L_BROOKLYN)
objective(40, 1168, 40, 1232, 4)
# E2: two orderlies and a porte-registre at the far end of the corridor
spot(-104, 1472, ORD, 200, 0)
spot(-168, 1456, ORD, 200, 0)
spot(-168, 1520, POR, 200, 0)
spot(-176, 1400, ORD, 200, 0, skill='hard')
wake(-48, 1256, 32, 1256, 200)
m.label(-40, 1200, 'COULOIR TECHNIQUE')

# the hangar (optional: stored decor, cable drums, boats of the water chute)
m.box(336, 1152, 704, 1856, HANGAR)
door(304, 1440, 336, 1504, 30, 'RFD_DBL', HANGAR, 'W', lintel=128, track='RF4_HANG', kind='open')
m.box(576, 1856, 640, 1888, HANGAR, ceil=128)                                                       # back doorway to the plaza
for (x0, y0, x1, y1, h) in ((400, 1216, 496, 1312, 48), (560, 1216, 656, 1280, 64), (400, 1600, 432, 1760, 40),
                            (560, 1520, 688, 1584, 56), (480, 1696, 544, 1760, 32)):
    block(x0, y0, x1, y1, h, 'RFW_TOP', 'RF4_HANG', HANGAR)
for (x, y) in ((440, 1420), (620, 1680)):
    lamp(x, y, 150, 230, 210, 170, 220)
m.thing(520, 1400, T_AMB, args=(AMB_ROOM, 55))
m.thing(640, 1400, T_MAG)
m.thing(460, 1480, T_DRESS)
spot(640, 1300, ORD, 250, 180, skill='hard')
spot(620, 1780, ORD, 250, 180, skill='hard')
wake(360, 1440, 360, 1504, 250)
m.label(400, 1180, 'HANGAR')

# ============================================================================ D. THE NIAGARA
m.box(-768, 1088, -128, 1728, RIM)
m.box(-704, 1152, -192, 1600, BASIN)
for k, z in enumerate((-24, -48, -72)):                                                             # south-east stair
    m.box(-256, 1152 + 16 * k, -192, 1168 + 16 * k, BASIN, floor=z)
for k, z in enumerate((-24, -48, -72)):                                                             # the cascade stair, north
    m.box(-480, 1584 - 16 * k, -416, 1600 - 16 * k, BASIN, floor=z)
m.box(-352, 1216, -288, 1264, PUDDLE)                                                               # the black puddle
m.box(-368, 1232, -352, 1248, PUDDLE)
m.box(-336, 1264, -304, 1280, PUDDLE)
m.box(-288, 1232, -272, 1248, PUDDLE)
block(-640, 1648, -512, 1712, 96, 'RFF_SLAB', 'RF4_ROCH', RIM)                                     # the fake rocks of the cascade
block(-384, 1648, -256, 1712, 96, 'RFF_SLAB', 'RF4_ROCH', RIM)
block(-512, 1680, -384, 1712, 128, 'RFF_SLAB', 'RF4_ROCH', RIM)
sign(-512, 1680, -384, 1680, 'RF4_NIAG', 88, off=1)                                                # LES CHUTES DU NIAGARA
m.thing(-320, 1240, T_SHOE, args=(L_SHOE,))
# the railing round the basin (a drop of 96): open at the two stairs
for (x0, y0, x1, y1) in ((-704, 1150, -256, 1150), (-190, 1152, -190, 1600), (-706, 1152, -706, 1600),
                         (-704, 1602, -480, 1602), (-416, 1602, -192, 1602)):
    m.decor_line(x0, y0, x1, y1, 'RF2_RAMB', 0, blocking=True, yscale=4)
m.thing(-448, 1400, T_AMB, args=(AMB_WIND, 45))
m.thing(-448, 1200, T_AMB, args=(AMB_DRIP, 40))
daylight(-448, 1380, 220, 600)
m.thing(-720, 1120, T_9MM)
m.thing(-160, 1700, T_MAG)
m.thing(-680, 1500, T_DRESS)
scene(-120, 1440, -120, 1504, L_NIAGARA)
objective(-136, 1440, -136, 1504, 5)
# E3: orderlies down the stairs from the rim, the brancardier by the cascade stair
spot(-640, 1760, ORD, 300, 270)
spot(-320, 1760, ORD, 300, 270)
spot(-448, 1776, BRA, 300, 270)
spot(-600, 1768, ORD, 300, 270)
spot(-560, 1760, POR, 300, 270, skill='hard')
wake(-152, 1440, -152, 1504, 300)
checkpoint(-168, 1440, -168, 1504)
m.label(-760, 1100, 'D NIAGARA')

# ============================================================================ E. THE ROLLER COASTER
m.box(-768, 1728, 48, 2304, POSTS)
# the track overhead (not walkable): two lanes and the west turn; the posts are solid columns under it
m.slab(-752, 1792, -128, 1824, 144, 160, 'RF4_ATEL', top='RF4_VOIE', bottom='RF4_ATEL')
m.slab(-752, 2176, -128, 2208, 144, 160, 'RF4_ATEL', top='RF4_VOIE', bottom='RF4_ATEL')
m.slab(-752, 1824, -720, 2176, 144, 160, 'RF4_ATEL', top='RF4_VOIE', bottom='RF4_ATEL')
for x in range(-752, -127, 96):
    for y in (1792, 2176):
        m.slab(x, y, x + 16, y + 16, 0, 144, 'RF4_ATEL')
for y in range(1888, 2177, 96):
    m.slab(-752, y, -736, y + 16, 0, 144, 'RF4_ATEL')
for x in range(-752, -224, 96):                                                                      # braces between the posts
    for y in (1800, 2184):
        m.decor_line(x + 17, y, x + 95, y, 'RF4_BOIS', 0, yscale=4, texwidth=78)
# the loading platform, a roof of canvas, steps from the alley; the station track walkable to the west
m.box(-128, 1824, 80, 1952, POSTS, floor=48, ftex='RFF_WOOD', lower='RF4_ATEL')
for k, z in enumerate((32, 16)):
    m.box(80 + 16 * k, 1856, 96 + 16 * k, 1920, ALLEY, floor=z, ftex='RFF_WOOD', lower='RF4_ATEL')
m.slab(-128, 1824, 80, 1952, 136, 144, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
m.slab(-640, 1872, -128, 1904, 32, 48, 'RF4_ATEL', top='RF4_VOIE', bottom='RF4_ATEL')                # the station track, walkable
for k, z in enumerate((32, 16)):                                                                    # steps up from the north field
    m.box(-64, 1952 + 16 * k, 0, 1968 + 16 * k, POSTS, floor=z, ftex='RFF_WOOD', lower='RF4_ATEL')
m.thing(-40, 1900, T_BENCH, angle=0)
m.thing(-600, 2000, T_AMB, args=(AMB_WIND, 40))
daylight(-400, 2000, 220, 600)
m.thing(-200, 2250, T_9MM)
m.thing(-680, 2260, T_MAG)
m.thing(40, 1840, T_DRESS)
objective(-768, 1736, -128, 1736, 6)
# a see-through fence closes the lane behind the posts (the door of the substation is seen, not reached)
m.decor_line(-768, 2296, 48, 2296, 'RFM_GRIL', 0, blocking=True, yscale=4)
# E4: orderlies among the posts, a porte-registre on the station track
spot(-600, 2240, ORD, 400, 270)
spot(-360, 2250, ORD, 400, 270)
spot(-420, 2100, ORD, 400, 0)
spot(-500, 2100, POR, 400, 270)                                   # on the ground: from the walkway (1888) the autopilot could not reach it
spot(-200, 2100, BRA, 400, 180, skill='hard')
wake(-768, 1752, -128, 1752, 400)
m.label(-760, 1740, 'E MONTAGNES RUSSES')

# ============================================================================ F. THE DANCE HALL
m.box(64, 1920, 624, 2048, PLAZA)
m.box(336, 1888, 640, 1920, PLAZA)
# the gutted marquee: a canopy of canvas with holes, over the turnstiles
m.slab(176, 1968, 560, 2048, 136, 144, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
m.box(336, 1984, 400, 2032, PLAZA)                                                                    # holes torn in the canvas
m.box(464, 1968, 560, 2000, PLAZA)
sign(336, 2048, 496, 2048, 'RF4_DANS', 152, off=1)                                                 # SALLE DE DANSE, faded
# the entrance and its turnstiles (l. 531): two gaps, the first with the counter
m.box(240, 2048, 496, 2080, HALL, ceil=128, ftex='RFF_SLAB')
for (x0, x1) in ((240, 288), (336, 384), (432, 496)):
    block(x0, 2048, x1, 2080, 40, 'RFM_TOP', 'RF4_TOUR', m.cells[(x0 // UNIT, 2048 // UNIT)])
sign(256, 2048, 288, 2048, 'RF4_C617', 14, off=1, user_scene=L_COUNTER)                             # the counter, on its post
m.decor_line(290, 2064, 334, 2064, 'RF2_RAMB', 0, blocking=True, yscale=4, user_scene=L_TURNSTILE)  # the bar that turns
m.decor_line(386, 2064, 430, 2064, 'RF2_RAMB', 0, blocking=True, yscale=4)                           # barred for good
m.thing(312, 2036, T_TURN, angle=90, args=(L_TURNSTILE,), z=24)
# the hall: warped parquet, pitted mirrors on both long walls, columns, the stage and the juke-box
m.box(128, 2080, 624, 2432, HALL)
for x in (256, 480):
    for y in (2176, 2320):
        m.carve(x, y, x + 32, y + 32)
        m.modify(x - 16, y - 16, x + 48, y + 48, wall='RF4_COLN')
for (x, y0, y1) in ((128, 2112, 2176), (128, 2208, 2288)):                                          # mirrors, west wall
    m.face(x, y0, x + 16, y1, 'W', texture='RFP_PLN', special=182)
    sign(x, y0, x, y1, 'RF4_PIQU', 0, off=2)
for (x, y0, y1) in ((624, 2112, 2208), (624, 2240, 2336)):                                           # mirrors, east wall
    m.face(x - 16, y0, x, y1, 'E', texture='RFP_PLN', special=182)
    sign(x, y1, x, y0, 'RF4_PIQU', 0, off=2)
m.thing(160, 2160, T_MIRROR, angle=180, args=(L_MIRROR,), z=0)
m.thing(200, 2200, T_VIKTOR_MIRROR)                                                                  # his reflection (F02-08)
block(352, 2384, 624, 2432, 24, 'RF4_PARQ', 'RFW_PANL', HALL)                                       # the orchestra stage
m.thing(160, 2400, T_JUKEBOX, angle=0, args=(L_JUKEBOX,))
# secret: the orchestra's box behind the stage (a curtain panel)
m.box(448, 2448, 624, 2512, ATELIER, special=1024, floor=24, light=80)
m.door(512, 2432, 560, 2448, 43, 'RFW_PANL', 'RFW_PANL', replace(HALL, floor=24), speed=24)
m.thing(480, 2480, T_MAG)
m.thing(590, 2480, T_DRESS)
for (x, y) in ((200, 2150), (560, 2150), (200, 2350), (560, 2350)):
    lamp(x, y, 150, 255, 226, 180, 150)
m.thing(376, 2250, T_FLICKER, args=(210, 214, 220, 180, 40), z=170)                                  # morning light by fragments
m.thing(376, 2250, T_AMB, args=(AMB_ROOM, 50))
m.thing(560, 2300, T_9MM)
m.thing(160, 2280, T_MAG)
objective(64, 1928, 624, 1928, 7)
checkpoint(64, 1944, 624, 1944)
scene(240, 2072, 496, 2072, L_HALL)
# E5: after the three knocks, they come through the marquee and from behind the stage
spot(400, 1960, ORD, JUKEBOX_WAVE, 90)
spot(160, 1970, ORD, JUKEBOX_WAVE, 90)
spot(560, 1960, POR, JUKEBOX_WAVE, 90)
spot(600, 2400, ORD, JUKEBOX_WAVE, 180, skill='normal+')
spot(300, 1900, ORD, JUKEBOX_WAVE, 90, skill='hard')
spot(560, 1992, ORD, JUKEBOX_WAVE, 90, skill='hard')         # a brancardier could not pass the turnstiles (80 wide)
m.label(140, 2100, 'F SALLE DE DANSE')
# the side door to the lane behind the track: opened from the hall only (the shortcut is opened by progression)
door(96, 2304, 128, 2368, 44, 'RFD_SGL', HALL, 'E', lintel=112, track='RFP_PLN', lock=LOCK_FROM_INSIDE, lockside='W')

# ============================================================================ G. THE LANE AND THE SUBSTATION DOOR
m.box(-896, 2304, 96, 2400, LANE)
door(-864, 2400, -800, 2432, 45, 'RF4_PSST', replace(LANE, ctex='RFP_CEID'), 'N', lintel=104, track='RF4_BASC', lock=LOCK_SUBSTATION)
m.box(-880, 2432, -784, 2528, VEST)
m.thing(-832, 2480, T_AMB, args=(AMB_MOTOR, 100))                                                   # the motor, below
lamp(-832, 2480, 80, 255, 210, 120, 90)
m.thing(-832, 2300, T_AMB, args=(AMB_MOTOR, 90))
m.trigger(-878, 2488, -786, 2488, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(x // UNIT, 2496 // UNIT) for x in range(-880, -784, 16)}
objective(56, 2304, 56, 2400, 10)
checkpoint(40, 2304, 40, 2400)
litter([(-600, 2350, 40), (-300, 2330, 170), (-100, 2370, 300)])
daylight(-400, 2352, 220, 600)
m.thing(-700, 2360, T_9MM)
m.thing(-860, 2390, T_DRESS)
# E6: the last lock before the door, from both ends of the lane
m.box(-640, 2400, -528, 2496, LANE, ceil=120, ctex='RFP_CEID', light=110)                            # lean-to sheds on the lane
m.box(-320, 2400, -224, 2464, LANE, ceil=120, ctex='RFP_CEID', light=110)
spot(-584, 2448, BRA, 600, 270, skill='normal+')
spot(-600, 2424, ORD, 600, 270)
spot(-272, 2440, ORD, 600, 270)
spot(-252, 2424, POR, 600, 270)
spot(-560, 2476, ORD, 600, 270, skill='hard')
wake(24, 2304, 24, 2400, 600)
m.label(-880, 2310, 'G SOUS-STATION')

# --------------------------------------------------------------------------- autopilot route (dev)
route = [
    # (x, y, use, wait, weapon, angle): the normal path, ordinary commands; scenes used on the way
    (832, 120, 0, 0, 1, 90),
    (832, 416, 1, 60, 0, 270),               # the warm rail (faced from where it stops)
    (832, 700, 0, 0, 0, 0),
    (832, 1040, 0, 400, 0, 90),              # the hut: "Tu es en retard." ... "Si tu veux."
    (872, 1092, 1, 420, 0, 90),              # the card: 06:06; "Celui ou ils entrent."
    (776, 1168, 1, 360, 0, 0),               # the key of the substation; the barrier lifts
    (700, 1104, 0, 0, 0, 0),
    (600, 1104, 0, 60, 0, 0),                # E1 behind him
    (560, 1100, 1, 60, 0, 6),                # he turns round: the hut is empty, ERREUR Ø
    (400, 1104, 0, 0, 0, 0),
    (192, 1104, 0, 0, 0, 0),
    (192, 1200, 0, 0, 0, 0),
    (48, 1200, 0, 0, 0, 0),                  # the gap in the decor
    (-8, 1240, 0, 60, 0, 0),                 # E2
    (-8, 1276, 0, 0, 0, 0),
    (-8, 1470, 0, 0, 0, 0),
    (-150, 1472, 0, 60, 0, 0),               # E3 (the rim)
    (-160, 1624, 0, 0, 0, 0),                # north along the east rim
    (-448, 1624, 0, 0, 0, 0),                # the rim under the rocks of the cascade
    (-448, 1560, 0, 0, 0, 0),                # down the cascade stair into the basin
    (-448, 1400, 0, 0, 0, 0),
    (-296, 1240, 0, 0, 0, 0),
    (-296, 1240, 1, 330, 0, 180),            # the shoe in the puddle
    (-224, 1220, 0, 0, 0, 0),
    (-224, 1140, 0, 0, 0, 0),                # up the south-east stair
    (-160, 1120, 0, 0, 0, 0),
    (-160, 1624, 0, 0, 0, 0),                # the east rim, north
    (-200, 1690, 0, 0, 0, 0),                # the passage between the rocks and the rim
    (-200, 1760, 0, 60, 0, 0),               # E4 among the posts
    (-400, 1848, 0, 0, 0, 0),
    (-688, 1848, 0, 0, 0, 0),                # round the west end of the station track
    (-688, 2000, 0, 0, 0, 0),
    (-300, 2040, 0, 0, 0, 0),
    (-32, 2040, 0, 0, 0, 0),
    (-32, 1990, 0, 0, 0, 0),                 # up the steps onto the platform
    (40, 1890, 0, 0, 0, 0),
    (120, 1890, 0, 0, 0, 0),                 # down into the alley
    (192, 1990, 0, 60, 0, 0),
    (312, 2010, 1, 120, 0, 90),              # the turnstile: 618
    (312, 2110, 0, 0, 0, 0),
    (200, 2160, 0, 0, 0, 0),
    (176, 2160, 1, 360, 0, 180),             # the mirror of the badge
    (180, 2350, 0, 0, 0, 0),
    (180, 2370, 1, 60, 0, 90),               # the juke-box: the tarpaulin
    (180, 2370, 1, 240, 0, 90),              # the key: nothing; three knocks (E5)
    (300, 2250, 0, 200, 0, 0),
    (160, 2336, 0, 0, 0, 0),
    (140, 2336, 1, 60, 0, 180),              # the side door, from inside
    (60, 2336, 0, 0, 0, 0),
    (8, 2340, 0, 0, 0, 0),
    (-400, 2352, 0, 60, 0, 0),               # E6
    (-832, 2352, 0, 0, 0, 0),
    (-832, 2380, 1, 60, 0, 90),              # the door of the substation (the key)
    (-832, 2500, 0, 0, 0, 0),                # exit
]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


# --------------------------------------------------------------------------- build
def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF04.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF04_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF04_plan.png', scale=0.25)
    # the key is given by the hut's scene, not picked up: the hook counts as the key for the check
    report2 = m.check({T_KEYHOOK: LOCK_SUBSTATION}, m.exit_cells, decor_types=(T_GUARD, T_SPOT))
    print('RF04 built:', m.stats)
    print('check:', {k: v for k, v in report2.items() if k != 'unreachable_things'})
    if report2['unreachable_things']:
        print('UNREACHABLE THINGS:', report2['unreachable_things'])
    from encounters import analyze
    problems = analyze(m, spawn_view=True)
    print('encounters/walls:', 'clean' if not problems else f'{len(problems)} problem(s)')
    for line in problems:
        print('  ' + line)
    return report2


if __name__ == '__main__':
    main()
