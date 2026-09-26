"""Read-only audit against active tree; exercise shared patches/model install in own scratch."""
from pathlib import Path
import json,hashlib,subprocess,shutil
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(r'C:/PROJECTS/RF2_ART_HANDOFF_20260925/CODEX_LIVRAISON')
ACTIVE=Path(r'C:/PROJECTS/RF2_UZDOOM')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads((DEST/'MANIFEST.json').read_text(encoding='utf8'))
    allowed=('src/sprites/enemies/','src/sprites/fx/','src/graphics/weapons/','src/sounds/','art/rf2_art_01/')
    base={}
    for line in (DEST.parent/'BASE_6e1a31b.sha256').read_text().splitlines():
        h,n=line.split('  ',1);base[n]=h
    conflicts=[];new=[];replace=[]
    for r in m['files']:
        name=r['target'];p=DEST/'files'/name
        assert name.startswith(allowed) and '..' not in Path(name).parts
        assert p.is_file() and sha(p)==r['sha256'],name
        dst=ACTIVE/name
        if not dst.exists():new.append(name)
        elif sha(dst) in (base.get(name),r['sha256']):replace.append(name)
        else:conflicts.append(name)
    stage=(ROOT/'build/delivery_patch_check').resolve();assert stage.is_relative_to(ROOT/'build')
    for p in (DEST/'patch/base_844b50f').rglob('*'):
        if p.is_file():
            dst=stage/p.relative_to(DEST/'patch/base_844b50f');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    for name in ['production.patch','evidence_only.patch']:
        for command in [['git','apply','--check'],['git','apply']]:subprocess.run(command+[str(DEST/'patch'/name)],cwd=stage,check=True)
    for p in (DEST/'patch/review_result').rglob('*'):
        if p.is_file():assert (stage/p.relative_to(DEST/'patch/review_result')).read_text(encoding='utf8')==p.read_text(encoding='utf8')
    for rel in ['art/rf2_art_01/install_models.py']+[r['source'] for r in m['model_install']]:
        dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(DEST/'files'/rel,dst)
    subprocess.run(['python',str(stage/'art/rf2_art_01/install_models.py')],cwd=stage,check=True)
    for r in m['model_install']:assert sha(stage/r['target'])==r['sha256'],r['target']
    assert not (DEST/'files/src/maps').exists()
    result=dict(manifest_files_verified=len(m['files']),new_on_active=len(new),safe_replacements_on_active=len(replace),active_manual_conflicts=conflicts,active_tree_access='READ_ONLY',patch_application='PASS on exact 844b50f bases; final shared text matches',model_install='6/6 hashes match in isolated scratch',maps_in_import=0)
    (DEST/'evidence/delivery_validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    # Include this final validation in the outer checksum set.
    (DEST/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+p.relative_to(DEST).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
