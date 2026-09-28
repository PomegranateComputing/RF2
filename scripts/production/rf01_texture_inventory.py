#!/usr/bin/env python3
"""Inventory of every surface RF01 shows (texture pass "Sainte-Anne 1940", 28/09): wall textures and flats of the
map, prop models and their skin, wear decals. For each entry: source file and sha256, size in pixels and in world
units, uses in RF01 (sides/sectors/things and the named zones of the map where they appear), other maps of the
project using it, transparency, dependencies (ANIMDEFS, GLDEFS, DECALDEF, SNDINFO, TERRAIN, MAPINFO, ZScript), and a
camera in front of a representative use for a capture (scripts/production/view_check_pk3.py).

Reads the map as built (src/maps/RF01.wad) and the map script (scripts/mapkit/rf01.py, run in memory up to its
main(): nothing is written by it) for the zones. Writes nothing in src/.

Usage: python scripts/production/rf01_texture_inventory.py <out_dir>
       -> <out_dir>/inventaire.json, <out_dir>/INVENTAIRE.md, <out_dir>/vues_captures.json
"""
import hashlib, json, math, re, struct, sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'src'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
rf01_src = (ROOT / 'scripts' / 'mapkit' / 'rf01.py').read_text(encoding='utf-8')
ns = {'__file__': str(ROOT / 'scripts' / 'mapkit' / 'rf01.py'), '__name__': 'rf01_inventory'}
exec(compile(re.sub(r"\nif __name__ == '__main__':\n(    .*\n?)+", '\n', rf01_src), 'rf01', 'exec'), ns)
m = ns['m']
import udmf


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def textmap(path):
    b = Path(path).read_bytes()
    n, off = struct.unpack('<ii', b[4:12])
    for i in range(n):
        o, sz, name = struct.unpack('<ii8s', b[off + 16 * i: off + 16 * i + 16])
        if name.rstrip(b'\0') == b'TEXTMAP':
            return b[o:o + sz].decode('utf-8', errors='replace')
    return ''


def blocks(t):
    out = defaultdict(list)
    for kind, body in re.findall(r'(\w+)\s*\{([^}]*)\}', t):
        out[kind].append(dict((k.strip(), v.strip().strip('"')) for k, v in (l.split('=', 1) for l in body.split(';') if '=' in l)))
    return out


# ------------------------------------------------------------------ definitions of the textures
TEXDEF = {}
for tf in sorted(f for f in SRC.glob('TEXTURES*') if f.is_file()):
    for kind, name, w, h, body in re.findall(r'(Texture|Flat|WallTexture|Graphic|Sprite)\s+"?(\w+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{([^}]*)\}',
                                             tf.read_text(encoding='utf-8', errors='replace'), re.I):
        xs = re.search(r'XScale\s+([\d.]+)', body, re.I)
        ys = re.search(r'YScale\s+([\d.]+)', body, re.I)
        patches = re.findall(r'Patch\s+"([^"]+)"', body, re.I)
        TEXDEF[name.upper()] = dict(defined_in=tf.name, kind=kind.lower(), px=[int(w), int(h)],
                                    scale=[float(xs.group(1)) if xs else 1.0, float(ys.group(1)) if ys else 1.0],
                                    patches=patches)

# ------------------------------------------------------------------ uses in every map
maps = {}
for wad in sorted((SRC / 'maps').glob('*.wad')):
    t = textmap(wad)
    maps[wad.stem] = dict(walls=Counter(re.findall(r'texture(?:top|middle|bottom)\s*=\s*"([^"]+)"', t)),
                          flats=Counter(re.findall(r'texture(?:floor|ceiling)\s*=\s*"([^"]+)"', t)),
                          things=Counter(int(x) for x in re.findall(r'thing\s*\{[^}]*?type\s*=\s*(\d+)', t)))
rf01 = blocks(textmap(SRC / 'maps' / 'RF01.wad'))

