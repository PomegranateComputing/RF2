#!/usr/bin/env python3
"""Import of the Astra batch RF2_MAP_02 (27/09) in its high-definition presentation, the variant Astra recommends:
six textures at their native definition (facades RF2_FAC1/2/3/FACU, TSF window RF2_TSFS, Amiga RF2_AMIG) and five
sprites on a 4x canvas (bucket, satchel, radio off/on, field telephone), imported together with the scale patch
that keeps their size in the world (src/TEXTURES.rf02, src/zscript/rf/paris.zs). Nothing else of the batch is
imported: the 3D masters, the audio proposals and the review builds stay in Astra's worktree.

Checks before anything is written: the batch manifests are read; every target in the tree still has the base hash
Astra worked from (manifest.json base_sha256); every delivered image has its announced hash and size; the patch
applies (git apply --check); a patched file whose hash differs from its base (patch_bases.json) is accepted only
when the patch applies, and the difference is recorded (RF02-A changed two unrelated entries of TEXTURES.rf02 before
this import). Then the images are
copied one by one, the patch is applied, and art/rf2_map_02_astra/IMPORT_RECORD.json lists every file with its
hashes before and after. Refuses to run twice (the bases would no longer match).

Usage: python scripts/production/import_astra_rf2_map_02.py [batch dir]
"""
import hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\PROJECTS\RF2_UZDOOM_ASTRA_20260927\incoming\astra\RF2_MAP_02')
ART = ROOT / 'art' / 'rf2_map_02_astra'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


compat = json.load(open(BATCH / 'manifest.json', encoding='utf-8'))
hd = json.load(open(BATCH / 'presentation_proposal' / 'manifest.json', encoding='utf-8'))
bases = {f['target_relpath']: f['base_sha256'] for f in compat['files']}
patch = BATCH / 'presentation_proposal' / 'presentation.diff'
patch_bases = json.load(open(BATCH / 'presentation_proposal' / 'patch_bases.json', encoding='utf-8'))
problems, record = [], []
for f in hd['files']:
    src, tgt = BATCH / f['file'], ROOT / 'src' / f['target_relpath']
    if f['target_relpath'] not in bases:
        problems.append(('cible hors du manifeste de base', f['target_relpath']))
        continue
    before = sha(tgt)
    if before != bases[f['target_relpath']]:
        problems.append(('base differente', f['target_relpath'], before))
    if sha(src) != f['sha256']:
        problems.append(('empreinte livree differente', f['file']))
    w, h = Image.open(src).size
    if (w, h) != (f['width'], f['height']):
        problems.append(('dimensions', f['file'], (w, h)))
    record.append(dict(target=f['target_relpath'], source=f['file'], base_sha256=before, new_sha256=f['sha256'],
                       size=[w, h], grAb=f.get('grAb')))
base_notes = {}
for pb in patch_bases:
    cur = sha(ROOT / pb['file'])
    if cur != pb['base_sha256']:
        base_notes[pb['file']] = cur
chk = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=ROOT, capture_output=True, text=True)
if chk.returncode:
    problems.append(('git apply --check', chk.stderr.strip()))
if problems:
    for p in problems:
        print('REFUS', *p)
    sys.exit(1)

for r in record:
    shutil.copyfile(BATCH / r['source'], ROOT / 'src' / r['target'])
subprocess.run(['git', 'apply', str(patch)], cwd=ROOT, check=True)
patched = []
for pb in patch_bases:
    cur = sha(ROOT / pb['file'])
    patched.append(dict(file=pb['file'], astra_base_sha256=pb['base_sha256'],
                        tree_base_sha256=base_notes.get(pb['file'], pb['base_sha256']), sha256=cur,
                        matches_astra=cur == pb['patched_sha256']))
ART.mkdir(parents=True, exist_ok=True)
json.dump(dict(batch='RF2_MAP_02', batch_path=str(BATCH), variant='presentation HD (presentation_proposal)',
               imported=time.strftime('%Y-%m-%d %H:%M'), manifest_sha256=sha(BATCH / 'manifest.json'),
               presentation_manifest_sha256=sha(BATCH / 'presentation_proposal' / 'manifest.json'),
               patch_sha256=sha(patch), files=record, patched=patched,
               not_imported=['source/models (3D masters: pram, bucket, satchel, radios, phone, suitcase, mattress, '
                             'Amiga, tram, track) - RF02-B', 'audio_proposal (19 WAV, never heard by Astra) - COMBAT-02',
                             'runtime/ (compatibility variant at the historical sizes, superseded by the HD one)',
                             'review/ and delivery/ (review builds and archive)']),
          open(ART / 'IMPORT_RECORD.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for r in record:
    print('importe', r['target'], r['size'])
for p in patched:
    print('patche', p['file'], 'identique au resultat d\'Astra' if p['matches_astra'] else
          ('base du tree differente de celle d\'Astra, patch applique' if p['file'] in base_notes
           else 'DIFFERENT du resultat annonce'))
