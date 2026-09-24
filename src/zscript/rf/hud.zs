// RF2 HUD: only live data. Health with Viktor's portrait, active weapon and its
// real ammunition model, contextual keys, brief objective, use prompt, crosshair.
class RFStatusBar : BaseStatusBar
{
    HUDFont labelFont;
    HUDFont numberFont;
    HUDFont bigFont;

    TextureID ViktorPortrait() const
    {
        if (CPlayer == null || CPlayer.mo == null || CPlayer.health <= 0)
            return TexMan.CheckForTexture("graphics/hud/viktor/VIKTOR_dead.png", TexMan.Type_MiscPatch);
        if (CPlayer.health <= 20) return TexMan.CheckForTexture("graphics/hud/viktor/VIKTOR_critical.png", TexMan.Type_MiscPatch);
        if (CPlayer.health <= 40) return TexMan.CheckForTexture("graphics/hud/viktor/VIKTOR_fatigue.png", TexMan.Type_MiscPatch);
        if (CPlayer.health <= 65) return TexMan.CheckForTexture("graphics/hud/viktor/VIKTOR_injured.png", TexMan.Type_MiscPatch);
        if (CPlayer.health <= 85) return TexMan.CheckForTexture("graphics/hud/viktor/VIKTOR_bruised.png", TexMan.Type_MiscPatch);
        return TexMan.CheckForTexture("graphics/hud/viktor/VIKTOR_intact.png", TexMan.Type_MiscPatch);
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
        StringTable.Localize("$RF_RF01_EXIT").Split(lines, "\n");
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

    override void Init()
    {
        Super.Init();
        SetSize(0, 640, 360);
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
            if (director.objective != "")
                DrawString(labelFont, director.objective, (12 * s, 10 * s), DI_SCREEN_LEFT_TOP | DI_ITEM_LEFT_TOP, Font.CR_GREY, 0.9, -1, 0, (s * 0.9, s * 0.9));
            if (director.titleTics > 0)
            {
                double a = min(1.0, director.titleTics / 35.0);
                String title = Level.LevelName.MakeUpper();
                String date = StringTable.Localize("$RF_RF01_DATE");
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

        if (director != null && director.outro)
        {
            DrawOutro(director.outroTics + ticFrac, s);
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
