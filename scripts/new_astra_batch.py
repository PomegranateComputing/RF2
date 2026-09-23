from __future__ import annotations
import json, re, sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: new_astra_batch.py <BATCH_ID>')
    batch_id=sys.argv[1].strip()
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9_.-]{2,80}',batch_id):
        raise SystemExit('invalid BATCH_ID')
    root=Path(__file__).resolve().parents[1]
    b=root/'incoming'/'astra'/batch_id
    if b.exists():
        raise SystemExit(f'already exists: {b}')
    for d in ('source','runtime','evidence'):
        (b/d).mkdir(parents=True,exist_ok=True)
    manifest={
        'schema':1,'batch_id':batch_id,'created_by':'Codex Astra','status':'ASTRA_GENERATED',
        'level':'RF01','summary':'','files':[]
    }
    (b/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (b/'README.md').write_text(f'# {batch_id}\n\nStatus: ASTRA_GENERATED\n',encoding='utf-8')
    print(b)
if __name__=='__main__': main()
