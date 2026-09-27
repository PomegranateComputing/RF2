"""Serial hidden UZDoom captures of the isolated menu candidate."""
from pathlib import Path
import argparse,json,os,sys,zipfile
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));import devrun
devrun.ROOT=ROOT;devrun.DEV=LOT/'review/engine';devrun.DEV.mkdir(exist_ok=True,parents=True)
cfg=devrun.DEV/'uzdoom.ini'
if not cfg.exists():cfg.write_text('',encoding='utf8')
os.environ['RF_DEV_HIDDEN']='1'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compile',action='store_true');ap.add_argument('--pages',action='store_true');ap.add_argument('--width',type=int,default=1920);ap.add_argument('--height',type=int,default=1080);a=ap.parse_args()
    pk3=LOT/'review/RF2_UI_01_CANDIDATE.pk3'
    if a.pages:
        # Test-only extension of the existing UI screenshot sequence. This file is
        # never part of the import patch or the playable candidate.
        with zipfile.ZipFile(pk3) as z:
            dev=z.read('zscript/rf/dev.zs').decode('utf8')
        old='        if (uiMenuTics == 45) Console.Printf("RF_DEV_UI_DONE");'
        assert old in dev
        dev=dev.replace(old,'''        if (uiMenuTics == 45) Menu.SetMenu('RFOptionsMenu');
        if (uiMenuTics == 90) Menu.SetMenu('LoadGameMenu');
        if (uiMenuTics == 135) Menu.SetMenu('SaveGameMenu');
        if (uiMenuTics == 65 || uiMenuTics == 110 || uiMenuTics == 155) Level.MakeScreenShot();
        if (uiMenuTics == 175) Console.Printf("RF_DEV_UI_DONE");''')
        out=LOT/'review/RF2_UI_01_PAGES_TEST.pk3'
        with zipfile.ZipFile(pk3) as z,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as w:
            for item in z.infolist():
                w.writestr(item,dev if item.filename=='zscript/rf/dev.zs' else z.read(item.filename))
        (LOT/'evidence/pages_test_dev.zs').write_text(dev,encoding='utf8')
        status,log,shots=devrun.run(out,'ui_pages','RF01',seconds=40,marker='RF_DEV_UI_DONE',extra=['+language','fr','+rf_dev_ui','1','+screenshot_quiet','1'],width=a.width,height=a.height)
        assert status.startswith('marker:'),(status,log[-1500:])
        print(status,'native pages:',len(list(shots.glob('*.png'))));return
    if a.compile:
        status,log,shots=devrun.run(pk3,'compile',norun=True,seconds=30)
        print(log[-2500:]);assert status in ('exited rc=0','exited rc=1337') and 'D_CheckNetGame' in log and 'Script error' not in log,status;return
    reports=[]
    for mode in [2,1]:
        name=f'ui_{a.width}x{a.height}_'+('title' if mode==2 else 'pause')
        status,log,shots=devrun.run(pk3,name,None if mode==2 else 'RF01',seconds=40,marker='RF_DEV_UI_DONE',
            extra=['+language','fr','+rf_dev_ui',str(mode),'+screenshot_quiet','1'],width=a.width,height=a.height)
        assert status.startswith('marker:'),(status,log[-1500:])
        reports.append(dict(name=name,status=status,screenshots=len(list(shots.glob('*.png')))))
    (LOT/'evidence'/f'captures_{a.width}x{a.height}.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
    print(json.dumps(reports))

if __name__=='__main__':main()
