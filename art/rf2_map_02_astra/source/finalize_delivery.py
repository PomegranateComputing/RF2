"""Build offline review and verifiable asset-only handoff. No game mutations."""
from pathlib import Path
import json,hashlib,shutil,zipfile,html,struct,math,importlib.metadata as md
from PIL import Image
import soundfile as sf
import numpy as np
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ELVIS=LOT.parent/'RF2_ELVIS_01'
BASE=Path('C:/PROJECTS/RF2_UZDOOM')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jwrite(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def grab(p):
    b=p.read_bytes();i=8
    while i<len(b):
        n=struct.unpack('>I',b[i:i+4])[0]
        if b[i+4:i+8]==b'grAb':return list(struct.unpack('>ii',b[i+8:i+16]))
        i+=n+12
    return None
def main():
    refs=HERE/'references';refs.mkdir(exist_ok=True)
    for n in ('RF2_FAC1','RF2_FAC2','RF2_FAC3','RF2_FACU','RF2_TSFS','RF2_AMIG'):
        shutil.copy2(BASE/f'src/patches/rf02/{n}.png',refs/f'{n}.png')
    for n in ('TEXTURES.rf02','zscript/rf/paris.zs'):
        dst=HERE/'contract'/Path(n).name;shutil.copy2(BASE/'src'/n,dst)
    versions={name:md.version(name) for name in ('Pillow','numpy','scipy','soundfile')}
    (HERE/'requirements-lock.txt').write_text('\n'.join(f'{k}=={v}' for k,v in versions.items())+'\n',encoding='utf8')
    jwrite(HERE/'tool_versions.json',{'python':'3.12','blender':'5.2.2 LTS d13f752e3b9c','image_generation':'built-in image_gen; no CLI fallback','python_libraries':versions})
    jobs=[('MATERIAL_ATLAS.txt','RF2_MATERIAL_ATLAS.png',[],True),('FAC1.txt','RF2_FAC1.png',['source/references/RF2_FAC1.png'],True),('FAC2.txt','RF2_FAC2.png',['source/references/RF2_FAC2.png','source/masters/RF2_FAC1.png'],True),('FAC3_DRAFT.txt','RF2_FAC3_DRAFT.png',['source/references/RF2_FAC3.png','source/masters/RF2_FAC1.png'],False),('FACU.txt','RF2_FACU.png',['source/references/RF2_FACU.png','source/masters/RF2_FAC1.png'],True),('FAC3_CORRECTION.txt','RF2_FAC3.png',['source/masters/RF2_FAC3_DRAFT.png'],True),('TSFS.txt','RF2_TSFS.png',['source/references/RF2_TSFS.png'],True),('AMIG.txt','RF2_AMIG.png',['source/masters/RF2_TSFS.png'],True)]
    jwrite(HERE/'IMAGEGEN_PROVENANCE.json',{'tool':'built-in image_gen','jobs':[{'prompt':'source/prompts/'+p,'output':'source/masters/'+o,'output_sha256':sha(HERE/'masters'/o),'references':r,'retained_for_export':ok} for p,o,r,ok in jobs]})
    models=[]
    for p in sorted((HERE/'models').glob('*.obj')):
        vertices=[];faces=0;vt=0
        for line in p.read_text().splitlines():
            a=line.split()
            if not a:continue
            if a[0]=='v':x,y,z=map(float,a[1:4]);vertices.append((x,-z,y))
            elif a[0]=='vt':vt+=1
            elif a[0]=='f':
                faces+=1
                for k in a[1:]:
                    ids=k.split('/');assert 1<=int(ids[0])<=len(vertices);assert 1<=int(ids[1])<=vt
        assert vertices and faces
        arr=np.array(vertices);lo=arr.min(0);hi=arr.max(0)
        models.append({'name':p.stem,'obj':p.relative_to(LOT).as_posix(),'sha256':sha(p),'glb':p.with_suffix('.glb').relative_to(LOT).as_posix(),'vertices':len(vertices),'triangles':faces,'bounds_min_xyz_up_z':lo.tolist(),'bounds_max_xyz_up_z':hi.tolist(),'overall_dimensions':(hi-lo).tolist(),'origin':[0,0,0],'units':'proposed game units','runtime_verified':p.stem=='pram','status':'SOURCE_ONLY' if p.stem!='pram' else 'ISOLATED_ENGINE_REVIEW','notes':'OBJ color-only materials not fully represented by single atlas; GLB/BLEND preserve complete materials. Source suitcase shoe forms rejected for runtime.' if p.stem not in ('pram','tram','track_straight') else 'Single-atlas source; game placement/collision remains with Opus.'})
    jwrite(HERE/'models'/'asset_catalogue.json',models)
    contract=HERE/'models/tram_contract_proposal.json'
    tr=json.loads(contract.read_text());tr['nominal_body_dimensions']=tr.pop('body_dimensions',tr.get('nominal_body_dimensions'))
    actual=next(m for m in models if m['name']=='tram');tr['overall_bounds_from_obj']={k:actual[k] for k in ('bounds_min_xyz_up_z','bounds_max_xyz_up_z','overall_dimensions')};jwrite(contract,tr)
    # The Elvis source has no fictional runtime path: custom source manifest is deliberately separate.
    portrait=ELVIS/'source/RF2_ELVIS_MASTER.png';im=Image.open(portrait)
    jwrite(ELVIS/'manifest.json',{'batch_id':'RF2_ELVIS_01','status':'OWNER_REVIEW_REQUIRED','scope':'Source portrait master and canon preparation, no runtime actor','owner_consent':{'date':'2026-09-27','source':'current user message','quote':'GO. ELVIS, ACCORD OK. PHOTO D’ELVIS CI JOINTE.','artistic_approval_of_new_master':False},'files':[],'source_assets':[{'file':'source/RF2_ELVIS_MASTER.png','sha256':sha(portrait),'bytes':portrait.stat().st_size,'width':im.width,'height':im.height,'prompt':'source/prompts/ELVIS_MASTER.txt','method':'built-in image_gen using user-attached photo','reference_file_hash':None,'reference_limitation':'Original attachment pixels not recovered as local file; no fabricated hash','runtime_ready':False}]})
    # Validate delivered runtime files and original counterpart dimensions/offsets.
    man=json.loads((LOT/'manifest.json').read_text());checks=[]
    for r in man['files']:
        p=LOT/r['file'];b=BASE/'src'/r['target_relpath'];im=Image.open(p)
        assert sha(p)==r['sha256'] and sha(b)==r['base_sha256']
        assert list(im.size)==[r['width'],r['height']]==list(Image.open(b).size)
        assert grab(p)==grab(b)
        checks.append({'file':r['file'],'hash_dimensions_grAb_match':True})
    aud=json.loads((LOT/'audio_proposal/manifest.json').read_text())
    for r in aud['files']:
        p=LOT/r['file'];info=sf.info(p);x,sr=sf.read(p)
        assert sha(p)==r['sha256'] and info.subtype=='PCM_24' and sr==48000 and info.channels==1
        assert np.isfinite(x).all() and abs(x).max()<1 and abs(x[0])<.0001 and abs(x[-1])<.0001
    validation={'runtime_files':checks,'audio_files':len(aud['files']),'audio_audition':'NOT_PERFORMED','obj_sources_valid':len(models),'owner_approval':False,'scope_complete':False,'missing_corrections_pack':True}
    jwrite(LOT/'evidence/validation.json',validation)
    style='''body{margin:0;background:#181919;color:#eee9df;font:16px/1.55 system-ui}main{max-width:1240px;margin:auto;padding:38px 24px}h1{font-size:42px;line-height:1.1}h2{margin-top:50px;font-size:26px}a{color:#dbb785}small,.muted{color:#bbb6af}.tag{border:1px solid #88654b;padding:5px 12px;display:inline-block}select,button{font:inherit;background:#343534;color:inherit;border:1px solid #777;padding:8px}img{max-width:100%;height:auto;background:#2c2e2e}input[type=range]{width:100%}.compare{position:relative}.compare img{display:block;width:100%}.compare #after{position:absolute;inset:0;clip-path:inset(0 50% 0 0)}.row{display:flex;gap:20px;flex-wrap:wrap;align-items:center}.row>*{flex:1;min-width:240px}figure{margin:20px 0}figcaption{color:#c0b8ad}.notice{border-left:3px solid #96624c;padding:12px 22px;background:#242424}audio{width:100%}code{color:#ddb790}nav{display:flex;gap:18px;flex-wrap:wrap}table{border-collapse:collapse;width:100%}td,th{padding:8px;text-align:left;border-bottom:1px solid #555}'''
    scenes=['Boulevard Arago','Seau','Façade sud','Tram existant','Sacoche','Reflet Amiga','Retour aux radios','Radio du comptoir','Téléphone','Rue et façades']
    model_names=['pram','bucket','satchel','radio_off','radio_on','phone','suitcase','mattress','amiga','tram']
    page=f'<!doctype html><html lang="fr"><meta charset="utf-8"><title>RF02 — Reprise Astra 01</title><style>{style}</style><main><small>POMEGRANATE INTERACTIVE · RF2 · 27 SEPTEMBRE 2026</small><h1>RF02 — reprise artistique</h1><span class="tag">LOT PARTIEL · OWNER_REVIEW_REQUIRED</span><p>Façades, vitrine et objets. Sources 3D, propositions de son et master Elvis. Les captures ci-dessous viennent d’UZDoom ; les rendus de masters sont identifiés séparément.</p><nav><a href="../POUR_OPUS.md">Passation Opus</a><a href="../README.md">Périmètre et limites</a><a href="../DEMANDE_CONTRATS_OPUS.md">Contrats manquants</a><a href="../../RF2_ELVIS_01/evidence/index.html">Elvis</a><a href="../SOURCES.md">Sources et crédits</a></nav><div class="notice"><strong>RF02 n’est pas terminé.</strong> Figures, pied-de-biche visuel, scènes et entrée Luna restent à produire/raccorder. Le dossier de corrections et ses dix captures sont manquants. Aucun asset nouveau n’est déclaré approuvé.</div><h2>Comparaison dans le moteur</h2><div class="row"><label>Scène <select id="scene">'+''.join(f'<option value="{i:02}">{html.escape(s)}</option>' for i,s in enumerate(scenes))+'</select></label><label>Candidate <select id="variant"><option value="hd">HD — proposition avec échelles compensées</option><option value="candidate">Compatibilité — tailles historiques</option></select></label></div><p class="muted">Gauche : candidate. Droite : référence Opus. Caméra et éclairage identiques. La HD exige le patch séparé de présentation.</p><div class="compare"><img id="before" src="engine/baseline/00.png" alt="Référence Opus"><img id="after" src="engine/hd/00.png" alt="Candidate Astra"></div><input id="wipe" type="range" value="50" min="0" max="100" aria-label="Partage avant après"><h2>Poussette 3D — contrôle réel UZDoom</h2><p>Quatre côtés et plongée à un emplacement d’essai. Le bloc de la carte et les collisions ne sont pas remplacés. Ancrage de test z=0,15 u pour poser le bord des roues à zéro.</p><img id="pram" src="engine/pram/00.png" alt="Poussette en jeu"><input id="pramview" type="range" min="0" max="4" value="0" step="1" aria-label="Vue moteur poussette"><h2>Masters contournables — rendus Blender</h2><p>Chaque rotation provient de la même géométrie. La valise reste hors runtime à cause des chaussures. Tram : cage vide, vieil homme absent ; son contrat expose le raccord aux rails et collisions.</p><select id="model">'+''.join(f'<option>{s}</option>' for s in model_names)+'</select><figure><img id="modelpic" src="../source/renders/pram/view_000.png" alt="Rendu de master Blender"><figcaption id="angle">Azimut source 0° — pas une capture du jeu</figcaption></figure><input id="rotation" type="range" min="0" max="7" value="0" step="1" aria-label="Rotation du master"><div class="row"><figure><img src="../source/renders/tram/interior.png"><figcaption>Intérieur du tram, douze valises. Rendu source.</figcaption></figure><figure><img src="../source/renders/track_straight.png"><figcaption>Voie assortie. Rendu source ; raccord carte à faire.</figcaption></figure></div><h2>Audio — produit, pas écouté par l’agent</h2><p>19 propositions, PCM24 mono 48 kHz. Sources créditées et empreintes archivées ; aucun son du jeu actif remplacé. Les niveaux ont été mesurés, sans audition ni validation du mix.</p><select id="sound">'+''.join(f'<option value="../{r["file"]}">{Path(r["file"]).stem}</option>' for r in aud['files'])+'</select><p><audio id="player" controls preload="none" src="../'+aud['files'][0]['file']+'"></audio></p><h2>Preuves et remise</h2><p><a href="engine_validation.json">Comparaison des paquets</a> · <a href="presentation_validation.json">Revue HD et poussette</a> · <a href="validation.json">Contrôles d’exports</a> · <a href="../presentation_proposal/presentation.diff">Patch de présentation</a> · <a href="../delivery/RF2_REPRISE_20260927_01.zip">Archive sources / assets / preuves</a></p><p class="muted">Pas de parcours complet ni d’acceptation propriétaire déduits de ces vues. Elvis : <a href="../../RF2_ELVIS_01/SCENES_ELVIS.md">scènes sourcées</a>.</p></main><script>const $=id=>document.getElementById(id);function compare(){$("before").src="engine/baseline/"+$("scene").value+".png";$("after").src="engine/"+$("variant").value+"/"+$("scene").value+".png";}$("scene").onchange=compare;$("variant").onchange=compare;$("wipe").oninput=()=>$("after").style.clipPath="inset(0 "+(100-$("wipe").value)+"% 0 0)";$("pramview").oninput=()=>$("pram").src="engine/pram/0"+$("pramview").value+".png";function turn(){const a=Number($("rotation").value)*45;$("modelpic").src="../source/renders/"+$("model").value+"/view_"+String(a).padStart(3,"0")+".png";$("angle").textContent="Azimut source "+a+"° — pas une capture du jeu";}$("rotation").oninput=turn;$("model").onchange=turn;$("sound").onchange=()=>{$("player").src=$("sound").value;$("player").load();};</script></html>'
    (LOT/'evidence/index.html').write_text(page,encoding='utf8')
    (ELVIS/'evidence/index.html').write_text(f'<!doctype html><html lang="fr"><meta charset="utf-8"><title>Elvis — master source</title><style>{style}</style><main><small>RF2 · ELVIS · MASTER SOURCE</small><h1>Elvis — proposition de personnage</h1><p class="tag">Accord déclaré par le propriétaire · nouveau visuel à examiner</p><p>Photo fournie dans la conversation, bonnet sombre et lampe au cou issus du roman. Tenue du corps : proposition d’adaptation. Aucun acteur animé ou jeu de rotations livré.</p><nav><a href="../README.md">Provenance</a><a href="../SCENES_ELVIS.md">Scènes sourcées</a><a href="../source/prompts/ELVIS_MASTER.txt">Prompt exact</a><a href="../../RF2_MAP_02/evidence/index.html">Reprise RF02</a></nav><img src="../source/RF2_ELVIS_MASTER.png" alt="Master en pied d’Elvis" style="max-height:1000px;margin-top:30px"><p class="muted">Un frontal ne prouve pas les profils ni le dos. Aucune voix produite, aucune acceptation artistique inventée.</p></main></html>',encoding='utf8')
    # Capture files and sources only; no PK3, WAD, personal settings, Blender backup or caches.
    def included(root):
        for p in sorted(root.rglob('*')):
            if p.is_file() and not any(x in ('review','delivery','__pycache__') for x in p.relative_to(root).parts) and p.suffix not in ('.pyc','.blend1','.log') and p.name!='SHA256SUMS.txt':yield p
    for root in (LOT,ELVIS):
        (root/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+p.relative_to(root).as_posix() for p in included(root))+'\n',encoding='utf8')
    delivery=LOT/'delivery';delivery.mkdir(exist_ok=True);archive=delivery/'RF2_REPRISE_20260927_01.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for root in (LOT,ELVIS):
            for p in [*included(root),root/'SHA256SUMS.txt']:z.write(p,root.name+'/'+p.relative_to(root).as_posix())
    jwrite(delivery/'archive.json',{'file':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'contents':'Assets, source, proposals, evidence; no executable game package or private configuration','batches':['RF2_MAP_02','RF2_ELVIS_01']})
    print('Finalized:',archive,'bytes',archive.stat().st_size,flush=True)
if __name__=='__main__':main()
