// RF2-UI-01 menus: a file in an institution that still runs. Charcoal, dirty paper, steel grey, deep
// oxblood as a rare signal. Engine functions are reused (new game chain, load/save, options pages,
// confirmations); only their presentation and navigation are RF. Text is rendered by the engine in the
// RF faces, never painted into an image. Layout is designed on a 1920x1080 frame scaled uniformly and
// centred, so 16:9, 16:10, 21:9 and 4:3 keep the same proportions.

// ------------------------------------------------------------------------------------------------ style
class RFUI ui
{
    const W = 1920.0;
    const H = 1080.0;
    // Palette (RF2 dossier maître §07: noir minéral, blancs institutionnels, gris du bâti, rouge grenade).
    const C_CHARCOAL = 0xFF0E0C0E;
    const C_PAPER = 0xFFE8E4DA;
    const C_PAPERDIM = 0xFFC9C4B8;
    const C_STEEL = 0xFF9A9A95;
    const C_STEELDIM = 0xFF6B6B68;
    const C_OXBLOOD = 0xFF7A1F2B;
    const C_OXBLOOD_HI = 0xFFA3303E;

    static double U() { return min(Screen.GetWidth() / W, Screen.GetHeight() / H); }
    static double OX() { return (Screen.GetWidth() - W * U()) / 2; }
    static double OY() { return (Screen.GetHeight() - H * U()) / 2; }
    static double SX(double x) { return OX() + x * U(); }
    static double SY(double y) { return OY() + y * U(); }

    static Font Face(Name n)
    {
        Font f = Font.GetFont(n);
        return f != null ? f : NewSmallFont;
    }

    // Width in design pixels of `text` drawn with line height `px`.
    static double TextW(Font f, String text, double px)
    {
        return f.StringWidth(StringTable.Localize(text)) * px / f.GetHeight();
    }

    // align: 0 left, 1 centre, 2 right.
    static void Text(Font f, String text, double x, double y, double px, int col, double alpha = 1.0, int align = 0)
    {
        String s = StringTable.Localize(text);
        double k = px * U() / f.GetHeight();
        double w = f.StringWidth(s) * k;
        double sx = SX(x);
        if (align == 1) sx -= w / 2;
        else if (align == 2) sx -= w;
        Screen.DrawText(f, Font.CR_UNTRANSLATED, sx, SY(y), s, DTA_ScaleX, k, DTA_ScaleY, k, DTA_Color, col, DTA_Alpha, alpha);
    }

    static void Fill(int col, double alpha, double x, double y, double w, double h)
    {
        if (alpha <= 0) return;
        int x0 = int(SX(x)), y0 = int(SY(y));
        int x1 = int(SX(x + w)), y1 = int(SY(y + h));
        if (x1 <= x0) x1 = x0 + 1;
        if (y1 <= y0) y1 = y0 + 1;
        Screen.Dim(col & 0xFFFFFF, alpha, x0, y0, x1 - x0, y1 - y0);
    }

    // Whole screen, not the design frame (ultrawide margins included).
    static void FillScreen(int col, double alpha)
    {
        Screen.Dim(col & 0xFFFFFF, alpha, 0, 0, Screen.GetWidth(), Screen.GetHeight());
    }

    // Horizontal gradient on the whole screen height, from `a0` at design x0 to `a1` at x1 (left of x0: a0).
    static void Gradient(int col, double x0, double x1, double a0, double a1)
    {
        int left = 0;
        int steps = 24;
        Screen.Dim(col & 0xFFFFFF, a0, 0, 0, int(SX(x0)), Screen.GetHeight());
        for (int i = 0; i < steps; i++)
        {
            double t = (i + 0.5) / steps;
            int sx0 = int(SX(x0 + (x1 - x0) * i / steps));
            int sx1 = int(SX(x0 + (x1 - x0) * (i + 1) / steps));
            Screen.Dim(col & 0xFFFFFF, a0 + (a1 - a0) * t, sx0, 0, max(1, sx1 - sx0), Screen.GetHeight());
        }
    }

