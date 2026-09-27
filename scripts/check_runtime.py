#!/usr/bin/env python3
"""Static consistency checks of src/ before building the PK3 (no engine needed).

- every $KEY used by ZScript, MENUDEF, MAPINFO, LOCKDEFS exists in LANGUAGE;
- every sprite frame used in ZScript states exists (sprites/ file or TEXTURES Sprite);
- every SNDINFO entry points at an existing file, $random members and ZScript "rf/..." sounds exist;
- every texture named in the built production TEXTMAPs (build/RFxx_TEXTMAP.txt) is defined.

Usage: python scripts/check_runtime.py        (exit 1 on any problem)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
ENGINE_KEYS = {'MUSIC_READ_M', 'MUSIC_RUNNIN', 'MNU_EPISODE', 'LOADNET', 'DOSY', 'PRESSYN'}


def read(p):
    return p.read_text(encoding='utf-8', errors='replace')


def zscript_files():
    return sorted((SRC / 'zscript').rglob('*.zs'))


def check_language():
    defined = set(re.findall(r'^\s*([A-Z0-9_]+)\s*=', read(SRC / 'LANGUAGE'), re.M))
    used = set()
    for p in zscript_files() + [SRC / 'MENUDEF', SRC / 'MAPINFO', SRC / 'LOCKDEFS']:
        t = read(p)
        used |= set(re.findall(r'\$([A-Z][A-Z0-9_]+)', t))
        used |= set(re.findall(r'lookup,\s*"([A-Z0-9_]+)"', t))
    # RFNote builds RF_NOTE_<args[0]> at runtime: check the notes placed in production maps
    for tm in (ROOT / 'build').glob('RF??_TEXTMAP.txt'):
        for block in re.findall(r'thing\s*\{([^}]*)\}', read(tm)):
            if 'type = 30621;' in block:
                arg = re.search(r'arg0 = (\d+);', block)
                used.add(f'RF_NOTE_{arg.group(1) if arg else 0}')
    # A key ending in '_' is the prefix of keys built with a number ("$RF_SKILL_HINT_%d"): at least one must exist.
    prefixes = {k for k in used if k.endswith('_')}
    missing = [k for k in sorted(used - defined - ENGINE_KEYS - prefixes)]
    missing += [k + '*' for k in sorted(prefixes) if not any(d.startswith(k) for d in defined)]
    return [f'LANGUAGE: missing {k}' for k in missing]


def check_sprites():
    have = set()
    for p in (SRC / 'sprites').rglob('*.png'):
        n = p.stem.upper()
        if len(n) >= 6:
            have.add((n[:4], n[4]))
            if len(n) >= 8:
                have.add((n[:4], n[6]))
    for t in (q for q in SRC.glob('TEXTURES*') if q.is_file()):
        for m in re.finditer(r'^\s*Sprite\s+([A-Z0-9]{4})([A-Z])\d', read(t), re.M | re.I):
            have.add((m.group(1).upper(), m.group(2).upper()))
    problems = []
    for p in zscript_files():
        for i, line in enumerate(read(p).splitlines(), 1):
            m = re.match(r'^\s{4,}([A-Z0-9]{4})\s+([A-Z\[\]\\#]+)\s+-?\d+', line)
            if not m or m.group(1) == 'TNT1':
                continue
            for f in m.group(2):
                if f.isalpha() and (m.group(1), f) not in have:
                    problems.append(f'SPRITE: {m.group(1)} {f} missing ({p.name}:{i})')
    return problems


def check_sounds():
    defined, randoms = {}, {}
    for line in read(SRC / 'SNDINFO').splitlines():
        line = line.split('//')[0].strip()
        m = re.match(r'^\$random\s+(\S+)\s*\{([^}]*)\}', line)
        if m:
            randoms[m.group(1).lower()] = m.group(2).split()
            continue
        m = re.match(r'^([^$\s]\S*)\s+"([^"]+)"', line)
        if m:
            defined[m.group(1).lower()] = m.group(2)
    problems = [f'SOUND: {k} -> missing file {v}' for k, v in defined.items() if not (SRC / v).exists()]
    names = set(defined) | set(randoms)
    problems += [f'SOUND: $random {k} member {x} undefined' for k, xs in randoms.items() for x in xs if x.lower() not in names]
    for p in zscript_files():
        for s in set(re.findall(r'"(rf/[a-z0-9_/]+)"', read(p), re.I)):
            if s.lower() not in names:
                problems.append(f'SOUND: {s} used in {p.name} but undefined')
    return problems


def check_map_textures():
    have = {'F_SKY1', '-'}
    for q in (x for x in SRC.glob('TEXTURES*') if x.is_file()):
        have |= set(m.upper() for m in re.findall(r'^\s*(?:Texture|Flat|WallTexture|Graphic)\s+"?([A-Za-z0-9_]+)"?', read(q), re.M))
    for d in ('textures', 'flats', 'patches'):
        have |= {p.stem.upper() for p in (SRC / d).rglob('*.png')}
    problems = []
    for tm in sorted((ROOT / 'build').glob('RF??_TEXTMAP.txt')):
        used = set(re.findall(r'texture(?:top|middle|bottom|floor|ceiling)\s*=\s*"([^"]+)"', read(tm)))
        problems += [f'TEXTURE: {tm.stem[:4]} uses undefined {u}' for u in sorted(used) if u.upper() not in have]
    return problems


def main():
    problems = check_language() + check_sprites() + check_sounds() + check_map_textures()
    for p in problems:
        print(p)
    print(f'check_runtime: {"PASS" if not problems else f"FAIL ({len(problems)})"}')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
