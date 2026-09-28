from pathlib import Path
import zipfile,difflib,json,hashlib
LOT=Path(__file__).resolve().parent.parent;BASE=Path('C:/PROJECTS/RF2_UZDOOM/src')
patch=[];records=[]
with zipfile.ZipFile(LOT/'review/RF2_MAP_02_HD_REVIEW.pk3') as z:
    for n in ('TEXTURES.rf02','zscript/rf/paris.zs'):
        raw=(BASE/n).read_bytes();old=raw.decode();new=z.read(n).decode().replace('\r\n','\n')
        if '\r\n' in old:new=new.replace('\n','\r\n')
        patch+=difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/src/'+n,tofile='b/src/'+n)
        records.append({'file':'src/'+n,'base_sha256':hashlib.sha256(raw).hexdigest(),'patched_sha256':hashlib.sha256(new.encode()).hexdigest()})
(LOT/'presentation_proposal/presentation.diff').write_bytes(''.join(patch).encode())
(LOT/'presentation_proposal/patch_bases.json').write_text(json.dumps(records,indent=2),encoding='utf8')
