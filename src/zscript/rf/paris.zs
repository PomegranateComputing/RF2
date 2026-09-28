// RF02 - Paris, 14 June 1940: the scenes of the walk from the boulevard Arago to the Porte Maillot
// (docs/production/maps/RF02_FICHE.md, novel lines 87-457). Objects Viktor can use, the reflection of the
// mattress in the pharmacy window, the Amiga in the TSF window, the field telephone, the wireless set.
// Scene lines carry the UDMF field user_scene; scene things are RFInteract subclasses (args[0] = scene).

// Carried objects of the chapter (no world sprite: given by a scene).
class RFTicket : Inventory
{
    Default
    {
        Inventory.MaxAmount 1;
        Tag "$RF_ITEM_TICKET";
        +INVENTORY.UNDROPPABLE
    }
}

class RFReaderCard : Inventory
{
    Default
    {
        Inventory.MaxAmount 1;
        Tag "$RF_ITEM_READERCARD";
        +INVENTORY.UNDROPPABLE
    }
}

// A usable object of a scene. The use key hands it to the chapter handler.
class RFInteract : Actor
{
    int prompt;       // HUD verb: 1 read, 3 operate
    property Prompt: prompt;

    Default
    {
        Radius 12;
        Height 24;
        +NOGRAVITY
        -SOLID
        +NOBLOOD
        +DONTTHRUST
        RFInteract.Prompt 3;
    }

    override bool Used(Actor user)
    {
        if (user == null || user.player == null) return false;
        let paris = RFParis(EventHandler.Find('RFParis'));
        if (paris != null) paris.Interact(self, user);
        return true;
    }
}

class RFSacoche : RFInteract        // the fare collector's satchel on its hook (l. 117)
{
    Default { Scale 0.125; }
    States { Spawn: RFBG A -1; Stop; }
}

class RFFormsBucket : RFInteract    // forms burning badly in a galvanised bucket (l. 87)
{
    Default { Scale 0.1375; RFInteract.Prompt 1; }
    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        A_StartSound("rf/paris/fire", CHAN_BODY, CHANF_LOOP, 0.55, ATTN_STATIC);
    }
    States { Spawn: RFBK A -1; Stop; }
}

class RFFieldPhone : RFInteract     // the military field telephone on the folding table (l. 333)
{
    Default { Scale 0.1375; }
    States { Spawn: RFPH A -1; Stop; }
}

class RFRadioSet : RFInteract       // the set whose dial lamp stays dark (l. 229)
{
    Default { Scale 0.125; }
    States
    {
    Spawn: RFRD A -1; Stop;
    Lit: RFRD B -1 Bright; Stop;
    }
}

class RFAtlas : RFInteract          // the atlas of the colonies on the book barricade (l. 311)
{
    Default { Scale 0.16; +FLATSPRITE; RFInteract.Prompt 1; }
    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        Sector under = Level.PointInSector(Pos.XY);
        SetZ(under.floorplane.ZAtPoint(Pos.XY) + 0.4);
    }
    States { Spawn: RFNP B -1; Stop; }
}

class RFPram : Actor                // the pram full of registers tied with string (l. 91): Astra's model, 47 x 30 u
{
    Default
    {
        +SOLID
        +NOBLOOD
        +DONTTHRUST
        Radius 18;
        Height 38;
    }
    States { Spawn: RFPR A -1; Stop; }
}

class RFTram : Actor                 // the tram stopped on its rails (l. 113): Astra's model; the map holds its volume
{
    Default
    {
        // Small body, large render radius: a body as large as the model would meet the invisible slabs of the
        // map at spawn and be pushed under the deck (the model then shows only its roof at street level); the
        // render radius keeps it drawn whenever a part of it is in view.
        Radius 8;
        Height 8;
        RenderRadius 180;
        +NOGRAVITY
        +NOBLOCKMAP
        +DONTSPLASH
    }
    States { Spawn: RFTM A -1; Stop; }
}

class RFTrack : Actor                // a 256 u module of rails set in the setts
{
    Default
    {
        Radius 4;
        Height 2;
        RenderRadius 130;
        +NOGRAVITY
        +NOBLOCKMAP
        +DONTSPLASH
    }
    States { Spawn: RFRL A -1; Stop; }
}

