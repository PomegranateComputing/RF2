// RF07 - Jerma, facade maritime (novel l. 733-763; docs/production/maps/RF07_FICHE.md, RF07_RF12_DECOUPAGE.md).
// The Jerma chapter has no combat (owner's decision of 01/10): Elvis waits on the terrace, Viktor turns round to the
// gutted room where the corridor was, the watch says 22 December 2022, 14:58, +2; Elvis leads him through the hotel
// down the service stair, where they lift the rusted bedframe together: "C'est la." Elvis is never a target: he is not
// shootable, does not block, cannot be hurt.

class RFWaterBottle : Inventory { Default { Inventory.MaxAmount 1; Tag "$RF_ITEM_WATER"; +INVENTORY.UNDROPPABLE } }

// A point of Elvis's way, in order (args[0] = 1, 2, ...).
class RFElvisPoint : Actor
{
    Default { +NOGRAVITY; +NOBLOCKMAP; +NOINTERACTION; RenderStyle "None"; }
    States { Spawn: TNT1 A -1; Stop; }
}

// Elvis (l. 735): tall, a dark beanie, a headlamp round his neck. PROVISIONAL silhouette until his figure (CAN-017).
// He walks ahead of Viktor from point to point once the scene sends him, and waits when Viktor is too far behind.
class RFElvis : Actor
{
    Array<Actor> way;
    int next, playerAhead;
    bool going, arrived;
    int walkTics;

    Default
    {
        Radius 14;
        Height 56;
        Scale 0.47;
        Speed 3.2;
        MaxStepHeight 24;
        -SOLID
        +NOBLOOD
        +DONTTHRUST
        +NOTARGET
        +DONTSPLASH
    }

    // His way, in order; built the first time he is sent (the map's points may spawn after him).
    void FindWay()
    {
        way.Clear();
        let it = ThinkerIterator.Create('RFElvisPoint');
        Actor p;
        Array<Actor> all;
        while ((p = Actor(it.Next())) != null) all.Push(p);
        for (int k = 1; k <= all.Size(); k++)
            for (int i = 0; i < all.Size(); i++)
                if (all[i].args[0] == k) way.Push(all[i]);
    }

    override void Tick()
    {
        Super.Tick();
        if (isFrozen()) return;
        let pl = players[consoleplayer].mo;
        if (going && way.Size() == 0) FindWay();
        if (!going || arrived || next >= way.Size())
        {
            if (pl != null && (!going || arrived)) A_Face(pl, 4);
            if (curstate != FindState("Spawn") && walkTics > 0) { walkTics = 0; SetStateLabel("Spawn"); }
            return;
        }
        Vector2 d = way[next].Pos.XY - Pos.XY;
        // Viktor's progress along the way: the furthest point he has come near. Elvis waits for him when he is far
        // behind; when Viktor has gone ahead, Elvis hurries.
        if (pl != null)
            for (int k = playerAhead + 1; k < way.Size(); k++)
                if (pl.Distance2D(way[k]) < 160) playerAhead = k;
        bool far = pl != null && Distance2D(pl) > 300;
        if (far && playerAhead < next)
        {
            A_Face(pl, 8);
            if (walkTics > 0) { walkTics = 0; SetStateLabel("Spawn"); }
            return;
        }
        double pace = far ? Speed * 2 : Speed;
        double len = d.Length();
        if (len < 8)
        {
            if (++next >= way.Size()) arrived = true;
            return;
        }
        angle = VectorAngle(d.X, d.Y);
        if (!TryMove(Pos.XY + d / len * min(pace, len), true))
            SetOrigin((Pos.XY + d / len * min(pace, len), Pos.Z), true);    // a doorframe's corner: he slips past it
        if (walkTics++ == 0) SetStateLabel("Walk");
    }

    States
    {
    Spawn: R7EV A -1; Stop;
    Walk: R7EV BC 8; Loop;
    }
}

// The bedframe across the door of the burnt room (l. 761): used when Elvis is there, they lift it together.
class RFJermaBed : RFInteract
{
    Default { Radius 20; Height 48; Scale 0.5; RFInteract.Prompt 3; }
    override bool Used(Actor user)
    {
        if (user == null || user.player == null) return false;
        let j = RFJerma(EventHandler.Find('RFJerma'));
        if (j != null) j.LiftBed(self, user);
        return true;
    }
    States { Spawn: R7SB A -1; Stop; Lifted: R7SB B -1; Stop; }
}

class RFJerma : EventHandler
{
    const J_BEHIND = 1;       // RFSceneSpot: the gutted room, looked back at
    const J_HALLS = 2;        // walk line: into the hotel
    const J_STAIR = 3;        // walk line: the service stair
    const J_BED = 4;          // the bedframe's blocking line (lifted)
    const ROOM_DOOR_TAG = 70;

