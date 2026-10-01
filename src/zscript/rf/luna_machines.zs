// RF05 - Les machines continuent: under the Luna Park and the park lit again (novel l. 551-707; fiche
// docs/production/maps/RF05_FICHE.md). The substation, its motor and wheel, the dials, the box NODE 0, the lever
// MARCHE / ATTENTE / ARRET, the young woman of Sainte-Anne (her words and her traces: her figure is requested from
// Astra), the repair, the fuse JERMA, the park that starts again without public, the empty train, the juke-box that
// plays, the dancers seen only in the mirrors, the service door and the sound of waves.

// Carried objects of the repair (given by the scenes).
class RFRepairRags : Inventory { Default { Inventory.MaxAmount 1; Tag "$RF_ITEM_RAGS"; +INVENTORY.UNDROPPABLE } }
class RFBeltKit : Inventory { Default { Inventory.MaxAmount 1; Tag "$RF_ITEM_BELTKIT"; +INVENTORY.UNDROPPABLE } }
class RFSpareFuse : Inventory { Default { Inventory.MaxAmount 1; Tag "$RF_ITEM_FUSE"; +INVENTORY.UNDROPPABLE } }
class RFCochinEnvelope : Inventory { Default { Inventory.MaxAmount 1; Tag "$RF_ITEM_ENVELOPE"; +INVENTORY.UNDROPPABLE } }

class RFSubDials : RFLunaInteract { Default { Radius 16; Height 48; RFInteract.Prompt 1; } }
class RFSubNode : RFLunaInteract { Default { Radius 14; Height 48; } }
class RFSubLever : RFLunaInteract { Default { Radius 12; Height 48; } }
class RFSubMotor : RFLunaInteract { Default { Radius 20; Height 40; } }
class RFSubFuses : RFLunaInteract { Default { Radius 14; Height 40; } }
class RFSubDrawer : RFLunaInteract { Default { Radius 14; Height 32; } }
class RFSubToolbox : RFLunaInteract { Default { Radius 14; Height 24; } }
class RFSubFuseBox : RFLunaInteract { Default { Radius 14; Height 32; } }

// The envelope of Cochin, put down on the workbench beside a tin of grease (l. 629). Appears with her words.
class RFEnvelopeProp : Actor
{
    Default { Radius 6; Height 2; Scale 0.35; +NOGRAVITY; +NOBLOCKMAP; +FLATSPRITE; }
    States { Spawn: R5EN A -1; Stop; }
}

// The juke-box, uncovered in RF04, now playing (l. 697): lit. The music itself stays a subtitle (no new music).
class RFJukeboxPlaying : Actor
{
    Default { Radius 16; Height 48; Scale 0.45; +SOLID; +NOBLOOD; +DONTTHRUST; }
    States { Spawn: R4JB B -1 Bright; Stop; }
}

// The roller-coaster train, three cars, nobody on board (l. 693). PROVISIONAL billboard until its model. Once the
// park has started again it runs along its track: args[0] units in the direction of its angle, rising args[1] units
// on the way (the lift hill), then goes out of sight behind the crest and comes round again; the automatic brake
// claps at each pass.
class RFCoasterTrain : Actor
{
    Vector3 p0;
    double travelled;
    bool running;
    int pause;
    bool braked;

    Default
    {
        Radius 8;
        Height 16;
        Scale 0.55;
        RenderRadius 120;
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
        +DONTSPLASH
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        p0 = Pos;
        bInvisible = true;
    }

    Vector3 At(double d)
    {
        double k = args[0] > 0 ? d / args[0] : 0;
        return (p0.XY + AngleToVector(angle, d), p0.Z + args[1] * k);
    }

    override void Activate(Actor activator)
    {
        running = true;
        bInvisible = false;
    }

