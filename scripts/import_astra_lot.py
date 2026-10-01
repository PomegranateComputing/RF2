#!/usr/bin/env python3
"""Import one of Astra's campaign lots (schema 1 manifest) into src/, with an import record.

Each manifest entry names a delivered file (`file`, relative to the lot), its sha256, its destination
(`target_relpath`, relative to src/) and, when it replaces a file, the sha256 of the file it was made against
(`base_sha256`). The import refuses when a delivered file does not match its hash, or when a destination has changed
since Astra's base (someone else's newer work would be overwritten), unless --accept-base-drift names the reason.
The lot folder is only read. Weapon lots (rf2-arsenal-delivery/1) go to the bench builder, not here.

Record: docs/production/handoff/<record dir>/IMPORT_<batch>.json (files, hashes before/after, base check).
Usage: python scripts/import_astra_lot.py <lot folder> --record-dir SUITE-20260930 [--only PREFIX ...] [--dry-run]
"""
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lot')
    ap.add_argument('--record-dir', required=True, help='folder under docs/production/handoff/')
    ap.add_argument('--only', action='append', default=[], help='import only targets starting with this prefix')
    ap.add_argument('--accept-base-drift', metavar='REASON', help='import over destinations changed since the base')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    lot = Path(a.lot).resolve()
    manifest = json.loads((lot / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 1:
        print(f"schema {manifest.get('schema')!r} : lot d'armes ou inconnu, pas importe ici")
        return 2
    entries = [e for e in manifest['files'] if not a.only or any(e['target_relpath'].startswith(p) for p in a.only)]
    rows, refused = [], []
    for e in entries:
        src_file = lot / e['file']
        dest = SRC / e['target_relpath']
        if '..' in Path(e['target_relpath']).parts or Path(e['target_relpath']).is_absolute():
            refused.append((e['target_relpath'], 'destination hors de src/'))
            continue
        # Maps, code and the definition lumps at the root of src/ (TEXTURES, MAPINFO...) are Opus's: a lot proposes
        # them as text (TEXTURES.proposition.txt, patch/), never as a file to copy.
        if e['target_relpath'].startswith(('maps/', 'zscript/')) or '/' not in e['target_relpath']:
            refused.append((e['target_relpath'], 'carte, code ou definition : a reprendre a la main'))
            continue
        got = sha256(src_file) if src_file.is_file() else None
        if got is None or (e.get('sha256') and got != e['sha256']):
            refused.append((e['file'], f'fichier livre absent ou different du manifeste ({got})'))
            continue
        before = sha256(dest) if dest.is_file() else None
        base = e.get('base_sha256')
        if before == got:
            state = 'deja_importe'
        elif before is None:
            state = 'nouveau'
        elif base is None:
            state = 'remplace_sans_base'
        elif before == base:
            state = 'remplace_base_conforme'
        else:
            state = 'base_differente'
            if not a.accept_base_drift:
                refused.append((e['target_relpath'], f'la destination a change depuis la base ({before[:12]} != {base[:12]})'))
                continue
        rows.append(dict(target=f"src/{e['target_relpath']}", delivered=e['file'], sha256=got, before=before,
                         base_sha256=base, state=state, kind=e.get('kind'), id=e.get('id') or e.get('asset_id')))
    if refused:
        print('Refus :')
        for r in refused:
            print('  ', *r)
        return 1
    counts = {}
    for r in rows:
        counts[r['state']] = counts.get(r['state'], 0) + 1
    print(f"{manifest.get('batch_id', lot.name)} : {len(rows)} fichiers {counts}")
    if a.dry_run:
        return 0
    for r in rows:
        dest = ROOT / r['target']
        dest.parent.mkdir(parents=True, exist_ok=True)
        if r['state'] != 'deja_importe':
            shutil.copyfile(lot / r['delivered'], dest)
        assert sha256(dest) == r['sha256'], dest
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    record = dict(batch=manifest.get('batch_id', lot.name),
                  lot=(lot.relative_to(ROOT) if lot.is_relative_to(ROOT) else lot).as_posix(),   # Codex's lots are outside
                  manifest_sha256=sha256(lot / 'manifest.json'), status=manifest.get('status'),
                  imported=time.strftime('%Y-%m-%d %H:%M'), by='Opus (integration)', head_before=head,
                  base_drift_reason=a.accept_base_drift, counts=counts, files=rows,
                  note='Import into the production tree only: engine review, listening and owner verdict are separate.')
    out = ROOT / 'docs' / 'production' / 'handoff' / a.record_dir
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"IMPORT_{record['batch']}.json"
    path.write_bytes((json.dumps(record, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    print(f'record: {path.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
