#!/usr/bin/env python3
"""Check, then import, Codex's RF2-ART-01 delivery into the active tree (dry run by default).

Reads C:\\PROJECTS\\RF2_ART_HANDOFF_20260925\\CODEX_LIVRAISON\\MANIFEST.json and files/ (see the handoff
contract, section 6). For every delivered file:
  - its SHA-256 must match the manifest;
  - its target must be inside Codex's scope (enemy sprites, weapon graphics, sounds, new FX
    sprites, art sources); maps and map sources are always refused;
  - the current tree file is compared with the base 6e1a31b (BASE_6e1a31b.sha256): unchanged
    since the base -> plain copy; changed since the base -> listed as a merge to do by hand.
Shared files (code, definitions) arrive as a patch in patch/; they are listed, never applied here.

Usage: python scripts/import_codex_delivery.py [--apply] [--delivery <folder>]
Writes build/dev/import_codex_report.json.
"""
import argparse, hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = Path(r'C:\PROJECTS\RF2_ART_HANDOFF_20260925')
OWNED = ('src/sprites/enemies/', 'src/sprites/fx/', 'src/sprites/items/', 'src/graphics/weapons/', 'src/sounds/',
         'src/graphics/fx/', 'art/rf2_art_01/')
REFUSED = ('src/maps/', 'scripts/mapkit/', 'campaign/')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def entries(manifest):
    items = manifest.get('files', manifest) if isinstance(manifest, dict) else manifest
    for it in items:
        target = it.get('target') or it.get('path') or it.get('chemin_cible') or it.get('chemin')
        yield target.replace('\\', '/').lstrip('/'), it.get('sha256'), it


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--delivery', default=str(HANDOFF / 'CODEX_LIVRAISON'))
    ap.add_argument('--apply', action='store_true', help='copy the checked files (never the shared patch)')
    a = ap.parse_args()
    delivery = Path(a.delivery)
    manifest_path = delivery / 'MANIFEST.json'
    if not manifest_path.exists():
        print(f'no delivery: {manifest_path} is missing')
        return 2
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    base = {}
    for line in (HANDOFF / 'BASE_6e1a31b.sha256').read_text(encoding='utf-8').splitlines():
        h, f = line.split('  ', 1)
        base[f] = h
    report = dict(delivery=str(delivery), copied=[], new=[], replace=[], merge_by_hand=[], refused=[], bad_hash=[], missing=[])
    for target, digest, item in entries(manifest):
        src = delivery / 'files' / target
        if not src.exists():
            report['missing'].append(target)
            continue
        if digest and sha256(src) != digest:
            report['bad_hash'].append(target)
            continue
        if target.startswith(REFUSED) or not target.startswith(OWNED):
            report['refused'].append(target)
            continue
        dst = ROOT / target
        if not dst.exists():
            report['new'].append(target)
        elif target in base and sha256(dst) != base[target]:
            report['merge_by_hand'].append(target)
            continue
        else:
            report['replace'].append(target)
        if a.apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            report['copied'].append(target)
    patches = sorted(p.name for p in (delivery / 'patch').glob('*')) if (delivery / 'patch').exists() else []
    report['shared_patch_files'] = patches
    out = ROOT / 'build' / 'dev' / 'import_codex_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    for k in ('new', 'replace', 'merge_by_hand', 'refused', 'bad_hash', 'missing', 'copied'):
        print(f'{k}: {len(report[k])}')
    print(f'shared patch: {patches}')
    print(f'report: {out}')
    return 1 if report['bad_hash'] or report['refused'] or report['missing'] else 0


if __name__ == '__main__':
    sys.exit(main())
