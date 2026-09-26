"""Recover editable project sources into this batch; never write outside it."""
from pathlib import Path
import hashlib
import json
import shutil

BATCH = Path(__file__).resolve().parents[1]
ROOT = BATCH.parents[2]
LEGACY = ROOT / 'legacy/import'

def digest(p):
    return hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()

def main():
    records = []
    def copy(rel, dst):
        src = LEGACY / rel
        dst = BATCH / 'source' / dst
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
        records.append({'original': src.relative_to(ROOT).as_posix(),
                        'copy': dst.relative_to(BATCH).as_posix(),
                        'sha256': digest(src)})
    snapshot = BATCH / 'evidence/protected_before.json'
    if not snapshot.exists():
        protected = {}
        for name in ('src', 'scripts', 'agent', 'campaign'):
            for p in sorted((ROOT / name).rglob('*')):
                if p.is_file():
                    protected[p.relative_to(ROOT).as_posix()] = digest(p)
        snapshot.write_text(json.dumps(protected, indent=2), encoding='utf-8')
    base = 'art/source/final_weapons'
    for p in sorted((LEGACY / base / 'fn_fal/layers').glob('*.png')):
        copy(p.relative_to(LEGACY), 'layers/' + p.name)
    for src, dest in [
        (base + '/fn_fal/fal_build.py', 'reference/fal_build_original.py.txt'),
        (base + '/_pipeline/rigcomp.py', 'reference/rigcomp_original.py.txt'),
        (base + '/fn_fal/rig.json', 'reference/rig_original.json'),
        ('art/source/fn_fal/fal_idle_v01.png', 'reference/fal_idle_v01.png'),
        ('art/source/fn_fal/README.md', 'reference/master_origin.md'),
        ('LICENSE.md', 'reference/LEGACY_LICENSE.md'),
        ('art/manifests/provenance.json', 'reference/legacy_provenance.json'),
        ('art/generated/final_weapons/fn_fal/_manifest.json', 'reference/legacy_frames.json'),
        ('art/generated/final_weapons/fn_fal/06_FAL_RELOAD_03_GRAB_MAG.png', 'reference/reload_before.png'),
    ]:
        copy(src, dest)
    original = (BATCH / 'source/reference/fal_build_original.py.txt').read_text(encoding='utf-8')
    # Only the native layer-composition and animation definitions are executable.
    # Master segmentation is archived as text; it has obsolete external write paths.
    native = original[original.index('def compose('):original.index('def render_frames():')]
    header = '''"""Native FAL composition and poses recovered from the project legacy."""
import numpy as np
import rigcomp as rc
PAD_L, PAD_T, PAD_R, PAD_B = 512, 256, 384, 512
W0, H0 = 1536, 1024
def P(x, y):
    return (x + PAD_L, y + PAD_T)
'''
    (BATCH / 'source/fal_native.py').write_text(header + native, encoding='utf-8')
    original = (BATCH / 'source/reference/rigcomp_original.py.txt').read_text(encoding='utf-8')
    basic = original[original.index('def load_rgba('):original.index('def polygon_mask(')]
    transforms = original[original.index('def affine_params('):original.index('def warp_layer(')]
    (BATCH / 'source/rigcomp.py').write_text(
        '"""Project native premultiplied-alpha compositor (Pillow/numpy only)."""\n'
        'import math\nimport numpy as np\nfrom PIL import Image\n' + basic + transforms,
        encoding='utf-8')
    (BATCH / 'source/provenance.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print('Recovered', len(records), 'source/reference files; protected baseline recorded.')

if __name__ == '__main__':
    main()
