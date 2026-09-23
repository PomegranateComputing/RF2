from __future__ import annotations
import hashlib, json, struct, sys, wave
from pathlib import Path

ALLOWED = {'.png','.jpg','.jpeg','.webp','.wav','.ogg','.flac','.blend','.fbx','.glb','.gltf','.json','.txt','.md','.ora','.kra','.psd'}

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def png_size(p: Path):
    with p.open('rb') as f:
        sig=f.read(24)
    if len(sig)>=24 and sig[:8]==b'\x89PNG\r\n\x1a\n' and sig[12:16]==b'IHDR':
        return struct.unpack('>II',sig[16:24])
    return None

def main():
    if len(sys.argv)!=2:
        raise SystemExit('usage: validate_astra_batch.py <batch_path>')
    root=Path(sys.argv[1]).resolve()
    man=root/'manifest.json'
    if not root.is_dir() or not man.is_file():
        raise SystemExit('FAIL: batch dir or manifest.json missing')
    data=json.loads(man.read_text(encoding='utf-8-sig'))
    if data.get('status') not in {'ASTRA_GENERATED','OWNER_REVIEW_REQUIRED','FABLE_REVIEWED'}:
        raise SystemExit('FAIL: invalid status')
    files=data.get('files')
    if not isinstance(files,list) or not files:
        raise SystemExit('FAIL: manifest files[] empty')
    errors=[]
    for idx,item in enumerate(files):
        rel=item.get('file','')
        target=item.get('target_relpath','')
        p=(root/rel).resolve()
        if root not in p.parents:
            errors.append(f'{idx}: file escapes batch')
            continue
        if not p.is_file():
            errors.append(f'{idx}: missing {rel}')
            continue
        if p.suffix.lower() not in ALLOWED:
            errors.append(f'{idx}: extension not allowed {p.suffix}')
        actual=sha256(p)
        expected=str(item.get('sha256','')).lower()
        if expected and actual!=expected:
            errors.append(f'{idx}: sha256 mismatch {rel}')
        if item.get('bytes') not in (None,0,p.stat().st_size):
            errors.append(f'{idx}: bytes mismatch {rel}')
        if not target or target.startswith(('/', '\\')) or '..' in Path(target).parts:
            errors.append(f'{idx}: invalid target_relpath {target!r}')
        if p.suffix.lower()=='.png':
            s=png_size(p)
            if not s:
                errors.append(f'{idx}: invalid PNG {rel}')
            else:
                w,h=s
                ew,eh=item.get('width'),item.get('height')
                if ew not in (None,0,w) or eh not in (None,0,h):
                    errors.append(f'{idx}: PNG dimensions mismatch {rel}: {w}x{h}')
        if p.suffix.lower()=='.wav':
            try:
                with wave.open(str(p),'rb') as w:
                    _=(w.getnchannels(),w.getframerate(),w.getsampwidth(),w.getnframes())
            except Exception as e:
                errors.append(f'{idx}: invalid WAV {rel}: {e}')
    if errors:
        print('ASTRA BATCH VALIDATION: FAIL')
        for e in errors: print(' -',e)
        raise SystemExit(2)
    print(f'ASTRA BATCH VALIDATION: PASS ({len(files)} files)')

if __name__=='__main__':
    main()
