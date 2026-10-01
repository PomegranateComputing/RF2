// RF06 - La sortie du personnel: the corridor that should not fit in the building (novel l. 709-731; fiche
// docs/production/maps/RF06_FICHE.md). The bare bulbs light ahead of Viktor and go out behind him; the roller
// coaster's rumble becomes the ventilation of a hotel; voices ahead and the beam of a lamp (never hostile).

class RFCorridor : EventHandler
{
    const PIECE_TAG = 600;       // corridor piece i: sector tag and lamp tid 600 + i
    const MAX_PIECES = 80;
    const C_VOICES = 1;
    const C_BEAM = 2;
    const C_RUMBLE = 3;
    const C_ERREUR = 5;
    const C_PAINT = 6;

    const BEAM_TID = 690;

    bool active;
    Array<int> pieceOf;          // sector index -> piece (-1 elsewhere); rebuilt on every load
    int pieces;                  // the pieces of the map's corridor (counted from the sector tags)
    int litPiece;                // the piece whose lamps are on around it (-1 none yet)
    bool synced;                 // the lamps set to litPiece since the map (or the save) was loaded
    bool voicesDone, rumbleDone, erreurDone, paintDone;
    int seqTic;                  // voices sequence
    Actor beam;
    int beamTics;

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "RF06";
        if (!active) return;
        pieceOf.Clear();
        for (int s = 0; s < Level.Sectors.Size(); s++) pieceOf.Push(-1);
        // A piece is marked by the UDMF sector field user_piece (piece + 1), which leaves the tags to the slabs of
        // the corridor (its pipes); maps of 30/09 marked them by the tag 600 + piece.
        pieces = 0;
        for (int s = 0; s < Level.Sectors.Size(); s++)
        {
            int p = Level.Sectors[s].GetUDMFInt('user_piece') - 1;
            if (p >= 0) { pieceOf[s] = p; pieces = max(pieces, p + 1); }
        }
        if (pieces == 0)
        {
            for (int i = 0; i < MAX_PIECES; i++)
            {
                let it = Level.CreateSectorTagIterator(PIECE_TAG + i);
                int sec;
                while ((sec = it.Next()) >= 0) { pieceOf[sec] = i; pieces = i + 1; }
            }
        }
        if (!e.IsSaveGame) litPiece = -1;
        synced = false;
    }

    void SetLamp(int piece, bool on)
    {
        let it = Level.CreateActorIterator(PIECE_TAG + piece);
        Actor a;
        while ((a = it.Next()) != null) { if (on) a.Activate(null); else a.Deactivate(null); }
    }

    // The lamps of the pieces from one behind to three ahead are on; the others are out. all: set every lamp, not
    // only those that change.
    void Light(int piece, bool all = false)
    {
        if (piece == litPiece && !all) return;
        for (int i = 0; i < pieces; i++)
        {
            bool on = i >= piece && i <= piece + 3;
            bool was = litPiece >= 0 && i >= litPiece && i <= litPiece + 3;
            if (all || on != was) SetLamp(i, on);
        }
        litPiece = piece;
    }

    override void WorldTick()
    {
        if (!active || !playeringame[0]) return;
        Actor pl = players[0].mo;
        if (pl == null) return;
        // A lamp attaches its light in its first tic (DynamicLight.PostBeginPlay): one switched on before that stays
        // dark, so the first lighting waits for tic 2, and sets every lamp (after a load as well).
        if (Level.maptime < 2) return;
        int sec = pl.CurSector.Index();
        int piece = sec >= 0 && sec < pieceOf.Size() ? pieceOf[sec] : -1;
        if (!synced)
        {
            synced = true;
            Light(piece >= 0 ? piece : max(litPiece, 0), true);
        }
        else if (piece >= 0) Light(piece);
        TickVoices(pl);
        if (beam != null && --beamTics > 0) beam.SetOrigin(beam.Pos + (0, -4, 0), true);
        else if (beam != null) { beam.Deactivate(null); beam = null; }
    }

    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        switch (e.ActivatedLine.GetUDMFInt('user_scene'))
        {
        case C_ERREUR: if (!erreurDone) { erreurDone = true; RFParis.Say(e.Thing, "RF_RF06_ERREUR", 7.0); } break;
        case C_PAINT: if (!paintDone) { paintDone = true; RFParis.Say(e.Thing, "RF_RF06_PAINT", 7.0); } break;
        case C_RUMBLE:
            if (!rumbleDone)
            {
                rumbleDone = true;
                e.Thing.A_StartSound("rf/luna/rumble", CHAN_AUTO, 0, 1.0, ATTN_NONE);
                RFParis.Say(e.Thing, "RF_RF06_RUMBLE", 7.0);
            }
            break;
        case C_VOICES: if (!voicesDone) { voicesDone = true; seqTic = 1; } break;
        }
    }

    void TickVoices(Actor pl)
    {
        if (seqTic <= 0) return;
        int t = seqTic++ - 1;
        if (t == 0) RFParis.Say(pl, "RF_RF06_SLOPE", 4.0);
        else if (t == 120) RFParis.Say(pl, "RF_RF06_VOICES_1", 4.0);
        else if (t == 230) RFParis.Say(pl, "RF_RF06_VOICES_2", 4.0);
        else if (t == 330)
        {
            RFParis.Say(pl, "RF_RF06_VOICES_3", 4.0);
            let it = Level.CreateActorIterator(BEAM_TID);
            beam = it.Next();
            if (beam != null) { beam.Activate(null); beamTics = 30; }
            seqTic = -1;
        }
    }
}
