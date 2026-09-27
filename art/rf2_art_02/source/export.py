"""RF2-ART-02: material-only re-render from the accepted rig and animation.

No geometry, pose, camera, crop, scale, alpha or runtime code changes.
python incoming/astra/RF2_ART_02/source/export.py --preview
python incoming/astra/RF2_ART_02/source/export.py --workers 4
"""
from pathlib import Path
import argparse, hashlib, json, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
LOT = HERE.parent
ROOT = LOT.parents[2]
sys.path.insert(0, str(HERE / 'enemies'))
import production as P

_family = P.family_module

def family(name):
    m = _family(name)
    if getattr(m, '_art02', False):
        return m
    for mat in m.MATERIALS.values():
        # Adjust each real material, not the image or the level's lighting.
        if mat.name in ('tunic', 'jacket'):
            row = 0 if mat.name == 'tunic' else 1
            patch = P.ATLAS[row*512+230:row*512+420, 1024+70:1024+240]
            mat.albedo = tuple(np.median(patch.reshape(-1, 3), axis=0)**2.2)
        if mat.name == 'skin':
            mat.spec = .025
            mat.rough = .85
        if mat.name in ('paper', 'manila', 'sheet'):
            mat.albedo = tuple(np.array(mat.albedo) * (.76 if mat.name == 'sheet' else .90))
        if mat.name.startswith('book_'):
            mat.albedo = tuple(np.array(mat.albedo) * np.array([.84, .86, .90]))
        if mat.name == 'brass':
            mat.albedo = tuple(np.array(mat.albedo)*.73)
            mat.spec *= .65
        if mat.name == 'label':
            mat.albedo = tuple(np.array(mat.albedo)*.75)
    m._art02 = True
    return m

P.family_module = family

def nearest_limb(local, wb, bones):
    """Stable cylindrical coordinates in the nearest articulated limb segment."""
    best = np.full(len(local), 1e9)
    coords = np.zeros_like(local)
    for bone, length in bones:
        if bone not in wb:
            continue
        rot, origin = wb[bone]
        q = (local-origin) @ rot
        d = q[:, 0]**2 + q[:, 1]**2 + (q[:, 2]-np.clip(q[:, 2], -length, 0))**2
        take = d < best
        best[take] = d[take]
        coords[take] = q[take]
    return coords, best

