"""RF2-ART-01: anatomical construction and grounded poses, from one articulated master.
Run: python art/rf2_art_01/enemies/production.py --preview / --family orderly
No gameplay, collision, map or timing edits. Eight actual renders, never mirrored.
"""
from pathlib import Path
import argparse, importlib, json, math, sys, time, struct, datetime
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE/'_pipeline'))
import sdfrig as S
import humanoid as H

ORIGINAL_BODY = H.build_body
ORIGINAL_SHADE = S.shade
ATLAS=np.array(Image.open(HERE/'material_atlas.png').convert('RGB'),dtype=np.float32)/255
CONTEXT={}

def tex_sample(col,row,u,v):
    from scipy.ndimage import map_coordinates
    w=ATLAS.shape[1]//3;h=ATLAS.shape[0]//2
    x=col*w+np.clip(u,0.015,.985)*(w-1);y=row*h+np.clip(v,.015,.985)*(h-1)
    return np.stack([map_coordinates(ATLAS[:,:,k],[y,x],order=1) for k in range(3)],axis=1)

def material_shade(field,hit,nrm,mat_id,materials,light):
    col,n=ORIGINAL_SHADE(field,hit,nrm,mat_id,materials,light)
    rig=CONTEXT['rig']; wb=CONTEXT['bones'];m=CONTEXT['family'];Rmodel=CONTEXT['rotation'];off=CONTEXT['offset']
    local=(hit-off)@Rmodel
    headR,headT=wb['head'];head=(local-headT)@headR
    chestR,chestT=wb['chest'];chest=(local-chestT)@chestR
    skin_ids=[k for k,v in materials.items() if v.name in ('skin','scalp','hair','eye')]
    sel=np.isin(mat_id,skin_ids)&(head[:,2]>-.6)&(head[:,2]<11.5)&(head[:,0]>1.7)
    if sel.any():
        h=head[sel];u=.5-h[:,1]/9.5
        v=np.interp(h[:,2],[.0,2.1,3.45,5.15,10.8],[.91,.66,.55,.36,0])
        skin=tex_sample(0,0,u,v)**2.2
        # Local frontal coverage fades to the modeled ears/scalp at the temples.
        weight=np.clip((h[:,0]-1.7)/1.6,0,1)*np.clip((4.35-np.abs(h[:,1]))/.9,0,1)
        key=np.array(light['key_dir']);key/=np.linalg.norm(key)
        illum=.61+.32*np.maximum(0,nrm[sel]@key)
        col[sel]=col[sel]*(1-weight[:,None])+skin*illum[:,None]*weight[:,None]
    for mid,mat in materials.items():
        if mat.name not in ('tunic','jacket'):continue
        sel=(mat_id==mid)&(np.abs(chest[:,1])<m.PROPS['chest_r'][1]*1.07)
        if not sel.any():continue
        h=chest[sel];front=h[:,0]>0
        u=.5-h[:,1]/(m.PROPS['chest_r'][1]*2.15)
        v=(8.4-h[:,2])/25
        texture=np.empty((len(h),3),np.float32)
        for isfront,column in [(True,1),(False,2)]:
            s=front==isfront
            texture[s]=tex_sample(column,0 if mat.name=='tunic' else 1,u[s],v[s])
        texture=np.minimum(texture,.69)**2.2
        factor=np.clip(col[sel]/np.maximum(np.array(mat.albedo),.02),.35,1.12)
        col[sel]=texture*factor
    return col,n

S.shade=material_shade

