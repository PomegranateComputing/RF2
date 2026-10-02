#!/usr/bin/env python3
"""Engine test of the family bench: each family is put on the bench (module over its frozen base), the stations run
until the bench prints its summary, and the measures are compared with the family's contract
(bench/familles/contrats.json: the poses and tics the game plays today). New images must leave them unchanged.

A probe player (an observer) goes round the stations and takes a picture of each.

Usage: python bench/familles/test_family_bench.py <bench folder dist/familles/RF2_BANC_FAMILLES_...> [classes...]
       [--module extra.pk3] [--seconds 240]
Writes <bench folder>/preuves/test_familles.json, RESULTATS.md and the pictures there.
"""
import argparse, json, re, shutil, sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import devrun  # noqa: E402

# (label, x, y, angle, pitch): the view mark and its two arcs, the walk, the obstacles, the attack, pain and death
VIEWS = [('rotations', 704, 256, 90, 0), ('rotations_pres', 704, 420, 90, 0), ('marche', 330, 464, 180, 0),
         ('obstacles', 1120, 500, 0, 0), ('obstacles_portes', 1150, 900, 300, 0), ('attaque', 880, 720, 80, 4),
         ('douleur_mort', 336, 720, 90, 4)]

PROBE = '''version "4.14"
class RFBenchProbe : RFPlayer
{
    static const double vx[] = { %(xs)s };
    static const double vy[] = { %(ys)s };
    static const double va[] = { %(angs)s };
    static const double vp[] = { %(pitches)s };
    int shot;
    override void PlayerThink()
    {
        Super.PlayerThink();
        if (player == null) return;
        player.cmd.buttons = 0;
        player.cmd.forwardmove = 0;
        player.cmd.sidemove = 0;
        // a round of the stations every 12 seconds of game, a picture a second after each arrival
        int n = %(count)d;
        int t = Level.maptime - 140;
        if (t < 0) return;
        int k = (t / 60) %% n;
        if (t %% 60 == 0)
        {
            SetOrigin((vx[k], vy[k], 0), false);
            angle = va[k];
            pitch = vp[k];
            Vel = (0, 0, 0);
        }
        if (t %% 60 == 35 && shot < n * 2)
        {
            Console.Printf("RF_BANCPROBE vue=%%d t=%%d", k, Level.maptime);
            Level.MakeScreenShot();
            shot++;
        }
    }
}
'''


def parse(text):
    out = dict(classe=None, marche_poses=None, marche=[], obstacles=None, gates=[], attaques=[], douleurs=[], morts=[])
    for line in text.splitlines():
        if not line.startswith('RF_BANC '):
            continue
        kind = line.split()[1]
        f = dict(re.findall(r'(\w+)=(\S+)', line))
        if kind == 'CLASSE':
            out['classe'] = f
        elif kind == 'MARCHE_POSES':
            out['marche_poses'] = f.get('poses')
        elif kind == 'MARCHE':
            out['marche'].append(dict(pas=float(f['pas']), cadence=float(f['cadence']), vitesse=float(f['vitesse'])))
        elif kind == 'OBSTACLE':
            if 'passe=' in line:
                out['gates'].append(line.split('passe=')[1].split(' tics=')[0])
        elif kind == 'OBSTACLES' and out['obstacles'] is None:
            out['obstacles'] = 'passe' if f.get('resultat') == 'passe' else f.get('resultat') + ' devant ' + line.split('devant=')[1].split(' franchis=')[0]
        elif kind == 'ATTAQUE':
            out['attaques'].append(dict(depart=f['depart'], poses=f['poses'], total=int(f['total']), tir=int(f['tir']), coup=int(f['coup'])))
        elif kind == 'DOULEUR':
            out['douleurs'].append(f.get('poses'))
        elif kind == 'MORT':
            out['morts'].append(dict(poses=f.get('poses'), corps=f.get('corps')))
    return out


