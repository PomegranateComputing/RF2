// The three enemy families of RF01. Sprite families ORDY / BRCD / PREG are the
// eight-rotation sets recovered from legacy/import (rendered at 5 px per unit).

// Scripted wake-up without engine dormancy. A thing flagged DORMANT in the map waits for
// its cue (Thing_Activate from a wake line) but stays animated and vulnerable: being hit
// also wakes it. A cued enemy goes straight for the player who triggered it.
class RFEnemy : Actor
{
    Default { BloodType "RFArtBlood"; }
    bool awaitingCue;

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        if (bDormant)
        {
            bDormant = false;
            awaitingCue = true;
        }
    }

    override void Activate(Actor activator)
    {
        Super.Activate(activator);
        if (!awaitingCue || health <= 0) return;
        awaitingCue = false;
        if (activator != null && activator.player != null && activator.health > 0)
        {
            target = activator;
            A_StartSound(SeeSound, CHAN_VOICE);
            SetStateLabel("See");
        }
    }

    override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
    {
        awaitingCue = false;
        return Super.DamageMobj(inflictor, source, damage, mod, flags, angle);
    }

    // Spawn-state look: blind and deaf until cued.
    void RFLook()
    {
        if (!awaitingCue) A_Look();
    }
}

// Reinforcement point for waves that must not stand in view before their cue (finale).
// Thing_Activate on its tid spawns args[0] (1 orderly, 2 brancardier, 3 porte-registre)
// facing the spot angle and sends it after the activator. Placed out of the player's sight.
class RFWaveSpot : Actor
{
    Default
    {
        Radius 16;
        Height 56;
        +NOGRAVITY
        +NOBLOCKMAP
        +DONTSPLASH
    }

    override void Activate(Actor activator)
    {
        class<Actor> kind = 'RFOrderly';
        if (args[0] == 2) kind = 'RFBrancardier';
        else if (args[0] == 3) kind = 'RFPorteRegistre';
        let mo = Spawn(kind, Pos, ALLOW_REPLACE);
        if (mo != null)
        {
            mo.angle = angle;
            if (activator != null && activator.player != null && activator.health > 0)
            {
                mo.target = activator;
                mo.A_StartSound(mo.SeeSound, CHAN_VOICE);
                mo.SetStateLabel("See");
            }
        }
        Destroy();
    }

    States
    {
    Spawn:
        TNT1 A -1;
        Stop;
    }
}

// Orderly: close-range pressure. Its committed swing can be sidestepped.
class RFOrderly : RFEnemy
{
    double strikeAngle;

    Default
    {
        Health 60;
        Radius 18;
        Height 60;
        Mass 110;
        Speed 9;
        PainChance 130;
        MeleeRange 44;
        Monster;
        +FLOORCLIP
        Scale 0.18;
        SeeSound "rf/orderly/sight";
        PainSound "rf/orderly/pain";
        DeathSound "rf/orderly/death";
        ActiveSound "rf/orderly/active";
        Tag "$RF_MONSTER_ORDERLY";
        Obituary "$RF_OBIT_ORDERLY";
    }

    void BeginStrike()
    {
        A_FaceTarget();
        strikeAngle = angle;
        Vel.X = Vel.Y = 0;
        A_StartSound("rf/orderly/step", CHAN_BODY, 0, 0.9);
    }

    void Strike()
    {
        if (target == null || target.health <= 0) return;
        Vector2 difference = target.Pos.XY - Pos.XY;
        double along = difference.X * cos(strikeAngle) + difference.Y * sin(strikeAngle);
        if (along > difference.Length() * 0.65 && CheckMeleeRange() && CheckSight(target))
            A_CustomMeleeAttack(random(8, 14), "rf/orderly/attack", "", "Melee");
    }

