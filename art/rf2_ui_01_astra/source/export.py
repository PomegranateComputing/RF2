"""RF2-UI-01: fixed generated painting + native vector UI + recorded CC0 cues."""
from pathlib import Path
import json, hashlib, math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent;LOT=HERE.parent;OUT=LOT/'runtime'

def fonts():
    chars=''.join(chr(c) for c in range(0x21,0x7f))+'ÀÂÄÇÈÉÊËÎÏÔÖÙÛÜŸàâäçèéêëîïôöùûüÿŒœ«»°’–—…'
    for name,size,weight,tracking in [('rfuititle',23,650,.065),('rfuimenu',12,500,.025)]:
        dst=HERE/'style_study/fonts'/name;dst.mkdir(parents=True,exist_ok=True)
        f=ImageFont.truetype(str(HERE/'Inter.woff2'),size*4);f.set_variation_by_axes([32,weight])
        pad=round(size*4*tracking);stroke=2;asc,desc=f.getmetrics();height=asc+desc+stroke*2
        for ch in chars:
            im=Image.new('RGBA',(round(f.getlength(ch))+pad+stroke*2,height),(255,255,255,0))
            ImageDraw.Draw(im).text((stroke+pad/2,stroke),ch,font=f,fill=(255,255,255,255),stroke_width=stroke,stroke_fill=(15,17,18,220))
            im.save(dst/f'{ord(ch):04X}.png')
        (dst/'font.inf').write_text(f'// Inter OFL 1.1, RF2 UI derivative, weight {weight}\nScale 4\nFontHeight {round(height/4)}\nSpaceWidth {round((f.getlength(" ")+pad)/4)}\nKerning -1\n',encoding='utf8')
    license_dir=HERE/'style_study/licenses';license_dir.mkdir(exist_ok=True)
    (license_dir/'RF2_UI_Inter_OFL.txt').write_bytes((HERE/'Inter-OFL.txt').read_bytes())

def graphics():
    dst=HERE/'style_study/graphics';dst.mkdir(parents=True,exist_ok=True)
    # Aspect-preserving export; source aspect differs by < 0.1% from 16:9.
    im=Image.open(HERE/'title_master.png').convert('RGB')
    w,h=im.size;crop_h=round(w*9/16)
    im=im.crop((0,(h-crop_h)//2,w,(h+crop_h)//2)).resize((1920,1080),Image.Resampling.LANCZOS)
    title=OUT/'graphics/ui/RFMENUBG.png';title.parent.mkdir(parents=True,exist_ok=True);im.save(title)
    (OUT/'graphics/TITLEPIC.png').write_bytes(title.read_bytes())
    # Simple geometric controls have editable SVG sources, never generated lettering.
    colors={'normal':'#8e9291','focus':'#b75b60','pressed':'#e0dacf','disabled':'#515655'}
    for state,c in colors.items():
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="64" viewBox="0 0 720 64"><path d="M2 8V56H10V8Z" fill="{c}"/><path d="M24 62H718" stroke="{c}" stroke-opacity="0.35"/></svg>\n'
        (HERE/f'row_{state}.svg').write_text(svg,encoding='utf8')
        im=Image.new('RGBA',(720,64));d=ImageDraw.Draw(im);d.rectangle((2,8,10,56),fill=c);d.line((24,62,718,62),fill=c,width=1)
        im.save(dst/f'RF2_UI_ROW_{state.upper()}.png')
    im=Image.new('RGBA',(12,12));d=ImageDraw.Draw(im)
    d.rectangle((2,1,4,10),fill='#b75b60');d.line((5,1,9,1),fill='#e0dacf');d.line((5,10,9,10),fill='#e0dacf')
    im.save(dst/'RFSELCT.png')
    im=Image.new('RGBA',(640,400));d=ImageDraw.Draw(im)
    d.rectangle((0,0,639,399),fill=(20,23,24,242));d.line((32,36,608,36),fill='#737976',width=1)
    d.rectangle((32,32,38,38),fill='#8c343c');d.line((32,368,608,368),fill='#494e4c')
    im.save(dst/'RF2_UI_SHEET.png')

def audio():
    dst=OUT/'sounds/ui';dst.mkdir(parents=True,exist_ok=True);masters=HERE/'audio/masters';masters.mkdir(exist_ok=True)
    cues=[('cursor','bookFlip3.ogg',.075,-27),('choose','metalLatch.ogg',.14,-20),
          ('change','metalClick.ogg',.065,-27),('backup','bookPlace2.ogg',.17,-24),
          ('clear','cloth2.ogg',.20,-26),('invalid','beltHandle2.ogg',.11,-24),
          ('prompt','bookOpen.ogg',.22,-23),('dismiss','bookFlip2.ogg',.11,-27)]
    report=[]
    for name,source,duration,db in cues:
        original,sr=sf.read(HERE/'audio'/source,always_2d=True);x=original.mean(axis=1)
        if sr!=48000:
            divisor=math.gcd(sr,48000);x=resample_poly(x,48000//divisor,sr//divisor)
        active=np.where(np.abs(x)>max(np.max(np.abs(x))*.02,.0001))[0]
        if len(active):x=x[max(0,active[0]-96):]
        x=x[:round(duration*48000)].copy();x-=x.mean()
        attack=min(96,len(x)//4);release=min(960,len(x)//3)
        x[:attack]*=np.linspace(0,1,attack);x[-release:]*=np.linspace(1,0,release)
        x*=10**(db/20)/max(np.max(np.abs(x)),1e-9)
        sf.write(masters/f'{name}.wav',x,48000,subtype='PCM_24');sf.write(dst/f'{name}.wav',x,48000,subtype='PCM_16')
        event='menu/'+name
        if name=='choose':event+=' + menu/advance'
        if name=='backup':event+=' + menu/activate'
        report.append(dict(event=event,source=source,seconds=len(x)/48000,peak_dbfs=db,rms_dbfs=float(20*np.log10(np.sqrt(np.mean(x*x))+1e-12)),audition=False,origin='Kenney RPG Audio, CC0'))
    (LOT/'evidence/audio_metrics.json').write_text(json.dumps(report,indent=2),encoding='utf8')

if __name__=='__main__':
    graphics();fonts();audio();print('Exported two title targets, eight recorded UI cues, and optional style study.')