    override void Tick()
    {
        Super.Tick();
        if (!running || isFrozen()) return;
        if (pause > 0)
        {
            if (--pause == 0) { travelled = 0; SetOrigin(p0, false); bInvisible = false; braked = false; }
            return;
        }
        travelled += 2.4;
        SetOrigin(At(travelled), true);
        if (!braked && travelled > args[0] / 2)
        {
            braked = true;
            A_StartSound("rf/luna/brake", CHAN_BODY, 0, 0.9);
        }
        if (travelled >= args[0])            // it goes behind the crest and comes round again
        {
            bInvisible = true;
            pause = 35 * 3;
        }
    }

    States { Spawn: R5TR A -1; Stop; }
}

class RFMachines : EventHandler
{
    const SIGNAL_TID = 999;
    // scenes (line field user_scene / RFLunaInteract args[0])
    const M_STAIR = 1;       // walk line: the stair, the bulb behind its grille
    const M_HEAT = 2;        // walk line: into the substation
    const M_DIALS = 3;       // RFSubDials; its lines (before / after)
    const M_NODE = 4;        // RFSubNode; its lines (closed / open green / open red)
    const M_LEVER = 5;       // RFSubLever; its lines (MARCHE / ARRET)
    const M_MOTOR = 6;       // RFSubMotor
    const M_FUSES = 7;       // RFSubFuses; its lines (JERMA empty / filled)
    const M_DRAWER = 8;      // RFSubDrawer
    const M_TOOLBOX = 9;     // RFSubToolbox
    const M_FUSEBOX = 10;    // RFSubFuseBox
    const M_PALM = 11;       // the stair wall where her palm was (ERREUR Ø appears)
    const M_WHEEL = 12;      // the wheel's line (turning / still)
    const M_PARK = 13;       // walk line: the park lit again
    const M_TRAIN = 14;      // walk line: the train on the track
    const M_HALL = 15;       // walk line: the dance hall, the juke-box playing, the mirrors
    const M_WAVES = 16;      // walk line: behind the service door, waves
    const M_SIGN = 18;       // the LUNA PARK bulbs (unlit / lit)
    const M_ENVELOPE = 19;   // RFSceneSpot: where the envelope is put down
    const GALLERY_WAVE_TID = 510;
    const FUSE_WAVE_TID = 540;
    const PARK_WAVE_TID = 550;
    const TRAIN_TID = 560;
    const BULB_TID = 570;

