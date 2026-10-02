#!/usr/bin/env python3
"""FAM01 - the bench of the enemy families (a bench, not a campaign map): one hall, six stations, every specimen of
the family chosen (bench/familles/zscript/famille.zs spawns them on the spots below).

  south          the start; three pads on the floor choose the family (orderly, brancardier, porte-registre)
  centre         the view mark (wood): from it, two arcs of eight specimens show the eight rotations, the near arc
                 standing, the far arc playing walk, attack and pain in every rotation
  west           the walk: a specimen patrols between two points 512 u apart (side view from the hall)
  east           the obstacles, behind a railing: a pillar (64 u and 96 u beside it), a step of 24, doors of 96, 64, 48 u
  north-east     the attack: a pen, a specimen and a post it strikes (melee from close, missiles from 400 u)
  north-west     pain (a specimen hit every four seconds) and death (killed, its body left, then replaced)

Usage: python bench/familles/famille_map.py   (writes bench/familles/maps/FAM01.wad, build/FAM01_plan.png)
"""
import sys
from pathlib import Path
from dataclasses import replace
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
from udmf import MapBuilder, Cell  # noqa: E402

HALL = Cell(floor=0, ceil=176, ftex='RFF_SLAB', ctex='RFP_CEID', light=184, wall='RFP_PLN', color=0xFFFFFF, env=(30, 3))
MARK = replace(HALL, ftex='RFF_WOOD')
T_START, T_SPOT, T_PATROL, T_SIGNAL = 1, 9001, 9024, 30623
SIGNAL_TID = 999
VIEW, WALK, RUN, STRIKE, DUMMY, PAIN, DEATH = 9100, 9200, 9300, 9400, 9401, 9500, 9600
PP_WALK, PP_RUN = 9211, 9311

m = MapBuilder('FAM01')
m.box(0, 0, 1376, 1024, HALL)
m.thing(704, 64, T_START, angle=90)
m.thing(760, 40, T_SIGNAL, tid=SIGNAL_TID)
# the pads that choose the family (walked over): user_scene 1, 2, 3
for k, x in enumerate((96, 224, 352)):
    m.box(x, 32, x + 64, 64, MARK)
    m.trigger(x, 48, x + 64, 48, 130, (SIGNAL_TID,), repeat=True, fields={'user_scene': k + 1})
# the view mark of the rotations
m.box(688, 240, 720, 272, MARK)
m.thing(704, 256, T_SPOT, tid=VIEW)
# the walk (west)
m.thing(96, 208, T_SPOT, angle=90, tid=WALK)
m.thing(96, 208, T_PATROL, tid=PP_WALK, args=(PP_WALK + 1, 0))
m.thing(96, 720, T_PATROL, tid=PP_WALK + 1, args=(PP_WALK, 0))
# the obstacles (east), behind a railing
m.decor_line(1180, 16, 1180, 1008, 'RF2_RAMB', 0, blocking=True, yscale=4)
m.carve(1248, 208, 1280, 240)                                            # a pillar: 64 u to its west, 96 to its east
m.raise_block(1184, 416, 1376, 480, 24, 'RFF_WOOD', 'RFW_PANL')           # a step of 24, up and down
for (y, x0, x1) in ((544, 1232, 1328), (656, 1248, 1312), (768, 1264, 1312)):   # doors of 96, 64 and 48
    m.carve(1184, y, x0, y + 16)
    m.carve(x1, y, 1376, y + 16)
m.thing(1296, 112, T_SPOT, angle=90, tid=RUN)
for k, (x, y) in enumerate(((1328, 288), (1280, 448), (1280, 608), (1280, 720), (1288, 880))):
    m.thing(x, y, T_PATROL, tid=PP_RUN + k, args=(PP_RUN + k + 1 if k < 4 else 0, 0), z=0)
# the attack (north-east): a pen, the post against a wall
m.decor_line(620, 796, 1150, 796, 'RF2_RAMB', 0, blocking=True, yscale=4)
m.decor_line(620, 796, 620, 1020, 'RF2_RAMB', 0, blocking=True, yscale=4)
m.decor_line(1150, 796, 1150, 1020, 'RF2_RAMB', 0, blocking=True, yscale=4)
m.carve(1120, 848, 1136, 944)
m.thing(688, 896, T_SPOT, angle=0, tid=STRIKE)
m.thing(1088, 896, T_SPOT, angle=180, tid=DUMMY)
# pain and death (north-west)
m.thing(240, 896, T_SPOT, angle=270, tid=PAIN)
m.thing(432, 896, T_SPOT, angle=270, tid=DEATH)
m.exit_cells = set()


def main():
    text = m.build()
    (HERE / 'maps').mkdir(exist_ok=True)
    (HERE / 'maps' / 'FAM01.wad').write_bytes(m.wad(text))
    (HERE / 'build').mkdir(exist_ok=True)
    m.plan_png(HERE / 'build' / 'FAM01_plan.png', scale=0.5)
    print('FAM01 built:', m.stats)


if __name__ == '__main__':
    main()
