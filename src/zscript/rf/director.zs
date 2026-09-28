// Level director: objective text, use prompts and the few scripted gates of RF01.
// Enemy wake-ups use native Thing_Activate lines; door gating uses native locks.
class RFDirector : EventHandler
{
    String objective;      // current short objective (HUD)
    int usePrompt;         // what the player faces: 0 nothing, 1 note (read), 2 closed door (open), 3 mechanism (operate)
    int objectiveCode;     // RF01 objective index, see SetObjective
    bool winchUsed;        // porch grille raised from the porter's lodge
    int titleTics;         // level title flash timer
    bool outro;            // level ending: fade, exit text, then the next map
    bool exiting;
    int outroTics;
    int notesRead;
    Actor promptThing;     // the note or scene object the prompt designates (chapters after RF01: see WorldTick)

    override void WorldLoaded(WorldEvent e)
    {
        titleTics = e.IsSaveGame ? 0 : 35 * 5;
        outro = false;
        exiting = false;
        outroTics = 0;
        if (!e.IsSaveGame)
        {
            objective = "";
            objectiveCode = 0;
            winchUsed = false;
            notesRead = 0;
            if (Level.MapName ~== "RF01") objective = StringTable.Localize("$RF_OBJ_WAKE");
            else
            {
                objective = ChapterObjective(0);
                StartingKit();
            }
        }
    }

    // A chapter after RF01 started on its own (chapter select, development) gets what Viktor carries out of
    // Sainte-Anne; arriving from the previous chapter, the inventory is already there and nothing is given.
    void StartingKit()
    {
        if (!playeringame[0] || players[0].mo == null) return;
        Actor pl = players[0].mo;
        if (pl.FindInventory('RFBrowning') == null)
        {
            pl.GiveInventory('RFBrowning', 1);
            pl.GiveInventory('RFPistolAmmo', 24);
        }
        if (pl.FindInventory('RFFAL') == null)
        {
            pl.GiveInventory('RFFAL', 1);
            pl.GiveInventory('RFRifleAmmo', 20);
        }
    }

    void NoteRead(int index, Actor user)
    {
        notesRead++;
        if (Level.MapName ~== "RF01")
        {
            if (index == 3) SetObjective(7);
        }
    }

    override void WorldLinePreActivated(WorldEvent e)
    {
        if (!(Level.MapName ~== "RF01") || e.ActivatedLine == null) return;
        // The finale wave line (Thing_Activate on tid 700) is inert until the winch is used.
        if (e.ActivatedLine.special == 130 && e.ActivatedLine.args[0] == 700 && !winchUsed)
            e.ShouldActivate = false;
    }

    override void WorldLineActivated(WorldEvent e)
    {
        if (e.ActivatedLine == null || e.Thing == null) return;
        let line = e.ActivatedLine;
        // Door_Open on tag 50: the porch grille winch (RF01).
        if (Level.MapName ~== "RF01" && line.special == 11 && line.args[0] == 50 && !winchUsed)
        {
            winchUsed = true;
            SetObjective(8);
            e.Thing.A_Print(StringTable.Localize("$RF_MSG_WINCH"), 5.0);
            e.Thing.A_StartSound("rf/world/winch", CHAN_AUTO, 0, 1.0, ATTN_NONE);
        }
        // Trigger lines carry objective updates in their UDMF field user_objective, the ending in user_outro
        // (every chapter).
        SetObjective(line.GetUDMFInt('user_objective'));
        if (line.GetUDMFInt('user_outro') > 0) StartOutro(e.Thing);
    }

    // Objectives of the chapters after RF01: LANGUAGE RF_OBJ_<MAP>_<code>, "" when undefined.
    static String ChapterObjective(int code)
    {
        String key = String.Format("RF_OBJ_%s_%d", Level.MapName.MakeUpper(), code);
        String text = StringTable.Localize("$" .. key);
        return text == key ? "" : text;
    }

    // Objectives only move forward: backtracking over an old trigger never regresses them.
    void SetObjective(int code)
    {
        if (code <= objectiveCode) return;
        if (!(Level.MapName ~== "RF01"))
        {
            String text = ChapterObjective(code);
            if (text == "") return;
            objectiveCode = code;
            objective = text;
            return;
        }
        String key;
        switch (code)
        {
            case 1: key = "$RF_OBJ_GRILLE"; break;
            case 2: key = "$RF_OBJ_GRILLE_OPEN"; break;
            case 3: key = "$RF_OBJ_ADMISSIONS"; break;
            case 4: key = "$RF_OBJ_COURT"; break;
            case 5: key = "$RF_OBJ_LINGERIE"; break;
            case 6: key = "$RF_OBJ_REGISTRES"; break;
            case 7: key = "$RF_OBJ_LODGE"; break;
            case 8: key = "$RF_OBJ_PORCH"; break;
            case 9: key = "$RF_OBJ_EXIT"; break;
            default: return;
        }
        objectiveCode = code;
        objective = StringTable.Localize(key);
    }

