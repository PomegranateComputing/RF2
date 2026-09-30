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
WEAPONS = {'W03': 'W03_rapid.json', 'W04': 'W04_mr73.json', 'W05': 'W05_famas.json', 'W09': 'W09_scorpion.json',
           'W10': 'W10_pied_de_biche.json'}

# One spec per mechanism: base class, sequences (state labels, in order), events that must appear, event -> code,
# the Fire entry, the reload check, what ends each sequence ("0 X" = a 0-tic frame calling X, else a Goto).
PUMP = dict(kind='pump', base='RFBenchPump', shots=True,
            labels={'fire': 'FireSeq', 'pump': 'PumpSeq', 'dry': 'DrySeq', 'reload_start': 'ReloadStartSeq',
                    'reload_shell': 'ReloadShellSeq', 'reload_end': 'ReloadEndSeq'},
            reload=('reload_start', 'reload_shell', 'reload_end'),
            need={'fire': {'shot': 1}, 'pump': {'pump_back': 1, 'pump_fwd': 1}, 'reload_shell': {'shell_in': 1}, 'dry': {}},
            events={'shot': 'A_PumpShot({pellets}, {damage}, {sh}, {sv})', 'pump_back': 'A_PumpBack()', 'pump_fwd': 'A_PumpFwd()',
                    'shell_in': 'A_PumpShellIn()', 'dry': 'A_BenchDry()'},
            entry='A_PumpFire()', reload_check='A_PumpReloadCheck()',
            tails={'fire': 'Goto PumpSeq', 'pump': '0 A_PumpAfterPump()', 'dry': 'Goto Ready', 'reload_start': 'Goto ReloadShellSeq',
                   'reload_shell': '0 A_PumpShellNext()', 'reload_end': '0 A_PumpAfterReload()'})
REVOLVER = dict(kind='revolver', base='RFBenchRevolver', shots=True,
                labels={'fire': 'FireSeq', 'dry': 'DrySeq', 'reload_open': 'ReloadOpenSeq', 'reload_eject': 'ReloadEjectSeq',
                        'reload_round': 'ReloadRoundSeq', 'reload_close': 'ReloadCloseSeq'},
                reload=('reload_open', 'reload_eject', 'reload_round', 'reload_close'),
                need={'fire': {'shot': 1}, 'reload_eject': {'eject': 1}, 'reload_round': {'round_in': 1}, 'dry': {},
                      'reload_open': {}, 'reload_close': {}},
                events={'shot': 'A_RevShot({pellets}, {damage}, {sh}, {sv})', 'dry': 'A_BenchDry()', 'cyl_open': 'A_RevOpen()',
                        'eject': 'A_RevEject()', 'round_in': 'A_RevRoundIn()', 'cyl_close': 'A_RevClose()'},
                entry='A_RevFire()', reload_check='A_RevReloadCheck()',
                tails={'fire': 'Goto Ready', 'dry': 'Goto Ready', 'reload_open': 'Goto ReloadEjectSeq', 'reload_eject': 'Goto ReloadRoundSeq',
                       'reload_round': '0 A_RevRoundNext()', 'reload_close': '0 A_RevAfterReload()'})
MAGAZINE = dict(kind='magazine', base='RFBenchMagazine', shots=True,
                labels={'fire': 'FireSeq', 'dry': 'DrySeq', 'reload': 'ReloadSeq', 'reload_empty': 'ReloadEmptySeq', 'mode': 'ModeSeq'},
                reload=('reload', 'reload_empty'),
                need={'fire': {'shot': 1}, 'dry': {}, 'reload': {'seat': 1}},
                optional={'reload_empty': {'seat': 1}, 'mode': {'mode': 1}},
                events={'shot': 'A_MagShot({pellets}, {damage}, {sh}, {sv})', 'seat': 'A_MagSeat()', 'dry': 'A_BenchDry()', 'mode': 'A_MagMode()'},
                entry='A_MagFire()', reload_check='A_MagReloadCheck()',
                tails={'fire': '0 A_MagAfterShot()', 'dry': 'Goto Ready', 'reload': '0 A_MagAfterReload()',
                       'reload_empty': '0 A_MagAfterReload()', 'mode': 'Goto Ready'})
