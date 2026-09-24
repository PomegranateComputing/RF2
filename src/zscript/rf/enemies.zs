// The three enemy families of RF01. Sprite families ORDY / BRCD / PREG are the
// eight-rotation sets recovered from legacy/import (rendered at 5 px per unit).

// Orderly: close-range pressure. Its committed swing can be sidestepped.
class RFOrderly : Actor
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
        ORDY A 10 A_Look;
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
        ORDY L 8;
        ORDY M -1;
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
        ORDY M -1;
        Stop;
    }
}

// Brancardier: audible brace, straight charge, recovery. Space to dodge is the counter.
class RFBrancardier : Actor
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
        BRCD A 10 A_Look;
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
        BRCD L 10;
        BRCD M -1;
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
        Damage 9;
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

class RFPorteRegistre : Actor
{
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
        // A lobbed bundle: slight upward pitch so it arcs under gravity.
        A_SpawnProjectile("RFRegistryBundle", 48, 0, 0, CMF_AIMDIRECTION | CMF_ABSOLUTEPITCH, -6);
    }

    States
    {
    Spawn:
        PREG A 8 A_Look;
        Loop;
    See:
        PREG B 5 A_Chase;
        PREG C 5 A_Chase;
        PREG D 5 A_Chase;
        PREG E 5 A_Chase;
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
        PREG J 7 A_NoBlocking;
        PREG K -1;
        Stop;
    }
}
