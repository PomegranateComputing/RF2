#!/usr/bin/env python3
"""Build the boss bench (outside the campaign): a module pk3 loaded over a frozen game build, its launcher and its
build record. The campaign's src/ is only read (the base is a copy of a built pk3); no accepted launcher loads it.

  dist/boss/base/RF2_BASE_<sha12>.pk3        the frozen base (a copy of --base, default dist/RF2_DEV.pk3)
  dist/boss/RF2_BOSS_ESSAI_<stamp>/RF2_BOSS_ESSAI.pk3, JOUER.cmd, BUILD_INFO.json

The module carries bench/boss/{lumps, zscript, sprites, sounds, maps}: map BOSS01, the actor RFBossSurveillant, the
bench handler RFBossBench. Sprite names are checked against the base: a collision is refused.
Usage: python bench/boss/build_boss_bench.py [--base dist/RF2_DEV.pk3] [--stamp 20261001_1500]
"""
import argparse, hashlib, json, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe'
IWAD = r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad'

LAUNCHER = r'''@echo off
setlocal
rem Red Flags 2 - BANC DU BOSS (hors campagne) : le surveillant-chef, prototype (adaptation declaree).
rem Module {module} (sha256 {module_sha})
rem Base   {base} (sha256 {base_sha})
rem Configuration, sauvegardes et journaux propres au banc ; ni la partie normale ni ses sauvegardes ne sont touchees.
set "ROOT=%~dp0..\..\..\"
set "ENGINE={engine}"
set "IWAD={iwad}"
set "BASE=%ROOT%{base}"
set "MODULE=%ROOT%{module}"
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
set "CFG=%ROOT%user\uzdoom_boss_essai.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_boss_essai" mkdir "%ROOT%user\savegames_boss_essai"
if not exist "%ROOT%user\logs_boss_essai" mkdir "%ROOT%user\logs_boss_essai"
set "D=%DATE:/=-%"
set "D=%D: =_%"
set "T=%TIME: =0%"
set "T=%T::=-%"
set "T=%T:.=-%"
set "T=%T:,=-%"
set "LOG=%ROOT%user\logs_boss_essai\essai_%D%_%T%.log"
echo RF2 BANC DU BOSS (hors campagne) : {module}
echo Journal : %LOG%
"%ENGINE%" -iwad "%IWAD%" -file "%BASE%" "%MODULE%" -config "%CFG%" -savedir "%ROOT%user\savegames_boss_essai" -skill 2 -stdout +map BOSS01 %* > "%LOG%" 2>&1
exit /b %errorlevel%
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default=str(ROOT / 'dist' / 'RF2_DEV.pk3'))
    ap.add_argument('--stamp', default=time.strftime('%Y%m%d_%H%M'))
    a = ap.parse_args()
    base = Path(a.base).resolve()
    base_sha = sha(base)
    # sprite names of the module must not exist in the base
    with zipfile.ZipFile(base) as z:
        base_sprites = {Path(n).name[:4].upper() for n in z.namelist() if n.lower().startswith('sprites/')}
    ours = {p.name[:4].upper() for p in (HERE / 'sprites').glob('*.png')}
    clash = sorted(ours & base_sprites)
    if clash:
        sys.exit(f'collision de noms de sprites avec la base : {clash}')
    out_dir = ROOT / 'dist' / 'boss' / f'RF2_BOSS_ESSAI_{a.stamp}'
    out_dir.mkdir(parents=True, exist_ok=True)
    base_dir = ROOT / 'dist' / 'boss' / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)
    base_copy = base_dir / f'RF2_BASE_{base_sha[:12]}.pk3'
    if not base_copy.exists():
        shutil.copy2(base, base_copy)
    module = out_dir / 'RF2_BOSS_ESSAI.pk3'
    files = []
    with zipfile.ZipFile(module, 'w', zipfile.ZIP_DEFLATED) as z:
        for lump in ('MAPINFO', 'SNDINFO', 'LANGUAGE', 'ZSCRIPT'):
            z.write(HERE / 'lumps' / lump, lump)
            files.append(lump)
        for src, dst in ((HERE / 'zscript', 'zscript/boss'), (HERE / 'sprites', 'sprites/boss'),
                         (HERE / 'sounds', 'sounds/boss')):
            for f in sorted(src.iterdir()):
                z.write(f, f'{dst}/{f.name}')
                files.append(f'{dst}/{f.name}')
        z.write(HERE / 'maps' / 'BOSS01.wad', 'maps/BOSS01.wad')
        files.append('maps/BOSS01.wad')
    rel = lambda p: str(p.relative_to(ROOT)).replace('/', '\\')
    info = dict(created=time.strftime('%Y-%m-%d %H:%M'),
                commit=subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
                module=rel(module), module_sha256=sha(module), files=len(files), base=rel(base_copy),
                base_sha256=base_sha, base_from=str(base), engine=ENGINE, iwad=IWAD,
                note='Banc hors campagne : prototype du surveillant-chef (adaptation declaree), visuels et sons provisoires.')
    (out_dir / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (out_dir / 'JOUER.cmd').write_bytes(LAUNCHER.format(module=info['module'], module_sha=info['module_sha256'],
                                                       base=info['base'], base_sha=base_sha, engine=ENGINE,
                                                       iwad=IWAD).replace('\n', '\r\n').encode('ascii'))
    print('boss bench:', info['module'], info['module_sha256'][:12], 'over', info['base'], f'({len(files)} files)')
    return out_dir


if __name__ == '__main__':
    main()
