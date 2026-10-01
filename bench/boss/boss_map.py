#!/usr/bin/env python3
"""BOSS01 - the boss bench map: the hall of the porters' lodge of Sainte-Anne (a bench, not a campaign map).

  start room (south): supplies, the way into the hall; the player comes back here for each reprise (tid 913)
  the hall: 768 x 640, four pillars, the lodge's counter as cover; crossing its entry line starts the fight
  north: his double doors (tag 900) and the corridor he comes from (his start, tid 910); he walks to the middle (911)
  west and east: the side doors (tag 902) the staff come through when he whistles (their spots, tid 912)

Usage: python bench/boss/boss_map.py   (writes bench/boss/maps/BOSS01.wad, bench/boss/build/BOSS01_plan.png)
"""
import sys
from pathlib import Path
from dataclasses import replace
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
from udmf import MapBuilder, Cell  # noqa: E402

ROOM = Cell(floor=0, ceil=128, ftex='RFF_SLAB', ctex='RFP_CEID', light=150, wall='RFP_PLN', color=0xF4ECDC, env=(30, 8))
HALL = replace(ROOM, ceil=192, light=144, env=(30, 3))
CORR = replace(ROOM, ceil=112, light=90, env=(13, 0))
T_START, T_MAG, T_9MM, T_DRESS, T_LAMP = 1, 30101, 30103, 30201, 30601
T_BOSS, T_SPOT = 30800, 30801
ENTRY_LINE, SIDE_DOORS, BOSS_DOOR = 901, 902, 900
SPOT_START, SPOT_GOAL, SPOT_STAFF, SPOT_PLAYER = 910, 911, 912, 913

m = MapBuilder('BOSS01')
# the start room and the way into the hall
m.box(0, 0, 256, 192, ROOM)
m.box(96, 192, 160, 256, CORR)
m.thing(128, 64, T_START, angle=90)
m.thing(128, 96, T_SPOT, angle=90, tid=SPOT_PLAYER)
m.thing(200, 24, 30623, tid=999)                                          # the signal thing walk lines activate
for (x, y, t) in ((40, 40, T_MAG), (72, 40, T_MAG), (216, 40, T_9MM), (184, 40, T_9MM), (40, 150, T_DRESS), (216, 150, T_DRESS)):
    m.thing(x, y, t)
m.thing(128, 120, T_LAMP, args=(150, 140, 120, 220), z=96)
# the hall
m.box(-256, 256, 512, 896, HALL)
for (x, y) in ((-96, 448), (320, 448), (-96, 704), (320, 704)):
    m.carve(x, y, x + 32, y + 32)
m.raise_block(0, 336, 256, 368, 40, 'RFW_TOP', 'RFW_PANL', HALL)          # the lodge's counter
m.trigger(98, 280, 158, 280, 130, (999,), repeat=True, fields={'user_scene': ENTRY_LINE})   # again after each reprise
m.thing(128, 640, T_SPOT, angle=270, tid=SPOT_GOAL)
for (x, y) in ((-128, 384), (384, 384), (-128, 768), (384, 768), (128, 576)):
    m.thing(x, y, T_LAMP, args=(150, 140, 120, 260), z=160)
# his doors and his corridor (north)
m.door(64, 896, 192, 912, BOSS_DOOR, 'RFD_DBL', 'RFP_DRK', HALL, kind='open', lock=3)
m.box(64, 912, 192, 1088, CORR)
m.thing(128, 1040, T_SPOT, angle=270, tid=SPOT_START)
m.thing(128, 1040, T_BOSS, angle=270)
# the side doors and the staff's rooms
m.door(-272, 576, -256, 640, SIDE_DOORS, 'RFD_SGL', 'RFP_DRK', HALL, kind='open', lock=3)
m.box(-368, 544, -272, 672, CORR)
m.thing(-320, 592, T_SPOT, angle=0, tid=SPOT_STAFF)
m.door(512, 576, 528, 640, SIDE_DOORS, 'RFD_SGL', 'RFP_DRK', HALL, kind='open', lock=3)
m.box(528, 544, 624, 672, CORR)
m.thing(576, 624, T_SPOT, angle=180, tid=SPOT_STAFF)
m.exit_cells = set()


def main():
    text = m.build()
    (HERE / 'maps').mkdir(exist_ok=True)
    (HERE / 'maps' / 'BOSS01.wad').write_bytes(m.wad(text))
    (HERE / 'build').mkdir(exist_ok=True)
    m.plan_png(HERE / 'build' / 'BOSS01_plan.png', scale=0.5)
    print('BOSS01 built:', m.stats)


if __name__ == '__main__':
    main()
