#!/usr/bin/env python3
"""The campaign chain in one game, on a frozen build, with a load in the middle: the targeted check of the freeze
that followed the player into the next chapter (candidates 1801 and 1708, fixed in 413457e) and of the endings.

Leg 1: new game at RF01, autopilot through RF01 -> RF02 -> RF04 -> start of RF05 (stopped on RF05's first scene,
its start autosave written by then). Leg 2: a new engine loads that autosave, autopilot RF05 -> RF06 -> RF07 -> exit
(RF07, the Jerma, since 01/10; --last RF06 for a build that ends there).
Each chapter change must show: the ending (RF_DEV_ENDING, with its page when the build has one, read by the
autopilot), the next map loaded, the arrival hold released with no frozen flag (RF_DEV_ARRIVAL ... cheats=0), the
inventory carried (RF_DEV_INV). Writes a JSON report.

Usage: python scripts/production/chain_test.py <build.pk3> <out.json> [--seconds 2400]
"""
import argparse, json, re, shutil, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import devrun  # noqa: E402

FAIL = r'RF_DEV_AUTOPILOT_(STUCK|TIMEOUT|DEAD)\b'
SAVES = devrun.DEV / 'saves'
CHAIN1 = ['RF01', 'RF02', 'RF04']
CHAIN2 = ['RF05', 'RF06', 'RF07']


def lines(text, prefix):
    return [l for l in text.splitlines() if l.startswith(prefix)]


def summary(text):
    return dict(loaded=lines(text, 'RF_DEV_LOADED'),
                exits=[l for l in lines(text, 'RF_DEV_UNLOADED') if not l.rstrip().endswith('next=')],
                endings=lines(text, 'RF_DEV_ENDING'), comics=lines(text, 'RF_DEV_COMIC'),
                arrivals=lines(text, 'RF_DEV_ARRIVAL'), inventory=lines(text, 'RF_DEV_INV'),
                failures=[l for l in text.splitlines() if re.match(FAIL, l)],
                waypoints=len(lines(text, 'RF_DEV_WAYPOINT')),
                script_errors=[l for l in text.splitlines() if 'Script error' in l or 'VM execution aborted' in l])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pk3')
    ap.add_argument('out')
    ap.add_argument('--seconds', type=float, default=2400)
    ap.add_argument('--last', default='RF07', help='the last chapter of the build (RF06 before 01/10)')
    a = ap.parse_args()
    pk3 = Path(a.pk3).resolve()
    t0 = time.time()
    s1, text1, _ = devrun.run(pk3, 'chain_leg1', 'RF01', autopilot=True, seconds=a.seconds, speed=4,
                              marker=rf're:^(RF_DEV_SCENE key=RF_RF05_HEAT|{FAIL})')
    time.sleep(1.0)
    leg1 = summary(text1)
    rf05 = []
    for p in SAVES.glob('*.zds'):
        if p.stat().st_mtime >= t0:
            info = json.loads(zipfile.ZipFile(p).read('info.json'))
            if info.get('Current Map') == 'RF05':
                rf05.append((p.stat().st_mtime, p))
    report = dict(pk3=str(pk3), leg1=dict(status=s1, **leg1))
    if not rf05:
        report.update(ok=False, reason='no RF05 autosave written in leg 1')
    else:
        # Kept under its own name at once: autosaves rotate, and another run between the two legs (any map that
        # autosaves on this savedir) would overwrite the slot before leg 2 loads it (01/10: a boss bench run did).
        save = SAVES / f'chain_rf05_{time.strftime("%Y%m%d_%H%M%S")}.zds'
        shutil.copy2(max(rf05)[1], save)
        s2, text2, _ = devrun.run(pk3, 'chain_leg2', None, autopilot=True, seconds=a.seconds / 2, speed=4, loadgame=save,
                                  marker=rf're:^(RF_DEV_UNLOADED map={a.last} time=\d+ next=\S+|{FAIL})')
        leg2 = summary(text2)
        maps1 = [re.search(r'map=(\w+)', l).group(1) for l in leg1['exits']]
        maps2 = [re.search(r'map=(\w+)', l).group(1) for l in leg2['exits']]
        released = {re.search(r'map=(\w+)', l).group(1): ('cheats=0' in l) for l in leg1['arrivals'] + leg2['arrivals']}
        chain2 = CHAIN2[:CHAIN2.index(a.last) + 1]
        expected_arrivals = ['RF02', 'RF04', 'RF05'] + chain2[1:]
        not_released = [m for m in expected_arrivals if not released.get(m)]    # RF06, RF07 are reached after the load
        report.update(save=str(save), leg2=dict(status=s2, **leg2), maps_exited=maps1 + maps2,
                      arrivals_released=released, not_released=not_released)
        report['ok'] = (maps1 == CHAIN1 and maps2 == chain2 and not not_released and not leg1['failures']
                        and not leg2['failures'] and not leg1['script_errors'] and not leg2['script_errors']
                        and any('save=1' in l and 'map=RF05' in l for l in leg2['loaded']))
    Path(a.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('CHAIN:', 'PASS' if report['ok'] else 'FAIL', report.get('maps_exited'), report.get('reason', ''),
          'non liberes:', report.get('not_released'))
    for l in report['leg1']['endings'] + report.get('leg2', {}).get('endings', []):
        print('  ', l[:160])
    for l in report['leg1']['arrivals'] + report.get('leg2', {}).get('arrivals', []):
        print('  ', l[:160])
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
