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

    override void Init()
    {
        Super.Init();
        SetSize(0, 640, 360);
        Font small = "NewSmallFont";
        Font big = "BigFont";
        labelFont = HUDFont.Create(small);
        numberFont = HUDFont.Create(big);
        bigFont = HUDFont.Create(big);
    }

    override void Draw(int state, double ticFrac)
    {
        Super.Draw(state, ticFrac);
        if (state != HUD_StatusBar && state != HUD_Fullscreen) return;
        if (CPlayer == null || CPlayer.mo == null) return;

        let setting = CVar.GetCVar('rf_hud_scale', CPlayer);
        double s = setting != null ? clamp(setting.GetFloat(), 0.75, 1.5) : 1.0;
        BeginHUD(1.0, false, 640, 360);

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
                else if (fal.Magazine == 0 && fal.ReserveCount() > 0)
                    DrawString(labelFont, StringTable.Localize("$RF_HUD_RELOADHINT"), (-16 * s, -58 * s), right | DI_ITEM_RIGHT_TOP | DI_TEXT_ALIGN_RIGHT, Font.CR_RED, 1.0, -1, 0, (s * 0.7, s * 0.7));
            }
            DrawString(numberFont, ammunition, (-16 * s, -32 * s), right | DI_ITEM_RIGHT_TOP | DI_TEXT_ALIGN_RIGHT, Font.CR_WHITE, 1.0, -1, 0, (s * 1.0, s * 1.0));
        }

        // Objective (top left, small) and level title flash.
        if (director != null)
        {
            if (director.objective != "")
                DrawString(labelFont, director.objective, (12 * s, 10 * s), DI_SCREEN_LEFT_TOP | DI_ITEM_LEFT_TOP, Font.CR_GREY, 0.85, -1, 0, (s * 0.75, s * 0.75));
            if (director.titleTics > 0)
            {
                double a = min(1.0, director.titleTics / 35.0);
                DrawString(bigFont, Level.LevelName, (0, 96 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_WHITE, a, -1, 0, (s * 1.1, s * 1.1));
                DrawString(labelFont, StringTable.Localize("$RF_RF01_DATE"), (0, 124 * s), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_CENTER, Font.CR_GREY, a, -1, 0, (s * 0.85, s * 0.85));
            }
            if (director.usePrompt != "")
                DrawString(labelFont, director.usePrompt, (0, 40 * s), DI_SCREEN_CENTER_BOTTOM | DI_TEXT_ALIGN_CENTER, Font.CR_WHITE, 1.0, -1, 0, (s * 0.85, s * 0.85));
        }

        // Crosshair: a restrained dot, drawn only when the native crosshair is off.
        let ch = CVar.GetCVar('crosshair', CPlayer);
        if (CPlayer.health > 0 && weapon != null && (ch == null || ch.GetInt() == 0))
        {
            Fill(0xb0e8e2d8, -1.2 * s, -1.2 * s, 2.4 * s, 2.4 * s, DI_SCREEN_CENTER);
        }
    }
}
