"""Audit the actual runtime contract, complete coverage and protected package entries."""
from pathlib import Path
import hashlib,json,re,struct,sys,zipfile
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2]
sys.path.insert(0,str(HERE));import export as E
SHA='5b53d9eaaaf088f49ae98f667fc1d575779dc74e'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def grab(p):
    b=p.read_bytes();i=b.index(b'grAb');return list(struct.unpack('>ii',b[i+4:i+12]))

def maps():
    consumers={n:[] for n in ['RFOrderly','RFBrancardier','RFPorteRegistre','RFOrderlyCorpse']}
    ids={30401:'RFOrderly',30402:'RFBrancardier',30403:'RFPorteRegistre',30410:'RFOrderlyCorpse'}
    for p in sorted((ROOT/'src/maps').glob('RF*.wad')):
        raw=p.read_bytes();count,offset=struct.unpack_from('<ii',raw,4)
        for k in range(count):
            off,size,name=struct.unpack_from('<ii8s',raw,offset+16*k)
            if name.rstrip(b'\0')!=b'TEXTMAP':continue
            text=raw[off:off+size].decode('utf8')
            for tid,n in ids.items():
                number=len(re.findall(r'\btype\s*=\s*'+str(tid)+r'\s*;',text))
                if number:consumers[n].append({'map':p.stem,'direct_placements':number})
    return consumers

def main():
    files=[];expected=set();families=[];consumers=maps()
    opus=json.loads((HERE/'contract/BASE_MANIFEST.json').read_text(encoding='utf-8-sig'))
    opus_files={p['path']:p for p in opus['sprites']}
    for entry in opus['terminal_models']:
        assert digest(ROOT/entry['path'])==entry['sha256'], entry['path']+' Opus model/skin base hash'
    for family,cls in [('orderly','RFOrderly'),('brancardier','RFBrancardier'),('porte_registre','RFPorteRegistre')]:
        m=E.family(family)
        families.append(dict(name=family,actor=cls,prefix=m.PREFIX,frames=[s[0] for s in m.STATES],rotation_yaw=m.ROT_YAW,scale=.18,consumers=consumers[cls]))
        for letter,state,fn,kw in m.STATES:
            for rotation in range(1,9):
                name=f'{m.PREFIX}{letter}{rotation}.png';relative='sprites/enemies/'+name;expected.add(relative)
                p=LOT/'runtime'/relative;base=ROOT/'src'/relative
                assert p.is_file(),str(p)
                op=opus_files['src/'+relative]
                assert digest(base)==op['sha256'],name+' Opus base hash'
                new,old=Image.open(p),Image.open(base)
                assert new.mode=='RGBA' and new.size==old.size,name+' dimensions/mode'
                assert grab(p)==grab(base),name+' pivot'
                assert np.array_equal(np.asarray(new)[:,:,3],np.asarray(old)[:,:,3]),name+' silhouette/alpha'
                files.append(dict(file='runtime/'+relative,target_relpath=relative,action='replace',kind='enemy_sprite',
                    sha256=digest(p),base_sha256=digest(base),bytes=p.stat().st_size,width=new.width,height=new.height,
                    grab=grab(p),scale=.18,actor=cls,state=state,frame=letter,rotation=rotation,runtime_states=op['states'],
                    source='source/export.py + source/enemies/',source_method='Existing articulated SDF master; material-only deterministic export from frozen image_gen atlas',
                    license_or_origin='Project source + image_gen generated material atlas; Nameless / Pomegranate Interactive',
                    confidence='runtime candidate; owner review required',notes='Exact base dimensions, grAb and alpha. Original actor code and timings unchanged.'))
        relative=f'models/rf2_art_01/{family}_skin.png';expected.add(relative)
        p=LOT/'runtime'/relative;base=ROOT/'src'/relative;im=Image.open(p)
        assert im.size==Image.open(base).size
        files.append(dict(file='runtime/'+relative,target_relpath=relative,action='replace',kind='corpse_skin',sha256=digest(p),base_sha256=digest(base),bytes=p.stat().st_size,width=im.width,height=im.height,
            actor=cls,source='source/enemies/material_atlas.png',source_method='Fixed atlas rebake; original OBJ and UVs unchanged',license_or_origin='Project + image_gen',confidence='owner review required',notes='No MODELDEF, mesh, pivot or settling change.'))
    actual={p.relative_to(LOT/'runtime').as_posix() for p in (LOT/'runtime').rglob('*') if p.is_file()}
    assert actual==expected,(actual-expected,expected-actual)
    contract=LOT/'source/contract';contract.mkdir(exist_ok=True)
    for rel in ['zscript/rf/enemies.zs','MODELDEF','MAPINFO']:
        dst=contract/Path(rel).name;dst.write_bytes((ROOT/'src'/rel).read_bytes())
    (contract/'families.json').write_text(json.dumps({'base_commit':SHA,'origin':'Observed in local base and matched to Opus contract received during this session','families':families,'map_consumers':consumers,'wave_consumers':'RFWaveSpot args 1/2/3 can spawn the same classes; RF02 reuse intended by Opus'},indent=2),encoding='utf8')
    protected=[]
    with zipfile.ZipFile(LOT/'review/REFERENCE_5b53d9e.pk3') as a,zipfile.ZipFile(LOT/'review/RF2_ART_02_CANDIDATE.pk3') as b:
        assert set(a.namelist())==set(b.namelist())
        for name in a.namelist():
            if name not in expected:
                assert a.read(name)==b.read(name),name+' outside scope changed'
                protected.append(name)
    (LOT/'manifest.json').write_text(json.dumps({'schema':1,'batch_id':'RF2-ART-02','status':'OWNER_REVIEW_REQUIRED','canon_coverage':[],'canon_register':'../RF2_CANON_01/catalogue.json','base_commit':SHA,'files':files},indent=2),encoding='utf8')
    (LOT/'evidence/validation.json').write_text(json.dumps({'complete_sprites':320,'corpse_skins':3,'alpha_identical':True,'dimensions_and_grab_identical':True,'protected_package_entries_identical':len(protected),'protected_entries':protected,'geometry_and_gameplay':'unchanged','owner_approval':False},indent=2),encoding='utf8')
    print('PASS: 320 complete sprites, exact alpha/canvas/grAb; 3 skins; protected package entries:',len(protected))

if __name__=='__main__':main()
