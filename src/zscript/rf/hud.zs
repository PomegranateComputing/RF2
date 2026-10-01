// RF2 HUD: only live data. Health with Viktor's portrait, active weapon and its
// real ammunition model, contextual keys, brief objective, use prompt, crosshair.

// Viktor's portrait state from the health of the player shown, as a share of his normal maximum (overhealth keeps
// the intact face; armour plays no part). Shared by the HUD and the development checks. 0 intact (> 80 %),
// 1 lightly injured (> 60 %), 2 wounded (> 40 %), 3 severely wounded (> 20 %), 4 critical (alive, <= 20 %), 5 dead.
class RFPortrait
{
    static clearscope int StateOf(PlayerInfo p)
    {
        if (p == null || p.mo == null) return 0;
        if (p.health <= 0 || p.playerstate == PST_DEAD) return 5;
        int normal = p.mo.GetMaxHealth(false);
        if (normal <= 0) normal = 100;
        double share = clamp(p.health * 100.0 / normal, 0.0, 100.0);
        if (share > 80) return 0;
        if (share > 60) return 1;
        if (share > 40) return 2;
        if (share > 20) return 3;
        return 4;
    }

    static clearscope String FileOf(int state)
    {
        static const String FILES[] = { "VIKTOR_H100", "VIKTOR_H080", "VIKTOR_H060", "VIKTOR_H040", "VIKTOR_H020", "VIKTOR_DEAD" };
        return "graphics/hud/viktor/" .. FILES[clamp(state, 0, 5)] .. ".png";
    }
}

class RFStatusBar : BaseStatusBar
{
    HUDFont labelFont;
    HUDFont numberFont;
    HUDFont bigFont;
    // Engine messages drawn by the HUD itself (ProcessNotify / ProcessMidPrint): pickups under
    // the objective, centred messages (notes, locks, winch) on a dark backing, in the RF faces.
    // The engine drew them in its red pixel font over the objective.
    Array<String> noteText;
    Array<int> noteStart;
    String midText;
    int midStart, midTics;
    int deathStart;          // map time of the player's death, -1 while alive

    // A per-chapter LANGUAGE string (RF_<MAP>_<suffix>), "" when the chapter has none.
    static String ChapterText(String suffix)
    {
        String key = String.Format("RF_%s_%s", Level.MapName.MakeUpper(), suffix);
        String text = StringTable.Localize("$" .. key);
        return text == key ? "" : text;
    }

