// RF04 - the Luna Park of the Porte Maillot, 14 June 1940, first passage (novel l. 451-551; fiche
// docs/production/maps/RF04_FICHE.md). The guard and his time clock, the key of the substation, the rail, the shoe of
// the Niagara, the turnstile, the mirrors and the silent juke-box. Scene lines carry the UDMF field user_scene,
// scene things are RFLunaInteract (args[0] = scene). Same method as RFParis (paris.zs).

// Carried objects: the time card Viktor has had since Sainte-Anne (l. 11, 75), then punched 06:06 (l. 481).
class RFTimeCard : Inventory
{
    Default
    {
        Inventory.MaxAmount 1;
        Inventory.Icon "RF4CART0";
        Tag "$RF_ITEM_CARD";
        +INVENTORY.UNDROPPABLE
    }
}

class RFTimeCardPunched : Inventory
{
    Default
    {
        Inventory.MaxAmount 1;
        Inventory.Icon "RF4CART1";
        Tag "$RF_ITEM_CARD_0606";
        +INVENTORY.UNDROPPABLE
    }
}

// The key of the substation, taken from the hook of the hut (l. 495-497). Lock 6 (LOCKDEFS).
class RFSousStationKey : Key
{
    Default
    {
        Inventory.PickupMessage "$RF_PICKUP_SOUSSTATION";
        Inventory.PickupSound "rf/luna/keys";
        Inventory.Icon "RFKYC0";
        Tag "$RF_KEY_SOUSSTATION";
        Scale 0.5;
    }
    States
    {
    Spawn:
        RFKY C -1;
        Stop;
    }
}

// A usable object of the Luna Park; the prompt of the director finds it (RFInteract), the use goes to RFLuna.
class RFLunaInteract : RFInteract
{
    override bool Used(Actor user)
    {
        if (user == null || user.player == null) return false;
        let luna = RFLuna(EventHandler.Find('RFLuna'));
        if (luna != null) luna.Interact(self, user);
        let machines = RFMachines(EventHandler.Find('RFMachines'));     // RF05 (luna_machines.zs)
        if (machines != null) machines.Interact(self, user);
        return true;
    }
    States { Spawn: TNT1 A -1; Stop; }
}

class RFLunaClock : RFLunaInteract { Default { Radius 14; Height 40; } }             // the hut's window, the clock behind it
class RFLunaKeyHook : RFLunaInteract { Default { Radius 12; Height 40; } }           // the hook of keys
class RFLunaRail : RFLunaInteract { Default { Radius 16; Height 8; RFInteract.Prompt 1; } }   // the warm rail
class RFLunaTurnstile : RFLunaInteract { Default { Radius 12; Height 40; } }         // the turnstile with a counter
class RFLunaMirror : RFLunaInteract { Default { Radius 16; Height 56; RFInteract.Prompt 1; } } // the mirror of the badge

class RFLunaShoe : RFLunaInteract           // the child's shoe in a black puddle (l. 523-525): flat, in the puddle
{
    Default { Radius 10; Height 8; Scale 0.45; +FLATSPRITE; RFInteract.Prompt 1; }
    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        SetZ(floorz + 0.4);
    }
    States { Spawn: R4SH A -1; Stop; }
}

class RFLunaJukebox : RFLunaInteract        // the juke-box under its tarpaulin (l. 541-549). PROVISIONAL sprite.
{
    Default { Radius 16; Height 48; Scale 0.45; +SOLID; }
    States
    {
    Spawn: R4JB A -1; Stop;
    Uncovered: R4JB B -1; Stop;
    }
}

// The guard in his hut (l. 467). Visual only, never hostile. PROVISIONAL silhouette until Astra's F04-01.
class RFFigureGuard : Actor
{
    Default
    {
        Scale 0.5;
        Radius 12;
        Height 48;
        +NOGRAVITY
        +NOBLOCKMAP
        +NOINTERACTION
        +DONTSPLASH
    }
    States
    {
    Spawn: R4G1 A -1; Stop;
    Talk: R4G1 B -1; Stop;
    }
}

