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
