// Level director: objective text, use prompts and the few scripted gates of RF01.
// Enemy wake-ups use native Thing_Activate lines; door gating uses native locks.
class RFDirector : EventHandler
{
    String objective;      // current short objective (HUD)
    String usePrompt;      // prompt when facing a readable/usable object
    bool winchUsed;        // porch grille raised from the porter's lodge
    int titleTics;         // level title flash timer
    int notesRead;

    override void WorldLoaded(WorldEvent e)
    {
        titleTics = e.IsSaveGame ? 0 : 35 * 5;
        if (!e.IsSaveGame)
        {
            objective = "";
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
            if (index == 3) objective = StringTable.Localize("$RF_OBJ_LODGE");
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
            objective = StringTable.Localize("$RF_OBJ_PORCH");
            e.Thing.A_Print(StringTable.Localize("$RF_MSG_WINCH"), 5.0);
            e.Thing.A_StartSound("rf/world/winch", CHAN_AUTO, 0, 1.0, ATTN_NONE);
        }
        // Thing_Activate lines carry objective updates through their arg1 code.
        if (line.special == 130)
        {
            int code = line.args[1];
            if (code == 1) objective = StringTable.Localize("$RF_OBJ_GRILLE");
            else if (code == 2) objective = StringTable.Localize("$RF_OBJ_ADMISSIONS");
            else if (code == 3) objective = StringTable.Localize("$RF_OBJ_COURT");
            else if (code == 4) objective = StringTable.Localize("$RF_OBJ_LINGERIE");
            else if (code == 5) objective = StringTable.Localize("$RF_OBJ_REGISTRES");
            else if (code == 6) objective = StringTable.Localize("$RF_OBJ_EXIT");
        }
    }

    override void WorldThingSpawned(WorldEvent e)
    {
    }

    override void WorldTick()
    {
        if (titleTics > 0) titleTics--;
        usePrompt = "";
        if (!playeringame[0]) return;
        Actor person = players[0].mo;
        if (person == null || person.health <= 0) return;
        // Prompt for readable notes in front of the player.
        let notes = ThinkerIterator.Create('RFNote');
        RFNote note;
        while ((note = RFNote(notes.Next())) != null)
        {
            if (person.Distance2D(note) > 72 || !person.CheckSight(note)) continue;
            Vector2 delta = note.Pos.XY - person.Pos.XY;
            double facing = delta.X * cos(person.angle) + delta.Y * sin(person.angle);
            if (facing < delta.Length() * 0.7) continue;
            usePrompt = StringTable.Localize("$RF_PROMPT_READ");
            break;
        }
    }
}
