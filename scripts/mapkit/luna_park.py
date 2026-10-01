#!/usr/bin/env python3
"""The Luna Park of the Porte Maillot as one place for RF04 (closed, 14 June 1940, morning) and RF05 (lit again).

A RECONSTRUCTION at game scale, not a survey (docs/production/maps/RF04_RELEVE_PLAN.md): the volumes and relations
come from the panorama of about 1910 (BHVP), the postcard Carnavalet CP9 and Roger Schall's photograph of 1935; the
order of the places comes from the novel (l. 451-551). North = +y, 1 cell = 16 u, sky at SKY.

  south      the backs of the public entrance (the LUNA PARK gates, the arcaded pavilion), closed
  east       the service path along the hoarding, behind the attractions: the staff door at its south end, the
             narrow rails, the guard's hut in a forecourt, the staff barrier, then a passage west to the esplanade
  east bldgs the attractions' backs; BROOKLYN BRIDGE faces the esplanade, its technical corridor runs behind it
  centre     the esplanade; the long basin of the water chute (the Niagara), its balustrade, two footbridges, the
             stair at its south end, the rocks of the cascade at its north-west end; the chute coming down from its
             tower at the north-east; the mast of the aerial tower
  west       the artificial rocks and the roller coaster on its trestles, against the sky; the loading platform; the
             lift hill climbing north into the rocks
  north      the dance hall, its marquee and turnstiles; behind it the lane behind the track (a see-through fence
             from the esplanade) and the substation door in the rocks

build_park(m, sign) authors the geometry and returns the anchors the chapters use (scenes, waves, route).
"""
from dataclasses import replace
from udmf import Cell, UNIT

SKY = 512
ENV_PARK, ENV_ROOM, ENV_CORR, ENV_HALL = (32, 0), (30, 8), (13, 0), (30, 3)

PARK = Cell(floor=0, ceil=SKY, ftex='RF4_DALH', ctex='F_SKY1', light=160, wall='RF4_FAC1', color=0xE2DED4,
            env=ENV_PARK, lower='RF4_BASC')
PATH = replace(PARK, ftex='RF4_HERB', wall='RF4_HANG', light=152)
RAILS = replace(PATH, ftex='RF4_DECA')
FORE = replace(PARK, ftex='RFF_GRAV', wall='RF4_HANG', light=156)
GRAVEL = replace(PARK, ftex='RFF_GRAV')
BASIN = replace(PARK, floor=-96, ftex='RF4_BASF', wall='RF4_BASS', lower='RF4_BASS', light=150, env=(30, 1))
ROCKS = replace(BASIN, ftex='RF4_ROCF', wall='RF4_ROCH', lower='RF4_ROCH')
PUDDLE = replace(BASIN, ftex='RF4_FLAQ')
LANE = replace(PARK, ftex='RF4_DALH', wall='RF4_HANG', light=144)
CORR = Cell(floor=0, ceil=104, ftex='RFF_WOOD', ctex='RFP_CEID', light=92, wall='RF4_CABL', color=0xEADCC4, env=ENV_CORR)
ATELIER = Cell(floor=0, ceil=120, ftex='RFF_WOOD', ctex='RFP_CEID', light=88, wall='RF4_ATEL', color=0xEAD8C0, env=ENV_ROOM)
HALL = Cell(floor=0, ceil=192, ftex='RF4_PARQ', ctex='RFP_CEID', light=122, wall='RFP_PLN', color=0xF0E2C8, env=ENV_HALL)
VEST = Cell(floor=0, ceil=112, ftex='RFF_CONC', ctex='RFP_CEID', light=72, wall='RF4_BASC', color=0xE0D8C8, env=ENV_ROOM)

