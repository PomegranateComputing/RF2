#!/usr/bin/env python3
"""Reconstruct, from Git alone, the manifest of the RF2-ART-01 import (commit 43ce8e1, parent 844b50f).

The original Codex MANIFEST.json lived in C:\\PROJECTS\\RF2_ART_HANDOFF_20260925, which disappeared. This lists what
Git shows the import did: path, add/replace, SHA-256 of the imported blob and of the replaced one, the route it came
by (importer copy, model installer, hand-merged shared patch), its runtime consumer, and whether it changed again up
to 5b53d9e. It is a dated reconstruction, not the original manifest.

Usage: python scripts/production/reconstruct_import_manifest.py
Writes docs/production/recovery/RF2_ART_01_IMPORT_43ce8e1_RECONSTRUCTION.json
"""
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMP, PAR, HEAD = '43ce8e1', '844b50f', '5b53d9e'
REPORT = ROOT / 'docs/production/recovery/import_codex_report_20260926_1349.json'


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, check=True).stdout


def full(rev):
    return git('rev-parse', rev).decode().strip()


def consumer(p):
    if p.startswith('src/sprites/enemies/'):
        return 'enemy sprites ' + p.split('/')[-1][:4]
    if p.startswith('src/graphics/weapons/browning'):
        return 'RFBrowning (BHPG, TEXTURES.weapons)'
    if p.startswith('src/graphics/weapons/fal'):
        return 'RFFAL (RFLV, TEXTURES.weapons)'
    if p.startswith('src/sounds/'):
        return 'SNDINFO route'
    if p.startswith('src/models/'):
        return 'MODELDEF terminal frames'
    if p.startswith('src/sprites/fx/'):
        return 'RFArtBlood (RFBX)'
    if p.startswith('art/'):
        return 'source / credit (not in the pk3)'
    return 'shared runtime definition (patch merged by Opus)'


def main():
    copied = set(json.loads(REPORT.read_text(encoding='utf-8'))['copied'])
    later = set(git('diff', '--name-only', IMP, HEAD).decode().split())
    rows = []
    for line in git('diff', '--name-status', PAR, IMP).decode().splitlines():
        st, path = line.split('\t')[0], line.split('\t')[-1]
        new = git('show', f'{IMP}:{path}')
        old = git('show', f'{PAR}:{path}') if st == 'M' else None
        via = ('import_codex_delivery.py (hash-checked copy)' if path in copied else
               'install_models.py' if path.startswith('src/models/') else 'patch/production.patch merged by hand')
        rows.append(dict(path=path, action={'A': 'add', 'M': 'replace'}.get(st, st), sha256=hashlib.sha256(new).hexdigest(),
                         base_sha256=hashlib.sha256(old).hexdigest() if old is not None else None, via=via,
                         consumer=consumer(path), changed_after_import_until_5b53d9e=path in later))
    out = dict(title='RF2-ART-01 import reconstructed from Git (not the original Codex MANIFEST.json)',
               reconstructed='2026-09-27 by Opus 5.5 from git objects (scripts/production/reconstruct_import_manifest.py)',
               import_commit=full(IMP), parent=full(PAR), later_head=full(HEAD),
               original_delivery='C:/PROJECTS/RF2_ART_HANDOFF_20260925/CODEX_LIVRAISON (external folder, missing on 2026-09-27)',
               import_report_copy=str(REPORT.relative_to(ROOT).as_posix()),
               counts=dict(total=len(rows), added=sum(r['action'] == 'add' for r in rows),
                           replaced=sum(r['action'] == 'replace' for r in rows),
                           via_importer=sum(r['via'].startswith('import') for r in rows),
                           via_models=sum(r['via'] == 'install_models.py' for r in rows),
                           via_patch=sum(r['via'].startswith('patch') for r in rows),
                           changed_later=sum(r['changed_after_import_until_5b53d9e'] for r in rows)),
               files=rows)
    target = ROOT / 'docs/production/recovery/RF2_ART_01_IMPORT_43ce8e1_RECONSTRUCTION.json'
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
    print(target, out['counts'])


if __name__ == '__main__':
    main()
