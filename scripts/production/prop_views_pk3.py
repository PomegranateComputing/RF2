#!/usr/bin/env python3
"""Automatic close-up of every prop of a map, to look at its placement (support, wall, scale, alignment).

A separate test pk3: at tic 40 the player class lists the visible non-monster actors (same filter as
prop_audit_pk3.py, litter and pickups optional), then for each one: from the prop, a trace at mid-height in 16
directions finds the most open side; the camera stands there at DIST units (or less if a wall is closer), eye at
CAM_Z above the floor, and looks at the prop's mid-height. One screenshot per prop, RF_PROPVIEW index/class/x/y/t
logged before it (tic strip in the corner, read back by capture tools).

Usage: python scripts/production/prop_views_pk3.py out.pk3 [--dist 96] [--litter] [--pickups] [--only Class1,Class2]
       python scripts/devrun.py --pk3 <build.pk3> --map RF02 --name pv_rf02 --seconds 300 --marker RF_DEV_UI_DONE -- -file out.pk3
"""
import argparse, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--dist', type=float, default=96)
ap.add_argument('--litter', action='store_true')
ap.add_argument('--pickups', action='store_true')
ap.add_argument('--only', default='')
a = ap.parse_args()
only = [c for c in a.only.split(',') if c]

ZS = r'''version "4.14"
class RFPropViewPlayer : RFPlayer
{
    Array<Actor> props;
    int step, phase;
    bool listed;
    Vector3 camPos;
    double camAngle, camPitch;

    bool Wanted(Actor a)
    {
        if (a == self || a.bIsMonster || a.player != null) return false;
        String c = a.GetClassName();
        static const String SKIP[] = { "Waypoint", "TourPoint", "WaveSpot", "Ambient", "SceneSpot", "Signal", "Puff", "Blood", "Decal", "SoundEnvironment", "Mirror" };
        for (int i = 0; i < SKIP.Size(); i++) if (c.IndexOf(SKIP[i]) >= 0) return false;
        if (a is 'Inventory') { if (Inventory(a).Owner != null) return false; if (!%(pickups)s && !(a is 'RFNote')) return false; }
        if (!%(litter)s && c.IndexOf("Litter") >= 0) return false;
        if (a.sprite == GetSpriteIndex('TNT1') && a.bInvisible) return false;
        %(only)s
        return true;
    }

    void ListProps()
    {
        let it = ThinkerIterator.Create('Actor');
        Actor a;
        while ((a = Actor(it.Next())) != null) if (Wanted(a)) props.Push(a);
        Console.Printf("RF_PROPVIEW_COUNT %%d", props.Size());
    }

    void PlaceCamera(Actor p)
    {
        double mid = p.Pos.Z + max(p.height, 16) * 0.5;
        // The side the prop faces when it is open enough (figures and props are drawn from the front), else the most
        // open side: 16 traces at mid-height; a side is "open" from 64 u.
        double bestD = -1, bestA = 0, frontD = -1, frontA = 0, frontGap = 999;
        FLineTraceData d;
        for (int k = 0; k < 16; k++)
        {
            double ang = k * 22.5;
            p.LineTrace(ang, %(dist)f + 32, 0, TRF_THRUACTORS, max(p.height, 16) * 0.5, 0, 0, d);
            double free = d.HitType == TRACE_HitNone ? %(dist)f + 32 : d.Distance;
            if (free > bestD) { bestD = free; bestA = ang; }
            double gap = abs(DeltaAngle(ang, p.angle));
            if (free >= 64 && gap < frontGap) { frontGap = gap; frontD = free; frontA = ang; }
        }
        if (frontD > 0 && frontGap <= 90) { bestD = frontD; bestA = frontA; }
        double cd = clamp(bestD - 12, 24, %(dist)f);
        Vector2 xy = p.Pos.XY + (cos(bestA), sin(bestA)) * cd;
        double fz = GetZAt(xy.X, xy.Y, 0, GZF_ABSOLUTEPOS | GZF_ABSOLUTEANG);
        camPos = (xy, fz);
        camAngle = bestA + 180;
        double eye = fz + player.viewheight;
        camPitch = clamp(-atan2(mid - eye, cd), -60, 60);
    }

    override void PlayerThink()
    {
        if (player != null)
        {
            player.cheats |= CF_NOCLIP | CF_GODMODE | CF_NOTARGET;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            if (Level.maptime >= 210)        // after the chapter's title card
            {
                if (!listed)
                {
                    listed = true;
                    ListProps();
                    let it = ThinkerIterator.Create('Actor');
                    Actor m;
                    while ((m = Actor(it.Next())) != null) if (m.bIsMonster) { m.A_SetRenderStyle(0, STYLE_None); m.bDormant = true; }
                }
                if (step >= props.Size()) { if (phase++ == 0) Console.Printf("RF_DEV_UI_DONE"); }
                else
                {
                    int t = phase++;
                    Actor p = props[step];
                    if (t == 0 && p != null) PlaceCamera(p);
                    SetOrigin(camPos, false);
                    angle = camAngle; pitch = camPitch; Vel = (0, 0, 0);
                    if (t == 10)
                    {
                        Console.Printf("RF_PROPVIEW index=%%d class=%%s x=%%.0f y=%%.0f t=%%d", step + 1, p ? p.GetClassName() : 'none', p ? p.Pos.X : 0, p ? p.Pos.Y : 0, Level.maptime);
                        Level.MakeScreenShot();
                    }
                    if (t >= 14) { step++; phase = 0; }
                }
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
'''
only_code = ''
if only:
    only_code = 'static const String ONLY[] = { %s }; bool keep = false; for (int i = 0; i < ONLY.Size(); i++) if (c == ONLY[i]) keep = true; if (!keep) return false;' % ', '.join('"%s"' % o for o in only)
zs = ZS % dict(dist=a.dist, litter='true' if a.litter else 'false', pickups='true' if a.pickups else 'false', only=only_code)
with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ZSCRIPT.propviews', zs)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFPropViewPlayer"\n    AddEventHandlers = "RFTicStrip"\n}\n')
print('prop views pk3', a.out)
