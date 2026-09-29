#!/usr/bin/env python3
"""Scripted checks of Viktor's lines at the first acquisition of the Rapid and of the MR73 (addendum of 28/09).

    python scripts/arsenal/voice_probe.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3 [--out report.json]

Run 1, new game on BANCDEC1: a save before anything (A); walk onto the Rapid (line 1 must start once); walk onto a
second Rapid (duplicate: nothing); a priority voice starts, walk onto the MR73 during it (line 0 must wait, then
start once); a pain sound cuts the line (no replay); a save after both lines (B); normal exit to BANCDEC2 and walk
onto a Rapid and an MR73 there (duplicates after a map change: nothing).
Run 2 loads B: no line may play. Run 3 loads A (before the discovery): walking onto the Rapid plays line 1 again.
Run 4, another new game: line 1 plays again (the state belongs to the campaign, not to a profile).
Reads the bench's own log lines (RF_BENCH voix ...). It checks triggers and states; it does not listen: the voices
are placeholders until Astra delivers the takes.
"""
import argparse, json, re, subprocess, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAVES = ROOT / 'build' / 'dev' / 'saves'

PROBE = r'''version "4.14"
class RFVoiceProbe : RFPlayer
{
    int t, step, wait, walkTo, markTic;
    bool hurt;
    transient bool live;

    void Say(String what)
    {
        let tok = RFViktorLines(FindInventory('RFViktorLines'));
        Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_VPROBE t=%d %s carte=%s rapid=%d mr73=%d entendue0=%d entendue1=%d attente0=%d attente1=%d lecture=%d",
            Level.maptime, what, Level.MapName, FindInventory('RFBenchRapid') != null, FindInventory('RFBenchMR73') != null,
            tok ? tok.heard0 : 0, tok ? tok.heard1 : 0, tok ? tok.pending0 : 0, tok ? tok.pending1 : 0, tok ? tok.playing : 0);
    }
    RFViktorLines Tok() { return RFViktorLines(FindInventory('RFViktorLines')); }
    bool Quiet() { let k = Tok(); return k != null && k.playing == 0 && !k.pending0 && !k.pending1; }
    // Walk east along y = 0 until x passes the target (pickups are touched on the way, as in play).
    bool Walk(int x) { if (Pos.X >= x) return true; angle = 0; player.cmd.forwardmove = 6400; return false; }

    void Advance()
    {
        let h = RFBenchHandler(EventHandler.Find('RFBenchHandler'));
        if (t > 4000 && step < 900) { Say("TIMEOUT"); step = 999; Console.Printf("RF_DEV_UI_DONE"); return; }
        switch (step)
        {
        // ---- loaded runs: which save is it?
        case 500:
            if (Tok() != null && Tok().heard0 && Tok().heard1) { Say("charge_apres_repliques"); markTic = t; step = 510; }
            else { Say("charge_avant_decouverte"); step = 520; }
            return;
        case 510: if (t < markTic + 120) return; Say("charge_apres_attente"); step = 999; Console.Printf("RF_DEV_UI_DONE"); return;
        case 520: if (!Walk(160)) return; Say("rechargee_ramassage_rapid"); step++; return;
        case 521: if (!Quiet()) return; Say("rechargee_apres_replique"); step = 999; Console.Printf("RF_DEV_UI_DONE"); return;
        // ---- new game
        case 0: if (t < 10) return; Say("depart"); Level.MakeAutoSave(); wait = 30; step++; return;
        case 1: if (!Walk(160)) return; Say("apres_ramassage_rapid"); step++; return;
        case 2: if (!Quiet()) return; Say("apres_replique_fusil"); step++; return;
        case 3: if (!Walk(290)) return; Say("apres_doublon"); wait = 70; step++; return;
        case 4: Say("apres_doublon_attente"); if (h) h.priorityUntil = Level.maptime + 140; Say("voix_prioritaire_debut"); step++; return;
        case 5: if (!Walk(480)) return; Say("ramassage_mr73_pendant_prioritaire"); step++; return;
        case 6:
            if (Tok() == null || !Tok().heard0) return;
            Say("replique_manurhin_commencee"); wait = 20; step++; return;
        case 7:
            player.cheats &= ~CF_GODMODE; hurt = true;
            DamageMobj(null, null, 5, 'None');         // a pain sound on the voice channel cuts the line
            Say("interruption_douleur"); step++; return;
        case 8: if (!Quiet()) return; wait = 35; step++; return;
        case 9: Say("sauvegarde_apres_repliques"); Level.MakeAutoSave(); wait = 40; step++; return;
        case 10: Say("sortie_carte"); step++; Level.ExitLevel(0, false); return;
        case 11: if (!(Level.MapName ~== "BANCDEC2")) return; Say("carte2_depart"); wait = 10; step++; return;
        case 12: if (!Walk(290)) return; Say("carte2_doublons"); wait = 90; step++; return;
        case 13: Say("carte2_fin"); step = 999; Console.Printf("RF_DEV_UI_DONE"); return;
        }
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            if (t == 1) live = true;
            if (!live && step < 500) step = 500;      // a save was loaded
            if (!hurt) player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            if (wait > 0) wait--;
            else if (step < 999) Advance();
        }
        Super.PlayerThink();
    }
}
'''


