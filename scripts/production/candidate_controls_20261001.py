#!/usr/bin/env python3
r"""The controls of the mandate of 01/10 on a frozen candidate (sequential: the engine lock serialises them).

  chain RF01 -> RF07 from a new game with a load in the middle; RF01, RF02, RF04, RF05, RF06, RF07 runs A (traverse)
  and B (save, quit, reload, death where the map has enemies, resume, exit); the comic page RF01_RF02 (read, pass, fire,
  save during the page, load), and the five pages read to the next chapter in 16:9, 21:9, 4:3; control views (RF02 reflection before/after, RF02 target
  views and sky-height spots, RF04 pilot zone, RF04 mirrors with the three outfits, RF05, RF06, RF07 with the watch); the
  orderly's walk in RF04; native sound film. The launchers from C:\ are checked after export (export_candidate.py).

Usage: python scripts/production/candidate_controls_20261001.py <candidate folder> [step ...]
Writes <candidate folder>/preuves/<step>/ and preuves/CONTROLES.json (one line per step: command, return, last line).
"""
import glob, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
V = ROOT / 'docs' / 'production' / 'handoff' / 'RF2_20261001' / 'vues'
OLD = ROOT / 'dist' / 'candidates' / 'RF2_CUMUL_20260930_1821' / 'RF2_CUMUL.pk3'
sys.path.insert(0, str(ROOT / 'scripts'))
import devrun  # noqa: E402

SIZES = {'16x9': (1920, 1080), '21x9': (2560, 1080), '4x3': (1440, 1080)}
# (scene, probe mode, size): the flow of the first page with every input; each other page read to the next chapter and
# shot in the three formats
COMICS = [('RF01_RF02', m, '16x9') for m in ('read', 'pass', 'fire', 'save', 'load')] + \
         [(s, 'shots', f) for s in ('RF01_RF02', 'RF02_RF04', 'RF04_RF05', 'RF05_RF06', 'RF06_RF07') for f in SIZES]


