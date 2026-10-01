// RF02 figures (Astra, batch RF2_MAP_02_REPRISE, 28/09/2026): the people of the street and of the scenes (novel,
// ch. RF02; contract docs/production/handoff/RF2-MAP-02-REPRISE/CONTRAT.md, section 5). Visual only: no collision,
// never hostile, not usable. Sprites in sprites/rf02_figures, 8 rotations, Scale 0.18 as the enemies, grAb at the
// soles (Astra's manifest). Placed by scripts/mapkit/rf02.py.

class RFFigure : Actor
{
    Default
    {
        Scale 0.18;
        Radius 12;
        Height 56;
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
        +DONTSPLASH
    }
}

class RFFigureForms : RFFigure       // F02-01: the uniform feeding the forms to the fire, slowly (l. 87)
{
    Default { Height 66; }
    States { Spawn: R2F1 A 20; R2F1 B 16; R2F1 C 12; R2F1 B 16; Loop; }
}

class RFFigurePram : RFFigure        // F02-02: the woman behind the pram of registers; Walk waits for the pram model
{
    Default { Height 64; }
    States
    {
    Spawn: R2F2 A -1; Stop;
    Walk: R2F2 ABCD 7; Loop;
    }
}

class RFFigureSanteA : RFFigure { Default { Height 62; } States { Spawn: R2B1 A -1; Stop; } }   // F02-03: the group at
class RFFigureSanteB : RFFigure { Default { Height 64; } States { Spawn: R2B2 A -1; Stop; } }   // the Sante gate, four
class RFFigureSanteC : RFFigure { Default { Height 64; } States { Spawn: R2B3 A -1; Stop; } }   // figures (the child
class RFFigureSanteD : RFFigure { Default { Height 44; } States { Spawn: R2B4 A -1; Stop; } }   // is R2B4)

class RFFigureTram : RFFigure        // F02-04: the old man asleep on the rear platform; his eyes open when Viktor is near
{
    Default { Height 44; }
    States
    {
    Spawn: R2F4 A 8 A_JumpIf(NearPlayer(112), "Awake"); Loop;
    Awake: R2F4 B -1; Stop;
    }

    bool NearPlayer(double dist)
    {
        for (int i = 0; i < MAXPLAYERS; i++)
        {
            if (!playeringame[i] || players[i].mo == null) continue;
            if (Distance3D(players[i].mo) < dist && CheckSight(players[i].mo)) return true;
        }
        return false;
    }
}

class RFFigureTSF : RFFigure { Default { Height 36; } States { Spawn: R2F5 A -1; Stop; } }       // F02-05: the boy
class RFFigureCochin : RFFigure { Default { Height 60; } States { Spawn: R2F6 A -1; Stop; } }    // F02-06: the nurse
class RFFigureValise : RFFigure { Default { Height 64; } States { Spawn: R2F7 A -1; Stop; } }    // F02-07: the girl

class RFViktorMirror : RFFigure      // F02-08: Viktor, seen only in mirrors; follows the player who looks at them
{
    Default
    {
        // Codex's R2F8 V02 (01/10): 311 px from head to soles, 56 u at the figures' 0.18 (the images of 28/09 stood
        // 378 px and were scaled 0.148 meanwhile; docs/production/handoff/RF2_20261001/mesures/reflet_rf02.md).
        Height 56;
        +ONLYVISIBLEINMIRRORS
    }
    States { Spawn: R2F8 A -1; Stop; }

    override void Tick()
    {
        Super.Tick();
        let pmo = players[consoleplayer].mo;
        if (pmo == null) return;
        SetOrigin(pmo.Pos, true);
        angle = pmo.angle;
        bInvisible = pmo.health <= 0;
    }
}

// RF04, the dance hall's mirrors (l. 533-539): "Dans un reflet, il porte sa tenue noire. Dans un autre, une blouse grise
// d'ouvrier. Dans un troisième, une chemise claire [...] un badge plastique à la ceinture." During the mirror scene
// (RFLuna) the other outfits stand beside him, shifted along the mirror wall: a figure shifted by s along a mirror is
// seen in the glass at s/2 from his own image, so each outfit shows in its own panel. Mirrors only; the scene removes
// them ("Le badge disparaît"). Codex's R4V2 / R4V3 V01, same face and height as R2F8 V02.
class RFViktorMirrorAlt : RFViktorMirror
{
    Vector2 shift;

    override void Tick()
    {
        Super.Tick();
        let pmo = players[consoleplayer].mo;
        if (pmo == null) return;
        SetOrigin((pmo.Pos.XY + shift, pmo.Pos.Z), true);
    }
}

class RFViktorMirrorGrey : RFViktorMirrorAlt { States { Spawn: R4V2 A -1; Stop; } }    // the worker's grey smock
class RFViktorMirrorShirt : RFViktorMirrorAlt { States { Spawn: R4V3 A -1; Stop; } }   // the light shirt, the badge
