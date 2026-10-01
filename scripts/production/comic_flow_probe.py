#!/usr/bin/env python3
"""Flow checks of the transition pages (comics.zs), with ordinary inputs, on any build.

Writes a test pk3 that (1) adds a TEST page for the scene of the chapter ending under test (assembled from four
game captures, marked ESSAI: a test fixture, never shipped), and (2) replaces the player class by a probe that ends
the chapter itself (RFDirector.StartOutro, as the exit line does) and then presses keys like a player:
  read   : Use every 40 tics until the page closes; then 150 tics in the next chapter
  pass   : Use held 45 tics (passes the page)
  fire   : Fire to advance, the last press held 120 tics across the change of chapter (must not fire there)
  save   : Use once, then an autosave during the page (MakeAutoSave), then the run stops: a second run loads it
  load   : after loading a save: Use every 40 tics (the replayed page must close and lead to the next chapter)
  shots  : screenshots of each panel step (aspect ratios: run with --width/--height)
Every step is logged (RF_COMICPROBE ...) with the director's state, the player's flags, position, weapon and ammo.

Usage: python scripts/production/comic_flow_probe.py out.pk3 <mode> <scene id> <page png> [<capture1..4>]
"""
import sys, zipfile, io
from PIL import Image, ImageDraw, ImageFont

out, mode, scene = sys.argv[1], sys.argv[2], sys.argv[3]
page_png = sys.argv[4] if len(sys.argv) > 4 else None

PROBE = r'''version "4.14"
class RFComicProbe : RFPlayer
{
    int t, holdUse, holdFire, pressUse, pressFire, mapT;
    String mapName;
    int ammo0;
    bool ended, arrived;

    override void PlayerThink()
    {
        if (player != null)
        {
            t++;
            if (!(Level.MapName ~== mapName)) { mapName = Level.MapName; mapT = 0; }
            mapT++;
            let d = RFDirector(EventHandler.Find('RFDirector'));
            Script(d);
            if (holdUse > 0) { player.cmd.buttons |= BT_USE; holdUse--; }
            if (holdFire > 0) { player.cmd.buttons |= BT_ATTACK; holdFire--; }
        }
        Super.PlayerThink();
    }

    int Ammo()
    {
        let w = player.ReadyWeapon;
        if (w == null) return -1;
        let fal = RFFAL(w);
        if (fal != null) return fal.Magazine * 1000 + fal.ReserveCount();
        return w.Ammo1 ? w.Ammo1.Amount : -1;
    }

    void Log(RFDirector d, String what)
    {
        Console.Printf("RF_COMICPROBE t=%d map=%s mt=%d %s outro=%d comic=%s step=%d hold=%d cheats=%d x=%.0f y=%.0f weapon=%s ammo=%d",
            t, Level.MapName, mapT, what, d ? d.outro : -1, (d && d.comic) ? d.comic.id : "-", d ? d.comicStep : -1,
            d ? d.arrivalHold : -1, player.cheats, Pos.X, Pos.Y, player.ReadyWeapon ? player.ReadyWeapon.GetClassName() : 'none', Ammo());
    }

    void Script(RFDirector d)
    {
        if (d == null) return;
        String mode = "%(mode)s";
        bool first = Level.MapName ~== "%(from)s";
        if (first)
        {
            if (mode == "fire" && mapT == 2) { GiveInventory('RFFAL', 1); GiveInventory('RFRifleAmmo', 40); A_SelectWeapon('RFFAL'); }
            if (mode != "load" && mapT == 60 && !d.outro) { ammo0 = Ammo(); d.StartOutro(self); Log(d, "fin_demandee"); }
            if (mode == "load" && mapT == 20) Log(d, "apres_chargement");
            if (!d.outro) return;
            if (mapT %% 10 == 0) Log(d, "page");
            if ((mode == "read" || mode == "load" || mode == "shots") && mapT > 100 && mapT %% 40 == 0) { holdUse = 1; Log(d, "appui_utiliser"); }
            if (mode == "shots" && mapT > 100 && mapT %% 40 == 20) { Level.MakeScreenShot(); Log(d, "capture"); }
            if (mode == "pass" && mapT == 110) { holdUse = 45; Log(d, "maintien_utiliser"); }
            if (mode == "fire" && mapT > 100 && mapT %% 40 == 0)
            {
                if (d.comic && d.comicStep >= d.comic.PanelCount()) { holdFire = 120; Log(d, "dernier_appui_tir_maintenu"); }
                else { holdFire = 1; Log(d, "appui_tir"); }
            }
            if (mode == "save" && mapT == 100) { holdUse = 1; Log(d, "appui_utiliser"); }
            if (mode == "save" && mapT == 150) { Level.MakeAutoSave(); Log(d, "sauvegarde_pendant_la_page"); }
            if (mode == "save" && mapT == 190) Console.Printf("RF_DEV_UI_DONE");
            if (mapT > 2000) Console.Printf("RF_DEV_UI_DONE");
        }
        else
        {
            if (mapT == 1) { Log(d, "arrivee"); }
            if (mapT <= 12 || mapT %% 15 == 0) Log(d, "suivant");
            if (mapT == 150) { Log(d, "fin_essai"); Console.Printf("RF_DEV_UI_DONE"); }
        }
    }
}
'''


def test_page(caps):
    W, H = 1920, 1080
    page = Image.new('RGB', (W, H), (12, 12, 12))
    rects = [(24, 24, 1180, 640), (1228, 24, 668, 310), (1228, 354, 668, 310), (24, 688, 1872, 368)]
    for (x, y, w, h), c in zip(rects, caps):
        im = Image.open(c).convert('L').convert('RGB')
        r = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
        im = im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))
        page.paste(im, (x, y))
        ImageDraw.Draw(page).rectangle([x - 3, y - 3, x + w + 2, y + h + 2], outline=(235, 235, 235), width=4)
    d = ImageDraw.Draw(page)
    f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 120)
    d.text((W // 2 - 300, H // 2 - 70), 'ESSAI', font=f, fill=(200, 40, 40))
    b = io.BytesIO()
    page.save(b, 'PNG')
    return b.getvalue()


SCENES = {'RF01_RF02': 'RF01', 'RF02_RF04': 'RF02', 'RF04_RF05': 'RF04', 'RF05_RF06': 'RF05', 'RF06_RF07': 'RF06'}
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ZSCRIPT.comicprobe', PROBE.replace('%(mode)s', mode).replace('%(from)s', SCENES[scene]).replace('%%', '%'))
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFComicProbe"\n}\n')
    if len(sys.argv) >= 9:
        z.writestr(f'graphics/comics/{scene}.png', test_page(sys.argv[5:9]))
print('comic probe', out, mode, scene)