SAW = dict(kind='saw', base='RFBenchSaw', shots=False,
           labels={'start': 'StartSeq', 'run': 'RunSeq', 'stop': 'StopSeq', 'contact': 'ContactSeq'}, reload=(),
           need={'start': {'start': 1}, 'run': {}, 'stop': {'stop': 1}}, optional={'contact': {}},
           events={'start': 'A_SawStart()', 'stop': 'A_SawStop()'},
           entry=None, fire_goto='StartSeq', frame_state={'run': 'A_SawRun()', 'contact': 'A_SawEffort()'},
           tails={'start': 'Goto RunSeq', 'run': 'Goto RunSeq', 'stop': 'Goto Ready', 'contact': 'Goto RunSeq'})
MELEE = dict(kind='melee', base='RFBenchMelee', shots=False,
             labels={'swing': 'SwingSeq'}, reload=(),
             need={'swing': {'strike': 1}},
             events={'strike': 'A_MeleeStrike()'},
             entry=None, fire_goto='SwingSeq', tails={'swing': 'Goto Ready'})
SPECS = {s['kind']: s for s in (PUMP, REVOLVER, MAGAZINE, SAW, MELEE)}


def sound_prefix(anim):
    return 'rf/bench/' + {'pump': 'rapid', 'revolver': 'mr73'}.get(anim['kind'], anim['weapon'].lower()) + '/'

def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def zs_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


# ------------------------------------------------------------------ sources
def find_delivery(weapon, folders):
    for folder in folders:
        top = sorted(Path(folder).glob('*.json'))              # the delivery's own files before its evidence copies
        for p in top + [q for q in sorted(Path(folder).rglob('*.json')) if q not in top]:
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
        images, sounds, provenance = {}, {}, {}
        # The module stores each file at the destination the delivery's manifest gives it (target_relpath), the path
        # a later import will use; a delivery without manifest keeps its own relative paths.
        targets = {}
        manifest = delivery / 'manifest.json'
        if manifest.is_file():
            for f in json.loads(manifest.read_text(encoding='utf-8')).get('files') or []:
                if isinstance(f, dict) and f.get('file') and f.get('target_relpath'):
                    targets[f['file']] = f['target_relpath']
        prefix = anim.get('file_prefix', '')
        rig = rig_of(anim)
        names = ({f['image'] for fr in anim['sequences'].values() for f in fr} | ({anim['flash']['image']} if anim.get('flash') else set())
                 | {img for group in rig.values() if group for poses in group for img in poses})
        for image in sorted(names):
            rel = anim.get('files', {}).get(image, prefix + image + '.png')
            src = resolve(rel, anim_path.parent, delivery)
            target = targets.get(rel, rel)
            files[target] = src.read_bytes()
            images[image] = target
            provenance[target] = dict(file=rel, sha256=sha256(files[target]))
        folder = 'sounds/bench/' + sound_prefix(anim).split('/')[2]
        for event, variants in anim.get('sounds', {}).items():
            rels = []
            for v in variants:
                rel = v if v.lower().endswith('.wav') else v + '.wav'
                src = resolve(rel, anim_path.parent, delivery)
                target = targets.get(rel, f'{folder}/{src.name}')
                files[target] = src.read_bytes()
                rels.append(target)
                provenance[target] = dict(file=rel, sha256=sha256(files[target]))
            sounds[event] = rels
        source = dict(kind='delivery', animation=str(anim_path), delivery=str(delivery),
                      animation_sha256=sha256(anim_path.read_bytes()), manifest_targets=bool(targets), files=provenance)
    anim['_images'], anim['_sounds'], anim['_source'] = images, sounds, source
    return anim


