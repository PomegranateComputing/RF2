#!/usr/bin/env python3
"""Every door of RF01 used from both sides in the real engine (gate B: doors verified).

The dev handler (rf_dev_doortest) stands the player in front of each door line, on the room
side, and presses use. Pass 1 without keys: plain doors must open, locked sides must stay shut.
Pass 2 with the grille key and the passe: locks 1 and 2 must open; lock 3 (porch grille, raised
by the winch only) and lock 4 (gallery grille, one-way) must stay shut.

Usage: python scripts/doortest_rf01.py [--speed 4]
"""
import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devrun  # noqa: E402

PK3 = Path(__file__).resolve().parents[1] / 'dist' / 'RF2_DEV.pk3'
KEYED = {1, 2}          # opened by keys found in RF01 (locks 3 and 4 never open by use)


def expected(pass_no, special, lock):
    if special != 13:
        return 'open'
    if pass_no == 1:
        return 'shut'
    return 'open' if lock in KEYED else 'shut'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--speed', type=float, default=4.0)
    a = ap.parse_args()
    status, text, _ = devrun.run(PK3, 'doortest', 'RF01', seconds=600, speed=a.speed,
                                 extra=['+rf_dev_doortest', '1'], marker='RF_DEV_DOORTEST_DONE')
    rows = re.findall(r'RF_DEV_DOOR pass=(\d) line=(\d+) special=(\d+) tag=(\d+) lock=(\d+) result=(\w+) h=(-?\d+)', text)
    bad = []
    skipped = 0
    for p, line, special, tag, lock, result, h in rows:
        if result == 'was_open':          # opened for good earlier (Door_Open): nothing to judge
            skipped += 1
            continue
        want = expected(int(p), int(special), int(lock))
        if result != want:
            bad.append(f'pass {p} line {line} tag {tag} special {special} lock {lock}: {result} (expected {want}, h={h})')
    tags = {int(r[3]) for r in rows}
    print(f'door lines tested: {len(rows)} ({len(tags)} doors, {skipped} already open for good), status {status}')
    for b in bad:
        print('  MISMATCH ' + b)
    ok = rows and not bad and 'RF_DEV_DOORTEST_DONE' in text
    print('DOORTEST: ' + ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
