#!/usr/bin/env python3
"""Scripted checks of the arsenal test bench in the engine: counters, transitions and layers, read from the log.

    python scripts/arsenal/bench_probe.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3 [--out report.json]

A probe player (a third file, for this run only) plays step by step, each step waiting for the weapon to be really
ready, so the animation's durations can change without breaking it:
  W03 and W04 in turn: emptied, dry fire, full reload, topping or partial reload (MR73 rule a), fire during a
  reload; then a control reload measures when the first round goes in, and five trials ask for another weapon 2 and
  1 tics before, on, 1 and 2 tics after that commit point; MR73 short reserve (2) then empty reserve; a save in the
  middle of an MR73 insertion (hand and chambers on screen), and a second run that loads it, lets the reload finish,
  then dies in the middle of another insertion.
The checks are the contract's rules (RF2-ARSENAL 3 and 4), not a copy of the bench's code:
  - rounds are conserved at every logged event ("ecart" 0); no negative count, nothing above capacity; no ERREUR;
  - each shot gives exactly its pellets' impacts (bullet puffs counted by the probe); a dry fire gives none;
  - fire pressed during a reload: a shot comes before any further round goes in (the round in progress may finish);
  - switch asked during a reload: no round goes in on or after the tic of the request (a round committed before it
    finishes), the other weapon comes up, the revolver's layers are gone;
  - an empty reserve starts no reload; a short one loads what there is;
  - a save during an insertion is loaded with the same counts, sequence and layers, and the reload then finishes
    with the rounds conserved;
  - death during an insertion: nothing goes in or is fired afterwards, the layers are removed.
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
    int t, step, wait, presses, trial, t0, commitDelay, reqTic, baseCommits, saveTic;
    bool dead;
    transient bool live;     // not saved: false once the probe's own save has been loaded

    int Offset(int n) { return n - 2; }                 // trials: -2, -1, 0, +1, +2 tics around the commit
    RFBenchWeapon W(Name cls) { return RFBenchWeapon(FindInventory(cls)); }

    bool IdleW(Weapon w)
    {
        if (w == null || player.ReadyWeapon != w || player.PendingWeapon != WP_NOCHANGE) return false;
        let psp = player.FindPSprite(PSP_WEAPON);
        if (psp == null || psp.y > 32.01 || psp.CurState != w.FindState("Ready")) return false;
        let bw = RFBenchWeapon(w);
        return bw == null || (!bw.Reloading && bw.SeqName == "ready");
    }
    bool Idle(Name cls) { return IdleW(Weapon(FindInventory(cls))); }

    String Rig()
    {
        String s = "";
        let w = RFBenchRevolver(FindInventory('RFBenchMR73'));
        for (int layer = 101; layer <= 107; layer++)
        {
            let psp = player.FindPSprite(layer);
            if (psp == null) continue;
            String lab = "?";
            for (int k = 0; k <= 2 && w != null; k++)
                for (int i = 1; i <= 6; i++)
                    for (int j = 1; j <= 7; j++)
                        if (lab == "?" && psp.CurState == w.RigState(k, i, j)) lab = String.Format("%d.%d.%d", k, i, j);
            s = s .. String.Format("%d:%s,", layer, lab);
        }
        return s == "" ? "aucun" : s;
    }

    void Say(String what)
    {
        let h = RFBenchProbeCount(EventHandler.Find('RFBenchProbeCount'));
        String cur = "";
        let w = RFBenchWeapon(player.ReadyWeapon);
        if (w != null) cur = String.Format("%s charge=%d reserve=%d tirs=%d ecart=%d seq=%s", w.GetClassName(), w.Loaded(), w.Reserve(), w.Shots, w.Balance(), w.SeqName);
        else if (player.ReadyWeapon != null) cur = String.Format("%s", player.ReadyWeapon.GetClassName());
        // t = Level.maptime, the clock of the bench's own lines; pt = the probe's count of its thinks
        Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_PROBE t=%d pt=%d %s puffs=%d calques=%s arme=%s", Level.maptime, t, what, h ? h.puffs : -1, Rig(), cur);
    }

    void Adjust(Name weapon, Class<Inventory> ammo, int delta)
    {
        let w = W(weapon);
        if (delta > 0) GiveInventory(ammo, delta);
        else if (delta < 0) TakeInventory(ammo, -delta, true);
        if (w != null) w.Baseline += delta;     // moved by the probe, not by the weapon
    }

    // Switch-timing trials for one weapon: steps s .. s+4. Returns the buttons of the tic.
    int Trials(int s, Name cls, String tag, int nextStep)
    {
        let w = W(cls);
        switch (step - s)
        {
        case 0:     // room for at least two rounds, then the control reload or a trial
            if (!Idle(cls)) return 0;
            if (w.Capacity() - w.Loaded() < 2) { wait = 2; return BT_ATTACK; }
            if (w.Reserve() < 8) Adjust(cls, w.AmmoType1, 12);
            t0 = t; baseCommits = w.Commits;
            reqTic = trial > 0 ? t0 + commitDelay + Offset(trial - 1) : -1;
            step++;
            return BT_RELOAD;
        case 1:
            if (trial == 0)
            {
                if (w.Commits > baseCommits) { commitDelay = (t - 1) - t0; Say(String.Format("%s_temoin delai_engagement=%d", tag, commitDelay)); step = s + 3; }
                return 0;
            }
            if (t == reqTic)
            {
                player.PendingWeapon = Weapon(FindInventory('RFBrowning'));
                Say(String.Format("%s_essai off=%d demande", tag, Offset(trial - 1)));
                step++;
            }
            return 0;
        case 2:
            if (!Idle('RFBrowning')) return 0;
            Say(String.Format("%s_essai_fin off=%d", tag, Offset(trial - 1)));
            player.PendingWeapon = Weapon(FindInventory(cls));
            step++;
            return 0;
        case 3:
            if (!Idle(cls)) return 0;
            trial++;
            step = trial <= 5 ? s : nextStep;
            if (trial > 5) trial = 0;
            return 0;
        }
        return 0;
    }

    int Advance()
    {
        let rp = W('RFBenchRapid');
        let mr = RFBenchRevolver(FindInventory('RFBenchMR73'));
        if (t > 9000 && step < 900) { Say(String.Format("TIMEOUT etape=%d", step)); step = 999; Console.Printf("RF_DEV_UI_DONE"); return 0; }
        switch (step)
        {
        // ---------------- W03
        case 0: if (!Idle('RFBenchRapid')) return 0; Say("W03_depart"); presses = 0; step++; return 0;
        case 1:
            if (!Idle('RFBenchRapid')) return 0;
            if (presses < rp.Capacity()) { presses++; wait = 2; return BT_ATTACK; }
            Say("W03_apres_tirs"); step++; return 0;
        case 2: if (!Idle('RFBenchRapid')) return 0; step++; wait = 2; return BT_ATTACK;
        case 3: if (!Idle('RFBenchRapid')) return 0; Say("W03_apres_tir_a_vide"); step++; wait = 2; return BT_RELOAD;
        case 4: if (!Idle('RFBenchRapid')) return 0; Say("W03_apres_recharge"); step++; wait = 2; return BT_RELOAD;
        case 5: if (!Idle('RFBenchRapid')) return 0; Say("W03_apres_complement"); presses = 0; step++; return 0;
        case 6:
            if (!Idle('RFBenchRapid')) return 0;
            if (presses < 2) { presses++; wait = 2; return BT_ATTACK; }
            Say("W03_apres_2_tirs"); baseCommits = rp.Commits; step++; wait = 2; return BT_RELOAD;
        case 7: if (rp.Commits <= baseCommits) return 0; Say("W03_tir_pendant_recharge"); step++; return BT_ATTACK;
        case 8: if (!Idle('RFBenchRapid')) return 0; Say("W03_apres_interruption_par_tir"); step = 10; trial = 0; return 0;
        case 10: case 11: case 12: case 13:
            return Trials(10, 'RFBenchRapid', "W03", 20);
        // ---------------- W04
        case 20: player.PendingWeapon = Weapon(FindInventory('RFBenchMR73')); step++; return 0;
        case 21: if (!Idle('RFBenchMR73')) return 0; Say("W04_depart"); presses = 0; step++; return 0;
        case 22:
            if (!Idle('RFBenchMR73')) return 0;
            if (mr.Rounds > 0) { wait = 2; return BT_ATTACK; }
            Say("W04_apres_tirs"); step++; return 0;
        case 23: if (!Idle('RFBenchMR73')) return 0; step++; wait = 2; return BT_ATTACK;
        case 24: if (!Idle('RFBenchMR73')) return 0; Say("W04_apres_tir_a_vide"); step++; wait = 2; return BT_RELOAD;
        case 25: if (!Idle('RFBenchMR73')) return 0; Say("W04_apres_recharge"); presses = 0; step++; return 0;
        case 26:
            if (!Idle('RFBenchMR73')) return 0;
            if (presses < 2) { presses++; wait = 2; return BT_ATTACK; }
            Say("W04_apres_2_tirs"); step++; wait = 2; return BT_RELOAD;
        case 27:
            if (!Idle('RFBenchMR73')) return 0;
            if (mr.Rounds > 1) { wait = 2; return BT_ATTACK; }
            Say("W04_avant_interruption"); baseCommits = mr.Commits; step++; wait = 2; return BT_RELOAD;
        case 28: if (mr.Commits <= baseCommits) return 0; Say("W04_tir_pendant_recharge"); step++; return BT_ATTACK;
        case 29: if (!Idle('RFBenchMR73')) return 0; Say("W04_apres_interruption_par_tir"); step = 30; trial = 0; return 0;
        case 30: case 31: case 32: case 33:
            return Trials(30, 'RFBenchMR73', "W04", 40);
        // short reserve, then empty reserve
        case 40:
            if (!Idle('RFBenchMR73')) return 0;
            if (mr.Rounds > 0) { wait = 2; return BT_ATTACK; }
            Adjust('RFBenchMR73', 'RFBenchMagnum', 2 - mr.Reserve());
            Say("W04_reserve_ramenee_a_2"); step++; wait = 2; return BT_RELOAD;
        case 41: if (!Idle('RFBenchMR73')) return 0; Say("W04_apres_recharge_reserve_courte"); presses = 0; step++; wait = 2; return BT_RELOAD;
        case 42: if (wait == 0 && presses < 30) { presses++; return 0; } presses = 0; step++; return 0;
        case 43: if (!Idle('RFBenchMR73')) return 0; Say("W04_apres_recharge_reserve_vide"); Adjust('RFBenchMR73', 'RFBenchMagnum', 18); step++; return 0;
        // a save in the middle of an insertion
        case 44:
            if (!Idle('RFBenchMR73')) return 0;
            if (mr.Rounds > 0) { wait = 2; return BT_ATTACK; }
            baseCommits = mr.Commits; step++; wait = 2; return BT_RELOAD;
        case 45:
            if (mr.Commits >= baseCommits + 2 && mr.RigStage >= 1 && mr.RigStage <= 4)
            {
                Say("sauvegarde_pendant_insertion"); saveTic = t; Level.MakeAutoSave(); step++;
            }
            return 0;
        case 46:
            if (live)
            {
                if (t == saveTic + 1) Say("etat_sauvegarde");
                if (t == saveTic + 40) { Say("fin_premiere_partie"); Console.Printf("RF_DEV_UI_DONE"); step = 999; }
                return 0;
            }
            Say("apres_chargement"); step++; return 0;
        case 47: if (!Idle('RFBenchMR73')) return 0; Say("apres_chargement_recharge_finie"); step++; return 0;
        // death in the middle of an insertion
        case 48:
            if (!Idle('RFBenchMR73')) return 0;
            if (mr.Rounds > 3) { wait = 2; return BT_ATTACK; }
            baseCommits = mr.Commits; step++; wait = 2; return BT_RELOAD;
        case 49:
            if (mr.Commits >= baseCommits + 1 && mr.RigStage >= 1 && mr.RigStage <= 4)
            {
                Say("mort_pendant_insertion"); dead = true; player.cheats &= ~CF_GODMODE;
                DamageMobj(null, null, 1000, 'None', DMG_FORCED); t0 = t; step++;
            }
            return 0;
        case 50: if (t < t0 + 50) return 0; Say("apres_mort"); Console.Printf("RF_DEV_UI_DONE"); step = 999; return 0;
        }
        return 0;
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            if (t == 1) live = true;
            if (!dead) player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            int b = 0;
            if (wait > 0) wait--;
            else if (step < 999) b = Advance();
            player.cmd.buttons = b;
        }
        Super.PlayerThink();
    }
}
'''


def probe_pk3(path):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('ZSCRIPT.probe', PROBE)
        z.writestr('MAPINFO.probe', 'gameinfo\n{\n    PlayerClasses = "RFBenchProbe"\n    AddEventHandlers = "RFBenchProbeCount"\n}\n')


def run(base, module, probe, name, seconds, loadgame=None):
    cmd = [sys.executable, str(ROOT / 'scripts' / 'devrun.py'), '--pk3', str(base), '--map', 'ARSENAL', '--name', name,
           '--seconds', str(seconds), '--marker', 'RF_DEV_UI_DONE', '--grep', 'RF_BENCH|RF_PROBE|rror|nknown|issing']
    if loadgame:
        cmd += ['--loadgame', loadgame]
    cmd += ['--', '-file', str(module), str(probe)]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return (ROOT / 'build' / 'dev' / 'logs' / f'{name}.txt').read_text(encoding='utf-8', errors='replace').splitlines()


def kv(line):
    return dict(re.findall(r'(\w+)=(-?[\w.,:\-]+)', line))


def tic(line):
    m = re.search(r' t=(\d+)', line)
    return int(m.group(1)) if m else -1


def one(lines, tag):
    hit = [l for l in lines if l.startswith('RF_PROBE') and f' {tag} ' in l + ' ']
    return hit[0] if hit else None


def evaluate(lines, reload_lines):
    fails, notes = [], []
    bench = [l for l in lines if l.startswith('RF_BENCH ')]
    probe = [l for l in lines if l.startswith('RF_PROBE ')]
    bench2 = [l for l in reload_lines if l.startswith('RF_BENCH ')]
    probe2 = [l for l in reload_lines if l.startswith('RF_PROBE ')]
    if any('TIMEOUT' in l for l in probe + probe2):
        fails.append('sonde bloquee : ' + next(l for l in probe + probe2 if 'TIMEOUT' in l))
    for l in bench + probe + bench2 + probe2:
        d = kv(l)
        if 'ERREUR' in l:
            fails.append('ERREUR : ' + l)
        if d.get('ecart', '0') != '0':
            fails.append('compte non conserve : ' + l)
        for k in ('charge', 'reserve'):
            if k in d and int(d[k]) < 0:
                fails.append(f'{k} negatif : ' + l)
        if d.get('arme', '').startswith('RFBenchMR73') and int(d.get('charge', 0)) > 6:
            fails.append('plus de six cartouches : ' + l)
        if d.get('arme', '').startswith('RFBenchRapid') and int(d.get('charge', 0)) > 5:
            fails.append('plus de 4+1 cartouches : ' + l)
    # impacts: pellets x shots, over the first run
    pellets = {'RFBenchRapid': 8, 'RFBenchMR73': 1}
    shots = {c: sum(1 for l in bench if f'arme={c} shot ' in l + ' ') for c in pellets}
    last = kv(probe[-1]) if probe else {}
    expected = sum(shots[c] * pellets[c] for c in pellets)
    if int(last.get('puffs', -1)) != expected:
        fails.append(f"impacts {last.get('puffs')} pour {shots} tirs (attendu {expected})")
    notes.append(f"tirs {shots}, impacts {last.get('puffs')} (attendu {expected})")
    # dry fire
    for w, c in (('W03', 'RFBenchRapid'), ('W04', 'RFBenchMR73')):
        a, b = one(probe, f'{w}_apres_tirs'), one(probe, f'{w}_apres_tir_a_vide')
        if not a or not b:
            fails.append(f'{w} : lignes de tir a vide absentes')
            continue
        a, b = kv(a), kv(b)
        if (a['tirs'], a['puffs']) != (b['tirs'], b['puffs']):
            fails.append(f'{w} tir a vide : {a} -> {b}')
        if not any(f'arme={c} dry' in l for l in bench):
            fails.append(f'{c} : pas de clic a vide')
        notes.append(f"{w} : {a['tirs']} tirs pour une arme pleine, puis clic a vide")
    # fire during a reload
    for c, ev in (('RFBenchRapid', 'shell_in'), ('RFBenchMR73', 'round_in')):
        seq = [l for l in bench if f'arme={c} ' in l]
        idx = [i for i, l in enumerate(seq) if 'tir_demande_pendant_la_recharge' in l]
        if not idx:
            fails.append(f'{c} : demande de tir pendant la recharge non vue')
            continue
        after = seq[idx[0] + 1:]
        first_shot = next((i for i, l in enumerate(after) if ' shot ' in l + ' '), None)
        rounds = [i for i, l in enumerate(after) if f' {ev} ' in l + ' ' and 'sans_cartouche' not in l]
        if first_shot is None:
            fails.append(f'{c} : aucun tir apres la demande pendant la recharge')
        elif len([i for i in rounds if i < first_shot]) > 1:
            fails.append(f'{c} : plus d\'une cartouche introduite entre la demande de tir et le tir')
    # switch trials
    for w, c, ev in (('W03', 'RFBenchRapid', 'shell_in'), ('W04', 'RFBenchMR73', 'round_in')):
        ctrl = one(probe, f'{w}_temoin')
        if not ctrl:
            fails.append(f'{w} : essai temoin absent')
            continue
        notes.append(f"{w} : premier engagement {kv(ctrl)['delai_engagement']} tics apres la demande de recharge")
        seen = []
        for off in (-2, -1, 0, 1, 2):
            req = next((l for l in probe if f'{w}_essai off={off} demande' in l), None)
            end = next((l for l in probe if f'{w}_essai_fin off={off}' in l), None)
            if not req or not end:
                fails.append(f'{w} essai {off:+d} : non termine')
                continue
            r, e = tic(req), tic(end)
            window = [l for l in bench if f'arme={c} ' in l and r <= tic(l) <= e]
            late = [l for l in window if f' {ev} ' in l + ' ' and 'annule' not in l and 'sans_cartouche' not in l]
            cancelled = [l for l in window if f'{ev}_annule' in l]
            before = [l for l in bench if f'arme={c} ' in l and f' {ev} ' in l + ' ' and 'annule' not in l and r - 30 <= tic(l) < r]
            if late:
                fails.append(f'{w} essai {off:+d} : cartouche engagee apres la demande de changement (t={r}) : {late[0]}')
            if kv(end).get('calques', 'aucun') != 'aucun':
                fails.append(f'{w} essai {off:+d} : calques encore presents apres le rangement : {end}')
            seen.append(f"{off:+d}: {'annulee' if cancelled else ('finie avant' if before else 'aucune')}")
        notes.append(f'{w} changement pendant la recharge : ' + ', '.join(seen))
    # short and empty reserve
    a, b = one(probe, 'W04_apres_recharge_reserve_courte'), one(probe, 'W04_apres_recharge_reserve_vide')
    if not a or not b:
        fails.append('reserve courte/vide : lignes absentes')
    else:
        a, b = kv(a), kv(b)
        if (a['charge'], a['reserve']) != ('2', '0'):
            fails.append(f'reserve courte : {a}')
        rv = one(probe, 'W04_apres_recharge_reserve_courte')
        if any('arme=RFBenchMR73 recharge_debut' in l and tic(rv) < tic(l) < tic(one(probe, 'W04_apres_recharge_reserve_vide')) for l in bench):
            fails.append('reserve vide : une recharge a commence')
        notes.append(f"reserve courte : charge {a['charge']} reserve {a['reserve']} ; reserve vide : aucune recharge")
    # save during an insertion, load
    saved = one(probe, 'etat_sauvegarde')
    loaded = one(probe2, 'apres_chargement')
    if not saved or not loaded:
        fails.append('sauvegarde pendant insertion : lignes absentes')
    else:
        s, l = kv(saved), kv(loaded)
        keys = ('arme', 'charge', 'reserve', 'tirs', 'seq', 'calques')
        if tic(saved) != tic(loaded) or any(s.get(k) != l.get(k) for k in keys):
            fails.append(f'sauvegarde {dict((k, s.get(k)) for k in keys)} / chargement {dict((k, l.get(k)) for k in keys)}')
        if s.get('calques') == 'aucun':
            fails.append('sauvegarde prise sans calques visibles (le cas a eprouver)')
        notes.append(f"sauvegarde pendant l'insertion (t={tic(saved)}) : calques {s.get('calques')} ; relus a l'identique : {not any(s.get(k) != l.get(k) for k in keys)}")
        fin = one(probe2, 'apres_chargement_recharge_finie')
        if not fin or kv(fin).get('calques') != 'aucun':
            fails.append(f'apres chargement, fin de recharge : {fin}')
    # death during an insertion
    death, after = one(probe2, 'mort_pendant_insertion'), one(probe2, 'apres_mort')
    if not death or not after:
        fails.append('mort pendant insertion : lignes absentes')
    else:
        late = [l for l in bench2 if tic(l) > tic(death) and (' round_in ' in l + ' ' or ' shot ' in l + ' ') and 'annule' not in l and 'sans_cartouche' not in l]
        if late:
            fails.append('apres la mort : ' + late[0])
        if kv(after).get('calques') != 'aucun':
            fails.append('calques encore presents apres la mort : ' + after)
        notes.append(f"mort pendant l'insertion : calques {kv(death).get('calques')} -> {kv(after).get('calques')}, rien apres")
    return fails, notes, probe + probe2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out', help='write the report (JSON) here')
    a = ap.parse_args()
    work = ROOT / 'build' / 'arsenal'
    work.mkdir(parents=True, exist_ok=True)
    p1 = work / 'probe_run.pk3'
    probe_pk3(p1)
    lines = run(a.base, a.module, p1, 'bench_probe', 300)
    reload_lines = run(a.base, a.module, p1, 'bench_probe_reload', 120, loadgame='latest')
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