def apply_presentation(anim, layer, path):
    """Recoil offsets (by sequence and frame index) and a short HUD name, for frames the animation leaves without."""
    anim['_presentation'] = None
    if not layer:
        return
    applied = []
    for seq, frames in (layer.get('offsets') or {}).items():
        for idx, off in frames.items():
            f = anim['sequences'][seq][int(idx)]
            if 'offset' not in f:
                f['offset'] = off
                applied.append(f'{seq}[{idx}]={off}')
    if layer.get('tag'):
        anim['tag'] = layer['tag']
    anim['_presentation'] = dict(file=path, offsets=applied, tag=layer.get('tag'))


def load_voices(deliveries, files):
    """Viktor's two lines: from a delivery JSON with a "voices" key, else placeholder cues. Durations come from the
    files. {"voices": {"manurhin": {"take": wav, "phrase": wav, "sneer": wav, "sneer_at_ms": int, "mode": "take"|"split"},
    "chasseurs": {"take": wav}}} (paths relative to that JSON or to the delivery)."""
    import wave
    found = None
    for folder in deliveries:
        for q in sorted(Path(folder).rglob('*.json')):
            try:
                d = json.loads(q.read_text(encoding='utf-8'))
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(d, dict) and isinstance(d.get('voices'), dict):
                found = (q, Path(folder), d['voices'])
                break
        if found:
            break
    rels, mode, sneer_ms = {}, 'take', 0
    if found:
        q, folder, v = found
        man, cha = v.get('manurhin', {}), v.get('chasseurs', {})
        mode = man.get('mode', 'take')
        sneer_ms = int(man.get('sneer_at_ms', 0))
        for logical, src in (('manurhin', man.get('take')), ('manurhin_phrase', man.get('phrase')),
                             ('manurhin_rire', man.get('sneer')), ('chasseurs', cha.get('take'))):
            if src:
                path = resolve(src, q.parent, folder)
                rels[logical] = f'sounds/bench/voice/{logical}.wav'
                files[rels[logical]] = path.read_bytes()
        source = dict(kind='delivery', file=str(q))
    else:
        tmp = ROOT / 'build' / 'arsenal' / 'placeholders'
        rels = placeholders.make_voices(tmp)
        for rel in rels.values():
            files[rel] = (tmp / rel).read_bytes()
        source = dict(kind='placeholder')

    def tics(logical):
        if logical not in rels:
            return 0
        with wave.open(io.BytesIO(files[rels[logical]])) as w:
            return int(w.getnframes() / w.getframerate() * 35 + 0.999)
    split = mode == 'split' and 'manurhin_phrase' in rels and 'manurhin_rire' in rels
    if split and not sneer_ms:
        sneer_ms = int(tics('manurhin_phrase') / 35 * 1000)
    man_tics = (max(tics('manurhin_phrase'), int(sneer_ms * 35 / 1000) + tics('manurhin_rire')) if split else tics('manurhin'))
    return dict(rels=rels, split=split, sneer_tics=int(sneer_ms * 35 / 1000), tics=(man_tics, tics('chasseurs')), source=source)


def gen_voices(v):
    kind = 'PROVISOIRE (reperes, pas des voix)' if v['source']['kind'] == 'placeholder' else 'livraison'
    code = ['class RFBenchVoiceData play', '{',
            f"    static int Tics(int line) {{ return line == 0 ? {v['tics'][0]} : {v['tics'][1]}; }}",
            f"    static bool ManurhinSplit() {{ return {'true' if v['split'] else 'false'}; }}",
            f"    static int SneerAt() {{ return {v['sneer_tics']}; }}",
            f'    static clearscope String Source() {{ return "{kind}"; }}', '}', '']
    snd = ['// Viktor: lines at the first acquisition - ' + kind]
    for logical, rel in v['rels'].items():
        snd.append(f'rf/bench/voice/{logical:<16} "{rel}"')
    return '\n'.join(code), '\n'.join(snd) + '\n'