    States
    {
    Spawn:
        ORDY A 10 RFLook;
        Loop;
    See:
        ORDY B 4 A_Chase;
        ORDY C 4 { A_Chase(); if (random(0, 2) == 0) A_StartSound("rf/orderly/step", CHAN_BODY, 0, 0.35); }
        ORDY D 4 A_Chase;
        ORDY E 4 { A_Chase(); if (random(0, 2) == 0) A_StartSound("rf/orderly/step", CHAN_BODY, 0, 0.35); }
        Loop;
    Melee:
        ORDY F 10 BeginStrike;
        ORDY G 4 Strike;
        ORDY H 14;
        Goto See;
    Pain:
        ORDY I 3;
        ORDY I 4 A_Pain;
        Goto See;
    Death:
        ORDY J 6 { Vel.X = Vel.Y = 0; A_Scream(); }
        ORDY K 7 A_NoBlocking;
        ORDY L 8 A_StartSound("rf/world/body_fall", CHAN_BODY, 0, 0.65);
        ORDY M -1 { RFBody.Settle(self, -30.5, 33.3, -19.4, 23.2); }
        Stop;
    }
}

// Decorative dead orderly (environmental storytelling), never a combatant.
class RFOrderlyCorpse : Actor
{
    Default
    {
        Radius 20;
        Height 8;
        Scale 0.18;
        +NOBLOCKMAP
        +FLOORCLIP
        -SOLID
    }
    States
    {
    Spawn:
        ORDY M -1 NoDelay { RFBody.Settle(self, -30.5, 33.3, -19.4, 23.2); }
        Stop;
    }
}

// Brancardier: audible brace, straight charge, recovery. Space to dodge is the counter.
class RFBrancardier : RFEnemy
{
    double chargeAngle;
    int chargeTics;
    bool chargeHit;

    Default
    {
        Health 170;
        Radius 40;
        Height 64;
        Mass 700;
        Speed 5;
        PainChance 40;
        MeleeRange 64;
        MinMissileChance 80;
        MaxTargetRange 640;
        Monster;
        +FLOORCLIP
        Scale 0.18;
        SeeSound "rf/brancardier/sight";
        PainSound "rf/brancardier/pain";
        DeathSound "rf/brancardier/death";
        ActiveSound "rf/brancardier/active";
        Tag "$RF_MONSTER_BRANCARDIER";
        Obituary "$RF_OBIT_BRANCARDIER";
    }

    void BeginBrace()
    {
        A_FaceTarget();
        chargeAngle = angle;
        chargeTics = 0;
        chargeHit = false;
        Vel.X = Vel.Y = 0;
        A_StartSound("rf/brancardier/brace", CHAN_VOICE, 0, 1.0);
    }

    void BeginCharge()
    {
        if (target == null || target.health <= 0 || !CheckSight(target))
        {
            SetStateLabel("Recovery");
            return;
        }
        chargeTics = 35;
        A_StartSound("rf/brancardier/wheel", CHAN_BODY, 0, 0.95);
    }

    bool ChargeCanHit()
    {
        if (chargeHit || target == null || target.health <= 0 || !CheckSight(target)) return false;
        Vector2 difference = target.Pos.XY - Pos.XY;
        double along = difference.X * cos(chargeAngle) + difference.Y * sin(chargeAngle);
        double across = abs(-difference.X * sin(chargeAngle) + difference.Y * cos(chargeAngle));
        return along >= 0 && along <= radius + target.radius + 12
            && across <= radius + target.radius - 8 && CheckMeleeRange();
    }

    void ChargeStep()
    {
        angle = chargeAngle;
        Vel.X = Vel.Y = 0;
        if (chargeTics-- <= 0)
        {
            SetStateLabel("Recovery");
            return;
        }
        if (ChargeCanHit())
        {
            chargeHit = true;
            A_CustomMeleeAttack(random(20, 28), "rf/brancardier/hit", "", "Melee");
            SetStateLabel("Impact");
            return;
        }
        if (!TryMove(Pos.XY + (cos(chargeAngle) * 11, sin(chargeAngle) * 11), 0))
        {
            A_StartSound("rf/brancardier/hit", CHAN_BODY, 0, 0.8);
            SetStateLabel("Impact");
        }
    }

    void BeginRecovery()
    {
        Vel.X = Vel.Y = 0;
        chargeTics = 0;
    }

