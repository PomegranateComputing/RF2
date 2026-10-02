#!/usr/bin/env python3
"""Before / after sheets of the door pass, one per family of defects, from the views of door_views.py (the same
element found in both sets by its place and the side it is seen from) and the four states of door_motion.py.

Usage: python scripts/production/door_sheets.py <pass dir> <out dir>
  <pass dir> holds vues_avant/, vues_apres/, facades_avant/, facades_apres/, mouvement/ (see docs/RF2_PORTES_*.md).
"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mapkit'))
import doors  # noqa: E402

W, H = 640, 360


def font(size):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/arial.ttf', size)
    except OSError:
        return ImageFont.load_default()


def family(r):
    d = ' '.join(r['defects'])
    if r['kind'] == 'facade':
        return ('F1_facades_de_Paris_rideau_ou_porte_coupe_en_bout_de_mur' if 'rez-de' in d else
                'F2_facades_foraines_fragment_sur_un_retour_de_mur' if 'fragment' in d else 'F3_facades_foraines_travee_coupee')
    if r['kind'] == 'static':
        return 'S1_portes_fixes_repetees' if 'repete' in d else 'S2_portes_fixes_coupees'
    if 'repete' in d and 'largeur' in d and 'decalage' in d:
        return 'P3_porte_a_badge_repetee_et_decalee'
    if 'repete' in d:
        return 'P1_portes_repetees_en_hauteur'
    return 'P2_portes_coupees'


def find(root, key):
    mp, label = key.split('/', 1)
    hits = list((root / mp).glob(f'*_{label}.png'))
    return hits[0] if hits else None


def match(b, after):
    best, bd = None, 25.0
    for k, a in after.items():
        if a['map'] != b['map'] or a['kind'] != b['kind'] or not k.endswith('_face'):
            continue
        if a['normal'][0] * b['normal'][0] + a['normal'][1] * b['normal'][1] < 0.9:
            continue
        d = math.hypot(a['mid'][0] - b['mid'][0], a['mid'][1] - b['mid'][1])
        if d < bd:
            best, bd = k, d
    return best


def sheet(rows, title, out):
    if not rows:
        return
    f, fs = font(20), font(15)
    img = Image.new('RGB', (2 * W + 30, 44 + len(rows) * (H + 30)), (24, 24, 26))
    d = ImageDraw.Draw(img)
    d.text((10, 10), title, font=f, fill=(235, 235, 235))
    d.text((W - 60, 14), 'AVANT', font=fs, fill=(255, 210, 90))
    d.text((2 * W - 50, 14), 'APRES', font=fs, fill=(120, 230, 120))
    for i, (caption, pa, pb) in enumerate(rows):
        y = 44 + i * (H + 30)
        d.text((10, y), caption[:170], font=fs, fill=(220, 200, 150))
        for col, p in enumerate((pa, pb)):
            if p is not None:
                img.paste(Image.open(p).convert('RGB').resize((W, H)), (10 + col * (W + 10), y + 24))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=84)
    print(out.name, len(rows), 'paires')


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    for before_dir, after_dir, same_labels in (('vues_avant', 'vues_apres', False), ('facades_avant', 'facades_apres', True)):
        ib = json.loads((root / before_dir / 'index.json').read_text(encoding='utf-8'))
        ia = json.loads((root / after_dir / 'index.json').read_text(encoding='utf-8'))
        fams = {}
        for k, b in ib.items():
            if not k.endswith('_face') or not b.get('defects'):
                continue
            if b['kind'] == 'mechanism' and not doors.is_door(b['tex']):
                continue                               # a door dressed as its wall: camouflage, not a defect
            ka = k if same_labels else match(b, ia)
            pa, pb = find(root / before_dir, k), (find(root / after_dir, ka) if ka else None)
            if pa is None or pb is None:
                continue
            cap = f"{b['map']} - {b['tex']} sur {b['W']:g} x {b['H']:g} u : {' ; '.join(b['defects'])}"
            fams.setdefault(family(b), []).append((b['map'], b['tex'], cap, pa, pb))
        for fam, items in sorted(fams.items()):
            # up to six pairs, spread over maps and textures
            picked, seen = [], set()
            for item in items:
                key = (item[0], item[1])
                if key not in seen:
                    seen.add(key)
                    picked.append(item)
            for item in items:
                if len(picked) >= 6:
                    break
                if item not in picked:
                    picked.append(item)
            sheet([(c, a, b) for (_, _, c, a, b) in picked[:6]], fam.replace('_', ' '), out / f'{fam}.jpg')
    # the four states
    rows = []
    for mdir in sorted((root / 'mouvement').iterdir()):
        mv = mdir / 'mouvement.json'
        if not mv.exists():
            continue
        for r in json.loads(mv.read_text(encoding='utf-8')):
            if r['moved']:
                rows.append((mdir.name, r))
    # doors with a door image first, at most two per map, the blockouts counted as one family
    picked, per = [], {}
    for mp, r in rows:
        group = 'blockouts' if mp == 'RF03' or mp > 'RF07' else mp
        tex = r['door'].split('_')[3]
        if not (tex.startswith('RD') or doors.is_door(tex)) or per.get(group, 0) >= 2 or len(picked) >= 8:
            continue
        if any(p[1]['door'].split('_')[3] == tex and p[0] == mp for p in picked):
            continue
        per[group] = per.get(group, 0) + 1
        picked.append((mp, r))
    f, fs = font(20), font(15)
    w, h = 480, 270
    img = Image.new('RGB', (4 * w + 50, 44 + len(picked) * (h + 30)), (24, 24, 26))
    d = ImageDraw.Draw(img)
    d.text((10, 10), 'Portes en mouvement : fermee, en course, ouverte, en fermeture (ouverture du vantail en unites)', font=f, fill=(235, 235, 235))
    for i, (mp, r) in enumerate(picked):
        y = 44 + i * (h + 30)
        d.text((10, y), f"{mp} - {r['door']} : ouverture {r['opening']}", font=fs, fill=(220, 200, 150))
        for j, ph in enumerate(('1_fermee', '2_en_course', '3_ouverte', '4_en_fermeture')):
            p = root / 'mouvement' / mp / f"{r['door']}_{ph}.png"
            if p.exists():
                img.paste(Image.open(p).convert('RGB').resize((w, h)), (10 + j * (w + 10), y + 24))
    img.save(out / 'M_portes_en_mouvement.jpg', quality=84)
    print('M_portes_en_mouvement.jpg', len(picked), 'portes')


if __name__ == '__main__':
    main()
