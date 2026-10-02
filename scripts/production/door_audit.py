#!/usr/bin/env python3
"""Inventory of every door-like surface of every map, read from the maps as shipped (src/maps/*.wad, UDMF TEXTMAP),
with the measures that decide whether its texture shows one whole object: the visible surface in map units, the
texture's world size (TEXTURES scale, sidedef scale), how many times the texture repeats across and up the surface,
what part of it is cut, the vertical anchoring (pegging) and the offsets.

A surface is a run of collinear, connected lines that show the same texture part between the same two sectors:
  - the faces of a MECHANISM: a sector moved by a door, ceiling, platform or lift special (from a line's special and
    tag, from a tag used by the scripts, or a sector shut at its floor), seen from each neighbour;
  - its TRACKS: the one-sided lines of that sector (the jambs the panel slides in);
  - every STATIC face whose texture is a door, gate, grille or shutter image (DOORLIKE below), whatever carries it.

Usage: python scripts/production/door_audit.py [--maps RF01,RF02] [--wads <dir>] [--out build/door_audit.json]
Prints one line per surface with its defects; writes the full records (with a camera point for views) as JSON.
"""
import argparse, json, math, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IWAD = Path(r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad')

# line specials that move a sector like a door, a shutter, a lift (arg0 = tag, 0 = the line's back sector)
DOOR_SPECIALS = {10: 'Door_Close', 11: 'Door_Open', 12: 'Door_Raise', 13: 'Door_LockedRaise', 14: 'Door_Animated',
                 105: 'Door_WaitRaise', 106: 'Door_WaitClose', 202: 'Generic_Door', 249: 'Door_CloseWaitOpen'}
MOVE_SPECIALS = {40: 'Ceiling_LowerByValue', 41: 'Ceiling_RaiseByValue', 42: 'Ceiling_CrushAndRaise', 43: 'Ceiling_LowerAndCrush',
                 44: 'Ceiling_CrushStop', 45: 'Ceiling_CrushRaiseAndStay', 47: 'Ceiling_MoveToValue', 192: 'Ceiling_LowerToHighestFloor',
                 193: 'Ceiling_LowerInstant', 194: 'Ceiling_RaiseInstant', 198: 'Ceiling_RaiseByValueTimes8', 252: 'Ceiling_RaiseToNearest',
                 253: 'Ceiling_LowerToLowest', 254: 'Ceiling_LowerToFloor', 255: 'Ceiling_CrushRaiseAndStaySilA',
                 60: 'Plat_PerpetualRaise', 62: 'Plat_DownWaitUpStay', 63: 'Plat_DownByValue', 64: 'Plat_UpWaitDownStay',
                 65: 'Plat_UpByValue', 172: 'Plat_UpNearestWaitDownStay', 203: 'Generic_Lift', 206: 'Plat_DownWaitUpStayLip',
                 207: 'Plat_PerpetualRaiseLip', 228: 'Plat_RaiseAndStayTx0', 230: 'Plat_UpByValueStayTx', 231: 'Plat_ToggleCeiling',
                 245: 'Elevator_RaiseToNearest', 246: 'Elevator_MoveToFloor', 247: 'Elevator_LowerToNearest',
                 29: 'Pillar_Build', 30: 'Pillar_Open', 94: 'Pillar_BuildAndCrush', 95: 'FloorAndCeiling_LowerByValue',
                 96: 'FloorAndCeiling_RaiseByValue', 20: 'Floor_LowerByValue', 21: 'Floor_LowerToLowest', 22: 'Floor_LowerToNearest',
                 23: 'Floor_RaiseByValue', 24: 'Floor_RaiseToHighest', 25: 'Floor_RaiseToNearest', 200: 'Generic_Floor',
                 201: 'Generic_Ceiling'}
POLY_SPECIALS = {2: 'Polyobj_RotateLeft', 3: 'Polyobj_RotateRight', 4: 'Polyobj_Move', 6: 'Polyobj_MoveTimes8',
                 7: 'Polyobj_DoorSwing', 8: 'Polyobj_DoorSlide'}
# images of a whole door, gate, grille or shutter: one object, not a material that may repeat freely
DOORLIKE = re.compile(r'^(RD[0-9A-F]{6}|RFD_\w+|RFD[A-Z0-9]{2,6}|RFM_DOOR|RFMDOOR\w*|RFM_GRIL|RFMGRIL\w*|RFDOORB|RF2_SGAT|RF2_RIDO|'
                      r'RF4_PSST|RF4_PORT|RF6_JOUR|RFEXIT|'
                      r'DOOR\d\w*|BIGDOOR\w*|SPCDOOR\w*|EXITDOOR|TEKBRON\d|BRNSMAL\w*|BRNBIGC|MIDBARS\w*|MIDGRATE|MIDSPACE)$')
# materials built from repeating members: repetition along the surface is the object's construction
# the image of one bay of an arcade (a row of gates): whole bays side by side are the composition
BAYS = re.compile(r'^(RF4_PORT)$')
REPEATING = re.compile(r'^(RFM_GRIL|RFMGRIL\w*|RF2_RIDO|MIDBARS\w*|MIDGRATE|MIDSPACE|BRNSMAL\w*|RF2_PALI)$')
TOL = 0.04


def lumps(path):
    b = Path(path).read_bytes()
    n, off = struct.unpack('<II', b[4:12])
    for i in range(n):
        p, s = struct.unpack('<II', b[off + i * 16: off + i * 16 + 8])
        yield b[off + i * 16 + 8: off + i * 16 + 16].rstrip(b'\0').decode('latin-1'), b[p:p + s]


def texture_db():
    """{NAME: (world width, world height, source)} of the wall textures: TEXTURES lumps, loose src/textures, the IWAD."""
    db = {}
    if IWAD.exists():
        for name, data in lumps(IWAD):
            if name in ('TEXTURE1', 'TEXTURE2'):
                n = struct.unpack('<I', data[:4])[0]
                for k in range(n):
                    o = struct.unpack('<I', data[4 + 4 * k: 8 + 4 * k])[0]
                    nm = data[o:o + 8].rstrip(b'\0').decode('latin-1').upper()
                    w, h = struct.unpack('<HH', data[o + 12:o + 16])
                    db[nm] = (float(w), float(h), 'IWAD')
    from PIL import Image
    for p in (ROOT / 'src' / 'textures').glob('*.png'):
        w, h = Image.open(p).size
        db[p.stem.upper()] = (float(w), float(h), 'src/textures')
    for tf in sorted((ROOT / 'src').glob('TEXTURES.*')) + sorted((ROOT / 'bench').glob('*/lumps/TEXTURES*')):
        t = tf.read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r'(?:Texture|WallTexture)\s+"?(\w+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{(.*?)\n\}', t, re.S):
            xs = re.search(r'XScale\s+([\d.]+)', m.group(4))
            ys = re.search(r'YScale\s+([\d.]+)', m.group(4))
            db[m.group(1).upper()] = (int(m.group(2)) / (float(xs.group(1)) if xs else 1.0),
                                      int(m.group(3)) / (float(ys.group(1)) if ys else 1.0), tf.name)
    return db