    States
    {
    Spawn:
        BRCD A 10 RFLook;
        Loop;
    See:
        BRCD B 5 A_Chase;
        BRCD C 5 { A_Chase(); if (random(0, 3) == 0) A_StartSound("rf/brancardier/wheel", CHAN_BODY, 0, 0.3); }
        BRCD D 5 A_Chase;
        BRCD E 5 A_Chase;
        Loop;
    Melee:
    Missile:
        BRCD F 24 BeginBrace;
        BRCD G 1 BeginCharge;
    Charge:
        BRCD G 2 ChargeStep;
        BRCD N 2 ChargeStep;
        Loop;
    Impact:
        BRCD O 8 BeginRecovery;
    Recovery:
        BRCD H 28 BeginRecovery;
        Goto See;
    Pain:
        BRCD I 8 { BeginRecovery(); A_Pain(); }
        Goto See;
    Death:
        BRCD J 7 { BeginRecovery(); A_Scream(); }
        BRCD K 8 A_NoBlocking;
        BRCD L 10 A_StartSound("rf/world/body_fall", CHAN_BODY, 0, 0.8);
        BRCD M -1 { RFBody.Settle(self, -49.1, 33.3, -47.3, 13.7); }
        Stop;
    }
}

// Porte-Registre: medium-range control. Visible windup, physical thrown bundle.
class RFRegistryBundle : Actor
{
    Default
    {
        Radius 6;
        Height 8;
        Speed 20;
        // 9 per hit, as declared. "Damage 9" means 9 x 1d8 (9-72) for a projectile: once the throw
        // was aimed (it used to miss), a bundle took 71 health at once in run B, above the
        // brancardier's charge (20-28). The family's scale is the melee range 8-14 / 20-28.
        DamageFunction 9;
        Gravity 0.35;
        Projectile;
        -NOGRAVITY
        Scale 0.9;
        SeeSound "rf/porte/throw";
    }
    States
    {
    Spawn:
        PRGS A 3;
        PRGS B 3;
        Loop;
    Death:
        PRGS A 6;
        Stop;
    }
}

class RFPorteRegistre : RFEnemy
{
    int boxedTics;

    Default
    {
        Health 110;
        Radius 22;
        Height 70;
        Mass 150;
        Speed 4;
        PainChance 90;
        MaxTargetRange 700;
        MinMissileChance 90;
        Monster;
        +FLOORCLIP
        Scale 0.18;
        SeeSound "rf/porte/alert";
        PainSound "rf/porte/pain";
        DeathSound "rf/porte/death";
        Tag "$RF_MONSTER_PORTE";
        Obituary "$RF_OBIT_PORTE";
    }

    // A_Chase tries a throw only when its move counter is zero, which never happens while every
    // move fails: boxed in by the player on a narrow stair, the porte-registre stood there
    // harmless. After about a second without moving, with its target in sight, it throws anyway.
    void PorteChase()
    {
        Vector2 before = Pos.XY;
        A_Chase();
        if (!InStateSequence(CurState, ResolveState("See")) || (Pos.XY - before).Length() > 0.01)
        {
            boxedTics = 0;
            return;
        }
        if (++boxedTics >= 6 && target != null && target.health > 0 && CheckSight(target))
        {
            boxedTics = 0;
            SetStateLabel("Missile");
        }
    }

    void PrepareVolley()
    {
        A_FaceTarget();
        Vel.X = Vel.Y = 0;
        A_StartSound("rf/porte/telegraph", CHAN_VOICE, 0, 0.9);
    }

    void ThrowBundle()
    {
        if (target == null || target.health <= 0 || !CheckSight(target)) return;
        A_FaceTarget();
        // A lobbed bundle: the arc is aimed at the target, so it lands at any range or height.
        A_SpawnProjectile("RFRegistryBundle", 48, 0, 0, CMF_AIMDIRECTION | CMF_ABSOLUTEPITCH, LobPitch(target, 48));
    }

