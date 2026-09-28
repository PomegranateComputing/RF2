#!/usr/bin/env python3
"""RF02 - Paris, 14 juin 1940, rue de service. Production map source (authored, not generated).

The walk of the novel (lines 87-457, docs/production/maps/RF02_FICHE.md), in its order, from the boulevard
Arago to the Porte Maillot, as seven spaces joined by streets:

  A  Boulevard Arago (start, east): the Sante wall and its closed gate, the forms burning in a bucket, the pram
     of registers, a side street.
  B  Carrefour du tramway / Denfert: the tram stopped with its doors open (suitcases on the benches, the fare
     collector's satchel: a punched ticket), shelter stencils, sandbags, mattresses, a tilted bus.
  C  Port-Royal / Cochin: the pharmacy shutter with ERREUR 0 fresh in black paint; in the side window, the
     reflection of the street where a mattress advances with nobody pulling it; the Cochin forecourt and its
     ambulances.
  D  Montparnasse / rue de Rennes: the closed station and its board of hours without departures, the TSF shop
     (the Amiga in the reflection of its window, the set with the blown fuse), the looted grocery (wine in the
     gutter), the bookshop barricade of books (the reader card: JERMA - ERREUR 0).
  E  The quay and the bridge: military papers, the engines from the north.
  F  The abandoned barrage near the Assemblee: the field telephone ("Ardent? Incident critique.").
  G  Back streets, the Champs-Elysees (the Morris column: Luna Park, then for a heartbeat JERMA PALACE), the
     avenue de la Grande-Armee (tyres, taxis), the Porte Maillot: LUNA PARK, the U hanging, FERMETURE
     DEFINITIVE crossed out, the gate padlocked, the service door ajar (exit).

Enemies continue the accepted RF01 adaptation: the staff of Sainte-Anne pursue Viktor out of the walls. No German
troops are fought (the text never does). The people of the text (the three women at the Sante, the old man on the
tram, the boy of the TSF shop, the woman of Cochin, the young woman with the suitcase of shoes...) are requested
from Astra; the map does not pretend they are there.

Units: 1 cell = 16. Streets: sky at 448 (facade textures are 448 high), pavements +8.
Usage: python scripts/mapkit/rf02.py   (writes src/maps/RF02.wad, build/RF02_plan.png, build/RF02_TEXTMAP.txt)
"""
import math
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- materials
SKY = 448
ENV_CITY, ENV_ROOM, ENV_SHOP, ENV_RIVER, ENV_ALLEY = (32, 0), (30, 8), (30, 3), (30, 1), (13, 0)


def street(light, ftex='RF2_ASPW', color=0xD8DAE0, wall='RF2_FAC1', env=ENV_CITY):
    return Cell(floor=0, ceil=SKY, ftex=ftex, ctex='F_SKY1', light=light, wall=wall, color=color, env=env,
                lower='RFS_BASE')


def pave(base, wall=None):
    return replace(base, floor=8, ftex='RFF_SLAB', wall=wall or base.wall, lower='RFS_BASE')


A_RD = street(172)
B_RD = street(176, 'RF2_SETT')
C_RD = street(168)
D_RD = street(164, 'RF2_ASPH')
E_RD = street(184, 'RF2_ASPH', 0xDCE0E6, env=ENV_RIVER)
F_RD = street(174, 'RF2_ASPH', 0xE0DCD4)
G_RD = street(162, 'RF2_ASPH', 0xE4DCCE)
M_RD = street(156, 'RF2_SETT', 0xE8DCC8)          # Porte Maillot: the light goes flat and yellow
SHOP = Cell(floor=8, ceil=144, ftex='RFF_WOOD', ctex='RFP_CEID', light=118, wall='RFW_PANL', color=0xFFE8D0, env=ENV_ROOM)
YARD = Cell(floor=8, ceil=SKY, ftex='RFF_GRAV', ctex='F_SKY1', light=170, wall='RFS_HOSP', color=0xDCE0E6, env=ENV_CITY)
WATER = Cell(floor=-192, ceil=SKY, ftex='RF2_EAU1', ctex='F_SKY1', light=176, wall='RF2_QUAI', color=0xD4DCE4, env=ENV_RIVER)

LAMP_GAIN = 0.55
DAY_GAIN = 0.45

# Thing types (MAPINFO DoomEdNums)
T_START, T_FAL, T_BROWNING, T_MAG, T_9MM, T_DRESS = 1, 30001, 30002, 30101, 30103, 30201
T_CHAIR, T_CABINET, T_TROLLEY, T_BENCH = 30302, 30303, 30305, 30306
T_ORDERLY, T_BRANC, T_PORTE, T_CORPSE, T_WAVE = 30401, 30402, 30403, 30410, 30405
ORD, BRA, POR = 1, 2, 3   # RFWaveSpot kinds
T_LAMP, T_FLICKER, T_AMB, T_NOTE, T_LITTER, T_SIGNAL, T_TOUR, T_WP = 30601, 30602, 30611, 30621, 30622, 30623, 30901, 30902
T_SACOCHE, T_BUCKET, T_PHONE, T_RADIO, T_ATLAS, T_FOUNTAIN, T_SPOT, T_MATTRESS, T_MORRIS = 30631, 30632, 30633, 30634, 30635, 30636, 30637, 30638, 30639
# the figures of Astra (RF2_MAP_02_REPRISE, 28/09), src/zscript/rf/figures.zs: visual only
T_FIG_FORMS, T_FIG_PRAM, T_FIG_SANTE_A, T_FIG_SANTE_B, T_FIG_SANTE_C, T_FIG_SANTE_D = 30641, 30642, 30643, 30644, 30645, 30646
T_FIG_TRAM, T_FIG_TSF, T_FIG_COCHIN, T_FIG_VALISE, T_VIKTOR_MIRROR = 30647, 30648, 30649, 30650, 30651
T_PRAM = 30652                  # Astra's pram model (RF02-B)
T_DECAL = 9200
DAMP, GRIME, STREAK, SCUFF = 11001, 11002, 11003, 11004