def tailored_body(rig, P, M, **kw):
    ORIGINAL_BODY(rig, P, M, **kw)
    # Replace separate chest/pelvis balloons with a continuous tailored volume.
    rig.prims = [p for p in rig.prims if not (p.bone in ('root','spine','chest') and p.group=='body')]
    cr = P['chest_r']; pr = P['pelvis_r']; torso=M['torso']
    rig.add('rbox','chest',(0,0,-.6),(cr[0]*.88,cr[1]*.97,cr[2]*.98,1.7),torso,blend=2.4)
    rig.add('rbox','spine',(.1,0,-.5),(cr[0]*.82,cr[1]*.74,5.5,1.7),torso,blend=2.8)
    rig.add('rbox','root',(.1,0,-.8),(pr[0],pr[1]*1.04,pr[2]*1.12,1.3),M['pelvis'],blend=2.6)
    # Elbows stay under continuous sleeves; shoulders have a cloth cap, not a ball.
    for side in ('l','r'):
        for p in rig.prims:
            if p.bone == 'shoulder_'+side and p.kind=='ellipsoid':
                r=P['deltoid_r'];p.params=(r*.88,r*.84,r*.93)
        if M['arm_upper'] != M['skin']:
            r=P['upper_arm_r'][1]
            rig.add('cylinder','elbow_'+side,(0,0,.8),(1.2,r+.2,.25),M['arm_upper'],group='cuff_'+side,blend=0)
        # Construct a few actual fabric folds at loaded joints, not uniform noise.
        rr=P['thigh_r'][1]
        for k in range(2):
            rig.add('ellipsoid','knee_'+side,(rr*.83,0,1.7+k*1.5),(.24,rr*.75,.36),M['leg_upper'],blend=.28)
    # Placket, button row and sewn garment edges attach to the chest bone.
    if torso == M['pelvis']:
        front=cr[0]*.88
        rig.add('rbox','chest',(front+.02,0,-.3),(.12,.34,6.5,.09),torso,group='placket',blend=0)
        for z in (-4,-.8,2.4,5.6):
            rig.add('ellipsoid','chest',(front+.18,0,z),(.14,.23,.23),M.get('shoe',M['skin']),group='buttons',blend=0)

def human_head(rig,M,skull=(4.5,4.1,5.3),jaw_open=0,brow=1,gaunt=.5,sockets=True,
               eyes=True,ears=True,mouth=True,nose=1,bone='head',group='head',offset=(.8,0,4.8)):
    x,y,z=offset; sx,sy,sz=skull; skin=M['skin']
    # Adult skull and flesh with small orbital recesses. No skull-shaped carved cheeks.
    rig.add('ellipsoid',bone,(x-.45,y,z+.65),(sx*.95,sy*.94,sz*.94),M['scalp'],group=group,blend=1.2)
    rig.add('rbox',bone,(x+1,y,z-1.8),(sx*.69,sy*.77,sz*.56,1.3),skin,group=group,blend=1.6)
    rig.add('ellipsoid',bone,(x+sx*.66,y,z-3.55),(1.7,sy*.56,1.6),skin,group=group,blend=1)
    rig.add('ellipsoid',bone,(x+sx*.56,y,z+2.0),(1.65,sy*.81,2.2),skin,group=group,blend=1.1)
    for sign in (-1,1):
        ey=y+sign*1.6
        rig.add('ellipsoid',bone,(x+sx*.63,y+sign*2.25,z-.9),(1.35,1.3,1.9),skin,group=group,blend=1)
        rig.add('ellipsoid',bone,(x+sx*.82,ey,z+.45),(.65,1.03,.46),skin,group=group,blend=.12,op='subtract')
        # Narrow visible eye, skin lids and brow following the orbital rim.
        if eyes:
            rig.add('ellipsoid',bone,(x+sx*.78,ey,z+.38),(.22,.72,.23),M['eye'],group='eyes',blend=0)
        rig.add('ellipsoid',bone,(x+sx*.83,ey,z+.93),(.46,1.08,.31),skin,group=group,blend=.4)
        rig.add('ellipsoid',bone,(x+sx*.83,ey,z+.02),(.32,.93,.2),skin,group=group,blend=.32)
        if ears:
            rig.add('ellipsoid',bone,(x-.25,y+sign*sy*.99,z-.6),(.6,.47,1.23),skin,group=group,blend=.3)
            rig.add('ellipsoid',bone,(x+.05,y+sign*sy,z-.55),(.25,.22,.66),skin,group=group,blend=.12,op='subtract')
    if nose:
        rig.capsule_between(bone,(x+sx*.83,y,z+1.0),(x+sx*1.02,y,z-1.22),.42,skin,r2=.56,group=group,blend=.48)
        rig.add('ellipsoid',bone,(x+sx*1.06,y,z-1.35),(.68,.72,.48),skin,group=group,blend=.42)
        for sign in (-1,1):
            rig.add('ellipsoid',bone,(x+sx*.98,y+sign*.64,z-1.63),(.36,.34,.23),skin,group=group,blend=.25)
    if mouth:
        rig.add('ellipsoid',bone,(x+sx*.81,y,z-2.7),(.48,1.38,.29),skin,group=group,blend=.35)
        rig.add('rbox',bone,(x+sx*.88,y,z-2.77),(.23,1.1,.055+min(jaw_open,.25),.04),skin,group=group,blend=.04,op='subtract')

