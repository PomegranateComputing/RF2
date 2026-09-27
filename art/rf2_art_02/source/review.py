"""Isolated review packaging and serial engine captures; never imports to the active game."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, sys, zipfile

HERE=Path(__file__).resolve().parent; LOT=HERE.parent; ROOT=LOT.parents[2]
BASE=Path('C:/PROJECTS/RF2_UZDOOM/dist/review/RF2_ART_REVIEW_20260926_1451/RF2_ART_REVIEW.pk3')
REVIEW=LOT/'review'
sys.path.insert(0,str(ROOT/'scripts'))

def package(preview=False):
    REVIEW.mkdir(exist_ok=True)
    base=REVIEW/'REFERENCE_5b53d9e.pk3'
    if not base.exists():shutil.copy2(BASE,base)
    overlays={p.relative_to(LOT/'runtime').as_posix():p for p in (LOT/'runtime').rglob('*') if p.is_file()}
    if preview:
        overlays.update({'sprites/enemies/'+p.name:p for p in (LOT/'evidence/sprite_preview').glob('*.png')})
    output=REVIEW/('RF2_ART_02_PREVIEW.pk3' if preview else 'RF2_ART_02_CANDIDATE.pk3')
    with zipfile.ZipFile(base) as src,zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as dst:
        for item in src.infolist():
            if item.filename not in overlays:dst.writestr(item,src.read(item.filename))
        for name,path in sorted(overlays.items()):dst.write(path,name)
    print(output,flush=True)
    return output

def capture(pk3,name,mode):
    import devrun
    devrun.ROOT=ROOT;devrun.DEV=REVIEW/'engine'
    devrun.DEV.mkdir(parents=True,exist_ok=True)
    cfg=devrun.DEV/'uzdoom.ini'
    if not cfg.exists():cfg.write_text('',encoding='utf8')
    os.environ['RF_DEV_HIDDEN']='1'
    args=['+rf_dev_autopilot','0','+rf_dev_art_combat','0','+rf_dev_weapons','0','+rf_dev_corpse','0',
          '+screenshot_quiet','1','+r_drawplayersprites','0','+screenblocks','12']
    if mode=='corpses':args+=['+rf_dev_corpse','1'];marker='RF_DEV_CORPSE_DONE'
    elif mode=='combat':args+=['+rf_dev_art_combat','1'];marker='RF_DEV_ART_COMBAT_DONE'
    else:args+=['+rf_dev_weapons','1'];marker='RF_DEV_WEAPONS_DONE'
    status,log,shots=devrun.run(pk3,name,'RF01',seconds=100,marker=marker,extra=args,width=1920,height=1080,speed=1)
    result={'name':name,'package':str(pk3),'package_sha256':hashlib.sha256(Path(pk3).read_bytes()).hexdigest(),
            'status':status,'screenshots':len(list(shots.glob('*.png'))),'width':1920,'height':1080,
            'config_sha256':hashlib.sha256(cfg.read_bytes()).hexdigest(),'extra':args,'hidden_desktop':True,
            'audio_audition':False}
    (LOT/'evidence'/f'{name}.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result),flush=True)
    if not status.startswith('marker:'):raise RuntimeError(status)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--baseline',action='store_true')
    ap.add_argument('--capture',choices=['lineup','corpses','combat']);a=ap.parse_args()
    pk3=package(a.preview)
    if a.baseline:pk3=REVIEW/'REFERENCE_5b53d9e.pk3'
    if a.capture:capture(pk3,('baseline' if a.baseline else 'preview' if a.preview else 'candidate')+'_'+a.capture,a.capture)

if __name__=='__main__':main()
