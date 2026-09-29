#!/usr/bin/env python3
"""Scripted checks of the next weapons' mechanics on the bench (W05 FAMAS, W09 Scorpion, W10 crowbar).

    python scripts/arsenal/next_probe.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3 [--out report.json]

FAMAS: one press in single shot fires 1, one press in burst fires 3, fire held 30 tics in automatic fires and stops
on release; a partial reload keeps the rounds; a switch asked before the seating frame puts no round in; dry fire.
Scorpion: in front of the open target, held 40 tics: contacts and damage; in front of the pillar with a target
just behind it: no damage to that target; the loop sound (weapon channel) is off after release, after stowing and
after death. Crowbar: a blow in front of the open target hits, in front of the pillar hits the obstacle only, towards
the empty lane misses. Rounds conserved everywhere. Counters and logs only: no judgement of look or sound.
"""
import argparse, json, re, subprocess, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PROBE = r'''version "4.14"
class RFNextProbe : RFPlayer
{
    int t, step, wait, presses, base0, hold, t0;
    bool dead;

    bool IdleW(Weapon w)
    {
        if (w == null || player.ReadyWeapon != w || player.PendingWeapon != WP_NOCHANGE) return false;
        let psp = player.FindPSprite(PSP_WEAPON);
        if (psp == null || psp.y > 32.01 || psp.CurState != w.FindState("Ready")) return false;
        let bw = RFBenchWeapon(w);
        return bw == null || (!bw.Reloading && bw.SeqName == "ready");
    }
    bool Idle(Name cls) { return IdleW(Weapon(FindInventory(cls))); }
    void Take(Name cls) { player.PendingWeapon = Weapon(FindInventory(cls)); }
    void Place(Vector2 at, double ang) { SetOrigin((at, 0), false); angle = ang; pitch = 0; Vel = (0, 0, 0); }
    void Say(String what)
    {
        let w = RFBenchWeapon(player.ReadyWeapon);
        String cur = w ? String.Format("%s charge=%d reserve=%d tirs=%d ecart=%d", w.GetClassName(), w.Loaded(), w.Reserve(), w.Shots, w.Balance()) : "-";
        Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_NPROBE t=%d %s boucle=%d arme=%s", Level.maptime, what, IsActorPlayingSound(CHAN_WEAPON), cur);
    }

    int Advance()
    {
        let fm = RFBenchMagazine(FindInventory('RFBenchFamas'));
        let sc = RFBenchSaw(FindInventory('RFBenchScorpion'));
        if (t > 5000 && step < 900) { Say("TIMEOUT"); step = 999; Console.Printf("RF_DEV_UI_DONE"); return 0; }
        switch (step)
        {
        // ---- FAMAS
        case 0: Take('RFBenchFamas'); step++; return 0;
        case 1: if (!Idle('RFBenchFamas')) return 0; Say("W05_depart"); base0 = fm.Shots; step++; wait = 2; return BT_ATTACK;
        case 2: if (!Idle('RFBenchFamas')) return 0; Say(String.Format("W05_coup_par_coup tirs=%d", fm.Shots - base0)); step++; wait = 2; return BT_ALTATTACK;
        case 3: if (!Idle('RFBenchFamas')) return 0; Say("W05_mode_rafale"); base0 = fm.Shots; step++; wait = 2; return BT_ATTACK;
        case 4: if (!Idle('RFBenchFamas')) return 0; Say(String.Format("W05_rafale tirs=%d", fm.Shots - base0)); step++; wait = 2; return BT_ALTATTACK;
        case 5: if (!Idle('RFBenchFamas')) return 0; Say("W05_mode_auto"); base0 = fm.Shots; hold = 0; step++; return 0;
        case 6: if (hold++ < 30) return BT_ATTACK; step++; return 0;
        case 7: if (!Idle('RFBenchFamas')) return 0; Say(String.Format("W05_auto_30_tics tirs=%d", fm.Shots - base0)); step++; wait = 2; return BT_RELOAD;
        case 8: if (!Idle('RFBenchFamas')) return 0; Say("W05_apres_recharge_partielle"); step++; return 0;
        case 9:  // a switch asked before the seating frame: nothing goes in
            if (!Idle('RFBenchFamas')) return 0;
            if (fm.Mag >= fm.MagCap() - 1) { hold = 0; step = 90; return 0; }
            base0 = fm.Commits; t0 = t; step++; wait = 2; return BT_RELOAD;
        case 10: if (t < t0 + 12) return 0; Take('RFBrowning'); Say("W05_changement_avant_engagement"); step++; return 0;
        case 11: if (!Idle('RFBrowning')) return 0; Say(String.Format("W05_apres_changement engagements=%d", fm.Commits - base0)); Take('RFBenchFamas'); step++; return 0;
        case 12: if (!Idle('RFBenchFamas')) return 0; if (fm.Mag > 0) { wait = 1; return BT_ATTACK; } step++; return 0;
        case 13: if (!Idle('RFBenchFamas')) return 0; Say("W05_vide"); base0 = fm.Shots; step++; wait = 8; return BT_ATTACK;
        case 14: if (!Idle('RFBenchFamas')) return 0; Say(String.Format("W05_tir_a_vide tirs=%d", fm.Shots - base0)); step = 20; return 0;
        case 90: if (hold++ < 3) return BT_ATTACK; step = 9; return 0;     // make room in the magazine first
        // ---- Scorpion
        case 20: Place((-40, 490), 90); Take('RFBenchScorpion'); step++; return 0;
        case 21: if (!Idle('RFBenchScorpion')) return 0; Say("W09_devant_cible"); hold = 0; step++; return 0;
        case 22: if (hold++ < 40) return BT_ATTACK; step++; wait = 20; return 0;
        case 23: Say(String.Format("W09_relachee touches=%d obstacle=%d", sc.Hits, sc.WallHits)); step++; return 0;
        case 24: if (!Idle('RFBenchScorpion')) return 0; Place((-120, 490), 90); base0 = sc.Hits; hold = 0; wait = 5; step++; return 0;
        case 25: if (hold++ < 40) return BT_ATTACK; step++; wait = 20; return 0;
        case 26: Say(String.Format("W09_devant_pilier touches=%d obstacle=%d", sc.Hits - base0, sc.WallHits)); step++; return 0;
        case 27: if (!Idle('RFBenchScorpion')) return 0; hold = 0; step++; return 0;
        case 28: if (hold++ < 15) return BT_ATTACK; Take('RFBrowning'); Say("W09_rangement_en_marche"); step++; return BT_ATTACK;
        case 29: if (!Idle('RFBrowning')) return 0; Say("W09_apres_rangement"); Take('RFBenchScorpion'); step++; return 0;
        // ---- crowbar (before the death test)
        case 30: if (!Idle('RFBenchScorpion')) return 0; Take('RFBenchCrowbar'); Place((-40, 490), 90); step++; return 0;
        case 31: if (!Idle('RFBenchCrowbar')) return 0; Say("W10_devant_cible"); step++; wait = 2; return BT_ATTACK;
        case 32: if (!Idle('RFBenchCrowbar')) return 0; Place((-120, 490), 90); wait = 4; Say("W10_devant_pilier"); step++; return 0;
        case 33: step++; wait = 2; return BT_ATTACK;
        case 34: if (!Idle('RFBenchCrowbar')) return 0; Place((-8, 128), 0); wait = 4; Say("W10_vers_le_couloir"); step++; return 0;
        case 35: step++; wait = 2; return BT_ATTACK;
        case 36: if (!Idle('RFBenchCrowbar')) return 0; Say("W10_fin"); Take('RFBenchScorpion'); Place((-40, 300), 90); step++; return 0;
        // ---- saw running at death
        case 37: if (!Idle('RFBenchScorpion')) return 0; hold = 0; step++; return 0;
        case 38:
            if (hold++ < 15) return BT_ATTACK;
            Say("W09_mort_en_marche"); dead = true; player.cheats &= ~CF_GODMODE;
            DamageMobj(null, null, 1000, 'None', DMG_FORCED); t0 = t; step++; return BT_ATTACK;
        case 39: if (t < t0 + 40) return 0; Say("W09_apres_mort"); step = 999; Console.Printf("RF_DEV_UI_DONE"); return 0;
        }
        return 0;
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            if (!dead) player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            Vel.XY = (0, 0);
            int b = 0;
            if (wait > 0) wait--;
            else if (step < 999) b = Advance();
            player.cmd.buttons = b;
        }
        Super.PlayerThink();
    }
}
'''


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