class RFLuna : EventHandler
{
    const SIGNAL_TID = 999;
    // scenes (line field user_scene / RFLunaInteract args[0])
    const L_HUT = 1;          // walk line: approaching the hut's window
    const L_CLOCK = 2;        // RFLunaClock
    const L_KEYS = 3;         // RFLunaKeyHook; lines of the key board (texture swap)
    const L_BARRIER = 4;      // the staff barrier (decor line), lifted by the scene
    const L_GLASS = 5;        // the hut's glass lines (ERREUR Ø appears)
    const L_RAIL = 6;         // RFLunaRail
    const L_BROOKLYN = 7;     // walk line: behind the decor, the technical corridor
    const L_NIAGARA = 8;      // walk line: the rim of the basin
    const L_SHOE = 9;         // RFLunaShoe
    const L_MOTOR = 10;       // walk line: the motor heard under the park
    const L_TURNSTILE = 11;   // RFLunaTurnstile; its bar (decor line)
    const L_COUNTER = 12;     // the counter's face lines (617 -> 618)
    const L_MIRROR = 13;      // RFLunaMirror
    const L_JUKEBOX = 14;     // RFLunaJukebox
    const L_HALL = 15;        // walk line: into the dance hall
    const L_GLASSLOOK = 16;   // the guard's spot: where the hut is looked back at from
    const JUKEBOX_WAVE_TID = 500;
    const BARRIER_WAVE_TID = 100;