def rig_of(anim):
    """Revolver rig layers: per chamber the images of each cylinder pose (and of the fired case when given), per
    chamber the images of each hand stage. The older single-image chamber_layers are one pose with no hand."""
    layers = anim.get('rig_layers') or {}
    chambers = layers.get('chambers') or [[c] for c in anim.get('chamber_layers', [])]
    return dict(chambers=chambers, fired=layers.get('chambers_fired'), hands=layers.get('hands'))


def rig_sprites(anim):
    """(state label, sprite, letter, image, rig code) of every rig layer image; code = kind*100 + chamber*10 + j."""
    rig, out = rig_of(anim), []
    for i, poses in enumerate(rig['chambers'], 1):
        for j, img in enumerate(poses, 1):
            out.append((f'Chamber{i}Pose{j}', f'RMC{i}', LETTERS[j - 1], img, 0 * 100 + i * 10 + j))
        for j, img in enumerate((rig['fired'] or [[]] * 6)[i - 1], 1):
            out.append((f'Chamber{i}Pose{j}Fired', f'RMC{i}', LETTERS[len(poses) + j - 1], img, 1 * 100 + i * 10 + j))
    for i, stages in enumerate(rig['hands'] or [], 1):
        for j, img in enumerate(stages, 1):
            out.append((f'Hand{i}Stage{j}', f'RMH{i}', LETTERS[j - 1], img, 2 * 100 + i * 10 + j))
    return out


# ------------------------------------------------------------------ generation
def check(anim, spec):
    problems = []
    needs = dict(spec['need'])
    needs.update({seq: need for seq, need in spec.get('optional', {}).items() if seq in anim['sequences']})
    for seq, need in needs.items():
        frames = anim['sequences'].get(seq)
        if not frames:
            problems.append(f'sequence absente : {seq}')
            continue
        for event, count in need.items():
            n = sum(1 for f in frames if f.get('event') == event)
            if n != count:
                problems.append(f'{seq} : {n} evenement(s) {event}, {count} attendu(s)')
    for seq, frames in anim['sequences'].items():
        for f in frames:
            if not isinstance(f.get('tics'), int) or f['tics'] < 1:
                problems.append(f"{seq} : duree invalide {f.get('tics')} ({f.get('image')})")
    if spec['shots']:
        shots = sum(1 for fr in anim['sequences'].values() for f in fr if f.get('event') == 'shot')
        if shots != 1:
            problems.append(f'{shots} evenements shot au total, 1 attendu (le tir est un seul evenement)')
    if spec is REVOLVER:
        rig = rig_of(anim)
        poses = [int(f.get('chamber_pose') or (1 if f.get('chambers') else 0)) for fr in anim['sequences'].values() for f in fr]
        stages = [int(f.get('hand_stage') or 0) for fr in anim['sequences'].values() for f in fr]
        if len(rig['chambers']) != 6 or not all(rig['chambers']):
            problems.append('six chambres attendues (rig_layers.chambers ou chamber_layers)')
        elif max(poses) > min(len(p) for p in rig['chambers']):
            problems.append(f'chamber_pose {max(poses)} sans image pour chaque chambre')
        if rig['fired'] and (len(rig['fired']) != 6 or any(len(f) != len(c) for f, c in zip(rig['fired'], rig['chambers']))):
            problems.append('chambers_fired : une image par chambre et par pose attendue')
        if max(stages) > 0 and (not rig['hands'] or len(rig['hands']) != 6 or max(stages) > min(len(h) for h in rig['hands'])):
            problems.append(f'hand_stage {max(stages)} sans image de main pour chaque chambre (rig_layers.hands)')
    if problems:
        raise SystemExit(f"{anim['weapon']} : animation refusee par le banc :\n  " + '\n  '.join(problems))


def letters_for(anim):
    order = []
    for seq in ['ready'] + [s for s in anim['sequences'] if s != 'ready']:
        for f in anim['sequences'].get(seq, []):
            if f['image'] not in order:
                order.append(f['image'])
    if len(order) > len(LETTERS):
        raise SystemExit(f"{anim['weapon']} : {len(order)} images, le banc en gere {len(LETTERS)} par sprite")
    return {img: LETTERS[i] for i, img in enumerate(order)}


