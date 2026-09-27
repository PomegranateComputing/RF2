#!/usr/bin/env python3
"""Manifest of the runtime files an art lot may replace, with their base hashes and consumers.

Written for the Opus -> Astra handoff (docs/production/handoff/<LOT>/BASE_MANIFEST.json): every sprite of
the families in scope with size, grAb offset, SHA-256 at the base commit, and the states that show it
(label, duration in tics) read from the ZScript source; the terminal models and their MODELDEF frames.

Usage: python scripts/production/handoff_manifest.py --lot RF2-ART-02 --families ORDY BRCD PREG PRGS
"""
import argparse, hashlib, json, re, struct, subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def png_info(data):
    i, w, h, grab = 8, None, None, None
    while i < len(data):
        n, t = struct.unpack('>I4s', data[i:i + 8])
        if t == b'IHDR':
            w, h = struct.unpack('>II', data[i + 8:i + 16])
        elif t == b'grAb':
            grab = list(struct.unpack('>ii', data[i + 8:i + 16]))
        i += 12 + n
    return w, h, grab


def state_uses(zs_text, families):
    """(sprite, frame) -> [(class, label, tics)] from 'SPRT F 10 ...' lines of States blocks."""
    uses = defaultdict(list)
    cls, label = None, None
    for line in zs_text.splitlines():
        m = re.match(r'\s*class\s+(\w+)', line)
        if m:
            cls = m.group(1)
        m = re.match(r'\s*(\w+):\s*$', line)
        if m:
            label = m.group(1)
        m = re.match(r'\s*([A-Z0-9]{4})\s+([A-Z\[\]\\]+)\s+(-?\d+)', line)
        if m and m.group(1) in families:
            for f in m.group(2):
                uses[(m.group(1), f)].append(dict(actor=cls, state=label, tics=int(m.group(3))))
    return uses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lot', required=True)
    ap.add_argument('--families', nargs='+', required=True)
    ap.add_argument('--base', default='HEAD')
    a = ap.parse_args()
    base = subprocess.run(['git', 'rev-parse', a.base], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    zs = (ROOT / 'src/zscript/rf/enemies.zs').read_text(encoding='utf-8')
    uses = state_uses(zs, set(a.families))
    modeldef = (ROOT / 'src/MODELDEF').read_text(encoding='utf-8')
    files = []
    for fam in a.families:
        for p in sorted((ROOT / 'src/sprites').rglob(f'{fam}*.png')):
            data = p.read_bytes()
            w, h, grab = png_info(data)
            name = p.stem
            frame, rot = name[4], name[5:]
            files.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(data).hexdigest(), family=fam,
                              frame=frame, rotation=rot, width=w, height=h, grAb=grab,
                              states=uses.get((fam, frame), []),
                              terminal_model=bool(re.search(rf'FrameIndex\s+{fam}\s+{frame}\s', modeldef))))
    models = []
    for p in sorted((ROOT / 'src/models/rf2_art_01').glob('*')):
        models.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    out = dict(lot=a.lot, base_commit=base, generated_by='scripts/production/handoff_manifest.py',
               families=a.families, sprite_count=len(files), sprites=files, terminal_models=models)
    target = ROOT / 'docs/production/handoff' / a.lot / 'BASE_MANIFEST.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
    print(target, len(files), 'sprites', len(models), 'model files')


if __name__ == '__main__':
    main()
