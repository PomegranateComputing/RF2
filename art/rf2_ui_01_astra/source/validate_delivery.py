"""Validate the actual ten-resource Opus contract and the captured package."""
from pathlib import Path
import hashlib,json,wave,zipfile
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;LOT=HERE.parent
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    expected={'graphics/TITLEPIC.png','graphics/ui/RFMENUBG.png'}
    expected.update('sounds/ui/'+n+'.wav' for n in ('cursor','choose','change','backup','clear','invalid','prompt','dismiss'))
    actual={p.relative_to(LOT/'runtime').as_posix():p for p in (LOT/'runtime').rglob('*') if p.is_file()}
    assert set(actual)==expected
    assert actual['graphics/TITLEPIC.png'].read_bytes()==actual['graphics/ui/RFMENUBG.png'].read_bytes()
    sounds=[]
    for name,p in actual.items():
        if p.suffix=='.png':
            im=Image.open(p);assert im.mode=='RGB' and im.size==(1920,1080)
        else:
            with wave.open(str(p)) as w:
                assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,48000)
                duration=w.getnframes()/w.getframerate();assert .06<=duration<=.25
                x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
            peak=20*np.log10(np.abs(x).max());assert -27.1<=peak<=-19.9
            assert abs(x[0])<1/32768 and abs(x[-1])<1/32768
            sounds.append(dict(file=name,seconds=duration,peak_dbfs=float(peak),edge_samples_zero=True))
    snapshot=json.loads((LOT/'evidence/opus_snapshot.json').read_text(encoding='utf8'))
    package=LOT/'review/RF2_UI_01_OPUS_SNAPSHOT.pk3'
    assert sha(package.read_bytes())==snapshot['package_sha256']
    protected=0
    with zipfile.ZipFile(package) as z:
        assert set(z.namelist())==set(snapshot['base_src_hashes'])|expected
        for n in z.namelist():
            if n in actual:assert z.read(n)==actual[n].read_bytes()
            else:
                assert sha(z.read(n))==snapshot['base_src_hashes'][n],n+' outside art scope changed'
                protected+=1
    reports=json.loads((LOT/'evidence/opus_snapshot_captures.json').read_text(encoding='utf8'))
    assert all(r['status']=='marker:RF_DEV_UI_DONE' for r in reports)
    result=dict(status='PASS',runtime_files=10,images_identical=True,sounds=sounds,protected_package_entries_identical=protected,
                package_sha256=snapshot['package_sha256'],menu_code_and_sndinfo_unchanged=True,audio_audition=False,owner_approval=False)
    (LOT/'evidence/validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('PASS: ten contract resources; eight WAVs;',protected,'other package entries unchanged.')
if __name__=='__main__':main()
