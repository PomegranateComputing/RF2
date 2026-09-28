#!/usr/bin/env python3
"""COMBAT-02: in-game checks of the crowbar in RF02 (a test pk3 loaded after the build; the build is not modified).
A player subclass, invulnerable, runs the cases and prints RF_CB lines: pickup, no ammunition, swing in the air,
against an ambulance, a target at 40 u (two blows), a target at 100 u (out of reach), the tram's cabin wall between
player and target, a weapon change asked during the recovery, a hostile orderly coming (moving target), then an
autosave. Targets are orderlies made friendly and still (they can be hurt, they do not fight back).
The second pk3 (<out>_reload.pk3) is loaded with the autosave (devrun --loadgame): the saved player resumes and
prints the inventory after the load.

Usage: python scripts/production/crowbar_probe.py <out.pk3>
       python scripts/devrun.py --pk3 dist/RF2_DEV.pk3 --map RF02 --name cb_probe --seconds 120 --marker RF_DEV_UI_DONE -- -file <out.pk3>
       python scripts/devrun.py --pk3 dist/RF2_DEV.pk3 --name cb_reload --seconds 60 --marker RF_DEV_UI_DONE --loadgame <autosave> -- -file <out_reload.pk3>
"""
import sys, zipfile
out = sys.argv[1]
zs = r'''version "4.14"
class RFCrowbarProbe : RFPlayer
{
    int t;
    Actor target1, target2, target3, mover;
    int fireAt[16];
    int step;

    void Log(String s) { Console.Printf("RF_CB %s t=%d", s, t); }

    Actor Dummy(Vector2 at)
    {
        Actor a = Actor.Spawn('RFOrderly', (at, Level.PointInSector(at).floorplane.ZAtPoint(at)));
        if (a != null) { a.bFriendly = true; a.Speed = 0; a.A_SetSpeed(0); }
        return a;
    }

    int Puffs() { int n = 0; let it = ThinkerIterator.Create('RFCrowbarPuff'); while (it.Next()) n++; return n; }

    void Place(Vector2 at, double ang) { SetOrigin((at, Level.PointInSector(at).floorplane.ZAtPoint(at)), false); angle = ang; pitch = 0; Vel = (0, 0, 0); }

    override void PlayerThink()
    {
        if (player != null && Level.maptime >= 180)
        {
            t++;
            player.cheats |= CF_GODMODE;
            player.cmd.forwardmove = 0; player.cmd.sidemove = 0; player.cmd.buttons = 0;
            bool fire = false;
            if (t >= 3 && t <= 9) player.cmd.forwardmove = 3200;
            switch (t)
            {
            case 1: Place((1172, 100), 90); break;                                    // walks onto the crowbar: pickup
            case 30: Log(String.Format("pickup inventaire=%d", FindInventory('RFCrowbar') != null));
                     TakeInventory('RFPistolAmmo', 999); TakeInventory('RFRifleAmmo', 999);
                     let fal = RFFAL(FindInventory('RFFAL')); if (fal != null) fal.Magazine = 0;
                     player.PendingWeapon = Weapon(FindInventory('RFCrowbar')); break;
            case 60: Log(String.Format("arme=%s munitions9mm=%d munitions762=%d", player.ReadyWeapon ? player.ReadyWeapon.GetClassName() : 'none', CountInv('RFPistolAmmo'), CountInv('RFRifleAmmo'))); break;
            case 65: fire = true; break;                                              // swing in the air
            case 75: Log(String.Format("dans_le_vide puffs=%d", Puffs())); break;
            case 85: Place((1120, 130), 270); break;
            case 95: fire = true; break;                                              // the ambulance's side
            case 105: Log(String.Format("contre_ambulance puffs=%d", Puffs())); break;
            case 125: Place((1300, 60), 0); target1 = Dummy((1340, 60)); break;
            case 135: fire = true; break;
            case 160: Log(String.Format("cible_40u coup1 sante=%d", target1 ? target1.health : -1)); break;
            case 165: fire = true; break;
            case 190: Log(String.Format("cible_40u coup2 sante=%d morte=%d", target1 ? target1.health : -1, target1 == null || target1.health <= 0)); Place((1250, 200), 0); target2 = Dummy((1350, 200)); break;
            case 200: fire = true; break;
            case 225: Log(String.Format("cible_100u sante=%d", target2 ? target2.health : -1)); SetOrigin((2150, 204, 31), false); angle = 270; pitch = 0; Vel = (0, 0, 0); target3 = Dummy((2150, 158)); break;
            case 235: fire = true; break;
            case 260: Log(String.Format("paroi_du_tram_entre sante=%d z_joueur=%.0f", target3 ? target3.health : -1, Pos.Z)); break;
            case 270: fire = true; break;                                             // switch during the recovery
            case 285: player.PendingWeapon = Weapon(FindInventory('RFBrowning')); Log("demande_de_changement_pendant_le_retour"); break;
            case 289: { let psp = player.FindPSprite(PSP_WEAPON); Log(String.Format("trois_tics_apres arme=%s etat_abaisse=%d", player.ReadyWeapon ? player.ReadyWeapon.GetClassName() : 'none', psp != null && psp.y > 40)); } break;
            case 300: Log(String.Format("apres_changement arme=%s", player.ReadyWeapon ? player.ReadyWeapon.GetClassName() : 'none')); break;
            case 304: if (target2) target2.Destroy(); if (target3) target3.Destroy(); break;   // no friendly dummy left to fight it
            case 305: player.PendingWeapon = Weapon(FindInventory('RFCrowbar')); Place((1384, 20), 90);
                      mover = Actor.Spawn('RFOrderly', ((1384, 224), 8)); if (mover) { mover.target = self; mover.SetStateLabel('See'); } break;   // a hostile orderly comes
            }
            if (t > 340 && t < 600 && mover != null && mover.health > 0 && Distance2D(mover) < 58 && (t % 22) == 0)
            {
                angle = AngleTo(mover); fire = true;
                Log(String.Format("cible_mobile distance=%.0f sante=%d", Distance2D(mover), mover.health));
            }
            if (t == 600) { Log(String.Format("cible_mobile fin sante=%d", mover ? mover.health : -1)); Level.MakeAutoSave(); }
            if (t == 640) { Log(String.Format("sauvegarde inventaire=%d", FindInventory('RFCrowbar') != null)); Console.Printf("RF_DEV_UI_DONE"); }
            if (fire) player.cmd.buttons = BT_ATTACK;
        }
        Super.PlayerThink();
    }
}
class RFCrowbarReload : RFPlayer
{
    int t;
    override void PlayerThink()
    {
        t++;
        if (t == 20) { Console.Printf("RF_CB rechargement inventaire=%d arme=%s", FindInventory('RFCrowbar') != null, player.ReadyWeapon ? player.ReadyWeapon.GetClassName() : 'none'); Console.Printf("RF_DEV_UI_DONE"); }
        Super.PlayerThink();
    }
}
'''
with zipfile.ZipFile(out, 'w') as z:
    z.writestr('ZSCRIPT.probe', zs)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFCrowbarProbe"\n}\n')
reload_out = out.replace('.pk3', '_reload.pk3')
with zipfile.ZipFile(reload_out, 'w') as z:
    z.writestr('ZSCRIPT.probe', zs)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFCrowbarReload"\n}\n')
print(out, reload_out)
