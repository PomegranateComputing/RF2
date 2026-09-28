#!/usr/bin/env python3
"""Import of an Astra batch made of new resources (manifest.json: 'files' and optional 'model_files', each with
'file', 'target_relpath', 'sha256'). Checks before anything is written: every delivered file has its announced hash
(and, for images, its announced size); a target that already exists in src/ is refused unless its hash is the
'base_sha256' the manifest names (then it is a replacement Astra worked from). Then the files are copied one by one,
and <archive>/IMPORT_RECORD.json lists every target with its hashes before and after. Code proposals (*.txt) are
never imported: Opus writes the definitions.

Usage: python scripts/production/import_astra_new_files.py <batch dir> <archive dir under art/>
"""
import hashlib, json, shutil, sys, time
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BATCH, ART = Path(sys.argv[1]), ROOT / sys.argv[2]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


man = json.load(open(BATCH / 'manifest.json', encoding='utf-8'))
entries = list(man.get('files', [])) + list(man.get('model_files', []))
problems, record = [], []
for f in entries:
    src, tgt = BATCH / f['file'], ROOT / 'src' / f['target_relpath']
    if sha(src) != f['sha256']:
        problems.append(('empreinte livree differente', f['file']))
    if 'width' in f and src.suffix.lower() == '.png' and list(Image.open(src).size) != [f['width'], f['height']]:
        problems.append(('dimensions', f['file']))
    before = sha(tgt) if tgt.exists() else None
    if before is not None and before != f.get('base_sha256'):
        problems.append(('cible existante sans base correspondante', f['target_relpath']))
    record.append(dict(target=f['target_relpath'], source=f['file'], base_sha256=before, new_sha256=f['sha256']))
if problems:
    for p in problems:
        print('REFUS', *p)
    sys.exit(1)
for r in record:
    t = ROOT / 'src' / r['target']
    t.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BATCH / r['source'], t)
ART.mkdir(parents=True, exist_ok=True)
json.dump(dict(batch=man.get('batch_id'), batch_path=str(BATCH), imported=time.strftime('%Y-%m-%d %H:%M'),
               manifest_sha256=sha(BATCH / 'manifest.json'), files=record),
          open(ART / 'IMPORT_RECORD.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
new = sum(r['base_sha256'] is None for r in record)
print(f'{len(record)} fichiers importes ({new} nouveaux, {len(record) - new} remplacements)')
