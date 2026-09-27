"""Read-only snapshot of Opus's current UI, with this lot's assets for local review.
Never writes or patches the active repository. Uncommitted source is identified.
"""
from pathlib import Path
import hashlib,json,subprocess,zipfile,sys,os,difflib
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2]
ACTIVE=Path('C:/PROJECTS/RF2_UZDOOM')

def main():
    original={p.relative_to(ACTIVE/'src').as_posix():p.read_bytes() for p in (ACTIVE/'src').rglob('*') if p.is_file()}
    changed=[n for n,data in original.items() if data!=(ACTIVE/'src'/n).read_bytes()]
    assert not changed,('Active files changed during snapshot; retry later',changed)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ACTIVE,text=True).strip()
    status=subprocess.check_output(['git','status','--short'],cwd=ACTIVE,text=True)
    hashes={n:hashlib.sha256(data).hexdigest() for n,data in original.items()}
    name='zscript/rf/menu.zs'
    old=original[name].decode('utf8').replace('\r\r\n','\n').replace('\r\n','\n')
    assert 'graphics/ui/RFMENUBG.png' in old, 'Opus title asset path changed; check current sources'
    assert not any(Path(n).stem.lower()=='rftitle' for n in original), 'Texture RFTitle would shadow the font'
    for p in (LOT/'runtime').rglob('*'):
        if p.is_file():original[p.relative_to(LOT/'runtime').as_posix()]=p.read_bytes()
    output=LOT/'review/RF2_UI_01_OPUS_SNAPSHOT.pk3'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for name,data in original.items():z.writestr(name,data)
    (LOT/'evidence/opus_snapshot.json').write_text(json.dumps({'head':head,'uncommitted_status':status,'base_src_hashes':hashes,'package_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'note':'Read-only working tree snapshot. Not an Opus approved build.'},indent=2),encoding='utf8')
    if '--package-only' in sys.argv:
        print('Read-only Opus snapshot packaged; engine capture deferred.');return
    sys.path.insert(0,str(ROOT/'scripts'));import devrun
    devrun.ROOT=ROOT;devrun.DEV=LOT/'review/opus_engine';devrun.DEV.mkdir(parents=True,exist_ok=True)
    cfg=devrun.DEV/'uzdoom.ini'
    if not cfg.exists():cfg.write_text('',encoding='utf8')
    os.environ['RF_DEV_HIDDEN']='1'
    reports=[]
    for mode in (2,1):
        name='opus_title' if mode==2 else 'opus_pause'
        status,log,shots=devrun.run(output,name,None if mode==2 else 'RF01',seconds=40,marker='RF_DEV_UI_DONE',extra=['+language','fr','+rf_dev_ui',str(mode),'+screenshot_quiet','1'],width=1920,height=1080)
        reports.append(dict(name=name,status=status,shots=[str(p.relative_to(LOT)) for p in sorted(shots.glob('*.png'),key=lambda p:p.stat().st_mtime_ns)]))
        (LOT/'evidence/opus_snapshot_captures.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
        assert status.startswith('marker:'),(status,log[-1500:])
    print('Opus snapshot captured with ten contract assets; code and SNDINFO unchanged.',flush=True)

if __name__=='__main__':main()