    // Death and resume (RF2-UI-01): the view sinks to charcoal, one line, and the two real actions:
    // use resumes (the engine reloads the last save, or restarts the chapter without one), Escape opens the menu.
    void DrawDeath(double s)
    {
        double t = (Level.maptime - deathStart) / 35.0;
        double a = clamp((t - 0.6) / 1.4, 0.0, 1.0);
        if (a <= 0) return;
        Screen.Dim(0x0e0c0e, 0.72 * a, 0, 0, Screen.GetWidth(), Screen.GetHeight());
        Fill(Color(int(255 * a), 0x7a, 0x1f, 0x2b), -150 * s, 150 * s, 300 * s, 2 * s, DI_SCREEN_CENTER_TOP);
        DrawString(bigFont, StringTable.Localize("$RF_UI_DEAD"), (0, 160 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_WHITE, a, -1, 0, (s * 1.2, s * 1.2));
        double b = clamp((t - 1.6) / 0.6, 0.0, 1.0);
        if (b <= 0) return;
        String line = KeyPrompt("+use", "$RF_UI_RESUME") .. "        [Esc] " .. StringTable.Localize("$RF_UI_MENU");
        DrawString(labelFont, line, (0, 196 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_GREY, b, -1, 0, (s * 0.85, s * 0.85));
    }

    // The six portraits are looked up once (texture ids, no disk access afterwards).
    TextureID portraits[6];
    bool portraitsReady;

    TextureID ViktorPortrait()
    {
        if (!portraitsReady)
        {
            for (int i = 0; i < 6; i++) portraits[i] = TexMan.CheckForTexture(RFPortrait.FileOf(i), TexMan.Type_MiscPatch);
            portraitsReady = true;
        }
        return portraits[RFPortrait.StateOf(CPlayer)];
    }

    // "[key] VERB" with the key the player really bound to the command.
    String KeyPrompt(String command, String verb) const
    {
        int k1, k2;
        [k1, k2] = Bindings.GetKeysForCommand(command);
        String key = k1 > 0 ? KeyBindings.NameKeys(k1, 0, false) : "?";
        return String.Format("[%s] %s", key, StringTable.Localize(verb));
    }

    // Level ending: fade to black, then the exit text line by line in the RF faces.
    void DrawOutro(double tics, double s)
    {
        double t = tics / 35.0;
        Screen.Dim(0, clamp(t / 2.5, 0.0, 1.0), 0, 0, Screen.GetWidth(), Screen.GetHeight());
        Array<String> lines;
        ChapterText("EXIT").Split(lines, "\n");
        double y = 150 - lines.Size() * 9;
        for (int i = 0; i < lines.Size(); i++)
        {
            double a = clamp((t - 2.6 - i * 0.7) / 1.2, 0.0, 1.0);
            if (lines[i] != "" && a > 0)
            {
                HUDFont face = i == 0 ? bigFont : labelFont;
                DrawString(face, lines[i], (0, y * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, i == 0 ? Font.CR_WHITE : Font.CR_GREY, a, -1, 0, (s, s));
            }
            y += i == 0 ? 26 : 18;
        }
    }

    // The ending's page (comics.zs): the whole page kept at 16:9 inside the screen (bands in 4:3 and 21:9), the panels
    // not yet reached in the dark, the captions of the panels reached on cream boxes in their zones, the keys in a
    // small line under the page. Sizes follow the page, with a floor so that a caption stays readable.
    void DrawComic(RFDirector d, double ticFrac)
    {
        int sw = Screen.GetWidth(), sh = Screen.GetHeight();
        Screen.Clear(0, 0, sw, sh, Color(255, 0, 0, 0));
        double pw = min(sw, sh * 16.0 / 9.0), ph = pw * 9.0 / 16.0;
        double hint = sh - ph > sh * 0.05 ? 0 : ph * 0.035;       // room for the keys line when there is no band
        ph -= hint;
        pw = ph * 16.0 / 9.0;
        double px = (sw - pw) / 2, py = (sh - ph - hint) / 2;
        double k = pw / 1920.0;
        double fade = clamp((d.comicTics + ticFrac) / 25.0, 0.0, 1.0);
        Screen.DrawTexture(d.comicTex, false, px, py, DTA_DestWidthF, pw, DTA_DestHeightF, ph, DTA_Alpha, fade);
        let c = d.comic;
        for (int i = d.comicStep; i < c.PanelCount(); i++)
            Screen.Dim(0, 0.88, int(px + c.panels[i * 4] * k), int(py + c.panels[i * 4 + 1] * k),
                       int(c.panels[i * 4 + 2] * k + 1), int(c.panels[i * 4 + 3] * k + 1));
        Font f = labelFont.mFont;
        double fs = max(ph * 0.034, 18.0) / f.GetHeight();
        for (int i = 0; i < c.captions.Size(); i++)
        {
            if (c.after[i] > d.comicStep) continue;
            double zx = px + c.zones[i * 4] * k, zy = py + c.zones[i * 4 + 1] * k, zw = c.zones[i * 4 + 2] * k;
            if (c.styles[i] == 1)
            {
                // On the page's black band: cream text, centred in the zone, sized on the zone's height.
                double zh = c.zones[i * 4 + 3] * k;
                double bs = max(zh * 0.55, 18.0) / f.GetHeight();
                BrokenLines band = f.BreakLines(StringTable.Localize(c.captions[i]), int(zw / bs));
                double blh = f.GetHeight() * bs * 1.15;
                double by = zy + (zh - band.Count() * blh) / 2;
                for (int j = 0; j < band.Count(); j++)
                    Screen.DrawText(f, Font.CR_WHITE, zx + (zw - f.StringWidth(band.StringAt(j)) * bs) / 2, by + j * blh,
                                    band.StringAt(j), DTA_ScaleX, bs, DTA_ScaleY, bs, DTA_Alpha, fade,
                                    DTA_Color, Color(255, 232, 222, 196));
                continue;
            }
            BrokenLines lines = f.BreakLines(StringTable.Localize(c.captions[i]), int((zw - 16) / fs));
            double lh = f.GetHeight() * fs * 1.2;
            double bh = lines.Count() * lh + 12;
            Screen.Dim(Color(255, 232, 222, 196), 0.94 * fade, int(zx), int(zy), int(zw), int(bh));
            Screen.Dim(0, 0.9 * fade, int(zx), int(zy), int(zw), 2);
            for (int j = 0; j < lines.Count(); j++)
                Screen.DrawText(f, Font.CR_BLACK, zx + 8, zy + 6 + j * lh, lines.StringAt(j), DTA_ScaleX, fs, DTA_ScaleY, fs, DTA_Alpha, fade);
        }
        String keys = String.Format("%s     %s", KeyPrompt("+use", "$RF_COMIC_NEXT"), StringTable.Localize("$RF_COMIC_PASS"));
        double ks = max(sh * 0.024, 15.0) / f.GetHeight();
        double ky = hint > 0 ? py + ph + hint * 0.15 : py + ph + (sh - ph) / 4 - f.GetHeight() * ks / 2;
        Screen.DrawText(f, Font.CR_GREY, px + pw - f.StringWidth(keys) * ks - 8, ky, keys,
                        DTA_ScaleX, ks, DTA_ScaleY, ks, DTA_Alpha, 0.8 * fade);
    }

    // Pickup lines (PRINT_LOW) and other notify lines. RF_DEV_ markers stay in the console and
    // the log, never on the player's screen.
    override bool ProcessNotify(EPrintLevel printlevel, String outline)
    {
        String text = outline;
        text.StripLeftRight();
        if (text == "" || text.Left(7) == "RF_DEV_" || text.Left(7) == "RF_DBG_" || text.Left(7) == "RF_ART_") return true;
        noteText.Push(text);
        noteStart.Push(Level.maptime);
        while (noteText.Size() > 3)
        {
            noteText.Delete(0);
            noteStart.Delete(0);
        }
        return true;
    }

    override void FlushNotify()
    {
        noteText.Clear();
        noteStart.Clear();
    }

    // Centred messages keep the duration asked by A_Print (it sets con_midtime around the call).
    override bool ProcessMidPrint(Font fnt, String msg, bool bold)
    {
        midText = msg;
        midText.StripLeftRight();
        midStart = Level.maptime;
        let midtime = CVar.FindCVar('con_midtime');
        midTics = int(35 * (midtime != null ? max(midtime.GetFloat(), 1.0) : 3.0));
        return true;
    }

    // Text wrapped to a width in virtual units, one line per entry.
    void Wrap(HUDFont face, String text, double width, double scale, out Array<String> lines)
    {
        lines.Clear();
        let broken = face.mFont.BreakLines(StringTable.Localize(text), int(width / scale));
        for (int i = 0; i < broken.Count(); i++) lines.Push(broken.StringAt(i));
    }

    void DrawMessages(double s, String objective)
    {
        Array<String> lines;
        // Top left: objective (wrapped), then pickups, three at most, 3 s and a half-second fade,
        // over a light dark backing that keeps them readable on the bright plaster.
        Array<String> rows;
        Array<double> alphas;
        Array<int> colours;
        Array<double> scales;
        if (objective != "")
        {
            Wrap(labelFont, objective, 300 * s, s * 0.9, lines);
            for (int k = 0; k < lines.Size(); k++) { rows.Push(lines[k]); alphas.Push(0.95); colours.Push(Font.CR_WHITE); scales.Push(0.9); }
        }
        for (int i = 0; i < noteText.Size(); i++)
        {
            double age = Level.maptime - noteStart[i];
            double a = clamp((122.5 - age) / 17.5, 0.0, 1.0);
            if (a <= 0) continue;
            Wrap(labelFont, noteText[i], 300 * s, s * 0.8, lines);
            for (int k = 0; k < lines.Size(); k++) { rows.Push(lines[k]); alphas.Push(a); colours.Push(Font.CR_TAN); scales.Push(0.8); }
        }
        if (rows.Size() > 0)
        {
            double widest = 0, height = 0;
            for (int k = 0; k < rows.Size(); k++)
            {
                widest = max(widest, labelFont.mFont.StringWidth(rows[k]) * s * scales[k]);
                height += (scales[k] > 0.85 ? 13 : 11) * s;
            }
            Fill(Color(80, 12, 10, 11), 6 * s, 6 * s, widest + 12 * s, height + 6 * s, DI_SCREEN_LEFT_TOP);
            double y = 9 * s;
            for (int k = 0; k < rows.Size(); k++)
            {
                double sc = s * scales[k];
                DrawString(labelFont, rows[k], (12 * s, y), DI_SCREEN_LEFT_TOP | DI_ITEM_LEFT_TOP, colours[k], alphas[k], -1, 0, (sc, sc));
                y += (scales[k] > 0.85 ? 13 : 11) * s;
            }
        }
        // Centred message: lower third, over a dark band sized to the text.
        if (midText == "") return;
        double age = Level.maptime - midStart;
        double a = clamp((midTics - age) / 17.5, 0.0, 1.0);
        if (a <= 0) return;
        Wrap(labelFont, midText, 400 * s, s, lines);
        double lineH = 15 * s;
        double top = 214 * s - lines.Size() * lineH;
        double widest = 0;
        for (int k = 0; k < lines.Size(); k++) widest = max(widest, labelFont.mFont.StringWidth(lines[k]) * s);
        Fill(Color(int(150 * a), 12, 10, 11), -widest / 2 - 10 * s, top - 6 * s, widest + 20 * s, lines.Size() * lineH + 10 * s, DI_SCREEN_CENTER_TOP);
        for (int k = 0; k < lines.Size(); k++)
            DrawString(labelFont, lines[k], (0, top + k * lineH), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_WHITE, a, -1, 0, (s, s));
    }

    override void Init()
    {
        Super.Init();
        SetSize(0, 640, 360);
        deathStart = -1;
        // RF2 font folders (scripts/mapkit/fonts.py); engine fonts only as a fallback.
        Font text = Font.GetFont('RFText');
        Font digits = Font.GetFont('RFHud');
        Font title = Font.GetFont('RFTitle');
        if (text == null) text = "NewSmallFont";
        if (digits == null) digits = "BigFont";
        if (title == null) title = "BigFont";
        labelFont = HUDFont.Create(text);
        numberFont = HUDFont.Create(digits);
        bigFont = HUDFont.Create(title);
    }

    override void Draw(int state, double ticFrac)
    {
        Super.Draw(state, ticFrac);
        if (state != HUD_StatusBar && state != HUD_Fullscreen) return;
        if (CPlayer == null || CPlayer.mo == null) return;

        let setting = CVar.GetCVar('rf_hud_scale', CPlayer);
        double s = setting != null ? clamp(setting.GetFloat(), 0.75, 1.5) : 1.0;
        BeginHUD(1.0, false, 640, 360);
        // The engine's HUD scale is a whole number that grows slower than the screen (3 at both
        // 1080p and 1440p, 4 at 4K): the layout takes the remainder, so it keeps the proportions
        // of a 640x360 screen everywhere (factor 1 at 1080p). rf_hud_scale adjusts on top.
        double fit = min(Screen.GetWidth() / 640.0, Screen.GetHeight() / 360.0);
        Vector2 engineScale = GetHUDScale();
        s *= fit / max(engineScale.Y, 1.0);

        let director = RFDirector(EventHandler.Find('RFDirector'));
        int left = DI_SCREEN_LEFT_BOTTOM;
        int right = DI_SCREEN_RIGHT_BOTTOM;

        // Portrait + health (bottom left).
        double ps = 0.15 * s;
        Fill(0xd00c0a0b, 10 * s, -96 * s, 80 * s, 86 * s, left);
        Fill(0xff6b1c22, 10 * s, -96 * s, 80 * s, 2 * s, left);
        DrawTexture(ViktorPortrait(), (12 * s, -94 * s), left | DI_ITEM_LEFT_TOP, 1.0, (-1, -1), (ps, ps));
        Fill(0xd00c0a0b, 92 * s, -48 * s, 70 * s, 38 * s, left);
        Fill(0xff6b1c22, 92 * s, -48 * s, 70 * s, 2 * s, left);
        DrawString(labelFont, StringTable.Localize("$RF_HUD_HEALTH"), (98 * s, -44 * s), left | DI_ITEM_LEFT_TOP, Font.CR_GREY, 1.0, -1, 0, (s * 0.8, s * 0.8));
        int healthColor = CPlayer.health <= 25 ? Font.CR_RED : Font.CR_WHITE;
        DrawString(numberFont, FormatNumber(max(0, CPlayer.health)), (98 * s, -32 * s), left | DI_ITEM_LEFT_TOP, healthColor, 1.0, -1, 0, (s * 1.0, s * 1.0));

        // Keys actually held (bottom left, above health).
        double ky = -60 * s;
        if (CPlayer.mo.FindInventory('RFGrilleKey') != null)
        {
            DrawString(labelFont, StringTable.Localize("$RF_KEY_GRILLE"), (92 * s, ky), left | DI_ITEM_LEFT_TOP, Font.CR_TAN, 1.0, -1, 0, (s * 0.7, s * 0.7));
            ky -= 10 * s;
        }
        if (CPlayer.mo.FindInventory('RFPasseKey') != null)
        {
            DrawString(labelFont, StringTable.Localize("$RF_KEY_PASSE"), (92 * s, ky), left | DI_ITEM_LEFT_TOP, Font.CR_TAN, 1.0, -1, 0, (s * 0.7, s * 0.7));
            ky -= 10 * s;
        }
        if (CPlayer.mo.FindInventory('RFSousStationKey') != null)
        {
            DrawString(labelFont, StringTable.Localize("$RF_KEY_SOUSSTATION"), (92 * s, ky), left | DI_ITEM_LEFT_TOP, Font.CR_TAN, 1.0, -1, 0, (s * 0.7, s * 0.7));
            ky -= 10 * s;
        }
        // The time card of the Luna Park (RF04), right of the health box: blank, then punched 06:06 (Astra, M04-02).
        let card = CPlayer.mo.FindInventory('RFTimeCardPunched');
        if (card == null) card = CPlayer.mo.FindInventory('RFTimeCard');
        if (card != null && card.Icon.IsValid() && Level.MapName ~== "RF04")
        {
            double cs = 48 * s / 512;
            DrawTexture(card.Icon, (166 * s, -10 * s), left | DI_ITEM_LEFT_BOTTOM, 1.0, (-1, -1), (cs, cs));
        }

        // Weapon and ammunition (bottom right).
        let weapon = CPlayer.ReadyWeapon;
        if (weapon != null)
        {
            String weaponName = weapon.GetTag();
            double w = 150;
            Fill(0xd00c0a0b, (-10 - w) * s, -48 * s, w * s, 38 * s, right);
            Fill(0xff6b1c22, (-10 - w) * s, -48 * s, w * s, 2 * s, right);
            DrawString(labelFont, weaponName, ((-10 - w + 6) * s, -44 * s), right | DI_ITEM_LEFT_TOP, Font.CR_GREY, 1.0, -1, 0, (s * 0.8, s * 0.8));
            String ammunition = weapon.Ammo1 != null ? FormatNumber(weapon.Ammo1.Amount) : "";
            let fal = RFFAL(weapon);
            if (fal != null)
            {
                ammunition = String.Format("%d | %d", fal.Magazine, fal.ReserveCount());
                if (fal.Reloading)
                    DrawString(labelFont, StringTable.Localize("$RF_HUD_RELOAD"), (-16 * s, -58 * s), right | DI_ITEM_RIGHT_TOP | DI_TEXT_ALIGN_RIGHT, Font.CR_TAN, 1.0, -1, 0, (s * 0.7, s * 0.7));
                else if (fal.Magazine == 0 && fal.ReserveCount() > 0 && CPlayer.health > 0)
                    DrawString(labelFont, KeyPrompt("+reload", "$RF_HUD_RELOADHINT"), (-16 * s, -58 * s), right | DI_ITEM_RIGHT_TOP | DI_TEXT_ALIGN_RIGHT, Font.CR_RED, 1.0, -1, 0, (s * 0.7, s * 0.7));
            }
            DrawString(numberFont, ammunition, (-16 * s, -32 * s), right | DI_ITEM_RIGHT_TOP | DI_TEXT_ALIGN_RIGHT, Font.CR_WHITE, 1.0, -1, 0, (s * 1.0, s * 1.0));
        }

        // Objective (top left, small) and level title flash.
        if (director != null)
        {
            if (director.titleTics > 0 && CPlayer.health > 0)
            {
                double a = min(1.0, director.titleTics / 35.0);
                String title = Level.LevelName.MakeUpper();
                String date = ChapterText("DATE");
                // Soft drop shadow first: the title sits over bright plaster at the start.
                DrawString(bigFont, title, (1.5 * s, 93.5 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_BLACK, a * 0.65, -1, 0, (s * 1.35, s * 1.35));
                DrawString(bigFont, title, (0, 92 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_WHITE, a, -1, 0, (s * 1.35, s * 1.35));
                DrawString(labelFont, date, (1 * s, 127 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_BLACK, a * 0.65, -1, 0, (s, s));
                DrawString(labelFont, date, (0, 126 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_GREY, a, -1, 0, (s, s));
            }
            if (director.usePrompt > 0)
            {
                String verb = director.usePrompt == 1 ? "$RF_PROMPT_READ" : director.usePrompt == 2 ? "$RF_PROMPT_OPEN" : "$RF_PROMPT_OPERATE";
                DrawString(labelFont, KeyPrompt("+use", verb), (0, 40 * s), DI_SCREEN_CENTER_BOTTOM | DI_TEXT_ALIGN_CENTER, Font.CR_WHITE, 0.9, -1, 0, (s * 0.85, s * 0.85));
            }
        }

        DrawMessages(s, director != null ? director.objective : "");

        if (CPlayer.health <= 0)
        {
            if (deathStart < 0 || deathStart > Level.maptime) deathStart = Level.maptime;
            DrawDeath(s);
            return;
        }
        deathStart = -1;

        if (director != null && director.outro)
        {
            if (director.comic != null) DrawComic(director, ticFrac);
            else DrawOutro(director.outroTics + ticFrac, s);
            return;
        }
        // Waking up: the first second of a new level fades in from black (titleTics runs 175 -> 0).
        if (director != null && director.titleTics > 140)
            Screen.Dim(0, clamp((director.titleTics - 140 - ticFrac) / 35.0, 0.0, 1.0), 0, 0, Screen.GetWidth(), Screen.GetHeight());

        // Crosshair: a restrained dot, drawn only when the native crosshair is off.
        let ch = CVar.GetCVar('crosshair', CPlayer);
        if (CPlayer.health > 0 && weapon != null && (ch == null || ch.GetInt() == 0))
        {
            Fill(0xb0e8e2d8, -1.2 * s, -1.2 * s, 2.4 * s, 2.4 * s, DI_SCREEN_CENTER);
        }
    }
}