H.build_body=tailored_body
H.build_head=human_head
_arm=H.arm
def anatomical_arm(*args,**kwargs):
    p=_arm(*args,**kwargs)
    for key in p:
        if key.startswith('elbow_'):p[key]=(0,-p[key][1],0)
        elif key.startswith('shoulder_'):p[key]=(-p[key][0],p[key][1],p[key][2])
    return p
H.arm=anatomical_arm
_leg=H.leg
def anatomical_leg(*args,**kwargs):
    p=_leg(*args,**kwargs)
    for key in p:
        if key.startswith('hip_'):p[key]=(-p[key][0],p[key][1],p[key][2])
    return p
H.leg=anatomical_leg
_hand=H.add_hand
def proportioned_hand(*args,**kwargs):
    kwargs['scale']=kwargs.get('scale',1)*.73
    return _hand(*args,**kwargs)
H.add_hand=proportioned_hand

def family_module(name):
    sys.path.insert(0,str(HERE/name))
    m=importlib.import_module(name)
    if getattr(m,'_art_linear',False):return m
    # Input palette is sRGB, the lighting calculation is linear. The old renderer
    # treated these values as linear then applied gamma a second time (washed out).
    for mat in m.MATERIALS.values():
        value=np.array(mat.albedo)
        if mat.name in ('tunic','sheet','paper','shirt'): value=np.minimum(value,.65)
        mat.albedo=tuple(value**2.2)
        if mat.albedo2:mat.albedo2=tuple(np.array(mat.albedo2)**2.2)
        if mat.detail=='cloth':mat.detail_amp=.12
        if mat.detail=='skin':mat.detail_amp=.35
        mat.spec*=.6
    m._art_linear=True
    return m

def corpse_pose(m,stage=1):
    p=H.merge({'spine':(0,0,0),'chest':(0,0,0),'neck':(0,0,0),'head':(0,0,26)},
        H.leg(0,3,0,out=6,side='l'),H.leg(-2,5,0,out=12,side='r'),
        H.arm(swing=0,out=17,elbow=6,side='l'),H.arm(swing=-3,out=26,elbow=10,side='r'))
    p['root_rot']=H.lying(face_down=False,roll=2)
    p['root_offset']=(m.PROPS['pelvis_z'],0,0)
    if m.PREFIX=='BRCD':p['root_offset']=(m.PROPS['pelvis_z']-20,29,0)
    if stage<1:
        p['root_rot']=S.rot_y(-72)
        p['hip_l']=(-8,-12,0);p['knee_l']=(0,20,0)
    return p

LIGHT=dict(S.DEFAULT_LIGHT)
LIGHT.update(key=(.48,.46,.44),fill=(.19,.21,.23),rim=(.08,.09,.10),ambient=(.65,.66,.68))