class RFTrackHalf : RFTrack { Default { RenderRadius 66; } }   // the half module at the east end of the square

class RFMorrisColumn : RFInteract   // the Morris column (l. 437): scratched, it shows JERMA PALACE for a heartbeat
{
    Default
    {
        +SOLID
        Radius 24;
        Height 150;
    }
    States
    {
    Spawn: RFMC A -1; Stop;
    Jerma: RFMC B -1; Stop;
    Dentifrice: RFMC C -1; Stop;
    }
}

class RFFountain : RFInteract       // a street fountain, rusty water (l. 425)
{
    Default { Radius 10; Height 40; }
    States { Spawn: TNT1 A -1; Stop; }
}

// Scene markers: args[0] scene, thing angle = direction (the pharmacy window, the mattress path).
class RFSceneSpot : Actor
{
    Default
    {
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
    }
    States { Spawn: TNT1 A -1; Stop; }
}

// Mattresses on the pavements of Denfert, loaded by the families (l. 129): flat on the ground.
class RFMattressProp : Actor
{
    Default
    {
        Radius 8;
        Height 4;
        +NOGRAVITY
        +NOBLOCKMAP
        +FLATSPRITE
    }
    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        SetZ(floorz + 0.5);
    }
    States { Spawn: RFMT A -1; Stop; }
}

// The mattress that advances with nobody pulling it (l. 157). It exists only in the reflection.
class RFMirrorMattress : Actor
{
    Default
    {
        Radius 8;
        Height 4;
        Scale 1.0;
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
        +FLATSPRITE
        +ONLYVISIBLEINMIRRORS
    }

    override void Tick()
    {
        Super.Tick();
        if (isFrozen()) return;
        // dragged on the asphalt: a slow advance by jerks, as a rope would pull it
        double pull = (Level.maptime % 35) < 22 ? 1.6 : 0.3;
        SetOrigin(Pos + (cos(angle) * pull, sin(angle) * pull, 0), true);
        SetZ(floorz + 1);
    }

    States { Spawn: RFMT A -1; Stop; }
}

class RFParis : EventHandler
{
    const SIGNAL_TID = 999;
    // scenes (line field user_scene / RFInteract args[0] / RFSceneSpot args[0])
    const S_MORRIS = 1;     // RFMorrisColumn: its poster, scratched
    const S_SHUTTER = 2;    // use line: ERREUR Ø on the pharmacy shutter
    const S_ENGINES = 3;    // walk line: engines from the north, mid-bridge
    const S_BELL = 4;       // walk line: a bell from the west
    const S_PHONE_RING = 5; // walk line: the field telephone starts ringing
    const S_TSF_VOICES = 6; // walk line: the wireless sets in front of the shop
    const S_TSF_WINDOW = 7; // window lines of the TSF shop (reflection)
    const S_MIRROR = 8;     // spot in front of the pharmacy side window
    const S_MATTRESS = 9;   // spot: where the mattress starts, angle = its way
    const S_TICKET = 10;    // RFSacoche
    const S_FORMS = 11;     // RFFormsBucket
    const S_PHONE = 12;     // RFFieldPhone
    const S_RADIO = 13;     // RFRadioSet
    const S_ATLAS = 14;     // RFAtlas
    const S_FOUNTAIN = 15;  // RFFountain
    const PHONE_WAVE_TID = 600;