    // Title composition, cover-scaled on the whole screen (no text in the image).
    static void TitleImage()
    {
        TextureID tex = TexMan.CheckForTexture("graphics/ui/RFMENUBG.png", TexMan.Type_Any);
        if (!tex.IsValid()) tex = TexMan.CheckForTexture("TITLEPIC", TexMan.Type_Any);
        if (!tex.IsValid()) { FillScreen(C_CHARCOAL, 1.0); return; }
        Vector2 size = TexMan.GetScaledSize(tex);
        double sw = Screen.GetWidth(), sh = Screen.GetHeight();
        double k = max(sw / size.X, sh / size.Y);
        double w = size.X * k, h = size.Y * k;
        Screen.DrawTexture(tex, false, (sw - w) / 2, (sh - h) / 2, DTA_DestWidthF, w, DTA_DestHeightF, h);
    }

    // Backdrop of every RF screen: the title composition out of a game, the dimmed game view in one.
    static void Backdrop(bool strong = false)
    {
        if (gamestate != GS_LEVEL)
        {
            TitleImage();
            Gradient(C_CHARCOAL, 0, 1150, strong ? 0.9 : 0.82, 0.0);
        }
        else
        {
            FillScreen(C_CHARCOAL, 0.45);
            Gradient(C_CHARCOAL, 0, 1250, strong ? 0.92 : 0.86, 0.12);
        }
    }

    // Heading block of a screen: a file tab (mono label), the title, a hairline and the oxblood rule.
    static void Heading(String tab, String title, double x = 190, double y = 150)
    {
        Fill(C_OXBLOOD, 1.0, x - 40, y + 4, 6, 118);
        if (tab != "") Text(Face('RFMono'), StringTable.Localize(tab).MakeUpper(), x, y, 26, C_STEEL, 0.95);
        Text(Face('RFTitle'), title, x, y + 34, 62, C_PAPER);
        Fill(C_STEELDIM, 0.8, x, y + 112, 560, 2);
    }

    // Footer hints: key names are the engine's menu keys (arrows, enter, escape).
    static void Hints(String text)
    {
        Fill(C_STEELDIM, 0.55, 190, 978, 1540, 1);
        Text(Face('RFMono'), text, 190, 992, 26, C_STEEL, 0.9);
    }
}

// ------------------------------------------------------------------------------------------------ saves
// "Continuer": the most recent savegame by creation time. The save list of the engine is sorted by title,
// so the date is read from each save's header (first line of its comment: the creation time).
class RFSaves ui
{
    static int Latest(SavegameManager manager, out String when)
    {
        int best = -1;
        String bestStamp = "";
        manager.ReadSaveStrings();
        for (int i = 0; i < manager.SavegameCount(); i++)
        {
            SaveGameNode node = manager.GetSavegame(i);
            if (node == null || node.bOldVersion || node.bMissingWads || node.Filename == "") continue;
            manager.ExtractSaveData(i);
            String stamp = Stamp(manager.SaveCommentString);
            if (stamp != "" && (best < 0 || stamp > bestStamp)) { best = i; bestStamp = stamp; }
        }
        manager.UnloadSaveData();
        when = bestStamp;
        return best;
    }

