#!/usr/bin/env python3
"""Intake of a transition page (planche): check its descriptor against its image, and declare it to the game.

A page is delivered as a folder holding planche.json and the page image (contract:
docs/production/handoff/RF2_20261002/DEMANDES_ASTRA/CONTRAT_TRANSITIONS.md):

    {"id": "RF01_RF02", "image": "graphics/comics/RF01_RF02.png", "dimensions": [1920, 1080],
     "cases": [{"id": "...", "rect": [x, y, w, h]}, ...],
     "legendes": [{"id": "...", "texte": "...", "zone": [x, y, w, h], "apres_case": "<id of a case>"}, ...]}

Checks: the image is 1920 x 1080; three to five panels, inside the page, not overlapping, in reading order; every
caption follows an existing panel, its zone is inside the page and its text is a single short line; a zone lying in a
black band of the page is declared "band" (cream text on the band), another one gets the cream box over the art.

    python scripts/production/comic_intake.py check <folder> [<folder> ...]     report, and the block to declare
    python scripts/production/comic_intake.py apply <folder> --lot "<lot name>"  write src/COMICDEF and src/LANGUAGE
    python scripts/production/comic_intake.py verify <folder> [...]            the game's declaration equals the
                                                                                 descriptor (regression of the intake)

apply never copies the image: it goes through scripts/import_astra_lot.py like any delivered file (base hash check).
The page's maps come from its id (<FROM>_<TO>), or from the fields "de" and "vers" of the descriptor.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMICDEF = ROOT / 'src' / 'COMICDEF'
LANGUAGE = ROOT / 'src' / 'LANGUAGE'
PAGE = (1920, 1080)
BAND_MIN = 126                  # px: the least height of a black band that takes a caption
LONG_TEXT = 150                 # characters: beyond, the game shrinks the caption until it fits


def find_image(folder, desc):
    """The page image of a delivered folder: the name of the descriptor's target, then any single page-sized PNG."""
    from PIL import Image
    name = Path(desc.get('image', '')).name
    cands = [p for p in folder.rglob('*.png') if p.name == name] or list(folder.rglob('*.png'))
    sized = []
    for p in cands:
        with Image.open(p) as im:
            if im.size == PAGE:
                sized.append(p)
    return sized[0] if len(sized) >= 1 and (len(sized) == 1 or sized[0].name == name) else (cands[0] if cands else None)


def overlap(a, b):
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(w, 0) * max(h, 0)


def inside(r):
    return r[0] >= 0 and r[1] >= 0 and r[2] > 0 and r[3] > 0 and r[0] + r[2] <= PAGE[0] and r[1] + r[3] <= PAGE[1]


def is_band(image, zone):
    """True when the caption zone lies on black (a band of the page), measured on the image."""
    from PIL import Image, ImageStat
    with Image.open(image) as im:
        crop = im.convert('L').crop((zone[0], zone[1], zone[0] + zone[2], zone[1] + zone[3]))
        st = ImageStat.Stat(crop)
        hist = crop.histogram()
    dark = sum(hist[:24]) / max(sum(hist), 1)
    return st.mean[0] < 16 and dark > 0.9


