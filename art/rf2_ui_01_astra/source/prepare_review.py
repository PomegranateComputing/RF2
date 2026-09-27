"""Builds the historical 5b53d9e style study, not a patch for Opus's newer menus."""
from pathlib import Path
import difflib,json,hashlib,zipfile
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2]

STYLE='''
// RF2-UI-01 presentation only; native navigation and save management are inherited.
class RFUIStyle ui
{
    static void Sheet()
    {
        let tex = TexMan.CheckForTexture("graphics/RF2_UI_SHEET.png", TexMan.Type_Any);
        Screen.DrawTexture(tex, true, 0, 0, DTA_DestWidth, Screen.GetWidth(), DTA_DestHeight, Screen.GetHeight());
    }
}

class RFUILoadMenu : LoadMenu
{
    override void Drawer() { RFUIStyle.Sheet(); Super.Drawer(); }
    override void DrawFrame(int left, int top, int width, int height)
    {
        Screen.DrawLineFrame(Color(255, 108, 113, 108), left, top, width, height, max(1, Screen.GetHeight()/720));
    }
}

class RFUISaveMenu : SaveMenu
{
    override void Drawer() { RFUIStyle.Sheet(); Super.Drawer(); }
    override void DrawFrame(int left, int top, int width, int height)
    {
        Screen.DrawLineFrame(Color(255, 108, 113, 108), left, top, width, height, max(1, Screen.GetHeight()/720));
    }
}
'''

def main():
    original={p:(ROOT/'src'/p).read_text(encoding='utf8') for p in ['zscript/rf/menu.zs','MENUDEF','SNDINFO']}
    files=dict(original)
    selection='''
    void DrawSelection()
    {
        if (manager == null || Selected < TopItem || Selected >= manager.SavegameCount()) return;
        int row = Selected - TopItem;
        if (row >= listboxRows) return;
        int y = listboxTop + row * rowHeight;
        Screen.SetClipRect(listboxLeft, y, listboxRight, y + rowHeight);
        Screen.Clear(listboxLeft, y, listboxRight, y + rowHeight, mEntering ? Color(255, 116, 61, 65) : Color(255, 93, 39, 46));
        String label = manager.GetSavegame(Selected).SaveTitle;
        int shift = 0;
        if (mEntering)
        {
            label = mInput.GetText() .. NewConsoleFont.GetCursor();
            shift = min(0, listboxWidth - 2 - int(NewConsoleFont.StringWidth(label) * FontScale));
        }
        Screen.DrawText(NewConsoleFont, Font.CR_WHITE, (listboxLeft + 1 + shift) / FontScale, (y + FontScale) / FontScale, label,
            DTA_VirtualWidthF, Screen.GetWidth() / FontScale, DTA_VirtualHeightF, Screen.GetHeight() / FontScale, DTA_KeepRatio, true);
        Screen.ClearClipRect();
    }
'''
    styled=STYLE.replace('override void Drawer() { RFUIStyle.Sheet(); Super.Drawer(); }', 'override void Drawer() { RFUIStyle.Sheet(); Super.Drawer(); DrawSelection(); }'+selection)
    for name in ['RFMainMenu','RFCreditsMenu','RFOptionMenu']:
        parent='OptionMenu' if name=='RFOptionMenu' else 'ListMenu'
        line=f'class {name} : {parent}\n{{'
        draw='if (gamestate == GS_LEVEL) RFUIStyle.Sheet();' if name=='RFMainMenu' else 'RFUIStyle.Sheet();'
        assert line in files['zscript/rf/menu.zs']
        files['zscript/rf/menu.zs']=files['zscript/rf/menu.zs'].replace(line,line+f'\n    override void Drawer() {{ {draw} Super.Drawer(); }}\n',1)
    files['zscript/rf/menu.zs']=files['zscript/rf/menu.zs'].replace("Font.GetFont('RFTitle')","Font.GetFont('RFUITitle')")+styled
    files['zscript/rf/menu.zs']=files['zscript/rf/menu.zs'].replace('        Rebuild();', '''        DontDim = gamestate != GS_LEVEL;
        mDesc.mXpos = int(Screen.GetWidth() * 0.14 / CleanXfac - (Screen.GetWidth() / CleanXfac - 320) / 2);
        Rebuild();''',1)
    files['MENUDEF']=files['MENUDEF'].replace('Font "RFMenu"','Font "RFUIMenu"')+'''

// Native save/load functions, styled frame only.
ListMenu "LoadGameMenu"
{
    NetgameMessage "$LOADNET"
    CaptionItem "$RF_MENU_LOAD"
    Position 80,40
    Class "RFUILoadMenu"
    Size Clean
}
ListMenu "SaveGameMenu"
{
    CaptionItem "$RF_MENU_SAVE"
    Position 80,40
    Class "RFUISaveMenu"
    Size Clean
}
'''
    files['SNDINFO']+='''

// RF2-UI-01: short recorded material cues, isolated from combat sounds.
menu/cursor "ui/RF2_UI_MOVE.wav"
menu/choose "ui/RF2_UI_CHOOSE.wav"
menu/backup "ui/RF2_UI_BACK.wav"
menu/activate "ui/RF2_UI_CONFIRM.wav"
menu/dismiss "ui/RF2_UI_BACK.wav"
'''
    patch=[]; info=[]
    for name,content in files.items():
        dst=LOT/'patches/files'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(content,encoding='utf8')
        patch.extend(difflib.unified_diff(original[name].splitlines(True),content.splitlines(True),fromfile='a/src/'+name,tofile='b/src/'+name))
        info.append(dict(target='src/'+name,base_sha256=hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
    (LOT/'patches/RF2_UI_01.patch').write_text(''.join(patch),encoding='utf8')
    (LOT/'patches/manifest.json').write_text(json.dumps(info,indent=2),encoding='utf8')
    base=LOT.parent/'RF2_ART_02/review/REFERENCE_5b53d9e.pk3'
    paths={p.relative_to(LOT/'runtime').as_posix():p for p in (LOT/'runtime').rglob('*') if p.is_file()}
    study=LOT/'source/style_study'
    paths.update({p.relative_to(study).as_posix():p for p in study.rglob('*') if p.is_file()})
    paths['graphics/TITLEPIC.png']=LOT/'runtime/graphics/ui/RFMENUBG.png'
    paths.update({n:LOT/'patches/files'/n for n in files})
    dst=LOT/'review/RF2_UI_01_CANDIDATE.pk3'
    with zipfile.ZipFile(base) as src,zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
        for item in src.infolist():
            if item.filename not in paths:out.writestr(item,src.read(item.filename))
        for name,path in paths.items():out.write(path,name)
    print(dst,flush=True)

if __name__=='__main__':main()