def frame_line(anim, spec, seq, i, f, letter):
    b = anim.get('ballistics') or dict(pellets=1, damage=0, spread=[0, 0])
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
        pose = int(f.get('chamber_pose') or (1 if f.get('chambers') else 0))
        parts.append(f"A_RevRig({pose}, {int(f.get('hand_stage') or 0)})")
    if f.get('ready_point'):
        parts.append('A_WeaponReady(WRF_NOFIRE | WRF_NOBOB)')
    state_fn = spec.get('frame_state', {}).get(seq)        # a check that may leave the sequence (the saw's run)
    bright = ' Bright' if ev == 'shot' else ''
    if state_fn:
        body = (' { ' + '; '.join(parts) + f'; return {state_fn}; }}') if parts else f' {state_fn};'
    else:
        body = (' { ' + '; '.join(parts) + '; }') if len(parts) > 1 else (' ' + parts[0] + ';' if parts else ';')
    return f"        {anim['sprite']} {letter} {f['tics']}{bright}{body}"


def gen_class(anim):
    spec = SPECS[anim['kind']]
    check(anim, spec)
    L = letters_for(anim)
    spr, ready = anim['sprite'], L[anim['sequences']['ready'][0]['image']]
    prefix = sound_prefix(anim)
    cap = anim.get('capacity') or {}
    contact = anim.get('contact') or {}
    out = [f"class {anim['class']} : {spec['base']}", '{', '    Default', '    {']
    if anim.get('ammo'):
        out += [f"        Weapon.AmmoType \"{anim['ammo']['class']}\";", '        Weapon.AmmoUse 0;', '        Weapon.AmmoGive 0;']
    out += [f"        Weapon.SlotNumber {anim['slot']};", f"        Weapon.SelectionOrder {3000 + anim['slot']};",
            '        Weapon.BobStyle "InverseSmooth";', '        Weapon.BobRangeX 0.5;', '        Weapon.BobRangeY 0.35;']
    if 'raise' in anim['_sounds']:
        out.append(f'        Weapon.UpSound "{prefix}raise";')
    out += [f"        Tag {zs_str(anim.get('tag') or anim['name'])};", '        +WEAPON.AMMO_OPTIONAL', '        +WEAPON.NOAUTOFIRE']
    if spec in (SAW, MELEE):
        out += ['        +WEAPON.MELEEWEAPON']
    out += ['    }', '', f'    override String SoundPrefix() {{ return "{prefix}"; }}']
    if spec is PUMP:
        out += [f"    override int TubeCap() {{ return {int(cap['tube'])}; }}",
                f"    override bool CarriesChamber() {{ return {'true' if cap.get('chamber', 1) else 'false'}; }}"]
    elif spec is REVOLVER:
        out += [f"    override int Cylinder() {{ return {int(cap.get('cylinder', 6))}; }}", '',
                '    override State RigState(int kind, int i, int j)', '    {', '        switch (kind * 100 + i * 10 + j)', '        {']
        out += [f'        case {code}: return FindState("{label}");' for label, _, _, _, code in rig_sprites(anim)]
        out += ['        }', '        return null;', '    }']
    elif spec is MAGAZINE:
        out += [f"    override int MagCap() {{ return {int(cap.get('magazine', 25))}; }}",
                f"    override int BurstSize() {{ return {int(anim.get('burst', 3))}; }}"]
    elif spec is SAW:
        out += [f"    override int Range() {{ return {int(contact.get('range', 56))}; }}",
                f"    override int ContactDamage() {{ return {int(contact.get('damage', 6))}; }}",
                f"    override int ContactEvery() {{ return {int(contact.get('every', 4))}; }}",
                f"    override bool EffortPoses() {{ return {'true' if anim['sequences'].get('contact') else 'false'}; }}"]
    elif spec is MELEE:
        out += [f"    override int Range() {{ return {int(contact.get('range', 64))}; }}",
                f"    override int StrikeDamage() {{ return {int(contact.get('damage', 50))}; }}"]
    out += ['', '    States', '    {',
            '    Ready:', f'        {spr} {ready} 1 A_BenchReady();', '        Loop;',
            '    Deselect:', f'        {spr} {ready} 1 A_Lower(12);', '        Loop;',
            '    Select:', f'        {spr} {ready} 1 A_Raise(12);', '        Loop;', '    Fire:']
    out += [f"        {spr} {ready} 0 {spec['entry']};", '        Goto Ready;'] if spec['entry'] else [f"        Goto {spec['fire_goto']};"]
    if spec is MAGAZINE:
        out += ['    AltFire:'] + (['        Goto ModeSeq;'] if 'mode' in anim['sequences'] else [f'        {spr} {ready} 6 A_MagMode();', '        Goto Ready;'])
    present = [seq for seq in spec['labels'] if seq in anim['sequences']]
    for seq in present:
        if spec['reload'] and seq == spec['reload'][0]:
            out += ['    Reload:', f"        {spr} {ready} 0 {spec['reload_check']};"]
        out.append(f"    {spec['labels'][seq]}:")
        for i, f in enumerate(anim['sequences'][seq]):
            out.append(frame_line(anim, spec, seq, i, f, L[f['image']]))
        tail = spec['tails'][seq]
        if tail.startswith('Goto'):
            out.append(f'        {tail};')
        else:
            out += [f'        {spr} {ready} {tail};', '        Goto Ready;']
    if spec is REVOLVER:
        for label, sprite, letter, _, _ in rig_sprites(anim):      # rig layers (101-107), set by RFBenchRevolver.ShowRig
            out += [f'    {label}:', f'        {sprite} {letter} -1;', '        Stop;']
    if anim.get('flash'):
        out += ['    Flash:', f"        {anim['flash_sprite']} A {anim['flash']['tics']} Bright A_Light2;", '        TNT1 A 0 A_Light0;', '        Stop;']
    out += ['    Spawn:', '        TNT1 A -1;', '        Stop;', '    }', '}', '']
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
    if anim.get('flash'):
        out += sprite(f"{anim['flash_sprite']}A0", anim['_images'][anim['flash']['image']])
    if anim['kind'] == 'revolver':
        for _, spr, letter, image, _ in rig_sprites(anim):
            out += sprite(f'{spr}{letter}0', anim['_images'][image])
    return '\n'.join(out) + '\n'


