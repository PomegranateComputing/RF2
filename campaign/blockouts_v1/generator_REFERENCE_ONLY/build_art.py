#!/usr/bin/env python3
"""Original code-authored tile materials. Pillow only needed to rebuild PNGs.
No borrowed game graphics; native IWAD actors are used by the map test pack.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random, math, struct, zipfile
from campaign import campaign
ROOT=Path(__file__).resolve().parents[1]
def font(size,bold=False):
    paths=[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf'),Path('C:/Windows/Fonts/arial'+('bd' if bold else '')+'.ttf')]
    for p in paths:
        if p.exists():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def noise(base,seed,w=128,h=128,amp=8):
    r=random.Random(seed);im=Image.new('RGB',(w,h));pix=im.load()
    for y in range(h):
        for x in range(w):
            v=r.randrange(-amp,amp+1);pix[x,y]=tuple(max(0,min(255,c+v)) for c in base)
    return im

def make(name,color,kind,flat=False):
    seed=sum(map(ord,name));im=noise(color,seed);d=ImageDraw.Draw(im);r=random.Random(seed)
    dark=tuple(int(c*.55) for c in color);bright=tuple(min(255,int(c*1.25)+12) for c in color)
    if kind=='brick':
        for y in range(0,128,32):
            d.line((0,y,128,y),fill=dark,width=2)
            for x in range(-64,192,64):d.line((x+(32 if (y//32)%2 else 0),y,x+(32 if (y//32)%2 else 0),y+32),fill=dark,width=2)
    if kind=='stone':
        for y in (0,64,127):d.line((0,y,127,y),fill=dark,width=2)
        d.line((64,0,64,64),fill=dark,width=2);d.line((16,64,16,128),fill=dark,width=2)
    if kind in ('plaster','paint','pom'):
        d.rectangle((0,72,127,125),fill=dark);d.line((0,70,127,70),fill=bright,width=3)
        d.rectangle((0,122,127,127),fill=(34,36,36))
        for k in range(20):
            x=r.randrange(128);y=r.randrange(115);d.line((x,y,x+r.randrange(-3,4),y+r.randrange(1,9)),fill=color)
    if kind=='tile':
        for v in range(0,128,32):d.line((v,0,v,127),fill=dark);d.line((0,v,127,v),fill=dark)
    if kind=='tilewall':
        for v in range(0,128,16):d.line((v,0,v,127),fill=dark);d.line((0,v,127,v),fill=dark)
        d.rectangle((0,70,127,82),fill=(41,63,69))
    if kind in ('metal','freeze','corr','panel'):
        for x in range(0,128,32 if kind!='corr' else 16):
            d.line((x,0,x,127),fill=dark,width=2);d.line((x+2,0,x+2,127),fill=bright)
        d.line((0,4,127,4),fill=dark,width=2);d.line((0,123,127,123),fill=dark,width=3)
        for x in (5,37,69,101):
            for y in (8,119):d.ellipse((x,y,x+2,y+2),fill=(36,37,38))
        if kind=='freeze':
            for x in range(128):
                yy=r.randrange(2,16);d.line((x,0,x,yy),fill=(171,190,188))
    if kind in ('wood','crate'):
        for x in range(0,128,16):d.line((x,0,x,128),fill=dark,width=2)
        for k in range(95):
            x=r.randrange(128);y=r.randrange(128);d.line((x,y,x,y+8),fill=bright)
        if kind=='crate':
            d.rectangle((0,0,127,127),outline=dark,width=8);d.line((4,4,124,124),fill=dark,width=9)
    if kind=='box':
        for y in range(0,128,32):
            d.line((0,y,128,y),fill=dark,width=3)
            for x in range(0,128,64):
                d.line((x,y,x,y+32),fill=dark,width=2);d.rectangle((x+8,y+8,x+43,y+18),fill=(185,174,144));d.text((x+10,y+8),'117',fill=(50,47,44),font=font(8))
    if kind=='rack':
        for y in range(0,128,16):
            d.rectangle((5,y+2,122,y+14),fill=(19,26,28),outline=(72,78,77))
            for x in range(12,84,5):d.line((x,y+5,x,y+11),fill=(53,62,62))
            for x in (102,110):d.rectangle((x,y+7,x+2,y+9),fill=(76,145,135))
    if kind=='ceil':
        d.rectangle((0,0,127,127),outline=dark,width=2);d.rectangle((20,49,108,79),fill=(57,67,68));d.rectangle((24,54,104,74),fill=(198,201,177))
    if kind=='carpet':
        for y in range(0,128,16):
            for x in range(0,128,16):d.polygon([(x+8,y+2),(x+14,y+8),(x+8,y+14),(x+2,y+8)],outline=bright)
    if kind=='road':
        d.rectangle((57,0,64,35),fill=(151,143,108));d.rectangle((57,75,64,116),fill=(151,143,108))
    if kind=='door':
        d.rectangle((0,0,127,127),outline=(30,45,53),width=6)
        d.rectangle((8,8,119,80),outline=bright,width=2)
        d.rectangle((8,91,119,111),fill=(29,53,70));d.text((25,93),'BADGE BLEU',fill=(179,205,212),font=font(10,True))
        d.rectangle((94,72,111,79),fill=(166,166,150))
    out=ROOT/'resources'/('flats' if flat else 'textures')/(name+'.png');im.save(out)

def main():
    specs=[('RFPLAST',(153,148,125),'plaster'),('RFBRICK',(104,76,61),'brick'),('RFCONC',(112,107,101),'stone'),('RFSTONE',(164,153,126),'stone'),('RFPAINT',(121,60,51),'paint'),('RFPOM',(108,36,39),'pom'),('RFMETAL',(63,75,77),'metal'),('RFTILEW',(139,155,147),'tilewall'),('RFFREEZ',(134,163,166),'freeze'),('RFCORR',(80,89,84),'corr'),('RFPANEL',(56,70,75),'panel'),('RFCRATE',(102,83,52),'crate'),('RFBOX',(131,113,79),'box'),('RFRACK',(41,47,49),'rack'),('RFDOORB',(52,91,116),'door')]
    for n,c,k in specs:make(n,c,k)
    flats=[('RFTILE',(132,133,114),'tile'),('RFROAD',(65,66,61),'road'),('RFGRIT',(105,99,84),'grit'),('RFWOOD',(90,71,49),'wood'),('RFCARPT',(75,45,44),'carpet'),('RFPOOL',(87,127,133),'tile'),('RFCEIL',(112,119,112),'ceil'),('RFCONCF',(103,104,95),'stone'),('RFLINO',(84,100,96),'tile'),('RFPOMF',(108,36,39),'tile'),('RFMETOP',(63,75,77),'metal'),('RFDOORF',(52,91,116),'metal')]
    for n,c,k in flats:make(n,c,k,True)
    # 64-unit switch panel: no stock switch texture dependency.
    for name,bg,label,fg in [('RFEXIT',(38,61,62),'SORTIE',(195,220,184)),('RFERR',(112,107,101),'ERREUR',(102,28,32))]:
        im=noise(bg,117,64,128);d=ImageDraw.Draw(im);d.rectangle((3,20,60,100),outline=fg,width=2);d.text((7,30),label,font=font(10,True),fill=fg)
        if name=='RFEXIT':
            d.polygon([(17,59),(36,59),(36,50),(51,66),(36,82),(36,73),(17,73)],fill=fg);d.text((9,91),'UTILISER',font=font(8),fill=fg)
        else:
            d.ellipse((17,52,46,90),outline=fg,width=3);d.line((15,91,49,50),fill=fg,width=3)
        im.save(ROOT/'resources/textures'/f'{name}.png')
    # Seamless horizon gradient for sky. Deliberately abstract prototype backdrop.
    im=Image.new('RGB',(1024,256));d=ImageDraw.Draw(im)
    for y in range(256):
        f=y/255;c=tuple(int(a+(b-a)*f) for a,b in zip((48,65,77),(161,163,148)));d.line((0,y,1023,y),fill=c)
    im.save(ROOT/'resources/textures/RFSKY.png')
    # UI is code-native typography, not a painted illustration.
    for name,end in [('TITLEPIC',False),('RFEND',True)]:
        im=Image.new('RGB',(960,600),(21,28,31));d=ImageDraw.Draw(im)
        for y in range(0,600,6):d.line((0,y,960,y),fill=(23,30,33))
        d.rectangle((62,65,898,534),outline=(106,116,113),width=2)
        d.rectangle((62,65,74,534),fill=(108,36,39))
        d.text((108,100),'POMEGRANATE INTERACTIVE',font=font(20),fill=(154,169,169))
        d.text((106,191),'RED FLAGS 2' if not end else 'DESTINATAIRE PRESENT',font=font(50 if not end else 37,True),fill=(227,218,199))
        d.text((109,272),'LA COULEUR DE LA GRENADE',font=font(27),fill=(194,177,150))
        d.line((110,332,839,332),fill=(108,36,39),width=6)
        d.text((109,366),'23 CARTES / PASSE DE CONSTRUCTION 01' if not end else 'FIN DU PARCOURS / LES DOSSIERS RESTENT OUVERTS',font=font(19),fill=(168,181,176))
        d.text((109,451),'PARIS 1940 / MALTE / WAUKEGAN / GENNEVILLIERS',font=font(16),fill=(119,140,144))
        out=ROOT/'resources/graphics';out.mkdir(exist_ok=True);im.save(out/f'{name}.png')
    mi=['clearepisodes','episode RF01 { name = "La Couleur de la Grenade" key = "g" }', 'gameinfo { TitlePage = "TITLEPIC" TitleTime = 3600 PageTime = 3600 }']
    for spec in campaign():
        i=spec['number'];nxt=f'"RF{i+1:02d}"' if i<23 else 'endgame { pic = "RFEND" music = "$MUSIC_READ_M" }'
        mi.append(f'''map {spec['code']} "{spec['title']}"
{{
 levelnum = {i}
 next = {nxt}
 sky1 = "RFSKY", 0
 music = "$MUSIC_RUNNIN"
 cluster = 117
 nojump
 nocrouch
 allowfreelook
}}''')
    (ROOT/'resources/MAPINFO').write_text('\n\n'.join(mi)+'\n',encoding='ascii')
    (ROOT/'resources/GAMEINFO').unlink(missing_ok=True)
    print('Original materials + campaign metadata built.')

if __name__=='__main__':main()
