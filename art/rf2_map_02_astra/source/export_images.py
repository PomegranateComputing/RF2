"""Technical export only: dimensions/PNG offsets/hash metadata from frozen sources.
No painting, generative approximation of rotations, or game mutation here.
"""
from pathlib import Path
import json,struct,hashlib,zlib,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;LOT=HERE.parent
BASE=Path('C:/PROJECTS/RF2_UZDOOM')
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def grab(p):
    b=p.read_bytes();i=8
    while i<len(b):
        n=struct.unpack('>I',b[i:i+4])[0]
        if b[i+4:i+8]==b'grAb':return list(struct.unpack('>ii',b[i+8:i+16]))
        i+=n+12
    return None
def save(im,path,anchor=None):
    path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
    if anchor is not None:
        b=path.read_bytes();data=b'grAb'+struct.pack('>ii',*anchor)
        chunk=struct.pack('>I',8)+data+struct.pack('>I',zlib.crc32(data)&0xffffffff)
        path.write_bytes(b[:33]+chunk+b[33:])
def main():
    records=[];hi=[]
    for name in ('RF2_FAC1','RF2_FAC2','RF2_FAC3','RF2_FACU','RF2_TSFS','RF2_AMIG'):
        target=f'patches/rf02/{name}.png';base=BASE/'src'/target;master=HERE/'masters'/f'{name}.png'
        size=Image.open(base).size;im=Image.open(master).convert('RGB')
        dst=LOT/'runtime'/target;save(im.resize(size,Image.Resampling.LANCZOS),dst)
        records.append(record(dst,target,base,master,'texture',size,None,'Replacement at the existing canvas and texture scale. Geometry unchanged.'))
        hi.append({'target_relpath':target,'native_master':master.relative_to(LOT).as_posix(),'native_pixels':list(im.size),'current_pixels':list(size),'scale_multiplier':[im.width/size[0],im.height/size[1]],'instruction':'Change TEXTURES dimensions AND XScale/YScale by the same multiplier if importing native source. Do not replace PNG alone.'})
        plate=Image.new('RGB',(1024,500 if size[0]>size[1] else 940),(28,29,29));d=ImageDraw.Draw(plate)
        for i,src in enumerate((base,dst)):
            a=Image.open(src).convert('RGB');a.thumbnail((494,plate.height-45),Image.Resampling.LANCZOS)
            plate.paste(a,(i*512+(512-a.width)//2,42));d.text((i*512+12,10),('BASE' if i==0 else 'CANDIDATE')+' / '+name,font=FONT,fill='white')
        plate.save(LOT/'evidence'/f'compare_{name}.png')
    # Legacy billboard compatibility candidates. The 3D masters and orbit renders are separate.
    spec=[('bucket','RFBKA0',.55),('satchel','RFBGA0',.5),('radio_off','RFRDA0',.5),('radio_on','RFRDB0',.5),('phone','RFPHA0',.55)]
    sprite_info=[]
    for name,lump,scale in spec:
        target=f'sprites/rf02/{lump}.png';base=BASE/'src'/target;original=Image.open(base).convert('RGBA');anchor=grab(base)
        master=HERE/'renders'/name/'view_000.png';im=Image.open(master).convert('RGBA');im=im.crop(im.getchannel('A').getbbox())
        bb=original.getchannel('A').getbbox();w,h=bb[2]-bb[0],bb[3]-bb[1]
        # Preserve old physical envelope without stretching the new object.
        factor=min(w/im.width,h/im.height);sz=(max(1,round(im.width*factor)),max(1,round(im.height*factor)))
        x=bb[0]+(w-sz[0])//2;y=bb[3]-sz[1]
        out=Image.new('RGBA',original.size);out.alpha_composite(im.resize(sz,Image.Resampling.LANCZOS),(x,y))
        dst=LOT/'runtime'/target;save(out,dst,anchor)
        records.append(record(dst,target,base,master,'sprite',original.size,anchor,'Legacy single billboard compatibility only; not a completed walk-around presentation. Full-volume GLB master and eight geometric view samples provided.'))
        records[-1]['actor_scale']=scale;records[-1]['model_source']=f'source/models/{name}.glb';records[-1]['integration_state']='COMPATIBILITY_REVIEW_ONLY'
        # Four-times canvas proposal keeps the exact same world envelope and pivot.
        out=Image.new('RGBA',(original.width*4,original.height*4));out.alpha_composite(im.resize((sz[0]*4,sz[1]*4),Image.Resampling.LANCZOS),(x*4,y*4))
        hd=LOT/'presentation_proposal'/'sprites'/f'{lump}.png';save(out,hd,[v*4 for v in anchor])
        sprite_info.append({'resource':lump,'legacy_canvas':list(original.size),'legacy_grAb':anchor,'legacy_scale':scale,'proposed_canvas':list(out.size),'proposed_grAb':[v*4 for v in anchor],'proposed_actor_scale':scale/4,'world_envelope_preserved':True,'model':name})
    (LOT/'presentation_proposal').mkdir(exist_ok=True)
    (LOT/'presentation_proposal'/'dimensions.json').write_text(json.dumps({'textures':hi,'sprites':sprite_info,'status':'PROPOSAL_NOT_APPLIED'},indent=2),encoding='utf8')
    (LOT/'manifest.json').write_text(json.dumps({'batch_id':'RF2_MAP_02','status':'OWNER_REVIEW_REQUIRED','source_commit':subprocess.check_output(['git','-C',str(BASE),'rev-parse','HEAD'],text=True).strip(),'files':records,'exclusions':['source/models OBJ/GLB are source/proposals, no consumer patch supplied','suitcase not promoted: shoe silhouette quality insufficient','missing correction pack and figure/weapon/tram/entrance contracts'],'scope':'Six wall/window textures and five legacy compatibility sprites; not RF02 completion'},ensure_ascii=False,indent=2),encoding='utf8')
    print('Exported',len(records),'runtime candidates; exact dimensions/grAb recorded.')
def record(dst,target,base,master,kind,size,anchor,notes):
    return {'file':dst.relative_to(LOT).as_posix(),'target_relpath':target,'kind':kind,'sha256':sha(dst),'bytes':dst.stat().st_size,'width':size[0],'height':size[1],'grAb':anchor,'base_sha256':sha(base),'source':master.relative_to(LOT).as_posix(),'source_sha256':sha(master),'source_method':'Built-in image_gen source + deterministic export' if kind=='texture' else 'Original Blender geometry, packed generated material atlas, same-master orthographic render','license_or_origin':'Original RF2 production, Nameless / Pomegranate Interactive; no third-party image sampled','confidence':'candidate','notes':notes}
if __name__=='__main__':main()
