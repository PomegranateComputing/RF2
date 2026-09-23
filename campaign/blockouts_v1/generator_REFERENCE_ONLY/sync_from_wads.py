#!/usr/bin/env python3
"""Adopt maps/*.wad edited in UDB as the current TEXTMAP sources; then repack.
Run deliberately after editor saves. It preserves any compiled nodes in WADs.
"""
from build_maps import ROOT,pack
from validate_pack import readwad
for i in range(1,24):
    code=f'RF{i:02d}';p=ROOT/'maps'/f'{code}.wad'
    lumps=readwad(p.read_bytes())
    (ROOT/'src'/code/'TEXTMAP').write_bytes(lumps['TEXTMAP'])
print(pack())
