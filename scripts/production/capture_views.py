#!/usr/bin/env python3
"""Capture a list of control views on a build and keep each picture under its view's name.

Builds the view probe (view_check_pk3.py: a player class that visits the views, tic strip in the corner), runs the
engine once (devrun.py, under the engine lock), then matches every screenshot to its view by the tic it shows
(ticcode.py): a picture showing another tic than its view is a stale frame and is not kept.

Usage: python scripts/production/capture_views.py <build.pk3> <MAP> <views.json> <out_dir> [--hide] [--give A,B]
       [--size 1920x1080] [--wait 180]
Writes <out_dir>/NN_<label>.png and <out_dir>/vues.json (label, tic, kept or not, source build and its sha256).
"""
import argparse, hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import ticcode  # noqa: E402
import devrun  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pk3')
    ap.add_argument('map')
    ap.add_argument('views')
    ap.add_argument('out')
    ap.add_argument('--hide', action='store_true', help='monsters made invisible during the views')
    ap.add_argument('--give', default='', help='inventory given before the first view (comma separated)')
    ap.add_argument('--size', default='1920x1080')
    ap.add_argument('--wait', type=int, default=180, help='tics before the first view (title card)')
    ap.add_argument('--name', default=None, help='run name (logs, shots); default from the output folder')
    a = ap.parse_args()
    pk3 = Path(a.pk3).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    views = json.loads(Path(a.views).read_text(encoding='utf-8'))
    name = a.name or ('cv_' + re.sub(r'[^A-Za-z0-9_]+', '_', out.name))[:60]
    probe = Path(tempfile.gettempdir()) / f'{name}_probe.pk3'
    cmd = [sys.executable, str(HERE / 'view_check_pk3.py'), a.views, str(probe), str(a.wait)]
    if a.hide:
        cmd.append('hide')
    if a.give:
        cmd.append('give=' + a.give)
    subprocess.run(cmd, check=True, capture_output=True)
    w, h = (int(x) for x in a.size.split('x'))
    status, text, shots = devrun.run(pk3, name, a.map.upper(), seconds=60 + 3 * len(views), width=w, height=h,
                                     marker='RF_DEV_UI_DONE', extra=['-file', str(probe)])
    logged = [(int(i), l, int(t)) for i, l, t in re.findall(r'RF_VIEWCHECK index=(\d+) label=(\S+) t=(\d+)', text)]
    by_tic = {}
    for p in sorted(shots.glob('*.png')):
        t = ticcode.read(p)
        if t is not None:
            by_tic.setdefault(t, p)
    rows = []
    for i, label, t in logged:
        p = by_tic.get(t)
        dst = out / f'{i:02d}_{label}.png'
        if p is not None:
            shutil.copy2(p, dst)
        rows.append(dict(index=i, label=label, tic=t, kept=p is not None, file=dst.name if p else None))
    missing = [v[0] for v in views if v[0] not in {r['label'] for r in rows}]
    report = dict(build=str(pk3), build_sha256=hashlib.sha256(pk3.read_bytes()).hexdigest(), map=a.map.upper(),
                  views=a.views, hide=a.hide, give=a.give, size=a.size, status=status, rows=rows, not_reached=missing)
    (out / 'vues.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    kept = sum(r['kept'] for r in rows)
    print(f'{a.map.upper()}: {kept}/{len(views)} vues gardees -> {out}' + (f' ; non atteintes : {missing}' if missing else ''))
    return 0 if kept == len(views) else 1


if __name__ == '__main__':
    sys.exit(main())
