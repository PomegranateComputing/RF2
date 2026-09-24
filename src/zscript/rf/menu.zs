// Main / pause menu built at open time so the item list matches the game state.
// Native sub-menus (options, load, save, quit, end game) are reused untouched.

class RFMenuItemClose : ListMenuItemTextItem
{
    override bool Activate()
    {
        Menu.MenuSound("menu/choose");
        let current = Menu.GetCurrentMenu();
        if (current != null) current.Close();
        return true;
    }
}

class RFMainMenu : ListMenu
{
    override void Init(Menu parent, ListMenuDescriptor desc)
    {
        Super.Init(parent, desc);
        Rebuild();
    }

    void AddItem(String text, String key, Name child)
    {
        let item = new("ListMenuItemTextItem");
        item.Init(mDesc, text, key, child);
        mDesc.mItems.Push(item);
        mDesc.mYpos += mDesc.mLinespacing;
    }

    void AddClose(String text, String key)
    {
        let item = new("RFMenuItemClose");
        item.Init(mDesc, text, key, 'None');
        mDesc.mItems.Push(item);
        mDesc.mYpos += mDesc.mLinespacing;
    }

    void AddStatic(double x, double y, String text, int color)
    {
        let item = new("ListMenuItemStaticText");
        item.Init(mDesc, x, y, text, color);
        mDesc.mItems.Push(item);
    }

    // Menu title in the larger title face (falls back to the menu font).
    void AddTitle(double x, double y, String text, int color)
    {
        let item = new("ListMenuItemStaticText");
        Font face = Font.GetFont('RFTitle');
        if (face == null) face = mDesc.mFont;
        item.InitDirect(x, y, text, face, color, false);
        mDesc.mItems.Push(item);
    }

    void Rebuild()
    {
        bool inGame = gamestate == GS_LEVEL;
        mDesc.mItems.Clear();
        AddTitle(mDesc.mXpos, mDesc.mYpos - 52, "$RF_MENU_TITLE", Font.CR_WHITE);
        AddStatic(mDesc.mXpos, mDesc.mYpos - 30, inGame ? "$RF_MENU_PAUSE" : "$RF_MENU_SUBTITLE", Font.CR_DARKRED);
        int firstY = mDesc.mYpos;
        if (inGame)
        {
            AddClose("$RF_MENU_RESUME", "r");
            AddItem("$RF_MENU_SAVE", "s", 'SaveGameMenu');
            AddItem("$RF_MENU_LOAD", "c", 'LoadGameMenu');
            AddItem("$RF_MENU_OPTIONS", "o", 'OptionsMenu');
            AddItem("$RF_MENU_MAIN", "m", 'EndGameMenu');
            AddItem("$RF_MENU_QUIT", "q", 'QuitMenu');
        }
        else
        {
            AddItem("$RF_MENU_NEWGAME", "n", 'PlayerclassMenu');
            AddItem("$RF_MENU_LOAD", "c", 'LoadGameMenu');
            AddItem("$RF_MENU_OPTIONS", "o", 'OptionsMenu');
            AddItem("$RF_MENU_CREDITS", "g", 'RFCreditsMenu');
            AddItem("$RF_MENU_QUIT", "q", 'QuitMenu');
        }
        mDesc.mYpos = firstY;
        mDesc.mSelectedItem = 2;
    }
}

class RFCreditsMenu : ListMenu
{
    override void Init(Menu parent, ListMenuDescriptor desc)
    {
        Super.Init(parent, desc);
        mDesc.mItems.Clear();
        double y = mDesc.mYpos - 40;
        Array<String> lines;
        lines.Push("$RF_CREDITS_1");
        lines.Push("$RF_CREDITS_2");
        lines.Push("$RF_CREDITS_3");
        lines.Push("$RF_CREDITS_4");
        lines.Push("$RF_CREDITS_5");
        for (int i = 0; i < lines.Size(); i++)
        {
            let item = new("ListMenuItemStaticText");
            item.Init(mDesc, mDesc.mXpos, y, lines[i], i == 0 ? Font.CR_WHITE : Font.CR_GREY);
            mDesc.mItems.Push(item);
            y += 16;
        }
        int firstY = mDesc.mYpos;
        mDesc.mYpos = y + 12;
        let back = new("RFMenuItemClose");
        back.Init(mDesc, "$RF_MENU_BACK", "r", 'None');
        mDesc.mItems.Push(back);
        mDesc.mYpos = firstY;
        mDesc.mSelectedItem = mDesc.mItems.Size() - 1;
    }
}