def gen_sndinfo(anim):
    prefix = sound_prefix(anim)
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
        out += [f"        pl.GiveInventory('{a['class']}', 1);"]
        if a.get('ammo'):
            out += [f"        pl.GiveInventory('{a['ammo']['class']}', {a['ammo']['start_reserve']});"]
    for a in anims:
        out.append(f"        {{ let w = RFBenchWeapon(pl.FindInventory('{a['class']}')); if (w != null) w.Baseline = w.Loaded() + w.Reserve(); }}")
    out += [f"        if (pl.player != null) pl.player.PendingWeapon = Weapon(pl.FindInventory('{anims[0]['class']}'));",
            '        RFBench.Log("dotation Browning FAL pied-de-biche ' + ' '.join(a['class'] for a in anims) + '");', '    }', '',
            '    static clearscope String Source()', '    {']
    groups = {}
    for a in anims:
        key = 'provisoire' if a['_source']['kind'] == 'placeholder' else ('livraison + recul banc' if a.get('_presentation') and a['_presentation']['offsets'] else 'livraison')
        groups.setdefault(key, []).append(a['weapon'])
    text = ' ; '.join(','.join(ws) + ' ' + (key.upper() if key == 'provisoire' else key) for key, ws in groups.items())
    out += [f'        return "{text}";', '    }', '}', '']
    for a in [a for a in anims if a.get('ammo')]:
        out += [f"class {a['ammo']['class']} : Ammo", '{', '    Default', '    {', '        Inventory.Amount 1;',
                '        Inventory.MaxAmount 999;', '        Ammo.BackpackAmount 0;', '        Ammo.BackpackMaxAmount 999;',
                f"        Tag {zs_str(a['ammo']['tag'])};", '        +INVENTORY.IGNORESKILL', '    }',
                '    States', '    {', '    Spawn:', '        TNT1 A -1;', '        Stop;', '    }', '}', '']
    return '\n'.join(out)


