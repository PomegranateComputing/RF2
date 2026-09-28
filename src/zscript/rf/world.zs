// World actors: lights, ambience, props, readable notes, dev markers.

// Attenuated point light. args: red, green, blue, radius. Placed per fixture in the map.
class RFLamp : PointLightAttenuated {}
class RFLampFlicker : PointLightFlickerAttenuated {}

// Looping ambience. args[0]: 0 hum, 1 wind, 2 drip, 3 room, 4 open street, 5 wireless sets (TSF shop).
// args[1]: volume percent (default 60).
class RFAmbientLoop : Actor
{
    Default
    {
        Radius 4;
        Height 4;
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        Sound s = "rf/amb/hum";
        if (args[0] == 1) s = "rf/amb/wind";
        else if (args[0] == 2) s = "rf/amb/drip";
        else if (args[0] == 3) s = "rf/amb/room";
        else if (args[0] == 4) s = "rf/paris/street";
        else if (args[0] == 5) s = "rf/paris/tsf";
        double volume = args[1] > 0 ? args[1] / 100.0 : 0.6;
        A_StartSound(s, CHAN_BODY, CHANF_LOOP, volume, ATTN_STATIC);
    }

    States
    {
    Spawn:
        TNT1 A -1;
        Stop;
    }
}

// Readable object. args[0] selects the LANGUAGE key RF_NOTE_<n>; args[1] the look
// (0 loose sheet, 1 open register). It lies flat on the surface under its centre
// (floor or desk top), whatever height the map gave it. Use key reads it.
class RFNote : Actor
{
    Default
    {
        Radius 16;
        Height 12;
        Scale 0.16;
        +NOGRAVITY
        -SOLID
        +NOBLOOD
        +FLATSPRITE
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        // args[2], bits: 1 the note lies at the height it was placed at (on an object such as the RF02 pram) instead
        // of the floor under it; 2 no sheet is drawn, the object itself shows what is read (the registers of the
        // pram model). 0 for every note of RF01 (unchanged).
        Sector under = Level.PointInSector(Pos.XY);
        if (!(args[2] & 1)) SetZ(under.floorplane.ZAtPoint(Pos.XY) + 0.4);
        if (args[2] & 2) A_SetRenderStyle(0, STYLE_None);
        if (args[1] == 1) SetStateLabel("Register");
    }

    int lastRead;

    override bool Used(Actor user)
    {
        if (user == null || user.player == null) return false;
        // One press, one reading (after RF01 the prompt can reach the note in the same moment as the engine).
        if (lastRead > 0 && Level.maptime - lastRead < 12) return true;
        lastRead = Level.maptime;
        String key = String.Format("RF_NOTE_%d", args[0]);
        user.A_Print(StringTable.Localize("$" .. key), 6.0);
        A_StartSound("rf/world/paper", CHAN_BODY, 0, 0.8);
        let director = RFDirector(EventHandler.Find('RFDirector'));
        if (director != null) director.NoteRead(args[0], user);
        return true;
    }

    States
    {
    Spawn:
        RFNP A -1;
        Stop;
    Register:
        RFNP B -1;
        Stop;
    }
}

// Loose paper on the ground (evacuation litter). Decorative only, flat on the floor.
class RFLitter : Actor
{
    Default
    {
        Radius 8;
        Height 2;
        Scale 0.16;
        +NOBLOCKMAP
        +FLATSPRITE
        +NOGRAVITY
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        SetZ(floorz + 0.3);
    }

    States
    {
    Spawn:
        RFNP A -1;
        Stop;
    }
}

// Solid furniture rendered through MODELDEF (legacy S1 meshes). Radii match footprints.
class RFPropBase : Actor
{
    Default
    {
        +SOLID
        +NOGRAVITY
        +NOBLOOD
        +DONTTHRUST
        Radius 16;
        Height 32;
    }
    States
    {
    Spawn:
        RFMD A -1;
        Stop;
    }
}
class RFPropDesk : RFPropBase { Default { Radius 26; Height 26; } }
class RFPropCabinet : RFPropBase { Default { Radius 16; Height 60; } }
class RFPropChair : RFPropBase { Default { Radius 8; Height 30; } }
class RFPropRadiator : RFPropBase { Default { Radius 18; Height 24; } }
class RFPropTrolley : RFPropBase { Default { Radius 16; Height 28; } }
class RFPropBench : RFPropBase { Default { Radius 22; Height 28; } }
class RFPropLamp : Actor
{
    Default
    {
        Radius 10;
        Height 8;
        +NOGRAVITY
        +NOBLOCKMAP
        +SPAWNCEILING
    }
    States
    {
    Spawn:
        RFMD A -1 Bright;
        Stop;
    }
}

// Target of objective-only and ending trigger lines (Thing_Activate on its tid). The engine
// reports a line as activated only when its special succeeds, and Thing_Activate succeeds only
// when a thing carries the tid: this inert marker makes those lines count.
class RFSignal : Actor
{
    Default
    {
        +NOBLOCKMAP
        +NOGRAVITY
        +NOINTERACTION
    }
    States
    {
    Spawn:
        TNT1 A -1;
        Stop;
    }
}

// Development markers. Invisible and inert in play.
// RFTourPoint: args[0] order, args[1] pitch in degrees (+down), thing angle = yaw.
class RFTourPoint : Actor
{
    Default
    {
        Radius 8;
        Height 8;
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
    }
    States
    {
    Spawn:
        TNT1 A -1;
        Stop;
    }
}

// RFDevWaypoint: args[0] order, args[1] flags (1 = press use facing thing angle,
// 2 = wait for args[2] tics after arrival), args[3] = weapon slot to select (0 none).
class RFDevWaypoint : RFTourPoint {}
