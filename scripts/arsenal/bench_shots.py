#!/usr/bin/env python3
"""Pictures of the arsenal test bench, each one labelled by what it really shows, at several screen formats.

    python scripts/arsenal/bench_shots.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3 --out DIR [--formats ...] [--speed 0.1]

A screenshot does not always show the tic it was asked at (while the engine writes PNG files it can present an
older frame, by up to a dozen tics in a burst). So the bench draws the game tic in the corner of every picture
(scripts/arsenal/ticcode.py) and logs, for every rendered tic, what the picture shows (RF_RENDER: weapon, sequence,
image, hand stage, chamber, ammunition). Here a scripted player plays the scene below while a screenshot is asked
at every tic (the game slowed by --speed); each picture is then read back, and one picture is kept per distinct
state, named from the RF_RENDER line of its own tic.
Scene: W03 ready, shot, pump, two shell insertions, dark lane and a shot there; W04 selection, ready, shot, a reload
with two fired cases and four rounds in the cylinder (opening, ejection, six insertions, closing); a shot against
the close wall; FAL and Browning at the same settings. Nothing here judges the pictures.
"""
import argparse, json, re, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ticcode  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FORMATS = [(1920, 1080), (2560, 1080), (1440, 1080)]

PROBE = r'''version "4.14"
class RFBenchShots : RFPlayer
{
    int t, step, wait;

    bool IdleW(Weapon w)
    {
        if (w == null || player.ReadyWeapon != w || player.PendingWeapon != WP_NOCHANGE) return false;
        let psp = player.FindPSprite(PSP_WEAPON);
        if (psp == null || psp.y > 32.01 || psp.CurState != w.FindState("Ready")) return false;
        let bw = RFBenchWeapon(w);
        return bw == null || (!bw.Reloading && bw.SeqName == "ready");
    }
    bool Idle(Name cls) { return IdleW(Weapon(FindInventory(cls))); }
    void Mark(String what) { Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_MARK t=%d %s", Level.maptime, what); }
    void Place(Vector2 at, double ang) { SetOrigin((at, 0), false); angle = ang; pitch = 0; Vel = (0, 0, 0); }

    int Advance()
    {
        let rp = RFBenchWeapon(FindInventory('RFBenchRapid'));
        let mr = RFBenchRevolver(FindInventory('RFBenchMR73'));
        if (t > 3000) { step = 999; return 0; }
        switch (step)
        {
        case 0: Place((-8, 128), 0); step++; return 0;
        case 1: if (!Idle('RFBenchRapid')) return 0; wait = 8; step++; return 0;
        case 2: Mark("W03_tir"); step++; wait = 2; return BT_ATTACK;
        case 3: if (!Idle('RFBenchRapid')) return 0; if (rp.Capacity() - rp.Loaded() < 2) { wait = 2; return BT_ATTACK; } Mark("W03_recharge"); step++; wait = 2; return BT_RELOAD;
        case 4: if (!Idle('RFBenchRapid')) return 0; Place((-8, 448), 0); Mark("W03_couloir_sombre"); wait = 10; step++; return 0;
        case 5: Mark("W03_tir_sombre"); step++; wait = 2; return BT_ATTACK;
        case 6: if (!Idle('RFBenchRapid')) return 0; Place((-8, 128), 0); Mark("W04_selection"); player.PendingWeapon = Weapon(FindInventory('RFBenchMR73')); step++; return 0;
        case 7: if (!Idle('RFBenchMR73')) return 0; wait = 8; step++; return 0;
        case 8: Mark("W04_tir"); step++; wait = 2; return BT_ATTACK;
        case 9: if (!Idle('RFBenchMR73')) return 0; step++; wait = 2; return BT_ATTACK;     // two fired cases, four rounds
        case 10: if (!Idle('RFBenchMR73')) return 0; Mark("W04_recharge"); step++; wait = 2; return BT_RELOAD;
        case 11: if (!Idle('RFBenchMR73')) return 0; Place((-160, 128), 180); Mark("W04_mur_proche"); wait = 10; step++; return 0;
        case 12: step++; wait = 2; return BT_ATTACK;
        case 13: if (!Idle('RFBenchMR73')) return 0; Place((-8, 128), 0); Mark("FAL_reference"); player.PendingWeapon = Weapon(FindInventory('RFFAL')); step++; return 0;
        case 14: if (!Idle('RFFAL')) return 0; wait = 6; Mark("Browning_reference"); player.PendingWeapon = Weapon(FindInventory('RFBrowning')); step++; return 0;
        case 15: if (!Idle('RFBrowning')) return 0; wait = 8; step++; return 0;
        case 16: step = 999; return 0;
        }
        return 0;
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            if (t == 1) { let h = RFBenchHandler(EventHandler.Find('RFBenchHandler')); if (h) h.renderLog = true; }
            player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            Vel = (0, 0, 0);
            int b = 0;
            if (wait > 0) wait--;
            else if (step < 999) b = Advance();
            player.cmd.buttons = b;
            if (t >= 12 && step < 999) Level.MakeScreenShot();
            if (step == 999) { step = 1000; Console.Printf("RF_DEV_UI_DONE"); }
        }
        Super.PlayerThink();
    }
}
'''
RENDER = re.compile(r'RF_RENDER t=(\d+) arme=(\S+) seq=(\S+) image=(\S+) y=(\S+) main=(\d+) ch=(\d+) pose=(\d+) munitions=(.*)$')
SHORT = {'RFBenchRapid': 'W03', 'RFBenchMR73': 'W04', 'RFFAL': 'FAL', 'RFBrowning': 'BHP', 'RFCrowbar': 'PDB'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--formats', default=','.join(f'{w}x{h}' for w, h in FORMATS))
    ap.add_argument('--speed', type=float, default=0.1)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    probe = ROOT / 'build' / 'arsenal' / 'shots_probe.pk3'
    probe.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(probe, 'w') as z:
        z.writestr('ZSCRIPT.shots', PROBE)
        z.writestr('MAPINFO.shots', 'gameinfo\n{\n    PlayerClasses = "RFBenchShots"\n}\n')
    # Slowed game, the way Astra's W03/W04 V01 checks did it (run_engine_checks.py): i_timescale set by a deferred
    # exec once the engine runs (on the command line it does not hold, and ZScript may not set it) and cl_capfps 1;
    # a 1080p PNG takes longer to write than a tic lasts, and a picture shows the last frame actually rendered.
    cfg = probe.with_name('timescale.cfg')
    cfg.write_bytes(f'wait 10; i_timescale {a.speed}\n'.encode())
    font = ImageFont.truetype('arial.ttf', 18)
    report = {}
    for fmt in a.formats.split(','):
        w, h = (int(v) for v in fmt.split('x'))
        name = f'bench_shots_{w}x{h}'
        shotdir = ROOT / 'build' / 'dev' / 'shots' / name
        before = set(shotdir.glob('*.png')) if shotdir.exists() else set()    # earlier runs are kept, not reused
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'devrun.py'), '--pk3', a.base, '--map', 'ARSENAL', '--name', name,
                        '--seconds', str(40 / a.speed + 120), '--marker', 'RF_DEV_UI_DONE', '--width', str(w), '--height', str(h),
                        '--', '-file', a.module, str(probe), '+exec', str(cfg), '+cl_capfps', '1'], cwd=ROOT, capture_output=True, text=True)
        log = (ROOT / 'build' / 'dev' / 'logs' / f'{name}.txt').read_text(encoding='utf-8', errors='replace').splitlines()
        pngs = sorted(set(shotdir.glob('*.png')) - before)
        render = {}
        for l in log:
            m = RENDER.match(l)
            if m:
                render[int(m.group(1))] = dict(arme=m.group(2), seq=m.group(3), image=m.group(4), y=float(m.group(5)),
                                               main=int(m.group(6)), ch=int(m.group(7)), pose=int(m.group(8)), munitions=m.group(9).strip())
        marks = [(int(t), what) for t, what in re.findall(r'RF_MARK t=(\d+) (\S+)', '\n'.join(log))]
        fdir = out / fmt
        fdir.mkdir(exist_ok=True)
        kept, seen, unreadable, shown_tics = [], set(), 0, set()
        read = sorted(((ticcode.read(p), p) for p in pngs), key=lambda r: (r[0] is None, r[0] or 0))
        for tic, p in read:
            im = Image.open(p)
            if tic is None or tic not in render:
                unreadable += 1
                continue
            shown_tics.add(tic)
            s = render[tic]
            raising = s['y'] > 32.5
            key = (s['arme'], s['seq'], s['image'], s['main'], s['ch'], s['pose'], s['munitions'], raising)
            if key in seen:
                continue
            seen.add(key)
            mark = max((m for m in marks if m[0] <= tic), default=(0, ''))[1]
            label = f"{tic:04d}_{SHORT.get(s['arme'], s['arme'])}_{s['seq']}_{s['image']}"
            if s['main']:
                label += f"_ch{s['ch']}_main{s['main']}"
            elif s['pose']:
                label += f"_pose{s['pose']}"
            if raising:
                label += '_en_mouvement'
            im.save(fdir / f'{label}.png')
            kept.append(dict(label=label, tic=tic, repere=mark, **s))
        span = range(min(shown_tics), max(shown_tics) + 1) if shown_tics else range(0)
        report[fmt] = dict(speed=a.speed, captures=len(pngs), illisibles=unreadable, tics_montres=len(shown_tics),
                           tics_de_la_scene=len(span), etats_retenus=len(kept), images=kept)
        print(f'{fmt}: {len(pngs)} captures, {len(shown_tics)} tics differents montres sur {len(span)}, {len(kept)} etats retenus, '
              f'{unreadable} illisibles')
        tw = 400
        th = int(tw * h / w)
        cols = 5
        rows = (len(kept) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + 46) + 40), (18, 18, 18))
        d = ImageDraw.Draw(sheet)
        d.text((8, 8), f"Banc d'essai arsenal - {fmt} - une image par etat, etiquetee par le tic qu'elle montre", fill=(255, 255, 255), font=font)
        for i, k in enumerate(kept):
            x, y = 8 + (i % cols) * (tw + 8), 40 + (i // cols) * (th + 46)
            d.text((x, y), k['label'][:44], fill=(255, 220, 120), font=font)
            d.text((x, y + 20), f"{k['munitions']}  ({k['repere']})", fill=(200, 200, 200), font=font)
            sheet.paste(Image.open(fdir / f"{k['label']}.png").convert('RGB').resize((tw, th)), (x, y + 42))
        sheet.save(out / f'planche_{fmt}.jpg', quality=85)
    (out / 'captures.json').write_bytes(json.dumps(report, indent=2, ensure_ascii=False).encode('utf-8'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