def evaluate(lines):
    fails, notes = [], []
    probe = [l for l in lines if l.startswith('RF_NPROBE')]
    bench = [l for l in lines if l.startswith('RF_BENCH')]
    def get(tag):
        """The probe's own values (before ' boucle='), then the loop flag: the weapon part repeats some keys (tirs)."""
        line = next((l for l in probe if f' {tag} ' in l + ' '), None)
        if line is None:
            return None
        head, _, tail = line.partition(' boucle=')
        d = kv(head)
        d['boucle'] = tail.split()[0] if tail else None
        return d
    if any('TIMEOUT' in l for l in probe):
        fails.append('sonde bloquee')
    for l in bench + probe:
        if 'ERREUR' in l:
            fails.append('ERREUR : ' + l)
        if kv(l).get('ecart', '0') != '0':
            fails.append('compte non conserve : ' + l)
    c = get('W05_coup_par_coup'); r = get('W05_rafale'); a = get('W05_auto_30_tics'); v = get('W05_tir_a_vide'); s = get('W05_apres_changement')
    if not (c and r and a and v and s):
        fails.append('FAMAS : etapes absentes')
    else:
        if c['tirs'] != '1': fails.append(f"coup par coup : {c['tirs']} tirs")
        if r['tirs'] != '3': fails.append(f"rafale : {r['tirs']} tirs")
        if not (5 <= int(a['tirs']) <= 12): fails.append(f"automatique 30 tics : {a['tirs']} tirs")
        if v['tirs'] != '0': fails.append(f"tir a vide : {v['tirs']} tirs")
        if s['engagements'] != '0': fails.append(f"changement avant engagement : {s['engagements']} chargeur engage")
        notes.append(f"FAMAS : coup par coup {c['tirs']}, rafale {r['tirs']}, automatique 30 tics {a['tirs']}, "
                     f"changement avant engagement {s['engagements']}, vide {v['tirs']}")
    op, pil = get('W09_relachee'), get('W09_devant_pilier')
    hurt_open = [l for l in bench if 'impact cible=71u' in l and 'RFBenchScorpion' in l]
    hurt_behind = [l for l in bench if 'impact cible=70u' in l and 'RFBenchScorpion' in l]
    if not op or not pil:
        fails.append('scie : etapes absentes')
    else:
        if int(op['touches']) == 0 or not hurt_open: fails.append('scie : aucun contact devant la cible')
        if int(pil['touches']) != 0 or hurt_behind: fails.append('scie : degats a travers le pilier')
        if op['boucle'] != '0': fails.append('scie : boucle encore active apres relachement')
        notes.append(f"scie : devant la cible {op['touches']} touches ; devant le pilier {pil['touches']} touches, "
                     f"{pil['obstacle']} contacts obstacle, cible derriere {len(hurt_behind)} impact")
    for tag, why in (('W09_apres_rangement', 'rangement'), ('W09_apres_mort', 'mort')):
        x = get(tag)
        if not x or x.get('boucle') != '0':
            fails.append(f'scie : boucle encore active apres {why} ({x})')
    if not any('scie_arret rangement' in l for l in bench): fails.append('scie : arret au rangement non journalise')
    if not any('scie_arret mort' in l for l in bench): fails.append('scie : arret a la mort non journalise')
    hits = [l for l in bench if 'coup_touche' in l]
    walls = [l for l in bench if 'coup_obstacle' in l]
    misses = [l for l in bench if 'coup_rate' in l]
    behind = [l for l in bench if 'impact cible=70u' in l and 'RFBenchCrowbar' in l]
    if len(hits) != 1 or len(walls) != 1 or len(misses) != 1 or behind:
        fails.append(f'pied-de-biche : touche {len(hits)}, obstacle {len(walls)}, rate {len(misses)}, derriere le pilier {len(behind)}')
    notes.append(f'pied-de-biche : touche {len(hits)}, obstacle {len(walls)}, rate {len(misses)}, cible derriere le pilier {len(behind)} impact')
    return fails, notes, probe


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out')
    a = ap.parse_args()
    probe = ROOT / 'build' / 'arsenal' / 'next_probe.pk3'
    probe.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(probe, 'w') as z:
        z.writestr('ZSCRIPT.nprobe', PROBE)
        z.writestr('MAPINFO.nprobe', 'gameinfo\n{\n    PlayerClasses = "RFNextProbe"\n}\n')
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'devrun.py'), '--pk3', a.base, '--map', 'ARSENAL', '--name', 'next_probe',
                    '--seconds', '200', '--marker', 'RF_DEV_UI_DONE', '--', '-file', a.module, str(probe)], cwd=ROOT, capture_output=True, text=True)
    lines = (ROOT / 'build' / 'dev' / 'logs' / 'next_probe.txt').read_text(encoding='utf-8', errors='replace').splitlines()
    fails, notes, probe_lines = evaluate(lines)
    for l in probe_lines:
        print(l)
    for n in notes:
        print('note:', n)
    print('RESULTAT :', 'PASS' if not fails else 'FAIL')
    for f in fails:
        print('  -', f)
    if a.out:
        Path(a.out).write_bytes(json.dumps(dict(created=time.strftime('%Y-%m-%d %H:%M'), module=a.module, base=a.base,
                                                result='PASS' if not fails else 'FAIL', failures=fails, notes=notes,
                                                log=[l for l in lines if l.startswith(('RF_NPROBE', 'RF_BENCH'))]),
                                           indent=2, ensure_ascii=False).encode('utf-8'))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
