#!/usr/bin/env python3
"""Compile gate (-norun) on a separate, invisible Windows desktop.

For a shared machine where another session needs the interactive desktop undisturbed: the engine
starts on its own desktop (hiddendesk.py), so no window appears and focus never moves. -norun
loads every lump and compiles ZScript, then exits (no game loop, no rendering). A fatal error
dialog, invisible there, is detected and saved as build/dev/logs/norun_hidden_fatal.png.

Usage: python scripts/hidden_norun.py [--pk3 dist/RF2_DEV.pk3]
Writes build/dev/logs/norun_hidden.txt and prints script errors, if any.
"""
import argparse, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hiddendesk import HiddenProcess  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENGINE = r'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe'
IWAD = r'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pk3', default=str(ROOT / 'dist' / 'RF2_DEV.pk3'))
    ap.add_argument('--seconds', type=float, default=60)
    a = ap.parse_args()
    log = ROOT / 'build' / 'dev' / 'logs' / 'norun_hidden.txt'
    log.parent.mkdir(parents=True, exist_ok=True)
    fatal_png = log.with_name('norun_hidden_fatal.png')
    fatal_png.unlink(missing_ok=True)
    cfg = ROOT / 'build' / 'dev' / 'uzdoom.ini'
    start = time.time()
    proc = HiddenProcess([ENGINE, '-stdout', '-norun', '-iwad', IWAD, '-file', a.pk3, '-config', str(cfg)], log, cwd=ROOT)
    fatal = False
    while proc.poll() is None:
        if time.time() - start > a.seconds:
            proc.kill()
            break
        if proc.fatal_error(fatal_png):
            fatal = True
            proc.kill()
            break
        time.sleep(0.25)
    text = log.read_text(encoding='utf-8', errors='replace')
    errors = [l for l in text.splitlines() if re.search(r'Script error|rror:|Unknown|not found|Could not', l)]
    print(f'norun (hidden desktop): exit {proc.returncode} after {time.time() - start:.1f}s, log {log}')
    if fatal:
        print(f'  fatal error dialog: {fatal_png}')
    for e in errors[:60]:
        print('  ' + e)
    reached = 'D_CheckNetGame' in text and not fatal
    print('COMPILE: ' + ('PASS' if reached and not any('Script error' in e for e in errors) else 'FAIL'))
    return 0 if reached else 1


if __name__ == '__main__':
    sys.exit(main())