# ------------------------------------------------------------------ dependencies (text definitions and code)
DEPFILES = [f for f in SRC.iterdir() if f.is_file() and f.suffix.lower() not in ('.wad', '.png')] + sorted((SRC / 'zscript').rglob('*.zs'))
DEPTEXT = {f.relative_to(SRC).as_posix(): f.read_text(encoding='utf-8', errors='replace') for f in DEPFILES}


def deps(name):
    out = []
    for f, t in DEPTEXT.items():
        if f.upper().startswith('TEXTURES'):
            continue
        if re.search(r'(?<![A-Z0-9_])' + re.escape(name) + r'(?![A-Z0-9_])', t, re.I):
            out.append(f)
    return out


# ------------------------------------------------------------------ zones: the plan labels of rf01.py
LABELS = [(x, y, txt) for (x, y, txt) in m.labels]


def zone(x, y):
    return min(LABELS, key=lambda l: (l[0] - x) ** 2 + (l[1] - y) ** 2)[2] if LABELS else '?'


cells_by_tex = defaultdict(list)                  # texture -> [(role, x, y)]
for (cx, cy), c in m.cells.items():
    x, y = cx * udmf.UNIT + 8, cy * udmf.UNIT + 8
    for role, tex in (('mur', c.wall), ('sol', c.ftex), ('plafond', c.ctex), ('contremarche', c.lower),
                      ('au-dessus', c.upper), ('milieu', c.mid), ('embrasure', c.track)):
        if tex:
            cells_by_tex[tex.upper()].append((role, x, y))


def alpha_info(p):
    im = Image.open(p)
    if im.mode in ('RGBA', 'LA') or 'transparency' in im.info:
        a = im.convert('RGBA').getchannel('A')
        lo, hi = a.getextrema()
        return 'aucune' if lo == 255 else ('masque (0/255)' if set(a.getdata()) <= {0, 255} else 'alpha progressif')
    return 'aucune'


def file_for(name):
    d = TEXDEF.get(name)
    if d and d['patches']:
        return SRC / d['patches'][0]
    for sub in ('patches', 'flats', 'textures', 'graphics'):
        for p in (SRC / sub).rglob(name + '.png'):
            return p
    return None


# ------------------------------------------------------------------ cameras for the captures
EYE = 41
lines = rf01['linedef']
sides = rf01['sidedef']
sectors = rf01['sector']
verts = rf01['vertex']


def clear_path(cx, cy, dx, dy, dist, f0):
    def ok(px, py):
        c = m.cell_at(px, py)
        return c is not None and c.role != 'door' and c.ceil - c.floor >= 56 and abs(c.floor - f0) <= 24
    d, best = 4, 0
    while d <= dist:
        px, py = cx + dx * d, cy + dy * d
        if not ok(px, py):
            break
        if d >= 16 and all(ok(px + e * dy * 16, py - e * dx * 16) for e in (1, -1)):
            best = d
        d += 4
    return best


def wall_view(name):
    best = None
    for ln in lines:
        for side_key, other_key in (('sidefront', 'sideback'), ('sideback', 'sidefront')):
            if side_key not in ln:
                continue
            sd = sides[int(ln[side_key])]
            parts = [p for p in ('texturemiddle', 'texturetop', 'texturebottom') if sd.get(p, '').upper() == name]
            if not parts:
                continue
            v1, v2 = verts[int(ln['v1'])], verts[int(ln['v2'])]
            x0, y0, x1, y1 = float(v1['x']), float(v1['y']), float(v2['x']), float(v2['y'])
            if side_key == 'sideback':
                x0, y0, x1, y1 = x1, y1, x0, y0
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 16:
                continue
            nx, ny = (y1 - y0) / L, -(x1 - x0) / L
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            front = sectors[int(sd['sector'])]
            f, c = float(front.get('heightfloor', 0)), float(front.get('heightceiling', 0))
            if parts[0] != 'texturemiddle' and other_key in ln:
                back = sectors[int(sides[int(ln[other_key])]['sector'])]
                bf, bc = float(back.get('heightfloor', 0)), float(back.get('heightceiling', 0))
                zlo, zhi = (bc, c) if parts[0] == 'texturetop' else (f, bf)
            else:
                zlo, zhi = f, c
            fc = m.cell_at(cx + nx * 8, cy + ny * 8)
            if fc is None:
                continue
            d = clear_path(cx, cy, nx, ny, 160, fc.floor)
            score = min(L, 256) + d
            if d >= 32 and (best is None or score > best[0]):
                zc = (zlo + min(zhi, zlo + 128)) / 2
                px, py = cx + nx * max(d - 12, 24), cy + ny * max(d - 12, 24)
                dd = math.hypot(cx - px, cy - py)
                pitch = -math.degrees(math.atan2(zc - (fc.floor + EYE), dd))
                yaw = math.degrees(math.atan2(cy - py, cx - px)) % 360
                best = (score, [round(px, 1), round(py, 1), 0, round(yaw, 1), round(max(-60, min(60, pitch)), 1)], parts[0])
    return best