    // Sortable "YYYY-MM-DD HH:MM:SS" from the creation-time line ("2026-09-27 12:34:56" or an asctime line).
    static String Stamp(String comment)
    {
        Array<String> lines;
        comment.Split(lines, "\n");
        if (lines.Size() == 0) return "";
        String s = lines[0];
        s.StripLeftRight();
        if (s.Length() >= 19 && s.Mid(4, 1) == "-" && s.Mid(7, 1) == "-") return s.Left(19);
        // "Sun Sep 27 12:34:56 2026"
        Array<String> p;
        s.Split(p, " ", TOK_SKIPEMPTY);
        if (p.Size() < 5) return "";
        static const String months[] = { "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
        int m = 0;
        for (int i = 0; i < 12; i++) if (p[1] ~== months[i]) m = i + 1;
        if (m == 0) return "";
        return String.Format("%s-%02d-%02d %s", p[4], m, p[2].ToInt(), p[3]);
    }
}

// ------------------------------------------------------------------------------------------------ lists
class RFMenuEntry ui
{
    String label;
    String hint;
    Name dest;          // menu to open; 'RFClose', 'RFContinue' are handled by the screen
    int param;
    bool enabled;
    int hotkey;
    ListMenuItem item;  // engine item to activate (skill list)
}

// A list screen in the RF style: heading, entries, focus bar, disabled state, pressed flash, hints.
// Keyboard (arrows, enter, escape, first letters), mouse (hover, click) and the engine's menu keys.
class RFListScreen : ListMenu
{
    Array<RFMenuEntry> entries;
    int sel;
    double focusY;
    int openedAt;
    int pressedAt;
    int pressedIndex;
    int hover;
    const FIRSTROW = 420.0;
    const ROWH = 64.0;
    const COLX = 190.0;

    override void Init(Menu parent, ListMenuDescriptor desc)
    {
        Super.Init(parent, desc);
        DontDim = true;
        openedAt = MenuTime();
        pressedIndex = -1;
        hover = -1;
        Build();
        sel = FirstEnabled(DefaultSelection());
        focusY = RowY(sel);
    }

    virtual void Build() {}
    virtual int DefaultSelection() { return 0; }
    virtual void DrawBackdrop() { RFUI.Backdrop(); }
    virtual void DrawHeader() {}
    virtual String HintText() { return "$RF_UI_HINTS"; }
    virtual double TopY() { return FIRSTROW; }

    RFMenuEntry Add(String label, Name dest, String key = "", bool enabled = true, String hint = "", int param = 0)
    {
        let e = new("RFMenuEntry");
        e.label = label;
        e.dest = dest;
        e.enabled = enabled;
        e.hint = hint;
        e.param = param;
        String hk = key != "" ? key : StringTable.Localize(label).Left(1);
        hk = hk.MakeLower();
        e.hotkey = hk.ByteAt(0);
        entries.Push(e);
        return e;
    }

    double RowY(int i) { return TopY() + max(i, 0) * ROWH; }

    int FirstEnabled(int from)
    {
        for (int k = 0; k < entries.Size(); k++)
        {
            int i = (from + k) % max(entries.Size(), 1);
            if (entries[i].enabled) return i;
        }
        return 0;
    }

    void Move(int dir)
    {
        if (entries.Size() == 0) return;
        int i = sel;
        for (int k = 0; k < entries.Size(); k++)
        {
            i = (i + dir + entries.Size()) % entries.Size();
            if (entries[i].enabled) break;
        }
        if (i != sel) { sel = i; MenuSound("menu/cursor"); }
    }

    virtual bool Run(RFMenuEntry e)
    {
        if (e.item != null) return e.item.Activate();
        if (e.dest == 'RFClose') { Close(); return true; }
        if (e.dest != 'None') { SetMenu(e.dest, e.param); return true; }
        return false;
    }

    void Choose(int i)
    {
        if (i < 0 || i >= entries.Size()) return;
        if (!entries[i].enabled) { MenuSound("menu/invalid"); return; }
        pressedAt = MenuTime();
        pressedIndex = i;
        MenuSound("menu/choose");
        Run(entries[i]);
    }

    override bool MenuEvent(int mkey, bool fromcontroller)
    {
        switch (mkey)
        {
        case MKEY_Up: Move(-1); return true;
        case MKEY_Down: Move(1); return true;
        case MKEY_Home: sel = FirstEnabled(0); return true;
        case MKEY_End: sel = entries.Size() - 1; Move(-1); Move(1); return true;
        case MKEY_Enter: Choose(sel); return true;
        case MKEY_Back:
        {
            Close();
            let m = GetCurrentMenu();
            MenuSound(m != null ? "menu/backup" : "menu/clear");
            if (!m) menuDelegate.MenuDismissed();
            return true;
        }
        }
        return false;
    }