def shade(field, hit, nrm, mids, materials, light):
    col, n = P.ORIGINAL_SHADE(field, hit, nrm, mids, materials, light)
    wb = P.CONTEXT['bones']; m = P.CONTEXT['family']
    local = (hit-P.CONTEXT['offset']) @ P.CONTEXT['rotation']
    rot, origin = wb['head']; head = (local-origin) @ rot
    rot, origin = wb['chest']; chest = (local-origin) @ rot
    bones = [(f'{b}_{s}', m.PROPS[l]) for s in ('l', 'r') for b,l in
             [('shoulder','upper_arm'),('elbow','forearm'),('hip','thigh'),('knee','shin')]]
    limb, distance = nearest_limb(local, wb, bones)
    key = np.array(light['key_dir']); key /= np.linalg.norm(key)
    for mid, mat in materials.items():
        take = mids == mid
        if not take.any():
            continue
        q = chest[take]; l = limb[take]; h = head[take]
        old = np.maximum(np.array(mat.albedo), .008)
        illumination = np.clip(col[take]/old, .16, 1.25)
        if mat.name in ('tunic', 'jacket'):
            row = 0 if mat.name == 'tunic' else 1
            # Torso front/back retain the approved placement of pocket and seams.
            u = .5-q[:,1]/(m.PROPS['chest_r'][1]*2.15)
            v = (8.4-q[:,2])/25
            tex = np.empty((len(q), 3), np.float32)
            for front,column in [(True,1),(False,2)]:
                s = (q[:,0]>0) == front
                tex[s] = P.tex_sample(column,row,u[s],v[s])
            # Sleeve mapping takes cloth from the same back panel, never a pocket.
            sleeve = np.abs(q[:,1]) > m.PROPS['chest_r'][1]*.88
            if sleeve.any():
                a = l[sleeve]
                u2 = .13 + .20*(.5+np.arctan2(a[:,1],a[:,0])/(2*np.pi))
                v2 = .30+np.clip(-a[:,2]/m.PROPS['upper_arm'],0,1)*.55
                tex[sleeve] = P.tex_sample(2,row,u2,v2)
            col[take] = np.minimum(tex,.69)**2.2 * illumination
        elif mat.name in ('skin', 'scalp'):
            # Skin on limbs uses the matching featureless tile, bone-attached.
            u = .5 + np.arctan2(l[:,1], l[:,0])/(2*np.pi)
            v = np.mod(-l[:,2]/27, 1)
            tex = P.tex_sample(0,1,u,v)
            tint = np.array([.85,.86,.86]) if m.PREFIX!='PREG' else np.array([.77,.81,.82])
            col[take] = (tex*tint)**2.2 * illumination
        elif mat.name.startswith('book_'):
            # Bookcloth and binding wear remain on the torso throughout poses.
            fibre = .5+.5*np.sin(q[:,2]*8.4+q[:,1]*1.1)*np.sin(q[:,1]*11)
            wear = np.exp(-((np.abs(q[:,1])-7.0)/.6)**2)
            col[take] *= (.94+.08*fibre+.16*wear)[:,None]
    ids = [i for i,mat in materials.items() if mat.name in ('skin','scalp','eye')]
    face = np.isin(mids,ids)&(head[:,2]>-.6)&(head[:,2]<11.5)&(head[:,0]>1.7)
    if face.any():
        q=head[face]; u=.5-q[:,1]/9.5
        v=np.interp(q[:,2],[0,2.1,3.45,5.15,10.8],[.91,.66,.55,.36,0])
        tex=P.tex_sample(0,0,u,v)**2.2
        weight=np.clip((q[:,0]-1.7)/1.6,0,1)*np.clip((4.35-np.abs(q[:,1]))/.9,0,1)
        illum=.55+.36*np.maximum(0,nrm[face]@key)
        col[face]=col[face]*(1-weight[:,None])+tex*illum[:,None]*weight[:,None]
    return col,n

P.S.shade = shade

def job(args):
    return P.render_job(args)

def skins():
    out = LOT/'runtime/models/rf2_art_01'; out.mkdir(parents=True,exist_ok=True)
    for name in ('orderly','brancardier','porte_registre'):
        m = family(name)
        # Keep the approved OBJ and UVs: only its existing diffuse skin changes.
        atlas = Image.new('RGB',(1536,1280),(80,77,72))
        atlas.paste(Image.open(HERE/'enemies/material_atlas.png').convert('RGB'),(0,0))
        for k,mat in m.MATERIALS.items():
            color=tuple(int(v**(1/2.2)*255) for v in mat.albedo)
            atlas.paste(color,(k*64,1060,k*64+60,1120))
        atlas.save(out/f'{name}_skin.png')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true')
    ap.add_argument('--family', choices=['orderly','brancardier','porte_registre'])
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--resume',action='store_true')
    a=ap.parse_args(); start=time.monotonic(); jobs=[]
    out=LOT/('evidence/sprite_preview' if a.preview else 'runtime/sprites/enemies')
    names=[a.family] if a.family else ['orderly','brancardier','porte_registre']
    for name in names:
        m=family(name)
        states=[s for s in m.STATES if s[0] in ('A','C','G','K','M')] if a.preview else m.STATES
        for s in states:
            for r in ([1] if a.preview else range(1,9)):
                if a.resume and (out/f'{m.PREFIX}{s[0]}{r}.png').exists():
                    try:
                        Image.open(out/f'{m.PREFIX}{s[0]}{r}.png').verify()
                        continue
                    except (OSError,ValueError,SyntaxError):
                        pass
                jobs.append((name,s[0],r,5,2,str(out)))
    results=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for result in pool.map(job,jobs):
            results.append(result); print(result['file'],round(time.monotonic()-start,1),flush=True)
    if not a.preview: skins()
    (LOT/'evidence'/('preview_render.json' if a.preview else f'render_{a.family or "all"}.json')).write_text(json.dumps(results,indent=2),encoding='utf8')
    print('Rendered',len(results),'in',round(time.monotonic()-start,1),'seconds',flush=True)

if __name__=='__main__':main()
