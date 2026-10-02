#!/usr/bin/env python3
"""Door openings built as architecture (door pass of 02/10/2026): works on the UDMF structures of a map (lists of
vertex, sector, sidedef and linedef dictionaries), for the maps of the kit and for any other UDMF map.

frame_doors(): a door sector is a slab the whole height of the rooms it joins, so its face was as high as each room:
a door image cut at the top in a low room, repeated above itself in a high one, and of two different heights on its
two sides. Each standard door (a rectangle between two rooms, or against one room, its two ends in the wall) is
rebuilt as

    room | frame strip | door leaf | frame strip | room          (the strips: FRAME units deep, inside the old door cell)

The strips are fixed sectors whose ceiling is the door's head: above it the room shows its own wall (a lintel, fixed,
aligned with the wall beside it); the leaf's face is then exactly width x head on both sides and gets the image
fitted to that size (doors.fit); its jambs are fixed and show the track material. The leaf keeps its tag, its special
and its lock; the use lines stay where they were and the leaf's own faces carry them too. Rooms, collisions and the
door's footprint do not change.

fit_static(): one-sided faces that carry a door image (shut doors that are part of a wall) get the image fitted to
the face, with the wall's material above the door's head when the wall is higher.
"""
import math, re
from pathlib import Path
import doors

ROOT = Path(__file__).resolve().parents[2]
FRAME = 4
USE_KEYS = ('special', 'arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'playeruse', 'playeruseback', 'repeatspecial',
            'monsteractivate', 'monsteruse', 'locknumber', 'secret')
_TEXINFO = None


def tex_info(name):
    """(world width, world height, x scale, y scale) of a wall texture, or None."""
    global _TEXINFO
    if _TEXINFO is None:
        _TEXINFO = {}
        from PIL import Image
        for p in (ROOT / 'src' / 'textures').glob('*.png'):
            w, h = Image.open(p).size
            _TEXINFO[p.stem.upper()] = (float(w), float(h), 1.0, 1.0)
        for tf in sorted((ROOT / 'src').glob('TEXTURES.*')):
            t = tf.read_text(encoding='utf-8', errors='replace')
            for m in re.finditer(r'(?:Texture|WallTexture)\s+"?(\w+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{(.*?)\n\}', t, re.S):
                xs = re.search(r'XScale\s+([\d.]+)', m.group(4))
                ys = re.search(r'YScale\s+([\d.]+)', m.group(4))
                xs, ys = (float(xs.group(1)) if xs else 1.0), (float(ys.group(1)) if ys else 1.0)
                _TEXINFO[m.group(1).upper()] = (int(m.group(2)) / xs, int(m.group(3)) / ys, xs, ys)
    return _TEXINFO.get(name.upper())


