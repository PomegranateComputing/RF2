"""ARSENAL: the firing range of the arsenal test bench (not a campaign map).

A firing room (the player starts on the line, facing the bright lane) opening on two parallel lanes 960 units long:
a bright one (light 224) and a dark one (light 56), with a paper target at 128, 256, 512 and 896 units in each, on a
paved stripe that marks the distance. The back wall of the firing room serves as the close wall (flash and impacts at
arm's length). Textures are the game's own RF01 surfaces, so the weapons are seen against familiar materials.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mapkit'))
from udmf import MapBuilder, Cell  # noqa: E402

TARGET = 30950
DISTANCES = (128, 256, 512, 896)
LANES = ((128, 0, 'claire'), (448, 1, 'sombre'))      # (lane centre y, dark flag, name)


def build():
    m = MapBuilder('ARSENAL')
    room = Cell(floor=0, ceil=160, ftex='RFF_CONC', ctex='RFP_CEIL', light=160, wall='RFP_PLN')
    m.box(-192, -64, 64, 640, room)
    bright = Cell(floor=0, ceil=192, ftex='RFF_CONC', ctex='RFP_CEIL', light=224, wall='RFP_PLN')
    dark = Cell(floor=0, ceil=192, ftex='RFF_CONC', ctex='RFP_CEIL', light=56, wall='RFP_DRK')
    m.box(64, 0, 1024, 256, bright)
    m.box(64, 320, 1024, 576, dark)
    for d in DISTANCES:                                   # distance stripes (32 u) centred under the targets
        m.modify(d - 16, 0, d + 16, 256, ftex='RFF_PAVE')
        m.modify(d - 16, 320, d + 16, 576, ftex='RFF_PAVE')
    m.modify(-16, -64, 0, 640, ftex='RFF_PAVE')          # the firing line; distances are counted from it
    m.thing(-8, 128, 1, angle=0)
    # Contact tools (saw, crowbar): a 16-unit pillar with a target just behind it, and a control target at the same
    # distance in the open; the player stands at y = 490 facing north. Nothing may be hurt through the pillar.
    m.carve(-128, 528, -112, 544)
    m.thing(-120, 560, TARGET, angle=270, args=(70, 0))
    m.thing(-40, 560, TARGET, angle=270, args=(71, 0))
    for y, dark_flag, _ in LANES:
        for d in DISTANCES:
            m.thing(d, y, TARGET, angle=180, args=(d, dark_flag))
    return m


def wad_bytes():
    m = build()
    return m.wad(m.build())


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('ARSENAL.wad')
    out.write_bytes(wad_bytes())
    print(out)


# Discovery rooms (Viktor's lines): BANCDEC1 holds a Rapid, a second Rapid (duplicate) and an MR73 along a straight
# walk; BANCDEC2, reached by the normal exit, holds one more of each (duplicates after a map change).
RAPID_PICKUP, MR73_PICKUP = 30951, 30952


def build_discovery(name, second):
    m = MapBuilder(name)
    room = Cell(floor=0, ceil=160, ftex='RFF_CONC', ctex='RFP_CEIL', light=190, wall='RFP_PLN')
    m.box(-64, -128, 640, 128, room)
    m.thing(-32, 0, 1, angle=0)
    if not second:
        m.thing(128, 0, RAPID_PICKUP)
        m.thing(256, 0, RAPID_PICKUP)
        m.thing(448, 0, MR73_PICKUP)
    else:
        m.thing(128, 0, RAPID_PICKUP)
        m.thing(256, 0, MR73_PICKUP)
    return m


def discovery_wads():
    out = {}
    for name, second in (('BANCDEC1', False), ('BANCDEC2', True)):
        m = build_discovery(name, second)
        out[name] = m.wad(m.build())
    return out
