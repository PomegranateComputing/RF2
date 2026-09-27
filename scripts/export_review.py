#!/usr/bin/env python3
"""Frozen review build for the owner (RF2-ART-01), next to a baseline build for comparison.

Builds dist/RF2_DEV.pk3 from src/ (scripts/build.ps1), copies it to
dist/review/RF2_ART_REVIEW_<date>_<time>/RF2_ART_REVIEW.pk3 with BUILD_INFO.json, and points
dist/review/LATEST.txt at it: JOUER_RF2_ART_REVIEW.cmd launches that file and never rebuilds.
The baseline (commit 6e1a31b, before the art pass) is built once from git into
dist/review/RF2_BASELINE_6e1a31b.pk3: same launcher arguments, for before/after and rollback.

Usage: python scripts/export_review.py [--label "texte"]
"""
import argparse, hashlib, io, json, shutil, subprocess, sys, tarfile, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'dist' / 'review'
BASE = '6e1a31b'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def baseline():
    out = REVIEW / f'RF2_BASELINE_{BASE}.pk3'
    if out.exists():
        return out
    # Same layout as build.ps1: the contents of src/ at the pk3 root.
    data = subprocess.run(['git', 'archive', '--format=tar', BASE, 'src'], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for m in tar.getmembers():
            if m.isfile():
                z.writestr(m.name[len('src/'):], tar.extractfile(m).read())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--label', default='')
    a = ap.parse_args()
    # 27/09/2026: the build this script last exported is the one the owner accepted, and
    # JOUER_RF2_ART_REVIEW.cmd follows LATEST.txt. Re-running it would re-point the accepted
    # launcher at a new build: candidates go through scripts/export_candidate.py instead.
    latest = REVIEW / 'LATEST.txt'
    if latest.exists():
        print('Refus : dist\\review\\LATEST.txt designe le build RF01 accepte (reference figee).\n'
              'Nouvelles candidates : python scripts/export_candidate.py --lot <ID> (lanceur distinct).')
        return 1
    REVIEW.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pwsh', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'scripts' / 'build.ps1')], check=True)
    stamp = time.strftime('%Y%m%d_%H%M')
    folder = REVIEW / f'RF2_ART_REVIEW_{stamp}'
    folder.mkdir(exist_ok=True)
    pk3 = folder / 'RF2_ART_REVIEW.pk3'
    shutil.copy2(ROOT / 'dist' / 'RF2_DEV.pk3', pk3)
    base = baseline()
    info = dict(label=a.label, created=time.strftime('%Y-%m-%d %H:%M'), commit=git('rev-parse', 'HEAD'),
                branch=git('branch', '--show-current'), tree_clean=git('status', '--porcelain') == '',
                pk3=str(pk3.relative_to(ROOT)), sha256=sha256(pk3),
                baseline=dict(commit=BASE, pk3=str(base.relative_to(ROOT)), sha256=sha256(base)),
                engine='C:\\PROJECTS\\TOOLS\\UZDoom-5.0.1\\uzdoom.exe', iwad='C:\\PROJECTS\\TOOLS\\Freedoom-0.13.0\\freedoom2.wad',
                launcher='JOUER_RF2_ART_REVIEW.cmd (config user\\uzdoom_art_review.ini, saves user\\savegames_art_review)')
    (folder / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding='utf-8')
    (REVIEW / 'LATEST.txt').write_text(str(pk3.relative_to(ROOT)).replace('/', '\\'), encoding='ascii')
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
