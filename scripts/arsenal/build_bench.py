#!/usr/bin/env python3
"""Build the RF2 arsenal test bench: a separate module loaded on top of a frozen game build (RF2-ARSENAL contract, 7).

    python scripts/arsenal/build_bench.py [--delivery DIR ...] [--base PK3] [--allow-dirty]

The module (dist/arsenal/RF2_ARSENAL_ESSAI_<date>_<time>/RF2_ARSENAL_ESSAI.pk3) holds the firing range ARSENAL, the
bench code (bench/arsenal/zscript), and for W03 (Manufrance Rapid) and W04 (Manurhin MR73) the weapon classes
generated from an animation file, with their images and sounds:
  - from Astra's delivery when --delivery points at a folder holding an animation file for that weapon (a JSON with
    "weapon": "W03"/"W04" and "sequences"; schema: bench/arsenal/README.md); image and sound paths are relative to
    that file's folder, or to the delivery folder;
  - otherwise from bench/arsenal/placeholder/<weapon>.json with labelled placeholder images and sounds
    (scripts/arsenal/placeholders.py), shown as PROVISOIRE on the bench HUD.
The base is a frozen copy of the game built from the current commit (dist/arsenal/base/RF2_BASE_<commit>.pk3), or
--base. Launchers: dist/arsenal/<build>/JOUER.cmd (this build) and JOUER_RF2_ARSENAL_ESSAI.cmd (the newest), with
their own configuration, saves and logs (user/uzdoom_arsenal_essai.ini, user/savegames_arsenal_essai,
user/logs_arsenal_essai). No accepted launcher, campaign map or inventory is touched.
"""
import argparse, hashlib, io, json, shutil, subprocess, sys, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import placeholders  # noqa: E402
import arsenal_map  # noqa: E402