    override bool OnUIEvent(UIEvent ev)
    {
        if (ev.Type == UIEvent.Type_Char)
        {
            int ch = String.CharLower(ev.KeyChar);
            for (int i = 0; i < entries.Size(); i++)
            {
                if (entries[i].enabled && entries[i].hotkey == ch) { sel = i; Choose(i); return true; }
            }
        }
        return Super.OnUIEvent(ev);
    }

    int EntryAt(int mx, int my)
    {
        for (int i = 0; i < entries.Size(); i++)
        {
            double y0 = RFUI.SY(RowY(i) - 8), y1 = RFUI.SY(RowY(i) + ROWH - 8);
            double x0 = RFUI.SX(COLX - 50), x1 = RFUI.SX(COLX + 640);
            if (mx >= x0 && mx < x1 && my >= y0 && my < y1) return i;
        }
        return -1;
    }

    override bool MouseEvent(int type, int mx, int my)
    {
        int i = EntryAt(mx, my);
        hover = i;
        if (i >= 0 && entries[i].enabled && i != sel && type != MOUSE_Release) { sel = i; MenuSound("menu/cursor"); }
        if (type == MOUSE_Release && i >= 0) Choose(i);
        return true;
    }

    override void Ticker()
    {
        Super.Ticker();
        double target = RowY(sel);
        focusY += (target - focusY) * 0.45;
        if (abs(target - focusY) < 0.5) focusY = target;
    }

    void DrawEntries()
    {
        Font face = RFUI.Face('RFMenu');
        Font mono = RFUI.Face('RFMono');
        double age = (MenuTime() - openedAt) / 35.0;
        // Focus: a charcoal band and the oxblood bar at the left of the column (eased between rows).
        if (entries.Size() > 0)
        {
            bool pressed = pressedIndex == sel && MenuTime() - pressedAt < 6;
            RFUI.Fill(RFUI.C_CHARCOAL, 0.55, COLX - 40, focusY - 6, 660, ROWH - 8);
            RFUI.Fill(pressed ? RFUI.C_PAPER : RFUI.C_OXBLOOD_HI, 1.0, COLX - 40, focusY - 6, 6, ROWH - 8);
        }
        for (int i = 0; i < entries.Size(); i++)
        {
            // Brief entrance: each row slides 10 px and fades in, 0.25 s, staggered; input is live at once.
            double a = clamp((age - i * 0.03) / 0.25, 0.0, 1.0);
            double dx = (1 - a) * 10;
            let e = entries[i];
            int col = !e.enabled ? RFUI.C_STEELDIM : i == sel ? RFUI.C_PAPER : RFUI.C_PAPERDIM;
            double alpha = (e.enabled ? 1.0 : 0.7) * a;
            RFUI.Text(face, e.label, COLX + dx, RowY(i), 40, col, alpha);
            if (e.hint != "" && (i == sel || !e.enabled))
            {
                double lw = RFUI.TextW(face, e.label, 40);
                RFUI.Text(mono, e.hint, COLX + lw + 26 + dx, RowY(i) + 11, 25, e.enabled ? RFUI.C_STEEL : RFUI.C_STEELDIM, alpha);
            }
        }
    }

    override void Drawer()
    {
        DrawBackdrop();
        DrawHeader();
        DrawEntries();
        RFUI.Hints(HintText());
    }
}

// ------------------------------------------------------------------------------------------------ main / pause
class RFMainMenu : RFListScreen
{
    bool inGame;
    int latestSave;
    String latestWhen;

