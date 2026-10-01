#!/usr/bin/env python3
"""Cell-grid UDMF authoring kit for RF2 production maps.

A map is authored as boxes of 16-unit cells (floor/ceiling heights, textures, light, role),
doors, windows, rails, wall faces, decor lines, walk triggers and things. The kit derives sectors
(connected identical cells), merges collinear edges into linedefs, assigns textures and pegging
by rule, writes a ZDoom-namespace TEXTMAP inside a PWAD and can render a plan PNG and check
reachability. The produced WAD is a normal UDMF map: UDB can open and edit it afterwards.

This is not a level generator: every box, door and thing is placed explicitly by the map script.
"""
from dataclasses import dataclass, replace
from collections import deque
import struct, json, math, re

UNIT = 16
DIRS = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
PLAYER_HEIGHT = 56
STEP = 24


def texture_scales(path):
    """{name: YScale} of the textures and flats of a TEXTURES lump. A sign on a decor line needs the scale of the file
    actually shipped (Opus's stand-ins are 4 pixels per unit, some of Astra's replacements 8)."""
    scales, name = {}, None
    for line in open(path, encoding='utf-8'):
        head = re.match(r'\s*(?:Texture|WallTexture|Flat)\s+"?(\w+)"?\s*,', line)
        if head:
            name = head.group(1).upper()
            scales[name] = 1.0
            continue
        ys = re.match(r'\s*YScale\s+([\d.]+)', line)
        if ys and name:
            scales[name] = float(ys.group(1))
    return {k: (int(v) if v == int(v) else v) for k, v in scales.items()}


@dataclass(frozen=True)
class Cell:
    floor: int = 0
    ceil: int = 128
    ftex: str = 'RFF_CER'
    ctex: str = 'RFP_CEIL'
    light: int = 160
    wall: str = 'RFP_DADB'
    lower: str = ''        # riser texture shown to lower neighbours ('' = neighbour's wall)
    upper: str = ''        # texture above this cell's ceiling shown to taller neighbours
    mid: str = ''          # masked middle texture on boundary lines (windows, rails)
    track: str = ''        # one-sided reveal texture of door cells
    tag: int = 0
    special: int = 0
    color: int = 0         # sector lightcolor, 0 = white
    role: str = 'floor'    # floor | door | window | rail
    door: tuple = ()       # (kind, speed, delay, lock, lockside)
    extra: tuple = ()      # extra UDMF sector fields as ((key, value), ...)
    env: tuple = ()        # reverb environment (id1, id2) of the sound zone, () = engine default
    slabs: tuple = ()      # solid 3D floors in this cell: ((z0, z1, side, top, bottom), ...) - see slab()


def _val(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, float):
        return repr(v)
    return str(v)


def _block(kind, d):
    return kind + '\n{\n' + ''.join(f'  {k} = {_val(v)};\n' for k, v in d.items() if v is not None) + '}\n'


