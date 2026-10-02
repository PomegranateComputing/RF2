#!/usr/bin/env python3
"""The table of the door pass: every door-like element whose audit showed a defect before, with what was done to it,
read from the two audits (door_audit.py before and after) and from the list of fitted images (doors.py).

An element of the first audit is matched to the second by its map, its place (the middle of its surface) and the
side it is seen from; a framed door moved its face a few units into the opening, so the match allows 24 units.

Usage: python scripts/production/door_report.py <audit_before.json> <audit_after.json> <out.md> [<motion dir> <views dir>]
"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    before = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    after = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    out = Path(sys.argv[3])
    variants = {}
    vp = ROOT / 'build' / 'door_variants_report.json'
    if vp.exists():
        variants = json.loads(vp.read_text(encoding='utf-8'))
    motion = {}
    if len(sys.argv) > 4:
        for f in Path(sys.argv[4]).glob('*/mouvement.json'):
            for r in json.loads(f.read_text(encoding='utf-8')):
                motion[(f.parent.name, r['sector'])] = r
    by_map = {}
    for r in after:
        by_map.setdefault(r['map'], []).append(r)

    def match(b):
        best, bd = None, 25.0
        for a in by_map.get(b['map'], []):
            if a['kind'] != b['kind'] and not (b['kind'] == 'mechanism' and a['kind'] == 'mechanism'):
                continue
            if 'mid' not in a or 'mid' not in b:
                continue
            if a['normal'][0] * b['normal'][0] + a['normal'][1] * b['normal'][1] < 0.9:
                continue
            d = math.hypot(a['mid'][0] - b['mid'][0], a['mid'][1] - b['mid'][1])
            if d < bd:
                best, bd = a, d
        return best

    def what(tex):
        v = variants.get(tex)
        if not v:
            return f'image {tex} a sa taille'
        s = f"image {v['source']} recomposee a {v['w']} x {v['h']} u ({v['how']})"
        return s

    rows = []
    for b in before:
        if not b.get('defects'):
            continue
        a = match(b)
        if b['kind'] == 'mechanism':
            elem = f"porte, secteur {b['sector']}, face vue du secteur {b['seen_from']} (ligne {b['lines'][0]})"
        elif b['kind'] == 'track':
            elem = f"montant de la porte secteur {b['sector']} (ligne {b['lines'][0]})"
        else:
            elem = f"face {b['part']} ligne {b['lines'][0]}, secteur {b['seen_from']}"
        defect = f"{b['tex']} sur {b['W']:g} x {b['H']:g} u : " + ' ; '.join(b['defects'])
        if a is None:
            sol = 'surface disparue (geometrie corrigee) ou non dessinee par le moteur'
            if b['tex'] == 'RF4_PORT' and b['part'] == 'top':
                sol = 'non dessinee par le moteur (mur entre deux ciels) : aucun defaut visible, retiree du releve'
            elif b['tex'] == 'RF4_PORT':
                sol = "flanc du batiment des portes habille en pierre (RF4_BASC) au lieu d'une demi-porte"
        elif a.get('camouflage'):
            sol = "porte habillee du materiau du mur qui la cache : camouflage conserve" + ('' if a['map'] in ('RF01', 'RF04') else ' ; rangs recales sur le mur voisin')
        elif a['kind'] == 'mechanism':
            framed = abs(a['H'] - b['H']) > 0.5 or abs(a['mid'][0] - b['mid'][0]) + abs(a['mid'][1] - b['mid'][1]) > 1
            sol = ('dormant et linteau fixes ajoutes, vantail de ' if framed else 'vantail de ') + f"{a['W']:g} x {a['H']:g} u ; " + what(a['tex'])
            mv = motion.get((a['map'], a['sector']))
            if mv:
                sol += ' ; vue fermee, en course, ouverte, en fermeture' if mv['moved'] else ' ; mouvement non capture'
        elif a['kind'] == 'track':
            sol = f"montant en {a['tex']}, ancre au sol (fixe pendant le mouvement)"
        else:
            sol = what(a['tex'])
            if a.get('defects'):
                sol += ' ; RESTE : ' + ' ; '.join(a['defects'])
        rows.append((b['map'], elem, defect, sol))
    lines = ['| Carte | Element | Defaut releve | Solution |', '|---|---|---|---|']
    for r in rows:
        lines.append('| ' + ' | '.join(r) + ' |')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    left = [a for a in after if a.get('defects')]
    print(f'{len(rows)} elements corriges ; {len(left)} defauts restants au releve -> {out}')


if __name__ == '__main__':
    main()
