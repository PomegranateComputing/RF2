"""Separate scale-compensated proposal and 3D pram inspection, no active game writes."""
from pathlib import Path
import zipfile,json,hashlib,re,difflib,shutil,os,sys
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;BASE=Path('C:/PROJECTS/RF2_UZDOOM')
sys.path.insert(0,str(HERE));import review_engine as R
P=LOT/'presentation_proposal';REVIEW=LOT/'review'
def write_zip(path,data):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in data.items():z.writestr(n,b)
def run(name,pkg,views,hide=False):
    extra=['+rf_dev_view','; '.join(['3500 160 0 180 -12']*12+[views]),'+rf_dev_autopilot','0','+rf_dev_tour','0','+rf_dev_ui','0','+rf_dev_film','0','+rf_dev_log','0']
    if hide:extra+=['+r_drawplayersprites','0','+screenblocks','12']
    st,log,shots=R.devrun.run(pkg,name,'RF02',seconds=40,marker='RF_DEV_UI_DONE',width=1280,height=720,extra=extra)
    dst=LOT/'evidence'/'engine'/name;dst.mkdir(parents=True,exist_ok=True)
    ps=sorted(shots.glob('*.png'),key=lambda p:p.stat().st_mtime_ns)[12:]
    for i,p in enumerate(ps):shutil.copy2(p,dst/f'{i:02}.png')
    (dst/'log.txt').write_text(log,encoding='utf8')
    assert st.startswith('marker:') and len(ps)==len(views.split(';')),(st,log[-1500:])
    return {'status':st,'package_sha256':R.sha(pkg),'views':views,'shots':len(ps),'hidden_weapons_hud':hide}
