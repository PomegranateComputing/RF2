#!/usr/bin/env python3
"""Check a lot before it is handed over (or before import): the manifest the importer reads (schema 1), the files it
names, and what would make the engine show something else than intended.

For each entry of manifest.json: the delivered file exists and matches its sha256; its destination is under src/ and
is not a map, code or a definition lump; the base it was made against is still the file in place (no drift); for a
PNG that replaces a PNG: same pixel size unless the entry says so ("resize": true, agreed with Opus), a grAb chunk when
the base has one (a sprite without its anchor floats or sinks), RGBA kept when the base has transparency. Then
SHA256SUMS.txt: present, LF line endings, every line verified.

--write fills the "sha256" of entries left as A_CALCULER... from the files, and (re)writes SHA256SUMS.txt in LF.
The lot is never copied anywhere: this only reads (and, with --write, completes the lot's own manifest and sums).

Usage: python scripts/production/astra_lot_check.py <lot folder> [--write]
Exit code 0 when nothing blocks the import.
"""
import hashlib, json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'src'


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def png_info(p):
    """(width, height, colour type, grAb or None) of a PNG, None when the file is not one."""
    b = Path(p).read_bytes()
    if b[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    w, h = struct.unpack('>II', b[16:24])
    ctype, grab, i = b[25], None, 8
    while i < len(b) - 12:
        n, typ = struct.unpack('>I4s', b[i:i + 8])
        if typ == b'grAb':
            grab = struct.unpack('>ii', b[i + 8:i + 16])
        if typ == b'IDAT':
            break
        i += 12 + n
    return w, h, ctype, grab


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--write' in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    lot = Path(args[0]).resolve()
    mp = lot / 'manifest.json'
    if not mp.is_file():
        sys.exit(f'pas de manifest.json dans {lot}')
    man = json.loads(mp.read_text(encoding='utf-8'))
    problems, notes = [], []
    if man.get('schema') != 1:
        problems.append(f"schema = {man.get('schema')!r} : l'importateur attend 1")
    if not man.get('batch_id') or 'A_RENOMMER' in str(man.get('batch_id')):
        problems.append('batch_id a renseigner (LOT_VERSION, ex. E01_ORDY_V05)')
    changed = False
    for e in man.get('files', []):
        name = e.get('target_relpath', '?')
        f = lot / e.get('file', '')
        if not f.is_file():
            problems.append(f'{name} : fichier livre absent ({e.get("file")})')
            continue
        got = sha256(f)
        if not e.get('sha256') or str(e['sha256']).startswith('A_CALCULER'):
            if write:
                e['sha256'] = got
                changed = True
            else:
                problems.append(f'{name} : sha256 a calculer (relancer avec --write)')
        elif e['sha256'] != got:
            problems.append(f'{name} : le fichier ne correspond pas a son sha256 du manifeste')
        tp = Path(name)
        if tp.is_absolute() or '..' in tp.parts:
            problems.append(f'{name} : destination hors de src/')
            continue
        if name.startswith(('maps/', 'zscript/')) or '/' not in name:
            problems.append(f'{name} : carte, code ou definition : a proposer en texte, pas en fichier')
            continue
        dest = SRC / name
        base = e.get('base_sha256')
        if dest.is_file():
            now = sha256(dest)
            if now == got:
                notes.append(f'{name} : identique au fichier en place')
            elif base is None:
                problems.append(f'{name} : la destination existe, base_sha256 manquant')
            elif base != now:
                problems.append(f'{name} : la destination a change depuis la base du lot (rapprocher les versions avec Opus)')
            a, b = png_info(dest), png_info(f)
            if a and b:
                if (a[0], a[1]) != (b[0], b[1]) and not e.get('resize'):
                    problems.append(f'{name} : {b[0]}x{b[1]} px au lieu de {a[0]}x{a[1]} (meme taille, ou "resize": true convenu avec Opus)')
                if a[3] and not b[3]:
                    problems.append(f'{name} : chunk grAb absent (ancrage de la base : {a[3][0]},{a[3][1]})')
                elif a[3] and b[3] and a[3] != b[3]:
                    notes.append(f'{name} : ancrage {b[3][0]},{b[3][1]} (base {a[3][0]},{a[3][1]})')
                if a[2] in (4, 6) and b[2] not in (4, 6):
                    problems.append(f'{name} : la base est en RGBA (transparence), le fichier livre ne l\'est pas')
        elif base:
            problems.append(f'{name} : base_sha256 donne mais aucune destination en place')
        else:
            notes.append(f'{name} : fichier neuf (destination a confirmer par Opus)')
    if changed:
        mp.write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    sums = lot / 'SHA256SUMS.txt'
    if write:
        lines = [f'{sha256(p)}  {p.relative_to(lot).as_posix()}' for p in sorted(lot.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS.txt']
        sums.write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    if not sums.is_file():
        problems.append('SHA256SUMS.txt absent (relancer avec --write)')
    else:
        raw = sums.read_bytes()
        if b'\r\n' in raw:
            problems.append('SHA256SUMS.txt en CRLF : le contrat demande LF')
        for line in raw.decode('utf-8').splitlines():
            if line.strip():
                h, rel = line.split(None, 1)
                p = lot / rel.lstrip('*').strip()
                if not p.is_file() or sha256(p) != h:
                    problems.append(f'SHA256SUMS.txt : {rel.strip()} absent ou different')
    for n in notes:
        print('note :', n)
    for p in problems:
        print('BLOQUANT :', p)
    print(f"{man.get('batch_id', lot.name)} : {len(man.get('files', []))} fichiers, {len(problems)} point(s) bloquant(s), {len(notes)} note(s)")
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