class MapBuilder:
    def __init__(self, name):
        self.name = name
        self.cells = {}
        self.things = []
        self.faces = {}       # (cx, cy, dir) -> props override for that cell edge
        self.decor = []       # standalone two-sided lines
        self.labels = []      # (x, y, text) for the plan
        self.notes = []       # free text for the plan legend
        self.start = None
        self.exit_cells = set()

    # ------------------------------------------------------------------ authoring
    @staticmethod
    def _cells(x0, y0, x1, y1):
        for x in range(x0, x1):
            for y in range(y0, y1):
                yield (x, y)

    def _range(self, x0, y0, x1, y1):
        assert x0 % UNIT == 0 and y0 % UNIT == 0 and x1 % UNIT == 0 and y1 % UNIT == 0, (x0, y0, x1, y1)
        assert x1 > x0 and y1 > y0, (x0, y0, x1, y1)
        return x0 // UNIT, y0 // UNIT, x1 // UNIT, y1 // UNIT

    def box(self, x0, y0, x1, y1, cell=None, only_empty=False, **kw):
        """Fill a rectangle (world units) with a cell descriptor. kw overrides fields of `cell`."""
        c = replace(cell, **kw) if cell is not None else Cell(**kw)
        for p in self._cells(*self._range(x0, y0, x1, y1)):
            if only_empty and p in self.cells:
                continue
            self.cells[p] = c
        return c

    def carve(self, x0, y0, x1, y1):
        """Make a rectangle solid (remove cells)."""
        for p in self._cells(*self._range(x0, y0, x1, y1)):
            self.cells.pop(p, None)

    def modify(self, x0, y0, x1, y1, **kw):
        """Change fields of existing cells in a rectangle."""
        for p in self._cells(*self._range(x0, y0, x1, y1)):
            if p in self.cells:
                self.cells[p] = replace(self.cells[p], **kw)

    def raise_block(self, x0, y0, x1, y1, height, ftex, lower, cell=None, **kw):
        """Furniture-like solid block: floor raised by `height` over the surrounding cell."""
        base = cell if cell is not None else self.cells[self._range(x0, y0, x1, y1)[:2]]
        self.box(x0, y0, x1, y1, base, floor=base.floor + height, ftex=ftex, lower=lower, **kw)

    def door(self, x0, y0, x1, y1, tag, tex, track, base, kind='raise', speed=16, delay=150,
             lock=0, lockside='', light=None):
        """Door sector (closed: ceiling at floor). lockside: 'N','S','E','W' = side of the room whose
        line is locked; '' = all sides locked. kind: raise | open."""
        self.box(x0, y0, x1, y1, base, ceil=base.floor, wall=tex, track=track, tag=tag, role='door',
                 door=(kind, speed, delay, lock, lockside), light=light if light is not None else base.light,
                 mid='', upper='', lower='')

    def window(self, x0, y0, x1, y1, base, sill, lintel, tex='RFG_WIN', wall=None, lower='RFP_PLN', light=None):
        self.box(x0, y0, x1, y1, base, floor=sill, ceil=lintel, mid=tex, role='window',
                 wall=wall or base.wall, lower=lower, upper='', light=light if light is not None else base.light)

    def rail(self, x0, y0, x1, y1, base, tex):
        self.box(x0, y0, x1, y1, base, mid=tex, role='rail')

    def slab(self, x0, y0, x1, y1, z0, z1, side, top=None, bottom=None, alpha=255):
        """Solid 3D floor between z0 and z1 in the existing cells of the rectangle (Sector_Set3DFloor, type
        solid): a vehicle body or a roof with open sky above it, a bridge deck over water, a mezzanine. side is
        the texture of its faces, top/bottom of its upper and lower surfaces. A cell may hold several slabs
        (a window between a sill slab and a lintel slab). Tags and control sectors are assigned at build.
        alpha 0: the slab is not drawn but stays solid (the collision of a model that shows the object)."""
        spec = (int(z0), int(z1), side, top or side, bottom or top or side)
        if alpha != 255:
            spec += (int(alpha),)
        for p in self._cells(*self._range(x0, y0, x1, y1)):
            if p in self.cells:
                c = self.cells[p]
                self.cells[p] = replace(c, slabs=tuple(sorted(c.slabs + (spec,))))

    @staticmethod
    def surfaces(c):
        """Heights a player can stand at in a cell: its floor and the tops of its slabs, each with 56 units of
        headroom under the next slab or the ceiling."""
        out = []
        for z in [c.floor] + [s[1] for s in c.slabs]:
            if any(a < z + PLAYER_HEIGHT and b > z for (a, b, *_) in c.slabs):
                continue
            above = [a for (a, b, *_) in c.slabs if a >= z] + [c.ceil]
            if min(above) - z >= PLAYER_HEIGHT:
                out.append(z)
        return out

    def face(self, x0, y0, x1, y1, side, **props):
        """Override sidedef/line props on the `side` edges of cells in the rectangle: texture, offsets, blocking,
        special/args/flags (a use line, Line_Mirror) and fields (extra UDMF line fields such as user_scene)."""
        for (cx, cy) in self._cells(*self._range(x0, y0, x1, y1)):
            self.faces[(cx, cy, side)] = props

    def decor_line(self, x0, y0, x1, y1, tex, zbottom=None, blocking=False, offsety=0, yscale=None, texwidth=None,
                   **flags):
        """Two-sided line inside one sector carrying a masked middle texture (signs, rails).

        yscale: the texture's YScale. Given, the texture's bottom is put at zbottom as the engine reads it: with
        the middle texture pegged to the floor, a positive row offset raises it, in texture pixels (height in map
        units x YScale). Not given: the legacy offset, negative and unscaled, which the engine draws below the
        intended height (RF01 as accepted on 27/09 used it: its plaques were not visible; RF01-PAN, 28/09, no longer).
        texwidth: the texture's width in map units. Given, the whole texture is fitted on the line (sidedef
        scalex_mid), which is 2 units shorter at each end than asked; not given, its last 4 units are cut."""
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        ix, iy = 2 * dx / L, 2 * dy / L
        self.decor.append(dict(x0=x0 + ix, y0=y0 + iy, x1=x1 - ix, y1=y1 - iy, tex=tex, zbottom=zbottom, blocking=blocking,
                               offsety=offsety, yscale=yscale, texwidth=texwidth, flags=flags))

    def trigger(self, x0, y0, x1, y1, special, args=(), repeat=False, monster=False, objective=0, fields=None):
        """Invisible walk-over line inside one sector. objective > 0 is written as the UDMF field
        user_objective, read by the level director (RFDirector) when the line fires."""
        # Endpoints are pulled 2 units inward so they never touch a wall line.
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        ix, iy = 2 * dx / L, 2 * dy / L
        self.decor.append(dict(x0=x0 + ix, y0=y0 + iy, x1=x1 - ix, y1=y1 - iy, tex='', special=special, args=list(args) + [0] * (5 - len(args)),
                               repeat=repeat, monster=monster, playercross=True, objective=objective, fields=fields or {}))

    def thing(self, x, y, type_, angle=0, args=(), tid=0, z=0, skill='all', dormant=False, ambush=False, extra=None):
        d = dict(x=float(x), y=float(y), height=float(z), angle=int(angle), type=int(type_))
        if tid:
            d['id'] = tid
        for i, a in enumerate(args):
            if a:
                d[f'arg{i}'] = int(a)
        if skill == 'all':
            flags = (True, True, True, True, True)
        elif skill == 'hard':
            flags = (False, False, False, True, True)
        elif skill == 'normal+':
            flags = (False, False, True, True, True)
        else:
            flags = tuple(skill)
        for i, f in enumerate(flags):
            d[f'skill{i + 1}'] = f
        d['single'] = True
        d['coop'] = True
        d['dm'] = False
        if dormant:
            d['dormant'] = True
        if ambush:
            d['ambush'] = True
        if extra:
            d.update(extra)
        self.things.append(d)
        if type_ == 1:
            self.start = (x, y)
        return d

    def label(self, x, y, text):
        self.labels.append((x, y, text))

    def cell_at(self, x, y):
        return self.cells.get((int(math.floor(x / UNIT)), int(math.floor(y / UNIT))))

    # ------------------------------------------------------------------ geometry
    def _sectors(self):
        sector_of = {}
        sectors = []
        for p in sorted(self.cells):
            if p in sector_of:
                continue
            d = self.cells[p]
            idx = len(sectors)
            sectors.append(d)
            stack = [p]
            sector_of[p] = idx
            while stack:
                u = stack.pop()
                for dx, dy in DIRS.values():
                    v = (u[0] + dx, u[1] + dy)
                    if v not in sector_of and self.cells.get(v) == d:
                        sector_of[v] = idx
                        stack.append(v)
        return sectors, sector_of

    def _edge_geometry(self, p, d):
        x, y = p
        if d == 'N':
            return (x, y + 1), (x + 1, y + 1)
        if d == 'E':
            return (x + 1, y + 1), (x + 1, y)
        if d == 'S':
            return (x + 1, y), (x, y)
        return (x, y), (x, y + 1)

    def _door_special(self, dcell, side_of_room):
        kind, speed, delay, lock, lockside = dcell.door
        locked = lock > 0 and (lockside == '' or lockside == side_of_room)
        if locked:
            return 13, [dcell.tag, speed, delay, lock, 0], dict(playeruse=True, playeruseback=True, repeatspecial=True)
        if kind == 'open':
            return 11, [dcell.tag, speed, 0, 0, 0], dict(playeruse=True, playeruseback=True, repeatspecial=False, monsteractivate=True)
        return 12, [dcell.tag, speed, delay, 0, 0], dict(playeruse=True, playeruseback=True, repeatspecial=True, monsteractivate=True)

    def _edge_props(self, pa, da, sa, pb, sb):
        """Sidedef/line properties for the edge on side `da` of cell pa (front) toward pb (back)."""
        A = self.cells[pa]
        fs = {'sector': sa}
        ls = {}
        face = self.faces.get((pa[0], pa[1], da))
        if pb is None:
            tex = A.track if A.role == 'door' else A.wall
            if face and 'texture' in face:
                tex = face['texture']
            fs['texturemiddle'] = tex
            ls['blocking'] = True
            if A.role == 'door':
                ls['dontpegtop'] = True
            else:
                ls['dontpegbottom'] = True
            if face:
                for k in ('offsetx', 'offsety'):
                    if k in face:
                        fs[k] = face[k]
                if 'special' in face:
                    ls['special'] = face['special']
                    for i, a in enumerate(face.get('args', ())):
                        ls[f'arg{i}'] = a
                    for k, v in face.get('flags', {}).items():
                        ls[k] = v
                for k, v in face.get('fields', {}).items():
                    ls[k] = v
            return fs, None, ls
        B = self.cells[pb]
        bs = {'sector': sb}
        ls['twosided'] = True
        faceb = self.faces.get((pb[0], pb[1], OPP[da]))
        # lowers / uppers from A's view
        if B.floor > A.floor:
            fs['texturebottom'] = B.lower or A.wall
        if B.ceil < A.ceil:
            fs['texturetop'] = B.wall if B.role == 'door' else (B.upper or A.wall)
        # lowers / uppers from B's view
        if A.floor > B.floor:
            bs['texturebottom'] = A.lower or B.wall
        if A.ceil < B.ceil:
            bs['texturetop'] = A.wall if A.role == 'door' else (A.upper or B.wall)
        if (B.ceil < A.ceil and B.role != 'door') or (A.ceil < B.ceil and A.role != 'door'):
            ls['dontpegtop'] = True
        # masked middles
        mid = B.mid or A.mid
        if mid:
            fs['texturemiddle'] = mid
            bs['texturemiddle'] = mid
            ls['blocking'] = True
            ls['clipmidtex'] = True
        if face and 'texture' in face:
            fs['texturemiddle'] = face['texture']
            ls['clipmidtex'] = True
            if face.get('blocking'):
                ls['blocking'] = True
        if faceb and 'texture' in faceb:
            bs['texturemiddle'] = faceb['texture']
            ls['clipmidtex'] = True
        # a use special and scene fields on a two-sided edge (a raised block's side, a window), from either side
        for f in (face, faceb):
            if not f:
                continue
            if 'special' in f:
                ls['special'] = f['special']
                for i, a in enumerate(f.get('args', ())):
                    ls[f'arg{i}'] = a
                for k, v in f.get('flags', {}).items():
                    ls[k] = v
            for k, v in f.get('fields', {}).items():
                ls[k] = v
        # door activation
        if A.role == 'door' and B.role != 'door':
            special, args, flags = self._door_special(A, da)
            ls.update(flags)
            ls['special'] = special
            for i, a in enumerate(args):
                ls[f'arg{i}'] = a
        elif B.role == 'door' and A.role != 'door':
            special, args, flags = self._door_special(B, OPP[da])
            ls.update(flags)
            ls['special'] = special
            for i, a in enumerate(args):
                ls[f'arg{i}'] = a
        if A.role in ('window', 'rail') or B.role in ('window', 'rail'):
            ls['blocking'] = True
            ls['blockmonsters'] = True
        if A.env != B.env:
            ls['zoneboundary'] = True     # reverb zones follow the spaces (see sound_zones)
        return fs, bs, ls

    def sound_zones(self):
        """One SoundEnvironment thing (ednum 9048) per connected zone of cells sharing an env."""
        seen, things = set(), []
        for p in sorted(self.cells):
            env = self.cells[p].env
            if p in seen or not env:
                continue
            stack, zone = [p], []
            seen.add(p)
            while stack:
                u = stack.pop()
                zone.append(u)
                for dx, dy in DIRS.values():
                    v = (u[0] + dx, u[1] + dy)
                    if v not in seen and v in self.cells and self.cells[v].env == env:
                        seen.add(v)
                        stack.append(v)
            floor_cells = [c for c in zone if self.cells[c].role == 'floor'] or zone
            cx, cy = floor_cells[len(floor_cells) // 2]
            things.append(dict(x=float(cx * UNIT + UNIT / 2), y=float(cy * UNIT + UNIT / 2), height=0.0, angle=0,
                               type=9048, arg0=env[0], arg1=env[1], skill1=True, skill2=True, skill3=True,
                               skill4=True, skill5=True, single=True, coop=True, dm=True))
        return things

    def _tag_slabs(self):
        """Give every distinct slab set its own sector tag (4000+); the control sectors refer to it."""
        specs = sorted({c.slabs for c in self.cells.values() if c.slabs})
        self.slab_tags = {spec: 4000 + i for i, spec in enumerate(specs)}
        for p, c in list(self.cells.items()):
            if c.slabs:
                tag = self.slab_tags[c.slabs]
                assert c.tag in (0, tag) and c.role != 'door', ('slab on a tagged or door cell', p)
                if c.tag != tag:
                    self.cells[p] = replace(c, tag=tag)

    def build(self):
        self._tag_slabs()
        sectors, sector_of = self._sectors()
        edges = {}
        touch = {}  # vertex -> set of axes ('h'/'v') of incident boundary edges
        for p in sorted(self.cells):
            for d, (dx, dy) in DIRS.items():
                q = (p[0] + dx, p[1] + dy)
                sb = sector_of.get(q)
                if sb is not None and sb == sector_of[p]:
                    continue
                v1, v2 = self._edge_geometry(p, d)
                key = frozenset((v1, v2))
                if key in edges:
                    continue
                fs, bs, ls = self._edge_props(p, d, sector_of[p], q if sb is not None else None, sb)
                edges[key] = dict(v1=v1, v2=v2, fs=fs, bs=bs, ls=ls, axis='h' if v1[1] == v2[1] else 'v')
                for v in (v1, v2):
                    touch.setdefault(v, set()).add(edges[key]['axis'])
        # group edges by (axis, line coordinate, signature) and merge collinear runs
        def sig(e):
            return (e['axis'], e['v1'][1] if e['axis'] == 'h' else e['v1'][0],
                    json.dumps(e['fs'], sort_keys=True), json.dumps(e['bs'], sort_keys=True), json.dumps(e['ls'], sort_keys=True))
        groups = {}
        for e in edges.values():
            groups.setdefault(sig(e), []).append(e)
        lines = []
        for key, es in groups.items():
            axis = key[0]
            coord = 0 if axis == 'h' else 1
            es.sort(key=lambda e: min(e['v1'][coord], e['v2'][coord]))
            run = [es[0]]
            def flush(run):
                a, b = run[0], run[-1]
                # keep the edge direction (front side stays on the right of v1->v2)
                if a['v2'][coord] > a['v1'][coord]:
                    v1, v2 = a['v1'], b['v2']
                else:
                    v1, v2 = b['v1'], a['v2']
                lines.append(dict(v1=v1, v2=v2, fs=a['fs'], bs=a['bs'], ls=a['ls']))
            for e in es[1:]:
                prev = run[-1]
                lo_prev = max(prev['v1'][coord], prev['v2'][coord])
                lo_e = min(e['v1'][coord], e['v2'][coord])
                shared = prev['v1'] if prev['v1'][coord] == lo_prev else prev['v2']
                junction = ('h' in touch.get(shared, set()) and 'v' in touch.get(shared, set()))
                if lo_e == lo_prev and not junction:
                    run.append(e)
                else:
                    flush(run)
                    run = [e]
            flush(run)
        # emit UDMF
        verts = []
        vindex = {}

        def vertex(v):
            if v not in vindex:
                vindex[v] = len(verts)
                verts.append(dict(x=v[0] * UNIT, y=v[1] * UNIT))
            return vindex[v]
        sides = []
        out_lines = []
        for L in sorted(lines, key=lambda l: (l['v1'], l['v2'])):
            sid = len(sides)
            sides.append(L['fs'])
            d = dict(v1=vertex(L['v1']), v2=vertex(L['v2']), sidefront=sid)
            if L['bs'] is not None:
                sides.append(L['bs'])
                d['sideback'] = sid + 1
            d.update(L['ls'])
            out_lines.append(d)
        # decor lines and triggers
        problems = []
        for dl in self.decor:
            mid = ((dl['x0'] + dl['x1']) / 2, (dl['y0'] + dl['y1']) / 2)
            cp = (int(math.floor(mid[0] / UNIT)), int(math.floor(mid[1] / UNIT)))
            assert cp in self.cells, ('decor line outside cells', dl)
            s = sector_of[cp]
            # every sample along the line (including endpoints) must be inside the same sector and off the grid lines
            n = max(2, int(math.hypot(dl['x1'] - dl['x0'], dl['y1'] - dl['y0']) / 4))
            for k in range(n + 1):
                sx = dl['x0'] + (dl['x1'] - dl['x0']) * k / n
                sy = dl['y0'] + (dl['y1'] - dl['y0']) * k / n
                sp = (int(math.floor(sx / UNIT)), int(math.floor(sy / UNIT)))
                if sector_of.get(sp) != s:
                    problems.append(('decor line crosses sectors', dl, (sx, sy)))
                    break
            for (ex, ey) in ((dl['x0'], dl['y0']), (dl['x1'], dl['y1'])):
                assert ex % UNIT != 0 or ey % UNIT != 0 or True
                assert not (abs(ex / UNIT - round(ex / UNIT)) < 1e-9 and abs(ey / UNIT - round(ey / UNIT)) < 1e-9), ('decor endpoint on grid vertex', dl)
            c = self.cells[cp]
            def fvertex(x, y):
                key = ('f', x, y)
                if key not in vindex:
                    vindex[key] = len(verts)
                    verts.append(dict(x=float(x), y=float(y)))
                return vindex[key]
            fs = {'sector': s}
            bs = {'sector': s}
            d = dict(v1=fvertex(dl['x0'], dl['y0']), v2=fvertex(dl['x1'], dl['y1']), sidefront=len(sides), sideback=len(sides) + 1, twosided=True)
            if dl.get('tex'):
                fs['texturemiddle'] = dl['tex']
                bs['texturemiddle'] = dl['tex']
                d['clipmidtex'] = True
                if dl.get('zbottom') is not None:
                    d['dontpegbottom'] = True
                    if dl.get('yscale') is None:
                        off = -(dl['zbottom'] - c.floor)
                    else:
                        off = (dl['zbottom'] - c.floor) * dl['yscale']
                    fs['offsety'] = off
                    bs['offsety'] = off
                if dl.get('texwidth'):
                    fit = round(dl['texwidth'] / math.hypot(dl['x1'] - dl['x0'], dl['y1'] - dl['y0']), 6)
                    fs['scalex_mid'] = fit
                    bs['scalex_mid'] = fit
                if dl.get('offsety'):
                    fs['offsety'] = fs.get('offsety', 0) + dl['offsety']
                    bs['offsety'] = bs.get('offsety', 0) + dl['offsety']
                if dl.get('blocking'):
                    d['blocking'] = True
                    d['blockmonsters'] = True
                for k, v in dl.get('flags', {}).items():
                    d[k] = v
            if dl.get('special'):
                d['special'] = dl['special']
                for i, a in enumerate(dl['args']):
                    if a:
                        d[f'arg{i}'] = a
                d['playercross'] = True
                d['repeatspecial'] = bool(dl.get('repeat'))
                if dl.get('objective'):
                    d['user_objective'] = int(dl['objective'])
                for k, val in dl.get('fields', {}).items():
                    d[k] = val
                if dl.get('monster'):
                    d['monstercross'] = True
            sides.append(fs)
            sides.append(bs)
            out_lines.append(d)
        if problems:
            raise AssertionError(chr(10).join(str(p) for p in problems))
        sector_dicts = []
        for c in sectors:
            d = dict(heightfloor=c.floor, heightceiling=c.ceil, texturefloor=c.ftex, textureceiling=c.ctex,
                     lightlevel=c.light, id=c.tag, special=c.special)
            if c.color:
                d['lightcolor'] = c.color
            for k, v in c.extra:
                d[k] = v
            sector_dicts.append(d)
        # 3D floor control sectors: one closed square per slab, outside the map, whose floor/ceiling are the
        # slab's bottom/top; its first line carries Sector_Set3DFloor(tag, solid, no light effects, opaque).
        if self.slab_tags:
            cx0 = (min(p[0] for p in self.cells) - 32) * UNIT
            cy0 = (min(p[1] for p in self.cells) - 32) * UNIT
            k = 0
            for spec, tag in sorted(self.slab_tags.items(), key=lambda kv: kv[1]):
                for (z0, z1, side, top, bottom, *rest) in spec:
                    alpha = rest[0] if rest else 255
                    x, y, size = cx0 - (k % 64) * 48, cy0 - (k // 64) * 48, 32
                    base = len(verts)
                    for (vx, vy) in ((x, y), (x, y + size), (x + size, y + size), (x + size, y)):
                        verts.append(dict(x=float(vx), y=float(vy)))
                    sec = len(sector_dicts)
                    sector_dicts.append(dict(heightfloor=z0, heightceiling=z1, texturefloor=bottom, textureceiling=top,
                                             lightlevel=160, id=0, special=0))
                    for e in range(4):
                        sides.append(dict(sector=sec, texturemiddle=side))
                        d = dict(v1=base + e, v2=base + (e + 1) % 4, sidefront=len(sides) - 1, blocking=True)
                        if e == 0:
                            # An invisible slab (alpha 0) is the collision of a model the player sees: it blocks
                            # bodies but lets shots through (type 1 + 32, shootability inverted), or a tram window
                            # or an open frame would stop bullets on nothing (RF02 audit, 01/10).
                            d.update(special=160, arg0=tag, arg1=33 if alpha == 0 else 1, arg2=1, arg3=alpha)
                        out_lines.append(d)
                    k += 1
        text = f'// {self.name} - Red Flags 2 production map. Authored with scripts/mapkit (cell grid {UNIT}).\n'
        text += 'namespace = "zdoom";\n\n'
        things = self.things + self.sound_zones()
        for kind, items in (('vertex', verts), ('sector', sector_dicts), ('sidedef', sides), ('linedef', out_lines), ('thing', things)):
            text += '\n'.join(_block(kind, d) for d in items) + '\n'
        self.stats = dict(sectors=len(sectors), vertices=len(verts), linedefs=len(out_lines), sidedefs=len(sides), things=len(self.things))
        self._sector_of = sector_of
        return text

    def wad(self, text):
        lumps = [(self.name, b''), ('TEXTMAP', text.encode('utf-8')), ('ENDMAP', b'')]
        out = bytearray(b'PWAD' + struct.pack('<ii', len(lumps), 0))
        directory = []
        for name, data in lumps:
            directory.append(struct.pack('<ii8s', len(out), len(data), name.encode().ljust(8, b'\0')))
            out.extend(data)
        struct.pack_into('<i', out, 8, len(out))
        out.extend(b''.join(directory))
        return bytes(out)

    # ------------------------------------------------------------------ validation
    def passable(self, p):
        c = self.cells.get(p)
        if c is None or c.role in ('window', 'rail'):
            return False
        if c.role == 'door':
            return True
        if c.slabs:
            return bool(self.surfaces(c))
        return c.ceil - c.floor >= PLAYER_HEIGHT

    def _stand(self, c, z_from):
        """Surface of cell c reached by a step from height z_from (None when no surface is within a step)."""
        if c.role == 'door':
            return c.floor             # a door is entered whatever its height (as before slabs)
        best = None
        for z in (self.surfaces(c) if c.slabs else [c.floor]):
            if abs(z - z_from) <= STEP and (best is None or abs(z - z_from) < abs(best - z_from)):
                best = z
        return best

    def reachable(self, keys=(), open_tags=()):
        """BFS over cells from the player start. keys: lock numbers considered opened.
        Locked door cells are entered only when the lock is in keys, or from the unlocked side."""
        start = (int(self.start[0] // UNIT), int(self.start[1] // UNIT))
        c0 = self.cells[start]
        z0 = self._stand(c0, c0.floor)
        dist = {start: 0}
        seen = {(start, z0)}
        q = deque([(start, z0)])
        while q:
            u, zu = q.popleft()
            for d, (dx, dy) in DIRS.items():
                v = (u[0] + dx, u[1] + dy)
                if not self.passable(v):
                    continue
                cv = self.cells[v]
                if cv.role == 'door':
                    kind, speed, delay, lock, lockside = cv.door
                    if lock and lock not in keys and cv.tag not in open_tags:
                        # entering from side `d` of the door means the room is on OPP[d]
                        if lockside == '' or lockside == OPP[d]:
                            continue
                zv = self._stand(cv, zu)
                if zv is None or (v, zv) in seen:
                    continue
                seen.add((v, zv))
                dist.setdefault(v, dist[u] + 1)
                q.append((v, zv))
        return dist

    def _touchable(self, t, dist):
        """A thing counts as reachable when its cell or a neighbouring cell is walkable (items on tables)."""
        p = (int(t['x'] // UNIT), int(t['y'] // UNIT))
        if p in dist:
            return True
        return any((p[0] + dx, p[1] + dy) in dist for dx, dy in DIRS.values())

    def check(self, key_items, exit_cells, winch_cell=None, winch_tag=None, decor_types=()):
        """Iterate reachability, collecting keys from reachable item things. Returns a report. decor_types:
        thing types that are only dressing (a mattress on a handcart) and need not be reachable."""
        keys = set()
        open_tags = set()
        for _ in range(6):
            dist = self.reachable(keys, open_tags)
            gained = False
            for t in self.things:
                lock = key_items.get(t['type'])
                if lock and self._touchable(t, dist) and lock not in keys:
                    keys.add(lock)
                    gained = True
            if winch_cell is not None and winch_tag is not None and winch_cell in dist and winch_tag not in open_tags:
                open_tags.add(winch_tag)
                gained = True
            if not gained:
                break
        unreachable = [(t['type'], t['x'], t['y']) for t in self.things
                       if not self._touchable(t, dist) and t['type'] not in (30901, 30902, 30601, 30602, 30611, 30315) + tuple(decor_types)]
        exit_ok = any(c in dist for c in exit_cells)
        exit_dist = min((dist[c] for c in exit_cells if c in dist), default=None)
        return dict(reachable_cells=len(dist), keys=sorted(keys), exit_reachable=exit_ok,
                    exit_path_units=None if exit_dist is None else exit_dist * UNIT, unreachable_things=unreachable)

    # ------------------------------------------------------------------ plan
    def plan_png(self, path, scale=0.5):
        from PIL import Image, ImageDraw, ImageFont
        xs = [p[0] for p in self.cells]
        ys = [p[1] for p in self.cells]
        minx, maxx = min(xs) - 4, max(xs) + 5
        miny, maxy = min(ys) - 4, max(ys) + 5
        px = int(UNIT * scale)
        W = (maxx - minx) * px
        H = (maxy - miny) * px + 40
        img = Image.new('RGB', (W, H), (18, 20, 24))
        d = ImageDraw.Draw(img)

        def xy(cx, cy):
            return (cx - minx) * px, 20 + (maxy - cy - 1) * px
        for p, c in self.cells.items():
            x, y = xy(*p)
            if c.role == 'door':
                col = (200, 140, 60) if not c.door[3] else (70, 120, 220)
            elif c.role == 'window':
                col = (90, 170, 200)
            elif c.role == 'rail':
                col = (150, 150, 90)
            elif c.ctex == 'F_SKY1':
                col = (110, 118, 100)
            else:
                h = c.floor
                base = 96 + max(-96, min(96, h)) // 2
                col = (base, base + 6, base + 16)
                if c.ceil - c.floor < PLAYER_HEIGHT:
                    col = (60, 50, 44)
            d.rectangle([x, y, x + px - 1, y + px - 1], fill=col)
        for dl in self.decor:
            a = xy(dl['x0'] / UNIT, dl['y0'] / UNIT)
            b = xy(dl['x1'] / UNIT, dl['y1'] / UNIT)
            d.line([a, b], fill=(240, 90, 90) if dl.get('special') else (240, 220, 120), width=2)
        for t in self.things:
            x, y = xy(t['x'] / UNIT, t['y'] / UNIT)
            ty = t['type']
            if ty == 1:
                col, r = (90, 240, 120), 5
            elif 30401 <= ty <= 30403:
                col, r = (240, 70, 70), 4
            elif ty in (30901, 30902):
                col, r = (120, 200, 255), 2
            elif ty in (30601, 30602, 30611, 30315):
                col, r = (250, 230, 120), 1
            else:
                col, r = (120, 230, 120), 3
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        try:
            font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
        except OSError:
            font = ImageFont.load_default()
        for (lx, ly, text) in self.labels:
            x, y = xy(lx / UNIT, ly / UNIT)
            d.text((x + 1, y + 1), text, fill=(0, 0, 0), font=font)
            d.text((x, y), text, fill=(250, 240, 220), font=font)
        d.text((6, H - 18), f'{self.name} plan: cells {len(self.cells)}  ' + '  '.join(self.notes), fill=(200, 200, 200), font=font)
        img.save(path)
        return path
