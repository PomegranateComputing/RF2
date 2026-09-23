#!/usr/bin/env python3
"""Independent reader of the delivered PK3/WAD, not the builder's tile graph.
Checks structural validity, sector loops, texture resolution, placed things and
key/exit reachability through actual two-sided linedefs. Not a runtime playtest.
"""
import struct, json, re, zipfile, hashlib
from pathlib import Path
from collections import defaultdict,deque,Counter
ROOT=Path(__file__).resolve().parents[1]

def readwad(b):
    magic,n,off=struct.unpack_from('<4sii',b)
    assert magic==b'PWAD' and 0<n<100 and 12<=off<=len(b)
    assert off+n*16==len(b)
    lumps={}
    for i in range(n):
        pos,size,name=struct.unpack_from('<ii8s',b,off+i*16);name=name.rstrip(b'\0').decode('ascii')
        assert 0<=pos<=off and 0<=size<=off-pos
        assert name not in lumps
        lumps[name]=b[pos:pos+size]
    assert 'TEXTMAP' in lumps and 'ENDMAP' in lumps
    assert list(lumps)[-1]=='ENDMAP'
    return lumps

def parse(text):
    text=re.sub(r'//[^\n]*','',text)
    assert 'namespace = "zdoom";' in text
    out=defaultdict(list)
    for kind,body in re.findall(r'(vertex|linedef|sidedef|sector|thing)\s*\{([^}]+)\}',text):
        d={}
        for key,value in re.findall(r'(\w+)\s*=\s*("[^"]*"|[^;]+);',body):
            v=value.strip()
            if v.startswith('"'):v=json.loads(v)
            elif v in ('true','false'):v=v=='true'
            else:v=float(v) if '.' in v else int(v)
            assert key not in d
            d[key]=v
        out[kind].append(d)
    return out

def check(code,wad_bytes,available,source):
    lumps=readwad(wad_bytes);assert next(iter(lumps))==code
    # A node builder may normalize whitespace. Canonical source is packaged separately.
    t=parse(lumps['TEXTMAP'].decode());vs=t['vertex'];ls=t['linedef'];ss=t['sidedef'];se=t['sector'];things=t['thing']
    assert len(vs)>3 and ls and ss and se and things
    xy=[(v['x'],v['y']) for v in vs];assert len(xy)==len(set(xy))
    loops=defaultdict(list);graph=defaultdict(list);seen=set();exits=[];door_tags=set()
    for l in ls:
        a,b=l['v1'],l['v2'];assert 0<=a<len(vs) and 0<=b<len(vs) and a!=b
        assert xy[a][0]==xy[b][0] or xy[a][1]==xy[b][1]
        key=tuple(sorted((a,b)));assert key not in seen;seen.add(key)
        fi=l['sidefront'];assert 0<=fi<len(ss);f=ss[fi]['sector'];assert 0<=f<len(se)
        loops[f].append((a,b));bi=l.get('sideback',-1)
        if bi>=0:
            assert bi<len(ss) and l.get('twosided') and not l.get('blocking')
            ba=ss[bi]['sector'];assert 0<=ba<len(se) and ba!=f
            loops[ba].append((b,a));graph[f].append(ba);graph[ba].append(f)
        else:assert l.get('blocking')
        if l.get('special')==243:
            assert l.get('playeruse');exits.append(f)
        if l.get('special')==13:
            assert l['arg3']==2, 'BlueCard requires lock 2 in UZDoom Doom LOCKDEFS'
            assert l['arg1']>0 and l['arg2']>0 and l.get('repeatspecial')
            door_tags.add(l['arg0'])
    assert len(exits)==1 and door_tags=={100}
    for s,edges in loops.items():
        incoming=Counter(b for a,b in edges);outgoing=Counter(a for a,b in edges)
        assert incoming==outgoing, f'{code}: open sector {s}'
        assert se[s]['heightfloor']<=se[s]['heightceiling']
    for obj in ss+se:
        for k,v in obj.items():
            if k.startswith('texture'):assert v in available or v in ('-','F_SKY1'),(code,'missing texture',v)

    def contains(si,x,y):
        inside=False
        for a,b in loops[si]:
            ax,ay=xy[a];bx,by=xy[b]
            if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
        return inside
    locations=[]
    for obj in things:
        hits=[s for s in range(len(se)) if contains(s,obj['x'],obj['y'])]
        assert len(hits)==1,(code,'thing outside or overlapping sector',obj,hits)
        s=hits[0];assert se[s]['heightceiling']-se[s]['heightfloor']>=56
        assert obj.get('single') and all(f'skill{i}' in obj for i in range(1,6))
        locations.append(s)
    assert len({(q['x'],q['y']) for q in things})==len(things)
    starts=[i for i,t in enumerate(things) if t['type']==1];keys=[i for i,t in enumerate(things) if t['type']==5]
    assert len(starts)==1 and len(keys)==1
    def reachable(key):
        first=locations[starts[0]];seen={first};q=deque([first])
        while q:
            a=q.popleft();sa=se[a]
            for b in graph[a]:
                if b in seen:continue
                sb=se[b];isdoor=sb.get('id',0) in (100,200,201)
                if isdoor and sb.get('id')==100 and not key:continue
                if not isdoor and sb['heightceiling']-sb['heightfloor']<56:continue
                # Doom's walk step is 24 units. Reject crossing tall scenery.
                if abs(sa['heightfloor']-sb['heightfloor'])>24:continue
                seen.add(b);q.append(b)
        return seen
    no=reachable(False);yes=reachable(True)
    assert locations[keys[0]] in no and exits[0] not in no and exits[0] in yes
    assert all(s in yes for s in locations)
    secret=[i for i,s in enumerate(se) if s.get('special',0)&1024]
    assert len(secret)==2 and all(s in yes for s in secret)
    return dict(code=code,status='PASS',vertices=len(vs),linedefs=len(ls),sectors=len(se),things=len(things),secrets=len(secret),lumps=list(lumps),sha256=hashlib.sha256(wad_bytes).hexdigest())

def main():
    p=ROOT/'build/RF2_MAPS_V1.pk3';reports=[]
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        available={Path(n).stem.upper() for n in z.namelist() if n.lower().endswith('.png')}
        maps=[n for n in z.namelist() if n.startswith('maps/') and n.endswith('.wad')]
        assert len(maps)==23 and len(set(maps))==23
        mi=z.read('MAPINFO').decode()
        for i in range(1,24):
            code=f'RF{i:02d}'
            assert re.search(r'map '+code+r'\s',mi)
            if i<23:assert f'next = "RF{i+1:02d}"' in mi
            reports.append(check(code,z.read(f'maps/{code}.wad'),available,ROOT/'src'/code/'TEXTMAP'))
        assert 'endgame' in mi and 'RF24' not in mi
    result=dict(scope='Static checks on delivered bytes; no runtime traversal claimed',pk3_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),maps=reports,status='PASS')
    (ROOT/'evidence/PACK_VALIDATION.json').write_text(json.dumps(result,indent=2))
    print('PASS: 23 WADs, geometry, closed sector boundaries, all thing positions, blue lock 2, secret access, all textures, campaign chain and ending.')

if __name__=='__main__':main()
