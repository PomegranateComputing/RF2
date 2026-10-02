#!/usr/bin/env python3
"""The current base handed to Astra for the art order of 02/10/2026 (pack RF2_ASTRA_ART_MASSIF_20261002): for each
priority lot, the files really in the game with their destination, pixels, anchor (grAb), world size, sha256 and
origin, a manifest in the importer's schema (scripts/import_astra_lot.py, schema 1) with the base hashes filled in,
and copies of the files themselves as references.

Everything is read from src/ at the moment of the run: nothing is invented, and a destination that changes later
simply shows as a base drift at import.

Usage: python scripts/production/astra_contracts.py
Writes docs/production/handoff/RF2_20261002/DEMANDES_ASTRA/ (tables, manifests, the rotation sheet) and
incoming/astra/DEMANDES_OPUS_20261002/ (the same, plus REFERENCES/ with copies of the files).
"""
import csv, glob, hashlib, json, re, shutil, struct, subprocess, sys, zlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'src'
DOCS = ROOT / 'docs' / 'production' / 'handoff' / 'RF2_20261002' / 'DEMANDES_ASTRA'
INBOX = ROOT / 'incoming' / 'astra' / 'DEMANDES_OPUS_20261002'

# lot of the pack -> (title, [glob under src/], notes)
LOTS = {
    'E01_ORDY': ("Infirmier RFOrderly : 104 images, corps final par modèle", ['sprites/enemies/ORDY*.png', 'models/rf2_art_01/orderly.obj', 'models/rf2_art_01/orderly_skin.png']),
    'E02_BRCD': ("Brancardier RFBrancardier : 120 images, corps final par modèle", ['sprites/enemies/BRCD*.png', 'models/rf2_art_01/brancardier.obj', 'models/rf2_art_01/brancardier_skin.png']),
    'E03_PREG': ("Porte-registre RFPorteRegistre : 96 images, liasse PRGS, corps final par modèle", ['sprites/enemies/PREG*.png', 'sprites/enemies/PRGS*.png', 'models/rf2_art_01/porte_registre.obj', 'models/rf2_art_01/porte_registre_skin.png']),
    'V01_VIKTOR': ("Reflets de Viktor : vitrine de RF02 (R2F8), miroirs de la salle de danse (R4V2 blouse grise, R4V3 chemise et badge)", ['sprites/rf02_figures/R2F8*.png', 'sprites/rf04/R4V2*.png', 'sprites/rf04/R4V3*.png']),
    'F01_FIGURES': ("Figures humaines : civils de RF02 (R2F1-R2F7, R2B1-R2B4), gardien de la guérite (R4G1)", ['sprites/rf02_figures/R2F[1-7]*.png', 'sprites/rf02_figures/R2B*.png', 'sprites/rf04/R4G1*.png']),
    'A02_RF05': ("Sous-station RF05 : surfaces, machines et leurs états", ['patches/rf04/RF5_*.png', 'sprites/rf04/R5*.png']),
    'A03_LUNA': ("Luna Park RF04/RF05 : surfaces, objets, ciel", ['patches/rf04/RF4_*.png', 'sprites/rf04/R4JB*.png', 'sprites/rf04/R4SH*.png', 'textures/RF4SKY.png']),
    'A04_RF06': ("Couloir RF06 : murs, sols, numéros, ERREUR Ø, le jour", ['patches/rf06/*.png']),
    'R01_RF02': ("RF02 : objets et surfaces (hors figures)", ['patches/rf02/*.png', 'sprites/rf02/*.png']),
    'R02_RF01': ("RF01 : décals d'usure", ['graphics/decals/*.png']),
    'J01_J02_JERMA': ("Jerma RF07 : tout est provisoire (Opus)", ['patches/rf07/*.png', 'sprites/rf07/*.png']),
    'T01_PLANCHES': ("Planches de transition : cinq pages en place", ['graphics/comics/*.png']),
}
REFERENCES = {      # read-only references: nothing to replace here
    'VIKTOR_HUD': ['graphics/hud/viktor/*.png'],
    'VIKTOR_BRAS_ARMES': ['graphics/weapons/browning/*.png', 'graphics/weapons/fal/*.png', 'graphics/weapons/crowbar/*.png'],
}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def grab(p):
    """(x, y) of a PNG's grAb chunk (the sprite's anchor: its offset in pixels), or None."""
    b = Path(p).read_bytes()
    i = 8
    while i < len(b) - 12:
        n, typ = struct.unpack('>I4s', b[i:i + 8])
        if typ == b'grAb':
            return struct.unpack('>ii', b[i + 8:i + 16])
        if typ == b'IDAT':
            return None
        i += 12 + n
    return None


