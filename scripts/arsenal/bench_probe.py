#!/usr/bin/env python3
"""Scripted checks of the arsenal test bench in the engine: counters and transitions only.

    python scripts/arsenal/bench_probe.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3

A probe player (loaded as a third file, for this run only) plays a fixed timeline on the range: W03 emptied, dry
fire, full and topping reloads, fire during a reload, weapon switch during a reload; W04 emptied, dry fire, reload
from empty, partial reload, fire during a reload, short reserve, empty reserve; then a save, and a second run loads it.
The checks are the contract's rules (RF2-ARSENAL 4), read from the bench's own log lines, not a copy of its code:
  - rounds are conserved at every event (loaded + reserve + fired = what was given): "ecart" stays 0;
  - no count below zero or above capacity; no ERREUR line;
  - each shot gives exactly its pellets' impacts (bullet puffs counted by the probe), a dry fire gives none;
  - fire pressed during a reload: a shot comes before any further round goes in;
  - weapon switched during a reload: no round goes in afterwards for that weapon;
  - an empty reserve starts no reload;
  - after save and load, the counts are the ones saved, and the weapon fires.
Nothing here says whether the animation looks or sounds right: that needs eyes and ears.
"""
import argparse, json, re, subprocess, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PROBE = r'''version "4.14"
class RFBenchProbeCount : EventHandler
{
    int puffs;
    override void WorldThingSpawned(WorldEvent e)
    {
        if (e.Thing is 'RFBulletPuff') puffs++;
    }
}

class RFBenchProbe : RFPlayer
{
    int t;
    transient bool live;     // not saved: false after loading the probe's own save

    RFBenchWeapon W(Name cls) { return RFBenchWeapon(FindInventory(cls)); }

    void Say(String what)
    {
        let h = RFBenchProbeCount(EventHandler.Find('RFBenchProbeCount'));
        String cur = "";
        let w = RFBenchWeapon(player.ReadyWeapon);
        if (w != null) cur = String.Format("%s charge=%d reserve=%d tirs=%d ecart=%d seq=%s", w.GetClassName(), w.Loaded(), w.Reserve(), w.Shots, w.Balance(), w.SeqName);
        Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_PROBE t=%d %s puffs=%d arme=%s", t, what, h ? h.puffs : -1, cur);
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            int b = 0;
            // ---- W03: 6 shots (5 in the tube + 1 chambered), then a dry fire
            if (t == 20) Say("W03_depart");
            if (t >= 30 && t <= 155 && (t - 30) % 25 == 0) { b |= BT_ATTACK; }
            if (t == 175) Say("W03_apres_6_tirs");
            if (t == 180) b |= BT_ATTACK;
            if (t == 196) Say("W03_apres_tir_a_vide");
            // full reload from empty, then a topping reload
            if (t == 200) b |= BT_RELOAD;
            if (t == 300) Say("W03_apres_recharge");
            if (t == 305) b |= BT_RELOAD;
            if (t == 336) Say("W03_apres_complement");
            if (t == 340 || t == 365) b |= BT_ATTACK;
            if (t == 388) Say("W03_apres_2_tirs");
            // fire during a reload
            if (t == 390) b |= BT_RELOAD;
            if (t == 415) { b |= BT_ATTACK; Say("W03_tir_pendant_recharge"); }
            if (t == 455) Say("W03_apres_interruption_par_tir");
            // switch during a reload
            if (t == 460) b |= BT_RELOAD;
            if (t == 471) { player.PendingWeapon = Weapon(FindInventory('RFBenchMR73')); Say("W03_changement_pendant_recharge"); }
            if (t == 515) Say("W04_depart");
            // ---- W04: 6 shots, a dry fire, reload from empty
            if (t >= 520 && t <= 620 && (t - 520) % 20 == 0) b |= BT_ATTACK;
            if (t == 638) Say("W04_apres_6_tirs");
            if (t == 640) b |= BT_ATTACK;
            if (t == 655) Say("W04_apres_tir_a_vide");
            if (t == 660) b |= BT_RELOAD;
            if (t == 736) Say("W04_apres_recharge");
            // partial reload after 2 shots (rule a)
            if (t == 740 || t == 760) b |= BT_ATTACK;
            if (t == 778) Say("W04_apres_2_tirs");
            if (t == 780) b |= BT_RELOAD;
            if (t == 856) Say("W04_apres_recharge_partielle");
            // fire during a reload
            if (t >= 860 && t <= 940 && (t - 860) % 20 == 0) b |= BT_ATTACK;
            if (t == 958) Say("W04_apres_5_tirs");
            if (t == 960) b |= BT_RELOAD;
            if (t == 994) { b |= BT_ATTACK; Say("W04_tir_pendant_recharge"); }
            if (t == 1030) Say("W04_apres_interruption_par_tir");
            // short reserve, then empty reserve
            if (t >= 1040 && t <= 1120 && (t - 1040) % 20 == 0) b |= BT_ATTACK;
            if (t == 1148)
            {
                let w = W('RFBenchMR73');
                int keep = 2, had = CountInv('RFBenchMagnum');
                if (had > keep)
                {
                    TakeInventory('RFBenchMagnum', had - keep, true);
                    if (w != null) w.Baseline -= had - keep;      // taken by the probe, not by the weapon
                }
                Say(String.Format("W04_reserve_ramenee_a_2 retirees=%d", had - keep));
            }
            if (t == 1160) b |= BT_RELOAD;
            if (t == 1240) Say("W04_apres_recharge_reserve_courte");
            if (t == 1250) b |= BT_RELOAD;
            if (t == 1290) Say("W04_apres_recharge_reserve_vide");
            if (t == 1300) { player.PendingWeapon = Weapon(FindInventory('RFBenchRapid')); }
            if (t == 1) live = true;
            if (t == 1330 && live) { Say("sauvegarde"); Level.MakeAutoSave(); }
            if (t == 1360 && live) Console.Printf("RF_DEV_UI_DONE");
            // second run: the save loaded (live is false), counts read back, one shot
            if (t == 1365 && !live) Say("apres_chargement");
            if (t == 1370 && !live) b |= BT_ATTACK;
            if (t == 1405 && !live) Say("apres_tir");
            if (t == 1410 && !live) Console.Printf("RF_DEV_UI_DONE");
            player.cmd.buttons = b;
        }
        Super.PlayerThink();
    }
}

'''


