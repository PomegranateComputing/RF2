#!/usr/bin/env python3
"""Frozen candidate build of a production lot, with its own launcher (RF2 campaign production).

The RF01 build accepted by the owner on 27/09/2026 stays where it is (dist/review/RF2_ART_REVIEW_20260926_1451,
JOUER_RF2_ART_REVIEW.cmd, LATEST.txt read-only). Every later lot gets a distinct build and launcher:

  dist/candidates/RF2_<LOT>_<date>_<time>/RF2_<LOT>.pk3   the build, never rebuilt in place
  dist/candidates/RF2_<LOT>_<date>_<time>/BUILD_INFO.json commit, hashes, engine, reference build
  dist/candidates/RF2_<LOT>_<date>_<time>/JOUER.cmd       launches exactly this build
  JOUER_RF2_<LOT>.cmd                                     launches the newest build of the lot

Each lot has its own configuration and saves (user/uzdoom_<lot>.ini, a copy of user/uzdoom.ini on the first
launch; user/savegames_<lot>): the owner's configuration and the accepted review saves are never touched.
The launchers start on the title screen; extra arguments pass through (for example: +map RF02).

Usage: python scripts/export_candidate.py --lot UI-01 --label "texte" [--allow-dirty]
"""
import unicodedata
import argparse, hashlib, json, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / 'dist' / 'candidates'
ENGINE = Path(r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe')
IWAD = Path(r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad')
ACCEPTED = dict(tag='rf01-owner-accepted-20260927', commit='5b53d9eaaaf088f49ae98f667fc1d575779dc74e',
                pk3='dist\\review\\RF2_ART_REVIEW_20260926_1451\\RF2_ART_REVIEW.pk3',
                sha256='04bdd0ae918761370c7620318f6e2add8bd1e1ac0acf88d55741c8be1883544f',
                launcher='JOUER_RF2_ART_REVIEW.cmd')

LAUNCHER = r'''@echo off
setlocal
rem Red Flags 2 - candidate {lot} ({label_ascii}).
rem Build fige : {pk3_rel}  (sha256 {sha})
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT={root_expr}"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%{pk3_rel}"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_{slug}.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_{slug}" mkdir "%ROOT%user\savegames_{slug}"
echo RF2 candidate {lot} : {pk3_rel}
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_{slug}" %*
exit /b %errorlevel%
'''


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lot', required=True, help='lot id, e.g. UI-01, MAP-02, ART-02')
    ap.add_argument('--label', default='')
    ap.add_argument('--allow-dirty', action='store_true', help='export even with uncommitted changes (recorded)')
    a = ap.parse_args()
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9-]{1,24}', a.lot):
        print('lot: capitals, digits and dashes only')
        return 2
    dirty = git('status', '--porcelain', '--untracked-files=no') != ''
    if dirty and not a.allow_dirty:
        print('Refus : modifications non committees (commit, ou --allow-dirty pour une candidate de travail).')
        return 1
    subprocess.run(['pwsh', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'scripts' / 'build.ps1')], check=True)
    stamp = time.strftime('%Y%m%d_%H%M')
    folder = CANDIDATES / f'RF2_{a.lot}_{stamp}'
    folder.mkdir(parents=True, exist_ok=False)
    pk3 = folder / f'RF2_{a.lot}.pk3'
    shutil.copy2(ROOT / 'dist' / 'RF2_DEV.pk3', pk3)
    pk3_rel = str(pk3.relative_to(ROOT)).replace('/', '\\')
    slug = a.lot.lower().replace('-', '')
    info = dict(lot=a.lot, label=a.label, created=time.strftime('%Y-%m-%d %H:%M'), commit=git('rev-parse', 'HEAD'),
                branch=git('branch', '--show-current'), tree_clean=not dirty, pk3=pk3_rel, sha256=sha256(pk3),
                status='RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED only once its evidence exists; otherwise INTEGRATED',
                engine=str(ENGINE), engine_sha256=sha256(ENGINE), iwad=str(IWAD), iwad_sha256=sha256(IWAD),
                reference_accepted=ACCEPTED,
                launcher=f'JOUER_RF2_{a.lot}.cmd (newest of the lot) / {folder.name}\\JOUER.cmd (this build); '
                         f'config user\\uzdoom_{slug}.ini, saves user\\savegames_{slug}')
    (folder / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding='utf-8')
    label_ascii = unicodedata.normalize('NFKD', a.label).encode('ascii', 'ignore').decode('ascii')   # cmd comments: plain ASCII
    common = dict(lot=a.lot, label_ascii=label_ascii, pk3_rel=pk3_rel, sha=info['sha256'], slug=slug)
    (ROOT / f'JOUER_RF2_{a.lot}.cmd').write_text(LAUNCHER.format(root_expr='%~dp0', **common).replace('\n', '\r\n'), encoding='ascii')
    (folder / 'JOUER.cmd').write_text(LAUNCHER.format(root_expr='%~dp0..\\..\\..\\', **common).replace('\n', '\r\n'), encoding='ascii')
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