def texture_defs():
    """patch path (under src/, lower case) -> (texture name, world w, world h, px per unit)."""
    out = {}
    for tf in sorted(SRC.glob('TEXTURES.*')):
        t = tf.read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r'(Texture|Flat|WallTexture|Sprite|Graphic)\s+"?(\w+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{(.*?)\n\}', t, re.S):
            xs = re.search(r'XScale\s+([\d.]+)', m.group(5))
            ys = re.search(r'YScale\s+([\d.]+)', m.group(5))
            xs, ys = (float(xs.group(1)) if xs else 1.0), (float(ys.group(1)) if ys else 1.0)
            for p in re.findall(r'Patch\s+"([^"]+)"', m.group(5)):
                key = p.lower() if p.lower().endswith('.png') else p.lower() + '.png'
                out.setdefault(key, (m.group(2), m.group(1), int(m.group(3)) / xs, int(m.group(4)) / ys, xs))
    return out


def sprite_scales():
    """sprite prefix -> (class, Scale) from the actors' Default blocks (own Scale only; inherited ones are not resolved)."""
    out = {}
    for zf in sorted((SRC / 'zscript').rglob('*.zs')):
        t = zf.read_text(encoding='utf-8', errors='replace')
        classes = {}
        for m in re.finditer(r'\nclass\s+(\w+)\s*(?::\s*(\w+))?[^{]*\{(.*?)(?=\nclass\s|\Z)', '\n' + t, re.S):
            body = m.group(3)
            sc = re.search(r'\bScale\s+([\d.]+)\s*;', body)
            classes[m.group(1)] = (m.group(2), float(sc.group(1)) if sc else None, body)
        for name, (parent, sc, body) in classes.items():
            k = parent
            while sc is None and k in classes:          # a Scale inherited from a parent of the same file
                sc, k = classes[k][1], classes[k][0]
            for pref in set(re.findall(r'[\s{:]([A-Z0-9]{4})\s+[A-Z\[\]\\]+\s+-?\d+', body)):
                out.setdefault(pref, (name, sc, zf.name))
    return out


def origins():
    """target (src/...) -> the lot that delivered the file now in place, from the import records."""
    out = {}
    for f in sorted((ROOT / 'docs' / 'production' / 'handoff').rglob('IMPORT_*.json'), key=lambda p: p.stat().st_mtime):
        try:
            rec = json.loads(f.read_text(encoding='utf-8'))
        except Exception:
            continue
        for e in rec.get('files', []):
            if e.get('state') in ('remplace_base_conforme', 'nouveau', 'deja_importe', 'remplace_derive_acceptee') and e.get('sha256'):
                out[e['target'].replace('\\', '/')] = (rec.get('batch'), e['sha256'], str(rec.get('imported')))
    return out


def rows_for(patterns, tex, scales, orig):
    rows = []
    for pat in patterns:
        for p in sorted(SRC.glob(pat)):
            rel = p.relative_to(SRC).as_posix()
            h = sha256(p)
            r = dict(target_relpath=rel, sha256=h, octets=p.stat().st_size, pixels='', mode='', grab='', monde_u='', px_par_u='', nom_moteur='', acteur='',
                     origine='')
            if p.suffix.lower() == '.png':
                im = Image.open(p)
                r['pixels'] = f'{im.size[0]}x{im.size[1]}'
                r['mode'] = im.mode
                g = grab(p)
                if g:
                    r['grab'] = f'{g[0]},{g[1]}'
                td = tex.get(rel.lower())
                if td:
                    r['nom_moteur'] = f'{td[0]} ({td[1]})'
                    r['monde_u'] = f'{td[2]:g}x{td[3]:g}'
                    r['px_par_u'] = f'{td[4]:g}'
                elif rel.startswith('sprites/'):
                    pref = p.stem[:4].upper()
                    sc = scales.get(pref)
                    r['nom_moteur'] = p.stem.upper()
                    if sc:
                        r['acteur'] = sc[0]
                        if sc[1]:
                            r['px_par_u'] = f'{1 / sc[1]:.3f}'.rstrip('0').rstrip('.')
                            r['monde_u'] = f'{im.size[0] * sc[1]:.1f}x{im.size[1] * sc[1]:.1f} (Scale {sc[1]:g})'
            o = orig.get('src/' + rel)
            if o and o[1] == h:
                r['origine'] = f'{o[0]} (importé {o[2]})'
            elif o:
                r['origine'] = f'modifié depuis {o[0]}'
            else:
                r['origine'] = 'Opus ou référence antérieure (aucun import enregistré)'
            rows.append(r)
    return rows