# --------------------------------------------------------------------------- the plan (u)
SVC_X0, SVC_X1 = 1792, 1920          # service path
FORE_BOX = (1664, 992, 1792, 1200)   # the forecourt of the hut, west of the path
HUT = (1680, 1024, 1776, 1152)       # the guard's hut: window and clock east (onto the path), keys north
BARRIER_Y = 1208                     # the staff barrier across the path, north of the hut
TURN_Y0, TURN_Y1 = 1600, 1664        # the passage west from the path to the esplanade
ESP = (256, 128, 1536, 2240)         # the esplanade
BAS = (768, 384, 1152, 1472)         # the basin
CHUTE = (1024, 1472, 1152, 1856)     # the chute's ramp (sloped, -96 to 320), its tower north of it
TOWER = (992, 1856, 1184, 1984)
TRESTLE_XS = (288, 400)              # the two rows of posts, west
TRESTLE_Y0, TRESTLE_Y1 = 256, 1120   # first and last post
QUAI = (416, 1216, 576, 1600)        # the loading platform
QUAI_Z = 96
HALLB = (480, 1920, 928, 2240)       # the dance hall's building
HALL_IN = (512, 1952, 896, 2208)     # its room
MARQ = (576, 1856, 832, 1920)        # its marquee
ORCH = (912, 2144, 1008, 2224)       # the orchestra's box, in the hall's east wing (the stage's side door is RF04's)
SERVICE_DOOR = (1008, 2160, 1024, 2208)   # the service door at the back of the hall, behind the stage (l. 703): the
SERVICE = (1024, 2160, 1216, 2208)   # chapters' door; the service corridor beyond it, in the east wing (RF05's exit)
SIDE_DOOR = (528, 2208, 592, 2240)   # the hall's side door to the lane: the door leaf south (the chapter's), frame north
LANE_BOX = (256, 2240, 1664, 2336)   # the lane behind the track
SHEDS = ((1024, 1120), (1168, 1264), (1424, 1504))   # sheds in the rocks north of the lane
SUB_DOOR = (1536, 2336, 1600, 2368)  # the substation door, in the rocks: frame south (the park's), leaf north
BROOKLYN = (576, 832)                # y range of the Brooklyn facade (west face of the east buildings, x 1536)
CORR_X0, CORR_X1 = 1600, 1696        # the technical corridor behind it
MAST = (1344, 992)                   # its arms clear the basin's balustrade
BANDSTAND = (1248, 1344, 1344, 1440)
CAROUSEL = (1216, 1680, 1344, 1808)
RIDE_Z = 384                         # the scenic railway on the crest of the rocks
RIDE_WEST = (96, 160)                # its track over the west rocks (x)
RIDE_NORTH = (2400, 2432)            # and over the north rocks (y), to x 1472


def roofline(m, x0, y0, x1, y1, top, side, base, ftex='RF2_ZINC'):
    """A mass lower than the sky: its floor and ceiling are its top (the side texture is its face), open sky above.
    Closed, so that the rooms carved in it draw no wall above it."""
    m.box(x0, y0, x1, y1, base, floor=top, ceil=top, ftex=ftex, lower=side, wall=side)


def open_top(m, x0, y0, x1, y1):
    """Open a mass's cells to the sky, to stand something on their top (posts, a dome). Never next to a roofed room:
    the room's upper wall would be drawn up to the sky height."""
    for p in m._cells(*m._range(x0, y0, x1, y1)):
        c = m.cells.get(p)
        if c is not None:
            m.cells[p] = replace(c, ceil=SKY, ctex='F_SKY1')


def opening(m, x0, y0, x1, y1, base, lintel, top, side, roof='RF2_ZINC', under='RFP_CEID'):
    """A doorway, a porch or a recess cut in a mass of height `top` and opening on the open sky: the cell is capped
    at the mass's height with a sky ceiling and the lintel is a slab (side texture: the mass's face), so that no wall
    of the opening rises above the mass (encounters.sky_uppers)."""
    m.box(x0, y0, x1, y1, base, ceil=top, ctex='F_SKY1')
    m.slab(x0, y0, x1, y1, base.floor + lintel, top, side, top=roof, bottom=under)


def walls(m, x0, y0, x1, y1, tex, sides='NSEW'):
    """The walls of a room carved in a mass show the room's texture: a riser shows the higher cell's `lower`, so the
    ring of mass cells around the room takes it (only on sides at least 32 thick: a 16 wall shows both its faces)."""
    cx0, cy0, cx1, cy1 = x0 // UNIT, y0 // UNIT, x1 // UNIT, y1 // UNIT
    ring = []
    if 'S' in sides:
        ring += [(x, cy0 - 1) for x in range(cx0, cx1)]
    if 'N' in sides:
        ring += [(x, cy1) for x in range(cx0, cx1)]
    if 'W' in sides:
        ring += [(cx0 - 1, y) for y in range(cy0, cy1)]
    if 'E' in sides:
        ring += [(cx1, y) for y in range(cy0, cy1)]
    room = m.cells[(cx0, cy0)]
    for p in ring:
        c = m.cells.get(p)
        if c is not None and c.role != 'door' and (c.ceil <= c.floor or c.floor >= room.ceil):
            m.cells[p] = replace(c, lower=tex)


