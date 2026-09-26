"""Verify actual packaged assets, animation budgets and map immutability."""
from pathlib import Path
import hashlib,json,re,struct,zipfile,csv,io
from PIL import Image
import soundfile as sf
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'art/rf2_art_01'
BASE=ROOT/'art_pass/base/opus_844b50f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    report={}
    expected={'src/maps/RF01.wad':'b643321673c6447a680c2e1a1fbed44359194e9fcc751c127a6d667f276930b7','scripts/mapkit/rf01.py':'7fe077a418e625f7d28d8fe8e3111d69a9c3c98ac374225a81afbc165b4060c6'}
    for p,h in expected.items():assert sha(ROOT/p)==h,p
    report['immutable_map']=expected
    frames=json.loads((ART/'enemies/manifest_all.json').read_text())
    assert len(frames)==320
    for item in frames:
        p=ROOT/'src/sprites/enemies'/item['file'];im=Image.open(p)
        assert im.mode=='RGBA' and list(im.size)==item['dimensions'],p
        raw=p.read_bytes();pos=raw.find(b'grAb');assert pos>=0
        assert list(struct.unpack('>ii',raw[pos+4:pos+12]))==item['grab']
        im.verify()
    report['enemy_frames']=len(frames)
    basezip=zipfile.ZipFile(ROOT/'art_pass/base/RF2_BASE_REVIEW_ONLY.pk3')
    heights=[]
    for pre in ['ORDY','BRCD','PREG']:
        old=Image.open(io.BytesIO(basezip.read(f'sprites/enemies/{pre}A1.png'))).convert('RGBA')
        new=Image.open(ROOT/f'src/sprites/enemies/{pre}A1.png').convert('RGBA')
        a=old.getchannel('A').getbbox();b=new.getchannel('A').getbbox()
        h0=(a[3]-a[1])*.18*1.2;h1=(b[3]-b[1])*.18*1.2
        assert abs(h1-h0)<2,(pre,h0,h1)
        heights.append(dict(family=pre,baseline_world_height=round(h0,3),candidate_world_height=round(h1,3),pixel_stretch=1.2,scale=.18))
    report['standing_height_comparison']=heights

    for path,prefixes in [('src/zscript/rf/weapons.zs',['BHPG','RFLV']),('src/zscript/rf/enemies.zs',['ORDY','BRCD','PREG'])]:
        a=(BASE/path).read_text();b=(ROOT/path).read_text()
        for pre in prefixes:
            pattern=rf'^\s*{pre}\s+([A-Z]+)\s+(-?\d+)'
            old=re.findall(pattern,a,re.M);new=re.findall(pattern,b,re.M)
            assert old==new,(pre,old,new)
    report['state_frame_time_budgets']='IDENTICAL to Opus 844b50f for BHPG/RFLV/ORDY/BRCD/PREG'
    aud=json.loads((ART/'audio/audio_manifest.json').read_text())
    for item in aud['files']:
        a,sr=sf.read(ROOT/item['target']);info=sf.info(ROOT/item['target'])
        assert sr==48000 and a.ndim==1 and info.subtype=='PCM_16'
        assert np.max(abs(a))<1
    report['audio_cues']=len(aud['files']);report['audio_file_clipping']=0
    report['human_audition']='NOT_PERFORMED_BY_AGENT'
    fal=ART/'weapons/fal_legacy_source/reexport'
    assert len(list(fal.glob('*.png')))==21
    assert all(sha(p)==sha(ROOT/'src/graphics/weapons/fal'/p.name) for p in fal.glob('*.png'))
    report['fal_reexport']='21/21 byte-identical'
    z=zipfile.ZipFile(ROOT/'dist/RF2_DEV.pk3');names=z.namelist();assert len(names)==len(set(names))
    checked=0
    for prefix in ['sprites/enemies/','sprites/fx/','graphics/weapons/','sounds/','models/rf2_art_01/']:
        for p in (ROOT/'src'/prefix).rglob('*'):
            if p.is_file():
                n=p.relative_to(ROOT/'src').as_posix();assert z.read(n)==p.read_bytes(),n;checked+=1
    assert hashlib.sha256(z.read('maps/RF01.wad')).hexdigest()==expected['src/maps/RF01.wad']
    report['pk3_assets_verified']=checked;report['pk3_sha256']=sha(ROOT/'dist/RF2_DEV.pk3')
    snd=(ROOT/'src/SNDINFO').read_text();rows=[]
    for line in snd.splitlines():
        m=re.match(r'([^/$\s]\S*)\s+"(sounds/[^\"]+)"',line)
        if m:
            event,target=m.groups();assert (ROOT/'src'/target).exists(),target
            rows.append([event,'src/'+target,'mono; actor channel/attenuation from ZScript; mix volume in SNDINFO'])
    with (ART/'audio/events.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['event','target','runtime_parameters']);w.writerows(rows)
    report['sound_routes_verified']=len(rows)
    (ROOT/'art_pass/evidence/verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