def rotation_sheet(out):
    """The eight files of one frame as they are in the game: the numbering in use (1 faces the viewer, 5 shows the back)."""
    files = [SRC / 'sprites' / 'enemies' / f'ORDYA{i}.png' for i in range(1, 9)]
    ims = [Image.open(f).convert('RGBA') for f in files]
    w, h = max(i.size[0] for i in ims), max(i.size[1] for i in ims)
    sheet = Image.new('RGB', (8 * (w + 12) + 12, h + 70), (88, 88, 92))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
    except OSError:
        f = ImageFont.load_default()
    for k, im in enumerate(ims):
        x = 12 + k * (w + 12)
        sheet.paste(im, (x + (w - im.size[0]) // 2, 40 + h - im.size[1]), im)
        d.text((x + 6, 8), f'ORDYA{k + 1}', font=f, fill=(255, 235, 140))
    d.text((12, h + 44), 'Fichiers en jeu : 1 = de face (il regarde la camera), 5 = de dos ; 2-3-4 et 6-7-8 comme montres ici. Garder cette numerotation.',
           font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18) if f else None, fill=(240, 240, 240))
    sheet.save(out, quality=90)


def main():
    tex, scales, orig = texture_defs(), sprite_scales(), origins()
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    for d in (DOCS, INBOX):
        d.mkdir(parents=True, exist_ok=True)
    (DOCS / 'CONTRATS').mkdir(exist_ok=True)
    summary = {}
    for lot, (title, patterns) in LOTS.items():
        rows = rows_for(patterns, tex, scales, orig)
        cols = ['target_relpath', 'pixels', 'mode', 'grab', 'monde_u', 'px_par_u', 'nom_moteur', 'acteur', 'origine', 'octets', 'sha256']
        with open(DOCS / 'CONTRATS' / f'{lot}_FICHIERS.csv', 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
        manifest = dict(schema=1, batch_id=f'{lot}_V01_A_RENOMMER', status='A_REMPLIR_PAR_ASTRA', base_commit=head,
                        base_build='RF2_PORTES_20261002_1018',
                        note="Manifeste de base au schéma de scripts/import_astra_lot.py. Garder seulement les fichiers livrés ; pour chacun, "
                             "'file' = chemin du fichier livré dans le lot, 'sha256' = son empreinte, 'target_relpath' et 'base_sha256' "
                             "tels quels. Un fichier neuf (sans destination existante) : 'base_sha256' absent, destination à convenir avec Opus.",
                        files=[dict(file='runtime/' + r['target_relpath'], sha256='A_CALCULER_APRES_EXPORT', target_relpath=r['target_relpath'],
                                    base_sha256=r['sha256'], pixels=r['pixels'], grab=r['grab'], monde_u=r['monde_u']) for r in rows])
        (DOCS / 'CONTRATS' / f'{lot}_MANIFESTE_BASE.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        summary[lot] = dict(titre=title, fichiers=len(rows), origines=sorted({r['origine'].split(' (')[0] for r in rows}))
        ref = INBOX / 'REFERENCES' / lot
        for r in rows:
            dst = ref / r['target_relpath']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SRC / r['target_relpath'], dst)
    for name, patterns in REFERENCES.items():
        rows = rows_for(patterns, tex, scales, orig)
        with open(DOCS / 'CONTRATS' / f'REF_{name}_FICHIERS.csv', 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['target_relpath', 'pixels', 'mode', 'grab', 'monde_u', 'px_par_u', 'nom_moteur', 'acteur', 'origine', 'octets', 'sha256'], lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
        summary['REF_' + name] = dict(titre='référence à ne pas remplacer', fichiers=len(rows))
        for r in rows:
            dst = INBOX / 'REFERENCES' / name / r['target_relpath']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SRC / r['target_relpath'], dst)
    rotation_sheet(DOCS / 'ROTATIONS_ETALON_ORDY_A.jpg')
    (DOCS / 'CONTRATS' / 'SOMMAIRE.json').write_text(json.dumps(dict(base_commit=head, lots=summary), indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    # the documents and tables go to Astra's inbox as well
    for p in DOCS.rglob('*'):
        if p.is_file():
            dst = INBOX / p.relative_to(DOCS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
    for lot, s in summary.items():
        print(f"{lot}: {s['fichiers']} fichiers", s.get('origines', ''))


if __name__ == '__main__':
    main()
