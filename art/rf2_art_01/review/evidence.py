"""Readable before/after plates from raw engine screenshots; no scene retouching."""
from pathlib import Path
import json,shutil,re,hashlib,csv
from PIL import Image,ImageDraw
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'art_pass/evidence';SHOTS=ROOT/'build/dev/shots'
def shots(name):return sorted((SHOTS/name).glob('*.png'))
def plate(rows,dest):
    w,h=640,360;canvas=Image.new('RGB',(w*2,(h+30)*len(rows)),(25,29,32));d=ImageDraw.Draw(canvas)
    for row,(before,after,label) in enumerate(rows):
        for col,p in enumerate((before,after)):
            im=Image.open(p).convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
            canvas.paste(im,(col*w,row*(h+30)+30))
            d.text((col*w+10,row*(h+30)+8),('AVANT | ' if col==0 else 'CANDIDATE | ')+label,fill='white')
    canvas.save(dest)
def main():
    OUT.mkdir(exist_ok=True,parents=True)
    a,b=shots('before_weapons_1080_v2'),shots('after_weapons_1080')
    assert len(a)==len(b)==17,(len(a),len(b))
    plate([(a[i],b[i],label) for i,label in [(0,'Browning / trois familles'),(2,'Browning / recul'),(5,'FAL / tir'),(9,'FAL / phase de recharge'),(13,'FAL / retour'),(15,'Browning / culasse ouverte')]],OUT/'comparatif_armes.png')
    for folder in ['before_weapons_1080_v2','after_weapons_1080','after_weapons_1440','after_weapons_1610']:
        dest=OUT/'raw'/folder;dest.mkdir(parents=True,exist_ok=True)
        for i,p in enumerate(shots(folder)):shutil.copy2(p,dest/f'{i:02d}.png')
    a,b=shots('before_corpses'),shots('after_corpses');assert len(a)==len(b)==120
    for family,name in enumerate(['infirmier','brancardier','porte_registre']):
        rows=[]
        for offset,label in [(4,'sol plat / hauteur normale'),(9,'sol plat / plongee'),(19,'mur'),(29,'seuil'),(39,'escalier - limite du corps rigide')]:
            i=family*40+offset;rows.append((a[i],b[i],label))
        plate(rows,OUT/f'comparatif_cadavre_{name}.png')
    dst=OUT/'raw/corpses_final';dst.mkdir(parents=True,exist_ok=True)
    for i,p in enumerate(b):shutil.copy2(p,dst/f'{i:03d}.png')
    # Isolated exports at their actual delivered level. No audition or loudness normalization.
    takes=['browning/fire_01.wav','browning/fire_02.wav','browning/fire_03.wav','fal/shot_01.wav','fal/shot_02.wav','fal/shot_03.wav','fal/action.wav','orderly/penitent_attack.wav','brancardier/brace.wav','brancardier/frame_hit.wav','porte/throw.wav','world/body_fall.wav','world/door.wav','world/door_close.wav']
    audio=[];cues=[];t=0
    for name in takes:
        x,sr=sf.read(ROOT/'src/sounds'/name);assert sr==48000
        cues.append(dict(start_seconds=round(t,3),file=name));audio.extend([x,np.zeros(48000)]);t+=len(x)/sr+1
    sf.write(OUT/'audio_isole_sans_gain.wav',np.concatenate(audio),48000,subtype='PCM_16')
    (OUT/'audio_isole_cues.json').write_text(json.dumps(cues,indent=2),encoding='utf8')
    perf={}
    for name in ['perf_before','perf_after']:
        text=(ROOT/'build/dev/logs'/(name+'.txt')).read_text(encoding='utf8')
        perf[name]=re.findall(r'RF_DEV_PERF scene=.*',text)
        assert len(perf[name])==4
    (OUT/'performance.json').write_text(json.dumps(perf,indent=2),encoding='utf8')
    cfg=ROOT/'build/dev/uzdoom.ini';shutil.copy2(cfg,OUT/'review_config.ini')
    items=['comparatif_armes.png','comparatif_cadavre_infirmier.png','comparatif_cadavre_brancardier.png','comparatif_cadavre_porte_registre.png']
    html='<!doctype html><html lang="fr"><meta charset="utf-8"><title>RF2-ART-01 — revue</title><style>body{background:#161b20;color:#ddd;font:18px system-ui;max-width:1320px;margin:32px auto}img,video{max-width:100%}a{color:#a8cdec}section{margin:40px 0}</style><h1>RF2-ART-01 — candidate</h1><p>OWNER_REVIEW_REQUIRED. Avant/après au même cadrage. Aucun filtre appliqué aux captures. Corps rigides : pénétration possible sur marches et près des murs. Mesures audio sans audition humaine.</p><p><a href="../RAPPORT.md">Rapport</a> · <a href="verification.json">Vérification</a> · <a href="performance.json">Performance</a></p>'
    for p in items:html+=f'<section><h2>{p}</h2><a href="{p}"><img src="{p}"></a></section>'
    html+='<h2>Sons isolés — gain inchangé</h2><audio controls src="audio_isole_sans_gain.wav"></audio><p><a href="audio_isole_cues.json">Repères</a></p>'
    for name,label in [('weapons_final','Cycle des deux armes'),('combat_final','Stress audio : deux vagues de cinq acteurs, trois familles, invulnérabilité de test'),('corpses_final','Chutes et vues autour des corps'),('rf01_final','Parcours réel RF01')]:
        html+=f'<section><h2>{label}</h2><video controls preload="metadata" src="films/{name}/{name}.mp4"></video><p><a href="films/{name}/film.json">Mesures et synchronisation</a></p></section>'
    html+='<p><a href="films/combat_before_fixed/combat_before_fixed.mp4">Même stress avec les sons et visuels de la base</a> — gain également inchangé ; le déroulement des combats peut varier.</p>'
    html+='<section><h2>Flash du Browning — capture du parcours RF01</h2><img src="browning_flash_frame.png"></section>'
    (OUT/'index.html').write_text(html+'</html>',encoding='utf8')
    print('Before/after plates, raw captures, audio excerpts and gallery written')
if __name__=='__main__':main()
