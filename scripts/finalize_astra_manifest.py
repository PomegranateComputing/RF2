from __future__ import annotations
import hashlib, json, struct, sys
from pathlib import Path

def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

def png_size(p):
    d=p.read_bytes()[:24]
    if len(d)>=24 and d[:8]==b'\x89PNG\r\n\x1a\n' and d[12:16]==b'IHDR':
        return struct.unpack('>II',d[16:24])

def main():
    if len(sys.argv)!=2: raise SystemExit('usage: finalize_astra_manifest.py <batch_path>')
    b=Path(sys.argv[1]).resolve(); m=b/'manifest.json'
    data=json.loads(m.read_text(encoding='utf-8-sig'))
    for item in data.get('files',[]):
        p=b/item['file']
        if not p.is_file(): raise SystemExit(f'missing: {p}')
        item['sha256']=sha256(p); item['bytes']=p.stat().st_size
        if p.suffix.lower()=='.png':
            s=png_size(p)
            if s: item['width'],item['height']=s
    m.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    print(m)
if __name__=='__main__': main()
