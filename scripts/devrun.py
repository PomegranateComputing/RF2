#!/usr/bin/env python3
"""Headless-ish UZDoom runner for development checks.

Launches the pinned UZDoom 5.0.1 with the dev IWAD and a PK3, captures stdout to a log,
stops when a console marker appears (or on timeout), and collects screenshots.

Examples:
  python scripts/devrun.py --norun                      # ZScript/lump compile gate
  python scripts/devrun.py --map RF01 --tour            # screenshot tour of RFTourPoint markers
  python scripts/devrun.py --map RF01 --autopilot       # waypoint playthrough (RFDevWaypoint)
  python scripts/devrun.py --map RF01 --seconds 20      # plain boot, killed after 20 s
"""
import argparse, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe')
IWAD = Path(r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad')
DEV = ROOT / 'build' / 'dev'


def run(pk3, name, map_name=None, norun=False, tour=False, autopilot=False, seconds=60,
        marker=None, extra=None, width=1920, height=1080, quiet=False):
    DEV.mkdir(parents=True, exist_ok=True)
    cfg = DEV / 'uzdoom.ini'
    if not cfg.exists():
        shutil.copy(ROOT / 'user' / 'uzdoom.ini', cfg)
    shots = DEV / 'shots' / name
    if shots.exists():
        shutil.rmtree(shots)
    shots.mkdir(parents=True)
    log = DEV / 'logs' / f'{name}.txt'
    log.parent.mkdir(parents=True, exist_ok=True)
    args = [str(ENGINE), '-stdout', '-iwad', str(IWAD), '-file', str(pk3), '-config', str(cfg),
            '-savedir', str(DEV / 'saves'), '-width', str(width), '-height', str(height),
            '+vid_fullscreen', '0', '+screenshot_dir', str(shots), '+screenshot_type', 'png', '+enablescriptscreenshot', '1', '+con_notifylines', '0']
    if norun:
        args.append('-norun')
    if map_name:
        args += ['+map', map_name]
    if tour:
        args += ['+rf_dev_tour', '1']
        marker = marker or 'RF_DEV_TOUR_DONE'
    if autopilot:
        args += ['+rf_dev_autopilot', '1']
        marker = marker or 'RF_DEV_AUTOPILOT'
    if extra:
        args += extra
    start = time.time()
    with open(log, 'w', encoding='utf-8', errors='replace') as lf:
        proc = subprocess.Popen(args, stdout=lf, stderr=subprocess.STDOUT, cwd=str(ROOT))
        status = 'exited'
        while True:
            rc = proc.poll()
            if rc is not None:
                status = f'exited rc={rc}'
                break
            if time.time() - start > seconds:
                proc.kill()
                status = 'timeout-killed'
                break
            if marker:
                try:
                    text = log.read_text(encoding='utf-8', errors='replace')
                except OSError:
                    text = ''
                if marker in text:
                    time.sleep(1.5)  # let the last screenshot flush
                    proc.kill()
                    status = f'marker:{marker}'
                    break
            time.sleep(0.25)
    elapsed = time.time() - start
    text = log.read_text(encoding='utf-8', errors='replace')
    if not quiet:
        print(f'[{name}] {status} after {elapsed:.1f}s, log={log}')
    return status, text, shots


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pk3', default=str(ROOT / 'dist' / 'RF2_DEV.pk3'))
    ap.add_argument('--name', default=None)
    ap.add_argument('--map', dest='map_name', default=None)
    ap.add_argument('--norun', action='store_true')
    ap.add_argument('--tour', action='store_true')
    ap.add_argument('--autopilot', action='store_true')
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--marker', default=None)
    ap.add_argument('--width', type=int, default=1920)
    ap.add_argument('--height', type=int, default=1080)
    ap.add_argument('--grep', default='RF_DEV_|rror|arning|nknown|issing|nvalid|ould not|xecution')
    ap.add_argument('extra', nargs='*')
    a = ap.parse_args()
    name = a.name or ('norun' if a.norun else f"{a.map_name or 'boot'}_{'tour' if a.tour else 'auto' if a.autopilot else 'run'}")
    status, text, shots = run(a.pk3, name, a.map_name, a.norun, a.tour, a.autopilot, a.seconds, a.marker, a.extra, a.width, a.height)
    import re
    rx = re.compile(a.grep)
    lines = [l for l in text.splitlines() if rx.search(l)]
    print('\n'.join(lines[-80:]))
    print('--- tail ---')
    print('\n'.join(text.splitlines()[-6:]))
    pngs = sorted(shots.glob('*.png'))
    if pngs:
        print(f'screenshots: {len(pngs)} in {shots}')
    sys.exit(0 if status.startswith(('marker', 'exited rc=0')) else 1)


if __name__ == '__main__':
    main()