    bool active;
    int hutStage;             // 0 nobody spoke, 1 talking, 2 waiting for the card, 3 punched, 4 key taken, 5 barrier open, 6 hut empty
    bool railDone, brooklynDone, niagaraDone, shoeDone, motorDone, mirrorDone, hallDone, turnstileDone;
    int jukeboxStage;         // 0 covered, 1 uncovered, 2 pressed (the knocks)
    int seqScene, seqTic;
    Actor seqUser;
    Actor guard;
    Actor lastUsed;
    int lastUsedTic;
    Actor mirrorSpot, greyImage, shirtImage;   // the mirror of the badge; the two other outfits during its scene

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "RF04";
        if (!active) return;
        if (e.IsSaveGame)
        {
            guard = FindGuard();
            return;
        }
        guard = FindGuard();
        // Viktor has carried the card since Sainte-Anne (l. 75); a direct start of the chapter gives it too.
        if (playeringame[0] && players[0].mo != null && players[0].mo.FindInventory('RFTimeCardPunched') == null)
            players[0].mo.GiveInventory('RFTimeCard', 1);
    }

    Actor FindGuard()
    {
        let it = ThinkerIterator.Create('RFFigureGuard');
        return Actor(it.Next());
    }

    static void Say(Actor to, String key, double seconds = 5.0)
    {
        RFParis.Say(to, key, seconds);
    }

    static void Objective(int code)
    {
        RFParis.Objective(code);
    }

    // One of the other outfits beside him in the mirror wall: shifted along the wall (the mirror spot faces the glass),
    // it shows in the glass half that distance from his own image, in the next panel (rf04.py: panels 48 apart).
    Actor MirrorOutfit(class<Actor> kind, double side, Actor user)
    {
        double a = (mirrorSpot != null ? mirrorSpot.angle : user.angle) + side;
        let img = RFViktorMirrorAlt(Actor.Spawn(kind, user.Pos));
        if (img != null) img.shift = Actor.AngleToVector(a, 96);
        return img;
    }

    void StartSequence(int scene, Actor user)
    {
        seqScene = scene;
        seqTic = 0;
        seqUser = user;
    }

    // Lines of a scene: textures swapped, a bar lifted.
    void SetSceneTexture(int scene, String tex)
    {
        TextureID id = TexMan.CheckForTexture(tex, TexMan.Type_Any);
        for (int i = 0; i < Level.Lines.Size(); i++)
        {
            Line l = Level.Lines[i];
            if (l.GetUDMFInt('user_scene') != scene) continue;
            for (int s = 0; s < 2; s++)
            {
                if (l.sidedef[s] != null) l.sidedef[s].SetTexture(Side.mid, id);
            }
        }
    }

    void LiftBar(int scene)
    {
        TextureID none;
        none.SetNull();
        for (int i = 0; i < Level.Lines.Size(); i++)
        {
            Line l = Level.Lines[i];
            if (l.GetUDMFInt('user_scene') != scene) continue;
            l.flags &= ~(Line.ML_BLOCKING | Line.ML_BLOCKMONSTERS | Line.ML_BLOCKEVERYTHING);
            for (int s = 0; s < 2; s++)
            {
                if (l.sidedef[s] != null) l.sidedef[s].SetTexture(Side.mid, none);
            }
        }
    }

    static void Wake(int tid, Actor by)
    {
        RFParis.Wake(tid, by);
    }

    // ------------------------------------------------------------------ things
    void Interact(RFLunaInteract t, Actor user)
    {
        if (!active) return;
        if (t == lastUsed && Level.maptime - lastUsedTic < 12) return;
        lastUsed = t;
        lastUsedTic = Level.maptime;
        switch (t.args[0])
        {
        case L_CLOCK:
            if (hutStage < 2) { if (hutStage == 0) StartHut(user); break; }
            if (hutStage == 2 && seqScene == 0)
            {
                StartSequence(L_CLOCK, user);
                hutStage = 3;
            }
            else if (hutStage >= 3) Say(user, "RF_RF04_CLOCK_AGAIN", 3.0);
            break;
        case L_KEYS:
            if (hutStage < 3) { Say(user, "RF_RF04_KEYS_EARLY", 4.0); break; }
            if (hutStage == 3 && seqScene == 0)
            {
                StartSequence(L_KEYS, user);
                hutStage = 4;
            }
            else if (hutStage >= 4) Say(user, "RF_RF04_KEYS_AGAIN", 3.0);
            break;
        case L_RAIL:
            if (railDone) break;
            railDone = true;
            user.A_StartSound("rf/luna/rail", CHAN_AUTO, 0, 0.8);
            Say(user, "RF_RF04_RAIL", 6.0);
            break;
        case L_SHOE:
            if (shoeDone) { Say(user, "RF_RF04_SHOE_AGAIN", 3.0); break; }
            shoeDone = true;
            StartSequence(L_SHOE, user);
            break;
        case L_TURNSTILE:
            if (turnstileDone) break;
            turnstileDone = true;
            t.A_StartSound("rf/luna/turnstile", CHAN_AUTO, 0, 1.0);
            SetSceneTexture(L_COUNTER, "RF4_C618");
            LiftBar(L_TURNSTILE);
            Say(user, "RF_RF04_TURNSTILE", 5.0);
            Objective(8);
            break;
        case L_MIRROR:
            if (mirrorDone) break;
            mirrorDone = true;
            mirrorSpot = t;
            StartSequence(L_MIRROR, user);
            break;
        case L_JUKEBOX:
            if (seqScene != 0) break;
            if (jukeboxStage == 0)
            {
                jukeboxStage = 1;
                t.SetStateLabel("Uncovered");
                t.A_StartSound("rf/luna/tarp", CHAN_AUTO, 0, 0.9);
                Say(user, "RF_RF04_JUKEBOX_1", 6.0);
            }
            else if (jukeboxStage == 1)
            {
                jukeboxStage = 2;
                StartSequence(L_JUKEBOX, user);
            }
            else Say(user, "RF_RF04_JUKEBOX_AGAIN", 3.0);
            break;
        }
    }

    void StartHut(Actor user)
    {
        if (hutStage != 0) return;
        hutStage = 1;
        StartSequence(L_HUT, user);
        Objective(1);
    }

    // ------------------------------------------------------------------ lines
    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        int scene = e.ActivatedLine.GetUDMFInt('user_scene');
        switch (scene)
        {
        case L_HUT:
            StartHut(e.Thing);
            break;
        case L_BROOKLYN:
            if (brooklynDone) break;
            brooklynDone = true;
            Say(e.Thing, "RF_RF04_BROOKLYN", 6.0);
            break;
        case L_NIAGARA:
            if (niagaraDone) break;
            niagaraDone = true;
            Say(e.Thing, "RF_RF04_NIAGARA", 6.0);
            break;
        case L_MOTOR:
            if (motorDone) break;
            motorDone = true;
            Say(e.Thing, "RF_RF04_MOTOR", 7.0);
            break;
        case L_HALL:
            if (hallDone) break;
            hallDone = true;
            Say(e.Thing, "RF_RF04_HALL", 6.0);
            break;
        }
    }

    // ------------------------------------------------------------------ tick
    override void WorldTick()
    {
        if (!active || !playeringame[0]) return;
        Actor pl = players[0].mo;
        if (pl == null) return;
        TickHutEmpty(pl);
        TickSequence(pl);
    }

    // When he turns round after the barrier, the hut is empty and the glass carries ERREUR Ø (l. 515-517).
    void TickHutEmpty(Actor pl)
    {
        if (hutStage != 5 || pl.health <= 0) return;
        let it = ThinkerIterator.Create('RFSceneSpot');
        RFSceneSpot spot;
        while ((spot = RFSceneSpot(it.Next())) != null)
        {
            if (spot.args[0] != L_GLASSLOOK) continue;
            double d = pl.Distance2D(spot);
            if (d < 200 || d > 900 || RFParis.Facing(pl, spot.Pos.XY) > 30 || !pl.CheckSight(spot, SF_IGNOREVISIBILITY)) return;
            hutStage = 6;
            if (guard != null) guard.Destroy();
            SetSceneTexture(L_GLASS, "RF4_VIT1");
            Say(pl, "RF_RF04_HUT_EMPTY", 6.0);
            if (CVar.GetCVar('rf_dev_autopilot').GetBool() || CVar.GetCVar('rf_dev_log').GetBool())
                Console.Printf("RF_DEV_SCENE key=HUT_EMPTY t=%d", Level.maptime);
            return;
        }
    }

    void TickSequence(Actor pl)
    {
        if (seqScene == 0) return;
        Actor u = seqUser != null ? seqUser : pl;
        int t = seqTic++;
        switch (seqScene)
        {
        case L_HUT:            // l. 465-479: "Tu es en retard." ... "Si tu veux."
            if (t == 0) { if (guard != null) guard.SetStateLabel("Talk"); Say(u, "RF_RF04_HUT_1", 4.0); }
            else if (t == 110) Say(u, "RF_RF04_HUT_2", 4.0);
            else if (t == 220) Say(u, "RF_RF04_HUT_3", 5.0);
            else if (t == 360)
            {
                Say(u, "RF_RF04_HUT_4", 5.0);
                if (guard != null) guard.SetStateLabel("Spawn");
                hutStage = 2;
                Objective(1);
                seqScene = 0;
            }
            break;
        case L_CLOCK:          // l. 481-493: the card in the clock, 06:06; "Celui où ils entrent." "Toujours les mêmes."
            if (t == 0)
            {
                Say(u, "RF_RF04_CLOCK_1", 4.0);
                u.A_StartSound("rf/luna/clock", CHAN_AUTO, 0, 1.0);
            }
            else if (t == 40)
            {
                u.TakeInventory('RFTimeCard', 1);
                u.GiveInventory('RFTimeCardPunched', 1);
                Say(u, "RF_RF04_CLOCK_2", 5.0);
            }
            else if (t == 200) { if (guard != null) guard.SetStateLabel("Talk"); Say(u, "RF_RF04_CLOCK_3", 5.0); }
            else if (t == 360)
            {
                Say(u, "RF_RF04_CLOCK_4", 5.0);
                if (guard != null) guard.SetStateLabel("Spawn");
                Objective(2);
                seqScene = 0;
            }
            break;
        case L_KEYS:           // l. 495-513: the key of the substation, "Pas celle-là." ... "Tu l'entendras."
            if (t == 0)
            {
                u.A_StartSound("rf/luna/keys", CHAN_AUTO, 0, 1.0);
                u.GiveInventory('RFSousStationKey', 1);
                SetSceneTexture(L_KEYS, "RF4_CLE4");
                Say(u, "RF_RF04_KEYS_1", 5.0);
            }
            else if (t == 150) { if (guard != null) guard.SetStateLabel("Talk"); Say(u, "RF_RF04_KEYS_2", 5.0); }
            else if (t == 300)
            {
                Say(u, "RF_RF04_KEYS_3", 5.0);
                if (guard != null) guard.SetStateLabel("Spawn");
                LiftBar(L_BARRIER);
                hutStage = 5;
                Objective(3);
                Wake(BARRIER_WAVE_TID, u);       // "Celui où ils entrent" (l. 489): the staff come in by the service door
                seqScene = 0;
            }
            break;
        case L_SHOE:           // l. 525-527
            if (t == 0) Say(u, "RF_RF04_SHOE_1", 5.0);
            else if (t == 150) Say(u, "RF_RF04_SHOE_2", 6.0);
            else if (t == 330) { Say(u, "RF_RF04_SHOE_3", 3.0); seqScene = 0; }
            break;
        case L_MIRROR:         // l. 533-539: black in his own panel, the grey smock in the next, then the shirt and badge
            if (t == 0) { Say(u, "RF_RF04_MIRROR_1", 5.0); greyImage = MirrorOutfit('RFViktorMirrorGrey', 90, u); }
            else if (t == 160) { Say(u, "RF_RF04_MIRROR_2", 5.0); shirtImage = MirrorOutfit('RFViktorMirrorShirt', -90, u); }
            else if (t == 320)
            {
                Say(u, "RF_RF04_MIRROR_3", 4.0);
                if (greyImage != null) greyImage.Destroy();
                if (shirtImage != null) shirtImage.Destroy();
                seqScene = 0;
            }
            break;
        case L_JUKEBOX:        // l. 547-549: he presses; nothing; the motor answers by three knocks
            if (t == 0)
            {
                u.A_StartSound("rf/luna/jukeboxkey", CHAN_AUTO, 0, 1.0);
                Say(u, "RF_RF04_JUKEBOX_2", 3.0);
            }
            else if (t == 70)
            {
                u.A_StartSound("rf/luna/knocks", CHAN_AUTO, 0, 1.0, ATTN_NONE);
                Say(u, "RF_RF04_JUKEBOX_3", 4.0);
            }
            else if (t == 140)
            {
                Objective(9);
                Wake(JUKEBOX_WAVE_TID, u);
                seqScene = 0;
            }
            break;
        default:
            seqScene = 0;
        }
    }
}