# Scenes (RFParis): line field user_scene / thing args[0]
S_MORRIS, S_SHUTTER, S_ENGINES, S_BELL, S_PHONE_RING, S_TSF_VOICES, S_TSF_WINDOW, S_MIRROR, S_MATTRESS = 1, 2, 3, 4, 5, 6, 7, 8, 9
S_TICKET, S_FORMS, S_PHONE, S_RADIO, S_ATLAS, S_FOUNTAIN = 10, 11, 12, 13, 14, 15
SIGNAL_TID = 999
PHONE_WAVE_TID = 600

m = MapBuilder('RF02')


# --------------------------------------------------------------------------- helpers
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
    """Solid street furniture or vehicle: floor raised over the surrounding cell."""
    m.raise_block(x0, y0, x1, y1, height, top, side, base)


def roofline(x0, y0, x1, y1, top, side, base):
    """A wall lower than the sky: a strip whose floor and ceiling are its top (the side texture is its riser)."""
    m.box(x0, y0, x1, y1, base, floor=top, ceil=top, ftex='RF2_ZINC', lower=side, wall=side)


def lamp(x, y, z, r=255, g=206, b=150, radius=200):
    m.thing(x, y, T_LAMP, args=(round(r * LAMP_GAIN), round(g * LAMP_GAIN), round(b * LAMP_GAIN), radius), z=z)


def daylight(x, y, z, radius=420):
    m.thing(x, y, T_LAMP, args=(round(200 * DAY_GAIN), round(208 * DAY_GAIN), round(222 * DAY_GAIN), radius), z=z)


def sign(x0, y0, x1, y1, tex, zbottom, off=1):
    """Masked sign on a decor line (plaque, fascia, poster, stencil): endpoints given on the face of the wall that
    holds it, the visible face toward the street (right of x0,y0 -> x1,y1). The line is drawn `off` units in front
    of that face (1: against it) and the whole texture is fitted between the endpoints, which span its width.
    RF02-A (28/09): the endpoints used to be given 4 units off the wall and the last 4 units of every texture were
    cut (decor lines are 2 units shorter at each end); scripts/production/sign_survey.py checks every sign."""
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = (y1 - y0) / L * off, -(x1 - x0) / L * off
    m.decor_line(x0 + nx, y0 + ny, x1 + nx, y1 + ny, tex, zbottom, yscale=4, texwidth=L)   # 4 pixels per unit


def across(x0, y0, x1, y1, special, args=(), objective=0, fields=None, repeat=False):
    """Walk-over trigger across several sectors (roadway, pavements, rails): one line per run of identical
    cells, all with the same special. The constant coordinate must be off the grid (n*16+8)."""
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


def use_decor(x0, y0, x1, y1, tex, zbottom, sc):
    """A masked decor line that can be used (the ERREUR 0 on the shutter); placed like sign()."""
    sign(x0, y0, x1, y1, tex, zbottom)
    m.decor[-1].update(special=130, args=[SIGNAL_TID, 0, 0, 0, 0], repeat=False,
                       fields={'user_scene': sc})
    m.decor[-1]['flags'] = dict(m.decor[-1]['flags'], playeruse=True, playeruseback=True)


def wear(x, y, wall, kind, z):
    m.thing(x, y, T_DECAL, angle={'N': 270, 'S': 90, 'E': 180, 'W': 0}[wall], args=(kind,), z=z)


def spot(x, y, kind, tid, angle, skill='all'):
    """Wave spot: the enemy is spawned out of sight when its line is crossed (no frozen figure in the street)."""
    m.thing(x, y, T_WAVE, angle=angle, tid=tid, args=(kind,), skill=skill)


def litter(points):
    for (x, y, a) in points:
        m.thing(x, y, T_LITTER, angle=a)


# ============================================================================ A. BOULEVARD ARAGO
m.box(2560, 64, 3840, 256, A_RD)
for (x0, x1, fac) in ((2560, 2816, 'RF2_FAC2'), (2816, 3072, 'RF2_FAC3'), (3072, 3264, 'RF2_FAC1'),
                      (3328, 3584, 'RF2_FAC2'), (3584, 3840, 'RF2_FAC3')):
    m.box(x0, 0, x1, 64, pave(A_RD, fac))
m.box(3264, 0, 3328, 64, pave(A_RD, 'RF2_FAC3'))                  # corner of the side street
for (x0, x1, fac) in ((2560, 2816, 'RF2_FAC1'), (2816, 3584, 'RF2_SANT'), (3584, 3840, 'RF2_FAC2')):
    m.box(x0, 256, x1, 320, pave(A_RD, fac))