def flat_view(name, ceiling):
    pts = [(x, y) for role, x, y in cells_by_tex.get(name, []) if role == ('plafond' if ceiling else 'sol')]
    if not pts:
        return None
    # the cell with the most same-texture cells around it
    S = set(pts)
    cx, cy = max(pts, key=lambda p: sum((p[0] + dx * 16, p[1] + dy * 16) in S for dx in range(-4, 5) for dy in range(-4, 5)))
    c = m.cell_at(cx, cy)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        d = clear_path(cx, cy, dx, dy, 96, c.floor)
        if d >= 48:
            px, py = cx + dx * (d - 12), cy + dy * (d - 12)
            return [round(px, 1), round(py, 1), 0, round((ang + 180) % 360, 1), -45.0 if ceiling else 40.0]
    return [cx, cy, 0, 0, -80.0 if ceiling else 80.0]


# ------------------------------------------------------------------ inventory
inv, views = [], []
wall_names = set(maps['RF01']['walls'])
flat_names = set(maps['RF01']['flats'])
for name in sorted(wall_names | flat_names):
    N = name.upper()
    d = TEXDEF.get(N, {})
    f = file_for(N)
    uses = {}
    if N in {k.upper() for k in maps['RF01']['walls']}:
        uses['cotes'] = maps['RF01']['walls'][name]
    if N in {k.upper() for k in maps['RF01']['flats']}:
        uses['secteurs'] = maps['RF01']['flats'][name]
    roles = Counter(r for r, _, _ in cells_by_tex.get(N, []))
    zones = Counter(zone(x, y) for _, x, y in cells_by_tex.get(N, []))
    others = sorted(k for k, v in maps.items() if k != 'RF01' and (name in v['walls'] or name in v['flats']))
    world = [round(d['px'][0] / d['scale'][0], 2), round(d['px'][1] / d['scale'][1], 2)] if d else None
    img = Image.open(f).size if f else None
    scope = 'hors lot (ciel)' if N == 'F_SKY1' else ('hors lot (plaques RF01-PAN)' if N.startswith('RFSIGN') else 'dans le lot')
    e = dict(id=N, famille='texture murale' if name in wall_names else 'plat', perimetre=scope,
             source=f.relative_to(ROOT).as_posix() if f else None, sha256=sha(f) if f else None,
             png_px=list(img) if img else None, definition=d.get('defined_in'), texture_px=d.get('px'), echelle=d.get('scale'),
             taille_monde=world, transparence=alpha_info(f) if f else None, usages_rf01=uses, roles_cellules=dict(roles),
             zones=[z for z, _ in zones.most_common(8)], autres_cartes=others, dependances=deps(N))
    inv.append(e)
    if scope == 'dans le lot':
        if name in wall_names:
            v = wall_view(N)
            if v:
                views.append([f'{N}_{v[2].replace("texture", "")}', *v[1]])
        for ceiling in (False, True):
            if roles.get('plafond' if ceiling else 'sol'):
                fv = flat_view(N, ceiling)
                if fv:
                    views.append([f'{N}_{"plafond" if ceiling else "sol"}', *fv])

