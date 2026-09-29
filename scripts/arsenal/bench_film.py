#!/usr/bin/env python3
"""A film of the arsenal test bench with the sound the engine really played, for eyes and ears.

    python scripts/arsenal/bench_film.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3 --name NAME [--every 2]

A scripted player (a third file, for this run only) plays, each step waiting for the weapon to be ready: W03 single
shot, repeated shots to empty, dry fire, full reload, two shots, reload stopped by fire; Browning then FAL, three
shots each (references, same session, same settings); W04 single shot, repeated shots to empty, dry fire, full
reload, two shots, partial reload; back to W03 (selection and stowing are in the film at every change).
scripts/film.py records it: engine screenshots on its millisecond clock, and the game's mixed sound through OpenAL
Soft's wave writer, aligned on the sync tone the engine plays at tic 1. The sound is the engine's output, not a track
rebuilt from the log. Writes build/dev/film/<NAME>/<NAME>.mp4, <NAME>.wav, film.json, and the scene's log lines.
"""
import argparse, json, re, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCENE = r'''version "4.14"
class RFBenchFilm : RFPlayer
{
    int t, step, wait, presses, baseCommits;

    bool IdleW(Weapon w)
    {
        if (w == null || player.ReadyWeapon != w || player.PendingWeapon != WP_NOCHANGE) return false;
        let psp = player.FindPSprite(PSP_WEAPON);
        if (psp == null || psp.y > 32.01 || psp.CurState != w.FindState("Ready")) return false;
        let bw = RFBenchWeapon(w);
        return bw == null || (!bw.Reloading && bw.SeqName == "ready");
    }
    bool Idle(Name cls) { return IdleW(Weapon(FindInventory(cls))); }
    void Mark(String what) { Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_SCENE t=%d %s", Level.maptime, what); }
    void Take(Name cls) { player.PendingWeapon = Weapon(FindInventory(cls)); }

    // Fire `count` times as soon as the weapon is ready (count 0: until it clicks empty).
    int Burst(Name cls, int count, int pause)
    {
        if (!Idle(cls)) return 0;
        let w = RFBenchWeapon(FindInventory(cls));
        bool more = count > 0 ? presses < count : (w == null || w.Loaded() > 0);
        if (more) { presses++; wait = pause; return BT_ATTACK; }
        presses = 0; step++; return 0;
    }

    int Advance()
    {
        let rp = RFBenchWeapon(FindInventory('RFBenchRapid'));
        let mr = RFBenchWeapon(FindInventory('RFBenchMR73'));
        if (t > 3200) { Mark("fin_limite"); step = 999; return 0; }
        switch (step)
        {
        case 0: if (!Idle('RFBenchRapid') || t < 45) return 0; Mark("W03_pret"); wait = 25; step++; return 0;     // filming starts at tic 36
        case 1: Mark("W03_tir_isole"); step++; return 0;
        case 2: return Burst('RFBenchRapid', 1, 30);
        case 3: if (!Idle('RFBenchRapid')) return 0; wait = 20; Mark("W03_tirs_repetes"); step++; return 0;
        case 4: return Burst('RFBenchRapid', 0, 1);
        case 5: if (!Idle('RFBenchRapid')) return 0; Mark("W03_tir_a_vide"); wait = 12; step++; return BT_ATTACK;
        case 6: if (!Idle('RFBenchRapid')) return 0; Mark("W03_recharge_complete"); wait = 2; step++; return BT_RELOAD;
        case 7: if (!Idle('RFBenchRapid')) return 0; wait = 15; Mark("W03_deux_tirs"); step++; return 0;
        case 8: return Burst('RFBenchRapid', 2, 1);
        case 9: if (!Idle('RFBenchRapid')) return 0; Mark("W03_recharge_interrompue_par_tir"); baseCommits = rp.Commits; step++; wait = 2; return BT_RELOAD;
        case 10: if (rp.Commits <= baseCommits) return 0; step++; return BT_ATTACK;
        case 11: if (!Idle('RFBenchRapid')) return 0; wait = 20; Mark("Browning_reference"); Take('RFBrowning'); step++; return 0;
        case 12: return Burst('RFBrowning', 3, 12);
        case 13: if (!Idle('RFBrowning')) return 0; wait = 15; Mark("FAL_reference"); Take('RFFAL'); step++; return 0;
        case 14: return Burst('RFFAL', 3, 10);
        case 15: if (!Idle('RFFAL')) return 0; wait = 15; Mark("W04_selection"); Take('RFBenchMR73'); step++; return 0;
        case 16: if (!Idle('RFBenchMR73')) return 0; wait = 25; Mark("W04_tir_isole"); step++; return 0;
        case 17: return Burst('RFBenchMR73', 1, 30);
        case 18: if (!Idle('RFBenchMR73')) return 0; wait = 20; Mark("W04_tirs_repetes"); step++; return 0;
        case 19: return Burst('RFBenchMR73', 0, 1);
        case 20: if (!Idle('RFBenchMR73')) return 0; Mark("W04_tir_a_vide"); wait = 12; step++; return BT_ATTACK;
        case 21: if (!Idle('RFBenchMR73')) return 0; Mark("W04_recharge_complete"); wait = 2; step++; return BT_RELOAD;
        case 22: if (!Idle('RFBenchMR73')) return 0; wait = 15; Mark("W04_deux_tirs"); step++; return 0;
        case 23: return Burst('RFBenchMR73', 2, 1);
        case 24: if (!Idle('RFBenchMR73')) return 0; Mark("W04_recharge_partielle"); step++; wait = 2; return BT_RELOAD;
        case 25: if (!Idle('RFBenchMR73')) return 0; wait = 20; Mark("W03_selection"); Take('RFBenchRapid'); step++; return 0;
        case 26: if (!Idle('RFBenchRapid')) return 0; wait = 30; step++; return 0;
        case 27: Mark("fin_scene"); step = 999; return 0;
        }
        return 0;
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            Vel = (0, 0, 0);
            int b = 0;
            if (wait > 0) wait--;
            else if (step < 999) b = Advance();
            player.cmd.buttons = b;
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_TICMS t=%d ms=%.1f", Level.maptime, MSTimeF());
        }
        Super.PlayerThink();
    }
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--every', type=int, default=2)
    ap.add_argument('--end', type=int, default=1000)
    ap.add_argument('--width', type=int, default=1280)
    ap.add_argument('--height', type=int, default=720)
    a = ap.parse_args()
    scene = ROOT / 'build' / 'arsenal' / 'film_scene.pk3'
    scene.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(scene, 'w') as z:
        z.writestr('ZSCRIPT.scene', SCENE)
        z.writestr('MAPINFO.scene', 'gameinfo\n{\n    PlayerClasses = "RFBenchFilm"\n}\n')
    cmd = [sys.executable, str(ROOT / 'scripts' / 'film.py'), '--name', a.name, '--map', 'ARSENAL', '--no-autopilot',
           '--pk3', str(Path(a.base).resolve()), '--every', str(a.every), '--end', str(a.end), '--width', str(a.width),
           '--height', str(a.height), '--seconds', str(a.end / 35 + 90), '--', '-file', str(Path(a.module).resolve()), str(scene)]
    code = subprocess.run(cmd, cwd=ROOT).returncode
    if code != 0:
        return code
    return retime(a.name, a.every)


def retime(name, every):
    """Put every picture at the tic it shows (its tic strip), on the engine's millisecond clock of that tic, and cut the
    engine's own recording on the same clock: <name>_tics.mp4. A screenshot can show an older frame than the tic it
    was asked at; placed by request it would drift from the sound, placed by what it shows it cannot."""
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(ROOT / 'scripts'))
    import ticcode
    import film
    out = ROOT / 'build' / 'dev' / 'film' / name
    info = json.loads((out / 'film.json').read_text(encoding='utf-8'))
    log = (ROOT / 'build' / 'dev' / 'logs' / f'film_{name}.txt').read_text(encoding='utf-8', errors='replace')
    ms = {int(k): float(v) for k, v in re.findall(r'RF_TICMS t=(\d+) ms=([\d.]+)', log)}
    shots = sorted((ROOT / 'build' / 'dev' / 'shots' / f'film_{name}').glob('*.png'))
    shown = {}
    for p in shots:
        tic = ticcode.read(p)
        if tic is not None and tic in ms and tic not in shown:
            shown[tic] = p
    tics = sorted(shown)
    if len(tics) < 2 or info.get('offset_s') is None:
        print('retime: pas assez d images lisibles ou pas de calage du son')
        return 1
    lines = []
    for k, tc in enumerate(tics):
        dur = (ms[tics[k + 1]] - ms[tc]) / 1000.0 if k + 1 < len(tics) else every / 35.0
        lines += [f"file '{shown[tc].as_posix()}'", f'duration {dur:.4f}']
    lines.append(f"file '{shown[tics[-1]].as_posix()}'")
    (out / 'frames_tics.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    audio, sr = film.read_wav(out / 'capture_float.wav')
    t0 = info['offset_s'] + ms[tics[0]] / 1000.0
    t1 = info['offset_s'] + ms[tics[-1]] / 1000.0 + every / 35.0
    seg = audio[max(0, int(t0 * sr)):int(t1 * sr)]
    wav = out / f'{name}_tics.wav'
    film.write_wav16(wav, seg, sr)
    mp4 = out / f'{name}_tics.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(out / 'frames_tics.txt'), '-i', str(wav),
                    '-vf', 'fps=35,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', str(mp4)], check=True)
    steps = np.diff([ms[k] for k in sorted(ms)])
    span = range(tics[0], tics[-1] + 1)
    gaps = np.diff(tics)
    report = dict(video=str(mp4), images_lues=len(shots), tics_montres=len(tics), tics_du_film=len(span),
                  plus_grand_trou_tics=int(gaps.max()), audio='sortie du moteur (OpenAL, ecrivain WAV), calee par le bip du tic 1',
                  duree_tic_ms=dict(nominal=round(1000 / 35, 2), mediane=round(float(np.median(steps)), 2),
                                    p95=round(float(np.percentile(steps, 95)), 2), max=round(float(steps.max()), 2)),
                  ecoute='non ecoute')
    (out / 'film_tics.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
