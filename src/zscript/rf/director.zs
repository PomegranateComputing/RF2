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
        if (!(Level.MapName ~== "RF01") || e.ActivatedLine == null || e.Thing == null) return;
        let line = e.ActivatedLine;
        // Door_Open on tag 50: the porch grille winch.
        if (line.special == 11 && line.args[0] == 50 && !winchUsed)
        {
            winchUsed = true;
            SetObjective(8);
            e.Thing.A_Print(StringTable.Localize("$RF_MSG_WINCH"), 5.0);
            e.Thing.A_StartSound("rf/world/winch", CHAN_AUTO, 0, 1.0, ATTN_NONE);
        }
        // Trigger lines carry objective updates in their UDMF field user_objective.
        SetObjective(line.GetUDMFInt('user_objective'));
        if (line.GetUDMFInt('user_outro') > 0) StartOutro(e.Thing);
    }

    // Objectives only move forward: backtracking over an old trigger never regresses them.
    void SetObjective(int code)
    {
        if (code <= objectiveCode) return;
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
        if (!playeringame[0]) return;
        Actor person = players[0].mo;
        if (person == null || person.health <= 0) return;
        usePrompt = FacedLine(person);
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
            break;
        }
    }
}
