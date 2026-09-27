from pathlib import Path
import json,shutil,html,re,struct
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2];OUT=LOT/'evidence'
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)

def shots(name):return sorted((LOT/'review/engine/shots'/name).glob('*.png'),key=lambda p:p.stat().st_mtime_ns)
def plate(a,b,label,dst):
    out=Image.new('RGB',(1920,580),(20,23,24));d=ImageDraw.Draw(out)
    for k,p in enumerate([a,b]):
        im=Image.open(p).convert('RGB');out.paste(im.resize((960,540),Image.Resampling.LANCZOS),(k*960,40))
        d.text((k*960+20,10),('REFERENCE ACCEPTEE | ' if k==0 else 'CANDIDATE | ')+label,font=FONT,fill='#e8e4da')
    out.save(dst)

def main():
    a,b=shots('baseline_lineup'),shots('candidate_lineup');assert len(a)==len(b)==17
    plate(a[0],b[0],'meme camera / meme lumiere',OUT/'01_alignement.png')
    ca,cb=shots('baseline_corpses'),shots('candidate_corpses');assert len(ca)==len(cb)==210
    gallery=[('01_alignement.png','Trois familles dans RF01')]
    for f,family in enumerate(['orderly','brancardier','porte_registre']):
        for offset,label in [(4,'sol plat'),(9,'plongee'),(39,'escalier'),(69,'perron')]:
            i=f*70+offset;name=f'corpse_{family}_{offset}.png'
            plate(ca[i],cb[i],family+' / '+label,OUT/name);gallery.append((name,family+' : '+label))
    # Same skeletal attachment and canvas across all views; deterministic export proof.
    for family,prefix,states in [('orderly','ORDY','ABCDEFGHIJKLM'),('brancardier','BRCD','ABCDEFGNOHIJKLM'),('porte_registre','PREG','ABCDEFGNHIJK')]:
        canvas=Image.new('RGB',(8*250,470),(38,41,42));d=ImageDraw.Draw(canvas)
        for r in range(1,9):
            im=Image.open(LOT/f'runtime/sprites/enemies/{prefix}A{r}.png').convert('RGBA')
            im.thumbnail((240,410),Image.Resampling.LANCZOS);canvas.paste(im,((r-1)*250+(250-im.width)//2,430-im.height),im)
            d.text(((r-1)*250+12,445),f'{prefix} A{r}',font=FONT,fill='white')
        canvas.save(OUT/f'{family}_rotations.png');gallery.append((f'{family}_rotations.png',family+' : huit rotations exportees'))
        ims=[]
        for ch in states:
            p=LOT/f'runtime/sprites/enemies/{prefix}{ch}1.png';im=Image.open(p).convert('RGBA')
            raw=p.read_bytes();k=raw.index(b'grAb');ox,oy=struct.unpack('>ii',raw[k+4:k+12])
            fr=Image.new('RGBA',(800,500),(38,41,42,255));fr.alpha_composite(im,(400-ox,440-oy))
            ImageDraw.Draw(fr).text((18,15),f'{prefix} {ch}1 | export, pas capture moteur',font=FONT,fill='white');ims.append(fr.convert('RGB'))
        ims[0].save(OUT/f'{family}_states.webp',save_all=True,append_images=ims[1:],duration=180,loop=0,lossless=True)
        gallery.append((f'{family}_states.webp',family+' : poses de controle (cadence de revue, pas timings moteur)'))
    for name in ['baseline_corpses','candidate_corpses','candidate_lineup','baseline_lineup','candidate_combat_film']:
        p=LOT/'review/engine/logs'/f'{name}.txt'
        if p.exists():shutil.copy2(p,OUT/p.name)
    before=(OUT/'baseline_corpses.txt').read_text(encoding='utf8');after=(OUT/'candidate_corpses.txt').read_text(encoding='utf8')
    x=re.findall(r'^RF_DEV_CORPSE class=.*$',before,re.M);y=re.findall(r'^RF_DEV_CORPSE class=.*$',after,re.M)
    assert len(x)==len(y)==21 and x==y,'Corpse positions differ from base'
    (OUT/'corpse_comparison.json').write_text(json.dumps({'placements':21,'telemetry_exactly_equal':True,'classes':3,'spots_per_class':7,'note':'Exact comparison of actor position, floor, size, frame, velocity, angle, pitch, roll; screenshots require visual review.'},indent=2),encoding='utf8')
    h='<!doctype html><html lang="fr"><meta charset="utf-8"><title>RF2-ART-02 — revue</title><style>body{background:#141719;color:#e8e4da;font:18px system-ui;max-width:1400px;margin:40px auto;padding:0 24px}img,video{width:100%}a{color:#d5a2a5}section{margin:48px 0}p{line-height:1.6}</style><h1>RF2-ART-02 — candidate</h1><p>Retouche de matières sur les rigs acceptés. Même silhouette alpha, dimensions, grAb, animations, gameplay et géométrie des corps. Avant/après dans RF01, réglages identiques. Aucune approbation propriétaire.</p><p><a href="../README.md">Livraison</a> · <a href="validation.json">Contrôles des 320 sprites</a> · <a href="corpse_comparison.json">21 placements des corps</a></p><h2>Combat réel RF01 — clip muet</h2><video controls preload="metadata" src="combat_RF01.mp4"></video><p>Scène de contrôle existante, trois familles, invulnérabilité ; aucun parcours de campagne revendiqué.</p>'
    for file,label in gallery:h+=f'<section><h2>{html.escape(label)}</h2><a href="{file}"><img src="{file}"></a></section>'
    (OUT/'index.html').write_text(h+'</html>',encoding='utf8')
    print('Comparison gallery, rotation/state sheets and exact corpse telemetry comparison complete.')

if __name__=='__main__':main()