def render_job(job):
    name,letter,rotation,ppu,ss,out=job
    m=family_module(name)
    _,state,fn,kw=next(s for s in m.STATES if s[0]==letter)
    rig=m.build(**kw)
    if name=='orderly':
        # Texture supplies the pocket/tab once; the mouth strap remains a real
        # asymmetric piece of equipment in front of the reconstructed face.
        rig.prims=[p for p in rig.prims if p.group!='tab']
        for p in rig.prims:
            if p.bone=='head' and p.group=='strap' and p.kind=='rbox' and p.pos[0]>0:p.pos[0]=6.0
    pose=fn(rig) if name=='brancardier' else fn()
    if state=='corpse':pose=corpse_pose(m)
    elif state=='death_3':pose=corpse_pose(m,.85)
    elif name=='porte_registre' and state=='death_2':pose=corpse_pose(m,.65)
    yaw=m.ROT_YAW[rotation]
    if name=='brancardier':pose=m.settle(pose,yaw,**kw)
    # Keep texture coordinates attached to their original bones through all poses.
    rotation_matrix=S.rot_z(yaw)
    dz=rig.snap_to_floor(pose,rotation_matrix) if name!='brancardier' else 0
    CONTEXT.update(rig=rig,bones=rig.world_bones(pose),family=m,rotation=rotation_matrix,offset=np.array([0,0,dz]))
    rgba,ox,oy=S.render(rig,pose,yaw,ppu=ppu,ss=ss,light=LIGHT,floor_snap=name!='brancardier')
    # Conservative canvas trim preserves the origin, alpha and actual world scale.
    yy,xx=np.where(rgba[:,:,3]>0)
    if len(xx):
        x0=max(0,int(xx.min())-3);x1=min(rgba.shape[1],int(xx.max())+4)
        y0=max(0,int(yy.min())-3);y1=min(rgba.shape[0],max(int(yy.max())+4,oy+2))
        rgba=rgba[y0:y1,x0:x1];ox-=x0;oy-=y0
    path=Path(out)/f'{m.PREFIX}{letter}{rotation}.png';path.parent.mkdir(parents=True,exist_ok=True)
    S.save_sprite(rgba,path,ox,oy)
    return dict(file=path.name,state=state,rotation=rotation,dimensions=[rgba.shape[1],rgba.shape[0]],grab=[ox,oy],scale=.18)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--family',choices=['orderly','brancardier','porte_registre','remaining']);ap.add_argument('--preview',action='store_true');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--resume-after',help='Reuse complete PNGs from this local ISO timestamp, only when sources are unchanged');args=ap.parse_args()
    names=['brancardier','porte_registre'] if args.family=='remaining' else [args.family] if args.family else ['orderly','brancardier','porte_registre']
    jobs=[]
    for name in names:
        m=family_module(name)
        states=[s for s in m.STATES if s[1] in ('idle','corpse')] if args.preview else m.STATES
        out=ROOT/'art_pass/previews'/name if args.preview else ROOT/'src/sprites/enemies'
        jobs.extend((name,s[0],r,5,2,str(out)) for s in states for r in ([1,3] if args.preview else range(1,9)))
    start=time.monotonic();cached=[]
    if args.resume_after:
        cutoff=datetime.datetime.fromisoformat(args.resume_after).timestamp();pending=[]
        for job in jobs:
            name,letter,rotation,ppu,ss,out=job;m=family_module(name);p=Path(out)/f'{m.PREFIX}{letter}{rotation}.png'
            try:
                assert p.stat().st_mtime>=cutoff
                im=Image.open(p);size=im.size;im.verify();raw=p.read_bytes();idx=raw.index(b'grAb');grab=struct.unpack('>ii',raw[idx+4:idx+12])
                cached.append(dict(file=p.name,state=next(s[1] for s in m.STATES if s[0]==letter),rotation=rotation,dimensions=list(size),grab=list(grab),scale=.18))
            except (OSError,AssertionError,ValueError):pending.append(job)
        jobs=pending;print(f'Reusing {len(cached)} complete frames, rendering {len(jobs)}',flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results=cached
        for r in pool.map(render_job,jobs):results.append(r);print(r['file'],r['dimensions'],flush=True)
    target=HERE/('preview_manifest.json' if args.preview else f'manifest_{args.family or "all"}.json')
    results.sort(key=lambda r:r['file'])
    target.write_text(json.dumps(results,indent=2),encoding='utf8')
    print(f'{len(results)} frames, {time.monotonic()-start:.1f}s',flush=True)
if __name__=='__main__':main()
