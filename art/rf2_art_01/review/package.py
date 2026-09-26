"""Assemble a map-free import payload and a separately labelled frozen review build."""
from pathlib import Path
import json,hashlib,shutil,difflib,struct,wave,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'art/rf2_art_01'
DEST=Path(r'C:/PROJECTS/RF2_ART_HANDOFF_20260925/CODEX_LIVRAISON')
BASE=ROOT/'art_pass/base/opus_844b50f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,q):
    q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def diff(oldpath,newpath,path):
    # Preserve the base's actual EOL convention in patch context. TEXTURES was
    # committed with CRLF; other shared files are LF. Do not manufacture CRCRLF.
    raw=oldpath.read_bytes();eol='\r\n' if b'\r\n' in raw else '\n'
    old=[line+eol for line in oldpath.read_text(encoding='utf8').splitlines()]
    new=[line+eol for line in newpath.read_text(encoding='utf8').splitlines()]
    return difflib.unified_diff(old,new,fromfile='a/'+path,tofile='b/'+path)
def main():
    verification=json.loads((ROOT/'art_pass/evidence/verification.json').read_text())
    assert verification['pk3_sha256']==sha(ROOT/'dist/RF2_DEV.pk3')
    DEST.mkdir(parents=True,exist_ok=True)
    files=[]
    for prefix in ['src/sprites/enemies','src/sprites/fx','src/graphics/weapons/browning','src/graphics/weapons/fal']:
        files.extend(p for p in (ROOT/prefix).rglob('*') if p.is_file())
    audio=json.loads((ART/'audio/audio_manifest.json').read_text())
    audio_meta={x['target']:x for x in audio['files']}
    files.extend(ROOT/p for p in audio_meta)
    for p in ART.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ART).parts
        if any(x in rel for x in ('downloads','__pycache__','reexport','evidence')):continue
        if p.name in ('manifest_orderly.json','preview_manifest.json','corpse_models_orderly.json'):continue
        if p.suffix=='.pyc':continue
        files.append(p)
    rows=[]
    for p in sorted(set(files)):
        rel=p.relative_to(ROOT).as_posix();item=dict(target=rel,sha256=sha(p),bytes=p.stat().st_size)
        assert not rel.startswith(('src/maps/','scripts/mapkit/','campaign/'))
        if rel.startswith('art/'):
            item.update(role='editable_source_or_reproduction_tool',origin='RF2-ART-01; see CREDITS.md and IMAGEGEN_PROMPTS.md')
        elif rel.startswith('src/sounds/'):
            item.update(audio_meta[rel]);item['event']='See art/rf2_art_01/audio/events.csv and production.patch SNDINFO'
        elif '/enemies/' in rel:
            item.update(actor={'ORDY':'RFOrderly / RFOrderlyCorpse','BRCD':'RFBrancardier','PREG':'RFPorteRegistre','PRGS':'RFRegistryBundle'}.get(p.stem[:4],''),scale=.18,origin='art/rf2_art_01/enemies/production.py' if p.stem[:4]!='PRGS' else 'retained base projectile')
        elif '/browning/' in rel:item.update(actor='RFBrowning',origin='single generated master + rigid animation',texture_scale=[6,7.2],texture_offset=[-700,-300])
        elif '/fal/' in rel:item.update(actor='RFFAL',origin='retained Astra layers; byte-identical reconstruction',texture_scale=[6.8,8.16],texture_offset=[-750,-460])
        else:item.update(actor='RFArtBlood',origin='art/rf2_art_01/fx.py',scale=.12)
        if p.suffix.lower()=='.png':
            im=Image.open(p);item.update(dimensions=list(im.size),format=im.mode)
            raw=p.read_bytes();idx=raw.find(b'grAb')
            if idx>=0:item['png_grAb']=list(struct.unpack('>ii',raw[idx+4:idx+12]))
        copy(p,DEST/'files'/rel);rows.append(item)
    shared=['src/SNDINFO','src/TEXTURES.weapons','src/MODELDEF','src/zscript/rf/weapons.zs','src/zscript/rf/enemies.zs']
    patchdir=DEST/'patch';patchdir.mkdir(exist_ok=True)
    for group,paths in [('production',shared),('evidence_only',['src/CVARINFO','src/zscript/rf/dev.zs'])]:
        chunks=[]
        for path in paths:
            chunks.extend(diff(BASE/path,ROOT/path,path))
            copy(BASE/path,patchdir/'base_844b50f'/path)
            copy(ROOT/path,patchdir/'review_result'/path)
        (patchdir/(group+'.patch')).write_text(''.join(chunks),encoding='utf8',newline='\n')
    historical=[]
    for path in shared:
        historical.extend(diff(ROOT/'art_pass/base'/path,ROOT/path,path))
    (patchdir/'REFERENCE_ONLY_production_vs_6e1a31b.patch').write_text(''.join(historical),encoding='utf8',newline='\n')
    (patchdir/'LIRE.md').write_text('production.patch : delta artistique contre Opus 844b50f, recommandé.\nevidence_only.patch : outils de capture seulement.\nREFERENCE_ONLY_production_vs_6e1a31b.patch : comparaison historique demandée par le contrat ; inclut aussi les changements Opus sur ces cinq fichiers. Ne pas appliquer les deux patches de production.\nLes six modèles sont installés explicitement par art/rf2_art_01/install_models.py ; leur chemin src/models est hors liste de l\'importeur.\n',encoding='utf8')
    models=[]
    for p in (ART/'enemies/model_exports').glob('*'):
        models.append(dict(source=p.relative_to(ROOT).as_posix(),target='src/models/rf2_art_01/'+p.name,sha256=sha(p),installation='python art/rf2_art_01/install_models.py'))
    manifest=dict(schema=1,batch='RF2-ART-01',status='CANDIDATE_ART_COMPLETE',owner_review='OWNER_REVIEW_REQUIRED',base='6e1a31b79a38099f8121e8ac0b53fe7b169cad6f',shared_patch_base='844b50f',files=rows,model_install=models,shared_files=shared,evidence_only_shared=['src/CVARINFO','src/zscript/rf/dev.zs'],maps_in_import=0,verification=verification)
    (DEST/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
    for p in (ROOT/'art_pass/evidence').rglob('*'):
        if p.is_file() and not any(word in p.name for word in ('probe','calibration','preview')):copy(p,DEST/'evidence'/p.relative_to(ROOT/'art_pass/evidence'))
    for name in ['weapons_final','combat_final','corpses_final','rf01_final','combat_before_fixed']:
        folder=ROOT/'build/dev/film'/name
        for file in [name+'.mp4',name+'.wav','film.json']:
            p=folder/file
            if p.exists():copy(p,DEST/'evidence/films'/name/file)
    for name in ['after_weapons_1080','after_weapons_1440','after_weapons_1610','after_corpses','before_weapons_1080_v2','before_corpses','perf_before','perf_after','film_weapons_final','film_combat_final','film_corpses_final','film_rf01_final','norun_hidden']:
        p=ROOT/'build/dev/logs'/(name+'.txt')
        if p.exists():copy(p,DEST/'evidence/logs'/p.name)
    review=DEST/'review';copy(ROOT/'dist/RF2_DEV.pk3',review/'RF2_ART_RF01_REVIEW_ONLY.pk3')
    copy(ROOT/'build/dev/uzdoom.ini',review/'review.ini')
    (DEST/'JOUER_CANDIDATE.cmd').write_text('@echo off\nsetlocal\ncd /d "%~dp0review"\n"C:\\PROJECTS\\TOOLS\\UZDoom-5.0.1\\uzdoom.exe" -iwad "C:\\PROJECTS\\TOOLS\\Freedoom-0.13.0\\freedoom2.wad" -file "RF2_ART_RF01_REVIEW_ONLY.pk3" -config "review.ini" -savedir "saves" +map RF01 +screenblocks 10 +r_drawplayersprites 1 +rf_hud_scale 1 +rf_dev_autopilot 0 +rf_dev_weapons 0 +rf_dev_corpse 0 +rf_dev_perf 0 +rf_dev_art_combat 0 +rf_dev_film 0\n',encoding='ascii')
    for name in ['RAPPORT.md','POUR_OPUS.md']:
        copy(ROOT/'art_pass'/name,DEST/name)
    (DEST/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+p.relative_to(DEST).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf8')
    print(json.dumps({'delivery':str(DEST),'files':len(rows),'model_install':len(models),'pk3':verification['pk3_sha256']},indent=2))
if __name__=='__main__':main()
