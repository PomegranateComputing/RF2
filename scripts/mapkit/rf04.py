#!/usr/bin/env python3
"""RF04 - Luna Park, personnel technique. Production map source (authored, not generated).

Recomposed on 01/10/2026 around the park itself (owner's review: the first version did not give the Luna Park's
identity): the esplanade, the long basin of the water chute, the rocks and the roller coaster against the sky, the
attractions' facades. The park is a declared reconstruction shared with RF05 (scripts/mapkit/luna_park.py,
docs/production/maps/RF04_RELEVE_PLAN.md). The novel's order (l. 451-551) is kept:

  the staff door and the service path (the warm rail) -> the guard's hut (06:06, the key SOUS-STATION, the barrier;
  looked back at, the hut is empty and ERREUR Ø is on the glass) -> the first view of the park -> BROOKLYN BRIDGE and
  the technical corridor behind it -> the Niagara (the basin, the line of algae, the child's shoe) -> the trestles and
  the loading platform -> the marquee and the turnstiles (617 -> 618) -> the dance hall (the reflections, the silent
  juke-box, the motor's three knocks) -> the lane behind the track -> the substation door (exit to RF05).

Enemies continue the accepted adaptation: the staff of Sainte-Anne come in behind Viktor ("Toujours les memes",
l. 493). The guard, the park's people and every figure of the text are never targets. Resources: Astra's tranche 01,
Codex's lots as they come, Opus's provisional stand-ins under the names of ZONE_PILOTE_RF04.md.

Usage: python scripts/mapkit/rf04.py   (writes src/maps/RF04.wad, build/RF04_plan.png, build/RF04_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT, texture_scales  # noqa: E402
import luna_park as lp  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

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
LOCK_SUBSTATION, LOCK_FROM_INSIDE, LOCK_SERVICE = 6, 7, 8

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


# ============================================================================ THE PARK (shared with RF05)
A = lp.build_park(m, sign)
SVC_X0, SVC_X1 = lp.SVC_X0, lp.SVC_X1
PATH = lp.PATH

# ============================================================================ A. THE SERVICE PATH
m.thing(*A['start'], T_START, angle=90)
m.thing(1840, 40, T_SIGNAL, tid=SIGNAL_TID)
m.thing(*A['rail'], T_RAIL, args=(L_RAIL,))                          # the rail, warm, a light vibration (l. 463)
# the workshop behind a loose board (secret; its key ATELIER stays on the hook)
m.door(1696, 640, 1712, 688, 41, 'RF4_CABL', 'RF4_CABL', lp.CORR, speed=24)   # a loose board in the corridor's east wall
block(1712, 736, 1760, 768, 32, 'RFW_TOP', 'RF4_ATEL', lp.ATELIER)    # workbench
m.thing(1744, 664, T_MAG)
m.thing(1732, 700, T_9MM)
m.thing(1728, 680, T_DRESS)
lamp(*A['atelier'], 96, 230, 200, 160, 120)
m.thing(1856, 640, T_AMB, args=(AMB_PARK, 50))
litter([(1840, 180, 30), (1880, 300, 140), (1820, 560, 250), (1870, 820, 70), (1830, 960, 200), (1860, 1380, 110)])
for y in (300, 800, 1400):
    daylight(1856, y, 220)
m.thing(1880, 860, T_9MM)
checkpoint(SVC_X0, 200, SVC_X1, 200)
m.label(1800, 100, 'A CHEMIN DE SERVICE')

# ============================================================================ B. THE HUT AND THE STAFF BARRIER
HX0, HY0, HX1, HY1 = lp.HUT
m.box(HX0, HY0, HX1, HY1, lp.FORE, ftex='RFF_WOOD')
m.slab(HX0, HY0, HX0 + 16, HY1, 0, 104, 'RF4_GUER')                                               # west wall
m.slab(HX0 + 16, HY1 - 16, HX1, HY1, 0, 104, 'RF4_GUER')                                          # north wall
m.slab(HX0 + 16, HY0, HX1, HY0 + 16, 0, 104, 'RF4_GUER')                                          # south wall
m.slab(HX1 - 16, HY0 + 16, HX1, HY0 + 64, 0, 104, 'RF4_GUER')                                     # east wall: the clock's part
m.slab(HX1 - 16, HY1 - 32, HX1, HY1 - 16, 0, 104, 'RF4_GUER')                                     # beside the window
m.slab(HX1 - 16, HY0 + 64, HX1, HY1 - 32, 0, 40, 'RF4_GUER')                                      # sill
m.slab(HX1 - 16, HY0 + 64, HX1, HY1 - 32, 80, 104, 'RF4_GUER')                                    # lintel
m.slab(HX0, HY0, HX1, HY1, 104, 116, 'RF4_GUER', top='RF2_ZINC', bottom='RFP_CEID')              # the roof
sign(HX1, HY0 + 64, HX1, HY1 - 32, 'RF4_VIT0', 40, off=-8, blocking=True, user_scene=L_GLASS)     # the glass (ERREUR Ø)
sign(HX1, HY0 + 24, HX1, HY0 + 48, 'RF4_POIN', 36, off=1)                                         # the clock (24 u), facing the path
sign(HX0 + 72, HY1, HX0 + 24, HY1, 'RF4_CLE5', 40, off=1, user_scene=L_KEYS)                      # the hook, on the north face
m.thing(HX0 + 48, HY0 + 80, T_GUARD, angle=0)                                                     # seated, the register on his knees
m.thing(HX1 + 10, HY0 + 36, T_CLOCK, angle=180, args=(L_CLOCK,), z=40)                             # at the clock: the card
m.thing(HX0 + 48, HY1 + 12, T_KEYHOOK, angle=270, args=(L_KEYS,), z=40)                            # at the hook
m.thing(HX1 + 4, HY0 + 80, T_SPOT, args=(L_GLASSLOOK,), z=60)                                       # the glass, looked back at
lamp(HX0 + 48, HY0 + 72, 90, 255, 214, 160, 90)
scene(SVC_X0, 904, SVC_X1, 904, L_HUT)                                                            # "Tu es en retard."
objective(SVC_X0, 888, SVC_X1, 888, 1)
# the staff barrier: a railing across the path north of the hut, lifted by the scene when the key is taken
sign(SVC_X0, lp.BARRIER_Y, SVC_X1, lp.BARRIER_Y, 'RF2_RAMB', 0, off=0, blocking=True, user_scene=L_BARRIER)
m.thing(1856, 1150, T_AMB, args=(AMB_PARK, 40))
m.thing(1700, 1180, T_DRESS)
daylight(1728, 1100, 220)
# E1: they come in by the staff door behind him ("Celui ou ils entrent", l. 489)
spot(1856, 96, ORD, BARRIER_WAVE, 90)
spot(1832, 140, ORD, BARRIER_WAVE, 90)
spot(1880, 150, ORD, BARRIER_WAVE, 90, skill='hard')
checkpoint(SVC_X0, 1240, SVC_X1, 1240)
m.label(1680, 980, 'B GUERITE')

# ============================================================================ C. THE FIRST VIEW, BROOKLYN BRIDGE AND ITS CORRIDOR
scene(1544, lp.TURN_Y0, 1544, lp.TURN_Y1, L_MOTOR)                                                # the motor beats under the park
objective(1528, lp.TURN_Y0, 1528, lp.TURN_Y1, 4)                                                  # the first view: the bridge
scene(1576, 672, 1576, 736, L_BROOKLYN)
litter([(1400, 1500, 30), (1300, 1250, 160), (1450, 900, 270), (1250, 600, 45), (1400, 300, 200), (600, 500, 320),
        (500, 900, 120), (1250, 1700, 60), (900, 1700, 250), (700, 300, 10)])
for (x, y) in ((1300, 1500), (1300, 500), (640, 900), (640, 1700), (1000, 2100)):
    daylight(x, y, 300, 600)
for (x, y) in ((1200, 1200), (700, 700)):
    m.thing(x, y, T_AMB, args=(AMB_PARK, 45))
m.thing(1420, 1300, T_9MM)
m.thing(1350, 760, T_MAG)
# inside the corridor: crates, drums of cable, a flickering bulb; a niche behind a loose board (secret)
block(1600, 560, 1632, 592, 24, 'RFW_TOP', 'RF4_ATEL', lp.CORR)
block(1664, 448, 1696, 480, 32, 'RFW_TOP', 'RF4_ATEL', lp.CORR)
lamp(1648, 600, 90, 255, 200, 140, 110)
m.thing(1648, 400, T_FLICKER, args=(255, 196, 130, 120, 60), z=90)
m.thing(1648, 500, T_AMB, args=(AMB_ROOM, 50))
m.box(1712, 352, 1776, 448, lp.ATELIER, special=1024, light=76)
m.door(1696, 384, 1712, 416, 42, 'RF4_CABL', 'RF4_CABL', lp.CORR, speed=24)
m.thing(1744, 370, T_MAG)
m.thing(1744, 430, T_DRESS)
# E2: two orderlies and a porte-registre come in by the far end of the corridor, round its corner
spot(1568, 288, ORD, 200, 0)
spot(1500, 296, ORD, 200, 0)
spot(1460, 240, POR, 200, 0)
spot(1500, 200, ORD, 200, 0, skill='hard')
wake(lp.CORR_X0, 648, lp.CORR_X1, 648, 200)
objective(1528, 256, 1528, 320, 5)                                                                # out of the corridor: the basin
m.label(1600, 760, 'C COULOIR TECHNIQUE')

# ============================================================================ D. THE NIAGARA
bx0, by0, bx1, by1 = lp.BAS
m.thing(*A['shoe'], T_SHOE, args=(L_SHOE,))
scene(896, 376, 1024, 376, L_NIAGARA)
m.thing(960, 900, T_AMB, args=(AMB_WIND, 45))
m.thing(960, 1300, T_AMB, args=(AMB_DRIP, 40))
daylight(960, 900, 200, 600)
m.thing(800, 600, T_DRESS)
m.thing(1120, 1200, T_9MM)
m.thing(800, 1320, T_MAG)
# E3: at the shoe they come down into the basin by the rocks of the cascade (out of sight from the bottom: the esplanade
# north-west of the basin, on lines that lead to the rocks)
spot(640, 1800, ORD, 300, 300)
spot(700, 1840, ORD, 300, 300)
spot(660, 1760, BRA, 300, 300)
spot(720, 1790, ORD, 300, 300, skill='normal+')
spot(600, 1840, POR, 300, 300, skill='hard')
wake(lp.BAS[0], 1224, lp.BAS[2], 1224, 300)
checkpoint(896, 440, 1024, 440)
m.label(bx0, by0 - 40, 'D NIAGARA')

# ============================================================================ E. THE TRESTLES AND THE LOADING PLATFORM
objective(lp.BAS[0], 1480, 896, 1480, 6)                                                         # out of the basin: the station
m.thing(*A['quai'], T_BENCH, angle=180)
m.thing(350, 700, T_AMB, args=(AMB_WIND, 40))
daylight(352, 800, 260, 600)
m.thing(340, 1000, T_9MM)
m.thing(520, 1560, T_DRESS)
m.thing(460, 1250, T_MAG)
# E4: as he climbs out, more come round the chute's tower from the north of the park
spot(1080, 2040, ORD, 400, 225)
spot(1250, 2070, ORD, 400, 225)
spot(1200, 2060, POR, 400, 225)
spot(1290, 2170, ORD, 400, 225, skill='normal+')
spot(1300, 2100, BRA, 400, 225, skill='hard')
wake(lp.BAS[0], 1496, 896, 1496, 400)
m.label(300, 230, 'E MONTAGNES RUSSES')

# ============================================================================ F. THE MARQUEE, THE TURNSTILES, THE DANCE HALL
hx0, hy0, hx1, hy1 = lp.HALLB
ix0, iy0, ix1, iy1 = lp.HALL_IN
for (x0, x1) in ((576, 624), (672, 720), (768, 832)):                                               # three turnstile posts
    block(x0, hy0, x1, iy0, 40, 'RFM_TOP', 'RF4_TOUR', m.cells[(x0 // UNIT, hy0 // UNIT)])
sign(592, hy0, 624, hy0, 'RF4_C617', 0, off=1, user_scene=L_COUNTER)                                 # the counter, the post's face
m.decor_line(626, 1936, 670, 1936, 'RF2_RAMB', 0, blocking=True, yscale=4, user_scene=L_TURNSTILE)   # the bar that turns
m.decor_line(722, 1936, 766, 1936, 'RF2_RAMB', 0, blocking=True, yscale=4)                          # barred for good
m.thing(648, 1904, T_TURN, angle=90, args=(L_TURNSTILE,), z=24)
# the room: warped parquet, pitted mirrors on both long walls, columns, the stage and the juke-box
for (x, y) in ((592, 2032), (800, 2032), (592, 2112), (800, 2112)):
    m.carve(x, y, x + 32, y + 32)
    m.modify(x - 16, y - 16, x + 48, y + 48, wall='RF4_COLN')
for (y0, y1) in ((2000, 2032), (2048, 2080), (2096, 2128)):     # mirrors, west wall: three narrow panels 48 apart, the
    m.face(ix0, y0, ix0 + 16, y1, 'W', texture='RFP_PLN', special=182)   # three outfits of the scene (luna.zs)
    m.carve(ix0 - 16, y0, ix0, y1)                       # a mirror (Line_Mirror) must be a one-sided wall: void behind
    sign(ix0, y0, ix0, y1, 'RF4_PIQU', 0, off=2)
for (y0, y1) in ((1984, 2064), (2096, 2144)):                                                        # mirrors, east wall
    m.face(ix1 - 16, y0, ix1, y1, 'E', texture='RFP_PLN', special=182)
    m.carve(ix1, y0, ix1 + 16, y1)
    sign(ix1, y1, ix1, y0, 'RF4_PIQU', 0, off=2)
m.thing(ix0 + 32, 2064, T_MIRROR, angle=180, args=(L_MIRROR,), z=0)                                  # the mirror of the badge
m.thing(704, 2080, T_VIKTOR_MIRROR)                                                                   # his reflection
block(672, 2160, ix1, iy1, 24, 'RF4_PARQ', 'RFW_PANL', lp.HALL)                                      # the orchestra stage
m.thing(648, 2188, T_JUKEBOX, angle=270, args=(L_JUKEBOX,))                                          # by the stage
# secret: the orchestra's box in the east wing, by a curtain panel at the stage's end
ox0, oy0, ox1, oy1 = A['orchestra']
m.door(ix1, 2160, ox0, 2208, 43, 'RFW_PANL', 'RFW_PANL', replace(lp.HALL, floor=24), speed=24)
vx0, vy0, vx1, vy1 = lp.SERVICE_DOOR                                                              # the service door: shut
m.door(vx0, vy0, vx1, vy1, 46, 'RFD_OAKS', 'RF4_ATEL', replace(lp.ATELIER, floor=24), lock=LOCK_SERVICE)
m.thing(950, 2184, T_MAG)
m.thing(985, 2160, T_DRESS)
for (x, y) in ((560, 2000), (850, 2000), (560, 2160), (850, 2120)):
    lamp(x, y, 150, 255, 226, 180, 150)
m.thing(704, 2080, T_FLICKER, args=(210, 214, 220, 180, 40), z=170)                                   # morning light by fragments
m.thing(704, 2080, T_AMB, args=(AMB_ROOM, 50))
m.thing(870, 2040, T_9MM)
m.thing(540, 2100, T_MAG)
objective(576, 1832, 832, 1832, 7)
checkpoint(576, 1816, 832, 1816)
scene(576, 1960, 832, 1960, L_HALL)
# E5: after the three knocks, they come through the marquee (out of sight of the juke-box: both sides of the vestibule)
spot(520, 1880, ORD, JUKEBOX_WAVE, 0)
spot(900, 1880, ORD, JUKEBOX_WAVE, 180)
spot(880, 1830, POR, JUKEBOX_WAVE, 135)
spot(540, 1830, ORD, JUKEBOX_WAVE, 45, skill='normal+')
spot(940, 1840, ORD, JUKEBOX_WAVE, 180, skill='hard')
spot(480, 1840, ORD, JUKEBOX_WAVE, 0, skill='hard')          # a brancardier could not pass the turnstiles (80 wide)
m.label(hx0, hy0 - 24, 'F SALLE DE DANSE')
# the side door to the lane behind the track: opened from the hall only (the shortcut is opened by progression)
sx0, sy0, sx1, sy1 = lp.SIDE_DOOR                                                                 # its frame is the park's
m.door(sx0, sy0, sx1, sy0 + 16, 44, 'RFD_OAKS', 'RFP_PLN', lp.HALL, lock=LOCK_FROM_INSIDE, lockside='N')

# ============================================================================ G. THE LANE AND THE SUBSTATION DOOR
lx0, ly0, lx1, ly1 = lp.LANE_BOX
dx0, dy0, dx1, dy1 = lp.SUB_DOOR
m.door(dx0, dy0 + 16, dx1, dy1, 45, 'RF4_PSST', 'RF4_BASC', lp.VEST, lock=LOCK_SUBSTATION)        # its frame is the park's
m.box(dx0 - 16, dy1, dx1 + 16, dy1 + 64, lp.VEST)
lp.walls(m, dx0 - 16, dy1, dx1 + 16, dy1 + 64, 'RF4_BASC')
m.thing((dx0 + dx1) // 2, dy1 + 32, T_AMB, args=(AMB_MOTOR, 100))                                  # the motor, below
lamp((dx0 + dx1) // 2, dy1 + 32, 80, 255, 210, 120, 90)
m.thing(1500, 2290, T_AMB, args=(AMB_MOTOR, 90))
m.trigger(dx0 - 14, dy1 + 40, dx1 + 14, dy1 + 40, 130, (SIGNAL_TID,), fields={'user_outro': 1})
m.exit_cells = {(x // UNIT, (dy1 + 48) // UNIT) for x in range(dx0 - 16, dx1 + 16, 16)}
objective(512, 2264, 608, 2264, 10)                                                               # out of the side door
checkpoint(600, ly0, 600, ly1)
litter([(700, 2300, 40), (1100, 2260, 170), (1450, 2310, 300)])
daylight(1000, 2288, 220, 600)
m.thing(1180, 2300, T_9MM)
m.thing(1600, 2260, T_DRESS)
# E6: the last lock before the door, out of the sheds dug into the rocks (hidden from the lane's west end)
(s1, s2, s3) = lp.SHEDS
spot(s1[0] + 48, ly1 + 16, BRA, 600, 180, skill='normal+')       # its 80 width fits the shed's mouth and the lane
spot(s2[0] + 24, ly1 + 32, ORD, 600, 180)
spot(s2[0] + 72, ly1 + 32, POR, 600, 180)
spot(s3[0] + 22, ly1 + 32, ORD, 600, 180)
spot(s3[0] + 60, ly1 + 32, ORD, 600, 180, skill='hard')
wake(616, ly0, 616, ly1, 600)
m.label(lx0 + 16, ly1 - 24, 'G SOUS-STATION')

# --------------------------------------------------------------------------- autopilot route (dev)
route = [
    # (x, y, use, wait, weapon, angle): the normal path, ordinary commands; scenes used on the way
    (1856, 120, 0, 0, 1, 90),
    (1856, 380, 1, 60, 0, 90),               # the warm rail
    (1856, 700, 0, 0, 0, 0),
    (1856, 920, 0, 400, 0, 90),              # the hut: "Tu es en retard." ... "Si tu veux."
    (1800, HY0 + 36, 1, 420, 0, 180),        # the card at the clock: 06:06; "Celui ou ils entrent."
    (1800, 1180, 0, 0, 0, 0),
    (HX0 + 48, 1180, 1, 360, 0, 270),        # the key of the substation; the barrier lifts
    (1800, 1180, 0, 0, 0, 0),
    (1856, 1250, 0, 60, 0, 0),               # E1 behind him
    (1856, 1420, 1, 60, 0, 255),             # he turns round: the hut is empty, ERREUR Ø
    (1856, 1632, 0, 0, 0, 0),
    (1600, 1632, 0, 0, 0, 0),
    (1480, 1632, 0, 0, 0, 0),                # the first view of the park
    (1480, 1100, 0, 0, 0, 0),
    (1480, 704, 0, 0, 0, 0),                 # facing BROOKLYN BRIDGE
    (1568, 704, 0, 0, 0, 0),                 # in under the bridge
    (1648, 704, 0, 0, 0, 0),
    (1648, 630, 0, 60, 0, 0),                # E2
    (1648, 300, 0, 0, 0, 0),
    (1568, 288, 0, 0, 0, 0),
    (1480, 288, 0, 0, 0, 0),
    (960, 300, 0, 0, 0, 0),                  # the basin's south stair
    (960, 470, 0, 0, 0, 0),                  # down into the basin
    (960, 900, 0, 0, 0, 0),
    (960, 1210, 0, 0, 0, 0),
    (968, 1240, 0, 0, 0, 0),                 # E3 cued
    (976, 1250, 1, 330, 0, 90),              # the shoe in the puddle
    (960, 1250, 0, 200, 0, 0),               # E3 down the rocks
    (832, 1300, 0, 0, 0, 0),
    (832, 1430, 0, 0, 0, 0),                 # up the rocks of the cascade
    (832, 1520, 0, 60, 0, 0),                # E4
    (664, 1500, 0, 0, 0, 0),
    (650, 1376, 0, 0, 0, 0),
    (500, 1376, 0, 0, 0, 0),                 # up onto the loading platform
    (500, 1580, 0, 0, 0, 0),
    (496, 1680, 0, 0, 0, 0),                 # down its north steps
    (704, 1760, 0, 0, 0, 0),
    (648, 1850, 0, 0, 0, 0),
    (648, 1880, 1, 120, 0, 90),              # the turnstile: 618
    (648, 1990, 0, 0, 0, 0),
    (560, 2000, 0, 0, 0, 0),
    (560, 2064, 1, 360, 0, 180),             # the mirror of the badge: three panels, three outfits
    (560, 2090, 0, 0, 0, 0),
    (648, 2090, 0, 0, 0, 0),
    (648, 2150, 1, 60, 0, 90),               # the juke-box: the tarpaulin
    (648, 2150, 1, 240, 0, 90),              # the key: nothing; three knocks (E5)
    (720, 2000, 0, 200, 0, 0),
    (680, 2090, 0, 0, 0, 0),
    (560, 2090, 0, 0, 0, 0),
    (560, 2150, 0, 0, 0, 0),
    (560, 2184, 1, 60, 0, 90),               # the side door, from inside
    (560, 2290, 0, 0, 0, 0),
    (680, 2290, 0, 60, 0, 0),                # E6
    (1300, 2288, 0, 0, 0, 0),
    (1568, 2300, 0, 0, 0, 0),
    (1568, 2316, 1, 60, 0, 90),              # the door of the substation (the key)
    (1568, dy1 + 48, 0, 0, 0, 0),            # exit
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
