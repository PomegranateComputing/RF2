#!/usr/bin/env python3
"""Engine views of one enemy family on any build: a separate test pk3 (loaded after the build) whose player class
places one figure of the family in front of a fixed camera, one pose per view, and takes a screenshot of each.
The build under test is not modified.

Standard sheet (same order on every build, so that two builds compare view by view):
  standing (Spawn) at 128, 256, 512 units, face then profile;
  the four walk frames (See) at 256, face then profile;
  the first frames of the attack (Melee, or Missile) and the pain frame at 128, face;
  the corpse after its fall (Death played to its end) at 128, face then profile.
The figure is frozen on its frame (no action runs after the first); the other monsters of the map are made invisible
and the player cannot be targeted. Each view prints RF_ENEMYVIEW index=.. label=.. t=.. before its screenshot, and a
tic strip in the top-left corner shows the tic the picture was drawn at (read it with ticcode.py).

Usage: python scripts/production/enemy_views_pk3.py <Class> <x> <y> <angle> out.pk3 [wait_tics]
       python scripts/devrun.py --pk3 <build.pk3> --map RF04 --name <name> --seconds 300 --marker RF_DEV_UI_DONE -- -file out.pk3
"""
import sys, zipfile

cls, x, y, ang, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
wait = int(sys.argv[6]) if len(sys.argv) > 6 else 180
# (label, state label, frame offset, distance, turn): turn 180 = facing the camera, 90 = its left side to the camera
views = []
for d in (128, 256, 512):
    views += [(f'debout_{d}_face', 'Spawn', 0, d, 180), (f'debout_{d}_profil', 'Spawn', 0, d, 90)]
for i in range(4):
    views += [(f'marche{i + 1}_256_face', 'See', i, 256, 180), (f'marche{i + 1}_256_profil', 'See', i, 256, 90)]
views += [(f'attaque{i + 1}_128_face', 'Attack', i, 128, 180) for i in range(3)]
views += [('douleur_128_face', 'Pain', 0, 128, 180), ('corps_128_face', 'Death', 0, 128, 180),
          ('corps_128_profil', 'Death', 0, 128, 90)]
arr = lambda i, q: ', '.join((f'"{v[i]}"' if q else str(float(v[i])) if isinstance(v[i], float) else str(v[i])) for v in views)
zs = '''version "4.14"
class RFEnemyViewPlayer : RFPlayer
{
    int step, phase;
    bool hidden;
    Actor foe;
    override void PlayerThink()
    {
        static const String LABELS[] = { %s };
        static const String POSES[] = { %s };
        static const int FRAMES[] = { %s };
        static const int DIST[] = { %s };
        static const int TURN[] = { %s };
        int n = %d;
        Vector2 cam = (%f, %f);
        double camAngle = %f;
        if (player != null && Level.maptime >= %d)
        {
            player.cheats |= CF_NOCLIP | CF_GODMODE | CF_NOTARGET;
            player.cmd.buttons = 0;
            player.cmd.forwardmove = 0;
            player.cmd.sidemove = 0;
            if (!hidden)
            {
                hidden = true;
                let it = ThinkerIterator.Create("Actor");
                Actor a;
                while ((a = Actor(it.Next())) != null)
                    if (a != self && a.bIsMonster)
                    {
                        a.A_SetRenderStyle(0, STYLE_None);
                        a.bDormant = true;
                    }
            }
            if (step >= n) { if (phase++ == 0) Console.Printf("RF_DEV_UI_DONE"); }
            else
            {
                int t = phase++;
                Vector2 at = cam + (cos(camAngle), sin(camAngle)) * DIST[step];
                if (t == 0)
                {
                    SetOrigin((cam, Level.PointInSector(cam).floorplane.ZAtPoint(cam)), false);
                    if (foe != null) foe.Destroy();
                    foe = Actor.Spawn("%s", (at, Level.PointInSector(at).floorplane.ZAtPoint(at)));
                    if (foe != null)
                    {
                        foe.angle = camAngle + TURN[step];
                        String label = POSES[step];
                        if (label == "Attack") label = foe.FindState("Melee") != null ? "Melee" : "Missile";
                        State s = null;                                  // state labels must be literal
                        if (label == "Spawn") s = foe.FindState("Spawn");
                        else if (label == "See") s = foe.FindState("See");
                        else if (label == "Melee") s = foe.FindState("Melee");
                        else if (label == "Missile") s = foe.FindState("Missile");
                        else if (label == "Pain") s = foe.FindState("Pain");
                        if (label == "Death")
                            foe.DamageMobj(null, null, foe.health + 100, 'None', DMG_FORCED);
                        else if (s != null)
                        {
                            for (int i = 0; i < FRAMES[step] && s.NextState != null; i++) s = s.NextState;
                            foe.SetState(s, true);                     // the frame without its action
                            foe.tics = -1;
                        }
                    }
                }
                if (foe != null && foe.health > 0)
                {
                    foe.SetOrigin((at, foe.floorz), false);
                    foe.angle = camAngle + TURN[step];
                    foe.Vel = (0, 0, 0);
                }
                int shot = POSES[step] == "Death" ? 110 : 12;
                angle = camAngle;
                pitch = 0;
                Vel = (0, 0, 0);
                if (t == shot)
                {
                    Console.Printf("RF_ENEMYVIEW index=%%d label=%%s t=%%d class=%%s frame=%%d x=%%.0f y=%%.0f",
                        step + 1, LABELS[step], Level.maptime, foe ? foe.GetClassName() : 'none', foe ? foe.frame : -1,
                        foe ? foe.Pos.X : 0, foe ? foe.Pos.Y : 0);
                    Level.MakeScreenShot();
                }
                if (t >= shot + 4) { step++; phase = 0; }
            }
        }
        Super.PlayerThink();
    }
}

class RFTicStrip : EventHandler
{
    override void RenderOverlay(RenderEvent e)
    {
        int tic = Level.maptime;
        Screen.Clear(0, 0, 8 * 18 + 4, 12, Color(255, 0, 0, 0));
        Screen.Clear(2, 2, 10, 10, Color(255, 255, 0, 0));
        for (int i = 0; i < 16; i++)
        {
            Color c = (tic >> i) & 1 ? Color(255, 255, 255, 255) : Color(255, 0, 0, 0);
            Screen.Clear(2 + 8 * (i + 1), 2, 10 + 8 * (i + 1), 10, c);
        }
        Screen.Clear(2 + 8 * 17, 2, 10 + 8 * 17, 10, Color(255, 0, 255, 0));
    }
}
''' % (arr(0, True), arr(1, True), arr(2, False), arr(3, False), arr(4, False), len(views), x, y, ang, wait, cls)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ZSCRIPT.enemyviews', zs)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFEnemyViewPlayer"\n    AddEventHandlers = "RFTicStrip"\n}\n')
print('enemy views pk3', out, cls, len(views), 'views')