def head_height(tex, width, clear):
    """Height of a door's head for its image, its width and the clear height available (multiple of 8)."""
    w, h = doors.natural(tex)
    kind = doors.CATALOG[tex][4]
    limit = h
    if kind == 'bars':
        limit = h * 1.25                               # a gate's bars may be drawn longer
        if limit < clear < limit + 24 and clear <= h * 1.5:
            limit = clear                              # rather than a strip of wall a few units high above it
    elif kind == 'panel' and width < w:
        limit = min(h, 2.25 * width)                   # a narrower leaf is not left as tall as the wide one
    return int(min(limit, clear) // 8 * 8)


def lintel_offset(wall, alias, rise):
    """Row offset of a bottom-pegged upper texture so that it shows, `rise` units above the room's floor, the row the
    wall beside it (anchored to that floor) shows there."""
    info = tex_info(alias.get(wall, wall))
    return round(-(rise % info[1]) * info[3], 3) if info else None


def frame_doors(verts, sectors, sides, lines, door_sectors, room_wall, alias=None, report=None):
    """door_sectors: {sector index: (door texture, track texture)}. room_wall(sector index) -> the wall texture of a
    room. alias: {texture: texture actually drawn} (RF01's 1940 materials are swapped after the build)."""
    alias = alias or {}
    report = report if report is not None else []
    vindex = {(float(v['x']), float(v['y'])): i for i, v in enumerate(verts)}

    def vertex(x, y):
        key = (float(x), float(y))
        if key not in vindex:
            vindex[key] = len(verts)
            verts.append(dict(x=x, y=y))
        return vindex[key]

    def xy(i):
        return float(verts[i]['x']), float(verts[i]['y'])

    for d, (door_tex, track) in sorted(door_sectors.items()):
        tex = alias.get(door_tex, door_tex).upper()
        mine = [i for i, l in enumerate(lines) if sides[l['sidefront']]['sector'] == d
                or (l.get('sideback') is not None and sides[l['sideback']]['sector'] == d)]
        pts = [xy(lines[i][k]) for i in mine for k in ('v1', 'v2')]
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        tag = sectors[d].get('id', 0)
        zf = sectors[d]['heightfloor']
        where = f'tag {tag} ({x0:g},{y0:g})-({x1:g},{y1:g})'
        if not doors.is_door(tex):
            report.append(dict(door=where, tex=tex, action='porte habillee en mur (camouflage) : laissee'))
            continue
        # every line of the leaf is on one edge of its rectangle and is either a room (an open sector at about the
        # leaf's floor) or wall (one-sided, or a mass shut above the floor)
        edge = {'S': [], 'N': [], 'W': [], 'E': []}
        standard = True
        for i in mine:
            (ax, ay), (bx, by) = xy(lines[i]['v1']), xy(lines[i]['v2'])
            if ay == by == y0:
                e = 'S'
            elif ay == by == y1:
                e = 'N'
            elif ax == bx == x0:
                e = 'W'
            elif ax == bx == x1:
                e = 'E'
            else:
                standard = False
                break
            room = False
            if lines[i].get('sideback') is not None:
                o = sectors[_other(lines, sides, i, d)]
                room = o['heightceiling'] - o['heightfloor'] >= 56 and o['heightfloor'] <= zf + 24
            edge[e].append((i, room))
        kinds = {e: ('room' if v and all(r for _, r in v) else 'wall' if v and not any(r for _, r in v) else 'mixed') for e, v in edge.items()}
        if standard and kinds['W'] == kinds['E'] == 'wall' and 'mixed' not in (kinds['S'], kinds['N']) and 'room' in (kinds['S'], kinds['N']):
            axis = 'y'
        elif standard and kinds['S'] == kinds['N'] == 'wall' and 'mixed' not in (kinds['W'], kinds['E']) and 'room' in (kinds['W'], kinds['E']):
            axis = 'x'
        else:
            report.append(dict(door=where, tex=tex, action=f'forme non standard ({kinds}) : non encadree'))
            continue
        lo_e, hi_e, end_a, end_b = ('S', 'N', 'W', 'E') if axis == 'y' else ('W', 'E', 'S', 'N')
        faces = [e for e in (lo_e, hi_e) if kinds[e] == 'room']
        T = (y1 - y0) if axis == 'y' else (x1 - x0)
        width = (x1 - x0) if axis == 'y' else (y1 - y0)
        if T < FRAME * (len(faces) + 1):
            report.append(dict(door=where, tex=tex, action=f'epaisseur {T:g} : non encadree'))
            continue
        clear = {}
        for e in faces:
            rooms = {_other(lines, sides, i, d) for i, _ in edge[e]}
            clear[e] = min(sectors[r]['heightceiling'] for r in rooms) - zf
        head = head_height(tex, width, min(clear.values()))
        if head < 64:
            report.append(dict(door=where, tex=tex, action=f'hauteur libre {min(clear.values()):g} : non encadree'))
            continue
        frames = {}
        for e in faces:
            f = dict(sectors[d])
            f.update(heightceiling=zf + head, id=0, special=0)
            frames[e] = len(sectors)
            sectors.append(f)
        lo, hi = (y0, y1) if axis == 'y' else (x0, x1)
        cut = {lo_e: lo + FRAME, hi_e: hi - FRAME}

        def at(c, t):                                  # point at depth c across the door, t along it
            return (t, c) if axis == 'y' else (c, t)

        def owner(depth):                              # the sector at a depth across the door
            if lo_e in frames and depth < cut[lo_e]:
                return frames[lo_e]
            if hi_e in frames and depth > cut[hi_e]:
                return frames[hi_e]
            return d
        # the faces toward the rooms: the room now meets the frame strip and shows its own wall above the head
        use = {}
        for e in faces:
            for i, _ in edge[e]:
                l = lines[i]
                room_side, door_side = ('sidefront', 'sideback') if sides[l['sideback']]['sector'] == d else ('sideback', 'sidefront')
                ds = dict(sides[l[door_side]])
                ds['sector'] = frames[e]
                sides[l[door_side]] = ds
                rs = dict(sides[l[room_side]])
                room = rs['sector']
                wall = room_wall(room)
                if wall and doors.is_door(alias.get(wall, wall).upper()):
                    wall = track                       # a gate's own recess: the lintel is the wall the gate is set in
                rs.pop('texturetop', None)
                if sectors[room]['heightceiling'] > zf + head and wall:
                    rs['texturetop'] = wall
                    off = lintel_offset(wall, alias, zf + head - sectors[room]['heightfloor'])
                    if off is not None:
                        rs['offsety_top'] = off
                sides[l[room_side]] = rs
                l.pop('dontpegtop', None)
                if 'special' in l and e not in use:
                    use[e] = {k: l[k] for k in USE_KEYS if k in l}
        # the leaf's own faces, one line across the whole opening on each side
        a0, a1 = (x0, x1) if axis == 'y' else (y0, y1)
        for e in faces:
            p, q = at(cut[e], a0), at(cut[e], a1)
            # the frame strip must be on the right of v1 -> v2
            v1, v2 = (p, q) if (axis == 'y') == (e == lo_e) else (q, p)
            front = dict(sector=frames[e], texturetop=doors.fit(tex, width, head, mirrored=(e == hi_e)))
            sides.append(front)
            sides.append(dict(sector=d))
            nl = dict(v1=vertex(*v1), v2=vertex(*v2), sidefront=len(sides) - 2, sideback=len(sides) - 1, twosided=True)
            nl.update(use.get(e, {}))
            lines.append(nl)
        # the ends in the wall: jamb of each strip, track of the leaf, all fixed
        for e in (end_a, end_b):
            for i, _ in edge[e]:
                l = lines[i]
                (ax, ay), (bx, by) = xy(l['v1']), xy(l['v2'])
                pa, pb = (ay, by) if axis == 'y' else (ax, bx)
                fixed = ax if axis == 'y' else ay
                cuts = sorted({pa, pb} | {cut[f] for f in faces if min(pa, pb) < cut[f] < max(pa, pb)}, reverse=pa > pb)
                two = l.get('sideback') is not None
                mine_key = 'sidefront' if sides[l['sidefront']]['sector'] == d else 'sideback'
                pieces = []
                for s, t in zip(cuts, cuts[1:]):
                    sd = dict(sides[l[mine_key]])
                    sd['sector'] = owner((s + t) / 2)
                    nl = {k: v for k, v in l.items() if k not in ('v1', 'v2', 'sidefront', 'sideback', 'dontpegtop')}
                    if two:
                        # a mass shut above the floor: the jamb is the riser the leaf's side shows up to it
                        if track:
                            sd['texturebottom'] = track
                        sd.pop('texturetop', None)
                        other = dict(sides[l['sideback' if mine_key == 'sidefront' else 'sidefront']])
                        sides.append(sd)
                        sides.append(other)
                        mine_i, other_i = len(sides) - 2, len(sides) - 1
                        nl['sidefront'], nl['sideback'] = (mine_i, other_i) if mine_key == 'sidefront' else (other_i, mine_i)
                    else:
                        if track:
                            sd['texturemiddle'] = track
                        sides.append(sd)
                        nl['sidefront'] = len(sides) - 1
                        nl['dontpegbottom'] = True
                    p, q = ((fixed, s), (fixed, t)) if axis == 'y' else ((s, fixed), (t, fixed))
                    nl.update(v1=vertex(*p), v2=vertex(*q))
                    pieces.append(nl)
                lines[i] = pieces[0]
                lines.extend(pieces[1:])
        report.append(dict(door=where, tex=tex, width=width, head=head, clear=clear, action='encadree',
                           faces=len(faces), image=doors.fit(tex, width, head)))
    compact_sides(sides, lines)
    return report


def _other(lines, sides, li, sec):
    l = lines[li]
    a = sides[l['sidefront']]['sector']
    b = sides[l['sideback']]['sector'] if l.get('sideback') is not None else None
    return b if a == sec else a


def compact_sides(sides, lines):
    """Drop the sidedefs no line uses any more and renumber: the engine counts the sides the lines refer to and
    refuses an index beyond that count ("Line N has no front sector")."""
    used = sorted({l[k] for l in lines for k in ('sidefront', 'sideback') if l.get(k) is not None})
    if len(used) == len(sides):
        return
    new = {old: i for i, old in enumerate(used)}
    kept = [sides[i] for i in used]
    sides[:] = kept
    for l in lines:
        for k in ('sidefront', 'sideback'):
            if l.get(k) is not None:
                l[k] = new[l[k]]


def fit_static(verts, sectors, sides, lines, room_wall, alias=None, skip_sectors=(), report=None):
    """One-sided faces carrying a door image: the image fitted to the face (see doors.fit)."""
    alias = alias or {}
    report = report if report is not None else []
    for l in lines:
        if l.get('sideback') is not None:
            continue
        sd = sides[l['sidefront']]
        name = sd.get('texturemiddle', '-')
        tex = alias.get(name, name).upper()
        if not doors.is_door(tex) or sd['sector'] in skip_sectors:
            continue
        sec = sectors[sd['sector']]
        H = sec['heightceiling'] - sec['heightfloor']
        if H <= 0:
            continue
        a, b = verts[l['v1']], verts[l['v2']]
        W = math.hypot(float(b['x']) - float(a['x']), float(b['y']) - float(a['y']))
        kind = doors.CATALOG[tex][4]
        if kind in ('plain',):
            new = doors.fit(tex, W, H)
            head = H
        else:
            head = head_height(tex, W, H)
            wall = room_wall(sd['sector'])
            wall = alias.get(wall, wall) if wall else wall
            if wall and doors.is_door(wall.upper()):
                wall = None
                head = H if kind == 'bars' else head
            new = doors.fit(tex, W, head, wall=wall, total=H) if H > head else doors.fit(tex, W, head)
        sd2 = dict(sd)
        sd2['texturemiddle'] = new
        sd2.pop('offsetx', None)
        sd2.pop('offsety', None)
        sides[l['sidefront']] = sd2
        l['dontpegbottom'] = True
        report.append(dict(face=f"({a['x']:g},{a['y']:g})-({b['x']:g},{b['y']:g})", tex=tex, width=W, head=head, wall_height=H, image=new,
                           action='ajustee'))
    return report


def fit_facades(verts, sectors, sides, lines, alias=None, report=None):
    """Walls dressed with a painted front (facades.py): the front fitted to the wall, so that no door or shutter of
    its ground floor is cut by the wall's end (one-sided walls, and the faces of masses lower than the sky)."""
    import facades
    alias = alias or {}
    report = report if report is not None else []
    for l in lines:
        a, b = verts[l['v1']], verts[l['v2']]
        W = math.hypot(float(b['x']) - float(a['x']), float(b['y']) - float(a['y']))
        for key, okey in (('sidefront', 'sideback'), ('sideback', 'sidefront')):
            if l.get(key) is None:
                continue
            sd = sides[l[key]]
            if sd.get('offsetx') or sd.get('offsety'):
                continue                               # a face placed by hand (the front around the Brooklyn passage)
            f = sectors[sd['sector']]
            if l.get(okey) is None:
                part, H = 'texturemiddle', f['heightceiling'] - f['heightfloor']
            else:
                o = sectors[sides[l[okey]]['sector']]
                part, H = 'texturebottom', min(o['heightfloor'], f['heightceiling']) - f['heightfloor']
            name = sd.get(part, '-')
            tex = alias.get(name, name).upper()
            if H <= 0 or not facades.is_facade(tex):
                continue
            if tex in facades.HAUSSMANN and part == 'texturebottom' and H <= facades.TILE_H - facades.band_height():
                continue                               # only the upper floors show above the wall in front of it
            new = doors.fit_facade(tex, W, H)
            if new == tex:
                continue
            sd2 = dict(sd)
            sd2[part] = new
            sides[l[key]] = sd2
            report.append(dict(face=f"({a['x']:g},{a['y']:g})-({b['x']:g},{b['y']:g})", tex=tex, width=W, wall_height=H, image=new,
                               action='facade ajustee'))
    return report