def comic(pk3, out, scene, mode, fmt):
    """A page with the probe of comic_flow_probe.py; 'load' loads the save of 'save'. Returns the record."""
    first, nxt = scene.split('_')
    tag = f'{mode}_{fmt}' if mode == 'shots' else mode
    c = out / f'planche_{scene}'
    c.mkdir(exist_ok=True)
    probe = Path(os.environ.get('TEMP', '.')) / f'comic_{scene}_{tag}.pk3'
    subprocess.run([PY, 'scripts/production/comic_flow_probe.py', str(probe), mode, scene, 'none'], cwd=ROOT,
                   check=True, capture_output=True)
    loadgame = None
    if mode == 'load':
        loadgame = sorted(glob.glob(str(ROOT / 'build/dev/saves/auto*.zds')), key=os.path.getmtime)[-1]
    w, h = SIZES[fmt]
    status, text, shots = devrun.run(pk3, f'comic_{scene}_{tag}', first, seconds=150, width=w, height=h,
                                     marker='RF_DEV_UI_DONE', loadgame=loadgame, extra=['-file', str(probe)])
    lines = [l for l in text.splitlines() if l.startswith(('RF_COMICPROBE', 'RF_DEV_COMIC', 'RF_DEV_ARRIVAL',
                                                           'RF_DEV_ENDING', 'RF_DEV_LOADED'))]
    (c / f'{tag}.log.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    for i, p in enumerate(sorted(shots.glob('*.png'))):
        shutil.copy2(p, c / f'{tag}_{i:02d}.png')
    arrivals = [l for l in lines if l.startswith('RF_DEV_ARRIVAL')]
    return dict(status=status, next_reached=any(f'map={nxt}' in l for l in lines), page=any(f'comic={scene}' in l for l in lines),
                arrival=arrivals[-1] if arrivals else None, shots=len(list(shots.glob('*.png'))))


def main():
    cand = Path(sys.argv[1]).resolve()
    only = set(sys.argv[2:])
    pk3 = next(cand.glob('RF2_*.pk3'))
    out = cand / 'preuves'
    out.mkdir(exist_ok=True)
    rec_path = out / 'CONTROLES.json'
    rec = json.loads(rec_path.read_text(encoding='utf-8')) if rec_path.exists() else {}
    cv = [PY, 'scripts/production/capture_views.py', str(pk3)]
    steps = [
        ('chaine', [PY, 'scripts/production/chain_test.py', str(pk3), str(out / 'chaine.json')]),
        ('e2e_RF01', [PY, 'scripts/e2e_rf01.py', '--map', 'RF01', '--pk3', str(pk3)]),
        ('e2e_RF02', [PY, 'scripts/e2e_rf01.py', '--map', 'RF02', '--save-at', '29', '--pk3', str(pk3)]),
        ('e2e_RF04', [PY, 'scripts/e2e_rf01.py', '--map', 'RF04', '--save-at', '30', '--pk3', str(pk3)]),
        ('e2e_RF05', [PY, 'scripts/e2e_rf01.py', '--map', 'RF05', '--save-at', '8', '--pk3', str(pk3)]),
        ('e2e_RF06', [PY, 'scripts/e2e_rf01.py', '--map', 'RF06', '--save-at', '5', '--no-death', '--pk3', str(pk3)]),
        ('e2e_RF07', [PY, 'scripts/e2e_rf01.py', '--map', 'RF07', '--save-at', '4', '--no-death', '--pk3', str(pk3)]),
        ('vues_RF02_reflet', cv + ['RF02', str(ROOT / 'docs/production/handoff/RF2_20261001/mesures/reflet_rf02_vues.json'),
                                   str(out / 'vues_RF02_reflet'), '--hide']),
        ('vues_RF02_reflet_1821', [PY, 'scripts/production/capture_views.py', str(OLD), 'RF02',
                                   str(ROOT / 'docs/production/handoff/RF2_20261001/mesures/reflet_rf02_vues.json'),
                                   str(out / 'vues_RF02_reflet_avant_1821'), '--hide']),
        ('vues_RF02_cible', cv + ['RF02', str(V / 'rf02_cible.json'), str(out / 'vues_RF02_cible'), '--hide']),
        ('vues_RF02_hauteur_ciel', cv + ['RF02', str(V / 'rf02_hauteur_ciel.json'), str(out / 'vues_RF02_hauteur_ciel'),
                                         '--hide']),
        ('vues_RF04_pilote', cv + ['RF04', str(V / 'rf04_pilote.json'), str(out / 'vues_RF04_pilote'), '--hide']),
        ('vues_RF04_miroirs', cv + ['RF04', str(V / 'rf04_miroirs.json'), str(out / 'vues_RF04_miroirs_trois_tenues'),
                                    '--hide', '--alt', 'RFViktorMirrorGrey:0:-96,RFViktorMirrorShirt:0:96']),
        ('vues_RF05', cv + ['RF05', str(V / 'rf05_controle_20261001.json'), str(out / 'vues_RF05'), '--hide']),
        ('vues_RF06', cv + ['RF06', str(V / 'rf06_controle_20261001.json'), str(out / 'vues_RF06')]),
        ('vues_RF07', cv + ['RF07', str(V / 'rf07_controle.json'), str(out / 'vues_RF07'), '--code',
                            "let j = RFJerma(EventHandler.Find('RFJerma')); if (j) j.watchTic = Level.maptime + 160;"]),
        ('marche_ORDY_RF04', [PY, 'scripts/production/walk_film.py', str(pk3), 'RF04', 'RFOrderly', '1300', '1700', '0',
                              str(out / 'marche_ORDY_RF04'), '--path', '1444,1840,1444,1300']),
        ('film_son_natif', [PY, 'scripts/film.py', '--name', f'son_natif_{cand.name}', '--map', 'RF01', '--end', '1500',
                            '--pk3', str(pk3)]),
    ]
    for (tag, cmd) in steps:
        if only and tag not in only:
            continue
        t0 = time.time()
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        last = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()][-3:]
        rec[tag] = dict(cmd=' '.join(Path(c).name if os.sep in c or '/' in c else c for c in cmd), rc=r.returncode,
                        seconds=round(time.time() - t0), last=last, at=time.strftime('%Y-%m-%d %H:%M'))
        print(f'[{tag}] rc={r.returncode} {round(time.time() - t0)}s :: {last[-1] if last else ""}', flush=True)
        rec_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    for (scene, mode, fmt) in COMICS:
        tag = f'planche_{scene}_{mode}' + (f'_{fmt}' if mode == 'shots' else '')
        if only and tag not in only and 'planche' not in only:
            continue
        rec[tag] = r = comic(pk3, out, scene, mode, fmt)
        print(f'[{tag}] {r["status"]} page={r["page"]} suite={r["next_reached"]} {r["arrival"] or ""}', flush=True)
        rec_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