def prop_height(cls):
    """Height of a prop class (ZScript Default block), 16 when not found."""
    t = DEPTEXT['zscript/rf/world.zs']
    i = t.find('class ' + cls)
    mm = re.search(r'Height\s+(\d+)', t[i:i + 400]) if i >= 0 else None
    return float(mm.group(1)) if mm else 16.0


def ceiling_prop(cls):
    t = DEPTEXT['zscript/rf/world.zs']
    i = t.find('class ' + cls)
    return i >= 0 and 'SPAWNCEILING' in t[i:i + 400].upper()


# props: models and their skin
mi = (SRC / 'MAPINFO').read_text(encoding='utf-8', errors='replace')
ednums = {int(a): b for a, b in re.findall(r'(\d+)\s*=\s*"?(\w+)"?', re.search(r'DoomEdNums\s*\{([^}]*)\}', mi, re.S).group(1))}
modeldef = (SRC / 'MODELDEF').read_text(encoding='utf-8', errors='replace')
rf01_things = [t for t in rf01['thing']]
for num, cls in sorted(ednums.items()):
    if not cls.startswith('RFProp') or num not in maps['RF01']['things']:
        continue
    mm = re.search(r'Model\s+' + cls + r'\s*\{([^}]*)\}', modeldef)
    path = re.search(r'Path\s+"([^"]+)"', mm.group(1)).group(1) if mm else None
    model = re.search(r'Model\s+0\s+"([^"]+)"', mm.group(1)).group(1) if mm else None
    skin = re.search(r'Skin\s+0\s+"([^"]+)"', mm.group(1)).group(1) if mm else None
    scale = re.search(r'Scale\s+([\d.\s]+)', mm.group(1)).group(1).split() if mm else None
    skin_f = SRC / path / skin if skin else None
    pos = [(float(t['x']), float(t['y']), float(t.get('angle', 0)), float(t.get('height', 0))) for t in rf01_things if int(t['type']) == num]
    others = sorted(k for k, v in maps.items() if k != 'RF01' and v['things'].get(num))
    shared = sorted(c for c in re.findall(r'Model\s+(\w+)\s*\{[^}]*Skin\s+0\s+"' + re.escape(skin or '#') + '"', modeldef))
    inv.append(dict(id=cls, famille='modele (accessoire)', perimetre='dans le lot', source=f'src/{path}/{model}',
                    peau=f'src/{path}/{skin}', sha256_peau=sha(skin_f) if skin_f and skin_f.exists() else None,
                    peau_px=list(Image.open(skin_f).size) if skin_f and skin_f.exists() else None,
                    sha256_modele=sha(SRC / path / model), echelle_modele=scale, usages_rf01=dict(objets=len(pos)),
                    zones=[z for z, _ in Counter(zone(x, y) for x, y, _, _ in pos).most_common(8)], autres_cartes=others,
                    peau_partagee_avec=shared, dependances=deps(cls)))
    # the most open placement, seen from its front (then from any side) at 64 units, no other prop in between
    props_xy = [(float(t['x']), float(t['y'])) for t in rf01_things if ednums.get(int(t['type']), '').startswith('RFProp')]
    ht = prop_height(cls)
    best = None
    for x, y, a, zoff in pos:
        c = m.cell_at(x, y)
        f0 = c.floor if c else 0
        for k, ang in enumerate([a] + [a + d for d in (30, -30, 60, -60, 90, -90, 180)]):
            r = math.radians(ang)
            dx, dy = math.cos(r), math.sin(r)
            if clear_path(x + dx * 24, y + dy * 24, dx, dy, 72, f0) < 48:
                continue
            px, py = x + dx * 64, y + dy * 64
            blocked = any(abs((ox - x) * dy - (oy - y) * dx) < 20 and 8 < (ox - x) * dx + (oy - y) * dy < 64
                          for ox, oy in props_xy if (ox, oy) != (x, y))
            if blocked:
                continue
            score = (k == 0, -k)
            if best is None or score > best[0]:
                zc = (c.ceil - ht / 2) if (c and ceiling_prop(cls)) else (f0 + zoff + ht / 2)
                pitch = math.degrees(math.atan2(f0 + EYE - zc, 64))
                best = (score, [round(px, 1), round(py, 1), 0, round((ang + 180) % 360, 1), round(pitch, 1)])
    if best:
        views.append([f'{cls}_modele', *best[1]])

