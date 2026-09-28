"""Isolated UZDoom comparison using the frozen Opus candidate and local overlays.
No WAD, source runtime or global configuration is modified.
"""
from pathlib import Path
import zipfile,json,hashlib,shutil,sys,os
HERE=Path(__file__).resolve().parent;LOT=HERE.parent
BASE=Path('C:/PROJECTS/RF2_UZDOOM')
PK3=BASE/'dist/candidates/RF2_MAP-02_20260927_1543/RF2_MAP-02.pk3'
REVIEW=LOT/'review';REVIEW.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'scripts'));import devrun
devrun.ROOT=BASE;devrun.DEV=REVIEW/'engine';os.environ['RF_DEV_HIDDEN']='1'
VIEWS='3500 160 0 180 -12; 3400 52 0 344 26; 2990 140 0 270 -14; 2200 48 0 90 -6; 2100 230 0 150 -8; 1140 1104 0 0 -8; 1288 1104 0 0 -26; 1472 1150 0 270 20; 1128 2650 0 90 20; 1500 2700 0 180 -14'
# Let the normal title animation finish without modifying its runtime or hiding the accepted HUD.
WARMUP=12
CAPTURE_VIEWS='; '.join(['3500 160 0 180 -12']*WARMUP+[VIEWS])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    with zipfile.ZipFile(PK3) as z:base={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    files=dict(base);man=json.loads((LOT/'manifest.json').read_text())
    for r in man['files']:
        p=LOT/r['file'];target=r['target_relpath']
        assert hashlib.sha256(base[target]).hexdigest()==r['base_sha256'],target
        files[target]=p.read_bytes()
    candidate=REVIEW/'RF2_MAP_02_ASSETS_REVIEW.pk3'
    with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in files.items():z.writestr(n,b)
    changed=[n for n in files if files[n]!=base[n]]
    assert sorted(changed)==sorted(r['target_relpath'] for r in man['files'])
    results=[]
    for name,pkg in [('baseline',PK3),('candidate',candidate)]:
        status,log,shots=devrun.run(pkg,'rf02_'+name+'_v2','RF02',seconds=40,marker='RF_DEV_UI_DONE',width=1280,height=720,
            extra=['+rf_dev_view',CAPTURE_VIEWS,'+rf_dev_autopilot','0','+rf_dev_tour','0','+rf_dev_ui','0','+rf_dev_film','0','+rf_dev_log','0'])
        dest=LOT/'evidence'/'engine'/name;dest.mkdir(parents=True,exist_ok=True)
        for i,p in enumerate(sorted(shots.glob('*.png'),key=lambda p:p.stat().st_mtime_ns)[WARMUP:]):shutil.copy2(p,dest/f'{i:02}.png')
        (dest/'log.txt').write_text(log,encoding='utf8')
        results.append({'name':name,'package_sha256':sha(pkg),'status':status,'screenshots':len(list(dest.glob('*.png'))),'camera_spec':VIEWS})
        print(name,status,results[-1]['screenshots'],flush=True)
        assert status.startswith('marker:') and results[-1]['screenshots']==10,(status,log[-1000:])
    (LOT/'evidence'/'engine_validation.json').write_text(json.dumps({'base_package_sha256':sha(PK3),'candidate_package_sha256':sha(candidate),'changed_entries':changed,'unchanged_entries':len(base)-len(changed),'maps_code_audio_weapons_unchanged':all(not n.startswith(('maps/','zscript/','sounds/','graphics/weapons/')) for n in changed),'runs':results,'evidence_scope':'Fixed-camera actual-engine comparison. Not playthrough, owner approval or audition.'},indent=2),encoding='utf8')
if __name__=='__main__':main()