# the Sante: enclosure wall lower than the sky, the great gate closed in a shallow recess
roofline(2816, 320, 3136, 336, 384, 'RF2_SANT', A_RD)
roofline(3264, 320, 3584, 336, 384, 'RF2_SANT', A_RD)
m.box(3136, 320, 3264, 336, pave(A_RD, 'RF2_SANT'), ceil=200, ctex='RFP_CEID', upper='RF2_SANT')
m.face(3136, 320, 3264, 336, 'N', texture='RF2_SGAT')
sign(3312, 320, 3360, 320, 'RF2_AFST', 60)                        # INTERDICTION DE STATIONNER, half torn
sign(2664, 0, 2600, 0, 'RF2_PL01', 120)                           # BOULEVARD ARAGO
# side street to the south (the staff come out of it)
m.box(3264, -320, 3328, 0, A_RD, wall='RF2_FAC3', ftex='RF2_SETT', light=150, env=ENV_ALLEY)
block(3264, -320, 3328, -272, 40, 'RFW_TOP', 'RFW_PANL', m.cells[(3264 // UNIT, -320 // UNIT)])   # handcart, crates
# east end: the way back toward Sainte-Anne is blocked by an abandoned bus
block(3696, 144, 3824, 192, 96, 'RF2_ZINC', 'RF2_BUSV', A_RD)
block(3776, 80, 3840, 128, 40, 'RFW_TOP', 'RFW_PANL', A_RD)
# the start: Viktor walks west
m.thing(3740, 232, T_START, angle=180)
m.thing(3700, 290, T_SIGNAL, tid=SIGNAL_TID)
# forms burning badly in a galvanised bucket; a uniform nobody fills (figure requested from Astra)
m.thing(3456, 36, T_BUCKET, args=(S_FORMS,))
m.thing(3456, 36, T_FLICKER, args=(255, 150, 80, 110, 80), z=28)
m.thing(3478, 30, T_FIG_FORMS, angle=180)                           # F02-01 feeds them to the fire, 20 u from the bucket
# the pram full of registers
m.thing(3016, 288, T_PRAM, angle=180)                               # pointing west, the handle toward the woman
m.thing(3006, 288, T_NOTE, angle=90, args=(20, 1, 3), z=35)        # the registers of the model, read with the use key
m.thing(3054, 288, T_FIG_PRAM, angle=180)                           # F02-02 her hands on the handle (still: no walk yet)
litter([(3620, 150, 20), (3500, 210, 130), (3300, 110, 250), (3150, 180, 75), (2950, 90, 300), (2700, 230, 190),
        (3420, 280, 40), (3200, 30, 160)])
m.thing(3200, 160, T_AMB, args=(4, 45))
m.thing(3296, -160, T_AMB, args=(1, 30))
for x in (2750, 3350):
    daylight(x, 160, 300)
m.thing(3600, 60, T_9MM)
m.thing(3620, 40, T_VIKTOR_MIRROR)                                  # F02-08: follows the player, seen only in mirrors
for (x, y, t, a) in ((3170, 298, T_FIG_SANTE_A, 270), (3200, 302, T_FIG_SANTE_B, 270), (3230, 298, T_FIG_SANTE_C, 270),
                     (3212, 282, T_FIG_SANTE_D, 300)):             # F02-03 the group at the Sante gate, the child in front
    m.thing(x, y, t, angle=a)
m.thing(2600, 290, T_DRESS)
# E1: two orderlies come out of the side street when Viktor passes it
spot(3296, -200, ORD, 101, 90)
spot(3296, -240, ORD, 101, 90)
spot(3296, -120, ORD, 101, 90, skill='hard')
wake(3176, 0, 3176, 320, 101, 1)
m.label(3000, 150, 'A BOULEVARD ARAGO')
m.label(3140, 360, 'SANTE (porte close)')

# ============================================================================ B. CARREFOUR DU TRAMWAY / DENFERT
m.box(1856, -128, 2496, 512, B_RD)
# rails across the square (and under the tram)
m.box(1856, 192, 2496, 272, B_RD, ftex='RF2_RAIL')
# pavement ring with openings east (Arago) and west (Port-Royal)
m.box(1792, -192, 2560, -128, pave(B_RD, 'RF2_FAC3'))
m.box(1792, 512, 2560, 576, pave(B_RD, 'RF2_FAC2'))
m.box(2496, -128, 2560, 0, pave(B_RD, 'RF2_FAC1'))
m.box(2496, 0, 2560, 64, pave(A_RD, 'RF2_FAC1'))
m.box(2496, 64, 2560, 256, B_RD)
m.box(2496, 256, 2560, 320, pave(A_RD, 'RF2_FAC1'))
m.box(2496, 320, 2560, 512, pave(B_RD, 'RF2_FAC1'))
m.box(1792, -128, 1856, 256, pave(B_RD, 'RF2_FAC2'))
m.box(1792, 256, 1856, 320, pave(C_RD, 'RF2_FAC2'))
m.box(1792, 320, 1856, 512, B_RD)
# north street (rue de la Sante / abris), a dead end behind sandbags and a tilted bus
m.box(2080, 576, 2208, 896, B_RD, ftex='RF2_ASPW', light=160)
m.box(2048, 576, 2080, 896, pave(B_RD, 'RF2_FAC1'), light=160)
m.box(2208, 576, 2240, 896, pave(B_RD, 'RF2_FAC3'), light=160)
block(2080, 848, 2208, 896, 48, 'RF2_SABT', 'RF2_SABL', m.cells[(2080 // UNIT, 848 // UNIT)])
block(2112, 624, 2208, 672, 104, 'RF2_ZINC', 'RF2_BUSV', m.cells[(2112 // UNIT, 624 // UNIT)])   # the tilted bus
sign(2048, 600, 2048, 664, 'RF2_PL02', 120)                       # RUE DE LA SANTE (west wall of the street)
# shelter stencils and sandbags (l. 129)
sign(2232, -192, 2168, -192, 'RF2_STCA', 56)
sign(1792, 40, 1792, 136, 'RF2_STPS', 56)
sign(2280, 576, 2344, 576, 'RF2_STEA', 56)
sign(2492, -192, 2444, -192, 'RF2_AFMO', 64)                      # mobilisation order
block(1904, -128, 2032, -112, 48, 'RF2_SABT', 'RF2_SABL', B_RD)
block(1888, -112, 1904, -64, 48, 'RF2_SABT', 'RF2_SABL', B_RD)
for (x, y, a) in ((2400, -80, 20), (2440, 460, 95), (1900, 460, 170), (2300, 420, 10)):
    m.thing(x, y, T_MATTRESS, angle=a)                              # the city carries its sleep away
block(2352, 400, 2448, 448, 36, 'RFW_TOP', 'RFW_PANL', B_RD)       # a handcart loaded with a mattress
m.thing(2400, 424, T_MATTRESS, angle=0, z=36)

# The tram: stopped in the middle of the crossing, doors open (l. 113). Floor 24, body of solid 3D floors:
# lower panel 24-72 and window band 120-152 along the sides (windows lowered), pillars full height, the roof
# 136-152 over the aisle. Two doors on the south side.
TX0, TX1, TY0, TY1 = 2016, 2368, 176, 288
TRAM = replace(B_RD, floor=24, ftex='RF2_TFLR', lower='RFP_DRK')
m.box(TX0, TY0, TX1, TY1, TRAM)
for x in range(TX0, TX1, 16):
    for (y0, y1) in ((TY0, TY0 + 16), (TY1 - 16, TY1)):
        door_cell = y0 == TY0 and (2080 <= x < 2128 or 2272 <= x < 2320)
        pillar = (x - TX0) % 64 == 0 or x == TX1 - 16
        if door_cell:
            m.slab(x, y0, x + 16, y1, 120, 152, 'RF2_TRMU')
        elif pillar:
            m.slab(x, y0, x + 16, y1, 24, 152, 'RF2_TRAM')
        else:
            m.slab(x, y0, x + 16, y1, 24, 72, 'RF2_TRML')
            m.slab(x, y0, x + 16, y1, 120, 152, 'RF2_TRMU')
for (x0, x1) in ((TX0, TX0 + 16), (TX1 - 16, TX1)):                 # ends: a window between two pillars
    for y in range(TY0 + 16, TY1 - 16, 16):
        if y in (TY0 + 16, TY1 - 32):
            m.slab(x0, y, x1, y + 16, 24, 152, 'RF2_TRAM')
        else:
            m.slab(x0, y, x1, y + 16, 24, 72, 'RF2_TRML')
            m.slab(x0, y, x1, y + 16, 120, 152, 'RF2_TRMU')
m.slab(TX0 + 16, TY0 + 16, TX1 - 16, TY1 - 16, 136, 152, 'RF2_TRMU', 'RF2_ZINC', 'RFP_CEID')
# benches along both sides, the dozen suitcases left on them, the satchel on its hook
DOORS = ((2080, 2128), (2272, 2320))
for (y0, y1) in ((TY0 + 16, TY0 + 32), (TY1 - 32, TY1 - 16)):
    for x in range(TX0 + 32, TX1 - 32, 64):
        if y0 == TY0 + 16 and any(x < b and x + 48 > a for (a, b) in DOORS):
            continue
        m.raise_block(x, y0, x + 48, y1, 16, 'RF2_TFLR', 'RF2_BNCH', m.cells[(x // UNIT, y0 // UNIT)])
for (x, y) in ((2112, 192), (2176, 192), (2304, 192), (2112, 256), (2176, 256), (2240, 256)):
    m.raise_block(x, y, x + 32, y + 16, 24, 'RFW_TOP', 'RF2_VALI', m.cells[(x // UNIT, y // UNIT)])
m.thing(2046, 264, T_SACOCHE, angle=270, args=(S_TICKET,), z=36)
m.thing(2072, 264, T_FIG_TRAM, angle=270)                           # F02-04 asleep on the bench of the rear platform
lamp(2192, 232, 110, 220, 214, 190, 140)
m.label(2040, 300, 'TRAMWAY')
m.thing(2176, 232, T_AMB, args=(3, 25))
m.thing(2176, 60, T_AMB, args=(4, 45))
litter([(1950, 30, 10), (2250, 90, 200), (2420, 330, 330), (2000, 420, 60), (1880, 380, 140), (2350, -40, 280)])
for (x, y) in ((1960, 100), (2380, 380)):
    daylight(x, y, 300)
m.thing(2440, -100, T_MAG)
m.thing(1900, -80, T_9MM)
m.thing(2140, 740, T_DRESS)
# E2: from the north street, a porte-registre with them; one more behind the sandbags (hard)
spot(2184, 720, ORD, 201, 270)
spot(2176, 800, ORD, 201, 270)
spot(2190, 760, POR, 201, 270)
spot(2168, 820, ORD, 201, 270, skill='hard')
wake(1976, -192, 1976, 576, 201, 2)
objective(2536, -192, 2536, 576, 1)
checkpoint(2520, -192, 2520, 576)
m.label(1900, -60, 'B CARREFOUR / DENFERT')

# ============================================================================ C. PORT-ROYAL / COCHIN
m.box(1024, 320, 1792, 512, C_RD)
m.box(1344, 512, 1792, 576, pave(C_RD, 'RF2_FAC3'))
m.box(1024, 512, 1344, 576, pave(C_RD, 'RF2_FAC2'))
for (x0, x1, fac) in ((1024, 1152, 'RF2_FAC1'), (1280, 1536, 'RF2_FAC2'), (1536, 1792, 'RF2_FAC1')):
    m.box(x0, 256, x1, 320, pave(C_RD, fac))
m.box(1152, 256, 1280, 320, pave(C_RD, 'RFS_HOSP'))
# the pharmacy: iron shutter in a shallow recess, ERREUR 0 fresh at shoulder height (l. 151), fascia over it
m.box(1408, 576, 1536, 592, pave(C_RD, 'RF2_SHOP'), ceil=136, ctex='RFP_CEID', upper='RF2_FACU')
m.face(1408, 576, 1536, 592, 'N', texture='RF2_RIDO')
sign(1408, 576, 1536, 576, 'RF2_FPHA', 140)
use_decor(1440, 592, 1504, 592, 'RF2_ERPH', 50, S_SHUTTER)
# the side window: a mirror behind the jars and the tonic card (l. 157)
m.box(1536, 576, 1600, 592, pave(C_RD, 'RF2_SHOP'), floor=32, ceil=112, ctex='RFP_CEID', upper='RF2_FACU', lower='RF2_SHOP')
m.face(1536, 576, 1600, 592, 'N', texture='RF2_SHOP', special=182)
sign(1536, 592, 1600, 592, 'RF2_PHVI', 40, off=6)   # the jars stand in front of the mirror
m.thing(1568, 548, T_SPOT, angle=90, args=(S_MIRROR,))
m.thing(1720, 400, T_SPOT, angle=180, args=(S_MATTRESS,))
sign(1344, 576, 1424, 576, 'RF2_PL03', 164)                        # BOULEVARD DE PORT-ROYAL: on the corner, as high as its neighbour
# Hopital Cochin: gateway, carved name, forecourt with the ambulances, engines off (l. 175)
m.box(1152, 240, 1280, 256, YARD, ceil=208, ctex='RFP_CEID', upper='RFS_HOSP')
sign(1280, 256, 1152, 256, 'RF2_COCP', 212)
m.thing(1216, 284, T_FIG_COCHIN, angle=90)                          # F02-06 in front of the gateway, the envelope held
m.box(1024, -32, 1408, 240, YARD)
block(1056, 64, 1184, 112, 96, 'RF2_ZINC', 'RF2_AMBU', YARD)
block(1232, 128, 1360, 176, 96, 'RF2_ZINC', 'RF2_AMBU', YARD)
m.thing(1300, 40, T_TROLLEY, angle=100)                            # a man on a stretcher (figure requested)
m.thing(1060, 200, T_BENCH, angle=0)
lamp(1216, 0, 140, 230, 226, 214, 220)
m.thing(1210, 110, T_AMB, args=(0, 30))
m.thing(1200, 20, T_MAG)
m.thing(1380, -10, T_DRESS)
litter([(1700, 450, 30), (1500, 360, 170), (1300, 480, 260), (1100, 400, 90), (1250, 220, 20)])
daylight(1400, 420, 300)
m.thing(1400, 420, T_AMB, args=(4, 40))
# E3: the brancardier charges out of the forecourt, orderlies behind it; a porte-registre at the corner
spot(1100, 20, BRA, 301, 45)
spot(1300, 90, ORD, 301, 135)
spot(1380, 60, ORD, 301, 135)
spot(1120, 30, POR, 302, 60)
spot(1330, -10, ORD, 301, 90, skill='hard')
wake(1352, 256, 1352, 576, 301, 2)
wake(1224, 256, 1224, 576, 302)
checkpoint(1768, 256, 1768, 576)
m.label(1100, 300, 'C PORT-ROYAL')
m.label(1060, 220, 'COCHIN')

# ============================================================================ D. MONTPARNASSE / RUE DE RENNES
m.box(1088, 576, 1280, 1792, D_RD)
m.box(1024, 576, 1088, 1792, pave(D_RD, 'RF2_FAC2'))
m.box(1280, 576, 1344, 1792, pave(D_RD, 'RF2_FAC1'))
for (y0, y1, fac) in ((576, 1024, 'RF2_FAC3'), (1216, 1472, 'RF2_FAC2'), (1600, 1792, 'RF2_FAC3')):
    m.modify(1280, y0, 1344, y1, wall=fac)
for (y0, y1, fac) in ((576, 656, 'RF2_FAC1'), (768, 1344, 'RF2_FAC3'), (1472, 1792, 'RF2_FAC1')):
    m.modify(1024, y0, 1088, y1, wall=fac)
sign(1344, 664, 1344, 584, 'RF2_PL07', 164)                        # BOULEVARD DU MONTPARNASSE
sign(1024, 580, 1024, 644, 'RF2_PL04', 124)                        # RUE DE RENNES
# the station, closed: a gate of bars, the board of hours without departures (l. 207)
m.box(1008, 656, 1024, 768, pave(D_RD, 'RFM_GRIL'), ceil=176, ctex='RFP_CEID', upper='RF2_FACU')
m.face(1008, 656, 1024, 768, 'W', texture='RFM_GRIL')
sign(1024, 784, 1024, 912, 'RF2_TABL', 72)
m.thing(1040, 840, T_NOTE, angle=0, args=(23,))
# the cafe: chairs stacked inside, pay sheets stuck to the pavement by the rain (l. 205)
sign(1344, 704, 1344, 640, 'RF2_FCAF', 124)
for (x, y, a) in ((1316, 660, 0), (1320, 690, 90), (1300, 720, 180), (1318, 750, 270)):
    m.thing(x, y, T_CHAIR, angle=a)
m.thing(1060, 980, T_NOTE, angle=30, args=(21,))
litter([(1150, 700, 10), (1200, 900, 200), (1100, 1200, 120), (1250, 1400, 320), (1180, 1650, 50)])
# the TSF shop (l. 211): window of wireless sets, rolling grille, counter, shelves of sets
m.box(1360, 1024, 1568, 1216, SHOP)
m.window(1344, 1040, 1360, 1168, SHOP, 56, 120, tex='RF2_TSFS', wall='RFW_PANL', lower='RF2_SHOP')
m.modify(1344, 1040, 1360, 1168, upper='RF2_FACU', env=ENV_CITY)
m.face(1328, 1040, 1344, 1168, 'E', fields={'user_scene': S_TSF_WINDOW})
door(1344, 1168, 1376, 1216, 60, 'RF2_RIDO', SHOP, 'W', lintel=104, track='RFW_PANL', speed=24)
m.carve(1360, 1152, 1376, 1168)
m.modify(1344, 1168, 1360, 1216, upper='RF2_FACU')
sign(1344, 1168, 1344, 1040, 'RF2_FTSF', 124)
m.raise_block(1536, 1024, 1568, 1216, 64, 'RFW_TOP', 'RF2_TSFS', SHOP)
m.raise_block(1376, 1024, 1536, 1040, 64, 'RFW_TOP', 'RF2_TSFS', SHOP)
m.raise_block(1424, 1072, 1520, 1104, 32, 'RFW_TOP', 'RFW_PANL', SHOP)          # counter
m.thing(1472, 1100, T_RADIO, angle=180, args=(S_RADIO,))   # at the edge of the counter: within reach of the use key
m.thing(1472, 1056, T_FIG_TSF, angle=90)                    # F02-05 crouched behind the counter
m.thing(1352, 1104, T_SPOT, angle=0, args=(S_TSF_WINDOW,))
m.thing(1470, 1150, T_AMB, args=(5, 60))
lamp(1470, 1130, 110, 255, 210, 150, 200)
m.thing(1520, 1180, T_9MM)
m.thing(1392, 1060, T_CABINET, angle=0)
scene(1088, 936, 1344, 936, S_TSF_VOICES)
# the grocery looted, wine in the gutter (l. 285-293)
GROC = replace(SHOP, ftex='RFF_CER', light=112)
m.box(880, 1360, 1008, 1472, GROC)
m.box(1008, 1376, 1024, 1456, GROC, ceil=112, upper='RF2_FACU')
sign(1024, 1360, 1024, 1472, 'RF2_FEPI', 116)
m.box(1088, 1360, 1104, 1600, D_RD, ftex='RF2_VIN1')
block(1040, 1392, 1072, 1424, 28, 'RFW_TOP', 'RFW_PANL', m.cells[(1040 // UNIT, 1392 // UNIT)])  # a broken crate
for (x, y) in ((912, 1376), (960, 1440)):
    block(x, y, x + 32, y + 16, 32, 'RFW_TOP', 'RFW_PANL', m.cells[(x // UNIT, y // UNIT)])
lamp(950, 1416, 100, 220, 200, 170, 150)
# the bookshop: books piled in front of its door (l. 305), the atlas on top (l. 311)
m.box(1344, 1520, 1360, 1568, pave(D_RD, 'RFW_PANL'), ceil=112, ctex='RFP_CEID', upper='RF2_FACU')
m.face(1344, 1520, 1360, 1568, 'E', texture='RFD_SGL')
sign(1344, 1600, 1344, 1488, 'RF2_FLIB', 120)
block(1296, 1504, 1328, 1584, 44, 'RFW_TOP', 'RF2_LIVR', m.cells[(1296 // UNIT, 1504 // UNIT)])
m.thing(1300, 1544, T_ATLAS, angle=180, args=(S_ATLAS,))
m.thing(1300, 1620, T_MAG)
# E4: orderlies down the street from the river, out of the grocery; the brancardier last (hard)
spot(900, 1864, ORD, 401, 0)
spot(1480, 1864, ORD, 401, 180)
spot(980, 1380, ORD, 401, 0)
spot(840, 1856, POR, 401, 0)
spot(1520, 1856, BRA, 401, 180, skill='hard')
wake(1024, 1256, 1344, 1256, 401, 4)
objective(1024, 600, 1344, 600, 3)
checkpoint(1024, 1000, 1344, 1000)
for (y) in (800, 1300, 1650):
    daylight(1184, y, 300)
m.thing(1184, 800, T_AMB, args=(4, 40))
m.thing(1184, 1500, T_AMB, args=(4, 40))
m.label(1100, 1000, 'D RUE DE RENNES')
m.label(1380, 1060, 'TSF')

# ============================================================================ E. QUAI AND BRIDGE
m.box(768, 1792, 1600, 1824, pave(E_RD, 'RF2_FAC2'))
m.box(768, 1824, 1600, 1904, E_RD)
for (x0, x1) in ((768, 1088), (1280, 1600)):
    m.box(x0, 1904, x1, 1920, E_RD, floor=32, ftex='RFF_SLAB', lower='RF2_QUAI', wall='RF2_QUAI')
m.box(1088, 1904, 1104, 1920, E_RD, floor=32, ftex='RFF_SLAB', lower='RF2_QUAI', wall='RF2_QUAI')
m.box(1264, 1904, 1280, 1920, E_RD, floor=32, ftex='RFF_SLAB', lower='RF2_QUAI', wall='RF2_QUAI')
m.box(1104, 1904, 1264, 1920, E_RD)
sign(1500, 1792, 1436, 1792, 'RF2_PL05', 110)                       # QUAI D'ORSAY
# the Seine: water well below, walls of the quays, the bridge deck with its parapets
m.box(256, 1920, 1104, 2432, WATER)
m.box(1264, 1920, 2112, 2432, WATER)
m.box(1104, 1920, 1264, 2432, E_RD)
for x in (1108, 1260):                                   # cast-iron railings: the river seen through them
    m.decor_line(x, 1920, x, 2432, 'RF2_RAMB', 0, blocking=True, yscale=4)
m.thing(1184, 2100, T_NOTE, angle=80, args=(22,))
litter([(1130, 1960, 40), (1230, 2030, 170), (1150, 2250, 260), (1210, 2330, 10), (1120, 2400, 130),
        (1180, 2180, 300)])
m.thing(1184, 2176, T_AMB, args=(1, 45))
m.thing(700, 2176, T_AMB, args=(2, 25))
daylight(1184, 2176, 320, 600)
scene(1104, 2168, 1264, 2168, S_ENGINES)
objective(768, 1848, 1600, 1848, 4)
objective(1104, 1960, 1264, 1960, 5)
checkpoint(768, 1864, 1600, 1864)
m.label(800, 1860, 'E QUAI')
m.label(1120, 2200, 'PONT')

# ============================================================================ F. THE BARRAGE NEAR THE ASSEMBLEE
for (x0, x1) in ((640, 1088), (1280, 1600)):
    m.box(x0, 2432, x1, 2448, F_RD, floor=32, ftex='RFF_SLAB', lower='RF2_QUAI', wall='RF2_QUAI')
m.box(1088, 2432, 1104, 2448, F_RD, floor=32, ftex='RFF_SLAB', lower='RF2_QUAI', wall='RF2_QUAI')
m.box(1264, 2432, 1280, 2448, F_RD, floor=32, ftex='RFF_SLAB', lower='RF2_QUAI', wall='RF2_QUAI')
m.box(1104, 2432, 1264, 2448, F_RD)
m.box(640, 2448, 1600, 2816, F_RD, wall='RF2_FAC1')
m.box(640, 2816, 1600, 2880, pave(F_RD, 'RF2_FAC1'))
m.modify(1344, 2448, 1600, 2816, wall='RF2_FAC2')
for (x0, x1) in ((784, 880), (1424, 1520)):
    m.box(x0, 2880, x1, 3072, F_RD, wall='RF2_FAC3', light=150, env=ENV_ALLEY)
    m.box(x0, 2816, x1, 2880, pave(F_RD, 'RF2_FAC3'))
# the barrage: sandbags in a chicane, the machine gun under its tarpaulin, the folding table and the telephone
for (x0, y0, x1, y1) in ((1040, 2624, 1168, 2640), (1232, 2624, 1360, 2640), (1040, 2640, 1056, 2704),
                         (1344, 2640, 1360, 2704)):
    block(x0, y0, x1, y1, 48, 'RF2_SABT', 'RF2_SABL', F_RD)
block(1200, 2720, 1264, 2752, 28, 'RF2_BACH', 'RF2_BACS', F_RD)
block(1104, 2688, 1152, 2720, 30, 'RFW_TOP', 'RFW_TBLS', F_RD)
m.thing(1128, 2692, T_PHONE, angle=270, args=(S_PHONE,))
m.thing(1296, 2680, T_FIG_VALISE, angle=225)                        # F02-07 inside the chicane, turned to the way in
scene(640, 2472, 1600, 2472, S_PHONE_RING)
objective(640, 2600, 1600, 2600, 6)
m.thing(1300, 2780, T_MAG)
m.thing(1080, 2770, T_MAG)
m.thing(1450, 2600, T_DRESS)
m.thing(1180, 2560, T_AMB, args=(4, 40))
daylight(1180, 2700, 300)
litter([(1000, 2700, 50), (1400, 2750, 200), (800, 2600, 300), (1500, 2500, 20)])
# E6: after the call, the staff close in from both ends of the boulevard (PHONE_WAVE_TID, RFParis)
spot(832, 3040, ORD, PHONE_WAVE_TID, 270)
spot(832, 2980, ORD, PHONE_WAVE_TID, 270)
spot(1472, 3010, BRA, PHONE_WAVE_TID, 270)
spot(1472, 2930, POR, PHONE_WAVE_TID, 270)
spot(816, 2930, ORD, PHONE_WAVE_TID, 270, skill='hard')
checkpoint(1104, 2456, 1264, 2456)
m.label(700, 2500, "F BARRAGE (ASSEMBLEE)")

# ============================================================================ G. BACK STREETS TO THE PORTE MAILLOT
# G1 rue de l'Universite: narrow, concierges' brooms, a fountain (l. 419-425)
m.box(0, 2688, 640, 2784, F_RD, wall='RF2_FAC3', light=150, env=ENV_ALLEY)
m.modify(0, 2688, 320, 2784, wall='RF2_FAC2')
block(320, 2768, 336, 2784, 40, 'RFM_TOP', 'RFM_PANL', m.cells[(320 // UNIT, 2768 // UNIT)])
m.thing(328, 2760, T_FOUNTAIN, angle=90, args=(S_FOUNTAIN,))
m.thing(320, 2736, T_AMB, args=(2, 30))
objective(600, 2688, 600, 2784, 7)
checkpoint(568, 2688, 568, 2784)
m.label(40, 2740, 'G1 RUE DE L UNIVERSITE')
# G2 Champs-Elysees: empty, vehicles abandoned across the lanes, the Morris column (l. 427-443)
m.box(-768, 2624, 0, 2848, G_RD)
m.box(-768, 2560, 0, 2624, pave(G_RD, 'RF2_FAC1'))
m.box(-768, 2848, 0, 2944, pave(G_RD, 'RF2_FAC2'))
block(-560, 2656, -432, 2704, 96, 'RF2_ZINC', 'RF2_BUSV', G_RD)
block(-240, 2752, -144, 2800, 64, 'RF2_ZINC', 'RF2_TAXI', G_RD)
m.thing(-352, 2896, T_MORRIS, angle=270, args=(S_MORRIS,))
litter([(-100, 2700, 30), (-300, 2650, 120), (-600, 2800, 250), (-700, 2600, 80)])
m.thing(-384, 2736, T_AMB, args=(4, 40))
daylight(-384, 2736, 300, 500)
m.thing(-640, 2900, T_9MM)
m.label(-760, 2580, 'G2 CHAMPS-ELYSEES')
# G3 avenue de la Grande-Armee: garages shut, tyres stacked like funeral rings (l. 447)
m.box(-1664, 2656, -768, 2848, G_RD)
m.box(-1664, 2624, -768, 2656, pave(G_RD, 'RF2_FAC1'))
m.box(-1664, 2848, -768, 2880, pave(G_RD, 'RF2_FAC3'))
for x in (-1408, -1296, -1008):
    block(x, 2848, x + 64, 2880, 32, 'RFM_TOP', 'RF2_TYRE', m.cells[(x // UNIT, 2848 // UNIT)])
sign(-800, 2624, -880, 2624, 'RF2_PL06', 110)
scene(-792, 2624, -792, 2880, S_BELL)
m.thing(-1200, 2750, T_AMB, args=(4, 40))
m.thing(-1500, 2700, T_DRESS)
m.thing(-1100, 2860, T_MAG)
m.label(-1650, 2680, 'G3 GRANDE-ARMEE')
# G4 Porte Maillot: taxis in a row before a station without passengers; the Luna Park behind its hoarding
m.box(-2432, 2432, -1664, 3200, M_RD)
m.box(-2176, 2112, -2048, 2432, M_RD, wall='RF2_FAC3', light=148, env=ENV_ALLEY)     # a street to the south
m.box(-2432, 3136, -1664, 3200, pave(M_RD, 'RF2_FAC2'))
for (x0, y0) in ((-2300, 2560), (-2176, 2560), (-2052, 2560), (-1928, 2560)):
    block(x0 // 16 * 16, y0, x0 // 16 * 16 + 96, y0 + 48, 64, 'RF2_ZINC', 'RF2_TAXI', M_RD)
block(-2400, 2880, -2336, 2944, 36, 'RFW_TOP', 'RFW_PANL', M_RD)
# the hoarding and the monumental entrance: LUNA PARK, the U hanging; FERMETURE DEFINITIVE; the padlocked gate
roofline(-2432, 3200, -2144, 3216, 256, 'RF2_PALI', M_RD)
roofline(-1984, 3200, -1776, 3216, 256, 'RF2_PALI', M_RD)
roofline(-1728, 3200, -1664, 3216, 256, 'RF2_PALI', M_RD)
m.box(-2144, 3200, -1984, 3216, pave(M_RD, 'RFM_GRIL'), ceil=176, ctex='RFP_CEID', upper='RF2_PALI')
m.door(-2144, 3216, -1984, 3232, 70, 'RFM_GRIL', 'RF2_PALI', replace(pave(M_RD), ctex='RFP_CEID'), kind='open', lock=5, lockside='')
sign(-2192, 3200, -1936, 3200, 'RF2_LUNA', 240)
sign(-2112, 3200, -2016, 3200, 'RF2_LUNF', 188)
# the service door ajar behind a heap of planks (l. 457): the way in
m.box(-1776, 3200, -1728, 3216, pave(M_RD, 'RFW_PANL'), ceil=120, ctex='RFP_CEID', upper='RF2_PALI', light=120)
m.box(-1792, 3216, -1712, 3328, Cell(floor=8, ceil=120, ftex='RFF_WOOD', ctex='RFP_CEID', light=96, wall='RFW_PANL',
                                    color=0xE8DCC8, env=ENV_ALLEY))
block(-1840, 3152, -1792, 3184, 40, 'RFW_TOP', 'RFW_PANL', M_RD)
block(-1712, 3152, -1680, 3184, 28, 'RFW_TOP', 'RFW_PANL', M_RD)
m.thing(-1760, 3300, T_AMB, args=(0, 30))
m.trigger(-1790, 3288, -1714, 3288, 130, (SIGNAL_TID,), fields={'user_outro': 1})
objective(-1688, 2624, -1688, 2880, 8)
checkpoint(-1672, 2624, -1672, 2880)
m.thing(-2100, 2700, T_AMB, args=(4, 45))
m.thing(-2000, 3100, T_AMB, args=(1, 30))
daylight(-2048, 2800, 300, 600)
litter([(-2200, 2700, 30), (-1900, 2900, 150), (-2300, 3050, 250), (-1800, 2500, 60), (-2050, 3120, 0)])
m.thing(-1760, 3000, T_MAG)
m.thing(-2350, 2500, T_DRESS)
# E7: the procedure catches up with him at the gate
spot(-2144, 2300, ORD, 701, 90)
spot(-2080, 2260, POR, 701, 90)
spot(-2144, 2200, ORD, 701, 90)
spot(-2096, 2160, BRA, 701, 90)
spot(-2080, 2340, ORD, 701, 90)
spot(-2144, 2140, POR, 701, 90, skill='hard')
wake(-1752, 2432, -1752, 3200, 701)
m.label(-2420, 2460, 'G4 PORTE MAILLOT')
m.label(-2140, 3260, 'LUNA PARK')
m.exit_cells = {(x // UNIT, 3312 // UNIT) for x in range(-1792, -1712, 16)}

# ============================================================================ joins between the spaces
# D <-> E: the rue de Rennes reaches the quay; F <-> G1: the back street leaves the boulevard westward;
# G1 <-> G2 and G2 <-> G3 and G3 <-> G4 share their edges (boxes above are contiguous).

# --------------------------------------------------------------------------- tour points (dev screenshots)
tour = [
    (3740, 232, 180, 2), (3456, 110, 250, 12), (3200, 230, 90, 0), (2600, 160, 180, 2), (2440, 230, 180, 4),
    (2080, 230, 0, 4), (2150, 120, 90, 3), (1900, 420, 330, 2), (1568, 540, 90, 2), (1472, 520, 90, 4),
    (1216, 380, 270, 2), (1184, 700, 90, 2), (1250, 1104, 0, 2), (1450, 1120, 0, 6), (1184, 1400, 90, 2),
    (1260, 1544, 0, 14), (1184, 1860, 90, 0), (1184, 2176, 90, -2), (1184, 2560, 90, 4), (1128, 2660, 90, 18),
    (320, 2736, 180, 0), (-300, 2800, 90, 2), (-352, 2840, 90, 6), (-1200, 2750, 180, 0), (-1900, 2900, 90, 2),
    (-2064, 3100, 90, -8), (-1760, 3150, 90, 2),
]
for i, (x, y, ang, pitch) in enumerate(tour):
    m.thing(x, y, T_TOUR, angle=ang, args=(i + 1, pitch))

# --------------------------------------------------------------------------- autopilot route (dev)
route = [
    # (x, y, use, wait, weapon, angle): the normal path, ordinary commands; the scenes are used on the way
    (3700, 200, 0, 0, 1, 180),
    (3480, 110, 0, 0, 0, 0),
    (3470, 70, 1, 60, 0, 270),             # the forms in the bucket
    (3300, 120, 0, 0, 0, 0),
    (3180, 150, 0, 60, 0, 0),              # E1 (side street)
    (2900, 160, 0, 0, 0, 0),
    (2560, 160, 0, 0, 0, 0),
    (2400, 120, 0, 0, 0, 0),
    (2104, 140, 0, 0, 0, 0),
    (2104, 216, 0, 0, 0, 0),               # through the south door of the tram
    (2064, 232, 0, 0, 0, 0),
    (2056, 244, 1, 120, 0, 90),            # the satchel: a punched ticket
    (2104, 216, 0, 0, 0, 0),
    (2104, 140, 0, 0, 0, 0),
    (1960, 140, 0, 0, 0, 0),               # E2
    (1900, 420, 0, 0, 0, 0),
    (1700, 440, 0, 0, 0, 0),
    (1568, 540, 0, 90, 0, 90),             # the pharmacy side window (the reflection)
    (1472, 552, 1, 140, 0, 90),            # ERREUR 0 on the shutter
    (1400, 420, 0, 0, 0, 0),               # E3 (Cochin)
    (1216, 420, 0, 0, 0, 0),
    (1184, 600, 0, 0, 0, 0),
    (1184, 900, 0, 0, 0, 0),               # TSF voices
    (1300, 1104, 0, 0, 0, 0),
    (1310, 1192, 1, 40, 0, 0),             # the grille of the shop
    (1440, 1192, 0, 0, 0, 0),
    (1472, 1120, 1, 480, 0, 270),          # the set with the blown fuse
    (1440, 1192, 0, 0, 0, 0),
    (1300, 1192, 0, 0, 0, 0),
    (1184, 1300, 0, 60, 0, 0),             # E4
    (1184, 1540, 0, 0, 0, 0),
    (1270, 1544, 1, 120, 0, 0),            # the atlas on the barricade: the reader card
    (1184, 1700, 0, 0, 0, 0),
    (1184, 1860, 0, 0, 0, 0),
    (1184, 2176, 0, 0, 0, 0),              # the engines
    (1184, 2470, 0, 0, 0, 0),              # the telephone rings
    (1200, 2600, 0, 0, 0, 0),
    (1200, 2664, 0, 0, 0, 0),
    (1128, 2664, 1, 820, 0, 90),           # the call; E6 after it
    (1200, 2664, 0, 0, 0, 0),
    (1200, 2590, 0, 60, 0, 0),
    (1000, 2560, 0, 0, 0, 0),
    (700, 2736, 0, 0, 0, 0),
    (328, 2736, 1, 30, 0, 90),             # the fountain
    (40, 2736, 0, 0, 0, 0),
    (-352, 2790, 0, 0, 0, 0),
    (-352, 2852, 1, 60, 0, 90),            # the Morris column
    (-700, 2750, 0, 0, 0, 0),
    (-1200, 2750, 0, 0, 0, 0),
    (-1700, 2750, 0, 0, 0, 0),
    (-1800, 2900, 0, 60, 0, 0),            # E7
    (-1760, 3140, 0, 0, 0, 0),
    (-1760, 3208, 0, 0, 0, 0),
    (-1760, 3310, 0, 0, 0, 0),             # the service door: exit
]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


# --------------------------------------------------------------------------- build
def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF02.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF02_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF02_plan.png', scale=0.25)
    report = m.check({}, m.exit_cells, decor_types=(T_MATTRESS,))
    print('RF02 built:', m.stats)
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