MAPINFO = '''// RF2 arsenal test bench: the firing range, outside the campaign (no next chapter, no music).
gameinfo
{
    AddEventHandlers = "RFBenchHandler"
    StatusBarClass = "RFBenchStatusBar"
}

map ARSENAL "Banc d'essai - arsenal"
{
    levelnum = 99
    next = "ARSENAL"
    nointermission
    lightmode = 8
    music = ""
}

map BANCDEC1 "Banc d'essai - premieres decouvertes"
{
    levelnum = 98
    next = "BANCDEC2"
    nointermission
    lightmode = 8
    music = ""
}

map BANCDEC2 "Banc d'essai - apres changement de carte"
{
    levelnum = 97
    next = "BANCDEC1"
    nointermission
    lightmode = 8
    music = ""
}

DoomEdNums
{
    30950 = RFBenchTarget
    30951 = RFBenchRapidPickup
    30952 = RFBenchMR73Pickup
}
'''
LANGUAGE = '''[enu default]
RF_OBJ_ARSENAL_0 = "Banc d'essai : 4 Rapid, 5 MR73, R recharger. Hors campagne.";
RF_ARSENAL_DATE = "Banc d'essai - hors campagne";
RF_OBJ_BANCDEC1_0 = "Banc d'essai : ramasser les armes (repliques de Viktor). Hors campagne.";
RF_OBJ_BANCDEC2_0 = "Banc d'essai : doublons apres changement de carte. Hors campagne.";
RF_BENCH_VOIX_MANURHIN = "« Police, Milice, prête à tirer ! » [ricane]";
RF_BENCH_VOIX_CHASSEURS = "« Y a les bons et les mauvais chasseurs ! »";
'''
PICKUP_TEXTURES = ''.join(f'Sprite RFPK{l}0, 96, 64\n{{\n    XScale 4\n    YScale 4\n    Offset 48, 64\n    Patch "graphics/bench/pickup_{l}.png", 0, 0\n}}\n' for l in 'AB')
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


