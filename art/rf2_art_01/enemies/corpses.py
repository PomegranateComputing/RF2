"""Static terminal OBJ corpses sampled from the same articulated SDF character masters.
No new runtime actor, no gravity/collision changes; MODELDEF maps only terminal frames.
Output uses the existing models namespace; a reproducible source copy travels with the art.
"""
from pathlib import Path
import argparse,json,sys,time
import numpy as np
from PIL import Image
from skimage.measure import marching_cubes
import production as P
S=P.S
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
OUT=ROOT/'src/models/rf2_art_01'

def make(name):
    start=time.monotonic();m=P.family_module(name)
    _,_,_,kw=next(s for s in m.STATES if s[1]=='corpse')
    rig=m.build(**kw);pose=P.corpse_pose(m)
    if name=='orderly':
        rig.prims=[p for p in rig.prims if p.group!='tab']
        for p in rig.prims:
            if p.bone=='head' and p.group=='strap' and p.kind=='rbox' and p.pos[0]>0:p.pos[0]=6.0
    if name=='brancardier':pose=m.settle(pose,0,**kw);dz=0
    else:dz=rig.snap_to_floor(pose)
    wb=rig.place(pose,model_off=(0,0,dz));lo,hi=rig.bbox(1)
    print(name,'sampling',lo,hi,flush=True)
    # Tight bounds via a coarse pass, then a dense signed distance mesh of the surface.
    coarse=S.VoxelSDF(rig,lo,hi,voxel=1.5,pad=0)
    occupied=np.array(np.where(coarse.grid<1)).T
    lo=coarse.lo+occupied.min(axis=0)*1.5-1.8;hi=coarse.lo+occupied.max(axis=0)*1.5+1.8
    step=.55 if name!='brancardier' else .7
    field=S.VoxelSDF(rig,lo,hi,voxel=step,pad=0)
    verts,faces,normals,_=marching_cubes(field.grid,level=0,spacing=(step,step,step),allow_degenerate=False)
    verts+=field.lo;verts[:,2]-=verts[:,2].min()
    centers=verts[faces].mean(axis=1);_,mid=rig.sdf(centers,want_material=True)
    # Shared diffuse atlas plus compact original palette for equipment.
    atlas=Image.new('RGB',(1536,1280),(80,77,72));atlas.paste(Image.open(HERE/'material_atlas.png').convert('RGB'),(0,0))
    for k,mat in m.MATERIALS.items():
        color=tuple(int(v**(1/2.2)*255) for v in mat.albedo)
        atlas.paste(color,(k*64,1060,k*64+60,1120))
    OUT.mkdir(parents=True,exist_ok=True);atlas.save(OUT/f'{name}_skin.png')
    lines=[f'# RF2-ART-01 {name}. Y-up OBJ, genuine grounded terminal pose.',f'o {name}_corpse',f'usemtl {name}_skin.png']
    lines += [f'v {x:.5f} {z:.5f} {-y:.5f}' for x,y,z in verts]
    # Smooth normals from the distance field; gradient is outward, unlike MC defaults.
    nr=S.normals(rig,verts,eps=.07)
    lines += [f'vn {x:.6f} {z:.6f} {-y:.6f}' for x,y,z in nr]
    triangles=[];uvindex=0
    for fi,face in enumerate(faces):
        material=m.MATERIALS[int(mid[fi])];pts=verts[face]-np.array([0,0,dz]);uv=[]
        if material.name in ('tunic','jacket'):
            R,t=wb['chest'];q=(pts-t)@R;front=q[:,0].mean()>0
            u=.5-q[:,1]/(m.PROPS['chest_r'][1]*2.15);v=(8.4-q[:,2])/25
            x=(1 if front else 2)*512+np.clip(u,.015,.985)*511;y=(0 if material.name=='tunic' else 512)+np.clip(v,.015,.985)*511
        elif material.name in ('skin','scalp','eye'):
            R,t=wb['head'];q=(pts-t)@R
            if q[:,2].mean()>-.6 and q[:,2].mean()<11.5 and q[:,0].mean()>1.7:
                x=np.clip(.5-q[:,1]/9.5,.015,.985)*511;y=np.interp(q[:,2],[0,2.1,3.45,5.15,10.8],[.91,.66,.55,.36,0])*511
            else:x=np.mod(pts[:,1]*.05,1)*500;y=512+np.mod(pts[:,0]*.04,1)*500
        else:
            x=np.full(3,int(mid[fi])*64+30);y=np.full(3,1090)
        for a,b in zip(x,y):lines.append(f'vt {a/1536:.6f} {1-b/1280:.6f}')
        # MC uses inward face winding for the negative-inside field; reverse it.
        triangles.append('f '+' '.join(f'{int(face[j])+1}/{uvindex+j+1}/{int(face[j])+1}' for j in (2,1,0)))
        uvindex+=3
    lines+=triangles;(OUT/f'{name}.obj').write_text('\n'.join(lines)+'\n',encoding='utf8')
    result=dict(name=name,vertices=len(verts),triangles=len(faces),source_bounds=[verts.min(axis=0).tolist(),verts.max(axis=0).tolist()],world_scale=.9,voxel=step,seconds=time.monotonic()-start)
    import shutil
    src=HERE/'model_exports';src.mkdir(exist_ok=True)
    for suffix in ('.obj','_skin.png'):shutil.copy2(OUT/f'{name}{suffix}',src/f'{name}{suffix}')
    print(result,flush=True);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--family',default='all');a=ap.parse_args()
    names=['orderly','brancardier','porte_registre'] if a.family=='all' else [a.family]
    r=[make(n) for n in names];(HERE/f'corpse_models_{a.family}.json').write_text(json.dumps(r,indent=2),encoding='utf8')
if __name__=='__main__':main()