def parse_textmap(text):
    out = {'vertex': [], 'linedef': [], 'sidedef': [], 'sector': [], 'thing': []}
    for kind, body in re.findall(r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*)?\s*\{(.*?)\}', text, re.S):
        d = {}
        for k, v in re.findall(r'(\w+)\s*=\s*("[^"]*"|[^;]+);', body):
            v = v.strip()
            if v.startswith('"'):
                d[k] = v[1:-1]
            elif v in ('true', 'false'):
                d[k] = v == 'true'
            else:
                try:
                    d[k] = int(v)
                except ValueError:
                    d[k] = float(v)
        out[kind].append(d)
    return out


def script_tags():
    """Sector tags moved from the scripts (Door_Open, Ceiling_... called with a literal tag)."""
    tags = {}
    files = list((ROOT / 'src' / 'zscript').rglob('*.zs')) + list((ROOT / 'bench').rglob('*.zs'))
    for f in files:
        t = f.read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r'\b(Door_\w+|Ceiling_\w+|Generic_Door|Plat_\w+|Floor_\w+)\s*,\s*0\s*,\s*(\d+)', t):
            tags.setdefault(int(m.group(2)), set()).add(f'{m.group(1)} ({f.name})')
        for m in re.finditer(r'\b(Door_\w+|Ceiling_\w+|Generic_Door|Plat_\w+|Floor_\w+)\s*\(\s*(\d+)', t):
            tags.setdefault(int(m.group(2)), set()).add(f'{m.group(1)} ({f.name})')
    return tags


