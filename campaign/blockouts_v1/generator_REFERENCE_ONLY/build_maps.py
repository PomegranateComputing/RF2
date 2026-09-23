#!/usr/bin/env python3
"""Build the authored RF2 layouts into editable ZDoom-namespace UDMF PWADs.
Python 3.10+ standard library; art PNGs are already supplied separately.
No stale BSP data is copied. UZDoom builds nodes when loading TEXTMAP.
"""
from pathlib import Path
from collections import deque, Counter
import json, struct, hashlib, zipfile, random, math, html
from campaign import campaign

ROOT = Path(__file__).resolve().parents[1]
UNIT = 64
DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
MONSTERS = {3004,9,3001,3002,58,3005,69,68,66,67,64,71}
PALETTES = {
 'clinic': ('RFPLAST','RFTILE','RFCEIL',184),
 'street': ('RFBRICK','RFROAD','F_SKY1',208),
 'rail': ('RFBRICK','RFGRIT','RFCEIL',184),
 'fair': ('RFPAINT','RFWOOD','RFCEIL',184),
 'machine': ('RFMETAL','RFGRIT','RFCEIL',168),
 'jerma': ('RFSTONE','RFTILE','RFCEIL',200),
 'hotel': ('RFPLAST','RFCARPT','RFCEIL',176),
 'pool': ('RFSTONE','RFPOOL','F_SKY1',216),
 'service': ('RFTILEW','RFTILE','RFCEIL',176),
 'anomaly': ('RFPOM','RFCARPT','RFCEIL',176),
 'stairs': ('RFCONC','RFCONCF','RFCEIL',192),
 'motel': ('RFPLAST','RFCARPT','RFCEIL',184),
 'dock': ('RFCORR','RFROAD','F_SKY1',200),
 'cold': ('RFFREEZ','RFTILE','RFCEIL',184),
 'broadcast': ('RFPANEL','RFCARPT','RFCEIL',176),
 'archive': ('RFPLAST','RFLINO','RFCEIL',184),
 'server': ('RFMETAL','RFLINO','RFCEIL',176)
}

def desc(wall='RFCONC',floor='RFCONCF',ceil='RFCEIL',light=184,z=0,h=192,tag=0,special=0,role='floor'):
    return (wall,floor,ceil,light,z,h,tag,special,role)

