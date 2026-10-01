#!/usr/bin/env python3
"""Engine test of the boss bench: the module over its frozen base, with a probe player that walks into the hall,
crosses the entry line and fights with the FAL (aim and fire handled by the probe, like a player who keeps the boss in
his sights and steps back when the stamp is raised). Checks, from the bench's console lines and the probe's log:
entry (doors, walk, untouchable during the entry), the three announced attacks seen, phase 2, the whistle and the
staff, the boss's death, the victory and the reprise (a second fight starts after it). Screenshots of each announce.

Usage: python bench/boss/test_boss_bench.py <bench folder dist/boss/RF2_BOSS_ESSAI_...> [--seconds 300]
Writes <bench folder>/preuves/test_boss.json and the screenshots there.
"""
import argparse, json, re, shutil, sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import devrun  # noqa: E402

PROBE = r'''version "4.14"
class RFBossProbe : RFPlayer
{
    int t, shots, lastAnnounce, phaseSeen, stampSeen, doneSaid;
    override void PlayerThink()
    {
        if (player != null && Level.maptime > 40)
        {
            if (t++ == 0)
            {
                GiveInventory("RFFAL", 1);
                GiveInventory("RFRifleAmmo", 400);
                player.PendingWeapon = Weapon(FindInventory("RFFAL"));
                player.cheats |= CF_GODMODE;      // the probe tests the boss, not the player's survival
            }
            player.cmd.buttons = 0;
            player.cmd.forwardmove = 0;
            player.cmd.sidemove = 0;
            let boss = RFBossSurveillant(ThinkerIterator.Create('RFBossSurveillant').Next());
            let bench = RFBossBench(EventHandler.Find('RFBossBench'));
            if (bench != null && !bench.engaged && !bench.won)
            {
                // walk north into the hall until the entry line fires
                angle = 90;
                player.cmd.forwardmove = 3200;
            }
            else if (boss != null && boss.health > 0)
            {
                Vector2 d = boss.Pos.XY - Pos.XY;
                angle = VectorAngle(d.X, d.Y);
                pitch = 0;
                double dist = d.Length();
                if (boss.announce == 1) stampSeen = 1;
                if (!stampSeen && !boss.bInvulnerable) player.cmd.forwardmove = dist > 72 ? 3200 : 0;   // close in once
                else if (boss.announce == 1 || dist < 140) player.cmd.forwardmove = -3200;              // back off the stamp
                else if (dist > 420) player.cmd.forwardmove = 2400;
                if (!boss.bInvulnerable && (Level.maptime % 9) < 3) { player.cmd.buttons |= BT_ATTACK; }
                if ((Level.maptime % 120) < 4) player.cmd.buttons |= BT_RELOAD;
                if (boss.announce != lastAnnounce)
                {
                    if (boss.announce > 0)
                    {
                        Console.Printf("RF_BOSSPROBE announce=%d t=%d health=%d phase=%d", boss.announce, Level.maptime, boss.health, boss.phase);
                        Level.MakeScreenShot();
                    }
                    lastAnnounce = boss.announce;
                }
                if (boss.phase == 2 && phaseSeen == 0) { phaseSeen = 1; Console.Printf("RF_BOSSPROBE phase2 t=%d", Level.maptime); Level.MakeScreenShot(); }
            }
            if (bench != null && bench.won && (Level.maptime % 70) == 0) Level.MakeScreenShot();
            if (bench != null && bench.victories >= 1 && bench.attempts >= 2 && bench.engaged && !doneSaid++)
            {
                Console.Printf("RF_BOSSPROBE second_entry t=%d", Level.maptime);
                Console.Printf("RF_DEV_UI_DONE");
            }
        }
        Super.PlayerThink();
    }
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bench')
    ap.add_argument('--seconds', type=int, default=300)
    a = ap.parse_args()
    bench = Path(a.bench).resolve()
    info = json.loads((bench / 'BUILD_INFO.json').read_text(encoding='utf-8'))
    base, module = ROOT / info['base'], ROOT / info['module']
    probe = Path(tempfile.gettempdir()) / 'rf2_boss_probe.pk3'
    with zipfile.ZipFile(probe, 'w') as z:
        z.writestr('ZSCRIPT.bossprobe', PROBE)
        z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFBossProbe"\n}\n')
    status, text, shots = devrun.run(base, 'boss_bench_test', 'BOSS01', seconds=a.seconds, width=1280, height=720,
                                     marker='RF_DEV_UI_DONE', extra=['-file', str(module), str(probe)])
    lines = [l for l in text.splitlines() if l.startswith(('RF_BOSS', 'RF_BOSSPROBE'))]
    errors = [l for l in text.splitlines() if 'Script error' in l or 'VM execution aborted' in l or 'error' in l.lower() and 'zscript' in l.lower()]
    announces = sorted({int(m) for m in re.findall(r'announce=(\d)', text)})
    report = dict(bench=str(bench), module_sha256=info['module_sha256'], status=status, lines=lines, errors=errors,
                  entry='RF_BOSS entry attempt=1' in text, announces_seen=announces, phase2='RF_BOSSPROBE phase2' in text,
                  whistle=bool(re.search(r'RF_BOSS whistle staff=[12]', text)), victory='RF_BOSS victory' in text,
                  reprise='RF_BOSS reprise' in text, second_entry='RF_BOSSPROBE second_entry' in text)
    report['ok'] = all(report[k] for k in ('entry', 'phase2', 'whistle', 'victory', 'reprise', 'second_entry')) \
        and announces == [1, 2, 3] and not errors
    out = bench / 'preuves'
    out.mkdir(exist_ok=True)
    for old in out.glob('boss_*.png'):
        old.unlink()
    for i, p in enumerate(sorted(shots.glob('*.png'))):
        shutil.copy2(p, out / f'boss_{i:02d}.png')
    (out / 'test_boss.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('BOSS BENCH:', 'PASS' if report['ok'] else 'FAIL', {k: report[k] for k in ('entry', 'announces_seen', 'phase2', 'whistle', 'victory', 'reprise', 'second_entry')})
    for l in errors[:5]:
        print('  ', l)
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