def main():
    with zipfile.ZipFile(REVIEW/'RF2_MAP_02_ASSETS_REVIEW.pk3') as z:data={n:z.read(n) for n in z.namelist()}
    original={n:data[n].decode('utf8') for n in ('TEXTURES.rf02','zscript/rf/paris.zs')}
    textures=original['TEXTURES.rf02'];paris=original['zscript/rf/paris.zs'];meta=json.loads((P/'dimensions.json').read_text())
    proposal=[]
    for row in meta['textures']:
        target=row['target_relpath'];name=Path(target).stem;w,h=row['native_pixels'];bw,bh=row['current_pixels']
        pattern=rf'(Texture {name}, )\d+, \d+(\s*\{{\s*XScale )(\d+(?:\.\d+)?)(\s*YScale )(\d+(?:\.\d+)?)'
        def sub(m):return f'{m[1]}{w}, {h}{m[2]}{float(m[3])*w/bw:.8g}{m[4]}{float(m[5])*h/bh:.8g}'
        textures,n=re.subn(pattern,sub,textures);assert n==1,name
        data[target]=(LOT/row['native_master']).read_bytes()
        proposal.append({'file':row['native_master'],'target_relpath':target,'sha256':hashlib.sha256(data[target]).hexdigest(),'kind':'texture','width':w,'height':h,'required_patch':'presentation.diff'})
    for cls,old,new in [('RFFormsBucket','0.55','0.1375'),('RFSacoche','0.5','0.125'),('RFRadioSet','0.5','0.125'),('RFFieldPhone','0.55','0.1375')]:
        pat=rf'(class {cls}\b.*?Default\s*\{{\s*Scale ){re.escape(old)}(;)' 
        paris,n=re.subn(pat,lambda m:m[1]+new+m[2],paris,count=1,flags=re.S);assert n==1,cls
    for row in meta['sprites']:
        target=f'sprites/rf02/{row["resource"]}.png';src=P/'sprites'/f'{row["resource"]}.png';data[target]=src.read_bytes()
        proposal.append({'file':src.relative_to(LOT).as_posix(),'target_relpath':target,'sha256':R.sha(src),'kind':'sprite','width':row['proposed_canvas'][0],'height':row['proposed_canvas'][1],'grAb':row['proposed_grAb'],'actor_scale':row['proposed_actor_scale'],'required_patch':'presentation.diff'})
    data['TEXTURES.rf02']=textures.encode();data['zscript/rf/paris.zs']=paris.encode()
    diff=[]
    for n in original:
        # Frozen PK3 and working tree may use different line endings. Preserve the recipient's
        # exact line ending convention in the review patch, without changing tested PK3 bytes.
        recipient=(BASE/'src'/n).read_bytes().decode('utf8')
        assert recipient.replace('\r\n','\n')==original[n].replace('\r\n','\n'),n
        proposed=data[n].decode().replace('\r\n','\n')
        if '\r\n' in recipient:proposed=proposed.replace('\n','\r\n')
        diff+=difflib.unified_diff(recipient.splitlines(True),proposed.splitlines(True),fromfile='a/src/'+n,tofile='b/src/'+n)
    (P/'presentation.diff').write_bytes(''.join(diff).encode('utf8'))
    (P/'manifest.json').write_text(json.dumps({'status':'OWNER_REVIEW_REQUIRED','base_package_sha256':R.sha(R.PK3),'no_gameplay_timing_changes':True,'requires_atomic_import':['all chosen high-resolution assets','corresponding dimensions/scale patch'],'files':proposal},indent=2),encoding='utf8')
    hd=REVIEW/'RF2_MAP_02_HD_REVIEW.pk3';write_zip(hd,data)
    runs={'hd':run('hd',hd,R.VIEWS)}
    # Independent geometric placement in the open street, not the original pram block.
    zs='''
class RFArtPram : Actor
{
    Default { Radius 24; Height 38; +NOGRAVITY +NOBLOCKMAP }
    States { Spawn: RFAP A -1; Stop; }
}
class RFArtPramReview : EventHandler
{
    override void WorldLoaded(WorldEvent e)
    {
        if (Level.MapName ~== "RF02")
        {
            Actor a = Actor.Spawn("RFArtPram", (3110,150,0.15));
            if (a != null) Console.Printf("RF2_PRAM_REVIEW x=%.3f y=%.3f z=%.3f",a.Pos.X,a.Pos.Y,a.Pos.Z);
        }
    }
}
'''
    md='''
Model RFArtPram
{
    Path "models/astra_review"
    Model 0 "pram.obj"
    Skin 0 "atlas.png"
    Scale 1 1 1.2
    CorrectPixelStretch
    IgnoreTranslation
    FrameIndex RFAP A 0 0
}
'''
    data['ZSCRIPT.txt']+=b'\n#include "zscript/astra_pram_review.zs"\n';data['zscript/astra_pram_review.zs']=zs.encode()
    data['MAPINFO']=data['MAPINFO'].replace(b'"RFDirector", "RFParis", "RFDevHandler"',b'"RFDirector", "RFParis", "RFDevHandler", "RFArtPramReview"')
    data['MODELDEF']+=md.encode();data['models/astra_review/pram.obj']=(HERE/'models/pram.obj').read_bytes();data['models/astra_review/atlas.png']=(HERE/'masters/RF2_MATERIAL_ATLAS.png').read_bytes()
    data['sprites/astra_review/RFAPA0.png']=data['sprites/rf02/RFMCA0.png']
    (P/'pram_review.zs.txt').write_text(zs,encoding='utf8');(P/'pram_MODELDEF.txt').write_text(md,encoding='utf8')
    model=REVIEW/'RF2_MAP_02_PRAM_REVIEW.pk3';write_zip(model,data)
    views='3110 70 0 90 18; 3190 150 0 180 18; 3110 230 0 270 18; 3030 150 0 0 18; 3110 80 48 90 45'
    runs['pram']=run('pram',model,views,True)
    (LOT/'evidence'/'presentation_validation.json').write_text(json.dumps({'status':'executed','runs':runs,'scope':'HD scale presentation proposal plus isolated 3D pram at a test location. Not integrated scene or collision playtest.'},indent=2),encoding='utf8')
if __name__=='__main__':main()