def collisions(files, base):
    """Sprite names of the module already used by the base game, the engine's own files or the IWAD, and module files
    that would shadow a file of the base (same path). The module must add, never replace."""
    import re, struct
    ours = sorted({m.group(1).upper() for m in re.finditer(r'^Sprite\s+"?([A-Za-z0-9\[\]\\]{4})', files['TEXTURES.bench'].decode(), re.M)})
    used = {}

    def note(name, where):
        used.setdefault(name[:4].upper(), set()).add(where)
    archives = [base] + sorted(ENGINE.parent.glob('*.pk3'))
    base_names = set()
    for arc in archives:
        with zipfile.ZipFile(arc) as z:
            for n in z.namelist():
                if arc == base:
                    base_names.add(n.lower())
                if n.lower().startswith('sprites/'):
                    note(Path(n).name, arc.name)
                if Path(n).name.lower().startswith('textures'):
                    for m in re.finditer(r'^\s*Sprite\s+"?(\w{4})', z.read(n).decode('utf-8', 'replace'), re.M | re.I):
                        note(m.group(1), f'{arc.name}:{n}')
    wad = IWAD.read_bytes()
    count, off = struct.unpack_from('<ii', wad, 4)
    inside = False
    for k in range(count):
        name = struct.unpack_from('<8s', wad, off + 16 * k + 8)[0].rstrip(b'\0').decode('ascii', 'replace')
        if name in ('S_START', 'SS_START'):
            inside = True
        elif name in ('S_END', 'SS_END'):
            inside = False
        elif inside:
            note(name, IWAD.name)
    sprite_hits = {p: sorted(used[p]) for p in ours if p in used}
    file_hits = sorted(n for n in files if n.lower() in base_names)
    return dict(sprites=ours, sprite_collisions=sprite_hits, file_collisions=file_hits)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--delivery', action='append', default=[], help="Astra delivery folder (repeatable)")
    ap.add_argument('--base', help='game pk3 to load under the module (default: frozen build of the current commit)')
    ap.add_argument('--allow-dirty', action='store_true')
    ap.add_argument('--scratch', help='only write the module to this path (development: no dated build, no launcher)')
    ap.add_argument('--presentation', help='bench presentation layer (JSON): code recoil offsets and short names applied on '
                    'top of the animation files, without changing the delivery')
    a = ap.parse_args()

    files = {}
    anims = [load_weapon(w, a.delivery, files) for w in WEAPONS]
    presentation = json.loads(Path(a.presentation).read_text(encoding='utf-8')) if a.presentation else {}
    for anim in anims:
        apply_presentation(anim, presentation.get(anim['weapon']), a.presentation)
    zs = ['version "4.14"', '#include "zscript/bench/bench_common.zs"', '#include "zscript/bench/bench_weapons.zs"', '']
    weapons_zs = ['// Generated by scripts/arsenal/build_bench.py - do not edit; see bench/arsenal/README.md.', '']
    textures = ['// Generated by scripts/arsenal/build_bench.py.', TARGET_TEXTURES, PICKUP_TEXTURES]
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
                           capacity=anim.get('capacity'), ballistics=anim.get('ballistics'), contact=anim.get('contact'), provisional=anim.get('provisional', False),
                           presentation=anim.get('_presentation')))
    weapons_zs.append(gen_setup(anims))
    voices = load_voices(a.delivery, files)
    voice_zs, voice_snd = gen_voices(voices)
    weapons_zs.append(voice_zs)
    sndinfo.append(voice_snd)
    tmp = ROOT / 'build' / 'arsenal'
    placeholders.make_target(tmp / 'target.png')
    files['graphics/bench/target.png'] = (tmp / 'target.png').read_bytes()
    files['ZSCRIPT.bench'] = '\n'.join(zs).encode()
    files['zscript/bench/bench_common.zs'] = (BENCH / 'zscript' / 'bench_common.zs').read_bytes()
    files['zscript/bench/bench_weapons.zs'] = '\n'.join(weapons_zs).encode()
    files['TEXTURES.bench'] = '\n'.join(textures).encode()
    files['SNDINFO.bench'] = '\n'.join(sndinfo).encode()
    files['MAPINFO.bench'] = MAPINFO.encode()
    files['LANGUAGE.bench'] = LANGUAGE.encode('utf-8')
    files['maps/ARSENAL.wad'] = arsenal_map.wad_bytes()
    for mapname, data in arsenal_map.discovery_wads().items():
        files[f'maps/{mapname}.wad'] = data
    for letter, label, colour in (('A', 'W03', (112, 74, 42)), ('B', 'W04', (60, 64, 70))):
        placeholders.make_pickup(tmp / f'pickup_{letter}.png', label, colour)
        files[f'graphics/bench/pickup_{letter}.png'] = (tmp / f'pickup_{letter}.png').read_bytes()

    base = Path(a.base).resolve() if (a.scratch and a.base) else (None if a.scratch else base_pk3(a))
    clash = collisions(files, base) if base else None
    if clash and (clash['sprite_collisions'] or clash['file_collisions']):
        raise SystemExit('collisions avec la base, le moteur ou l\'IWAD : ' + json.dumps(clash, ensure_ascii=False))
    if a.scratch:
        with zipfile.ZipFile(a.scratch, 'w', zipfile.ZIP_DEFLATED) as z:
            for name in sorted(files):
                z.writestr(name, files[name])
        print('module (developpement) :', a.scratch, '; collisions :', 'non controlees (sans --base)' if clash is None else 'aucune')
        return 0
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
                engine=str(ENGINE), iwad=str(IWAD), collisions=clash, weapons=report,
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
