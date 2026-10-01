// Transition pages between chapters (owner's request of 01/10/2026): a page of 1980s black comic art (Codex) shown
// when a chapter ends, its panels revealed in reading order and its captions composed by the game over the art.
// The scenes are data: the lump COMICDEF (one scene per transition, see the file). The ending of a chapter
// (RFDirector.StartOutro) plays the page when the scene of "this map -> next map" exists and its image is in the
// build; otherwise the chapter's exit text, as before. Rules (docs/RF2_TRANSITIONS.md):
// - the player reads at his pace: Use or Fire shows the next panel, then closes the page; holding Use one second,
//   or Jump, passes the whole page;
// - closing or passing the page leaves the chapter once (Level.ExitLevel) and the inventory travels once;
// - the press that closes the page is swallowed: the next chapter starts with the player held until every button is
//   released (RFDirector.BeginArrivalHold / TickArrival), so it never becomes a shot or a use;
// - a save made during the page reloads at the panel reached (the director's state is in the save).

class RFComicScene
{
    String id, from, to, page;
    Array<int> panels;      // x, y, w, h per panel, in pixels of the page (1920 x 1080)
    Array<String> captions; // LANGUAGE key (with its dollar sign) or plain text
    Array<int> zones;       // x, y, w, h per caption, page pixels
    Array<int> after;       // the panel (1-based) after which each caption appears
    Array<int> styles;      // 0 a cream box over the art, 1 cream text centred on the page's black band

    int PanelCount() { return panels.Size() / 4; }

    // The scene of the transition from -> to, or null. COMICDEF lines (# starts a comment):
    //   scene <ID> <FROM> <TO> <page image path>
    //   panel <x> <y> <w> <h>
    //   caption <after panel> <LANGUAGE key> <x> <y> <w> <h> [band]
    static RFComicScene Find(String from, String to)
    {
        int lump = Wads.FindLump("COMICDEF", 0, Wads.AnyNamespace);
        if (lump < 0) return null;
        Array<String> lines;
        Wads.ReadLump(lump).Split(lines, "\n");
        RFComicScene cur = null;
        for (int i = 0; i < lines.Size(); i++)
        {
            String l = lines[i];
            l.Replace("\r", "");
            l.Replace("\t", " ");
            l.StripLeftRight();
            if (l == "" || l.Left(1) == "#") continue;
            Array<String> w;
            l.Split(w, " ", TOK_SKIPEMPTY);
            if (w[0] == "scene" && w.Size() >= 5)
            {
                if (cur != null) return cur;                 // the wanted scene ended
                if (w[2] ~== from && w[3] ~== to)
                {
                    cur = new('RFComicScene');
                    cur.id = w[1]; cur.from = w[2]; cur.to = w[3]; cur.page = w[4];
                }
            }
            else if (cur != null && w[0] == "panel" && w.Size() >= 5)
            {
                for (int k = 1; k <= 4; k++) cur.panels.Push(w[k].ToInt());
            }
            else if (cur != null && w[0] == "caption" && w.Size() >= 7)
            {
                cur.after.Push(w[1].ToInt());
                cur.captions.Push(w[2]);
                for (int k = 3; k <= 6; k++) cur.zones.Push(w[k].ToInt());
                cur.styles.Push(w.Size() >= 8 && w[7] ~== "band" ? 1 : 0);
            }
        }
        return cur;
    }
}