def compare(m, c):
    """-> list of (point, expected, measured, ok)."""
    rows = []

    def row(point, expected, measured, ok):
        rows.append(dict(point=point, attendu=expected, mesure=measured, ok=bool(ok)))

    row('marche, poses', c['marche_poses'], m['marche_poses'], m['marche_poses'] == c['marche_poses'])
    sp = m['marche']
    row('marche, longueur du pas (u)', c['pas'], sorted({s['pas'] for s in sp}), bool(sp) and all(abs(s['pas'] - c['pas']) <= 0.2 for s in sp))
    row('marche, un pas tous les (tics)', c['cadence'], [s['cadence'] for s in sp],
        bool(sp) and all(abs(s['cadence'] - c['cadence']) <= c.get('cadence_tolerance', 1.0) for s in sp))
    row('obstacles', c['obstacles'], m['obstacles'], m['obstacles'] == c['obstacles'])
    atk = m['attaques']
    row('attaque, poses', c['attaque'], sorted({a['poses'] for a in atk}), bool(atk) and all(re.fullmatch(c['attaque'], a['poses']) for a in atk))
    if 'coup' in c:
        hit = [a['coup'] for a in atk if a['coup'] >= 0]
        row('attaque, tic du coup', c['coup'], sorted(set(hit)), bool(hit) and all(h == c['coup'] for h in hit))
    if 'tir' in c:
        row('attaque, tic du tir', c['tir'], sorted({a['tir'] for a in atk}), bool(atk) and all(a['tir'] == c['tir'] for a in atk))
    row('douleur, poses', c['douleur'], sorted(set(m['douleurs'])), bool(m['douleurs']) and all(p == c['douleur'] for p in m['douleurs']))
    row('mort, poses', c['mort'], sorted({d['poses'] for d in m['morts']}), bool(m['morts']) and all(re.fullmatch(c['mort'], d['poses']) for d in m['morts']))
    row('corps', c['corps'], sorted({d['corps'] for d in m['morts']}), bool(m['morts']) and all(str(d['corps']).startswith(c['corps']) for d in m['morts']))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bench')
    ap.add_argument('classes', nargs='*')
    ap.add_argument('--module', action='append', default=[], help='another module loaded after the bench (a new family)')
    ap.add_argument('--seconds', type=int, default=240)
    a = ap.parse_args()
    bench = Path(a.bench).resolve()
    info = json.loads((bench / 'BUILD_INFO.json').read_text(encoding='utf-8'))
    base, module = ROOT / info['base'], ROOT / info['module']
    contracts = json.loads((HERE / 'contrats.json').read_text(encoding='utf-8'))
    classes = a.classes or [k for k in contracts if not k.startswith('_')]
    probe = Path(tempfile.gettempdir()) / 'rf2_banc_probe.pk3'
    fill = dict(xs=', '.join(str(float(v[1])) for v in VIEWS), ys=', '.join(str(float(v[2])) for v in VIEWS),
                angs=', '.join(str(float(v[3])) for v in VIEWS), pitches=', '.join(str(float(v[4])) for v in VIEWS), count=len(VIEWS))
    with zipfile.ZipFile(probe, 'w') as z:
        z.writestr('ZSCRIPT.bancprobe', PROBE % fill)
        z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFBenchProbe"\n}\n')
    out = bench / 'preuves'
    out.mkdir(exist_ok=True)
    report = dict(bench=str(bench), module_sha256=info['module_sha256'], base_sha256=info['base_sha256'], classes={})
    ok_all = True
    for cls in classes:
        status, text, shots = devrun.run(base, f'banc_{cls}', 'FAM01', seconds=a.seconds, width=1280, height=720,
                                         marker='RF_BANC BILAN',
                                         extra=['-file', str(module)] + a.module + [str(probe), '+set', 'rf_banc_classe', cls, '+set', 'rf_dev_log', '1'])
        errors = [l for l in text.splitlines() if 'Script error' in l or 'VM execution aborted' in l]
        m = parse(text)
        rows = compare(m, contracts[cls]) if cls in contracts else []
        ok = bool(rows) and all(r['ok'] for r in rows) and not errors and 'RF_BANC BILAN' in text
        if cls not in contracts:
            ok = not errors and 'RF_BANC BILAN' in text
        ok_all &= ok
        pics = []
        for old in out.glob(f'{cls}_*.png'):
            old.unlink()
        for i, p in enumerate(sorted(shots.glob('*.png'))[:len(VIEWS)]):
            dst = out / f'{cls}_{i + 1:02d}_{VIEWS[i][0]}.png'
            shutil.copy2(p, dst)
            pics.append(dst.name)
        report['classes'][cls] = dict(status=status, ok=ok, bilan='RF_BANC BILAN' in text, errors=errors, mesures=m, controle=rows, images=pics)
        print(f'{cls}:', 'PASS' if ok else 'FAIL', '' if ok else [r for r in rows if not r['ok']] or errors or 'pas de bilan')
    report['ok'] = ok_all
    (out / 'test_familles.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    md = ['# Banc des familles : mesures', '', f"Module `{info['module']}` (sha256 `{info['module_sha256']}`), base `{info['base']}`.", '']
    for cls, r in report['classes'].items():
        c = r['mesures']['classe'] or {}
        md += [f"## {cls} : {'conforme' if r['ok'] else 'ECART'}", '',
               f"Rayon {c.get('rayon', '?')} u, hauteur {c.get('hauteur', '?')} u, vitesse {c.get('vitesse', '?')}, santé {c.get('sante', '?')}, échelle {c.get('echelle', '?')}.", '',
               '| Point | Attendu (contrat) | Mesuré | |', '|---|---|---|---|']
        md += [f"| {x['point']} | `{x['attendu']}` | `{x['mesure']}` | {'conforme' if x['ok'] else '**écart**'} |" for x in r['controle']]
        md += ['', 'Images : ' + ', '.join(f'`{p}`' for p in r['images']), '']
    (out / 'RESULTATS.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('FAMILY BENCH:', 'PASS' if ok_all else 'FAIL')
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