class Map:
    def __init__(self, name, text, db, stags):
        self.name, self.db = name, db
        m = parse_textmap(text)
        self.V, self.L, self.S, self.SE = m['vertex'], m['linedef'], m['sidedef'], m['sector']
        self.by_tag = {}
        for i, s in enumerate(self.SE):
            for t in [s.get('id', 0)] + [int(x) for x in str(s.get('moreids', '')).split() if x]:
                if t:
                    self.by_tag.setdefault(t, []).append(i)
        self.mech = {}                                   # sector -> set of mechanism names
        for li, l in enumerate(self.L):
            sp = l.get('special', 0)
            name_ = DOOR_SPECIALS.get(sp) or MOVE_SPECIALS.get(sp)
            if not name_:
                continue
            tag = l.get('arg0', 0)
            if tag:
                targets = self.by_tag.get(tag, [])
            else:
                targets = [self.S[l['sideback']]['sector']] if l.get('sideback', -1) >= 0 else []
            for s in targets:
                self.mech.setdefault(s, set()).add(name_ + (f' lock {l.get("arg3")}' if sp == 13 else ''))
        for tag, names in stags.items():
            for s in self.by_tag.get(tag, []):
                self.mech.setdefault(s, set()).update(names)
        # a sector shut at its floor between rooms is a door even when only a script opens it
        self.lines_of = {}
        for li, l in enumerate(self.L):
            for side in ('sidefront', 'sideback'):
                if l.get(side, -1) >= 0:
                    self.lines_of.setdefault(self.S[l[side]]['sector'], []).append(li)
        for s, sec in enumerate(self.SE):
            if s in self.mech or sec.get('heightceiling', 0) != sec.get('heightfloor', 0):
                continue
            for li in self.lines_of.get(s, []):
                o = self.other(li, s)
                if o is not None and self.SE[o].get('heightceiling', 0) > self.SE[o].get('heightfloor', 0) \
                        and abs(self.SE[o].get('heightfloor', 0) - sec.get('heightfloor', 0)) <= 24 and sec.get('id', 0):
                    self.mech.setdefault(s, set()).add('shut sector with a tag')
                    break
        self.poly = [(li, POLY_SPECIALS[l['special']]) for li, l in enumerate(self.L) if l.get('special', 0) in POLY_SPECIALS]

    def other(self, li, s):
        l = self.L[li]
        a = self.S[l['sidefront']]['sector']
        b = self.S[l['sideback']]['sector'] if l.get('sideback', -1) >= 0 else None
        return b if a == s else a if b == s else None

    def xy(self, v):
        return (self.V[v]['x'], self.V[v]['y'])

    def length(self, li):
        (x0, y0), (x1, y1) = self.xy(self.L[li]['v1']), self.xy(self.L[li]['v2'])
        return math.hypot(x1 - x0, y1 - y0)

    def part(self, li, side, part):
        """(texture, visible height, z bottom) of a part ('top', 'mid', 'bottom') of a side of a line, or None."""
        l = self.L[li]
        sd = self.S[l[side]]
        tex = sd.get({'top': 'texturetop', 'mid': 'texturemiddle', 'bottom': 'texturebottom'}[part], '-')
        if tex in ('-', ''):
            return None
        f = self.SE[sd['sector']]
        oside = 'sideback' if side == 'sidefront' else 'sidefront'
        if l.get(oside, -1) < 0:
            if part != 'mid':
                return None
            return tex, f['heightceiling'] - f['heightfloor'], f['heightfloor']
        b = self.SE[self.S[l[oside]]['sector']]
        if part == 'top':
            if f.get('textureceiling') == 'F_SKY1' and b.get('textureceiling') == 'F_SKY1':
                return None                              # between two skies the engine draws no upper wall
            h = f['heightceiling'] - max(b['heightceiling'], f['heightfloor'])
            return (tex, h, max(b['heightceiling'], f['heightfloor'])) if h > 0 else None
        if part == 'bottom':
            h = min(b['heightfloor'], f['heightceiling']) - f['heightfloor']
            return (tex, h, f['heightfloor']) if h > 0 else None
        z0, z1 = max(f['heightfloor'], b['heightfloor']), min(f['heightceiling'], b['heightceiling'])
        if z1 <= z0:
            return None
        # a two-sided middle texture is drawn once (no vertical repeat) unless the line wraps it
        th = self.db.get(tex.upper(), (None, None))[1]
        h = z1 - z0
        if th and not l.get('wrapmidtex') and not sd.get('wrapmidtex'):
            h = min(h, th / sd.get('scaley_mid', 1.0))
        return tex, h, z0

    def surfaces(self):
        """Group the door-like parts into surfaces (runs of collinear connected lines) and measure them."""
        items = []
        for li, l in enumerate(self.L):
            for side in ('sidefront', 'sideback'):
                if l.get(side, -1) < 0:
                    continue
                sd = self.S[l[side]]
                sec = sd['sector']
                oside = 'sideback' if side == 'sidefront' else 'sidefront'
                osec = self.S[l[oside]]['sector'] if l.get(oside, -1) >= 0 else None
                for part in ('top', 'mid', 'bottom'):
                    p = self.part(li, side, part)
                    if not p:
                        continue
                    tex, h, z0 = p
                    if h <= 0 and not (osec is None and sec in self.mech):
                        continue
                    kind = None
                    if osec is not None and osec in self.mech and sec not in self.mech and part in ('top', 'bottom'):
                        kind = 'mechanism'
                    elif osec is None and sec in self.mech and part == 'mid':
                        kind = 'track'
                    elif DOORLIKE.match(tex.upper()):
                        kind = 'static'
                    if not kind:
                        continue
                    items.append(dict(line=li, side=side, part=part, tex=tex.upper(), h=h, z0=z0, kind=kind, sec=sec, osec=osec))
        # runs: same kind, texture, part, sectors, direction; consecutive (v2 of one = v1 of the next along the side)
        key = lambda it: (it['kind'], it['tex'], it['part'], it['sec'], it['osec'], it['side'], round(it['h'], 1), it['z0'])
        groups = {}
        for it in items:
            groups.setdefault(key(it), []).append(it)
        out = []
        for k, its in groups.items():
            remaining = list(its)
            while remaining:
                run = [remaining.pop(0)]
                grew = True
                while grew:
                    grew = False
                    for it in list(remaining):
                        if self._joins(run[-1], it):
                            run.append(it); remaining.remove(it); grew = True
                        elif self._joins(it, run[0]):
                            run.insert(0, it); remaining.remove(it); grew = True
                out.append(self.measure(run))
        return out

    def _dir(self, it):
        l = self.L[it['line']]
        a, b = (l['v1'], l['v2']) if it['side'] == 'sidefront' else (l['v2'], l['v1'])
        return a, b

    def _joins(self, a, b):
        a0, a1 = self._dir(a)
        b0, b1 = self._dir(b)
        if a1 != b0:
            return False
        (x0, y0), (x1, y1), (x2, y2) = self.xy(a0), self.xy(a1), self.xy(b1)
        return abs((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)) < 1e-6 and (x1 - x0) * (x2 - x1) + (y1 - y0) * (y2 - y1) > 0

    def measure(self, run):
        it = run[0]
        W = sum(self.length(r['line']) for r in run)
        H = it['h']
        l0 = self.L[it['line']]
        sd = self.S[l0[it['side']]]
        suffix = {'top': 'top', 'mid': 'mid', 'bottom': 'bottom'}[it['part']]
        sx = sd.get(f'scalex_{suffix}', 1.0)
        sy = sd.get(f'scaley_{suffix}', 1.0)
        tw, th, src = self.db.get(it['tex'], (None, None, 'UNKNOWN'))
        rec = dict(map=self.name, kind=it['kind'], tex=it['tex'], part=it['part'], lines=[r['line'] for r in run],
                   side='front' if it['side'] == 'sidefront' else 'back',
                   sector=it['osec'] if it['kind'] == 'mechanism' else it['sec'], seen_from=it['sec'],
                   W=round(W, 1), H=round(H, 1), z0=it['z0'], tex_source=src, scalex=sx, scaley=sy,
                   offsetx=[self.S[self.L[r['line']][r['side']]].get('offsetx', 0) + self.S[self.L[r['line']][r['side']]].get(f'offsetx_{suffix}', 0) for r in run],
                   offsety=sd.get('offsety', 0) + sd.get(f'offsety_{suffix}', 0),
                   dontpegtop=bool(l0.get('dontpegtop')), dontpegbottom=bool(l0.get('dontpegbottom')),
                   mechanism=sorted(self.mech.get(it['osec'] if it['kind'] == 'mechanism' else it['sec'], [])))
        a0, _ = self._dir(run[0])
        _, b1 = self._dir(run[-1])
        (x0, y0), (x1, y1) = self.xy(a0), self.xy(b1)
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        nx, ny = (y1 - y0) / L, -(x1 - x0) / L          # to the right of the direction of travel = toward the viewer
        if it['side'] == 'sideback':
            pass                                         # _dir already walks the side with its sector on the right
        rec['mid'] = [round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1)]
        rec['normal'] = [round(nx, 3), round(ny, 3)]
        defects = []
        if tw is None:
            defects.append('texture inconnue')
        else:
            ew, eh = tw / sx, th / sy                    # world size as drawn on this side
            rec['tex_world'] = [round(ew, 1), round(eh, 1)]
            rx, ry = W / ew, H / eh
            rec['repeat'] = [round(rx, 2), round(ry, 2)]
            object_like = bool(DOORLIKE.match(it['tex']))
            repeating = bool(REPEATING.match(it['tex']))
            if it['kind'] == 'mechanism' and not object_like:
                # a door dressed as the wall it is set in (a secret door, a loose board): the material is the wall's
                rec['camouflage'] = True
            bays = bool(BAYS.match(it['tex'])) and abs(rx - round(rx)) < TOL and rx >= 1
            if object_like and it['kind'] != 'track':
                if rx > 1 + TOL and not repeating and not bays:
                    defects.append(f'repete {rx:.2f}x en largeur')
                if rx < 1 - TOL and not repeating:
                    defects.append(f'coupe en largeur ({W:g} u sur {ew:g})')
                if ry > 1 + TOL:
                    defects.append(f'repete {ry:.2f}x en hauteur')
                if ry < 1 - TOL:
                    defects.append(f'coupe en hauteur ({H:g} u sur {eh:g})')
                if abs(sx / sy - 1) > 0.12:
                    defects.append(f'etire (echelle {sx:g} x {sy:g})')
                first = rec['offsetx'][0]
                if not repeating and abs(first % ew) > 0.5 and abs(first % ew - ew) > 0.5:
                    defects.append(f'decalage horizontal {first:g}')
            if it['kind'] == 'track' and DOORLIKE.match(it['tex']) and not repeating:
                defects.append('image de porte sur un montant')
        rec['defects'] = defects
        return rec