    // Launch pitch (negative = up) of the low arc that brings the bundle onto the target's chest.
    // A fixed pitch landed at one distance only and flew over a player standing close below.
    double LobPitch(Actor t, double spawnHeight)
    {
        let bundle = GetDefaultByType('RFRegistryBundle');
        double v = bundle.Speed;
        double g = bundle.Gravity * Level.Gravity * CurSector.gravity * 0.00125;   // per tic squared
        double d = max(Distance2D(t), 1);
        double h = (t.pos.z + t.height * 0.5) - (pos.z + spawnHeight);
        if (g < 1e-6) return -atan2(h, d);
        double a = g * d * d / (2 * v * v);
        double disc = d * d - 4 * a * (a + h);
        if (disc < 0) return -45;                                                  // out of reach
        return -atan((d - sqrt(disc)) / (2 * a));
    }

    States
    {
    Spawn:
        PREG A 8 RFLook;
        Loop;
    See:
        PREG B 5 PorteChase;
        PREG C 5 PorteChase;
        PREG D 5 PorteChase;
        PREG E 5 PorteChase;
        Loop;
    Missile:
        PREG F 26 PrepareVolley;
        PREG G 2 ThrowBundle;
        PREG N 12;
        Goto See;
    Pain:
        PREG H 5 A_Pain;
        Goto See;
    Death:
        PREG I 7 A_Scream;
        PREG J 7 { A_NoBlocking(); A_StartSound("rf/world/body_fall", CHAN_BODY, 0, 0.65); }
        PREG K -1 { RFBody.Settle(self, -31.3, 37.9, -19.2, 23.6); }
        Stop;
    }
}

// Same engine blood physics; original smooth sprites replace the low-resolution IWAD family.
class RFArtBlood : Blood
{
    Default { Scale 0.12; }
    States
    {
    Spawn:
        RFBX ABC 8;
        Stop;
    Spray:
        RFBX ABC 6;
        Stop;
    }
}

// Terminal pose of a body drawn by a static model (MODELDEF, USEACTORPITCH/ROLL). A rigid model
// laid flat cuts into steps and walls: once, when the final frame starts, the body turns away
// from a wall its length would cross, then tilts along the floor under it so that it rests on
// the step edges. Extents are the model's footprint (units, t forward = feet, s to the left).
// Collisions are untouched: the body is already non-solid; its radius only decides the floor
// under it (floorz), so it shrinks to the centre, and the pose is then held (no gravity).
class RFBody play
{
    // An edge a body cannot lie across: a wall, a rise over 24 units in one edge (a table, a
    // counter; a stair step is 16), or a gap too low (a closed door).
    static bool EdgeBlocks(Line l)
    {
        if (l.backsector == null) return true;
        Vector2 mid = (l.v1.p + l.v2.p) / 2;
        double fa = l.frontsector.floorplane.ZAtPoint(mid), fb = l.backsector.floorplane.ZAtPoint(mid);
        double ca = l.frontsector.ceilingplane.ZAtPoint(mid), cb = l.backsector.ceilingplane.ZAtPoint(mid);
        return abs(fa - fb) > 24 || min(ca, cb) - max(fa, fb) < 16;
    }

    static bool Crosses(Vector2 a, Vector2 b, double tmin, double tmax, double smin, double smax)
    {
        // Liang-Barsky: does segment a-b (body coordinates) enter the footprint rectangle?
        double u0 = 0, u1 = 1;
        double dx = b.X - a.X, dy = b.Y - a.Y;
        double p[4], q[4];
        p[0] = -dx; q[0] = a.X - tmin;
        p[1] = dx;  q[1] = tmax - a.X;
        p[2] = -dy; q[2] = a.Y - smin;
        p[3] = dy;  q[3] = smax - a.Y;
        for (int i = 0; i < 4; i++)
        {
            if (abs(p[i]) < 1e-9)
            {
                if (q[i] < 0) return false;
                continue;
            }
            double r = q[i] / p[i];
            if (p[i] < 0) { if (r > u1) return false; if (r > u0) u0 = r; }
            else { if (r < u0) return false; if (r < u1) u1 = r; }
        }
        return u0 <= u1;
    }

