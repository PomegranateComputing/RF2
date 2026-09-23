#!/usr/bin/env python3
"""Repackage edited TEXTMAPs. Never regenerates authored geometry."""
from pathlib import Path
import sys
from build_maps import ROOT,wad,pack
for i in range(1,24):
    code=f'RF{i:02d}';source=ROOT/'src'/code/'TEXTMAP'
    if not source.exists():raise SystemExit(f'Missing canonical source: {source}')
    (ROOT/'maps'/f'{code}.wad').write_bytes(wad(code,source.read_text(encoding='utf-8')))
print(pack())
