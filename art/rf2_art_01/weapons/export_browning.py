"""Export all seven BHPG frames from a single generated rear-view master.
Rigid slide travel / locked-open state; no independently generated animation frames.
The original timing and engine select/lower choreography remain unchanged.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE/'browning/master.png'
OUT=ROOT/'src/graphics/weapons/browning'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    master=Image.open(SOURCE).convert('RGBA');a=np.array(master)
    # Generated alpha has a 253 opaque plateau. Restore opaque pixels without
    # touching RGB or inventing a key-colour matte. Alpha-zero RGB is discarded.
    a[:,:,3]=np.clip(a[:,:,3].astype(float)*255/253,0,255).astype('uint8')
    a[a[:,:,3]==0,:3]=0;master=Image.fromarray(a)
    mask=Image.new('L',master.size);d=ImageDraw.Draw(mask)
    d.polygon([(827,215),(848,206),(850,191),(868,190),(872,207),(989,290),(1051,290),(1068,306),(1083,336),(1087,431),(1044,446),(975,433),(925,398),(850,329),(830,305)],fill=255)
    # The hammer is fixed to the frame and must not ride with the slide.
    d.polygon([(1026,354),(1065,354),(1080,390),(1073,491),(1024,492),(1012,409)],fill=0)
    slide=master.copy();slide.putalpha(Image.fromarray(np.minimum(np.array(mask),a[:,:,3])))
    base=master.copy();base.putalpha(Image.fromarray(np.where(np.array(mask)>0,0,a[:,:,3]).astype('uint8')))
    # Source-native receiver rails and exposed barrel, only visible during cycling.
    rails=Image.new('RGBA',master.size);dr=ImageDraw.Draw(rails)
    dr.polygon([(832,242),(850,226),(1048,403),(1074,450),(975,435),(847,324)],fill=(43,46,47,255))
    dr.polygon([(846,244),(856,238),(976,350),(965,364),(853,272)],fill=(90,92,88,255))
    dr.line([(849,244),(976,355)],fill=(131,130,120,255),width=3)
    arms=Image.alpha_composite(rails,base)
    spec=[('00_BHP_READY',0,0,0),('01_BHP_FIRE',0,0,.25),('02_BHP_SLIDE_REAR',23,24,.8),
          ('03_BHP_RECOIL_MAX',25,27,1.25),('04_BHP_SLIDE_FORWARD',10,11,.6),('05_BHP_RECOVERY',0,0,.2),('06_BHP_EMPTY',25,27,0)]
    manifest=[]
    for name,dx,dy,angle in spec:
        if dx==0:img=master.copy()
        else:
            layer=Image.new('RGBA',master.size);layer.alpha_composite(slide,(dx,dy));img=Image.alpha_composite(arms,layer)
        if angle:img=img.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(1060,840))
        # Less obstructive layout. One identical canvas/scale for the entire family.
        img=img.resize((1382,922),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(1672,941));canvas.alpha_composite(img,(-200,19))
        canvas.save(OUT/(name+'.png'))
        manifest.append(dict(file=name+'.png',canvas=[1672,941],offset=[-700,-300],scale=[6,7.2],slide_travel=[dx,dy],recoil_degrees=angle))
    (HERE/'browning/animation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    # Flash drawn in projected muzzle space on its own layer: one event, no baked duplicate.
    flash=Image.new('RGBA',(1672,941)); f=np.zeros((941,1672,4),np.float32)
    yy,xx=np.mgrid[:941,:1672];x=(xx-556)/45;y=(yy-207)/24
    r=np.sqrt(x*x+y*y);theta=np.arctan2(y,x)
    flare=np.exp(-r*r*2.8)*(0.45+0.55*np.cos(theta*5+.2)**8)
    f[:,:,:3]=[255,187,81];f[:,:,3]=np.clip(flare*320,0,245)
    core=np.exp(-r*r*15);f[:,:,:3]=f[:,:,:3]*(1-core[:,:,None])+np.array([255,244,206])*core[:,:,None]
    f[f[:,:,3]<1]=0;Image.fromarray(f.astype('uint8')).save(OUT/'07_BHP_FLASH.png')
    print('Browning: 7 rigid-master frames + separate flash exported')
if __name__=='__main__':main()