    // Obstacles the footprint crosses at this heading: walls, ledges over 24 units, closed doors.
    static int Obstacles(Actor body, double ang, double floor, double tmin, double tmax, double smin, double smax)
    {
        int count = 0;
        Vector2 fwd = (cos(ang), sin(ang)), left = (-sin(ang), cos(ang));
        let it = BlockLinesIterator.Create(body, 96);
        while (it.Next())
        {
            Line l = it.CurLine;
            bool blocks = l.backsector == null;
            if (!blocks)
            {
                blocks = EdgeBlocks(l);
            }
            if (!blocks) continue;
            Vector2 a = l.v1.p - body.Pos.XY, b = l.v2.p - body.Pos.XY;
            Vector2 la = (a dot fwd, a dot left), lb = (b dot fwd, b dot left);
            if (Crosses(la, lb, tmin + 2, tmax - 2, smin + 2, smax - 2)) count++;
        }
        return count;
    }

    // Lowest line resting on every sample (upper support): returns slope and height at 0.
    static double, double Support(Array<double> at, Array<double> z)
    {
        double bestM = 0, bestC = -1e9;
        for (int i = 0; i < z.Size(); i++) bestC = max(bestC, z[i]);   // flat on the highest point
        for (int i = 0; i < z.Size(); i++)
        {
            for (int j = i + 1; j < z.Size(); j++)
            {
                if (abs(at[j] - at[i]) < 1) continue;
                double m = (z[j] - z[i]) / (at[j] - at[i]);
                double c = z[i] - m * at[i];
                bool valid = true;
                for (int k = 0; k < z.Size() && valid; k++) valid = z[k] <= c + m * at[k] + 0.01;
                if (valid && c < bestC - 0.01) { bestC = c; bestM = m; }
            }
        }
        return bestM, bestC;
    }

    static double FloorAt(Vector2 p)
    {
        return Level.PointInSector(p).floorplane.ZAtPoint(p);
    }

    // Does the move from a to b cross a wall, a ledge or a closed door?
    static bool Blocked(Actor body, Vector2 a, Vector2 b, double floor)
    {
        let it = BlockLinesIterator.Create(body, 128);
        while (it.Next())
        {
            Line l = it.CurLine;
            bool blocks = l.backsector == null;
            if (!blocks)
            {
                blocks = EdgeBlocks(l);
            }
            if (!blocks) continue;
            // Segment intersection a-b / v1-v2.
            Vector2 r = b - a, q = l.v2.p - l.v1.p;
            double den = r.X * q.Y - r.Y * q.X;
            if (abs(den) < 1e-9) continue;
            Vector2 w = l.v1.p - a;
            double u = (w.X * q.Y - w.Y * q.X) / den, v = (w.X * r.Y - w.Y * r.X) / den;
            if (u >= 0 && u <= 1 && v >= 0 && v <= 1) return true;
        }
        return false;
    }

    // Floor under the footprint on a 9 x 5 grid (t along, s across). A point behind a blocking
    // edge (table, counter) is not a support: the body lies beside the furniture.
    static void Grid(Actor body, Vector2 pos, double ang, double tmin, double tmax, double smin, double smax, double floor,
        out Array<double> gt, out Array<double> gs, out Array<double> gz)
    {
        gt.Clear(); gs.Clear(); gz.Clear();
        Vector2 fwd = (cos(ang), sin(ang)), left = (-sin(ang), cos(ang));
        for (int i = 0; i <= 8; i++)
        {
            for (int j = 0; j <= 4; j++)
            {
                double t = tmin + (tmax - tmin) * i / 8.0, sv = smin + (smax - smin) * j / 4.0;
                Vector2 pnt = pos + fwd * t + left * sv;
                gt.Push(t); gs.Push(sv);
                gz.Push(Blocked(body, pos, pnt, floor) ? floor : FloorAt(pnt));
            }
        }
    }