def audit(wads, names=None):
    db = texture_db()
    stags = script_tags()
    out = []
    for wad in sorted(wads):
        name = wad.stem.upper()
        if names and name not in names:
            continue
        text = dict(lumps(wad)).get('TEXTMAP')
        if text is None:
            print(f'{name}: pas de TEXTMAP (format non UDMF) - non inspecte')
            continue
        m = Map(name, text.decode('utf-8', 'replace'), db, stags)
        recs = m.surfaces()
        for li, pname in m.poly:
            recs.append(dict(map=name, kind='polyobject', lines=[li], mechanism=[pname], defects=[], tex='-', part='-', W=0, H=0))
        out += recs
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--maps', default='')
    ap.add_argument('--wads', default=str(ROOT / 'src' / 'maps'))
    ap.add_argument('--extra', nargs='*', default=[], help='other wads (bench maps)')
    ap.add_argument('--out', default=str(ROOT / 'build' / 'door_audit.json'))
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    names = {n.strip().upper() for n in a.maps.split(',') if n.strip()} or None
    wads = list(Path(a.wads).glob('*.wad')) + [Path(e) for e in a.extra]
    recs = audit(wads, names)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(recs, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    per = {}
    for r in recs:
        p = per.setdefault(r['map'], [0, 0])
        p[0] += 1
        p[1] += bool(r['defects'])
        if r['defects'] and not a.quiet:
            print(f"{r['map']} {r['kind']:9s} s{r.get('sector')} l{r['lines'][0]} {r['tex']:9s} {r['part']:6s} "
                  f"{r['W']:g}x{r['H']:g} tex {r.get('tex_world')} : {'; '.join(r['defects'])}")
    for mname in sorted(per):
        print(f'{mname}: {per[mname][0]} surfaces, {per[mname][1]} avec defaut')
    print(f'total: {len(recs)} surfaces, {sum(bool(r["defects"]) for r in recs)} avec defaut -> {a.out}')


if __name__ == '__main__':
    main()
