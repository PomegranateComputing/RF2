#!/usr/bin/env python3
"""UI evidence for gate D, in the real engine, through console commands only.

For each resolution: title-screen main menu, options menu, credits, in-game pause menu and the
in-game HUD, each captured to build/dev/shots/ui_<w>x<h>/. Then the persistence check: a first
run sets rf_hud_scale and quits cleanly (config written on exit), a second run starts and the
value is read back from the config file.

Usage: python scripts/ui_evidence.py [--res 1920x1080 2560x1440]
"""
import argparse, re, shutil, sys, time
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devrun  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / 'dist' / 'RF2_DEV.pk3'


def cmds(*parts):
    """Command-line console commands executed in order; 'wait N' delays by N tics."""
    out = []
    for p in parts:
        out += ['+' + p.split(' ', 1)[0]] + ([p.split(' ', 1)[1]] if ' ' in p else [])
    return out


def shots(w, h):
    name = f'ui_{w}x{h}'
    # title screen menus
    devrun.run(PK3, name, None, seconds=40, width=w, height=h, marker='re:^RF_UI_DONE',
               extra=cmds('wait 70', 'menu_main', 'wait 20', 'screenshot', 'wait 10', 'menu_options', 'wait 20',
                          'screenshot', 'wait 10', 'closemenu', 'openmenu RFCreditsMenu', 'wait 20', 'screenshot',
                          'wait 10', 'echo RF_UI_DONE'))
    first = sorted((devrun.DEV / 'shots' / name).glob('*.png'))
    keep = devrun.DEV / 'shots' / f'{name}_menus'
    if keep.exists():
        shutil.rmtree(keep)
    keep.mkdir(parents=True)
    for p in first:
        shutil.copy(p, keep / p.name)
    # in game: HUD after the title flash, then the pause menu
    devrun.run(PK3, name, 'RF01', seconds=40, width=w, height=h, marker='re:^RF_UI_DONE',
               extra=cmds('wait 70', 'screenshot', 'wait 140', 'screenshot', 'menu_main', 'wait 20', 'screenshot',
                          'wait 10', 'echo RF_UI_DONE'))
    return keep, devrun.DEV / 'shots' / name


def persistence():
    cfg = devrun.DEV / 'uzdoom.ini'
    value = '1.15'
    devrun.run(PK3, 'ui_persist_1', None, seconds=30, marker=None,
               extra=cmds('wait 35', f'set rf_hud_scale {value}', 'wait 10', 'quit'))
    text = cfg.read_text(encoding='utf-8', errors='replace') if cfg.exists() else ''
    saved = re.search(r'^rf_hud_scale=(\S+)', text, re.M)
    status, log, _ = devrun.run(PK3, 'ui_persist_2', None, seconds=30, marker='re:^RF_UI_VALUE',
                                extra=cmds('wait 35', 'echo RF_UI_VALUE', 'rf_hud_scale', 'wait 10', 'quit'))
    shown = re.search(r'"rf_hud_scale" is "([^"]+)"', log)
    # restore the default for the other dev runs
    devrun.run(PK3, 'ui_persist_3', None, seconds=30, marker=None,
               extra=cmds('wait 20', 'set rf_hud_scale 1.0', 'wait 5', 'quit'))
    ok = bool(saved and abs(float(saved.group(1)) - float(value)) < 1e-3 and shown and abs(float(shown.group(1)) - float(value)) < 1e-3)
    return ok, saved.group(1) if saved else None, shown.group(1) if shown else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--res', nargs='*', default=['1920x1080', '2560x1440'])
    ap.add_argument('--skip-persistence', action='store_true')
    a = ap.parse_args()
    for r in a.res:
        w, h = map(int, r.split('x'))
        menus, game = shots(w, h)
        pngs = sorted(menus.glob('*.png')) + sorted(game.glob('*.png'))
        sizes = sorted({Image.open(p).size for p in pngs})
        size_ok = sizes == [(w, h)]
        print(f'{r}: menus {len(list(menus.glob("*.png")))} shots in {menus}; game {len(list(game.glob("*.png")))} shots in {game}; '
              f'capture size {sizes} {"OK" if size_ok else "MISMATCH"}')
    if not a.skip_persistence:
        ok, saved, shown = persistence()
        print(f'persistence: {"PASS" if ok else "FAIL"} (config {saved}, read back {shown})')


if __name__ == '__main__':
    main()