    bool active;
    int stage;               // 0 running (as found), 1 stopped (the scene), 2 stopped (repair), 3 running again
    bool motorSeen, nodeOpen, bearingDone, beltDone, fuseDone;
    bool stairDone, heatDone, parkDone, trainDone, hallDone, wavesDone;
    int seqScene, seqTic;
    Actor seqUser;
    Actor lastUsed;
    int lastUsedTic;
    int bulbTic;

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "RF05";
    }

    static void Say(Actor to, String key, double seconds = 5.0) { RFParis.Say(to, key, seconds); }
    static void Objective(int code) { RFParis.Objective(code); }

    void SetScene(int scene, String tex)
    {
        TextureID id = TexMan.CheckForTexture(tex, TexMan.Type_Any);
        for (int i = 0; i < Level.Lines.Size(); i++)
        {
            Line l = Level.Lines[i];
            if (l.GetUDMFInt('user_scene') != scene) continue;
            for (int s = 0; s < 2; s++) if (l.sidedef[s] != null) l.sidedef[s].SetTexture(Side.mid, id);
        }
    }

    // The motor's own sound (RFAmbientLoop kind 7) and the fans of the box (kind 8).
    void MotorSound(bool on)
    {
        let it = ThinkerIterator.Create('RFAmbientLoop');
        RFAmbientLoop a;
        while ((a = RFAmbientLoop(it.Next())) != null)
        {
            if (a.args[0] != 7) continue;
            if (on) a.A_StartSound("rf/luna/motor", CHAN_BODY, CHANF_LOOP, a.args[1] > 0 ? a.args[1] / 100.0 : 0.6, 0.45);
            else a.A_StopSound(CHAN_BODY);
        }
    }

    RFSceneSpot FindSpot(int scene)
    {
        let it = ThinkerIterator.Create('RFSceneSpot');
        RFSceneSpot s;
        while ((s = RFSceneSpot(it.Next())) != null) if (s.args[0] == scene) return s;
        return null;
    }

    void StartSequence(int scene, Actor user) { seqScene = scene; seqTic = 0; seqUser = user; }

    // ------------------------------------------------------------------ things
    void Interact(RFLunaInteract t, Actor user)
    {
        if (!active) return;
        if (t == lastUsed && Level.maptime - lastUsedTic < 12) return;
        lastUsed = t;
        lastUsedTic = Level.maptime;
        if (seqScene != 0) return;
        switch (t.args[0])
        {
        case M_DIALS:
            Say(user, stage < 3 ? "RF_RF05_DIALS_0" : "RF_RF05_DIALS_1", 6.0);
            break;
        case M_NODE:
            if (!nodeOpen)
            {
                nodeOpen = true;
                SetScene(M_NODE, fuseDone ? "RF5_NOD2" : "RF5_NOD1");
                t.A_StartSound("rf/luna/fans", CHAN_BODY, CHANF_LOOP, 0.5, ATTN_STATIC);
                StartSequence(M_NODE, user);
            }
            else Say(user, fuseDone ? "RF_RF05_NODE_RED" : "RF_RF05_NODE_AGAIN", 3.0);
            break;
        case M_MOTOR:
            if (stage == 0)
            {
                if (!motorSeen) { motorSeen = true; Say(user, "RF_RF05_MOTOR_0", 7.0); Objective(2); }
                else Say(user, "RF_RF05_MOTOR_RUNNING", 3.0);
            }
            else if (stage == 2)
            {
                if (!bearingDone && user.FindInventory('RFRepairRags')) { bearingDone = true; StartSequence(M_MOTOR, user); }
                else if (!beltDone && user.FindInventory('RFBeltKit')) { beltDone = true; StartSequence(M_TOOLBOX, user); }
                else if (bearingDone && beltDone) Say(user, "RF_RF05_MOTOR_DONE", 3.0);
                else Say(user, !bearingDone ? "RF_RF05_MOTOR_NEEDRAGS" : "RF_RF05_MOTOR_NEEDBELT", 4.0);
                CheckReady();
            }
            else if (stage == 3) Say(user, "RF_RF05_MOTOR_AGAIN", 3.0);
            break;
        case M_LEVER:
            if (stage == 0) { stage = 1; StartSequence(M_LEVER, user); }
            else if (stage == 2)
            {
                if (bearingDone && beltDone && fuseDone) { stage = 3; StartSequence(M_WHEEL, user); }
                else Say(user, "RF_RF05_LEVER_NOTYET", 5.0);
            }
            break;
        case M_FUSES:
            if (stage < 2) { Say(user, "RF_RF05_FUSES_RUNNING", 4.0); break; }
            if (fuseDone) { Say(user, "RF_RF05_FUSES_DONE", 3.0); break; }
            if (!user.FindInventory('RFSpareFuse')) { Say(user, "RF_RF05_FUSES_EMPTY", 6.0); break; }
            fuseDone = true;
            StartSequence(M_FUSES, user);
            break;
        case M_DRAWER:
            if (user.FindInventory('RFRepairRags')) { Say(user, "RF_RF05_DRAWER_AGAIN", 3.0); break; }
            user.GiveInventory('RFRepairRags', 1);
            user.A_StartSound("rf/luna/keys", CHAN_AUTO, 0, 0.7);
            Say(user, "RF_RF05_DRAWER", 6.0);
            break;
        case M_TOOLBOX:
            if (user.FindInventory('RFBeltKit')) { Say(user, "RF_RF05_TOOLBOX_AGAIN", 3.0); break; }
            user.GiveInventory('RFBeltKit', 1);
            user.A_StartSound("rf/world/paper", CHAN_AUTO, 0, 0.7);
            Say(user, "RF_RF05_TOOLBOX", 6.0);
            break;
        case M_FUSEBOX:
            if (user.FindInventory('RFSpareFuse') || fuseDone) { Say(user, "RF_RF05_FUSEBOX_AGAIN", 3.0); break; }
            user.GiveInventory('RFSpareFuse', 1);
            user.A_StartSound("rf/paris/fuse", CHAN_AUTO, 0, 0.8);
            Say(user, "RF_RF05_FUSEBOX", 6.0);
            RFParis.Wake(FUSE_WAVE_TID, user);
            break;
        }
    }

    void CheckReady()
    {
        if (stage == 2 && bearingDone && beltDone && fuseDone) Objective(5);
    }

    // ------------------------------------------------------------------ lines
    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        switch (e.ActivatedLine.GetUDMFInt('user_scene'))
        {
        case M_STAIR: if (!stairDone) { stairDone = true; Say(e.Thing, "RF_RF05_STAIR", 6.0); } break;
        case M_HEAT: if (!heatDone) { heatDone = true; Say(e.Thing, "RF_RF05_HEAT", 7.0); } break;
        case M_PARK: if (stage == 3 && !parkDone) { parkDone = true; Say(e.Thing, "RF_RF05_PARK", 7.0); } break;
        case M_TRAIN: if (stage == 3 && !trainDone) { trainDone = true; Say(e.Thing, "RF_RF05_TRAIN", 7.0); } break;
        case M_HALL: if (!hallDone) { hallDone = true; StartSequence(M_HALL, e.Thing); } break;
        case M_WAVES:
            if (!wavesDone)
            {
                wavesDone = true;
                e.Thing.A_StopSound(CHAN_7);
                e.Thing.A_StartSound("rf/luna/waves", CHAN_7, CHANF_LOOP, 0.9, ATTN_NONE);
                Say(e.Thing, "RF_RF05_WAVES", 5.0);
            }
            break;
        }
    }

    // ------------------------------------------------------------------ tick
    override void WorldTick()
    {
        if (!active || !playeringame[0]) return;
        Actor pl = players[0].mo;
        if (pl == null) return;
        if (bulbTic > 0) TickBulbs();
        TickSequence(pl);
    }

    // The bulbs come on one after the other, each with its small delay (l. 687): dormant lamps of the map (tid 570).
    void TickBulbs()
    {
        int n = bulbTic++;
        int k = 0;
        let it = Level.CreateActorIterator(BULB_TID);
        Actor lamp;
        while ((lamp = it.Next()) != null)
        {
            if (n == 4 + k * 5) lamp.Activate(null);
            k++;
        }
        if (n > 4 + k * 5) bulbTic = 0;
    }

    void TickSequence(Actor pl)
    {
        if (seqScene == 0) return;
        Actor u = seqUser != null ? seqUser : pl;
        int t = seqTic++;
        switch (seqScene)
        {
        case M_NODE:            // l. 565-569
            if (t == 0) Say(u, "RF_RF05_NODE_1", 6.0);
            else if (t == 190) { Say(u, "RF_RF05_NODE_2", 5.0); seqScene = 0; }
            break;
        case M_LEVER:           // l. 571-583 the lever; 587-655 the young woman; 655 her palm
            if (t == 0) Say(u, "RF_RF05_LEVER_1", 6.0);
            else if (t == 200) Say(u, "RF_RF05_LEVER_2", 6.0);
            else if (t == 380)
            {
                SetScene(M_LEVER, "RF5_LEVA");
                MotorSound(false);
                SetScene(M_WHEEL, "RF5_ROUS");
                u.A_StartSound("rf/luna/motorstop", CHAN_AUTO, 0, 1.0, ATTN_NONE);
                Say(u, "RF_RF05_LEVER_3", 6.0);
            }
            else if (t == 580) Say(u, "RF_RF05_WOMAN_1", 6.0);
            else if (t == 780) Say(u, "RF_RF05_WOMAN_2", 5.0);
            else if (t == 950) Say(u, "RF_RF05_WOMAN_3", 5.0);
            else if (t == 1120) Say(u, "RF_RF05_WOMAN_4", 5.0);
            else if (t == 1290)
            {
                Say(u, "RF_RF05_WOMAN_5", 6.0);
                RFSceneSpot spot = FindSpot(M_ENVELOPE);
                if (spot != null) Actor.Spawn('RFEnvelopeProp', spot.Pos);
            }
            else if (t == 1490) Say(u, "RF_RF05_WOMAN_6", 5.0);
            else if (t == 1660) Say(u, "RF_RF05_WOMAN_7", 6.0);
            else if (t == 1860) Say(u, "RF_RF05_WOMAN_8", 5.0);
            else if (t == 2030)
            {
                Say(u, "RF_RF05_WOMAN_9", 6.0);
                SetScene(M_PALM, "RF5_PAUM");
            }
            else if (t == 2230)
            {
                Say(u, "RF_RF05_REPAIR", 6.0);
                stage = 2;
                Objective(3);
                RFParis.Wake(GALLERY_WAVE_TID, u);
                seqScene = 0;
            }
            break;
        case M_MOTOR:           // l. 661-663: the bearing cleaned; the red synthetic fabric
            if (t == 0) Say(u, "RF_RF05_BEARING_1", 6.0);
            else if (t == 200) { Say(u, "RF_RF05_BEARING_2", 6.0); CheckReady(); seqScene = 0; }
            break;
        case M_TOOLBOX:         // l. 667: the belt reinforced
            if (t == 0) { Say(u, "RF_RF05_BELT", 7.0); CheckReady(); seqScene = 0; }
            break;
        case M_FUSES:           // l. 669-677
            if (t == 0) Say(u, "RF_RF05_FUSE_1", 6.0);
            else if (t == 200) Say(u, "RF_RF05_FUSE_2", 7.0);
            else if (t == 420)
            {
                SetScene(M_FUSES, "RF5_FUS1");
                if (nodeOpen) SetScene(M_NODE, "RF5_NOD2");
                u.A_StartSound("rf/paris/fuse", CHAN_AUTO, 0, 0.9);
                Say(u, "RF_RF05_FUSE_3", 5.0);
                u.TakeInventory('RFSpareFuse', 1, true);
                Objective(4);
                CheckReady();
                seqScene = 0;
            }
            break;
        case M_WHEEL:           // l. 679-689: MARCHE; the park lights up
            if (t == 0)
            {
                SetScene(M_LEVER, "RF5_LEVM");
                u.A_StartSound("rf/luna/motorstart", CHAN_AUTO, 0, 1.0, ATTN_NONE);
                Say(u, "RF_RF05_START_1", 6.0);
            }
            else if (t == 120) { MotorSound(true); SetScene(M_WHEEL, "RF5_ROU0"); SetScene(M_DIALS, "RF5_CAD1"); }
            else if (t == 200) Say(u, "RF_RF05_START_2", 7.0);
            else if (t == 420)
            {
                Say(u, "RF_RF05_START_3", 6.0);
                u.A_StartSound("rf/luna/bulbs", CHAN_AUTO, 0, 0.8, ATTN_NONE);
                SetScene(M_SIGN, "RF5_LUN1");
                bulbTic = 1;
                RFParis.Wake(TRAIN_TID, u);
            }
            else if (t == 620)
            {
                u.GiveInventory('RFCochinEnvelope', 1);
                Say(u, "RF_RF05_START_4", 6.0);
                Objective(6);
                RFParis.Wake(PARK_WAVE_TID, u);
                seqScene = 0;
            }
            break;
        case M_HALL:            // l. 697-701
            if (t == 0) Say(u, "RF_RF05_HALL_1", 6.0);
            else if (t == 200) Say(u, "RF_RF05_HALL_2", 6.0);
            else if (t == 400) { Say(u, "RF_RF05_HALL_3", 4.0); Objective(8); seqScene = 0; }
            break;
        default:
            seqScene = 0;
        }
    }
}