    override void WorldThingSpawned(WorldEvent e)
    {
    }

    // A usable line straight ahead within use range: a closed door (2) or another mechanism (3).
    int FacedLine(Actor person)
    {
        Vector2 fwd = (cos(person.angle), sin(person.angle));
        let it = BlockLinesIterator.Create(person, 72);
        while (it.Next())
        {
            Line l = it.CurLine;
            if (l.special == 0 || !(l.activation & SPAC_Use)) continue;
            Vector2 mid = (l.v1.p + l.v2.p) / 2;
            Vector2 d = mid - person.Pos.XY;
            double len = d.Length();
            if (len > 68 || len < 1 || (d.X * fwd.X + d.Y * fwd.Y) < len * 0.75) continue;
            bool door = l.special == 11 || l.special == 12 || l.special == 13;
            if (door && l.frontsector != null && l.backsector != null)
            {
                double hf = l.frontsector.CenterCeiling() - l.frontsector.CenterFloor();
                double hb = l.backsector.CenterCeiling() - l.backsector.CenterFloor();
                if (min(hf, hb) < 56) return 2;      // this line bounds a closed door
                if (l.frontsector != l.backsector) continue;   // open door: nothing to do
            }
            return 3;                                  // switch, winch, remote door
        }
        return 0;
    }

    // The ending: the player stops in the street, the view fades and the exit text is read.
    void StartOutro(Actor who)
    {
        if (outro) return;
        outro = true;
        outroTics = 0;
        if (who != null && who.player != null)
        {
            who.player.cheats |= CF_TOTALLYFROZEN | CF_GODMODE;
            who.Vel = (0, 0, 0);
        }
    }

    override void WorldTick()
    {
        if (outro)
        {
            outroTics++;
            usePrompt = 0;
            bool skip = outroTics > 35 * 3 && playeringame[0] && (players[0].cmd.buttons & (BT_USE | BT_ATTACK));
            if (!exiting && (outroTics >= 35 * 11 || skip))
            {
                exiting = true;
                Level.ExitLevel(0, false);
            }
            return;
        }
        if (titleTics > 0) titleTics--;
        usePrompt = 0;
        promptThing = null;
        if (!playeringame[0]) return;
        Actor person = players[0].mo;
        if (person == null || person.health <= 0) return;
        usePrompt = FacedLine(person);
        FindPromptThing(person);
        // After RF01 the prompt is a promise: the use key reaches the object it names, even when the engine's
        // use trace would stop at the edge of the table it lies on or miss a small object by a few units.
        // (RF01 keeps its accepted behaviour.)
        let pl = players[0];
        if ((pl.cmd.buttons & BT_USE) && !(pl.oldbuttons & BT_USE)) UsePressed(person, false);
    }

    // The use key was pressed: the object named by the prompt is used (chapters after RF01). The development
    // autopilot presses through here too (its press lands after this handler's tick), with refresh = true.
    void UsePressed(Actor person, bool refresh)
    {
        if (Level.MapName ~== "RF01" || person == null) return;
        if (refresh) FindPromptThing(person);
        if (promptThing != null) promptThing.Used(person);
    }

    void FindPromptThing(Actor person)
    {
        // Prompt for the scene objects of a chapter (RFInteract) in front of the player.
        let things = ThinkerIterator.Create('RFInteract');
        RFInteract thing;
        while ((thing = RFInteract(things.Next())) != null)
        {
            if (person.Distance2D(thing) > 72 + thing.radius || !person.CheckSight(thing)) continue;
            Vector2 delta = thing.Pos.XY - person.Pos.XY;
            double facing = delta.X * cos(person.angle) + delta.Y * sin(person.angle);
            // Within 45 degrees, or within 72 degrees when the object is right against the player (40 units).
            if (facing < delta.Length() * (delta.Length() < 40 ? 0.3 : 0.7)) continue;
            usePrompt = thing.prompt;
            promptThing = thing;
            return;
        }
        // Prompt for readable notes in front of the player.
        let notes = ThinkerIterator.Create('RFNote');
        RFNote note;
        while ((note = RFNote(notes.Next())) != null)
        {
            if (person.Distance2D(note) > 72 || !person.CheckSight(note)) continue;
            Vector2 delta = note.Pos.XY - person.Pos.XY;
            double facing = delta.X * cos(person.angle) + delta.Y * sin(person.angle);
            if (facing < delta.Length() * 0.7) continue;
            usePrompt = 1;
            promptThing = note;
            break;
        }
    }
}
