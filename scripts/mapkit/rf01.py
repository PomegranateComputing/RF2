#!/usr/bin/env python3
"""RF01 - Sainte-Anne, 14 juin 1940. Production map source (authored, not generated).

Flow: Chambre -> couloir du pavillon ouest (E1, cle de la grille) -> Admissions (FAL, E2)
-> Cour des hommes (E3, perron nord) -> Pavillon est (E4) -> Lingerie en sous-sol (E5, passe)
-> escalier -> Galerie nord (vues sur la cour, grille a sens unique) -> Registres (revelation)
-> couloir ouest -> Chapelle (respiration, secret) -> Consultations (E6) -> Admissions
-> Loge du portier (passe, treuil) -> Admissions transformees (E7) -> Porche -> rue (sortie).

Units: 1 cell = 16. Doors are 32-deep strips: [frame cell][door cell].
Usage: python scripts/mapkit/rf01.py   (writes src/maps/RF01.wad, build/RF01_plan.png)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from udmf import MapBuilder, Cell, UNIT

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- materials
ADM = Cell(floor=0, ceil=256, ftex='RFF_CER', ctex='RFP_CEIL', light=150, wall='RFP_DADB', color=0xFFF4E4)
VEST = Cell(floor=0, ceil=160, ftex='RFF_CER', ctex='RFP_CEIL', light=135, wall='RFP_DADB', color=0xFFF4E4)
COR = Cell(floor=0, ceil=160, ftex='RFF_CER', ctex='RFP_CEIL', light=138, wall='RFP_DADB')
ROOM = Cell(floor=0, ceil=144, ftex='RFF_WOOD', ctex='RFP_CEIL', light=128, wall='RFP_DADG')
POSTE = Cell(floor=0, ceil=144, ftex='RFF_WOOD', ctex='RFP_CEIL', light=140, wall='RFP_DADR', color=0xFFF0DC)
WC = Cell(floor=0, ceil=144, ftex='RFF_CHK', ctex='RFP_CEIL', light=120, wall='RFP_TILE', color=0xE6F0F4)
YARD = Cell(floor=-32, ceil=384, ftex='RFF_GRAV', ctex='F_SKY1', light=212, wall='RFS_REND', color=0xE6ECF4)
ARC = Cell(floor=-32, ceil=112, ftex='RFF_SLAB', ctex='RFP_CEID', light=172, wall='RFS_REND')
WARD = Cell(floor=16, ceil=208, ftex='RFF_LINO', ctex='RFP_CEIL', light=152, wall='RFP_DADG', color=0xF4F6F0)
OFFICE = Cell(floor=16, ceil=144, ftex='RFF_WOOD', ctex='RFP_CEIL', light=128, wall='RFP_DADG')
SERV = Cell(floor=0, ceil=144, ftex='RFF_CONC', ctex='RFP_CEID', light=108, wall='RFP_DRK', color=0xE8ECF0)
LGR = Cell(floor=-96, ceil=32, ftex='RFF_CHK', ctex='RFP_CEID', light=104, wall='RFP_TILE', color=0xD8E6F0)
GAL = Cell(floor=32, ceil=224, ftex='RFF_WOOD', ctex='RFP_CEIL', light=166, wall='RFP_DADB', color=0xF6F4EC)
REG = Cell(floor=32, ceil=192, ftex='RFF_WOOD', ctex='RFP_CEID', light=118, wall='RFP_DADR', color=0xFFEEDA)
CH = Cell(floor=0, ceil=320, ftex='RFF_SLAB', ctex='RFP_CEID', light=142, wall='RFS_LIME', color=0xFFF0DA)
CHA = Cell(floor=0, ceil=192, ftex='RFF_SLAB', ctex='RFP_CEID', light=118, wall='RFS_LIME', color=0xFFF0DA)
CONS = Cell(floor=0, ceil=144, ftex='RFF_CHK', ctex='RFP_CEIL', light=134, wall='RFP_TILE')
C2C = Cell(floor=0, ceil=144, ftex='RFF_CHK', ctex='RFP_CEIL', light=126, wall='RFP_TILE')
LOGE = Cell(floor=0, ceil=144, ftex='RFF_WOOD', ctex='RFP_CEID', light=112, wall='RFP_DADR', color=0xFFEEDA)
PORCH = Cell(floor=0, ceil=176, ftex='RFF_SLAB', ctex='RFP_CEID', light=182, wall='RFS_LIME')
STREET = Cell(floor=-48, ceil=384, ftex='RFF_CONC', ctex='F_SKY1', light=216, wall='RFS_REND', color=0xE6ECF4)
EXT = Cell(floor=-32, ceil=384, ftex='RFF_GRAV', ctex='F_SKY1', light=205, wall='RFS_REND', color=0xE6ECF4)

# Thing types (MAPINFO DoomEdNums)
T_START, T_FAL, T_BROWNING, T_MAG, T_9MM, T_DRESS, T_KGRILLE, T_KPASSE = 1, 30001, 30002, 30101, 30103, 30201, 30211, 30212
T_DESK, T_CHAIR, T_CABINET, T_RADIATOR, T_TROLLEY, T_BENCH, T_LAMPMODEL = 30301, 30302, 30303, 30304, 30305, 30306, 30315
T_ORDERLY, T_BRANC, T_PORTE, T_CORPSE = 30401, 30402, 30403, 30410
T_LAMP, T_FLICKER, T_AMB, T_NOTE, T_TOUR, T_WP = 30601, 30602, 30611, 30621, 30901, 30902

m = MapBuilder('RF01')


# --------------------------------------------------------------------------- helpers
def door(x0, y0, x1, y1, tag, tex, base, frame_side, lintel=112, track='RFP_PLN', **kw):
    """32-deep door strip. frame_side: which edge of the box holds the lintel/frame cell."""
    if frame_side in ('N', 'S'):
        assert y1 - y0 == 32
        if frame_side == 'N':
            fy0, fy1, dy0, dy1 = y1 - 16, y1, y0, y1 - 16
        else:
            fy0, fy1, dy0, dy1 = y0, y0 + 16, y0 + 16, y1
        m.box(x0, fy0, x1, fy1, base, ceil=base.floor + lintel, wall=track, upper='', mid='', lower='')
        m.door(x0, dy0, x1, dy1, tag, tex, track, base, **kw)
    else:
        assert x1 - x0 == 32
        if frame_side == 'E':
            fx0, fx1, dx0, dx1 = x1 - 16, x1, x0, x1 - 16
        else:
            fx0, fx1, dx0, dx1 = x0, x0 + 16, x0 + 16, x1
        m.box(fx0, y0, fx1, y1, base, ceil=base.floor + lintel, wall=track, upper='', mid='', lower='')
        m.door(dx0, y0, dx1, y1, tag, tex, track, base, **kw)


def steps(x0, y0, x1, y1, axis, floors, base, depth=16, ceil_over=144, lower='RFS_BASE'):
    """Successive strips along axis ('x' increasing / 'y' increasing) with the given floor heights."""
    for i, z in enumerate(floors):
        if axis == 'x':
            m.box(x0 + i * depth, y0, x0 + (i + 1) * depth, y1, base, floor=z, ceil=z + ceil_over, lower=lower)
        elif axis == '-x':
            m.box(x1 - (i + 1) * depth, y0, x1 - i * depth, y1, base, floor=z, ceil=z + ceil_over, lower=lower)
        elif axis == 'y':
            m.box(x0, y0 + i * depth, x1, y0 + (i + 1) * depth, base, floor=z, ceil=z + ceil_over, lower=lower)
        else:
            m.box(x0, y1 - (i + 1) * depth, x1, y1 - i * depth, base, floor=z, ceil=z + ceil_over, lower=lower)


def bed(x, y, base, along='y'):
    """Hospital bed 48x80 (impassable block with mattress top)."""
    if along == 'y':
        m.raise_block(x, y, x + 48, y + 80, 28, 'RFT_BED', 'RFT_MAT', base)
        m.raise_block(x, y + 64, x + 48, y + 80, 44, 'RFT_MAT', 'RFT_MAT', base)  # headboard/pillow end
    else:
        m.raise_block(x, y, x + 80, y + 48, 28, 'RFT_BED', 'RFT_MAT', base)
        m.raise_block(x, y, x + 16, y + 48, 44, 'RFT_MAT', 'RFT_MAT', base)


def table(x0, y0, x1, y1, base, height=32):
    m.raise_block(x0, y0, x1, y1, height, 'RFW_TOP', 'RFW_PANL', base)


def shelf(x0, y0, x1, y1, base):
    m.raise_block(x0, y0, x1, y1, 60, 'RFW_TOP', 'RFW_PANL', base)


def pillar(x, y, size=32):
    m.carve(x, y, x + size, y + size)


def sign(x, y, side, name, zbottom=92):
    """Enamel plaque: 64-long decor line 4 units off a wall. side = wall the sign hangs on."""
    if side == 'W':
        m.decor_line(x + 4, y, x + 4, y + 64, name, zbottom)
    elif side == 'E':
        m.decor_line(x - 4, y + 64, x - 4, y, name, zbottom)
    elif side == 'S':
        m.decor_line(x + 64, y + 4, x, y + 4, name, zbottom)
    else:
        m.decor_line(x, y - 4, x + 64, y - 4, name, zbottom)


def lamp(x, y, z, r=255, g=214, b=160, radius=200):
    m.thing(x, y, T_LAMP, args=(r, g, b, radius), z=z)


def daylight(x, y, z, radius=260):
    m.thing(x, y, T_LAMP, args=(214, 226, 244, radius), z=z)


def wake_line(x0, y0, x1, y1, tid, code=0):
    m.trigger(x0, y0, x1, y1, 130, (tid, code))


# --------------------------------------------------------------------------- ADMISSIONS
m.box(128, -448, 640, -64, ADM)
for y in (-400, -304, -208, -112):                      # pilasters on the long walls
    m.carve(128, y, 144, y + 16)
    m.carve(624, y, 640, y + 16)
for x in (304, 432):                                     # two free columns
    pillar(x, -256)
# reception counter (L shape) and waiting benches
table(224, -336, 448, -304, ADM, 40)
table(224, -304, 256, -208, ADM, 40)
table(496, -272, 592, -240, ADM, 28)
table(496, -192, 592, -160, ADM, 28)
m.label(300, -420, 'ADMISSIONS')
# vestibule (south) with framed opening, porch grille, porch, street
m.box(320, -592, 448, -448, VEST)
m.box(336, -464, 432, -448, VEST, ceil=128)
m.carve(320, -464, 336, -448)
m.carve(432, -464, 448, -448)
m.carve(320, -608, 336, -592)
m.carve(432, -608, 448, -592)
m.door(336, -608, 432, -592, 50, 'RFM_GRIL', 'RFS_LIME', PORCH, kind='open', speed=8, lock=3, lockside='')
m.box(288, -800, 480, -608, PORCH)
for x in (288, 368, 448):
    m.carve(x, -800, x + 16, -784)
m.box(288, -816, 480, -800, STREET, floor=-16, lower='RFS_BASE')
m.box(288, -832, 480, -816, STREET, floor=-32, lower='RFS_BASE')
m.box(96, -1024, 672, -832, STREET)
m.trigger(96, -1008, 672, -1008, 243, (0,))
m.label(330, -700, 'PORCHE')
m.label(330, -930, 'RUE / SORTIE')
# hall <-> courtyard passage (north)
door(336, -80, 432, -48, 10, 'RFD_DBL', ADM, 'S', lintel=128)
m.box(336, -48, 432, -16, ADM, ceil=128, light=160)
m.box(336, -16, 432, 0, ADM, floor=-16, ceil=128, light=160, lower='RFS_BASE')
# loge du portier (east of the vestibule)
m.box(464, -592, 608, -464, LOGE)
door(512, -464, 576, -432, 36, 'RFD_SGL', ADM, 'N', lock=1, lockside='N')
m.window(448, -560, 464, -496, LOGE, 40, 104, lower='')
table(544, -560, 608, -528, LOGE, 32)
m.decor_line(592, -588, 528, -588, 'RFM_SW0', 44, blocking=False)
m.faces  # (winch is the decor switch line below)
m.decor[-1].update(special=11, args=[50, 8, 0, 0, 0], repeat=False)
m.decor[-1]['flags'] = dict(playeruse=True, playeruseback=True)
m.thing(576, -544, T_NOTE, args=(5,), z=32)
m.thing(488, -488, T_CABINET, angle=0)
m.thing(520, -576, T_CHAIR, angle=90)
lamp(536, -520, 120)
m.label(470, -540, 'LOGE')

# --------------------------------------------------------------------------- PAVILLON OUEST (start wing)
m.box(-640, -432, 112, -304, COR)
door(96, -400, 128, -336, 20, 'RFM_GRIL', COR, 'W', lintel=128, track='RFP_DADB', lock=2, lockside='W')
# corridor pilasters + radiators, west end window
for x in range(-560, 0, 160):
    m.carve(x, -432, x + 16, -416)
    m.carve(x, -320, x + 16, -304)
m.window(-656, -400, -640, -336, COR, 40, 120)
m.box(-720, -432, -656, -304, EXT)
daylight(-620, -368, 100, 240)
# chambres (south side) with a service yard behind their windows
m.box(-640, -592, -480, -448, ROOM)   # Chambre 1 (start)
door(-576, -464, -512, -432, 21, 'RFD_SGL', ROOM, 'S')
bed(-640, -592, ROOM)
table(-592, -592, -576, -560, ROOM, 30)
m.window(-608, -608, -544, -592, ROOM, 40, 104)
m.thing(-528, -540, T_START, angle=90)
m.thing(-500, -470, T_CHAIR, angle=180)
m.thing(-500, -580, T_RADIATOR, angle=90)
lamp(-560, -520, 120, radius=160)
m.label(-630, -520, 'CHAMBRE')

m.box(-448, -592, -288, -448, ROOM)   # Chambre 2
door(-384, -464, -320, -432, 24, 'RFD_SGL', ROOM, 'S')
bed(-448, -592, ROOM)
bed(-336, -592, ROOM)
m.window(-416, -608, -352, -592, ROOM, 40, 104)
m.thing(-368, -500, T_DRESS)
m.thing(-400, -470, T_ORDERLY, angle=90, tid=102, dormant=True)
lamp(-368, -520, 120, radius=160)

m.box(-256, -592, -96, -448, ROOM)    # Chambre 3
door(-192, -464, -128, -432, 25, 'RFD_SGL', ROOM, 'S')
bed(-256, -592, ROOM)
m.window(-224, -608, -160, -592, ROOM, 40, 104)
m.thing(-160, -560, T_9MM)
m.thing(-128, -470, T_CABINET, angle=180)
lamp(-176, -520, 120, radius=160)

m.box(-64, -592, 112, -448, WC)       # lavabos
door(0, -464, 64, -432, 26, 'RFD_SGL', WC, 'S')
m.raise_block(96, -576, 112, -480, 34, 'RFM_TOP', 'RFP_TILE', WC)
m.thing(40, -560, T_DRESS)
lamp(24, -520, 120, 220, 232, 240, 160)
m.box(-640, -672, -96, -608, EXT)     # service yard behind the windows (light only)
for x in (-576, -384, -192):
    daylight(x, -570, 90, 200)

m.box(-64, -304, 112, -208, POSTE)    # poste de surveillance
door(48, -304, 112, -272, 22, 'RFD_SGL', POSTE, 'N')
m.window(-48, -304, 16, -288, POSTE, 40, 104)
table(-48, -256, 32, -224, POSTE, 32)
m.thing(-8, -240, T_KGRILLE, z=34)
m.thing(16, -240, T_NOTE, args=(0,), z=32)
m.thing(-40, -212, T_CABINET, angle=270)
m.thing(-8, -280, T_CHAIR, angle=90)
m.thing(80, -240, T_ORDERLY, angle=270, tid=101, dormant=True)
lamp(24, -256, 120, radius=180)
m.label(-60, -230, 'POSTE')

m.box(-256, -304, -160, -224, ROOM, light=100)   # closet
door(-224, -304, -176, -272, 23, 'RFD_SGL', ROOM, 'N')
shelf(-256, -240, -160, -224, ROOM)
m.thing(-232, -256, T_9MM)
m.thing(-184, -256, T_9MM)
# corridor dressing: dead orderly, pistol, first cartridges
m.thing(-540, -372, T_CORPSE, angle=20)
m.thing(-544, -392, T_BROWNING)
m.thing(-500, -400, T_9MM)
m.thing(-330, -420, T_RADIATOR, angle=90)
m.thing(-100, -316, T_RADIATOR, angle=270)
m.thing(-460, -368, T_TROLLEY, angle=0)
for x in (-480, -240, 0):
    lamp(x, -368, 140, radius=200)
# E1 wake: orderly in the poste when the player passes the middle of the corridor
wake_line(-200, -432, -200, -304, 101, 1)
wake_line(-64, -260, 112, -260, 102)
m.thing(-8, -224, T_AMB, args=(3, 50))
m.label(-620, -370, 'COULOIR DU PAVILLON OUEST')
sign(132, -376, 'W', 'RFSIGN8')          # PAVILLON OUEST (hall side of the grille)
sign(-60, -368, 'S', 'RFSIGN0', 96)      # ADMISSIONS plaque above the corridor near the grille

# --------------------------------------------------------------------------- COUR DES HOMMES
m.box(0, 0, 768, 640, YARD)
m.box(0, 0, 768, 96, ARC)                                # south arcade
for x in (32, 160, 288, 448, 576, 704):
    pillar(x, 64)
m.box(672, 96, 768, 576, ARC)                             # east arcade
for y in (128, 256, 384, 512):
    pillar(672, y)
# basin and planter
m.box(320, 256, 448, 384, YARD, floor=-16, ftex='RFF_SLAB', lower='RFS_BASE')
m.box(336, 272, 432, 368, YARD, floor=-40, ftex='RFF_CERD', lower='RFS_BASE', light=180)
m.raise_block(96, 400, 192, 496, 40, 'RFF_GRAV', 'RFS_BASE', YARD)
m.raise_block(96, 128, 192, 224, 40, 'RFF_GRAV', 'RFS_BASE', YARD)
# north perron (four steps up to the gallery level)
m.box(0, 576, 768, 592, YARD, floor=-16, ftex='RFF_SLAB', lower='RFS_BASE')
m.box(0, 592, 768, 608, YARD, floor=0, ftex='RFF_SLAB', lower='RFS_BASE')
m.box(0, 608, 768, 624, YARD, floor=16, ftex='RFF_SLAB', lower='RFS_BASE')
m.box(0, 624, 768, 640, YARD, floor=32, ftex='RFF_SLAB', lower='RFS_BASE')
m.door(352, 640, 416, 656, 45, 'RFM_GRIL', 'RFS_BASE', GAL, kind='open', speed=8, lock=4, lockside='S')
# benches under the arcade, ambience
for x in (100, 230, 520, 640):
    m.thing(x, 30, T_BENCH, angle=90)
m.thing(736, 200, T_BENCH, angle=180)
m.thing(736, 440, T_BENCH, angle=180)
m.thing(384, 320, T_AMB, args=(1, 60))
# E3: porte-registre on the perron, orderlies from the east arcade
m.thing(384, 632, T_PORTE, angle=270, tid=301, dormant=True)
m.thing(720, 180, T_ORDERLY, angle=180, tid=301, dormant=True)
m.thing(720, 330, T_ORDERLY, angle=180, tid=301, dormant=True)
m.thing(200, 560, T_ORDERLY, angle=270, tid=301, dormant=True, skill='hard')
wake_line(336, 24, 432, 24, 301, 3)
m.label(300, 480, 'COUR DES HOMMES')
sign(400, 8, 'S', 'RFSIGN2', 96)      # PAVILLON EST direction plaque under the arcade

# --------------------------------------------------------------------------- PAVILLON EST
door(768, 272, 800, 368, 40, 'RFD_DBL', ARC, 'W', lintel=112, track='RFS_LIME')
steps(800, 272, 848, 368, 'x', [-16, 0, 16], WARD, depth=16, ceil_over=144)
m.box(848, 128, 1408, 512, WARD)
m.box(848, 128, 960, 240, OFFICE)                          # office infirmiere
door(880, 240, 944, 272, 41, 'RFD_SGL', WARD, 'N', lintel=112)
m.modify(880, 240, 944, 256, ceil=OFFICE.floor + 112)
table(864, 144, 944, 176, OFFICE, 32)
m.thing(904, 200, T_ORDERLY, angle=90, tid=402, dormant=True)
m.thing(880, 190, T_MAG, z=0)
m.thing(928, 160, T_CHAIR, angle=270)
lamp(904, 190, 110, radius=160)
for k in range(3):                                          # two rows of beds
    bed(992 + k * 96, 448 - 16, WARD)
    bed(992 + k * 96, 128, WARD)
m.box(1296, 128, 1408, 512, WARD, floor=32, ftex='RFF_WOOD', lower='RFW_PANL')  # dais
table(1328, 288, 1392, 320, WARD, 72)
m.thing(1360, 340, T_DRESS)
m.thing(1360, 280, T_CHAIR, angle=90)
# windows north and south onto light wells
for x in (880, 1008, 1136, 1264):
    m.window(x, 512, x + 64, 528, WARD, 64, 176)
    m.window(x, 112, x + 64, 128, WARD, 64, 176)
    daylight(x + 32, 480, 150, 240)
    daylight(x + 32, 160, 150, 240)
m.box(848, 528, 1408, 592, EXT)
m.box(848, 48, 1408, 112, EXT)
for x in (960, 1120, 1280):
    lamp(x, 320, 180, radius=240)
m.thing(1000, 320, T_TROLLEY, angle=0)
m.thing(1200, 400, T_RADIATOR, angle=0)
m.thing(1100, 320, T_AMB, args=(3, 45))
# E4: brancardier on the dais charges down the aisle; orderly from the office
m.thing(1360, 400, T_BRANC, angle=180, tid=401, dormant=True)
m.thing(1200, 240, T_ORDERLY, angle=180, tid=401, dormant=True, skill='hard')
wake_line(900, 288, 900, 496, 401)
wake_line(1120, 224, 1120, 416, 402)
m.label(950, 300, 'PAVILLON EST - SALLE COMMUNE')
sign(768, 200, 'E', 'RFSIGN2', 84)

# stair down to the laundry (east side)
door(1408, 400, 1440, 464, 42, 'RFM_DOOR', WARD, 'W', lintel=104, track='RFP_DRK')
m.box(1440, 400, 1504, 464, SERV, floor=16, ceil=160)
steps(1440, 464, 1504, 688, 'y', [0, -16, -32, -48, -64, -80, -96], SERV, depth=32, ceil_over=144)
m.box(1440, 688, 1504, 752, SERV, floor=-96, ceil=48)
door(1408, 688, 1440, 752, 47, 'RFM_DOOR', LGR, 'E', lintel=104, track='RFP_DRK')
lamp(1472, 432, 130, 230, 224, 200, 150)
lamp(1472, 600, 40, 230, 224, 200, 150)
sign(1404, 400, 'E', 'RFSIGN3', 120)   # LINGERIE plaque beside the service door

# --------------------------------------------------------------------------- LINGERIE
m.box(1040, 656, 1408, 1008, LGR)
for (x, y) in ((1120, 752), (1120, 880), (1264, 752), (1264, 880)):
    m.raise_block(x, y, x + 64, y + 64, 48, 'RFM_TOP', 'RFM_PANL', LGR)
m.box(1232, 1008, 1360, 1072, LGR, floor=-80, ceil=32, light=90, wall='RFP_DRK', lower='RFM_PANL')  # boiler alcove
m.raise_block(1056, 720, 1088, 752, 30, 'RFW_TOP', 'RFW_PANL', LGR)
m.thing(1072, 736, T_KPASSE, z=32)
m.thing(1072, 700, T_NOTE, args=(2,), z=0)
m.thing(1200, 960, T_DRESS)
m.thing(1350, 700, T_MAG)
m.thing(1200, 700, T_TROLLEY, angle=90)
m.thing(1340, 980, T_TROLLEY, angle=0)
m.thing(1224, 816, T_AMB, args=(2, 60))
lamp(1200, 816, 26, 200, 214, 230, 200)
lamp(1330, 950, 26, 200, 214, 230, 200)
lamp(1080, 700, 26, 200, 214, 230, 160)
# secret drying room behind a tiled panel
door(1408, 896, 1440, 960, 43, 'RFP_TILE', LGR, 'W', lintel=96, track='RFP_TILE')
m.box(1440, 880, 1520, 976, LGR, special=1024, light=96, wall='RFP_DRK', ftex='RFF_WOOD')
m.thing(1480, 928, T_MAG)
m.thing(1500, 900, T_MAG)
m.thing(1460, 950, T_DRESS)
# E5: orderlies among the vats, porte-registre at the top of the west stair
m.thing(1200, 820, T_ORDERLY, angle=180, tid=501, dormant=True)
m.thing(1230, 900, T_ORDERLY, angle=180, tid=501, dormant=True)
m.thing(1100, 960, T_ORDERLY, angle=0, tid=501, dormant=True, skill='hard')
wake_line(1392, 688, 1392, 752, 501)
wake_line(1216, 656, 1216, 1008, 502, 4)
m.label(1120, 680, 'LINGERIE')
# west stair up to the gallery
door(1008, 704, 1040, 768, 44, 'RFM_DOOR', LGR, 'E', lintel=104, track='RFP_DRK')
steps(752, 704, 1008, 768, '-x', [-80, -64, -48, -32, -16, 0, 16, 32], SERV, depth=32, ceil_over=144)
m.thing(800, 736, T_PORTE, angle=0, tid=502, dormant=True)
lamp(880, 736, 100, 230, 224, 200, 150)

# --------------------------------------------------------------------------- GALERIE NORD
m.box(0, 656, 752, 800, GAL)
for x in (64, 192, 512, 640):
    m.window(x, 640, x + 64, 656, GAL, 80, 176)
    daylight(x + 32, 690, 120, 220)
for x in (120, 300, 460, 620):
    lamp(x, 760, 190, radius=200)
m.thing(160, 780, T_BENCH, angle=270)
m.thing(560, 780, T_BENCH, angle=270)
m.thing(680, 780, T_RADIATOR, angle=270)
m.thing(300, 740, T_AMB, args=(0, 45))
m.thing(200, 700, T_MAG)
m.label(280, 770, 'GALERIE NORD')
sign(384, 660, 'S', 'RFSIGN9', 120)
door(-32, 704, 0, 768, 46, 'RFD_SGL', GAL, 'E', lintel=112, track='RFP_DADB')

# --------------------------------------------------------------------------- REGISTRES
m.box(-336, 656, -32, 944, REG)
shelf(-320, 912, -48, 944, REG)
shelf(-336, 672, -304, 912, REG)
shelf(-256, 720, -224, 880, REG)
shelf(-160, 720, -128, 880, REG)
table(-112, 768, -48, 800, REG, 32)
m.thing(-80, 808, T_NOTE, args=(3,), z=0)
m.thing(-80, 740, T_CHAIR, angle=90)
m.thing(-100, 700, T_MAG)
m.thing(-300, 700, T_DRESS)
m.thing(-190, 900, T_ORDERLY, angle=270, tid=503, dormant=True, skill='hard')
lamp(-192, 800, 160, radius=220)
lamp(-80, 700, 160, radius=180)
m.thing(-190, 780, T_AMB, args=(3, 40))
m.label(-330, 930, 'REGISTRES')
sign(-4, 704, 'E', 'RFSIGN4', 120)
door(-144, 624, -80, 656, 48, 'RFD_SGL', REG, 'N', lintel=112, track='RFP_DADR')

# --------------------------------------------------------------------------- COULOIR OUEST + CHAPELLE
m.box(-160, 560, -32, 624, COR, floor=32, ceil=208, light=130)
steps(-160, 496, -32, 560, '-y', [24, 16, 8, 0], COR, depth=16, ceil_over=176, lower='RFP_PLN')
m.box(-160, 64, -32, 496, COR, ceil=176, light=126)
for (y0, sill, lintel) in ((112, 48, 144), (400, 48, 144), (576, 80, 176)):
    m.window(-32, y0, 0, y0 + 64, COR, sill, lintel)
    daylight(-96, y0 + 32, 110, 220)
for y in (200, 330, 470):
    lamp(-96, y, 150, radius=190)
m.thing(-96, 300, T_AMB, args=(0, 40))
m.label(-150, 240, 'COULOIR OUEST')
m.thing(-140, 380, T_RADIATOR, angle=0)
# chapel: nave, aisles, altar dais, high windows, sacristy secret
door(-192, 352, -160, 480, 49, 'RFD_DBL', CH, 'E', lintel=128, track='RFS_LIME')
m.box(-640, 256, -192, 576, CHA)
m.box(-640, 352, -192, 480, CH)
for x in (-560, -448, -336):
    pillar(x, 320)
    pillar(x, 480)
m.box(-640, 352, -560, 480, CH, floor=16, lower='RFS_BASE')
m.raise_block(-624, 384, -592, 448, 40, 'RFF_SLAB', 'RFS_LIME', m.cells[(-624 // UNIT, 384 // UNIT)])
for x in (-560, -432, -304):
    m.window(x, 576, x + 64, 592, CHA, 128, 192)
    daylight(x + 32, 540, 170, 260)
m.box(-640, 592, -192, 640, EXT)
m.thing(-576, 416, T_NOTE, args=(4,), z=16)
m.thing(-560, 400, T_DRESS, z=16)
m.thing(-560, 436, T_MAG, z=16)
m.thing(-608, 380, T_FLICKER, args=(255, 190, 120, 120, 90), z=70)
m.thing(-608, 452, T_FLICKER, args=(255, 190, 120, 120, 90), z=70)
lamp(-400, 416, 200, 255, 226, 190, 260)
lamp(-260, 416, 200, 255, 226, 190, 220)
for y in (300, 540):
    m.thing(-500, y, T_BENCH, angle=0)
    m.thing(-380, y, T_BENCH, angle=0)
m.thing(-400, 416, T_AMB, args=(3, 35))
m.label(-630, 560, 'CHAPELLE VIDE')
sign(-164, 384, 'E', 'RFSIGN5', 100)
door(-544, 224, -480, 256, 51, 'RFS_LIME', CHA, 'N', lintel=96, track='RFS_LIME')
m.box(-576, 160, -448, 224, CHA, special=1024, light=88, wall='RFP_DRK', ftex='RFF_WOOD', ceil=128)
m.thing(-512, 190, T_MAG)
m.thing(-480, 190, T_MAG)
m.thing(-544, 190, T_DRESS)

# --------------------------------------------------------------------------- CONSULTATIONS
door(-144, 48, -80, 80, 35, 'RFD_SGL', COR, 'N', lintel=112, track='RFP_TILE')
m.box(-304, -64, -32, 48, CONS)                          # salle d'attente
m.box(-224, -80, -112, -64, CONS, ceil=128)              # opening to the corridor
m.box(-448, -192, 112, -80, C2C)                         # couloir des consultations
m.box(-448, -64, -320, 48, CONS, light=124)              # cabinet A
door(-400, -96, -336, -64, 31, 'RFD_SGL', CONS, 'N', track='RFP_TILE')
m.box(0, -64, 112, 48, CONS, light=124)                  # infirmerie
door(32, -96, 96, -64, 32, 'RFD_SGL', CONS, 'N', track='RFP_TILE')
door(96, -176, 128, -112, 30, 'RFD_SGL', C2C, 'W', lintel=112, track='RFP_DADB', lock=1, lockside='E')
table(-432, 0, -368, 32, CONS, 32)
table(16, 0, 80, 32, CONS, 32)
m.thing(-400, -20, T_CHAIR, angle=90)
m.thing(48, -20, T_CHAIR, angle=90)
m.thing(-280, 20, T_BENCH, angle=0)
m.thing(-160, 20, T_BENCH, angle=0)
m.thing(-60, 20, T_CABINET, angle=270)
m.thing(-120, -30, T_DRESS)
m.thing(-380, 20, T_MAG)
m.thing(-300, -136, T_MAG)
m.thing(20, 30, T_DRESS)
for x in (-400, -240, -80, 60):
    lamp(x, -136, 120, radius=170)
lamp(-168, -8, 130, radius=200)
m.thing(-168, -8, T_AMB, args=(3, 40))
# E6: brancardier waits in the corridor, orderlies in the offices; porte-registre 701 rests here until the finale
m.thing(-380, -136, T_BRANC, angle=0, tid=601, dormant=True)
m.thing(-384, 0, T_ORDERLY, angle=270, tid=602, dormant=True)
m.thing(56, -8, T_ORDERLY, angle=270, tid=602, dormant=True)
m.thing(-200, -136, T_ORDERLY, angle=0, tid=602, dormant=True, skill='hard')
m.thing(80, 20, T_PORTE, angle=270, tid=700, dormant=True)
wake_line(-224, -72, -112, -72, 601)
wake_line(-100, -192, -100, -80, 602)
m.label(-300, -180, 'CONSULTATIONS')
m.label(-290, 30, "SALLE D'ATTENTE")
sign(-48, -100, 'N', 'RFSIGN1', 96)
sign(132, -184, 'W', 'RFSIGN1', 100)
sign(432, -448, 'S', 'RFSIGN7', 120)

# --------------------------------------------------------------------------- HALL details, E2 & E7
m.thing(384, -520, T_FAL)
m.thing(400, -540, T_MAG)
m.thing(368, -540, T_MAG)
m.thing(384, -470, T_CORPSE, angle=200)
m.thing(180, -400, T_9MM)
m.thing(600, -420, T_DRESS)
m.thing(240, -140, T_MAG)
m.thing(160, -220, T_RADIATOR, angle=0)
m.thing(600, -300, T_RADIATOR, angle=180)
m.thing(300, -380, T_CHAIR, angle=270)
m.thing(400, -380, T_CHAIR, angle=270)
m.thing(200, -260, T_TROLLEY, angle=45)
for (x, y) in ((224, -352), (544, -352), (224, -160), (544, -160), (384, -256)):
    lamp(x, y, 230, radius=260)
m.thing(384, -256, T_AMB, args=(3, 50))
# E2: one orderly behind the counter, one from the courtyard door
m.thing(336, -280, T_ORDERLY, angle=270, tid=201, dormant=True)
m.thing(384, -30, T_ORDERLY, angle=270, tid=201, dormant=True)
wake_line(480, -448, 480, -64, 201, 2)
# E7: finale wave woken when leaving the lodge after the winch (director gates tid 700)
m.thing(704, 200, T_ORDERLY, angle=180, tid=700, dormant=True)
m.thing(720, 40, T_ORDERLY, angle=180, tid=700, dormant=True)
m.thing(560, 40, T_ORDERLY, angle=180, tid=700, dormant=True)
m.thing(200, 40, T_ORDERLY, angle=0, tid=700, dormant=True, skill='hard')
wake_line(496, -424, 592, -424, 700, 6)
sign(352, -440, 'S', 'RFSIGN6', 136)   # SORTIE above the vestibule opening
sign(352, -96, 'N', 'RFSIGN2', 136)    # PAVILLON EST above the courtyard door

# --------------------------------------------------------------------------- tour points (dev screenshots)
tour = [
    (-528, -560, 90, 4), (-500, -368, 0, 3), (150, -368, 10, 2), (384, -430, 90, 2), (384, 20, 90, 3),
    (384, 600, 270, 5), (880, 320, 0, 3), (1080, 700, 40, 4), (720, 728, 180, 2), (-48, 700, 160, 3),
    (-208, 416, 180, -3), (90, -136, 180, 2), (536, -480, 270, 4), (384, -700, 270, 3), (384, -900, 270, 2),
]
for i, (x, y, ang, pitch) in enumerate(tour):
    m.thing(x, y, T_TOUR, angle=ang, args=(i + 1, pitch))

# --------------------------------------------------------------------------- autopilot route (dev)
route = [
    (-544, -470, 1, 40, 0, 90), (-544, -392, 0, 0, 1, 0), (-200, -368, 0, 0, 0, 0), (80, -330, 1, 40, 0, 90),
    (-8, -260, 0, 30, 0, 0), (80, -330, 1, 40, 0, 90), (80, -368, 1, 40, 0, 0), (200, -368, 0, 0, 0, 0),
    (384, -520, 0, 20, 2, 0), (384, -100, 1, 40, 2, 90), (384, 40, 0, 0, 0, 0), (600, 320, 0, 0, 0, 0),
    (760, 320, 1, 40, 0, 0), (900, 320, 0, 0, 0, 0), (1360, 430, 0, 0, 0, 0), (1400, 432, 1, 40, 0, 0),
    (1472, 432, 0, 0, 0, 0), (1472, 720, 0, 0, 0, 0), (1448, 720, 1, 40, 0, 180), (1072, 720, 0, 20, 0, 0),
    (1048, 736, 1, 40, 0, 180), (784, 736, 0, 0, 0, 0), (600, 728, 0, 0, 0, 0), (8, 736, 1, 40, 0, 180),
    (-80, 810, 1, 40, 0, 270), (-112, 664, 1, 40, 0, 270), (-112, 300, 0, 0, 0, 0), (-112, 88, 1, 40, 0, 270),
    (-168, 0, 0, 0, 0, 0), (-168, -100, 0, 0, 0, 0), (0, -136, 0, 0, 0, 0), (88, -144, 1, 40, 0, 0),
    (300, -300, 0, 0, 0, 0), (544, -424, 1, 40, 0, 270), (560, -560, 1, 40, 0, 270), (544, -424, 1, 40, 0, 90),
    (384, -440, 0, 0, 0, 0), (384, -620, 0, 0, 0, 0), (384, -760, 0, 0, 0, 0), (384, -1000, 0, 0, 0, 0),
]
for i, (x, y, use, wait, weapon, ang) in enumerate(route):
    m.thing(x, y, T_WP, angle=ang, args=(i + 1, use, wait, weapon))


# --------------------------------------------------------------------------- build
def main():
    text = m.build()
    (ROOT / 'src' / 'maps' / 'RF01.wad').write_bytes(m.wad(text))
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'RF01_TEXTMAP.txt').write_text(text, encoding='utf-8')
    m.plan_png(ROOT / 'build' / 'RF01_plan.png')
    exit_cells = {(x // UNIT, -1016 // UNIT) for x in range(96, 672, 16)}
    report = m.check({T_KGRILLE: 2, T_KPASSE: 1}, exit_cells, winch_cell=(560 // UNIT, -576 // UNIT), winch_tag=50)
    print('RF01 built:', m.stats)
    print('check:', {k: v for k, v in report.items() if k != 'unreachable_things'})
    if report['unreachable_things']:
        print('UNREACHABLE THINGS:', report['unreachable_things'])
    return report


if __name__ == '__main__':
    main()