def rail_line(m, x0, x1, y, tex):
    """A blocking see-through rail along x at y, one decor line per run of identical cells (a decor line stays in one
    sector): call it once the slabs of the cells it crosses are placed."""
    cy = int(y // UNIT)
    runs, cur, start = [], None, None
    for cx in range(x0 // UNIT, x1 // UNIT):
        c = m.cells.get((cx, cy))
        if c != cur:
            if cur is not None:
                runs.append((start, cx * UNIT))
            cur, start = c, cx * UNIT
    if cur is not None:
        runs.append((start, x1))
    for (s, e) in runs:
        m.decor_line(s, y, e, y, tex, 0, blocking=True, yscale=4)


def build_park(m, sign):
    """Author the park into MapBuilder m. sign: the chapter's sign() helper (decor line at a texture's own scale)."""
    a = {}
    # ---- the south: the backs of the public entrance, closed, the full width; the domed pillars of the gates above
    roofline(m, 0, 0, SVC_X0, 128, 256, 'RF4_PORT', PARK, ftex='RF4_ROCF')
    for x in (448, 768, 1088, 1408):
        open_top(m, x, 48, x + 64, 112)
        m.slab(x, 48, x + 64, 112, 256, 352, 'RF4_BASC', top='RF4_ROCF', bottom='RF4_BASC')     # the shaft
        m.slab(x, 48, x + 64, 112, 352, 368, 'RF2_ZINC')                                        # the cornice
        m.slab(x + 16, 64, x + 48, 96, 368, 400, 'RF2_ZINC')                                    # the dome
        m.slab(x + 16, 64, x + 32, 80, 400, 440, 'RF4_MAST')                                    # the flagstaff
    # ---- the west rocks and the north rocks, irregular tops (silhouettes against the sky)
    for (y0, y1, h) in ((128, 512, 256), (512, 896, 304), (896, 1280, 272), (1280, 1664, 320), (1664, 2048, 288),
                        (2048, 2432, 336)):
        roofline(m, 0, y0, 256, y1, h, 'RF4_ROCH', PARK, ftex='RF4_ROCF')
    for (x0, x1, h) in ((256, 768, 320), (768, 1280, 352), (1280, SVC_X1, 304)):
        roofline(m, x0, 2336, x1, 2432, h, 'RF4_ROCH', PARK, ftex='RF4_ROCF')
    # the scenic railway along their crest: a track on posts against the sky, west then north
    wx0, wx1 = RIDE_WEST
    ny0, ny1 = RIDE_NORTH
    open_top(m, wx0, 128, wx1, 2432)
    open_top(m, wx0, ny0, 1472, ny1)
    for y in range(160, 2432, 128):
        for x in (wx0, wx1 - 16):
            z = m.cells[(x // UNIT, y // UNIT)].floor
            m.slab(x, y, x + 16, y + 16, z, RIDE_Z, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    for x in range(256, 1472, 128):
        for y in (ny0, ny1 - 16):
            z = m.cells[(x // UNIT, y // UNIT)].floor
            m.slab(x, y, x + 16, y + 16, z, RIDE_Z, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    m.slab(wx0, 128, wx1, ny1, RIDE_Z, RIDE_Z + 12, 'RF4_BOIS', top='RF4_VOIE', bottom='RF4_BOIS')
    m.slab(wx1, ny0, 1472, ny1, RIDE_Z, RIDE_Z + 12, 'RF4_BOIS', top='RF4_VOIE', bottom='RF4_BOIS')
    # two dark mouths where the track went into the rocks
    for (y0, y1) in ((704, 768), (1408, 1472)):
        opening(m, 224, y0, 256, y1, replace(PARK, light=70), 96, m.cells[(14, y0 // UNIT)].floor, 'RF4_ROCH',
                roof='RF4_ROCF', under='RF4_ROCF')
    # ---- the service path, the hoarding, the avenue beyond it (seen over the hoarding, not reached)
    m.box(SVC_X0, 0, SVC_X1, TURN_Y1, PATH)
    m.box(SVC_X0, 384, SVC_X1, 448, RAILS)                                          # narrow rails across it (l. 463)
    roofline(m, SVC_X1, 0, SVC_X1 + 16, 2432, 176, 'RF2_PALI', PATH)
    m.box(SVC_X1 + 16, 0, SVC_X1 + 112, 2432, replace(PARK, ftex='RF2_ASPH', wall='RF2_FAC1', light=150))
    roofline(m, SVC_X1 + 112, 0, SVC_X1 + 128, 2432, 320, 'RF2_FAC2', PARK)          # the far side of the avenue
    roofline(m, SVC_X0, TURN_Y1, SVC_X1, 2336, 288, 'RF4_ROCH', PARK, ftex='RF4_ROCF')
    m.face(SVC_X0 + 32, 0, SVC_X1 - 32, 16, 'S', texture='RFD_SGL')                # the staff door (RF02's exit)
    a['start'] = (1856, 72)
    a['rail'] = (1856, 416)
    # ---- the east buildings: masses 192 high whose west faces are the attractions' facades
    roofline(m, 1536, 128, SVC_X0, TURN_Y0, 192, 'RF4_HANG', PARK)
    m.modify(1536, 128, 1552, BROOKLYN[0], wall='RF4_FAC1', lower='RF4_FAC1')
    m.modify(1536, BROOKLYN[0], 1552, BROOKLYN[1], wall='RF4_BROO', lower='RF4_BROO')
    m.modify(1536, BROOKLYN[1], 1552, 1216, wall='RF4_FAC2', lower='RF4_FAC2')
    m.modify(1536, 1216, 1552, TURN_Y0, wall='RF4_FAC3', lower='RF4_FAC3')
    for y in (BROOKLYN[0], BROOKLYN[1] - 32):                                       # the decor bridge's two turrets
        open_top(m, 1536, y, 1568, y + 32)
        m.slab(1536, y, 1568, y + 32, 192, 272, 'RF4_BASC', top='RF2_ZINC', bottom='RF4_BASC')
        m.slab(1536, y, 1568, y + 32, 272, 280, 'RF2_ZINC')
        m.slab(1536, y + 16, 1552, y + 32, 280, 320, 'RF2_ZINC')                                # the spire
    # the technical corridor behind the bridge: in under the decor (the passage's lintel is the decor's middle, the
    # texture continued from the facade), south inside, out on the esplanade's south-east
    m.box(CORR_X0, 256, CORR_X1, 736, CORR)
    walls(m, CORR_X0, 256, CORR_X1, 736, 'RF4_CABL')
    m.modify(CORR_X0 - 16, BROOKLYN[0], CORR_X0, 672, lower='RF4_BRBK')            # the decor's back, seen from inside
    opening(m, 1536, 672, CORR_X0, 736, CORR, 112, 192, 'RF4_BROO')
    m.face(1520, 672, 1536, 736, 'E', offsetx=96)                                   # the facade seen from the esplanade
    m.face(1520, BROOKLYN[0], 1536, 672, 'E', offsetx=160)                          # runs north to south (u from 832)
    walls(m, 1552, 672, CORR_X0, 736, 'RF4_CABL', sides='NS')
    opening(m, 1536, 256, CORR_X0, 320, CORR, 112, 192, 'RF4_FAC1')
    walls(m, 1552, 256, CORR_X0, 320, 'RF4_CABL', sides='NS')
    a['corr_in'] = (1568, 704)
    a['corr_out'] = (1568, 288)
    # the forecourt of the hut, the workshop behind the corridor (its loose board is the chapter's door)
    m.box(*FORE_BOX, FORE)
    m.box(1712, 640, 1776, 768, ATELIER, special=1024)
    walls(m, 1712, 640, 1776, 768, 'RF4_ATEL', sides='NS')
    a['atelier'] = (1744, 704)
    # the passage from the path to the esplanade, and the mass north of it
    m.box(1536, TURN_Y0, SVC_X0, TURN_Y1, GRAVEL)
    roofline(m, 1536, TURN_Y1, SVC_X0, LANE_BOX[1], 192, 'RF4_HANG', PARK)
    # ---- the esplanade (fills what is left)
    m.box(*ESP, PARK, only_empty=True)
    # the lane behind the track, north of the esplanade: a see-through fence on both sides of the hall
    lx0, ly0, lx1, ly1 = LANE_BOX
    m.box(lx0, ly0, lx1, ly1, LANE)
    # the basin: 384 x 1088, 96 deep; its stair at the south end; the cascade rocks at the north-west end
    bx0, by0, bx1, by1 = BAS
    m.modify(bx0 - 16, by0 - 16, bx1 + 16, by1 + 16, lower='RF4_BASS')             # the rim: a riser shows the higher
    m.box(bx0, by0, bx1, by1, BASIN)                                                # cell's texture (the basin's wall)
    for k, z in enumerate((-24, -48, -72)):
        m.box(896, by0 + 16 * k, 1024, by0 + 16 * (k + 1), BASIN, floor=z)
    for k, z in enumerate((-72, -48, -24)):                                        # a way out, up the rocks
        m.box(bx0, by1 - 112 + 32 * k, 896, by1 - 80 + 32 * k, ROCKS, floor=z)
    m.box(bx0, by1 - 16, 896, by1, ROCKS, floor=-8)
    m.box(896, by1 - 48, 1024, by1, ROCKS, floor=-56)                               # the cascade's foot, under the chute
    for (x0, y0, x1, y1) in ((944, 1280, 1008, 1296), (960, 1264, 992, 1312), (928, 1264, 960, 1280),
                             (992, 1296, 1024, 1312)):                              # the black puddle of the shoe
        m.box(x0, y0, x1, y1, PUDDLE)
    a['shoe'] = (976, 1288)
    for (y0, y1) in ((704, 736), (1056, 1088)):                                     # two footbridges at the esplanade's level
        m.slab(bx0, y0, bx1, y1, -6, 0, 'RF4_BASC', top='RFF_WOOD', bottom='RF4_BASC')
    rail = 'RF4_BALU'                                                               # the balustrade; open at the stair,
    for (x0, y0, x1, y1) in ((bx0, by0 - 2, 896, by0 - 2), (1024, by0 - 2, bx1, by0 - 2),   # the rocks, the chute
                             (bx0 - 2, by0, bx0 - 2, 704), (bx0 - 2, 736, bx0 - 2, 1056), (bx0 - 2, 1088, bx0 - 2, by1 - 112),
                             (bx1 + 2, by0, bx1 + 2, 704), (bx1 + 2, 736, bx1 + 2, 1056), (bx1 + 2, 1088, bx1 + 2, by1)):
        m.decor_line(x0, y0, x1, y1, rail, 0, blocking=True, yscale=4)
    # the chute: a ramp from the tower (320) down into the basin (-96), too steep to climb; the tower and its pavilion
    cx0, cy0, cx1, cy1 = CHUTE
    slope = (320 + 96) / (cy1 - cy0)
    m.box(cx0, cy0, cx1, cy1, PARK, floor=-96, ftex='RF4_CHUT', wall='RF4_CHUS', lower='RF4_CHUS',
          extra=(('floorplane_a', 0.0), ('floorplane_b', -slope), ('floorplane_c', 1.0),
                 ('floorplane_d', round(slope * cy0 + 96.0, 4))))
    tx0, ty0, tx1, ty1 = TOWER
    m.raise_block(tx0, ty0, tx1, ty1, 320, 'RF4_VOIE', 'RF4_TOWR', PARK)
    for (x, y) in ((tx0, ty0), (tx1 - 16, ty0), (tx0, ty1 - 16), (tx1 - 16, ty1 - 16)):
        m.slab(x, y, x + 16, y + 16, 320, 384, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    m.slab(tx0, ty0, tx1, ty1, 384, 396, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
    m.slab(tx0 + 48, ty0 + 32, tx1 - 48, ty1 - 32, 396, 428, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
    sign(cx0, cy1 - 16, cx1, cy1 - 16, 'RF4_NIAG', 328, off=0)                       # LES CHUTES DU NIAGARA over the
    # chute's top (128 x 32), facing south down the basin
    # ---- the roller coaster on its trestles, west: two rows of posts, the track over them, the lattice between
    for x in TRESTLE_XS:
        for y in range(TRESTLE_Y0, TRESTLE_Y1 + 1, 96):
            m.slab(x, y, x + 16, y + 16, 0, 224, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    m.slab(TRESTLE_XS[0], TRESTLE_Y0, TRESTLE_XS[1] + 16, TRESTLE_Y1 + 16, 224, 236, 'RF4_BOIS', top='RF4_VOIE', bottom='RF4_BOIS')
    for x in TRESTLE_XS:
        for y in range(TRESTLE_Y0, TRESTLE_Y1, 96):
            m.decor_line(x + 8, y + 17, x + 8, y + 95, 'RF4_TREI', 0, yscale=4, texwidth=64)   # one panel between posts
    for y in range(TRESTLE_Y0, TRESTLE_Y1 + 1, 192):
        m.decor_line(TRESTLE_XS[0] + 17, y + 8, TRESTLE_XS[1] - 1, y + 8, 'RF4_TREI', 96, yscale=4, texwidth=64)
    # the loading platform (96), the station track beside it, its canvas roof, steps east and north
    qx0, qy0, qx1, qy1 = QUAI
    m.box(qx0, qy0, qx1, qy1, PARK, floor=QUAI_Z, ftex='RFF_WOOD', lower='RF4_ATEL', wall='RF4_ATEL')
    m.box(TRESTLE_XS[0], qy0, qx0, qy1, PARK, floor=QUAI_Z - 16, ftex='RF4_VOIE', lower='RF4_ATEL', wall='RF4_ATEL')
    m.slab(TRESTLE_XS[0], qy0, qx1, qy1, 192, 200, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
    for k, z in enumerate((72, 48, 24)):
        m.box(qx1 + 16 * k, 1344, qx1 + 16 * (k + 1), 1408, PARK, floor=z, ftex='RFF_WOOD', lower='RF4_ATEL')
    for k, z in enumerate((72, 48, 24)):
        m.box(448, qy1 + 16 * k, 544, qy1 + 16 * (k + 1), PARK, floor=z, ftex='RFF_WOOD', lower='RF4_ATEL')
    m.decor_line(qx1 + 1, qy0, qx1 + 1, 1344, 'RF2_RAMB', QUAI_Z, blocking=True, yscale=4)
    m.decor_line(qx1 + 1, 1408, qx1 + 1, qy1, 'RF2_RAMB', QUAI_Z, blocking=True, yscale=4)
    a['quai'] = (496, 1408)
    # the lift hill: from the station north over the lane, up to the track on the crest of the north rocks
    open_top(m, TRESTLE_XS[0], 2336, TRESTLE_XS[1] + 16, ny0)
    for k in range(13):
        y0 = qy1 + 64 * k
        y1 = min(y0 + 64, ny0)
        z = QUAI_Z + 20 * (k + 1) if k < 11 else (336, 360)[k - 11]
        m.slab(TRESTLE_XS[0], y0, TRESTLE_XS[1] + 16, y1, z, z + 12, 'RF4_BOIS', top='RF4_VOIE', bottom='RF4_BOIS')
        if y0 >= qy1 + 64:
            for x in TRESTLE_XS:
                base = m.cells[(x // UNIT, y0 // UNIT)].floor
                m.slab(x, y0, x + 16, y0 + 16, base, z, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    # ---- the mast of the aerial tower, its four arms and their nacelles
    mx, my = MAST
    m.slab(mx, my, mx + 16, my + 16, 0, 448, 'RF4_MAST', top='RF4_MAST', bottom='RF4_MAST')
    for (x0, y0, x1, y1) in ((mx - 160, my, mx, my + 16), (mx + 16, my, mx + 176, my + 16),
                             (mx, my - 160, mx + 16, my), (mx, my + 16, mx + 16, my + 176)):
        m.slab(x0, y0, x1, y1, 400, 408, 'RF4_MAST', top='RF4_MAST', bottom='RF4_MAST')
    for (x0, y0) in ((mx - 160, my - 16), (mx + 144, my - 16), (mx - 16, my - 160), (mx - 16, my + 144)):
        m.slab(x0, y0, x0 + 32, y0 + 32, 340, 372, 'RF2_ZINC', top='RF2_ZINC', bottom='RF4_BASC')
    # ---- a bandstand and the carousel, still standing on the esplanade
    sx0, sy0, sx1, sy1 = BANDSTAND
    m.raise_block(sx0, sy0, sx1, sy1, 16, 'RFF_WOOD', 'RF4_ATEL', PARK)
    for (x, y) in ((sx0, sy0), (sx1 - 16, sy0), (sx0, sy1 - 16), (sx1 - 16, sy1 - 16)):
        m.slab(x, y, x + 16, y + 16, 16, 112, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    m.slab(sx0, sy0, sx1, sy1, 112, 124, 'RF2_ZINC', top='RF2_ZINC', bottom='RFF_WOOD')
    m.slab(sx0 + 32, sy0 + 32, sx1 - 32, sy1 - 32, 124, 148, 'RF2_ZINC')
    kx0, ky0, kx1, ky1 = CAROUSEL
    m.raise_block(kx0, ky0, kx1, ky1, 16, 'RFF_WOOD', 'RF4_FAC1', PARK)
    m.slab(kx0 + 48, ky0 + 48, kx1 - 48, ky1 - 48, 16, 160, 'RF4_MAST', top='RF4_MAST', bottom='RF4_MAST')
    for (x, y) in ((kx0, ky0), (kx1 - 16, ky0), (kx0, ky1 - 16), (kx1 - 16, ky1 - 16)):
        m.slab(x, y, x + 16, y + 16, 16, 144, 'RF4_POTE', top='RF4_POTE', bottom='RF4_POTE')
    for k, (z0, z1) in enumerate(((144, 160), (160, 176), (176, 192), (192, 224))):
        m.slab(kx0 + 16 * k, ky0 + 16 * k, kx1 - 16 * k, ky1 - 16 * k, z0, z1, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
    # ---- the dance hall: the building, its room, the marquee, the porch and the turnstiles' vestibule
    hx0, hy0, hx1, hy1 = HALLB
    roofline(m, hx0, hy0, hx1, hy1, 256, 'RF4_FAC2', PARK)
    m.box(*HALL_IN, HALL)
    roofline(m, hx1, 2096, SERVICE[2] + 16, hy1, 160, 'RF4_FAC2', PARK)             # the east wing: the orchestra's box,
    m.box(*SERVICE, VEST, floor=24, ceil=24 + 104, light=64)                         # the service corridor
    walls(m, *SERVICE, 'RF4_BASC', sides='NSE')
    m.box(*ORCH, ATELIER, floor=24, light=80, special=1024)
    walls(m, *HALL_IN, HALL.wall)
    walls(m, *ORCH, 'RF4_ATEL', sides='NSE')
    a['orchestra'] = ORCH
    mx0, my0, mx1, my1 = MARQ
    m.slab(mx0, my0, mx1, my1, 136, 144, 'RF4_MARQ', top='RF4_MARF', bottom='RF4_MARF')
    m.box(736, my0, 800, my0 + 32, PARK)                                            # a hole torn in the canvas
    opening(m, mx0, hy0 - 16, mx1, hy0, replace(HALL, ftex='RFF_SLAB'), 128, 256, 'RF4_FAC2')   # the porch
    m.box(mx0, hy0, mx1, HALL_IN[1], HALL, ceil=128, ftex='RFF_SLAB')               # the turnstiles' vestibule
    a['turnstile_y'] = hy0
    sign(640, hy0 - 16, 768, hy0 - 16, 'RF4_DANS', 152, off=1)                     # SALLE DE DANSE, faded, on the porch
    # ---- the lane behind the track: its side door and its sheds
    lx0, ly0, lx1, ly1 = LANE_BOX
    dx0, dy0, dx1, dy1 = SIDE_DOOR                                                  # the side door's frame on the lane
    opening(m, dx0, dy1 - 16, dx1, dy1, LANE, 112, 256, 'RF4_FAC2')
    for (x0, x1) in SHEDS:                                                          # sheds dug into the rocks,
        top = m.cells[(x0 // UNIT, ly1 // UNIT)].floor                               # open on the lane
        opening(m, x0, ly1, x1, ly1 + 64, replace(LANE, light=110), 120, top, 'RF4_ROCH', roof='RF4_ROCF')
    for (x0, x1) in ((lx0, HALLB[0]), (HALLB[2], 1536)):                            # the fence (split where the
        rail_line(m, x0, x1, ly0 + 1, 'RFM_GRIL')                                    # lift hill's posts stand)
    dx0, dy0, dx1, dy1 = SUB_DOOR                                                   # the substation door's frame
    opening(m, dx0, dy0, dx1, dy0 + 16, LANE, 104, m.cells[(dx0 // UNIT, dy0 // UNIT)].floor, 'RF4_ROCH',
            roof='RF4_ROCF')
    return a