    // Lowest plane z = c + mt t + ms s resting on the grid: slope along the body, then across it
    // once the along slope is removed, each capped at 45 degrees; c puts the plane on the samples.
    static double, double, double Plane(Array<double> gt, Array<double> gs, Array<double> gz)
    {
        Array<double> at, az, bs, bz;
        for (int i = 0; i <= 8; i++)
        {
            double m = -1e9;
            for (int j = 0; j <= 4; j++) m = max(m, gz[i * 5 + j]);
            at.Push(gt[i * 5]); az.Push(m);
        }
        double mt, c0;
        [mt, c0] = Support(at, az);
        double cap = tan(45);
        mt = clamp(mt, -cap, cap);
        for (int j = 0; j <= 4; j++)
        {
            double m = -1e9;
            for (int i = 0; i <= 8; i++) m = max(m, gz[i * 5 + j] - mt * gt[i * 5 + j]);
            bs.Push(gs[j]); bz.Push(m);
        }
        double ms, c1;
        [ms, c1] = Support(bs, bz);
        ms = clamp(ms, -cap, cap);
        double c = -1e9;
        for (int k = 0; k < gz.Size(); k++) c = max(c, gz[k] - mt * gt[k] - ms * gs[k]);
        return mt, ms, c;
    }

    // A candidate pose: obstacles crossed first, then how steep the resting tilt is (along the
    // body is a slope; across it as well is a twisted pose, counted double).
    static double, double, double, double Evaluate(Actor body, Vector2 pos, double ang, double tmin, double tmax,
        double smin, double smax)
    {
        Vector2 keep = body.Pos.XY;
        body.SetOrigin((pos, body.Pos.Z), false);
        double floor = FloorAt(pos);
        int n = Obstacles(body, ang, floor, tmin, tmax, smin, smax);
        Array<double> gt, gs, gz;
        Grid(body, pos, ang, tmin, tmax, smin, smax, floor, gt, gs, gz);
        double mt, ms, c;
        [mt, ms, c] = Plane(gt, gs, gz);
        body.SetOrigin((keep, body.Pos.Z), false);
        double pa = abs(atan(mt)), ra = abs(atan(ms));
        return 1000 * n + max(pa, ra) + 2 * min(pa, ra), mt, ms, c;
    }

    static void Settle(Actor body, double tmin, double tmax, double smin, double smax)
    {
        if (body == null) return;
        Vector2 home = body.Pos.XY;
        double homeFloor = FloorAt(home);
        Vector2 bestPos = home;
        double bestAng = body.angle;
        double best, mt, ms, c;
        [best, mt, ms, c] = Evaluate(body, home, body.angle, tmin, tmax, smin, smax);
        // The pose where it fell, unless it crosses an obstacle or has to tilt over 12 degrees:
        // then the best of 8 headings and small shifts (12 or 24 units, never across a wall),
        // a change costing a little so that the smallest adequate one wins.
        if (best > 12)
        {
            for (int ring = 0; ring <= 2; ring++)
            {
                for (int dir = 0; dir < (ring == 0 ? 1 : 8); dir++)
                {
                    Vector2 pos = home + (cos(dir * 45), sin(dir * 45)) * (ring * 12);
                    if (ring > 0 && (Blocked(body, home, pos, homeFloor) || abs(FloorAt(pos) - homeFloor) > 24)) continue;
                    for (int k = 0; k < 8; k++)
                    {
                        if (ring == 0 && k == 0) continue;
                        double ang = body.angle + k * 45;
                        double cost, m1, m2, c1;
                        [cost, m1, m2, c1] = Evaluate(body, pos, ang, tmin, tmax, smin, smax);
                        cost += ring * 3 + (k == 0 ? 0 : 1);
                        if (cost < best) { best = cost; bestPos = pos; bestAng = ang; mt = m1; ms = m2; c = c1; }
                    }
                }
            }
        }
        body.SetOrigin((bestPos, body.Pos.Z), false);
        body.angle = bestAng;
        body.A_SetSize(4, -1);
        body.bNoGravity = true;
        body.Vel = (0, 0, 0);
        body.pitch = -atan(mt);
        body.roll = atan(ms);
        body.SetZ(c);
    }
}