    override void Build()
    {
        inGame = gamestate == GS_LEVEL;
        entries.Clear();
        if (inGame)
        {
            Add("$RF_MENU_RESUME", 'RFClose', "r");
            Add("$RF_MENU_SAVE", 'SaveGameMenu', "s");
            Add("$RF_MENU_LOAD", 'LoadGameMenu', "c");
            Add("$RF_MENU_OPTIONS", 'RFOptionsMenu', "o");
            Add("$RF_MENU_MAIN", 'EndGameMenu', "m");
            Add("$RF_MENU_QUIT", 'QuitMenu', "q");
            return;
        }
        latestSave = RFSaves.Latest(SavegameManager.GetManager(), latestWhen);
        Add("$RF_MENU_CONTINUE", 'RFContinue', "u", latestSave >= 0, latestSave >= 0 ? "" : "$RF_UI_NOSAVE");
        Add("$RF_MENU_NEWGAME", 'PlayerclassMenu', "n");
        Add("$RF_MENU_LOAD", 'LoadGameMenu', "c");
        Add("$RF_MENU_OPTIONS", 'RFOptionsMenu', "o");
        Add("$RF_MENU_CREDITS", 'RFCreditsMenu', "g");
        Add("$RF_MENU_QUIT", 'QuitMenu', "q");
    }

    override int DefaultSelection() { return inGame ? 0 : (latestSave >= 0 ? 0 : 1); }
    override double TopY() { return inGame ? 470 : 470; }

    override bool Run(RFMenuEntry e)
    {
        if (e.dest == 'RFContinue')
        {
            let manager = SavegameManager.GetManager();
            manager.ReadSaveStrings();
            String when;
            int i = RFSaves.Latest(manager, when);
            if (i < 0) { MenuSound("menu/invalid"); return false; }
            manager.LoadSavegame(i);
            return true;
        }
        return Super.Run(e);
    }

    override void DrawBackdrop() { RFUI.Backdrop(inGame); }

    override void DrawHeader()
    {
        if (!inGame)
        {
            RFUI.Fill(RFUI.C_OXBLOOD, 1.0, 150, 168, 6, 196);
            RFUI.Text(RFUI.Face('RFMono'), "$RF_UI_HOUSE", 190, 164, 26, RFUI.C_STEEL, 0.95);
            RFUI.Text(RFUI.Face('RFLogo'), "$RF_MENU_TITLE", 184, 196, 118, RFUI.C_PAPER);
            RFUI.Text(RFUI.Face('RFTitle'), "$RF_MENU_SUBTITLE", 190, 316, 40, RFUI.C_PAPERDIM);
            RFUI.Fill(RFUI.C_STEELDIM, 0.8, 190, 380, 560, 2);
            if (latestSave >= 0 && sel == 0)
                RFUI.Text(RFUI.Face('RFMono'), String.Format("%s %s", StringTable.Localize("$RF_UI_LASTSAVE"), latestWhen.Left(16)), 190, 400, 22, RFUI.C_STEEL, 0.9);
            return;
        }
        // Pause: the chapter and its current objective, beside the file tab.
        String tab = String.Format("%s  %s", StringTable.Localize("$RF_MENU_PAUSE"), ChapterNumber());
        RFUI.Heading(tab, Level.LevelName, 190, 170);
        let director = RFDirector(EventHandler.Find('RFDirector'));
        if (director != null && director.objective != "")
        {
            RFUI.Text(RFUI.Face('RFMono'), "$RF_UI_OBJECTIVE", 190, 312, 22, RFUI.C_STEEL, 0.9);
            RFUI.Text(RFUI.Face('RFText'), director.objective, 190, 342, 30, RFUI.C_PAPERDIM, 0.95);
        }
    }

    static String ChapterNumber()
    {
        String m = Level.MapName;
        if (m.Length() == 4 && m.Left(2) ~== "RF") return String.Format("%s %s", StringTable.Localize("$RF_UI_CHAPTER"), m.Mid(2, 2));
        return m;
    }
}

// Difficulty: the engine fills the list from MAPINFO skills; the RF screen draws and runs those items.
class RFSkillMenu : RFListScreen
{
    override void Build()
    {
        entries.Clear();
        for (int i = 0; i < mDesc.mItems.Size(); i++)
        {
            let item = ListMenuItemTextItem(mDesc.mItems[i]);
            if (item == null || !item.Selectable()) continue;
            let e = Add(item.mText, 'None', "", true, String.Format("$RF_SKILL_HINT_%d", entries.Size()));
            e.item = item;
            if (item.mHotkey > 0) e.hotkey = String.CharLower(item.mHotkey);
        }
    }