def run(base, module, probe, name, loadgame=None):
    cmd = [sys.executable, str(ROOT / 'scripts' / 'devrun.py'), '--pk3', str(base), '--map', 'BANCDEC1', '--name', name,
           '--seconds', '150', '--marker', 'RF_DEV_UI_DONE', '--grep', 'RF_BENCH|RF_VPROBE|rror']
    if loadgame:
        cmd += ['--loadgame', str(loadgame)]
    cmd += ['--', '-file', str(module), str(probe)]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return (ROOT / 'build' / 'dev' / 'logs' / f'{name}.txt').read_text(encoding='utf-8', errors='replace').splitlines()


def tic(line):
    m = re.search(r' t=(\d+)', line)
    return int(m.group(1)) if m else -1


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


def evaluate(r1, r2, r3, r4):
    fails, notes = [], []
    lect = lambda lines, n: [l for l in lines if f'voix lecture ligne={n}' in l]
    p = lambda lines, tag: next((l for l in lines if l.startswith('RF_VPROBE') and f' {tag} ' in l + ' '), None)
    # run 1
    if len(lect(r1, 1)) != 1:
        fails.append(f'partie 1 : ligne du fusil jouee {len(lect(r1, 1))} fois (1 attendue)')
    if len(lect(r1, 0)) != 1:
        fails.append(f'partie 1 : ligne du Manurhin jouee {len(lect(r1, 0))} fois (1 attendue)')
    pick = [l for l in r1 if 'voix ramassage' in l]
    states = [kv(l).get('etat') for l in pick]
    notes.append('partie 1, ramassages : ' + ', '.join(f"{kv(l).get('ramassage')}={kv(l).get('etat')}" for l in pick))
    if states[:2] != ['decouverte', 'doublon']:
        fails.append(f'partie 1 : premier Rapid puis doublon attendus, lu {states[:2]}')
    prio = p(r1, 'voix_prioritaire_debut')
    if prio and lect(r1, 0):
        start = tic(lect(r1, 0)[0])
        if start < tic(prio) + 140:
            fails.append(f'Manurhin commence a t={start} pendant la voix prioritaire (jusqu a t={tic(prio) + 140})')
        notes.append(f'voix prioritaire t={tic(prio)}..{tic(prio) + 140} ; Manurhin commence a t={start}')
    if not p(r1, 'interruption_douleur'):
        fails.append('interruption non jouee')
    exit_at = next((i for i, l in enumerate(r1) if l.startswith('RF_VPROBE') and ' sortie_carte ' in l), len(r1))
    after_exit = r1[exit_at + 1:]                       # map time starts again at 0 on the new map: use the log order
    c2 = [l for l in after_exit if 'voix ramassage' in l]
    if not p(r1, 'carte2_fin'):
        fails.append('changement de carte : partie non terminee')
    else:
        d = kv(p(r1, 'carte2_depart'))
        if d.get('entendue0') != '1' or d.get('entendue1') != '1':
            fails.append(f'etat perdu au changement de carte : {d}')
        if any(kv(l).get('etat') == 'decouverte' for l in c2) or lect(after_exit, 0) or lect(after_exit, 1):
            fails.append('une replique rejouee apres le changement de carte')
        notes.append('carte 2 : ' + ', '.join(f"{kv(l).get('ramassage')}={kv(l).get('etat')}" for l in c2))
    # run 2: after the lines
    if not p(r2, 'charge_apres_attente'):
        fails.append('chargement apres repliques : partie non terminee')
    if lect(r2, 0) or lect(r2, 1):
        fails.append('chargement apres repliques : une replique a ete rejouee')
    # run 3: before the discovery
    if not p(r3, 'rechargee_apres_replique') or len(lect(r3, 1)) != 1:
        fails.append(f'chargement avant decouverte : ligne du fusil jouee {len(lect(r3, 1))} fois (1 attendue)')
    # run 4: a new game
    if len(lect(r4, 1)) != 1:
        fails.append(f'nouvelle partie : ligne du fusil jouee {len(lect(r4, 1))} fois (1 attendue)')
    notes.append(f"chargement apres : {len(lect(r2, 0)) + len(lect(r2, 1))} replique ; chargement avant : {len(lect(r3, 1))} ; nouvelle partie : {len(lect(r4, 1))}")
    return fails, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out')
    a = ap.parse_args()
    probe = ROOT / 'build' / 'arsenal' / 'voice_probe.pk3'
    probe.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(probe, 'w') as z:
        z.writestr('ZSCRIPT.vprobe', PROBE)
        z.writestr('MAPINFO.vprobe', 'gameinfo\n{\n    PlayerClasses = "RFVoiceProbe"\n}\n')
    before = {p: p.stat().st_mtime for p in SAVES.glob('*.zds')} if SAVES.exists() else {}
    r1 = run(a.base, a.module, probe, 'voice_probe_1')
    new = sorted((p for p in SAVES.glob('*.zds') if before.get(p) != p.stat().st_mtime), key=lambda p: p.stat().st_mtime)
    # The exit to BANCDEC2 adds the engine's own save on entering a map: A and B are the probe's saves on BANCDEC1.
    on_first = [p for p in new if json.loads(zipfile.ZipFile(p).read('info.json')).get('Current Map') == 'BANCDEC1']
    if len(on_first) < 2:
        print('sauvegardes A et B introuvables :', new)
        return 1
    save_a, save_b = on_first[0], on_first[-1]
    r2 = run(a.base, a.module, probe, 'voice_probe_2', loadgame=save_b)
    r3 = run(a.base, a.module, probe, 'voice_probe_3', loadgame=save_a)
    r4 = run(a.base, a.module, probe, 'voice_probe_4')
    fails, notes = evaluate(r1, r2, r3, r4)
    for lines in (r1, r2, r3, r4):
        for l in lines:
            if l.startswith('RF_VPROBE') or 'voix ' in l:
                print(l)
        print('--')
    for n in notes:
        print('note:', n)
    print('RESULTAT :', 'PASS' if not fails else 'FAIL')
    for f in fails:
        print('  -', f)
    if a.out:
        Path(a.out).write_bytes(json.dumps(dict(created=time.strftime('%Y-%m-%d %H:%M'), module=a.module, base=a.base,
                                                result='PASS' if not fails else 'FAIL', failures=fails, notes=notes,
                                                saves=[str(save_a), str(save_b)],
                                                runs=[[l for l in r if l.startswith(('RF_VPROBE', 'RF_BENCH'))] for r in (r1, r2, r3, r4)]),
                                           indent=2, ensure_ascii=False).encode('utf-8'))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
