"""RF01 register check (mandate of 27/09 evening). A separate test pk3, loaded after the build under test, stands the
player at given spots of RF01, presses use once through the player's own think (as the development autopilot does)
and reports what the press did: notes read (RFDirector.notesRead, objective) and the opening of the start chamber
door. The player class is a test subclass of RFPlayer declared only in the test pk3; the build itself is unchanged.
Controls: the chamber door (tag 21) and the chapel note 4.

Usage: python scripts/production/rf01_register_check_pk3.py <out.pk3>
       python scripts/devrun.py --pk3 <build.pk3> --map RF01 --name register --seconds 150 --marker RF_DEV_UI_DONE -- -file <out.pk3>
Result lines: RF_USETEST step=... notes read N, objective '...', chamber door opening H
"""
import sys, zipfile
out = sys.argv[1]
POS = [('door_chamber', -544, -500, 0, 90),
       ('note4_chapel_nave', -548, 416, 0, 180),
       ('note4_chapel_dais', -566, 390, 16, 110),
       ('register_1', -80, 745, 32, 90), ('register_2', -80, 752, 32, 90), ('register_3', -60, 742, 32, 105),
       ('register_4', -104, 744, 32, 72), ('register_5', -80, 730, 32, 90),
       ('duty_register_counter', 320, -290, 0, 270)]
zs = '''version "4.14"
class RFUseTestPlayer : RFPlayer
{
    int step;
    int phase;
    int readBefore;
    override void PlayerThink()
    {
        static const double PX[] = { %s };
        static const double PY[] = { %s };
        static const double PZ[] = { %s };
        static const double PA[] = { %s };
        int n = %d;
        let dir = RFDirector(EventHandler.Find('RFDirector'));
        if (dir != null && Level.maptime >= 35)
        {
            if (step >= n) { if (phase++ == 0) Console.Printf("RF_DEV_UI_DONE"); }
            else
            {
                int t = phase++;
                if (t == 0)
                {
                    SetOrigin((PX[step], PY[step], PZ[step]), false);
                    angle = PA[step];
                    pitch = 0;
                    Vel = (0, 0, 0);
                    readBefore = dir.notesRead;
                }
                player.cmd.buttons &= ~BT_USE;
                if (t == 10) player.cmd.buttons |= BT_USE;
                if (t == 60)
                {
                    Sector door = Level.PointInSector((-544, -440));
                    Console.Printf("RF_USETEST step=%%d at %%.0f %%.0f z %%.0f angle %%.0f: notes read %%d, objective '%%s', chamber door opening %%.0f",
                        step + 1, Pos.X, Pos.Y, Pos.Z, PA[step], dir.notesRead - readBefore, dir.objective, door.CenterCeiling() - door.CenterFloor());
                    step++;
                    phase = 0;
                }
            }
        }
        Super.PlayerThink();
    }
}
''' % (', '.join(str(p[1]) for p in POS), ', '.join(str(p[2]) for p in POS), ', '.join(str(p[3]) for p in POS),
       ', '.join(str(p[4]) for p in POS), len(POS))
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ZSCRIPT.usetest', zs)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFUseTestPlayer"\n}\n')
print('usetest pk3', out, [p[0] for p in POS])