class Map:
    def __init__(self,spec):
        self.spec=spec; self.cells={}; self.things=[]; self.landmarks=[]; self.doors={}; self.wall_actions={}
        self.rng=random.Random(11700+spec['number']); self.used=set()
        self.base=desc(*PALETTES[spec['theme']]); self.route=set(); self.secret_centres=[]

    def rect(self,x,y,w,h,d,overwrite=True):
        for xx in range(x,x+w):
            for yy in range(y,y+h):
                if overwrite or (xx,yy) not in self.cells:self.cells[xx,yy]=d

    def path(self,points,width=3,d=None):
        d=d or desc(wall=self.base[0],floor=self.base[1],light=168,h=160)
        for (ax,ay),(bx,by) in zip(points,points[1:]):
            assert ax==bx or ay==by
            dx=(bx>ax)-(bx<ax);dy=(by>ay)-(by<ay)
            for step in range(abs(bx-ax)+abs(by-ay)+1):
                x,y=ax+step*dx,ay+step*dy
                self.route.add((x,y))
                self.rect(x-width//2,y-width//2,width,width,d,False)

    def room(self,i,room):
        x,y,w,h=room; name=self.spec['labels'][i]; theme=self.spec['theme']
        wall,floor,ceil,light=PALETTES[theme]
        outdoor=any(t in name.lower() for t in ['cour','quai','parking','parvis','terrasse','boulevard','route','friches','toiture','carrefour','voie','promenade','grille','place','canal'])
        if theme=='street':outdoor=i not in (2,4,5,8)
        if outdoor:ceil='F_SKY1';light=216;floor='RFGRIT' if theme in ('jerma','pool') else 'RFROAD'
        elif ceil=='F_SKY1':ceil='RFCEIL'
        ht=384 if outdoor else (256 if w*h>=130 else 192)
        d=desc(wall,floor,ceil,light,0,ht)
        self.rect(x-w//2,y-h//2,w,h,d)
        self.landmarks.append(dict(index=i,cell=[x,y],name=name,bounds=[x-w//2,y-h//2,w,h],outdoor=outdoor))

    def relief(self):
        n=self.spec['number'];theme=self.spec['theme']
        for i,(x,y,w,h) in enumerate(self.spec['rooms']):
            if i==0:continue
            base=self.cells[x,y]
            # Structural piers, shelving runs, scenery represented as real geometry.
            if theme in ('archive','cold','server','broadcast'):
                for xx in [x-w//2+2,x+w//2-3]:
                    for yy in range(y-h//2+2,y+h//2-2,3):
                        if abs(xx-x)<=1 or abs(yy-y)<=1:continue
                        wall='RFRACK' if theme=='server' else ('RFBOX' if theme=='archive' else 'RFMETAL')
                        self.rect(xx,yy,1,2,desc(wall,'RFMETOP',base[2],base[3]-8,96,base[5],role='obstacle'))
            elif theme in ('street','dock','rail'):
                for xx,yy in [(x-2,y-2),(x+2,y+2)]:
                    self.rect(xx,yy,2,1,desc('RFCRATE','RFWOOD',base[2],base[3]-8,64,base[5],role='obstacle'))
            else:
                for xx,yy in [(x-w//2+2,y-h//2+2),(x+w//2-3,y+h//2-3)]:
                    self.rect(xx,yy,1,1,desc('RFCONC','RFCONCF',base[2],base[3],base[5],base[5],role='pillar'))
            # Stepped dais / gallery. 16-unit risers, no jump needed.
            if i in (3,7) and h>=8:
                for step in range(1,4):
                    yy=y+h//2-1-step
                    self.rect(x-w//2+2,yy,w-4,1,desc(base[0],base[1],base[2],base[3]-step*6,16*(4-step),base[5]))
            # Recessed central pool with traversable 16-unit concentric steps.
            if (n==9 and i==1) or (theme=='fair' and i==4):
                for inset in range(4):
                    ww=w-6-2*inset;hh=h-6-2*inset
                    if min(ww,hh)<2:break
                    floor='RFPOOL' if n==9 else 'RFPOMF'
                    self.rect(x-ww//2,y-hh//2,ww,hh,desc(base[0],floor,base[2],base[3]-inset*8,-16*(inset+1),base[5]))
            # A different recessed light patch in every room, not a post-process veil.
            for xx in range(x-1,x+2):
                p=(xx,y)
                d=list(self.cells[p]);d[3]=min(240,d[3]+24);self.cells[p]=tuple(d)

    def available(self,p,radius=20):
        if p in self.used or p not in self.cells:return False
        d=self.cells[p]
        if d[8] in ('door','obstacle','pillar') or d[5]-d[4]<72:return False
        # Radius 20 sits inside a 64-unit tile. Larger actors require adjacent space.
        if radius>30:
            for dx,dy in DIRS:
                dd=self.cells.get((p[0]+dx,p[1]+dy))
                if dd is None or dd[8] in ('obstacle','pillar','door') or abs(dd[4]-d[4])>24:return False
        return True

    def thing(self,type,p,skill=1,angle=0,radius=20):
        assert self.available(p,radius),(self.spec['code'],type,p)
        self.used.add(p)
        d=dict(x=p[0]*UNIT+UNIT//2,y=p[1]*UNIT+UNIT//2,type=type,angle=angle,
               skill1=skill<=1,skill2=skill<=1,skill3=skill<=2,skill4=True,skill5=True,
               single=True,coop=True,dm=False)
        if type in MONSTERS:d['ambush']=True
        self.things.append(d)

    def place_near(self,type,p,skill=1,radius=20):
        candidates=[(p[0]+dx,p[1]+dy) for dx in range(-4,5) for dy in range(-4,5)]
        candidates.sort(key=lambda v:((v[0]-p[0])**2+(v[1]-p[1])**2,v))
        for c in candidates:
            if self.available(c,radius):self.thing(type,c,skill,self.rng.randrange(8)*45,radius);return c
        raise ValueError(('No free position',type,p))

    def add_exit(self):
        # Attach the exit to the north-most room. Everything beyond the door is new.
        rooms=self.spec['rooms'];i=max(range(len(rooms)),key=lambda j:rooms[j][1]+rooms[j][3]//2)
        x,y,w,h=rooms[i]; edge=y-h//2+h
        d=desc('RFMETAL','RFLINO','RFCEIL',184)
        self.rect(x-1,edge,3,5,d)
        dy=edge+2
        self.rect(x-1,dy,3,1,desc('RFDOORB','RFLINO','RFDOORF',176,0,0,100,role='door'))
        self.doors[100]=dict(lock=2,name='Controle bleu',cells=[(xx,dy) for xx in range(x-1,x+2)])
        self.rect(x-3,edge+5,7,6,desc('RFPOM','RFLINO','RFCEIL',200))
        self.exit_cell=(x,edge+10);self.exit_approach=(x,edge+8)
        self.wall_actions[(self.exit_cell,(0,1))]=dict(special=243,arg0=0,playeruse=True)
        self.exit_room=i
        self.landmarks.append(dict(index=len(rooms),cell=[x,edge+7],name='Sortie / badge bleu',bounds=[x-3,edge+5,7,6],outdoor=False))

    def add_secrets(self):
        # Hidden, usable panel doors open into small off-route recesses.
        for s in range(2):
            made=False
            for i in range(2+s,len(self.spec['rooms'])):
                x,y,w,h=self.spec['rooms'][i]
                for sign in (-1,1):
                    edge=x-w//2 if sign==-1 else x-w//2+w-1
                    # Entire extension plus a one-tile safety border must be empty.
                    px=edge+sign*5;py=y+2
                    region=[(xx,yy) for xx in range(px-3,px+4) for yy in range(py-3,py+4)]
                    if any(p in self.cells for p in region):continue
                    self.rect(px-2,py-2,5,5,desc(self.base[0],'RFPOMF','RFCEIL',160,special=1024))
                    self.path([(edge,py),(px,py)],1,desc(self.base[0],self.base[1],'RFCEIL',160))
                    dp=(edge+sign,py);tag=200+s
                    self.cells[dp]=desc(self.base[0],self.base[1],'RFDOORF',160,0,0,tag,role='door')
                    self.doors[tag]=dict(lock=0,name=f'Secret {s+1}',cells=[dp])
                    self.secret_centres.append((px,py));made=True;break
                if made:break
            if not made:raise ValueError(('No secret slot',self.spec['code'],s))

    def populate(self):
        n=self.spec['number'];rooms=self.spec['rooms'];start=tuple(rooms[0][:2]);self.start=start
        self.thing(1,start,angle=90)
        # This is a map pack. These are base-game slots for later RF2 replacements.
        if n!=23:
            self.place_near(2001,(start[0]+1,start[1]))  # shotgun
            self.place_near(2002,(start[0]-1,start[1]))  # automatic weapon slot
            self.place_near(2048,(start[0],start[1]+1))
            self.place_near(2049,(start[0],start[1]-1))
            self.place_near(2018,(start[0]+2,start[1]))
        distances=self.reachable(start,keys=False)
        # Authored side destination, separated from the final door: a real return loop.
        ri=self.spec['key_index'];x,y,w,h=rooms[ri]
        assert ri!=self.exit_room
        self.key_room=ri;self.key_cell=self.place_near(5,(x+w//2-2,y-h//2+2))
        for s,p in enumerate(self.secret_centres):
            if n!=23:
                self.place_near(2013 if s==0 else 2019,p)
                self.place_near(2048,(p[0]+1,p[1]))
        for i,(x,y,w,h) in enumerate(rooms):
            if i==0 or n==23:continue
            self.place_near(2048,(x,y))
            self.place_near(2049,(x+1,y))
            self.place_near(2012 if i%3==0 else 2011,(x-1,y))
            if i in (3,6):self.place_near(2018,(x,y-1))
            if n==23:continue  # Explicit quiet epilogue, no waiting-room combat.
            easy=[3004,3001,9,3002][(i+n)%4]
            spots=[(x-w//2+2,y+1),(x+w//2-2,y-1),(x+1,y+h//2-2),(x-1,y-h//2+2),(x+2,y+2),(x-2,y-2)]
            for j,p in enumerate(spots):
                type=easy if j<2 else ([3001,9,58,69][(i+n+j)%4])
                if j==5 and n>=7:type=66
                self.place_near(type,p,1 if j<2 else (2 if j<4 else 3),24)
            if i==ri and n>=10:self.place_near(69,(x+2,y-2),1,24)
            if i==4:self.place_near(82,(x,y+1))
        # No RPG, railgun, Doom boss or replacement FAL is silently invented here.

    def reachable(self,start,keys=True):
        q=deque([start]);dist={start:0}
        while q:
            p=q.popleft();a=self.cells[p]
            for dx,dy in DIRS:
                v=(p[0]+dx,p[1]+dy);b=self.cells.get(v)
                if b is None or v in dist:continue
                if b[8] in ('obstacle','pillar') or a[8] in ('obstacle','pillar'):continue
                if b[8]=='door' and b[6]==100 and not keys:continue
                if b[8]!='door' and b[5]-b[4]<56:continue
                if abs(b[4]-a[4])>24:continue
                dist[v]=dist[p]+1;q.append(v)
        return dist

    def build(self):
        for i,r in enumerate(self.spec['rooms']):self.room(i,r)
        for a,b in self.spec['links']:
            x1,y1,*_=self.spec['rooms'][a];x2,y2,*_=self.spec['rooms'][b]
            elbow=(x2,y1) if (a+b)%2 else (x1,y2)
            self.path([(x1,y1),elbow,(x2,y2)],3)
        self.relief();self.add_exit();self.add_secrets();self.populate()
        return self

    def geometry(self):
        self.sectors=[];self.sector_cells=[];assignment={}
        for p in sorted(self.cells):
            if p in assignment:continue
            d=self.cells[p];idx=len(self.sectors);q=[p];component=[];assignment[p]=idx
            while q:
                u=q.pop();component.append(u)
                for dx,dy in DIRS:
                    v=(u[0]+dx,u[1]+dy)
                    if v not in assignment and self.cells.get(v)==d:assignment[v]=idx;q.append(v)
            wall,floor,ceil,light,z,h,tag,special,role=d
            self.sectors.append(dict(heightfloor=z,heightceiling=h,texturefloor=floor,textureceiling=ceil,lightlevel=light,id=tag,special=special))
            self.sector_cells.append(component)
        verts=[];vindex={};sides=[];lines=[];edges={}
        def vertex(p):
            if p not in vindex:vindex[p]=len(verts);verts.append(dict(x=p[0]*UNIT,y=p[1]*UNIT))
            return vindex[p]
        for (x,y),si in sorted(assignment.items()):
            corners=[(x,y),(x,y+1),(x+1,y+1),(x+1,y)]
            ns=[(-1,0),(0,1),(1,0),(0,-1)]
            for j,(dx,dy) in enumerate(ns):
                other=(x+dx,y+dy);oi=assignment.get(other)
                if oi==si:continue
                a,b=corners[j],corners[(j+1)%4];key=tuple(sorted([a,b]));d=self.cells[x,y]
                texture=d[0];action=self.wall_actions.get(((x,y),(dx,dy)))
                if action:texture='RFEXIT'
                elif oi is None and (x+y)%41==0:texture='RFERR'
                side=dict(sector=si,texturemiddle=texture if oi is None else '-',texturetop=texture,texturebottom=texture,offsetx=(x if dx==0 else y)*UNIT%128)
                if action:side['offsetx']=0
                sid=len(sides);sides.append(side)
                if key in edges:
                    li=edges[key];lines[li]['sideback']=sid;lines[li]['twosided']=True
                    assert not lines[li].get('blocking'),(key,'blocked twin')
                else:
                    line=dict(v1=vertex(a),v2=vertex(b),sidefront=sid)
                    if oi is None:line['blocking']=True
                    if action:line.update(action)
                    dd=self.cells.get(other)
                    door=d if d[8]=='door' else dd if dd and dd[8]=='door' else None
                    if door and oi is not None:
                        tag=door[6];lock=self.doors[tag]['lock']
                        line.update(special=13 if lock else 12,arg0=tag,arg1=16,arg2=150,playeruse=True,repeatspecial=True)
                        if lock:line['arg3']=lock
                        if not lock:line['secret']=True
                        sides[sid]['texturetop']='RFDOORB' if lock else self.base[0]
                    edges[key]=len(lines);lines.append(line)
        # Door textures must be correct on both sides.
        for line in lines:
            if line.get('special') in (12,13):
                for k in ('sidefront','sideback'):
                    if k in line:sides[line[k]]['texturetop']='RFDOORB' if line['special']==13 else self.base[0]
        self.vertices=verts;self.sides=sides;self.lines=lines;self.assignment=assignment
        def emit(kind,d):
            def val(v):
                if isinstance(v,bool):return str(v).lower()
                if isinstance(v,str):return json.dumps(v)
                return str(v)
            return kind+'\n{\n'+''.join(f'  {k} = {val(v)};\n' for k,v in d.items())+'}\n'
        out='// RF2 original map. Canonical editable source.\nnamespace = "zdoom";\n\n'
        for kind,items in [('vertex',verts),('sector',self.sectors),('sidedef',sides),('linedef',lines),('thing',self.things)]:
            out+='\n'.join(emit(kind,d) for d in items)+'\n'
        return out

    def validate(self):
        no=self.reachable(self.start,False);yes=self.reachable(self.start,True)
        errors=[]
        if self.key_cell not in no:errors.append('Blue key inaccessible before door')
        if self.exit_approach in no:errors.append('Exit accessible without blue key')
        if self.exit_approach not in yes:errors.append('Exit unreachable after blue key')
        for p in self.secret_centres:
            if p not in yes:errors.append(f'Secret unreachable {p}')
        for t in self.things:
            p=(t['x']//UNIT,t['y']//UNIT)
            if p not in yes:errors.append(f'Unreachable thing {t["type"]} at {p}')
        for lm in self.landmarks:
            if tuple(lm['cell']) not in yes:errors.append(f'Room centre unreachable {lm["name"]}')
        if sum(t['type']==1 for t in self.things)!=1:errors.append('Player start count')
        return dict(code=self.spec['code'],errors=errors,vertices=len(self.vertices),linedefs=len(self.lines),sectors=len(self.sectors),things=len(self.things),
                    enemies={str(skill):sum(t['type'] in MONSTERS and t[f'skill{skill}'] for t in self.things) for skill in (2,3,4)},
                    secrets=2,blue_key=self.key_cell,start=self.start,exit=self.exit_approach,
                    key_room=self.spec['labels'][self.key_room],reachable_cells=len(yes),
                    exit_distance_cells=no.get(self.key_cell,0)+yes.get(self.exit_approach,0),
                    rooms=len(self.landmarks))

def wad(code,text):
    lumps=[(code,b''),('TEXTMAP',text.encode()),('ENDMAP',b'')]
    out=bytearray(b'PWAD'+struct.pack('<ii',len(lumps),0));directory=[]
    for name,data in lumps:
        directory.append(struct.pack('<ii8s',len(out),len(data),name.encode().ljust(8,b'\0')));out.extend(data)
    struct.pack_into('<i',out,8,len(out));out.extend(b''.join(directory));return bytes(out)

def svg(m):
    cells=m.cells;minx=min(p[0] for p in cells)-3;maxx=max(p[0] for p in cells)+4;miny=min(p[1] for p in cells)-3;maxy=max(p[1] for p in cells)+4
    scale=11;w=(maxx-minx)*scale;h=(maxy-miny)*scale+100
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="#11191e"/>',f'<text x="22" y="29" fill="#efddd0" font-family="sans-serif" font-size="17">{m.spec["code"]} / {html.escape(m.spec["title"])}</text>']
    def xy(p):return ((p[0]-minx)*scale,58+(maxy-p[1]-1)*scale)
    for p,d in cells.items():
        x,y=xy(p)
        color='#757369' if d[2]=='F_SKY1' else '#52636a'
        if d[4]<0:color='#38616c'
        if d[4]>0:color='#858178'
        if d[8] in ('obstacle','pillar'):color='#222a2b'
        if d[8]=='door':color='#498dda' if d[6]==100 else '#b17d4b'
        if d[7]==1024:color='#916e44'
        out.append(f'<rect x="{x}" y="{y}" width="{scale+.2}" height="{scale+.2}" fill="{color}"/>')
    for lm in m.landmarks:
        x,y=xy(lm['cell']);label=str(lm['index']+1)
        out.append(f'<circle cx="{x+5}" cy="{y+5}" r="10" fill="#172127" stroke="#dfb8a0"/><text x="{x+5}" y="{y+9}" text-anchor="middle" fill="white" font-size="10" font-family="sans-serif">{label}</text>')
    for p,label,c in [(m.start,'S','#79dc9a'),(m.key_cell,'K','#72b4f0'),(m.exit_approach,'E','#ef665b')]:
        x,y=xy(p);out.append(f'<text x="{x-7}" y="{y-9}" fill="{c}" font-size="18" font-weight="bold" font-family="sans-serif">{label}</text>')
    out.append(f'<text x="22" y="{h-12}" fill="#9daeb1" font-family="sans-serif" font-size="11">PLAN DE GEOMETRIE / S depart - K badge bleu - E sortie / pas une capture du jeu</text></svg>')
    return '\n'.join(out)

def pack():
    target=ROOT/'build/RF2_MAPS_V1.pk3'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for base in ('resources','maps'):
            for p in sorted((ROOT/base).rglob('*')):
                if p.is_file():
                    name=p.relative_to(ROOT/'resources') if base=='resources' else p.relative_to(ROOT)
                    info=zipfile.ZipInfo(str(name).replace('\\','/'),(2026,9,23,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                    z.writestr(info,p.read_bytes())
    return target

def main():
    allreports=[];allmeta=[]
    for spec in campaign():
        m=Map(spec).build();text=m.geometry();report=m.validate()
        if report['errors']:raise ValueError(report)
        p=ROOT/'src'/spec['code'];p.mkdir(parents=True,exist_ok=True)
        (p/'TEXTMAP').write_text(text,encoding='utf-8')
        (ROOT/'maps'/f'{spec["code"]}.wad').write_bytes(wad(spec['code'],text))
        (ROOT/'previews'/f'{spec["code"]}.svg').write_text(svg(m),encoding='utf-8')
        meta=dict(**spec,landmarks=m.landmarks,key_room=report['key_room'])
        (p/'layout.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        allreports.append(report);allmeta.append(meta)
        print(spec['code'],len(m.lines),'lines',report['enemies'],'enemies')
    (ROOT/'evidence/STATIC_VALIDATION.json').write_text(json.dumps(allreports,indent=2),encoding='utf-8')
    (ROOT/'docs/CAMPAIGN.json').write_text(json.dumps(allmeta,ensure_ascii=False,indent=2),encoding='utf-8')
    p=pack();print(p,hashlib.sha256(p.read_bytes()).hexdigest())

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regenerate',action='store_true',help='Overwrite all maps and TEXTMAPs from the V1 arrangement')
    args=parser.parse_args()
    if (ROOT/'src/RF01/TEXTMAP').exists() and not args.regenerate:
        parser.error('Sources already exist. Use repack.py after editing, or --regenerate to discard manual geometry edits.')
    main()
