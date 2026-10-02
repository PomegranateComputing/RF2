#!/usr/bin/env python3
"""Door pass of 02/10/2026 on the V1 blockout maps (RF03, RF08-RF23: UDMF with prebuilt nodes, not made by the kit).

Only sidedef textures, offsets and pegging flags change: no vertex, line or sector is added or moved, so the maps'
ZNODES stay valid and every tag, special, lock and trigger is untouched. Per map:
  - the badge door (three lines per face, the 128-unit door image tiled with offsets 64, 0, 64 over a 192 x 192
    face): one image fitted to the whole face (doors.fit), its three lines offset 0, 64, 128;
  - the door's tracks carried the door image: they get a plain metal jamb, pegged to the floor (they rode up with
    the door);
  - the tracks of every other door sector: pegged to the floor;
  - the exit sign (a 64 x 128 sign on a 192-unit wall, repeated above itself): the sign once, the wall's own material
    above it, in one image;
  - the secret doors keep the wall material that hides them; their face is shifted to the row the wall beside them
    shows (they were anchored 64 units off it).

Usage: python scripts/production/door_fix_blockouts.py [--maps RF03,RF08] [--dry]
"""
import argparse, json, struct, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
import door_audit  # noqa: E402
import doors  # noqa: E402
import doorfit  # noqa: E402

BLOCKOUTS = ['RF03'] + [f'RF{i:02d}' for i in range(8, 24)]
JAMB = 'RFMETAL'


def val(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, float):
        return repr(v)
    return str(v)


def emit(m):
    out = ['namespace = "zdoom";', '']
    for kind, items in (('thing', m.T), ('vertex', m.V), ('linedef', m.L), ('sidedef', m.S), ('sector', m.SE)):
        for d in items:
            out.append(kind + '\n{\n' + '\n'.join(f'{k} = {val(v)};' for k, v in d.items()) + '\n}\n')
    return '\n'.join(out)


def fix(name, text, db, stags, log):
    m = door_audit.Map(name, text, db, stags)
    m.T = door_audit.parse_textmap(text)['thing']
    recs = m.surfaces()
    for r in recs:
        side_key = 'sidefront' if r['side'] == 'front' else 'sideback'
        if r['tex'].startswith('RD') and len(r['tex']) == 8 and r['tex'] not in doors.CATALOG:
            continue                                   # already fitted by an earlier run
        sds = [m.S[m.L[li][side_key]] for li in r['lines']]
        if r['kind'] == 'mechanism' and doors.is_door(r['tex']):
            new = doors.fit(r['tex'], r['W'], r['H'])
            x = 0.0
            for li, sd in zip(r['lines'], sds):
                sd['texturetop'] = new
                sd['offsetx'] = int(x) if x == int(x) else x
                sd.pop('offsetx_top', None)
                sd.pop('offsety', None)
                x += m.length(li)
            log.append(dict(map=name, element=f"porte secteur {r['sector']} (tag {m.SE[r['sector']].get('id', 0)}), face vue du secteur {r['seen_from']}",
                            defect='; '.join(r['defects']), fix=f"image {r['tex']} ajustee a {r['W']:g} x {r['H']:g} ({new}), lignes recalees"))
        elif r['kind'] == 'mechanism':
            # a secret door in the wall's material: match the rows of the one-sided wall beside it (top-pegged)
            room = m.SE[r['seen_from']]
            info = doorfit.tex_info(r['tex'])
            if info:
                rows = ((room['heightceiling'] - room['heightfloor']) % info[1]) * info[3]
                for sd in sds:
                    if rows:
                        sd['offsety_top'] = rows
                    else:
                        sd.pop('offsety_top', None)
                log.append(dict(map=name, element=f"porte secrete secteur {r['sector']} (tag {m.SE[r['sector']].get('id', 0)}), face vue du secteur {r['seen_from']}",
                                defect='camouflage : rangs decales de %g u par rapport au mur voisin' % (rows / info[3]) if rows else 'camouflage : aucun',
                                fix='rangs recales sur le mur voisin' if rows else 'laissee'))
        elif r['kind'] == 'track':
            for li, sd in zip(r['lines'], sds):
                if doors.is_door(r['tex']):
                    sd['texturemiddle'] = JAMB
                    sd.pop('offsetx', None)
                m.L[li]['dontpegbottom'] = True
                m.L[li].pop('dontpegtop', None)
            log.append(dict(map=name, element=f"montants de la porte secteur {r['sector']}, lignes {r['lines']}",
                            defect='image de porte sur le montant ; montant ancre au plafond mobile' if doors.is_door(r['tex']) else 'montant ancre au plafond mobile',
                            fix=(f'materiau {JAMB} ; ' if doors.is_door(r['tex']) else '') + 'ancre au sol'))
        elif r['kind'] == 'static' and doors.is_door(r['tex']) and r['part'] == 'mid':
            sec = m.SE[r['seen_from']]
            H = sec['heightceiling'] - sec['heightfloor']
            w, h = doors.natural(r['tex'])
            # the wall beside it: the middle texture most used on the one-sided lines of the sector
            count = {}
            for li in m.lines_of[r['seen_from']]:
                l = m.L[li]
                if l.get('sideback', -1) < 0:
                    t = m.S[l['sidefront']].get('texturemiddle', '-').upper()
                    if t not in ('-', r['tex']) and not doors.is_door(t):
                        count[t] = count.get(t, 0) + m.length(li)
            wall = max(count, key=count.get) if count else None
            head = min(h, H)
            new = doors.fit(r['tex'], r['W'], head, wall=wall, total=H) if (H > head and wall) else doors.fit(r['tex'], r['W'], head)
            for li, sd in zip(r['lines'], sds):
                sd['texturemiddle'] = new
                sd.pop('offsetx', None)
                sd.pop('offsety', None)
                m.L[li]['dontpegbottom'] = True
            log.append(dict(map=name, element=f"panneau {r['tex']} secteur {r['seen_from']}, ligne {r['lines'][0]}",
                            defect='; '.join(r['defects']), fix=f'image unique {new} : le panneau une fois, mur {wall} au-dessus'))
    return emit(m)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--maps', default='')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    names = [n.strip().upper() for n in a.maps.split(',') if n.strip()] or BLOCKOUTS
    db, stags = door_audit.texture_db(), door_audit.script_tags()
    log = []
    for name in names:
        wad = ROOT / 'src' / 'maps' / f'{name}.wad'
        lumps = list(door_audit.lumps(wad))
        text = dict(lumps)['TEXTMAP'].decode('utf-8', 'replace')
        new = fix(name, text, db, stags, log)
        if a.dry:
            continue
        out = bytearray(b'PWAD' + struct.pack('<ii', len(lumps), 0))
        directory = []
        for lname, data in lumps:
            if lname == 'TEXTMAP':
                data = new.encode('utf-8')
            directory.append(struct.pack('<ii8s', len(out), len(data), lname.encode('latin-1').ljust(8, b'\0')))
            out.extend(data)
        struct.pack_into('<i', out, 8, len(out))
        out.extend(b''.join(directory))
        wad.write_bytes(bytes(out))
    (ROOT / 'build' / 'door_pass').mkdir(parents=True, exist_ok=True)
    (ROOT / 'build' / 'door_pass' / 'blockouts_corrections.json').write_text(json.dumps(log, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{len(names)} cartes, {len(log)} corrections' + (' (essai)' if a.dry else ''))


if __name__ == '__main__':
    main()