def probe_pk3(path, player_class):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('ZSCRIPT.probe', PROBE)
        z.writestr('MAPINFO.probe', 'gameinfo\n{\n    PlayerClasses = "%s"\n    AddEventHandlers = "RFBenchProbeCount"\n}\n' % player_class)


def run(base, module, probe, name, seconds, loadgame=None):
    cmd = [sys.executable, str(ROOT / 'scripts' / 'devrun.py'), '--pk3', str(base), '--map', 'ARSENAL', '--name', name,
           '--seconds', str(seconds), '--marker', 'RF_DEV_UI_DONE', '--grep', 'RF_BENCH|RF_PROBE|rror|nknown|issing']
    if loadgame:
        cmd += ['--loadgame', loadgame]
    cmd += ['--', '-file', str(module), str(probe)]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return (ROOT / 'build' / 'dev' / 'logs' / f'{name}.txt').read_text(encoding='utf-8', errors='replace').splitlines()


def kv(line):
    return dict(re.findall(r'(\w+)=(-?\w[\w.\-]*)', line))


def evaluate(lines, reload_lines):
    bench = [l for l in lines if l.startswith('RF_BENCH ')]
    probe = [l for l in lines if l.startswith('RF_PROBE ')]
    fails, notes = [], []
    caps = {'RFBenchRapid': None, 'RFBenchMR73': 6}
    for l in bench + probe:
        d = kv(l)
        if 'ERREUR' in l:
            fails.append('ERREUR : ' + l)
        if d.get('ecart', '0') != '0':
            fails.append('compte non conserve : ' + l)
        for k in ('charge', 'reserve'):
            if k in d and int(d[k]) < 0:
                fails.append(f'{k} negatif : ' + l)
    # shots against impacts: each shot line is followed by exactly its pellets' puffs by the next probe line
    pellets = {'RFBenchRapid': 8, 'RFBenchMR73': 1}
    shots = {c: sum(1 for l in bench if f'arme={c} shot' in l) for c in pellets}
    last = kv([l for l in probe if 'sauvegarde' in l][0])
    expected_puffs = sum(shots[c] * pellets[c] for c in pellets)
    # Browning/FAL are not fired; puffs come only from the bench weapons
    if int(last['puffs']) != expected_puffs:
        fails.append(f"impacts {last['puffs']} pour {shots} tirs (attendu {expected_puffs})")
    notes.append(f'tirs {shots}, impacts {last["puffs"]}')
    # dry fire gives no shot
    for c, tag in (('RFBenchRapid', 'W03_apres_tir_a_vide'), ('RFBenchMR73', 'W04_apres_tir_a_vide')):
        before = kv([l for l in probe if tag.replace('tir_a_vide', '6_tirs') in l][0])
        after = kv([l for l in probe if tag in l][0])
        if before['tirs'] != after['tirs'] or before['puffs'] != after['puffs']:
            fails.append(f'tir a vide {c} : {before} -> {after}')
        if not any(f'arme={c} dry' in l for l in bench):
            fails.append(f'{c} : pas de clic a vide')
    # fire during a reload: a shot before any further round goes in
    for c, ev in (('RFBenchRapid', 'shell_in'), ('RFBenchMR73', 'round_in')):
        seq = [l for l in bench if f'arme={c} ' in l]
        idx = [i for i, l in enumerate(seq) if 'tir_demande_pendant_la_recharge' in l]
        if not idx:
            fails.append(f'{c} : demande de tir pendant la recharge non vue')
            continue
        after = seq[idx[0] + 1:]
        first_shot = next((i for i, l in enumerate(after) if ' shot ' in l + ' '), None)
        rounds = [i for i, l in enumerate(after) if f' {ev}' in l and 'sans_cartouche' not in l]
        if first_shot is None:
            fails.append(f'{c} : aucun tir apres la demande pendant la recharge')
        else:
            extra = [i for i in rounds if i < first_shot]
            if len(extra) > 1:
                fails.append(f'{c} : {len(extra)} cartouches introduites apres la demande de tir (1 au plus : celle en cours)')
            notes.append(f'{c} : tir {first_shot + 1} evenement(s) apres la demande, {len(extra)} cartouche en cours finie')
    # switch during a reload: no shell afterwards
    sw = next(i for i, l in enumerate(lines) if 'W03_changement_pendant_recharge' in l)
    later = [l for l in lines[sw:] if l.startswith('RF_BENCH') and 'arme=RFBenchRapid shell_in' in l]
    if later:
        fails.append('W03 : cartouche introduite apres le changement d\'arme : ' + later[0])
    # empty reserve starts no reload
    a = kv([l for l in probe if 'W04_apres_recharge_reserve_courte' in l][0])
    b = kv([l for l in probe if 'W04_apres_recharge_reserve_vide' in l][0])
    if a['charge'] != b['charge'] or b['reserve'] != '0':
        fails.append(f'reserve vide : {a} -> {b}')
    notes.append(f"reserve courte : charge {a['charge']} reserve {a['reserve']}")
    # capacity
    for l in probe:
        d = kv(l)
        if d.get('arme', '').startswith('RFBenchMR73') and int(d.get('charge', 0)) > 6:
            fails.append('plus de six cartouches : ' + l)
    # save / load
    saved = kv([l for l in probe if 'sauvegarde' in l][0])
    loaded = [kv(l) for l in reload_lines if l.startswith('RF_PROBE') and 'apres_chargement' in l]
    fired = [kv(l) for l in reload_lines if l.startswith('RF_PROBE') and 'apres_tir' in l]
    if not loaded or not fired:
        fails.append('rechargement de la sauvegarde : lignes absentes')
    else:
        same = all(loaded[0].get(k) == saved.get(k) for k in ('arme', 'charge', 'reserve', 'tirs', 'ecart'))
        if not same:
            fails.append(f'sauvegarde {saved} / chargement {loaded[0]}')
        if int(fired[0]['tirs']) != int(saved['tirs']) + 1 or fired[0]['ecart'] != '0':
            fails.append(f'tir apres chargement : {fired[0]}')
        notes.append(f"sauvegarde/chargement : {loaded[0]['arme']} charge {loaded[0]['charge']} reserve {loaded[0]['reserve']} "
                     f"tirs {loaded[0]['tirs']} ; apres un tir : tirs {fired[0]['tirs']}, ecart {fired[0]['ecart']}")
    if not any('banc=ARSENAL sauvegarde=1' in l for l in reload_lines):
        notes.append('WorldLoaded du banc non journalise au chargement')
    return fails, notes, probe


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out', help='write the report (JSON) here')
    a = ap.parse_args()
    work = ROOT / 'build' / 'arsenal'
    work.mkdir(parents=True, exist_ok=True)
    p1 = work / 'probe_run.pk3'
    probe_pk3(p1, 'RFBenchProbe')
    lines = run(a.base, a.module, p1, 'bench_probe', 120)
    reload_lines = run(a.base, a.module, p1, 'bench_probe_reload', 60, loadgame='latest')
    fails, notes, probe = evaluate(lines, reload_lines)
    for l in probe:
        print(l)
    for n in notes:
        print('note:', n)
    print('RESULTAT :', 'PASS' if not fails else 'FAIL')
    for f in fails:
        print('  -', f)
    if a.out:
        Path(a.out).write_bytes(json.dumps(dict(created=time.strftime('%Y-%m-%d %H:%M'), base=a.base, module=a.module,
                                                result='PASS' if not fails else 'FAIL', failures=fails, notes=notes,
                                                probe=probe, bench=[l for l in lines if l.startswith('RF_BENCH')],
                                                reload=[l for l in reload_lines if l.startswith(('RF_BENCH', 'RF_PROBE'))]),
                                           indent=2, ensure_ascii=False).encode('utf-8'))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