    override int DefaultSelection()
    {
        // The MAPINFO default skill (Service) is the engine's preselected item.
        int n = 0;
        for (int i = 0; i < mDesc.mItems.Size(); i++)
        {
            if (mDesc.mItems[i] == null || !mDesc.mItems[i].Selectable()) continue;
            if (i == mDesc.mSelectedItem) return n;
            n++;
        }
        return 0;
    }

    override double TopY() { return 330; }
    override void DrawHeader() { RFUI.Heading("$RF_MENU_NEWGAME", "$RF_MENU_SKILL"); }
}

// ------------------------------------------------------------------------------------------------ credits
class RFCreditsMenu : RFListScreen
{
    override void Build()
    {
        entries.Clear();
        Add("$RF_MENU_BACK", 'RFClose', "r");
    }

    override double TopY() { return 880; }

    override void DrawHeader()
    {
        RFUI.Heading("$RF_UI_HOUSE", "$RF_MENU_CREDITS");
        Font text = RFUI.Face('RFText');
        Font mono = RFUI.Face('RFMono');
        double y = 320;
        for (int i = 1; i <= 12; i++)
        {
            String key = String.Format("RF_CREDITS_%d", i);
            String line = StringTable.Localize("$" .. key);
            if (line == key) break;
            bool label = line.Left(1) == "#";
            if (label) line = line.Mid(1);
            if (line != "") RFUI.Text(label ? mono : text, line, 190, y, label ? 24 : 30, label ? RFUI.C_STEEL : RFUI.C_PAPERDIM, label ? 0.9 : 1.0);
            y += label ? 34 : 40;
        }
    }
}

// ------------------------------------------------------------------------------------------------ options
// RF options page: native items (the engine's option pages stay complete), RF backdrop and heading.
class RFOptionMenu : OptionMenu
{
    override void Init(Menu parent, OptionMenuDescriptor desc)
    {
        Super.Init(parent, desc);
        DontDim = true;
    }

    override int DrawCaption(String title, int y, bool drawit)
    {
        if (drawit) RFUI.Heading("$RF_UI_HOUSE", title, 190, 70);
        // Native items start under the heading (screen pixels).
        return int(RFUI.SY(260));
    }

