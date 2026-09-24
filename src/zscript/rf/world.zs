// World actors: lights, ambience, props, readable notes, dev markers.

// Attenuated point light. args: red, green, blue, radius. Placed per fixture in the map.
class RFLamp : PointLightAttenuated {}
class RFLampFlicker : PointLightFlickerAttenuated {}

// Looping ambience. args[0]: 0 hum, 1 wind, 2 drip, 3 room. args[1]: volume percent (default 60).
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

// Readable object. args[0] selects the LANGUAGE key RF_NOTE_<n>. Use key reads it.
class RFNote : Actor
{
    Default
    {
        Radius 24;
        Height 40;
        +NOGRAVITY
        -SOLID
        +NOBLOOD
    }

    override bool Used(Actor user)
    {
        if (user == null || user.player == null) return false;
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
        TNT1 A -1;
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
