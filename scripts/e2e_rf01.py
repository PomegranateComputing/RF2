#!/usr/bin/env python3
"""RF01 end-to-end runs in the real engine (gate E), driven by ordinary player input only.

Run A: new game -> RF01 -> exit.
Run B: new game -> save mid-level -> quit -> relaunch -> load -> die -> resume -> exit.

The autopilot (RFDevHandler, rf_dev_autopilot) walks the RFDevWaypoint route of the map with
movement, use, fire and reload commands: no noclip, god mode, warp or give. "Quit" in run B is
the termination of the engine process once the autosave file exists; the relaunch loads that
file with -loadgame. Death is obtained by a pacifist first life after the load; the autopilot
then presses use on the death screen, which reloads the last save like a player would.

Usage: python scripts/e2e_rf01.py [--speed 4] [--save-at 29] [--only A|B]
Writes build/dev/e2e/RF01_E2E_<stamp>.json and prints a short verdict.
"""
import argparse, json, os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devrun  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / 'dist' / 'RF2_DEV.pk3'
SAVES = devrun.DEV / 'saves'
FAIL = r'RF_DEV_AUTOPILOT_(STUCK|TIMEOUT|DEAD)\b'


def markers(text):
    lines = [l for l in text.splitlines() if l.startswith('RF_DEV_')]
    return dict(
        loaded=[l for l in lines if l.startswith('RF_DEV_LOADED')],
        exits=[l for l in lines if l.startswith('RF_DEV_UNLOADED')],
        waypoints=len([l for l in lines if l.startswith('RF_DEV_WAYPOINT')]),
        kills=len([l for l in lines if l.startswith('RF_DEV_DIED')]),
        deaths=[l for l in lines if l.startswith('RF_DEV_AUTOPILOT_DEATH')],
        failures=[l for l in lines if re.match(FAIL, l)],
        objectives=[int(m.group(1)) for m in re.finditer(r'RF_DEV_LINE .*objective=(\d+)', text) if int(m.group(1)) > 0],
        saves=[l for l in lines if l.startswith('RF_DEV_SAVE_REQUESTED')],
        resumes=[l for l in lines if l.startswith('RF_DEV_RESUME_REQUESTED')],
        script_errors=[l for l in text.splitlines() if 'Script error' in l or 'VM execution aborted' in l],
    )


def exited_rf01(m):
    # A real exit names the next map; a teardown for a savegame load has an empty next=.
    return any(re.search(r'map=RF01 .*next=\S+', l) for l in m['exits'])


def run_a(speed, seconds):
    status, text, _ = devrun.run(PK3, 'e2e_A', 'RF01', autopilot=True, seconds=seconds, speed=speed,
                                 marker=rf're:^(RF_DEV_UNLOADED map=RF01 time=\d+ next=\S+|{FAIL})')
    m = markers(text)
    ok = exited_rf01(m) and not m['failures'] and not m['script_errors']
    return dict(run='A', ok=ok, status=status, **m)


def run_b(speed, seconds, save_at):
    SAVES.mkdir(parents=True, exist_ok=True)
    before = {p: p.stat().st_mtime for p in SAVES.glob('*.zds')}
    # B1: new game, autosave after waypoint `save_at`, then quit (process terminated after the write).
    status1, text1, _ = devrun.run(PK3, 'e2e_B1', 'RF01', autopilot=True, seconds=seconds, speed=speed,
                                   extra=['+rf_dev_save_at', str(save_at)],
                                   marker=f're:^(RF_DEV_SAVE_REQUESTED|{FAIL})')
    time.sleep(1.0)
    m1 = markers(text1)
    fresh = [p for p in SAVES.glob('*.zds') if before.get(p) != p.stat().st_mtime]
    save = max(fresh, key=os.path.getmtime) if fresh else None
    if not m1['saves'] or save is None:
        return dict(run='B', ok=False, reason='no save written', b1=dict(status=status1, **m1))
    # B2: relaunch, load, pacifist first life -> death -> use -> reload -> autopilot to the exit.
    status2, text2, _ = devrun.run(PK3, 'e2e_B2', None, autopilot=True, seconds=seconds, speed=speed, loadgame=save,
                                   extra=['+rf_dev_start_wp', str(save_at + 1), '+rf_dev_pacifist', '1'],
                                   marker=rf're:^(RF_DEV_UNLOADED map=RF01 time=\d+ next=\S+|{FAIL})')
    m2 = markers(text2)
    loaded_from_save = [l for l in m2['loaded'] if 'save=1' in l]
    ok = (exited_rf01(m2) and len(m2['deaths']) >= 1 and len(m2['resumes']) >= 1 and len(loaded_from_save) >= 2
          and not m2['failures'] and not m1['script_errors'] and not m2['script_errors'])
    return dict(run='B', ok=ok, save=str(save), save_at=save_at,
                b1=dict(status=status1, **m1), b2=dict(status=status2, loaded_from_save=len(loaded_from_save), **m2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--speed', type=float, default=4.0)
    ap.add_argument('--seconds', type=float, default=600)
    ap.add_argument('--save-at', type=int, default=29, help='waypoint after which run B saves')
    ap.add_argument('--only', choices=('A', 'B'))
    a = ap.parse_args()
    results = []
    if a.only in (None, 'A'):
        results.append(run_a(a.speed, a.seconds))
    if a.only in (None, 'B'):
        results.append(run_b(a.speed, a.seconds, a.save_at))
    out = devrun.DEV / 'e2e'
    out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    report = dict(map='RF01', pk3=str(PK3), speed=a.speed, input='autopilot (ordinary player commands)', results=results)
    path = out / f'RF01_E2E_{stamp}.json'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    for r in results:
        if r['run'] == 'A':
            print(f"RUN A: {'PASS' if r['ok'] else 'FAIL'}  waypoints={r['waypoints']} kills={r['kills']} "
                  f"objectives={r['objectives']} failures={r['failures'][:2]} errors={r['script_errors'][:2]}")
        else:
            b2 = r.get('b2', {})
            print(f"RUN B: {'PASS' if r['ok'] else 'FAIL'}  save={r.get('save')} deaths={len(b2.get('deaths', []))} "
                  f"resumes={len(b2.get('resumes', []))} loads={b2.get('loaded_from_save')} "
                  f"failures={b2.get('failures', [])[:2]} {r.get('reason', '')}")
    print(f'report: {path}')
    sys.exit(0 if all(r['ok'] for r in results) else 1)


if __name__ == '__main__':
    main()