def examine(folder):
    """-> (descriptor, image path, errors, warnings, declaration lines, {language key: text})."""
    folder = Path(folder)
    errors, warnings = [], []
    f = folder / 'planche.json'
    if not f.is_file():
        return None, None, [f'{folder}: planche.json absent'], [], [], {}
    desc = json.loads(f.read_text(encoding='utf-8'))
    sid = str(desc.get('id', '')).upper()
    if not re.fullmatch(r'[A-Z0-9]+_[A-Z0-9]+', sid):
        errors.append(f'id "{sid}" : attendu <CARTE DE DEPART>_<CARTE D ARRIVEE>, par exemple RF07_RF08')
    src, dst = (desc.get('de'), desc.get('vers')) if desc.get('de') and desc.get('vers') else (sid.split('_') + ['', ''])[:2]
    target = desc.get('image', f'graphics/comics/{sid}.png')
    if target != f'graphics/comics/{sid}.png':
        warnings.append(f'image "{target}" : la destination du jeu est graphics/comics/{sid}.png')
    if list(desc.get('dimensions', [])) != list(PAGE):
        errors.append(f'dimensions {desc.get("dimensions")} : la page de jeu fait 1920 x 1080 (le maitre peut etre plus grand, pas l export)')
    image = find_image(folder, desc)
    if image is None:
        errors.append('aucune image PNG dans le dossier')
    else:
        from PIL import Image
        with Image.open(image) as im:
            if im.size != PAGE:
                errors.append(f'{image.name} : {im.size[0]} x {im.size[1]} px, attendu 1920 x 1080')
            if im.mode not in ('RGB', 'RGBA', 'P', 'L'):
                warnings.append(f'{image.name} : mode {im.mode}')
    cases = desc.get('cases', [])
    if not 3 <= len(cases) <= 5:
        warnings.append(f'{len(cases)} cases : le contrat en prevoit trois a cinq')
    ids = [c.get('id') for c in cases]
    if len(set(ids)) != len(ids):
        errors.append('deux cases portent le meme id')
    for c in cases:
        if not inside(c['rect']):
            errors.append(f'case {c.get("id")} hors de la page : {c["rect"]}')
    for i, a in enumerate(cases):
        for b in cases[i + 1:]:
            if overlap(a['rect'], b['rect']):
                errors.append(f'les cases {a.get("id")} et {b.get("id")} se recouvrent')
    covered = sum(c['rect'][2] * c['rect'][3] for c in cases) / (PAGE[0] * PAGE[1])
    lines = [f'scene {sid} {src} {dst} graphics/comics/{sid}.png'] + ['panel %d %d %d %d' % tuple(c['rect']) for c in cases]
    texts = {}
    legends = desc.get('legendes', [])
    if not legends:
        warnings.append('aucune legende : la planche se lit sans texte')
    for n, lg in enumerate(legends, 1):
        key = f'RF_COMIC_{sid}_{n}'
        text = ' '.join(str(lg.get('texte', '')).split())
        if not text:
            errors.append(f'legende {lg.get("id")} vide')
        if len(text) > LONG_TEXT:
            warnings.append(f'legende {lg.get("id")} : {len(text)} caracteres, elle sera reduite pour tenir dans sa zone')
        if lg.get('apres_case') not in ids:
            errors.append(f'legende {lg.get("id")} : apres_case "{lg.get("apres_case")}" n est pas une case')
            continue
        zone = lg.get('zone', [])
        if len(zone) != 4 or not inside(zone):
            errors.append(f'legende {lg.get("id")} : zone hors de la page : {zone}')
            continue
        band = bool(image) and not errors and is_band(image, zone)
        if band and zone[3] > 0 and image:
            if PAGE[1] * (1 - covered) < BAND_MIN * PAGE[0] / PAGE[0] and covered > 0.999:
                warnings.append('la bande noire est plus basse que 126 px')
        if not band and any(overlap(zone, c['rect']) == 0 for c in cases) and all(overlap(zone, c['rect']) == 0 for c in cases):
            warnings.append(f'legende {lg.get("id")} : zone hors des cases et pas sur du noir')
        lines.append('caption %d $%s %d %d %d %d%s' % (ids.index(lg['apres_case']) + 1, key, *zone, ' band' if band else ''))
        texts[key] = text
    return desc, image, errors, warnings, lines, texts


def current_block(sid):
    """The declaration lines of a scene in src/COMICDEF (without comments), or []."""
    out, on = [], False
    for line in COMICDEF.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if s.startswith('scene '):
            on = s.split()[1] == sid
        if on and s and not s.startswith('#'):
            out.append(' '.join(s.split()))
    return out


