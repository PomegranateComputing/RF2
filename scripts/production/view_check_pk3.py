#!/usr/bin/env python3
"""Control views on any build, the accepted one included: a separate test pk3 (loaded after the build) whose player
class, a subclass of RFPlayer declared only in the test pk3, visits a list of views and takes one screenshot each.
The build under test is not modified.

views.json: [[label, x, y, z_above_floor, angle, pitch(, door_tag)], ...]   (pitch negative = looking up)
door_tag: optional; the door sectors with that tag are opened (Door_Open, fast) before the view is taken.
Usage: python scripts/production/view_check_pk3.py views.json out.pk3 [wait_tics] [hide]
       python scripts/devrun.py --pk3 <build.pk3> --map RF01 --name <name> --seconds 300 --marker RF_DEV_UI_DONE -- -file out.pk3
hide: monsters and shootable characters are made invisible (not removed) before the first view, so that none of
them stands between a camera and what it checks; say so wherever the views are shown.
Each view prints RF_VIEWCHECK index=... label=... before its screenshot.
"""
import json, sys, zipfile

views = json.load(open(sys.argv[1], encoding='utf-8'))
out = sys.argv[2]
wait = int(sys.argv[3]) if len(sys.argv) > 3 else 180          # after the level title card
hide = 'true' if len(sys.argv) > 4 and sys.argv[4] == 'hide' else 'false'
labels = ', '.join('"%s"' % v[0].replace('"', "'") for v in views)
cols = [', '.join(str(float(v[i])) for v in views) for i in range(1, 6)]
doors = ', '.join(str(int(v[6]) if len(v) > 6 else 0) for v in views)
zs = '''version "4.14"
class RFViewCheckPlayer : RFPlayer
{
    int step, phase;
    bool hidden;
    override void PlayerThink()
    {
        static const String LABELS[] = { %s };
        static const double VX[] = { %s };
        static const double VY[] = { %s };
        static const double VZ[] = { %s };
        static const double VA[] = { %s };
        static const double VP[] = { %s };
        static const int VO[] = { %s };
        int n = %d;
        if (player != null && Level.maptime >= %d)
        {
            player.cheats |= CF_NOCLIP | CF_GODMODE;
            player.cmd.buttons = 0;
            player.cmd.forwardmove = 0;
            player.cmd.sidemove = 0;
            if (%s && !hidden)
            {
                hidden = true;
                let it = ThinkerIterator.Create("Actor");
                Actor a;
                while ((a = Actor(it.Next())) != null)
                    if (a != self && (a.bIsMonster || a.bShootable))
                        a.A_SetRenderStyle(0, STYLE_None);
            }
            if (step >= n) { if (phase++ == 0) Console.Printf("RF_DEV_UI_DONE"); }
            else
            {
                int t = phase++;
                if (t == 0)
                {
                    Vector2 at = (VX[step], VY[step]);
                    double floor = Level.PointInSector(at).floorplane.ZAtPoint(at);
                    SetOrigin((at, floor + VZ[step]), false);
                    if (VO[step] > 0)
                        Level.ExecuteSpecial(11, self, null, false, VO[step], 64);     // Door_Open
                }
                int shot = VO[step] > 0 ? 48 : 12;
                angle = VA[step];
                pitch = VP[step];
                Vel = (0, 0, 0);
                if (t == shot)
                {
                    Console.Printf("RF_VIEWCHECK index=%%d label=%%s", step + 1, LABELS[step]);
                    Level.MakeScreenShot();
                }
                if (t >= shot + 4) { step++; phase = 0; }
            }
        }
        Super.PlayerThink();
    }
}
''' % (labels, cols[0], cols[1], cols[2], cols[3], cols[4], doors, len(views), wait, hide)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ZSCRIPT.viewcheck', zs)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFViewCheckPlayer"\n}\n')
print('view check pk3', out, len(views), 'views', 'hide' if hide == 'true' else '')
