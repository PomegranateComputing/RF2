#!/usr/bin/env python3
r"""Build the bench of the enemy families (outside the campaign): a module pk3 loaded over a frozen game build, its
launcher and its build record. The campaign's src/ is only read (the base is a copy of a built pk3); no accepted
launcher loads the module.

  dist/familles/base/RF2_BASE_<sha12>.pk3        the frozen base (a copy of --base, default dist/RF2_DEV.pk3)
  dist/familles/RF2_BANC_FAMILLES_<stamp>/RF2_BANC_FAMILLES.pk3, JOUER.cmd, BUILD_INFO.json

The module carries bench/familles/{lumps, zscript, sprites, maps}: map FAM01, the post RFBenchDummy, the bench
handler RFFamilyBench. Sprite names are checked against the base: a collision is refused.
A new family is put on the bench by loading its own module after this one and naming its class:
    set RF2_BANC_CLASSE=RFNouvelleFamille & JOUER.cmd -file chemin\du\module.pk3
Usage: python bench/familles/build_family_bench.py [--base dist/RF2_DEV.pk3] [--stamp 20261002_1500]
"""
import argparse, hashlib, json, shutil, subprocess, sys, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe'
IWAD = r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad'

LAUNCHER = r'''@echo off
setlocal
rem Red Flags 2 - BANC DES FAMILLES (hors campagne) : rotations, marche, obstacles, attaque, douleur, mort et corps.
rem Module {module} (sha256 {module_sha})
rem Base   {base} (sha256 {base_sha})
rem Famille au depart : RFOrderly, ou celle de la variable RF2_BANC_CLASSE ; en jeu, les trois dalles de bois au sud.
rem Configuration, sauvegardes et journaux propres au banc ; ni la partie normale ni ses sauvegardes ne sont touchees.
set "ROOT=%~dp0{up}"
set "ENGINE={engine}"
set "IWAD={iwad}"
set "BASE=%ROOT%{base}"
set "MODULE=%ROOT%{module}"
if not defined RF2_BANC_CLASSE set "RF2_BANC_CLASSE=RFOrderly"
if not exist "%BASE%" (
    echo Build de base absent : %BASE%
    exit /b 1
)
if not exist "%MODULE%" (
    echo Module du banc absent : %MODULE%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_banc_familles.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_banc_familles" mkdir "%ROOT%user\savegames_banc_familles"
if not exist "%ROOT%user\logs_banc_familles" mkdir "%ROOT%user\logs_banc_familles"
set "D=%DATE:/=-%"
set "D=%D: =_%"
set "T=%TIME: =0%"
set "T=%T::=-%"
set "T=%T:.=-%"
set "T=%T:,=-%"
set "LOG=%ROOT%user\logs_banc_familles\banc_%D%_%T%.log"
echo RF2 BANC DES FAMILLES (hors campagne) : {module} - famille %RF2_BANC_CLASSE%
echo Journal : %LOG%
"%ENGINE%" -iwad "%IWAD%" -file "%BASE%" "%MODULE%" -config "%CFG%" -savedir "%ROOT%user\savegames_banc_familles" -skill 2 -stdout +set rf_banc_classe %RF2_BANC_CLASSE% +map FAM01 %* > "%LOG%" 2>&1
exit /b %errorlevel%
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default=str(ROOT / 'dist' / 'RF2_DEV.pk3'))
    ap.add_argument('--stamp', default=time.strftime('%Y%m%d_%H%M'))
    ap.add_argument('--root-launcher', action='store_true', help='also write JOUER_RF2_BANC_FAMILLES.cmd at the root')
    a = ap.parse_args()
    base = Path(a.base).resolve()
    base_sha = sha(base)
    with zipfile.ZipFile(base) as z:
        base_sprites = {Path(n).name[:4].upper() for n in z.namelist() if n.lower().startswith('sprites/')}
    ours = {p.name[:4].upper() for p in (HERE / 'sprites').glob('*.png')}
    clash = sorted(ours & base_sprites)
    if clash:
        sys.exit(f'collision de noms de sprites avec la base : {clash}')
    out_dir = ROOT / 'dist' / 'familles' / f'RF2_BANC_FAMILLES_{a.stamp}'
    out_dir.mkdir(parents=True, exist_ok=True)
    base_dir = ROOT / 'dist' / 'familles' / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)
    base_copy = base_dir / f'RF2_BASE_{base_sha[:12]}.pk3'
    if not base_copy.exists():
        shutil.copy2(base, base_copy)
    module = out_dir / 'RF2_BANC_FAMILLES.pk3'
    files = []
    with zipfile.ZipFile(module, 'w', zipfile.ZIP_DEFLATED) as z:
        for lump in ('MAPINFO', 'CVARINFO', 'ZSCRIPT'):
            z.write(HERE / 'lumps' / lump, lump)
            files.append(lump)
        for src, dst in ((HERE / 'zscript', 'zscript/familles'), (HERE / 'sprites', 'sprites/familles')):
            for f in sorted(src.iterdir()):
                z.write(f, f'{dst}/{f.name}')
                files.append(f'{dst}/{f.name}')
        z.write(HERE / 'maps' / 'FAM01.wad', 'maps/FAM01.wad')
        files.append('maps/FAM01.wad')
    rel = lambda p: str(p.relative_to(ROOT)).replace('/', '\\')
    info = dict(created=time.strftime('%Y-%m-%d %H:%M'),
                commit=subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
                module=rel(module), module_sha256=sha(module), files=len(files), base=rel(base_copy),
                base_sha256=base_sha, base_from=str(base), engine=ENGINE, iwad=IWAD,
                note='Banc hors campagne : les familles d ennemis, une a la fois (rotations, marche, obstacles, attaque, '
                     'douleur, mort et corps).')
    (out_dir / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    fill = dict(module=info['module'], module_sha=info['module_sha256'], base=info['base'], base_sha=base_sha, engine=ENGINE, iwad=IWAD)
    (out_dir / 'JOUER.cmd').write_bytes(LAUNCHER.format(up='..\\..\\..\\', **fill).replace('\n', '\r\n').encode('ascii'))
    if a.root_launcher:
        (ROOT / 'JOUER_RF2_BANC_FAMILLES.cmd').write_bytes(LAUNCHER.format(up='', **fill).replace('\n', '\r\n').encode('ascii'))
    print('family bench:', info['module'], info['module_sha256'][:12], 'over', info['base'], f'({len(files)} files)')
    return out_dir


if __name__ == '__main__':
    main()