# wear decals
decaldef = (SRC / 'DECALDEF').read_text(encoding='utf-8', errors='replace')
decal_ids = Counter(int(t.get('arg0', 0)) for t in rf01_things if int(t['type']) == 9200)
for did, n in sorted(decal_ids.items()):
    mm = re.search(r'decal\s+(\w+)\s+' + str(did) + r'\s*\{([^}]*)\}', decaldef, re.I)
    pic = re.search(r'pic\s+(\w+)', mm.group(2), re.I).group(1) if mm else None
    pf = next(iter((SRC / 'graphics').rglob((pic or '#') + '.png')), None)
    inv.append(dict(id=mm.group(1) if mm else f'decal {did}', famille='decalque d\'usure', perimetre='dans le lot',
                    source=pf.relative_to(ROOT).as_posix() if pf else None, sha256=sha(pf) if pf else None,
                    png_px=list(Image.open(pf).size) if pf else None, usages_rf01=dict(objets=n),
                    autres_cartes=sorted(k for k, v in maps.items() if k != 'RF01' and v['things'].get(9200)),
                    transparence=alpha_info(pf) if pf else None, dependances=['DECALDEF']))

json.dump(dict(carte='RF01', wad_sha256=sha(SRC / 'maps' / 'RF01.wad'), entrees=inv), open(OUT / 'inventaire.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
json.dump(views, open(OUT / 'vues_captures.json', 'w', encoding='utf-8'), indent=1)
print(len(inv), 'entrees,', len(views), 'vues')

# ------------------------------------------------------------------ table for the contract
WHAT = {
    'RFP_DADB': 'mur 256 : enduit au-dessus, soubassement peint bleu (44 u en bas, calé en bas), moulure — admissions, couloirs',
    'RFP_DADG': 'mur 256 : soubassement vert (44 u en bas) — salles, chambres',
    'RFP_DADR': 'mur 256 : soubassement sang-de-boeuf (44 u en bas) — registres, loge',
    'RFP_TILE': 'mur 256 : faience 16 u jusqu\'a 48 u, enduit au-dessus — lingerie, consultations',
    'RFP_PLN': 'enduit uni 128 (retours, embrasures, contremarches)', 'RFP_DRK': 'enduit de service assombri 128',
    'RFS_LIME': 'pierre calcaire appareillee 128 — chapelle, porche', 'RFS_BASE': 'soubassement de pierre 128x64 (bas de facades)',
    'RFS_REND': 'enduit de facade 128x256 (cour, exterieurs)', 'RFW_PANL': 'lambris / boiserie 128 (meubles, rayonnages)',
    'RFM_PANL': 'metal peint 128', 'RFD_DBL': 'porte a deux vantaux 128x128', 'RFD_SGL': 'porte simple 64x128',
    'RFM_DOOR': 'porte metallique 64x128 (lingerie)', 'RFM_GRIL': 'grille de fer 128x128 (grilles verrouillees)',
    'RFG_WIN': 'fenetre 64 (vitrage a alpha progressif)', 'RFG_VITR': 'vitrail de la chapelle 64 (+ brightmap RFG_VITR_BM)',
    'RFM_SW0': 'interrupteur eteint 64 (paire ANIMDEFS avec RFM_SW1 allume)', 'RFM_VATS': 'cotes des cuves de la lingerie 64x48',
    'RFT_BEDS': 'cote de lit 64x32', 'RFT_HEAD': 'tete de lit 64x48', 'RFW_TBLS': 'cote de table 64x32', 'RFW_SHLF': 'face de rayonnage 64',
    'RFS_FACD': 'facade parisienne 256x448 (rue Cabanis, vue de loin)', 'RFS_HOSP': 'facade de pavillon hospitalier 256x320',
    'RFF_CER': 'sol carrele 32 u', 'RFF_CERD': 'sol carrele sombre', 'RFF_CHK': 'sol en damier', 'RFF_WOOD': 'parquet',
    'RFF_LINO': 'linoleum', 'RFF_GRAV': 'gravier (cour)', 'RFF_SLAB': 'dallage de pierre 64 u', 'RFF_CONC': 'ciment',
    'RFF_PAVE': 'paves (rue)', 'RFP_CEIL': 'plafond platre clair', 'RFP_CEID': 'plafond platre sombre (service)',
    'RFW_TOP': 'dessus de meuble en bois', 'RFT_BED': 'dessus de lit (literie)', 'RFM_TOP': 'dessus metallique (cuves, radiateurs)',
    'RFPropChair': 'chaise (modele, atlas commun)', 'RFPropCabinet': 'armoire (modele, atlas commun)',
    'RFPropRadiator': 'radiateur (modele, atlas commun)', 'RFPropTrolley': 'chariot (modele, atlas commun)',
    'RFPropBench': 'banc (modele, atlas commun)', 'RFPropLamp': 'plafonnier de service (modele, atlas commun)',
    'RFDamp': 'decalque : tache d\'humidite', 'RFGrime': 'decalque : crasse', 'RFStreak': 'decalque : coulure', 'RFScuff': 'decalque : frottement',
}
FIRST = {'RFP_DADG', 'RFP_DADB', 'RFP_PLN', 'RFF_WOOD', 'RFF_CER', 'RFP_CEIL', 'RFD_SGL', 'RFT_BEDS', 'RFT_HEAD', 'RFT_BED', 'RFPropRadiator'}


def variant(n):
    return n[:3] + '4' + n[4:] if n[3] == '_' else n[:3] + '4' + n[3:7]


rows = []
for e in inv:
    n = e['id']
    if e['perimetre'] != 'dans le lot':
        action = e['perimetre']
    elif e['famille'].startswith('modele'):
        action = 'nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048)' if e['autres_cartes'] or len(e.get('peau_partagee_avec', [])) > 1 else 'remplacer la peau'
    elif e['autres_cartes'] or any(d in ('MAPINFO',) for d in e['dependances']):
        action = f'variante RF01 `{variant(n)}`'
    else:
        action = 'remplacer'
    ppu = round(e['texture_px'][0] / e['taille_monde'][0], 2) if e.get('texture_px') and e.get('taille_monde') else None
    size = f"{e['taille_monde'][0]:g}x{e['taille_monde'][1]:g}" if e.get('taille_monde') else ''
    rows.append(f"| {'**' if n in FIRST else ''}{n}{'**' if n in FIRST else ''} | {WHAT.get(n, '')} | {e.get('source') or e.get('peau') or ''} | "
                f"{'x'.join(map(str, e.get('png_px') or e.get('peau_px') or []))} | {size} | {ppu or ''} | "
                f"{', '.join(f'{k} {v}' for k, v in e['usages_rf01'].items())} | {', '.join(e.get('zones', [])[:4])} | "
                f"{', '.join(e['autres_cartes'][:3]) + (' ...' if len(e['autres_cartes']) > 3 else '') or '-'} | {', '.join(e['dependances']) or '-'} | "
                f"{e.get('transparence') or '-'} | {action} |")
md = ['# RF01 — inventaire des surfaces (passe « Sainte-Anne 1940 »)', '',
      f'Généré par `scripts/production/rf01_texture_inventory.py` depuis `src/maps/RF01.wad` (sha256 `{sha(SRC / "maps" / "RF01.wad")}`) '
      'et `scripts/mapkit/rf01.py` (zones). Empreintes et détails : `inventaire.json`. En gras : premier ensemble représentatif '
      '(chambre de départ et couloir du pavillon ouest).', '',
      '| Id | Représente | Fichier | px | Monde (u) | px/u | Usages RF01 | Zones | Autres cartes | Dépendances | Transparence | Action |',
      '|---|---|---|---|---|---|---|---|---|---|---|---|'] + rows
(OUT / 'INVENTAIRE.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
print('INVENTAIRE.md', len(rows), 'lignes')
