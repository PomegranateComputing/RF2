#!/usr/bin/env python3
"""Engine audit of the props of a map: what floats, what sinks, what stands in a wall, what lacks a support.

A separate test pk3 (loaded after the build): at tic 40 its player class walks the thinker list and prints, for
every visible non-monster actor (props, models, figures, pickups, litter, lamps, signs drawn as actors):
  RF_AUDIT class x y z dz=<z - floor under the centre> floor_min/floor_max under 8 points of the footprint
           r=<radius> h=<height> vis=<half width of the drawn sprite, world units> wall=<distance to the nearest
           wall line> solid nograv model
"wall" is the distance from the centre to the nearest one-sided line or two-sided line whose other side is closed or
much higher/lower (a step of more than 24 u). Models: the footprint radius is the actor radius (the model's own
extent is checked on the close-up views). The build is not modified.

Usage: python scripts/production/prop_audit_pk3.py out.pk3
       python scripts/devrun.py --pk3 <build.pk3> --map RF02 --name audit_rf02 --seconds 60 --marker RF_DEV_UI_DONE -- -file out.pk3
"""
import sys, zipfile

ZS = r'''version "4.14"
class RFAuditPlayer : RFPlayer
{
    bool done;
    override void PlayerThink()
    {
        if (player != null)
        {
            player.cheats |= CF_NOTARGET | CF_GODMODE;
            player.cmd.buttons = 0; player.cmd.forwardmove = 0; player.cmd.sidemove = 0;
            if (!done && Level.maptime >= 40)
            {
                done = true;
                Audit();
                Console.Printf("RF_DEV_UI_DONE");
            }
        }
        Super.PlayerThink();
    }

    static bool Skip(Actor a)
    {
        if (a.bIsMonster || a.player != null) return true;
        String c = a.GetClassName();
        if (c.IndexOf("Waypoint") >= 0 || c.IndexOf("TourPoint") >= 0 || c.IndexOf("WaveSpot") >= 0) return true;
        if (c.IndexOf("Ambient") >= 0 || c.IndexOf("SceneSpot") >= 0 || c.IndexOf("Signal") >= 0) return true;
        if (c.IndexOf("Puff") >= 0 || c.IndexOf("Blood") >= 0 || c.IndexOf("Decal") >= 0) return true;
        if (a is 'Inventory' && Inventory(a).Owner != null) return true;
        return false;
    }

    // Distance from p to the nearest line that bounds the walkable space (wall, or a step the actor cannot stand across).
    static double WallDistance(Actor a, out double wallAngle)
    {
        double best = 1e9;
        wallAngle = 0;
        let it = BlockLinesIterator.Create(a, 160);
        while (it.Next())
        {
            Line l = it.CurLine;
            bool wall = l.backsector == null || (l.flags & (Line.ML_BLOCKING | Line.ML_BLOCKEVERYTHING));
            if (!wall)
            {
                double f1 = l.frontsector.floorplane.ZAtPoint(a.Pos.XY), f2 = l.backsector.floorplane.ZAtPoint(a.Pos.XY);
                double c1 = l.frontsector.ceilingplane.ZAtPoint(a.Pos.XY), c2 = l.backsector.ceilingplane.ZAtPoint(a.Pos.XY);
                if (abs(f1 - f2) > 24 || min(c1, c2) - max(f1, f2) < 8) wall = true;
            }
            if (!wall) continue;
            Vector2 v1 = l.v1.p, v2 = l.v2.p, d = v2 - v1, p = a.Pos.XY;
            double len2 = d dot d;
            double t = len2 > 0 ? clamp(((p - v1) dot d) / len2, 0, 1) : 0;
            Vector2 q = v1 + d * t;
            double dist = (p - q).Length();
            if (dist < best) { best = dist; wallAngle = atan2(q.y - p.y, q.x - p.x); }
        }
        return best;
    }

    void Audit()
    {
        let it = ThinkerIterator.Create('Actor');
        Actor a;
        int n = 0;
        while ((a = Actor(it.Next())) != null)
        {
            if (a == self || Skip(a)) continue;
            bool hasSprite = a.sprite != GetSpriteIndex('TNT1');
            if (!hasSprite && a.bInvisible) continue;
            double floorC = a.GetZAt(a.Pos.X, a.Pos.Y, 0, GZF_ABSOLUTEPOS | GZF_ABSOLUTEANG);
            double fmin = 1e9, fmax = -1e9;
            double r = max(a.radius, 4);
            for (int k = 0; k < 8; k++)
            {
                double ang = k * 45;
                double fz = a.GetZAt(a.Pos.X + cos(ang) * r, a.Pos.Y + sin(ang) * r, 0, GZF_ABSOLUTEPOS | GZF_ABSOLUTEANG);
                fmin = min(fmin, fz); fmax = max(fmax, fz);
            }
            double vis = 0;
            if (hasSprite && a.CurState != null)
            {
                TextureID tex = a.CurState.GetSpriteTexture(0);
                if (tex.IsValid())
                {
                    Vector2 size = TexMan.GetScaledSize(tex);
                    vis = size.X * a.Scale.X * 0.5;
                }
            }
            double wa;
            double wall = WallDistance(a, wa);
            Console.Printf("RF_AUDIT class=%s x=%.0f y=%.0f z=%.1f dz=%.1f fmin=%.1f fmax=%.1f r=%.0f h=%.0f vis=%.1f wall=%.1f wallang=%.0f ang=%.0f solid=%d nograv=%d",
                a.GetClassName(), a.Pos.X, a.Pos.Y, a.Pos.Z, a.Pos.Z - floorC, fmin - floorC, fmax - floorC, a.radius, a.height, vis,
                wall > 1e8 ? -1 : wall, wa, a.angle, a.bSolid, a.bNoGravity);
            n++;
        }
        Console.Printf("RF_AUDIT_COUNT %d", n);
    }
}
'''

with zipfile.ZipFile(sys.argv[1], 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ZSCRIPT.propaudit', ZS)
    z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFAuditPlayer"\n}\n')
print('prop audit pk3', sys.argv[1])