    override void Drawer()
    {
        RFUI.Backdrop(true);
        Super.Drawer();
    }
}

// ------------------------------------------------------------------------------------------------ load / save
// The engine's load and save lists (selection, delete, name entry, loading) with an RF layout: the list at
// the left in the menu column, the save's picture and its comment at the right.
mixin class RFSaveListDraw
{
    void RFLayout()
    {
        rowHeight = int(46 * RFUI.U());
        listboxLeft = int(RFUI.SX(150));
        listboxTop = int(RFUI.SY(330));
        listboxWidth = int(RFUI.SX(930)) - listboxLeft;
        listboxRows = max(1, int((RFUI.SY(930) - listboxTop) / max(rowHeight, 1)));
        listboxHeight = listboxRows * rowHeight;
        listboxRight = listboxLeft + listboxWidth;
        savepicLeft = int(RFUI.SX(1010));
        savepicTop = listboxTop;
        savepicWidth = int(RFUI.SX(1650)) - savepicLeft;
        savepicHeight = savepicWidth * 5 / 8;
    }

    void RFDraw(String heading)
    {
        RFUI.Backdrop(true);
        RFUI.Heading("$RF_UI_HOUSE", heading);
        RFLayout();
        if (gameaction == ga_loadgame || gameaction == ga_loadgamehidecon || gameaction == ga_savegame) return;
        Font text = RFUI.Face('RFText');
        Font mono = RFUI.Face('RFMono');
        double u = RFUI.U();
        // List.
        Screen.Dim(0x0E0C0E, 0.55, listboxLeft, listboxTop, listboxWidth, listboxHeight);
        int count = manager.SavegameCount();
        if (count == 0)
        {
            RFUI.Text(mono, "$RF_UI_NOSAVE", 190, 350, 26, RFUI.C_STEEL);
        }
        int j = TopItem;
        for (int i = 0; i < listboxRows && j < count; i++)
        {
            SaveGameNode node = manager.GetSavegame(j);
            double y = (listboxTop - RFUI.OY()) / u + i * 46;
            bool isSel = j == Selected;
            if (isSel)
            {
                RFUI.Fill(RFUI.C_CHARCOAL, 0.7, 150, y, (listboxWidth / u), 46);
                RFUI.Fill(mEntering ? RFUI.C_PAPER : RFUI.C_OXBLOOD_HI, 1.0, 150, y, 6, 46);
            }
            String title = node.SaveTitle;
            int col = node.bOldVersion ? RFUI.C_OXBLOOD_HI : node.bMissingWads ? RFUI.C_STEELDIM : isSel ? RFUI.C_PAPER : RFUI.C_PAPERDIM;
            if (isSel && mEntering && mInput != null) title = mInput.GetText() .. text.GetCursor();
            else if (title == "" && j == 0 && self is 'SaveMenu') title = StringTable.Localize("$RF_UI_NEWSAVE");
            Screen.SetClipRect(listboxLeft, listboxTop, listboxWidth - int(8 * u), listboxHeight);
            RFUI.Text(text, title, 172, y + 8, 30, col);
            Screen.ClearClipRect();
            j++;
        }
        // Picture and comment of the selected save.
        Screen.Dim(0x0E0C0E, 0.6, savepicLeft, savepicTop, savepicWidth, savepicHeight);
        if (!manager.DrawSavePic(savepicLeft, savepicTop, savepicWidth, savepicHeight) && count > 0)
            RFUI.Text(mono, "$RF_UI_NOPICTURE", (savepicLeft - RFUI.OX()) / u + 24, (savepicTop - RFUI.OY()) / u + 24, 22, RFUI.C_STEEL);
        Screen.DrawLineFrame(Color(255, 107, 107, 104), savepicLeft, savepicTop, savepicWidth, savepicHeight, max(1, int(u)));
        if (Selected >= 0 && Selected < count)
        {
            Array<String> lines;
            manager.SaveCommentString.Split(lines, "\n");
            double y = (savepicTop + savepicHeight - RFUI.OY()) / u + 20;
            for (int k = 0; k < lines.Size() && k < 6; k++)
            {
                RFUI.Text(k == 0 ? mono : text, lines[k], (savepicLeft - RFUI.OX()) / u, y, k == 0 ? 22 : 28, k == 0 ? RFUI.C_STEEL : RFUI.C_PAPERDIM);
                y += k == 0 ? 32 : 36;
            }
        }
    }
}

class RFLoadMenu : LoadMenu
{
    mixin RFSaveListDraw;
    override void Init(Menu parent, ListMenuDescriptor desc) { Super.Init(parent, desc); DontDim = true; RFLayout(); }
    override void Drawer() { RFDraw("$RF_MENU_LOAD"); RFUI.Hints("$RF_UI_HINTS_LOAD"); }
}

class RFSaveMenu : SaveMenu
{
    mixin RFSaveListDraw;
    override void Init(Menu parent, ListMenuDescriptor desc) { Super.Init(parent, desc); DontDim = true; RFLayout(); }
    override void Drawer() { RFDraw("$RF_MENU_SAVE"); RFUI.Hints("$RF_UI_HINTS_SAVE"); }
}

// ------------------------------------------------------------------------------------------------ confirmation
// Engine confirmations (quit, end the game, delete a save, overwrite): a file card with Oui / Non.
class RFMessageBox : MessageBoxMenu
{
    String rawMessage;

