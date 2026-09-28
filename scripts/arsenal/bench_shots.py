#!/usr/bin/env python3
"""Screenshots of the arsenal test bench at chosen moments, at several screen formats, and a contact sheet.

    python scripts/arsenal/bench_shots.py --base BASE.pk3 --module RF2_ARSENAL_ESSAI.pk3 --out DIR

A scripted player (a third file, for this run only) fires, pumps, reloads, opens the revolver with one then three
rounds in, shoots in the dark lane and against the close wall, then raises the FAL and the Browning for comparison at
the same presentation settings. Formats: 1920x1080 (reference), 2560x1080 (21:9), 1440x1080 (4:3).
The pictures are for eyes: nothing here judges them.
"""
import argparse, shutil, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SHOTS = [  # (tic, label)
    (24, 'W03_pret'), (31, 'W03_tir_flash'), (41, 'W03_pompe_arriere'), (47, 'W03_pompe_avant'),
    (71, 'W03_cartouche_introduite'), (140, 'W03_apres_recharge'), (160, 'W03_couloir_sombre'), (166, 'W03_tir_sombre'),
    (200, 'W04_pret'), (206, 'W04_tir_flash'), (298, 'W04_ejection'), (313, 'W04_barillet_1_cartouche'),
    (327, 'W04_barillet_3_cartouches'), (380, 'W04_apres_recharge'), (401, 'W04_tir_mur_proche'),
    (445, 'FAL_reference'), (475, 'Browning_reference'),
]
FORMATS = [(1920, 1080), (2560, 1080), (1440, 1080)]

PROBE = r'''version "4.14"
class RFBenchShots : RFPlayer
{
    int t;
    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            player.cheats |= CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            int b = 0;
            if (t == 1) { SetOrigin((-8, 128, 0), false); angle = 0; pitch = 0; }
            if (t == 30 || t == 165 || t == 205 || t == 225 || t == 245 || t == 265 || t == 400) b |= BT_ATTACK;
            if (t == 60 || t == 285) b |= BT_RELOAD;
            if (t == 150) { SetOrigin((-8, 448, 0), false); angle = 0; }
            if (t == 180) player.PendingWeapon = Weapon(FindInventory('RFBenchMR73'));
            if (t == 190) { SetOrigin((-8, 128, 0), false); angle = 0; }
            if (t == 390) { SetOrigin((-160, 128, 0), false); angle = 180; }
            if (t == 420) { SetOrigin((-8, 128, 0), false); angle = 0; player.PendingWeapon = Weapon(FindInventory('RFFAL')); }
            if (t == 450) player.PendingWeapon = Weapon(FindInventory('RFBrowning'));
            %s
            if (t == 490) Console.Printf("RF_DEV_UI_DONE");
            Vel = (0, 0, 0);
            player.cmd.buttons = b;
        }
        Super.PlayerThink();
    }
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    shots = '\n            '.join(f'if (t == {tic}) {{ Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_SHOT {label}"); Level.MakeScreenShot(); }}' for tic, label in SHOTS)
    probe = ROOT / 'build' / 'arsenal' / 'shots_probe.pk3'
    probe.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(probe, 'w') as z:
        z.writestr('ZSCRIPT.shots', PROBE % shots)
        z.writestr('MAPINFO.shots', 'gameinfo\n{\n    PlayerClasses = "RFBenchShots"\n}\n')
    font = ImageFont.truetype('arial.ttf', 22)
    for w, h in FORMATS:
        name = f'bench_shots_{w}x{h}'
        shotdir = ROOT / 'build' / 'dev' / 'shots' / name
        before = set(shotdir.glob('*.png')) if shotdir.exists() else set()    # earlier runs are kept, not reused
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'devrun.py'), '--pk3', a.base, '--map', 'ARSENAL', '--name', name,
                        '--seconds', '60', '--marker', 'RF_DEV_UI_DONE', '--width', str(w), '--height', str(h),
                        '--', '-file', a.module, str(probe)], cwd=ROOT, capture_output=True, text=True)
        pngs = sorted(set(shotdir.glob('*.png')) - before)
        if len(pngs) != len(SHOTS):
            print(f'{name}: {len(pngs)} captures pour {len(SHOTS)} prevues')
        fdir = out / f'{w}x{h}'
        fdir.mkdir(exist_ok=True)
        for (tic, label), p in zip(SHOTS, pngs):
            shutil.copy2(p, fdir / f'{label}.png')
        tw = 480
        th = int(tw * h / w)
        cols = 3
        rows = (len(SHOTS) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + 34) + 40), (18, 18, 18))
        d = ImageDraw.Draw(sheet)
        d.text((8, 8), f'Banc d\'essai arsenal - {w}x{h} - images et sons PROVISOIRES si non livres', fill=(255, 255, 255), font=font)
        for i, (tic, label) in enumerate(SHOTS):
            f = fdir / f'{label}.png'
            if not f.exists():
                continue
            x, y = 8 + (i % cols) * (tw + 8), 40 + (i // cols) * (th + 34)
            d.text((x, y), f'{label} (t={tic})', fill=(255, 220, 120), font=font)
            sheet.paste(Image.open(f).convert('RGB').resize((tw, th)), (x, y + 28))
        sheet.save(out / f'planche_{w}x{h}.jpg', quality=85)
        print(out / f'planche_{w}x{h}.jpg')
    return 0


if __name__ == '__main__':
    sys.exit(main())