    bool active;
    int stage;                // 0 arrival, 1 greeted, 2 turned round, 3 talking, 4 following, 5 at the bed, 6 lifted, 7 done
    int stageTic, watchTic;
    bool hallsDone, stairDone, bedNoted;
    Actor elvis;

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "RF07";
        if (!active) return;
        elvis = Actor(ThinkerIterator.Create('RFElvis').Next());
    }

    static void Say(Actor to, String key, double seconds = 5.0) { RFParis.Say(to, key, seconds); }
    static void Objective(int code) { RFParis.Objective(code); }

    void Next(int s) { stage = s; stageTic = Level.maptime; }

    override void WorldTick()
    {
        if (!active || !playeringame[0]) return;
        Actor pl = players[0].mo;
        if (pl == null) return;
        int t = Level.maptime - stageTic;
        let el = RFElvis(elvis);
        if (el != null && Level.maptime % 70 == 0
            && (CVar.GetCVar('rf_dev_autopilot').GetBool() || CVar.GetCVar('rf_dev_log').GetBool()))
            Console.Printf("RF_DEV_ELVIS t=%d stage=%d x=%.0f y=%.0f z=%.0f next=%d/%d going=%d arrived=%d dist=%.0f",
                           Level.maptime, stage, el.Pos.X, el.Pos.Y, el.Pos.Z, el.next, el.way.Size(), el.going,
                           el.arrived, pl.Distance2D(el));
        switch (stage)
        {
        case 0:               // l. 735-737: he was waiting by a broken bay window
            if (Level.maptime > 70 && (el == null || pl.Distance2D(el) < 420 || Level.maptime > 210))
            {
                Say(pl, "RF_RF07_ARRIVE", 4.0);
                Objective(1);
                Next(1);
            }
            break;
        case 1:               // l. 739-743: he turns round; behind him, no corridor any more
            if (LookedBehind(pl) || t > 35 * 12)
            {
                Say(pl, "RF_RF07_BEHIND", 7.0);
                Next(2);
            }
            break;
        case 2:               // l. 745-755
            if (t == 230) Say(pl, "RF_RF07_WORK_1", 3.0);
            else if (t == 330) Say(pl, "RF_RF07_WORK_2", 4.0);
            else if (t == 460) { Say(pl, "RF_RF07_WATCH", 6.0); watchTic = Level.maptime; }
            else if (t == 680) { Say(pl, "RF_RF07_WATER", 4.0); pl.GiveInventory('RFWaterBottle', 1); }
            else if (t == 820)
            {
                Say(pl, "RF_RF07_ROOM", 5.0);
                Objective(2);
                if (el != null) el.going = true;
                Next(4);
            }
            break;
        case 4:               // following him; at the landing the bedframe blocks the door (l. 761)
            if (el != null && el.arrived && pl.Distance2D(el) < 200 && !bedNoted)
            {
                bedNoted = true;
                Say(pl, "RF_RF07_BED_1", 5.0);
                Objective(3);
                Next(5);
            }
            break;
        case 6:               // l. 761-763: the black line on their palms; "C'est la."
            if (t == 180)
            {
                Say(pl, "RF_RF07_HERE", 3.0);
                Level.ExecuteSpecial(11, pl, null, false, ROOM_DOOR_TAG, 24);      // Door_Open
                Objective(4);
                Next(7);
            }
            break;
        }
    }

    // The gutted room behind him (RFSceneSpot args[0] = J_BEHIND), in front of him and in sight.
    bool LookedBehind(Actor pl)
    {
        let it = ThinkerIterator.Create('RFSceneSpot');
        RFSceneSpot spot;
        while ((spot = RFSceneSpot(it.Next())) != null)
        {
            if (spot.args[0] != J_BEHIND) continue;
            return pl.Distance2D(spot) < 700 && RFParis.Facing(pl, spot.Pos.XY) < 35 && pl.CheckSight(spot, SF_IGNOREVISIBILITY);
        }
        return false;
    }

    void LiftBed(Actor bed, Actor user)
    {
        let el = RFElvis(elvis);
        if (stage != 5 || el == null || !el.arrived) return;
        Say(user, "RF_RF07_BED_2", 6.0);
        user.A_StartSound("rf/luna/keys", CHAN_AUTO, 0, 0.6);
        bed.SetStateLabel("Lifted");
        bed.SetOrigin(bed.Pos + (0, 40, 0), true);
        for (int i = 0; i < Level.Lines.Size(); i++)
        {
            Line l = Level.Lines[i];
            if (l.GetUDMFInt('user_scene') != J_BED) continue;
            l.flags &= ~(Line.ML_BLOCKING | Line.ML_BLOCKMONSTERS | Line.ML_BLOCKEVERYTHING);
        }
        Next(6);
    }

    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        switch (e.ActivatedLine.GetUDMFInt('user_scene'))
        {
        case J_HALLS: if (!hallsDone) { hallsDone = true; Say(e.Thing, "RF_RF07_HALLS", 7.0); } break;
        case J_STAIR: if (!stairDone) { stairDone = true; Say(e.Thing, "RF_RF07_STAIR", 4.0); } break;
        }
    }

    // l. 751: the watch works; beside the hour a small +2 blinks without explanation.
    override void RenderOverlay(RenderEvent e)
    {
        if (!active || watchTic <= 0) return;
        int t = Level.maptime - watchTic;
        if (t < 0 || t > 35 * 7) return;
        Font f = Font.GetFont('RFHud');
        if (f == null) f = SmallFont;
        double s = max(Screen.GetHeight() / 1080.0 * 2.2, 1.0);
        double a = clamp(min(t / 20.0, (35 * 7 - t) / 20.0), 0.0, 1.0);
        String date = "22.12.2022   14:58";
        double w = f.StringWidth(date) * s;
        double x = (Screen.GetWidth() - w) / 2, y = Screen.GetHeight() * 0.62;
        Screen.Dim(0, 0.55 * a, int(x - 24 * s), int(y - 10 * s), int(w + 70 * s), int(f.GetHeight() * s + 20 * s));
        Screen.DrawText(f, Font.CR_WHITE, x, y, date, DTA_ScaleX, s, DTA_ScaleY, s, DTA_Alpha, a);
        if ((t / 12) % 2 == 0)
            Screen.DrawText(f, Font.CR_WHITE, x + w + 10 * s, y + f.GetHeight() * s * 0.35, "+2",
                            DTA_ScaleX, s * 0.6, DTA_ScaleY, s * 0.6, DTA_Alpha, a);
    }
}