    override void Init(Menu parent, String message, int messagemode, bool playsound, Name cmd, voidptr native_handler)
    {
        Super.Init(parent, message, messagemode, playsound, cmd, native_handler);
        // The engine appends its key reminders ("press Y..."): the card shows Oui / Non instead.
        rawMessage = StringTable.Localize(message);
        rawMessage.Replace(StringTable.Localize("$DOSY"), "");
        rawMessage.Replace(StringTable.Localize("$PRESSYN"), "");
        rawMessage.StripRight();
        DontDim = true;
    }

    // Card geometry in design pixels.
    const CX = 560.0;
    const CW = 800.0;

    double CardTop(int lines) { return 540 - (lines * 40 + 170) / 2; }

    override void Drawer()
    {
        RFUI.FillScreen(RFUI.C_CHARCOAL, 0.55);
        Font text = RFUI.Face('RFText');
        Font menu = RFUI.Face('RFMenu');
        let broken = text.BreakLines(rawMessage, int(700 * text.GetHeight() / 30.0));
        int n = broken.Count();
        double top = CardTop(n);
        double h = n * 40 + 170;
        RFUI.Fill(RFUI.C_CHARCOAL, 0.96, CX, top, CW, h);
        RFUI.Fill(RFUI.C_OXBLOOD, 1.0, CX, top, CW, 5);
        RFUI.Fill(RFUI.C_STEELDIM, 0.8, CX, top + h - 1, CW, 1);
        double y = top + 40;
        for (int i = 0; i < n; i++)
        {
            RFUI.Text(text, broken.StringAt(i), CX + 50, y, 30, RFUI.C_PAPER);
            y += 40;
        }
        if (mMessageMode != 0)
        {
            RFUI.Text(RFUI.Face('RFMono'), "$RF_UI_ANYKEY", CX + 50, top + h - 60, 22, RFUI.C_STEEL);
            return;
        }
        y = top + h - 80;
        for (int k = 0; k < 2; k++)
        {
            double bx = CX + 50 + k * 220;
            bool isSel = messageSelection == k;
            if (isSel)
            {
                RFUI.Fill(RFUI.C_CHARCOAL, 0.9, bx - 20, y - 6, 200, 52);
                RFUI.Fill(RFUI.C_OXBLOOD_HI, 1.0, bx - 20, y - 6, 6, 52);
            }
            RFUI.Text(menu, k == 0 ? "$RF_OPT_YES" : "$RF_OPT_NO", bx, y, 38, isSel ? RFUI.C_PAPER : RFUI.C_PAPERDIM);
        }
    }

    override bool MenuEvent(int mkey, bool fromcontroller)
    {
        if (mMessageMode == 0 && (mkey == MKEY_Left || mkey == MKEY_Right))
        {
            MenuSound("menu/cursor");
            messageSelection = !messageSelection;
            return true;
        }
        return Super.MenuEvent(mkey, fromcontroller);
    }

    override bool MouseEvent(int type, int x, int y)
    {
        if (mMessageMode != 0) return Super.MouseEvent(type, x, y);
        Font text = RFUI.Face('RFText');
        let broken = text.BreakLines(rawMessage, int(700 * text.GetHeight() / 30.0));
        double top = CardTop(broken.Count());
        double by = top + broken.Count() * 40 + 170 - 86;
        int sel = -1;
        for (int k = 0; k < 2; k++)
        {
            double bx = CX + 30 + k * 220;
            if (x >= RFUI.SX(bx) && x < RFUI.SX(bx + 200) && y >= RFUI.SY(by) && y < RFUI.SY(by + 52)) sel = k;
        }
        if (sel >= 0 && sel != messageSelection) MenuSound("menu/cursor");
        if (sel >= 0) messageSelection = sel;
        if (type == MOUSE_Release && sel >= 0) return MenuEvent(MKEY_Enter, true);
        return true;
    }
}
