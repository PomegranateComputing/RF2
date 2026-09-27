#!/usr/bin/env python3
"""Headless-ish UZDoom runner for development checks.

Launches the pinned UZDoom 5.0.1 with the dev IWAD and a PK3, captures stdout to a log,
stops when a console marker appears (or on timeout), and collects screenshots.

Examples:
  python scripts/devrun.py --norun                      # ZScript/lump compile gate
  python scripts/devrun.py --map RF01 --tour            # screenshot tour of RFTourPoint markers
  python scripts/devrun.py --map RF01 --autopilot       # waypoint playthrough (RFDevWaypoint)
  python scripts/devrun.py --map RF01 --seconds 20      # plain boot, killed after 20 s
  RF_DEV_HIDDEN=1 python scripts/devrun.py ...          # same, on an invisible desktop (shared machine)
  python scripts/devrun.py --map RF01 --name doors +rf_dev_doortest 1 --speed 4   # every door, both sides
"""
import argparse, os, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe')
IWAD = Path(r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad')
DEV = ROOT / 'build' / 'dev'


def run(pk3, name, map_name=None, norun=False, tour=False, autopilot=False, seconds=60,
        marker=None, extra=None, width=None, height=None, quiet=False, speed=1.0, loadgame=None, audio_wav=None):
    """marker: substring, or 're:<regex>' to stop on the first matching console line.

    width/height: client size of the game window (vid_setsize). Without them the window keeps the
    size stored in the config: -width/-height do nothing in windowed mode.
    audio_wav: the game's mixed sound output is written to this WAV (OpenAL Soft wave writer,
    32-bit float stereo) instead of the speakers. Hidden runs without it use OpenAL's null output:
    on a shared machine a test never sounds in the room."""
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
            '-savedir', str(DEV / 'saves'),
            '+vid_fullscreen', '0', '+screenshot_dir', str(shots), '+screenshot_type', 'png', '+enablescriptscreenshot', '1',
            '+i_pauseinbackground', '0',   # a shared machine: another window taking focus must not pause the test
            '+screenshot_quiet', '1']      # no "Captured ..." line in the next capture (dev config only)
    if norun:
        args.append('-norun')
    if width and height:
        args += ['+vid_setsize', str(width), str(height)]
    if loadgame:
        # UZDoom resolves -loadgame against -savedir: pass the file name, the save copied there if needed.
        save = Path(loadgame)
        if save.is_absolute() and save.parent.resolve() != (DEV / 'saves').resolve():
            (DEV / 'saves').mkdir(parents=True, exist_ok=True)
            shutil.copy(save, DEV / 'saves' / save.name)
        args += ['-loadgame', save.name]
    if map_name:
        args += ['+map', map_name]
    if tour:
        args += ['+rf_dev_tour', '1']
        marker = marker or 'RF_DEV_TOUR_DONE'
    if autopilot:
        args += ['+rf_dev_autopilot', '1']
        marker = marker or 'RF_DEV_AUTOPILOT'
    if extra and '+rf_dev_doortest' in extra:
        marker = marker or 'RF_DEV_DOORTEST_DONE'
    if extra and '+rf_dev_weapons' in extra:
        marker = marker or 'RF_DEV_WEAPONS_DONE'
    if extra and '+rf_dev_ui' in extra:
        marker = marker or 'RF_DEV_UI_DONE'
    if speed != 1.0:
        # i_timescale runs more game tics per real second; tic logic is unchanged.
        args += ['+i_timescale', str(speed)]
    if extra:
        args += extra
    start = time.time()
    hidden = os.environ.get('RF_DEV_HIDDEN') == '1'   # shared machine: run on an invisible desktop
    sound_env = {}
    if audio_wav:
        conf = log.with_name(f'{name}_alsoft.ini')
        conf.write_text('\n'.join(['[general]', 'drivers = wave', '[wave]', f'file = {Path(audio_wav).as_posix()}',
                                   'bformat = false', '']), encoding='utf-8')
        Path(audio_wav).unlink(missing_ok=True)
        sound_env = {'ALSOFT_DRIVERS': 'wave', 'ALSOFT_CONF': str(conf)}
    elif hidden:
        sound_env = {'ALSOFT_DRIVERS': 'null'}
    saved_env = {k: os.environ.get(k) for k in sound_env}
    os.environ.update(sound_env)              # read by the child at creation, restored right after
    with open(log, 'w', encoding='utf-8', errors='replace') as lf:
        try:
            if hidden:
                lf.close()
                from hiddendesk import HiddenProcess
                proc = HiddenProcess(args, log, cwd=ROOT)
            else:
                proc = subprocess.Popen(args, stdout=lf, stderr=subprocess.STDOUT, cwd=str(ROOT))
        finally:
            for k, v in saved_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
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
            if hidden and proc.fatal_error(log.with_name(f'{name}_fatal.png')):
                proc.kill()                  # the error dialog would wait forever on the hidden desktop
                status = f'fatal-error (dialog captured: {log.with_name(name + "_fatal.png")})'
                break
            if marker:
                try:
                    text = log.read_text(encoding='utf-8', errors='replace')
                except OSError:
                    text = ''
                hit = re.search(marker[3:], text, re.M) if marker.startswith('re:') else (marker in text)
                if hit:
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
    ap.add_argument('--width', type=int, default=None, help='game window client width (default: config size)')
    ap.add_argument('--height', type=int, default=None)
    ap.add_argument('--speed', type=float, default=1.0, help='i_timescale (game tics per real tic)')
    ap.add_argument('--loadgame', default=None, help="savegame path, or 'latest' (newest in build/dev/saves)")
    ap.add_argument('--grep', default='RF_DEV_|rror|arning|nknown|issing|nvalid|ould not|xecution')
    ap.add_argument('extra', nargs='*')
    a = ap.parse_args()
    name = a.name or ('norun' if a.norun else f"{a.map_name or 'boot'}_{'tour' if a.tour else 'auto' if a.autopilot else 'run'}")
    loadgame = a.loadgame
    if loadgame == 'latest':
        saves = sorted((DEV / 'saves').glob('*.zds'), key=os.path.getmtime)
        loadgame = saves[-1] if saves else None
    status, text, shots = run(a.pk3, name, a.map_name, a.norun, a.tour, a.autopilot, a.seconds, a.marker, a.extra, a.width, a.height,
                              speed=a.speed, loadgame=loadgame)
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