    bool active;
    // one-shot states
    bool morrisDone, shutterDone, ticketDone, atlasDone, radioDone, phoneDone, mirrorDone;
    int tsfWindow;          // 0 radios, 1 the reflection shows, 2 gone for good
    int phoneState;         // 0 silent, 1 ringing, 2 call running, 3 over
    Actor phoneThing, radioThing;
    Actor mattress;
    int mirrorTics;
    int fountainTics;
    // timed sequences of the objects Viktor uses: one at a time (WorldTick); the radio voices heard from the
    // street run on their own clock, so they never hold back an object
    int seqScene, seqTic;
    int voiceTic;
    Actor seqUser;
    Actor morris;
    int morrisTics;

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "RF02";
        if (!active || e.IsSaveGame) return;
        let it = ThinkerIterator.Create('RFInteract');
        RFInteract t;
        while ((t = RFInteract(it.Next())) != null)
        {
            if (t.args[0] == S_PHONE) phoneThing = t;
            if (t.args[0] == S_RADIO) radioThing = t;
        }
    }

    // ------------------------------------------------------------------ messages and objectives
    static void Say(Actor to, String key, double seconds = 5.0)
    {
        if (to != null) to.A_Print(StringTable.Localize("$" .. key), seconds);
        // Development evidence: the scene texts are centred prints, which the console does not log.
        if (CVar.GetCVar('rf_dev_autopilot').GetBool() || CVar.GetCVar('rf_dev_log').GetBool())
            Console.Printf("RF_DEV_SCENE key=%s t=%d", key, Level.maptime);
    }

    static void Objective(int code)
    {
        let director = RFDirector(EventHandler.Find('RFDirector'));
        if (director != null) director.SetObjective(code);
    }

    static void Wake(int tid, Actor by)
    {
        let it = Level.CreateActorIterator(tid);
        Actor a;
        while ((a = it.Next()) != null) a.Activate(by);
    }

    void StartSequence(int scene, Actor user)
    {
        seqScene = scene;
        seqTic = 0;
        seqUser = user;
    }

    // ------------------------------------------------------------------ things
    Actor lastUsed;
    int lastUsedTic;

    void Interact(RFInteract t, Actor user)
    {
        if (!active) return;
        // One press, one answer: the engine's use trace and the prompt (RFDirector.UsePressed) can both reach
        // the same object in the same moment.
        if (t == lastUsed && Level.maptime - lastUsedTic < 12) return;
        lastUsed = t;
        lastUsedTic = Level.maptime;
        switch (t.args[0])
        {
        case S_FORMS:
            Say(user, "RF_RF02_FORMS", 6.0);
            break;
        case S_TICKET:
            if (ticketDone) { Say(user, "RF_RF02_TICKET_AGAIN", 3.0); break; }
            ticketDone = true;
            StartSequence(S_TICKET, user);
            break;
        case S_ATLAS:
            if (atlasDone) { Say(user, "RF_RF02_ATLAS_AGAIN", 3.0); break; }
            atlasDone = true;
            StartSequence(S_ATLAS, user);
            break;
        case S_RADIO:
            if (radioDone || seqScene != 0) break;
            radioDone = true;
            StartSequence(S_RADIO, user);
            break;
        case S_PHONE:
            if (phoneState >= 2 || seqScene != 0) break;
            phoneState = 2;
            t.A_StopSound(CHAN_VOICE);
            StartSequence(S_PHONE, user);
            break;
        case S_MORRIS:
            if (morrisDone) break;
            morrisDone = true;
            morris = t;
            t.SetStateLabel("Jerma");
            t.A_StartSound("rf/world/paper", CHAN_AUTO, 0, 0.6);
            morrisTics = 12;                      // one heartbeat
            break;
        case S_FOUNTAIN:
            if (fountainTics > 0) break;
            fountainTics = 35 * 20;
            user.GiveBody(15, 100);
            user.A_StartSound("rf/item/pickup", CHAN_AUTO, 0, 0.5);
            Say(user, "RF_RF02_FOUNTAIN", 4.0);
            break;
        }
    }

    // ------------------------------------------------------------------ lines
    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        int scene = e.ActivatedLine.GetUDMFInt('user_scene');
        switch (scene)
        {
        case S_SHUTTER:
            if (shutterDone) break;
            shutterDone = true;
            StartSequence(S_SHUTTER, e.Thing);
            break;
        case S_ENGINES:
            e.Thing.A_StartSound("rf/paris/engines", CHAN_AUTO, 0, 1.0, ATTN_NONE);
            Say(e.Thing, "RF_RF02_ENGINES", 5.0);
            break;
        case S_BELL:
            e.Thing.A_StartSound("rf/paris/bell", CHAN_AUTO, 0, 0.8, ATTN_NONE);
            Say(e.Thing, "RF_RF02_BELL", 5.0);
            break;
        case S_PHONE_RING:
            if (phoneState == 0 && phoneThing != null)
            {
                phoneState = 1;
                phoneThing.A_StartSound("rf/paris/phonering", CHAN_VOICE, CHANF_LOOP, 1.0, ATTN_NORM);
            }
            break;
        case S_TSF_VOICES:
            if (voiceTic == 0) voiceTic = 1;
            break;
        }
    }

    void SetTsfWindow(String tex)
    {
        TextureID id = TexMan.CheckForTexture(tex, TexMan.Type_Any);
        for (int i = 0; i < Level.Lines.Size(); i++)
        {
            Line l = Level.Lines[i];
            if (l.GetUDMFInt('user_scene') != S_TSF_WINDOW) continue;
            for (int s = 0; s < 2; s++)
            {
                if (l.sidedef[s] != null) l.sidedef[s].SetTexture(Side.mid, id);
            }
        }
    }

    RFSceneSpot FindSpot(int scene)
    {
        let it = ThinkerIterator.Create('RFSceneSpot');
        RFSceneSpot s;
        while ((s = RFSceneSpot(it.Next())) != null)
        {
            if (s.args[0] == scene) return s;
        }
        return null;
    }

    static double Facing(Actor who, Vector2 target)
    {
        Vector2 d = target - who.Pos.XY;
        return abs(Actor.DeltaAngle(who.angle, VectorAngle(d.X, d.Y)));
    }

    // ------------------------------------------------------------------ tick
    override void WorldTick()
    {
        if (!active || !playeringame[0]) return;
        Actor pl = players[0].mo;
        if (pl == null) return;
        if (fountainTics > 0) fountainTics--;

        if (morrisTics > 0 && --morrisTics == 0)
        {
            if (morris != null) morris.SetStateLabel("Dentifrice");
            Say(pl, "RF_RF02_MORRIS", 5.0);
        }

        TickTsfWindow(pl);
        TickMirror(pl);
        TickVoices(pl);
        TickSequence(pl);
    }

    // The TSF window: from the street the sets change shape in the reflection; the image goes when he comes
    // closer (l. 213).
    void TickTsfWindow(Actor pl)
    {
        if (tsfWindow == 2 || pl.health <= 0) return;
        RFSceneSpot spot = FindSpot(S_TSF_WINDOW);
        if (spot == null) return;
        double d = pl.Distance2D(spot);
        if (tsfWindow == 0 && d > 176 && d < 520 && Facing(pl, spot.Pos.XY) < 28)
        {
            tsfWindow = 1;
            SetTsfWindow("RF2_AMIG");
            if (CVar.GetCVar('rf_dev_autopilot').GetBool() || CVar.GetCVar('rf_dev_log').GetBool())
                Console.Printf("RF_DEV_SCENE key=TSF_AMIGA t=%d", Level.maptime);
        }
        else if (tsfWindow == 1 && d < 160)
        {
            tsfWindow = 2;
            SetTsfWindow("RF2_TSFS");
        }
    }

    // The pharmacy side window: behind him, at the end of the street, the mattress advances with nobody to pull
    // it; he turns round; when he looks at the window again it has gone (l. 157).
    void TickMirror(Actor pl)
    {
        if (mirrorDone) return;
        RFSceneSpot spot = FindSpot(S_MIRROR);
        if (spot == null) return;
        Vector2 window = spot.Pos.XY + (cos(spot.angle), sin(spot.angle)) * 48;
        double facing = Facing(pl, window);
        if (mattress == null)
        {
            if (pl.Distance2D(spot) < 96 && facing < 35)
            {
                RFSceneSpot start = FindSpot(S_MATTRESS);
                if (start == null) { mirrorDone = true; return; }
                mattress = Actor.Spawn('RFMirrorMattress', start.Pos);
                if (mattress != null) mattress.angle = start.angle;
                if (CVar.GetCVar('rf_dev_autopilot').GetBool() || CVar.GetCVar('rf_dev_log').GetBool())
                    Console.Printf("RF_DEV_SCENE key=MIRROR_MATTRESS t=%d", Level.maptime);
                mirrorTics = 0;
            }
            return;
        }
        mirrorTics++;
        if (facing > 100 || mirrorTics > 35 * 9 || pl.Distance2D(spot) > 260)
        {
            mattress.Destroy();
            mattress = null;
            mirrorDone = true;
        }
    }

    // The wireless sets behind the grille (l. 211): three voices, each on its own set. Once.
    void TickVoices(Actor pl)
    {
        if (voiceTic <= 0) return;
        int t = voiceTic++ - 1;
        if (t == 0) Say(pl, "RF_RF02_TSF_1", 3.5);
        else if (t == 120) Say(pl, "RF_RF02_TSF_2", 3.5);
        else if (t == 240) { Say(pl, "RF_RF02_TSF_3", 3.5); voiceTic = -1; }
    }

    void TickSequence(Actor pl)
    {
        if (seqScene == 0) return;
        Actor u = seqUser != null ? seqUser : pl;
        int t = seqTic++;
        switch (seqScene)
        {
        case S_TICKET:
            if (t == 0) { Say(u, "RF_RF02_TICKET_1", 4.0); u.A_StartSound("rf/world/paper", CHAN_AUTO, 0, 0.7); }
            else if (t == 90)
            {
                Say(u, "RF_RF02_TICKET_2", 5.0);
                u.A_GiveInventory('RFTicket', 1);
                seqScene = 0;
            }
            break;
        case S_ATLAS:
            if (t == 0) { Say(u, "RF_RF02_ATLAS_1", 4.0); u.A_StartSound("rf/world/paper", CHAN_AUTO, 0, 0.8); }
            else if (t == 90)
            {
                Say(u, "RF_RF02_ATLAS_2", 7.0);
                u.A_GiveInventory('RFReaderCard', 1);
                seqScene = 0;
            }
            break;
        case S_SHUTTER:
            if (t == 0) Say(u, "RF_RF02_SHUTTER_1", 4.0);
            else if (t == 110) { Say(u, "RF_RF02_SHUTTER_2", 5.0); seqScene = 0; }
            break;
        case S_RADIO:
            if (t == 0) Say(u, "RF_RF02_RADIO_1", 4.0);
            else if (t == 100) { Say(u, "RF_RF02_RADIO_2", 4.0); if (radioThing != null) radioThing.A_StartSound("rf/paris/fuse", CHAN_AUTO); }
            else if (t == 200) Say(u, "RF_RF02_RADIO_3", 4.0);
            else if (t == 300)
            {
                if (radioThing != null) { radioThing.SetStateLabel("Lit"); radioThing.A_StartSound("rf/paris/radioburst", CHAN_BODY, 0, 1.0); }
                Say(u, "RF_RF02_RADIO_4", 4.5);
            }
            else if (t == 460)
            {
                if (radioThing != null) { radioThing.SetStateLabel("Spawn"); radioThing.A_StopSound(CHAN_BODY); }
                Say(u, "RF_RF02_RADIO_5", 4.0);
                seqScene = 0;
            }
            break;
        case S_PHONE:
            if (t == 0) Say(u, "RF_RF02_PHONE_1", 3.0);
            else if (t == 100) Say(u, "RF_RF02_PHONE_2", 5.0);
            else if (t == 260) Say(u, "RF_RF02_PHONE_3", 5.0);
            else if (t == 420) Say(u, "RF_RF02_PHONE_4", 4.0);
            else if (t == 540)
            {
                if (phoneThing != null) phoneThing.A_StartSound("rf/paris/phonetone", CHAN_VOICE, 0, 0.7);
                Say(u, "RF_RF02_PHONE_5", 5.0);
                Wake(PHONE_WAVE_TID, u);          // the line is dead; the staff are already coming out of the side streets
            }
            else if (t == 720)
            {
                if (phoneThing != null) phoneThing.A_StartSound("rf/paris/phonering", CHAN_VOICE, 0, 1.0);
                Say(u, "RF_RF02_PHONE_6", 4.0);
            }
            else if (t == 800)
            {
                phoneState = 3;
                Objective(7);
                seqScene = 0;
            }
            break;
        default:
            seqScene = 0;
        }
    }
}