BENCH = ROOT / 'bench' / 'arsenal'
OUT = ROOT / 'dist' / 'arsenal'
ENGINE = Path(r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe')
IWAD = Path(r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad')
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
WEAPONS = {'W03': 'W03_rapid.json', 'W04': 'W04_mr73.json'}

PUMP = dict(base='RFBenchPump', labels={'fire': 'FireSeq', 'pump': 'PumpSeq', 'dry': 'DrySeq', 'reload_start': 'ReloadStartSeq',
                                        'reload_shell': 'ReloadShellSeq', 'reload_end': 'ReloadEndSeq'},
            reload=('reload_start', 'reload_shell', 'reload_end'),
            need={'fire': {'shot': 1}, 'pump': {'pump_back': 1, 'pump_fwd': 1}, 'reload_shell': {'shell_in': 1}, 'dry': {}},
            events={'shot': 'A_PumpShot({pellets}, {damage}, {sh}, {sv})', 'pump_back': 'A_PumpBack()', 'pump_fwd': 'A_PumpFwd()',
                    'shell_in': 'A_PumpShellIn()', 'dry': 'A_BenchDry()'})
REVOLVER = dict(base='RFBenchRevolver', labels={'fire': 'FireSeq', 'dry': 'DrySeq', 'reload_open': 'ReloadOpenSeq',
                                                'reload_eject': 'ReloadEjectSeq', 'reload_round': 'ReloadRoundSeq',
                                                'reload_close': 'ReloadCloseSeq'},
                reload=('reload_open', 'reload_eject', 'reload_round', 'reload_close'),
                need={'fire': {'shot': 1}, 'reload_eject': {'eject': 1}, 'reload_round': {'round_in': 1}, 'dry': {},
                      'reload_open': {}, 'reload_close': {}},
                events={'shot': 'A_RevShot({pellets}, {damage}, {sh}, {sv})', 'dry': 'A_BenchDry()', 'cyl_open': 'A_RevOpen()',
                        'eject': 'A_RevEject()', 'round_in': 'A_RevRoundIn()', 'cyl_close': 'A_RevClose()'})


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def zs_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


# ------------------------------------------------------------------ sources
def find_delivery(weapon, folders):
    for folder in folders:
        for p in sorted(Path(folder).rglob('*.json')):
            try:
                d = json.loads(p.read_text(encoding='utf-8'))
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(d, dict) and d.get('weapon') == weapon and isinstance(d.get('sequences'), dict):
                return p, Path(folder)
    return None, None


def resolve(rel, anim_dir, delivery_dir):
    for base in (anim_dir, delivery_dir):
        p = base / rel
        if p.is_file():
            return p
    raise SystemExit(f'fichier introuvable dans la livraison : {rel}')


def load_weapon(weapon, deliveries, files):
    """Animation dict, plus the module files it needs added to `files` ({path in pk3: bytes})."""
    anim_path, delivery = find_delivery(weapon, deliveries)
    if anim_path is None:
        anim = json.loads((BENCH / 'placeholder' / WEAPONS[weapon]).read_text(encoding='utf-8'))
        tmp = ROOT / 'build' / 'arsenal' / 'placeholders'
        images = placeholders.make_images(anim, tmp)
        sounds = placeholders.make_sounds(anim, tmp)
        for rel in list(images.values()) + [r for v in sounds.values() for r in v]:
            files[rel] = (tmp / rel).read_bytes()
        source = dict(kind='placeholder', animation=f'bench/arsenal/placeholder/{WEAPONS[weapon]}')
    else:
        anim = json.loads(anim_path.read_text(encoding='utf-8'))
        images, sounds = {}, {}
        prefix = anim.get('file_prefix', '')
        names = {f['image'] for fr in anim['sequences'].values() for f in fr} | {anim['flash']['image']} | set(anim.get('chamber_layers', []))
        for image in names:
            rel = anim.get('files', {}).get(image, prefix + image + '.png')
            files[rel] = resolve(rel, anim_path.parent, delivery).read_bytes()
            images[image] = rel
        folder = 'sounds/bench/' + ('rapid' if anim['kind'] == 'pump' else 'mr73')
        for event, variants in anim.get('sounds', {}).items():
            rels = []
            for v in variants:
                src = resolve(v if v.lower().endswith('.wav') else v + '.wav', anim_path.parent, delivery)
                rel = f'{folder}/{src.name}'
                files[rel] = src.read_bytes()
                rels.append(rel)
            sounds[event] = rels
        source = dict(kind='delivery', animation=str(anim_path), delivery=str(delivery),
                      animation_sha256=sha256(anim_path.read_bytes()))
    anim['_images'], anim['_sounds'], anim['_source'] = images, sounds, source
    return anim


# ------------------------------------------------------------------ generation
def check(anim, spec):
    problems = []
    for seq, need in spec['need'].items():
        frames = anim['sequences'].get(seq)
        if not frames:
            problems.append(f'sequence absente : {seq}')
            continue
        for event, count in need.items():
            n = sum(1 for f in frames if f.get('event') == event)
            if n != count:
                problems.append(f'{seq} : {n} evenement(s) {event}, {count} attendu(s)')
        for f in frames:
            if not isinstance(f.get('tics'), int) or f['tics'] < 1:
                problems.append(f"{seq} : duree invalide {f.get('tics')} ({f.get('image')})")
    shots = sum(1 for fr in anim['sequences'].values() for f in fr if f.get('event') == 'shot')
    if shots != 1:
        problems.append(f'{shots} evenements shot au total, 1 attendu (le tir est un seul evenement)')
    if spec is REVOLVER and len(anim.get('chamber_layers', [])) != 6:
        problems.append('six couches de chambre attendues (chamber_layers)')
    if problems:
        raise SystemExit(f"{anim['weapon']} : animation refusee par le banc :\n  " + '\n  '.join(problems))


def letters_for(anim):
    order = []
    for seq in ['ready'] + [s for s in anim['sequences'] if s != 'ready']:
        for f in anim['sequences'].get(seq, []):
            if f['image'] not in order:
                order.append(f['image'])
    order += [c for c in anim.get('chamber_layers', []) if c not in order]
    if len(order) > len(LETTERS):
        raise SystemExit(f"{anim['weapon']} : {len(order)} images, le banc en gere {len(LETTERS)} par sprite")
    return {img: LETTERS[i] for i, img in enumerate(order)}


def frame_line(anim, spec, seq, i, f, letter, prefix_sound):
    b = anim['ballistics']
    parts = []
    if i == 0:
        parts.append(f'A_BenchSeq("{seq}")')
    if 'offset' in f:
        parts.append(f"A_WeaponOffset({f['offset'][0]}, {f['offset'][1]})")
    ev = f.get('event')
    if ev:
        code = spec['events'].get(ev)
        parts.append(code.format(pellets=b['pellets'], damage=b['damage'], sh=b['spread'][0], sv=b['spread'][1]) if code
                     else f'A_BenchEvent("{ev}")')
    if seq in spec['reload'] and spec is REVOLVER:
        parts.append(f"A_RevChambers({'true' if f.get('chambers') else 'false'})")
    if f.get('ready_point'):
        parts.append('A_WeaponReady(WRF_NOFIRE | WRF_NOBOB)')
    bright = ' Bright' if ev == 'shot' else ''
    body = (' { ' + '; '.join(parts) + '; }') if len(parts) > 1 else (' ' + parts[0] + ';' if parts else ';')
    return f"        {anim['sprite']} {letter} {f['tics']}{bright}{body}"


def gen_class(anim):
    spec = PUMP if anim['kind'] == 'pump' else REVOLVER
    check(anim, spec)
    L = letters_for(anim)
    spr, ready = anim['sprite'], L[anim['sequences']['ready'][0]['image']]
    prefix = 'rf/bench/' + ('rapid/' if spec is PUMP else 'mr73/')
    cap = anim['capacity']
    out = [f"class {anim['class']} : {spec['base']}", '{', '    Default', '    {',
           f"        Weapon.AmmoType \"{anim['ammo']['class']}\";", '        Weapon.AmmoUse 0;', '        Weapon.AmmoGive 0;',
           f"        Weapon.SlotNumber {anim['slot']};", f"        Weapon.SelectionOrder {3000 + anim['slot']};",
           '        Weapon.BobStyle "InverseSmooth";', '        Weapon.BobRangeX 0.5;', '        Weapon.BobRangeY 0.35;']
    if 'raise' in anim['_sounds']:
        out.append(f'        Weapon.UpSound "{prefix}raise";')
    out += [f"        Tag {zs_str(anim['name'])};", '        +WEAPON.AMMO_OPTIONAL', '        +WEAPON.NOAUTOFIRE', '    }', '',
            f'    override String SoundPrefix() {{ return "{prefix}"; }}']
    if spec is PUMP:
        out += [f"    override int TubeCap() {{ return {int(cap['tube'])}; }}",
                f"    override bool CarriesChamber() {{ return {'true' if cap.get('chamber', 1) else 'false'}; }}"]
    else:
        out += [f"    override int Cylinder() {{ return {int(cap.get('cylinder', 6))}; }}"]
    out += ['', '    States', '    {',
            '    Ready:', f'        {spr} {ready} 1 A_BenchReady();', '        Loop;',
            '    Deselect:', f'        {spr} {ready} 1 A_Lower(12);', '        Loop;',
            '    Select:', f'        {spr} {ready} 1 A_Raise(12);', '        Loop;',
            '    Fire:', f"        {spr} {ready} 0 {'A_PumpFire()' if spec is PUMP else 'A_RevFire()'};", '        Goto Ready;']
    tails = ({'fire': 'Goto PumpSeq;', 'pump': f'{spr} {ready} 0 A_PumpAfterPump();', 'dry': 'Goto Ready;',
              'reload_start': 'Goto ReloadShellSeq;', 'reload_shell': f'{spr} {ready} 0 A_PumpShellNext();',
              'reload_end': f'{spr} {ready} 0 A_PumpAfterReload();'} if spec is PUMP else
             {'fire': 'Goto Ready;', 'dry': 'Goto Ready;', 'reload_open': 'Goto ReloadEjectSeq;',
              'reload_eject': 'Goto ReloadRoundSeq;', 'reload_round': f'{spr} {ready} 0 A_RevRoundNext();',
              'reload_close': f'{spr} {ready} 0 A_RevAfterReload();'})
    order = list(spec['labels'])
    for seq in order:
        if seq == spec['reload'][0]:
            out += ['    Reload:', f"        {spr} {ready} 0 {'A_PumpReloadCheck()' if spec is PUMP else 'A_RevReloadCheck()'};"]
        out.append(f"    {spec['labels'][seq]}:")
        for i, f in enumerate(anim['sequences'][seq]):
            out.append(frame_line(anim, spec, seq, i, f, L[f['image']], prefix))
        tail = tails[seq]
        out.append('        ' + tail if not tail.startswith('Goto') else '        ' + tail)
        if not tail.startswith('Goto'):
            out.append('        Goto Ready;')
    if spec is REVOLVER:
        for n, layer in enumerate(anim['chamber_layers'], 1):
            out += [f'    Chamber{n}:', f'        {spr} {L[layer]} 1 A_JumpIf(invoker.Rounds < {n}, "Chamber{n}Off");', '        Loop;',
                    f'    Chamber{n}Off:', f'        TNT1 A 1 A_JumpIf(invoker.Rounds >= {n}, "Chamber{n}");', '        Loop;']
    out += ['    Flash:', f"        {anim['flash_sprite']} A {anim['flash']['tics']} Bright A_Light2;", '        TNT1 A 0 A_Light0;',
            '        Stop;', '    Spawn:', '        TNT1 A -1;', '        Stop;', '    }', '}', '']
    return '\n'.join(out), L


def gen_textures(anim, L, files):
    from PIL import Image
    out = [f"// {anim['weapon']} {anim['name']} - {anim['_source']['kind']}"]
    sx, sy = anim['scale']
    ox, oy = anim['offset']

    def sprite(name, rel):
        w, h = Image.open(io.BytesIO(files[rel])).size
        return [f'Sprite {name}, {w}, {h}', '{', f'    XScale {sx}', f'    YScale {sy}', f'    Offset {ox}, {oy}',
                f'    Patch "{rel}", 0, 0', '}']
    for image, letter in L.items():
        out += sprite(f"{anim['sprite']}{letter}0", anim['_images'][image])
    out += sprite(f"{anim['flash_sprite']}A0", anim['_images'][anim['flash']['image']])
    return '\n'.join(out) + '\n'


def gen_sndinfo(anim):
    prefix = 'rf/bench/' + ('rapid/' if anim['kind'] == 'pump' else 'mr73/')
    out = [f"// {anim['weapon']} {anim['name']} - {anim['_source']['kind']}"]
    for event, rels in anim['_sounds'].items():
        if len(rels) == 1:
            out.append(f'{prefix}{event:<16} "{rels[0]}"')
        else:
            out.append(f'$random {prefix}{event} {{ ' + ' '.join(f'{prefix}{event}_{i + 1}' for i in range(len(rels))) + ' }')
            out += [f'{prefix}{event}_{i + 1:<14} "{r}"' for i, r in enumerate(rels)]
    return '\n'.join(out) + '\n'


def gen_setup(anims):
    out = ['class RFBenchSetup play', '{', '    static void Give(Actor pl)', '    {']
    for a in anims:
        out += [f"        pl.GiveInventory('{a['class']}', 1);", f"        pl.GiveInventory('{a['ammo']['class']}', {a['ammo']['start_reserve']});"]
    for a in anims:
        out.append(f"        {{ let w = RFBenchWeapon(pl.FindInventory('{a['class']}')); if (w != null) w.Baseline = w.Loaded() + w.Reserve(); }}")
    out += [f"        if (pl.player != null) pl.player.PendingWeapon = Weapon(pl.FindInventory('{anims[0]['class']}'));",
            '        RFBench.Log("dotation Browning FAL pied-de-biche ' + ' '.join(a['class'] for a in anims) + '");', '    }', '',
            '    static clearscope String Source()', '    {']
    provisional, delivered = '\\cgPROVISOIRE\\c-', 'livraison'
    text = '  '.join(f"{a['weapon']} " + (provisional if a['_source']['kind'] == 'placeholder' else delivered) for a in anims)
    out += [f'        return "{text}";', '    }', '}', '']
    for a in anims:
        out += [f"class {a['ammo']['class']} : Ammo", '{', '    Default', '    {', '        Inventory.Amount 1;',
                '        Inventory.MaxAmount 999;', '        Ammo.BackpackAmount 0;', '        Ammo.BackpackMaxAmount 999;',
                f"        Tag {zs_str(a['ammo']['tag'])};", '        +INVENTORY.IGNORESKILL', '    }',
                '    States', '    {', '    Spawn:', '        TNT1 A -1;', '        Stop;', '    }', '}', '']
    return '\n'.join(out)


MAPINFO = '''// RF2 arsenal test bench: the firing range, outside the campaign (no next chapter, no music).
gameinfo
{
    AddEventHandlers = "RFBenchHandler"
}

map ARSENAL "Banc d'essai - arsenal"
{
    levelnum = 99
    next = "ARSENAL"
    nointermission
    lightmode = 8
    music = ""
}

DoomEdNums
{
    30950 = RFBenchTarget
}
'''
LANGUAGE = '''[enu default]
RF_OBJ_ARSENAL_0 = "Banc d'essai : 4 Rapid, 5 MR73, R recharger. Hors campagne.";
RF_ARSENAL_DATE = "Banc d'essai - hors campagne";
'''
TARGET_TEXTURES = 'Sprite RFTGA0, 160, 288\n{\n    XScale 4\n    YScale 4\n    Offset 80, 288\n    Patch "graphics/bench/target.png", 0, 0\n}\n'

LAUNCHER = r'''@echo off
setlocal
rem Red Flags 2 - BANC D'ESSAI DE L'ARSENAL (hors campagne) : W03 Manufrance Rapid, W04 Manurhin MR73.
rem Module {module_rel} (sha256 {module_sha})
rem Base   {base_rel} (sha256 {base_sha})
rem Configuration, sauvegardes et journaux propres au banc ; ni la partie normale ni ses sauvegardes ne sont touchees.
set "ROOT={root_expr}"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "BASE=%ROOT%{base_rel}"
set "MODULE=%ROOT%{module_rel}"
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
set "CFG=%ROOT%user\uzdoom_arsenal_essai.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_arsenal_essai" mkdir "%ROOT%user\savegames_arsenal_essai"
if not exist "%ROOT%user\logs_arsenal_essai" mkdir "%ROOT%user\logs_arsenal_essai"
set "D=%DATE:/=-%"
set "D=%D: =_%"
set "T=%TIME: =0%"
set "T=%T::=-%"
set "T=%T:.=-%"
set "T=%T:,=-%"
set "STAMP=%D%_%T%"
set "LOG=%ROOT%user\logs_arsenal_essai\essai_%STAMP%.log"
echo RF2 BANC D'ESSAI ARSENAL (hors campagne) : {module_rel}
echo Journal : %LOG%
rem Journal par la sortie standard du moteur (+logfile n'est pas pris en compte en ligne de commande par UZDoom 5.0.1).
"%ENGINE%" -iwad "%IWAD%" -file "%BASE%" "%MODULE%" -config "%CFG%" -savedir "%ROOT%user\savegames_arsenal_essai" -skill 2 -stdout +map ARSENAL %* > "%LOG%" 2>&1
exit /b %errorlevel%
'''


def base_pk3(a):
    """The game under the module depends on src/ only: one frozen build per src tree, reused by later bench builds."""
    if a.base:
        return Path(a.base).resolve()
    dirty = git('status', '--porcelain', '--untracked-files=no', '--', 'src') != ''
    if dirty and not a.allow_dirty:
        raise SystemExit('Refus : modifications non committees dans src/ (commit, ou --allow-dirty).')
    tree = git('rev-parse', '--short=12', 'HEAD:src') + ('-dirty' if dirty else '')
    target = OUT / 'base' / f'RF2_BASE_src_{tree}.pk3'
    if target.exists() and not dirty:
        return target
    subprocess.run(['pwsh', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'scripts' / 'build.ps1')], check=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target = target.with_name(target.stem + time.strftime('_%Y%m%d_%H%M%S') + '.pk3')
    shutil.copy2(ROOT / 'dist' / 'RF2_DEV.pk3', target)
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--delivery', action='append', default=[], help="Astra delivery folder (repeatable)")
    ap.add_argument('--base', help='game pk3 to load under the module (default: frozen build of the current commit)')
    ap.add_argument('--allow-dirty', action='store_true')
    ap.add_argument('--scratch', help='only write the module to this path (development: no dated build, no launcher)')
    a = ap.parse_args()

    files = {}
    anims = [load_weapon(w, a.delivery, files) for w in WEAPONS]
    zs = ['version "4.14"', '#include "zscript/bench/bench_common.zs"', '#include "zscript/bench/bench_weapons.zs"', '']
    weapons_zs = ['// Generated by scripts/arsenal/build_bench.py - do not edit; see bench/arsenal/README.md.', '']
    textures = ['// Generated by scripts/arsenal/build_bench.py.', TARGET_TEXTURES]
    sndinfo = ['// Generated by scripts/arsenal/build_bench.py.']
    report = []
    for anim in anims:
        code, L = gen_class(anim)
        weapons_zs.append(code)
        textures.append(gen_textures(anim, L, files))
        sndinfo.append(gen_sndinfo(anim))
        report.append(dict(weapon=anim['weapon'], cls=anim['class'], source=anim['_source'], images=len(L) + 1,
                           sounds={k: len(v) for k, v in anim['_sounds'].items()},
                           sequences={k: [dict(image=f['image'], tics=f['tics'], event=f.get('event')) for f in v]
                                      for k, v in anim['sequences'].items()},
                           tics={k: sum(f['tics'] for f in v) for k, v in anim['sequences'].items()},
                           capacity=anim['capacity'], ballistics=anim['ballistics'], provisional=anim.get('provisional', False)))
    weapons_zs.append(gen_setup(anims))
    tmp = ROOT / 'build' / 'arsenal'
    placeholders.make_target(tmp / 'target.png')
    files['graphics/bench/target.png'] = (tmp / 'target.png').read_bytes()
    files['ZSCRIPT.bench'] = '\n'.join(zs).encode()
    files['zscript/bench/bench_common.zs'] = (BENCH / 'zscript' / 'bench_common.zs').read_bytes()
    files['zscript/bench/bench_weapons.zs'] = '\n'.join(weapons_zs).encode()
    files['TEXTURES.bench'] = '\n'.join(textures).encode()
    files['SNDINFO.bench'] = '\n'.join(sndinfo).encode()
    files['MAPINFO.bench'] = MAPINFO.encode()
    files['LANGUAGE.bench'] = LANGUAGE.encode()
    files['maps/ARSENAL.wad'] = arsenal_map.wad_bytes()

    if a.scratch:
        with zipfile.ZipFile(a.scratch, 'w', zipfile.ZIP_DEFLATED) as z:
            for name in sorted(files):
                z.writestr(name, files[name])
        print('module (developpement) :', a.scratch)
        return 0
    base = base_pk3(a)
    stamp = time.strftime('%Y%m%d_%H%M')
    folder = OUT / f'RF2_ARSENAL_ESSAI_{stamp}'
    folder.mkdir(parents=True, exist_ok=False)
    module = folder / 'RF2_ARSENAL_ESSAI.pk3'
    with zipfile.ZipFile(module, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            z.writestr(name, files[name])
    (folder / 'genere').mkdir(exist_ok=True)
    for name in ('ZSCRIPT.bench', 'zscript/bench/bench_weapons.zs', 'TEXTURES.bench', 'SNDINFO.bench', 'MAPINFO.bench'):
        (folder / 'genere' / Path(name).name).write_bytes(files[name])
    rel = lambda p: str(p.relative_to(ROOT)).replace('/', '\\')
    info = dict(created=time.strftime('%Y-%m-%d %H:%M'), commit=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'),
                module=rel(module), module_sha256=sha256(module.read_bytes()), files=len(files),
                base=rel(base) if base.is_relative_to(ROOT) else str(base), base_sha256=sha256(base.read_bytes()),
                base_src_tree=None if a.base else git('rev-parse', 'HEAD:src'),
                engine=str(ENGINE), iwad=str(IWAD), weapons=report,
                status='BANC D\'ESSAI - hors campagne ; aucune approbation du proprietaire',
                launcher='JOUER_RF2_ARSENAL_ESSAI.cmd (le plus recent) / ' + folder.name + '\\JOUER.cmd (ce build) ; '
                         'user\\uzdoom_arsenal_essai.ini, user\\savegames_arsenal_essai, user\\logs_arsenal_essai')
    (folder / 'BUILD_INFO.json').write_bytes(json.dumps(info, indent=2, ensure_ascii=False).encode('utf-8'))
    common = dict(module_rel=rel(module), module_sha=info['module_sha256'], base_rel=info['base'], base_sha=info['base_sha256'])
    (ROOT / 'JOUER_RF2_ARSENAL_ESSAI.cmd').write_bytes(LAUNCHER.format(root_expr='%~dp0', **common).replace('\n', '\r\n').encode('ascii'))
    (folder / 'JOUER.cmd').write_bytes(LAUNCHER.format(root_expr='%~dp0..\\..\\..\\', **common).replace('\n', '\r\n').encode('ascii'))
    print(json.dumps({k: v for k, v in info.items() if k != 'weapons'}, indent=2, ensure_ascii=False))
    for r in report:
        print(r['weapon'], r['source']['kind'], 'tics', r['tics'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