def language_value(key):
    m = re.search(r'^' + re.escape(key) + r'\s*=\s*"(.*)";\s*$', LANGUAGE.read_text(encoding='utf-8'), re.M)
    return m.group(1).replace('\\"', '"') if m else None


def write_keeping_endings(path, text):
    crlf = b'\r\n' in path.read_bytes()
    text = text.replace('\r\n', '\n')
    path.write_bytes((text.replace('\n', '\r\n') if crlf else text).encode('utf-8'))


def apply(sid, lines, texts, lot):
    # COMICDEF: the scene's block (its comment line and its declaration) replaced, or appended
    text = COMICDEF.read_text(encoding='utf-8').replace('\r\n', '\n')
    blocks = text.split('\n\n')
    head = f'# {lot}, planche.json: {sum(1 for l in lines if l.startswith("panel "))} panels, ' \
           f'{sum(1 for l in lines if l.startswith("caption "))} caption(s)'
    new = head + '\n' + '\n'.join(lines)
    for i, b in enumerate(blocks):
        if re.search(r'^scene ' + re.escape(sid) + r'\s', b, re.M):
            blocks[i] = new + ('\n' if b.endswith('\n') else '')
            break
    else:
        blocks[-1] = blocks[-1].rstrip('\n')
        blocks.append(new + '\n')
    write_keeping_endings(COMICDEF, '\n\n'.join(blocks))
    # LANGUAGE: the keys replaced where they are, new ones after the last caption of the pages
    lang = LANGUAGE.read_text(encoding='utf-8').replace('\r\n', '\n').split('\n')
    stale = [i for i, l in enumerate(lang) if re.match(r'RF_COMIC_' + re.escape(sid) + r'_\d+\s*=', l)]
    at = stale[0] if stale else max(i for i, l in enumerate(lang) if l.startswith('RF_COMIC_')) + 1
    for i in reversed(stale):
        del lang[i]
    for k, (key, value) in enumerate(texts.items()):
        lang.insert(at + k, '%s = "%s";' % (key, value.replace('"', '\\"')))
    write_keeping_endings(LANGUAGE, '\n'.join(lang))


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ('check', 'apply', 'verify'):
        sys.exit(__doc__)
    mode = sys.argv[1]
    args = sys.argv[2:]
    lot = None
    if '--lot' in args:
        lot = args[args.index('--lot') + 1]
        args = [a for i, a in enumerate(args) if a != '--lot' and (i == 0 or args[i - 1] != '--lot')]
    bad = 0
    for folder in args:
        desc, image, errors, warnings, lines, texts = examine(folder)
        sid = str((desc or {}).get('id', '?')).upper()
        print(f'== {sid}  ({folder})')
        if image:
            print(f'   image : {image}')
        for w in warnings:
            print(f'   REMARQUE  {w}')
        for e in errors:
            print(f'   REFUS     {e}')
        if errors:
            bad += 1
            continue
        if mode == 'check':
            print('   declaration :')
            for l in lines:
                print('     ' + l)
            for k, v in texts.items():
                print(f'     {k} = "{v}";')
        elif mode == 'verify':
            cur = current_block(sid)
            same = cur == lines and all(language_value(k) == v for k, v in texts.items())
            print('   ' + ('IDENTIQUE a la declaration du jeu' if same else 'DIFFERENT de la declaration du jeu'))
            if not same:
                bad += 1
                for a, b in zip(lines + [''] * len(cur), cur + [''] * len(lines)):
                    if a != b:
                        print(f'     descripteur : {a}\n     jeu         : {b}')
                for k, v in texts.items():
                    if language_value(k) != v:
                        print(f'     {k}\n       descripteur : {v}\n       jeu         : {language_value(k)}')
        else:
            apply(sid, lines, texts, lot or Path(folder).name)
            print('   ecrit : src/COMICDEF, src/LANGUAGE (image : par scripts/import_astra_lot.py)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
