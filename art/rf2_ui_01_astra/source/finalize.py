from pathlib import Path
import hashlib,json,shutil,html,wave
from PIL import Image
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    files=[]
    for p in sorted((LOT/'runtime').rglob('*')):
        if not p.is_file():continue
        target=p.relative_to(LOT/'runtime').as_posix();base=ROOT/'src'/target
        snapshot=json.loads((LOT/'evidence/opus_snapshot.json').read_text(encoding='utf8'))
        base_hash=snapshot['base_src_hashes'].get(target)
        entry=dict(file=p.relative_to(LOT).as_posix(),target_relpath=target,action='replace' if base_hash else 'add',sha256=sha(p),bytes=p.stat().st_size,
            base_sha256=base_hash,confidence='candidate; owner review required')
        if p.suffix=='.png':
            im=Image.open(p);im.verify();im=Image.open(p)
            entry.update(kind='menu_background',width=im.width,height=im.height,source='source/title_master.png',source_method='Frozen image_gen master from RF01 reference, proportional export',license_or_origin='Project screenshot + image_gen; Nameless / Pomegranate Interactive',consumer='RFUI.TitleImage()',notes='Current Opus asset path RFMENUBG; no text in image. No menu code patch.')
        else:
            with wave.open(str(p)) as w:entry.update(sample_rate=w.getframerate(),channels=w.getnchannels(),bits=w.getsampwidth()*8,duration=w.getnframes()/w.getframerate())
            entry.update(kind='ui_sound',source='source/audio/',source_method='Recorded CC0 material cue trimmed, fades, calibrated peak',license_or_origin='Kenney RPG Audio, CC0; source/audio/Kenney_RPG.txt',notes='Existing Opus SNDINFO routing unchanged; agent audition not performed.')
        files.append(entry)
    assert len(files)==10
    (LOT/'manifest.json').write_text(json.dumps({'schema':1,'batch_id':'RF2-UI-01','status':'OWNER_REVIEW_REQUIRED','canon_coverage':[],'canon_register':'../RF2_CANON_01/catalogue.json','historical_base_commit':'5b53d9eaaaf088f49ae98f667fc1d575779dc74e','integration_base_head':snapshot['head'],'integration_base_worktree':'evidence/opus_snapshot.json contains the actual source hashes, including uncommitted files','integration_note':'Ten runtime replacements matching source/contract/CONTRAT.md. No runtime code or SNDINFO patch. Historical source/style_study and patches/RF2_UI_01.patch are not for import.','files':files},indent=2),encoding='utf8')
    gallery=[]
    for folder,names in [('opus_engine/shots/opus_title',['Titre — sources Opus photographiées','Difficulté','Chargement','Options','Crédits','Confirmation de sortie']),('opus_engine/shots/opus_pause',['Début RF01','HUD inchangé','Pause','Sauvegarde','Confirmation de retour au titre']),('engine/shots/ui_pages',['Début RF01 — étude','HUD — étude','Pause — étude','Options — étude','Chargement — étude historique','Sauvegarde — étude historique'])]:
        shots=sorted((LOT/'review'/folder).glob('*.png'),key=lambda p:p.stat().st_mtime_ns)
        assert len(shots)==len(names),(folder,len(shots))
        for i,(p,label) in enumerate(zip(shots,names)):
            if i<2 and 'pause' in folder or i<4 and 'ui_pages' in folder:continue
            stem=folder.split('/')[-1]+f'_{i:02d}.png';dst=LOT/'evidence'/stem;shutil.copy2(p,dst)
            gallery.append((stem,label))
    h='<!doctype html><html lang="fr"><meta charset="utf-8"><title>RF2-UI-01 — revue</title><style>body{background:#131617;color:#e8e4da;font:18px system-ui;max-width:1300px;margin:40px auto;padding:0 24px}img{width:100%;height:auto}a{color:#d5a2a5}section{margin:48px 0}p{line-height:1.55}</style><h1>RF2-UI-01 — candidate</h1><p>Fond et sons seulement pour les menus Opus actuels. Les captures Opus proviennent d’une copie identifiée de sources en cours, pas d’un build approuvé. Aucune audition ni approbation propriétaire.</p><p><a href="../README.md">Livraison / limites</a> · <a href="opus_snapshot.json">Sources de la capture Opus</a></p>'
    for file,label in gallery:h+=f'<section><h2>{html.escape(label)}</h2><a href="{file}"><img src="{file}"></a></section>'
    h+='<h2>Cues isolés — niveau livré</h2>'
    for p in sorted((LOT/'runtime/sounds/ui').glob('*.wav')):h+=f'<p>{p.stem}</p><audio controls src="../runtime/sounds/ui/{p.name}"></audio>'
    (LOT/'evidence/index.html').write_text(h+'</html>',encoding='utf8')
    print('UI manifest: 10 files. Gallery and source provenance complete.')

if __name__=='__main__':main()
