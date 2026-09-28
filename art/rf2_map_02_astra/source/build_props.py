"""Original RF02 geometry. Blender 5.2 --background --python build_props.py.
Units: proposed game units; +Z up, object front -Y. No active repository writes.
The renders named view_NNN are geometric azimuth samples, NOT assigned Doom rotations.
"""
from pathlib import Path
import bpy, math, json, sys, hashlib
from mathutils import Vector
from math import sin, cos, pi
HERE=Path(__file__).resolve().parent
LOT=HERE.parent
OUT=HERE/'models'; OUT.mkdir(exist_ok=True)
REN=HERE/'renders'; REN.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=640; scene.render.resolution_y=640; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'
scene.world.color=(.35,.35,.35)
atlas=bpy.data.images.load(str(HERE/'masters/RF2_MATERIAL_ATLAS.png')); atlas.pack()
TILES={'wood':0,'leather':1,'zinc':2,'iron':3,'green':4,'ivory':5,'canvas':6,'paper':7,'brass':8,'rubber':9,'wicker':10,'bakelite':11,'ticking':12,'grille':13,'plastic':14,'rope':15}
MATS={}
for name,i in TILES.items():
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.66
    bs.inputs['Metallic'].default_value=.65 if name in ('zinc','iron','brass') else 0
    tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas
    m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);MATS[name]=m
def flat(name,col,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1)
    b.inputs['Roughness'].default_value=.6
    if emission:b.inputs['Emission Color'].default_value=(*col,1);b.inputs['Emission Strength'].default_value=emission
    return m
MATS['dial']=flat('dial amber',(.46,.24,.055),.5)
MATS['ember']=flat('ember',(.52,.025,.003),2)
MATS['screen']=flat('CRT blue',(.035,.12,.40),.7)
MATS['red']=flat('muted red',(.3,.018,.01))
MATS['white']=flat('chalk',(.75,.72,.6))
MATS['black']=flat('black',(.006,.008,.009))
COL=None
def adopt(o,name,mat):
    o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o)
    o.data.materials.append(MATS[mat]);o['rf_mat']=mat
    return o
def box(name,pos,size,mat,bevel=.15):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=adopt(bpy.context.object,name,mat);o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('constructed rounded edges','BEVEL');mod.width=bevel;mod.segments=3
        mod=o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o
def cyl(name,a,b,r,mat,r2=None,n=24):
    a,b=Vector(a),Vector(b);v=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=v.length,location=(a+b)/2)
    o=adopt(bpy.context.object,name,mat);o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    mod=o.modifiers.new('rim softened','BEVEL');mod.width=min(.09,r*.13);mod.segments=2
    for p in o.data.polygons:p.use_smooth=True
    return o
def ell(name,pos,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=pos)
    o=adopt(bpy.context.object,name,mat);o.scale=Vector(size)/2
    for p in o.data.polygons:p.use_smooth=True
    return o
def line(name,points,r,mat,closed=False):
    cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.resolution_u=2;cv.bevel_depth=r;cv.bevel_resolution=2
    s=cv.splines.new('POLY');s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    s.use_cyclic_u=closed
    o=bpy.data.objects.new(name,cv);COL.objects.link(o);cv.materials.append(MATS[mat]);o['rf_mat']=mat;return o
def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);COL.objects.link(o);me.materials.append(MATS[mat]);o['rf_mat']=mat;return o
def txt(body,pos,size,mat='white',rot=(pi/2,0,0)):
    cv=bpy.data.curves.new('typeset '+body,'FONT');cv.body=body;cv.size=size;cv.align_x='CENTER';cv.extrude=.005
    o=bpy.data.objects.new('text '+body,cv);COL.objects.link(o);o.location=pos;o.rotation_euler=rot;cv.materials.append(MATS[mat]);o['rf_mat']=mat;return o
def ring(name,center,rx,ry,r,mat,zplane=True):
    x,y,z=center
    pts=[(x+rx*cos(a),y+ry*sin(a),z) if zplane else (x+rx*cos(a),y,z+ry*sin(a)) for a in [2*pi*k/48 for k in range(48)]]
    return line(name,pts,r,mat,True)
def book(x,y,z,w=9,d=7,h=2,mat='green'):
    box('paper block',(x,y,z+h/2),(w-.4,d-.4,h-.25),'paper',.1)
    for zz in (z+.1,z+h-.1):box('register cover',(x,y,zz),(w,d,.2),mat,.08)
    box('cloth spine',(x-w/2,y,z+h/2),(.45,d,h),mat,.16)
    for xx in (x-w*.25,x+w*.25):
        line('hemp register tie',[(xx,y-d/2-.12,z-.06),(xx,y+d/2+.12,z-.06),(xx,y+d/2+.12,z+h+.1),(xx,y-d/2-.12,z+h+.1)],.11,'rope',True)
    line('cross tie',[(x-w/2-.12,y,z),(x+w/2+.12,y,z),(x+w/2+.12,y,z+h+.15),(x-w/2-.12,y,z+h+.15)],.1,'rope',True)
    ell('knot',(x,y,z+h+.23),(.8,.5,.4),'rope')
def pram():
    for x in (-13,13):
        cyl('axle',(x,-15,7),(x,15,7),.55,'iron')
        for y in (-14,14):
            ring('rubber tyre',(x,y,7),6.6,6.6,.55,'rubber',False)
            ring('steel rim',(x,y,7),6.1,6.1,.32,'zinc',False)
            cyl('hub',(x,y-1,7),(x,y+1,7),1,'iron')
            for k in range(16):
                a=k*pi/8;cyl('thin spoke',(x,y,7),(x+6*cos(a),y,7+6*sin(a)),.12,'zinc',n=8)
    for y in (-10,10):
        line('bow spring',[(-17+34*k/20,y,10+5*sin(pi*k/20)) for k in range(21)],.45,'iron')
        for x in (-13,13):cyl('frame stay',(x,y,7),(x*.65,y,17),.55,'iron')
    # Oval tub with inside, outer shell and rolled edge. No solid block pretending to be wheels.
    vs=[]
    for z,rx,ry in ((15,16,9),(25,20,12),(24.4,18.9,10.9),(16.2,15,8)):
        vs += [(rx*cos(k*pi/24),ry*sin(k*pi/24),z) for k in range(48)]
    fs=[]
    for level in range(3):
        for k in range(48):fs.append((level*48+k,level*48+(k+1)%48,(level+1)*48+(k+1)%48,(level+1)*48+k))
    fs.append(tuple(range(144,192)))
    mesh('wicker carriage shell with interior',vs,fs,'wicker')
    ring('rolled tub rim',(0,0,25),20,12,.6,'leather')
    # Rear canopy: hoops and cloth form a quarter cylinder over the rear half.
    verts=[]
    for x in (-19,-16,-13,-10,-7):
        for k in range(25):
            a=k*pi/24;verts.append((x,11*cos(a),25+12*sin(a)))
    faces=[]
    for j in range(4):
        for k in range(24):a=j*25+k;faces.append((a,a+1,a+26,a+25))
    ob=mesh('folded hood canvas',verts,faces,'canvas');mo=ob.modifiers.new('canvas thickness','SOLIDIFY');mo.thickness=.17
    for x in (-19,-13,-7):line('hood bow',[(x,11*cos(k*pi/24),25+12*sin(k*pi/24)) for k in range(25)],.22,'iron')
    for y in (-10,10):line('handle riser',[(-13,y,7),(-23,y,26),(-26,y,33)],.6,'iron')
    cyl('wood push handle',(-26,-10,33),(-26,10,33),.8,'wood')
    for x,y,z,w,d,h,m in ((0,0,17,21,12,3,'green'),(0,0,20,20,12,3,'leather'),(1,0,23,21,13,4,'green'),(2,0,27,19,12,3,'canvas')):book(x,y,z,w,d,h,m)
def bucket():
    vs=[]
    for z,r in ((.4,5.4),(13,7.4),(13,6.95),(1,5.05)):
        vs += [(r*cos(k*pi/24),r*sin(k*pi/24),z) for k in range(48)]
    fs=[]
    for j in range(3):
        for k in range(48):fs.append((j*48+k,j*48+(k+1)%48,(j+1)*48+(k+1)%48,(j+1)*48+k))
    fs.append(tuple(range(144,192)));fs.append(tuple(reversed(range(48))))
    mesh('galvanized sheet body double wall',vs,fs,'zinc')
    for z,r in ((.6,5.5),(11.8,7.3),(13,7.4)):ring('rolled galvanized lip',(0,0,z),r,r,.18,'zinc')
    for x in (-7.4,7.4):ell('handle ear',(x,0,11),(1,.7,1.6),'iron')
    line('wire bail',[(7.5*cos(k*pi/32),0,11+9*sin(k*pi/32)) for k in range(33)],.22,'iron')
    for i in range(7):
        o=box('charred form',(sin(i*2)*1.6,cos(i*3)*1.6,7+i*.5),(4.8,3.2,.1),'paper' if i%3 else 'iron',.03);o.rotation_euler=(.08*i,.06*i,.75*i)
    for i in range(5):ell('ember',((i-2)*1.1,.2,10.2),(.6,.9,.22),'ember')
def satchel():
    box('stitched leather satchel',(0,0,10),(19,7,16),'leather',1.1)
    box('closing leather flap',(0,-3.8,15),(19,.7,7),'leather',.8)
    for x in (-6,6):
        box('retaining strap',(x,-4.25,10),(1.6,.45,12),'leather',.18)
        line('brass buckle',[(x-1,-4.55,9),(x+1,-4.55,9),(x+1,-4.55,11.5),(x-1,-4.55,11.5)],.17,'brass',True)
    line('long leather suspension strap',[(-8,0,16),(-10,0,27),(-5,0,35),(0,0,37),(5,0,35),(10,0,27),(8,0,16)],.6,'leather')
    for x in range(-8,9):
        cyl('flap stitch',(x,-4.23,12),(x+.3,-4.23,12),.055,'rope',n=6)
def radio(lit=False):
    box('walnut cabinet',(0,0,10),(28,11,20),'wood',1.4)
    box('front bevel border',(0,-5.4,10),(25,.7,17),'brass',.65)
    box('speaker grille',(0,-5.83,13),(22,.22,10),'grille',.55)
    for x in (-9,-5,-1,3,7):box('carved speaker bar',(x,-6,13),(.65,.5,10),'wood',.25)
    box('station dial surround',(0,-5.9,5.2),(14,.4,3.3),'bakelite',.35)
    box('dial glass',(0,-6.15,5.3),(12.8,.1,2.4),'dial' if lit else 'paper',.2)
    for x in range(-5,6):box('station scale',(x,-6.23,5.4),(.055,.03,.55 if x%2 else .9),'iron',0)
    box('dial needle',(2,-6.27,5.4),(.09,.04,1.7),'red',0)
    for x in (-10,10):cyl('Bakelite control',(x,-5.7,3.6),(x,-7,3.6),1.5,'bakelite')
    for x in (-10,10):
        for y in (-3,3):box('cabinet foot',(x,y,.5),(3,3,1),'rubber',.3)
    box('rear fiberboard',(0,5.5,10),(25,.25,16),'canvas',.2)
    for x in range(-10,11,2):box('rear vent',(x,5.7,12),(.5,.15,9),'iron',.1)
    line('mains flex',[(7,5.8,2),(9,9,1),(3,11,.7),(-3,9,.7)],.23,'rubber')
def phone():
    box('field telephone case',(0,0,5.5),(20,13,11),'green',.65)
    box('open lid',(0,7.1,13),(20,1,15),'green',.6)
    box('lid inner plate',(0,6.5,13),(16,.25,11),'iron',.3)
    for x in (-7,7):cyl('handset earpiece',(x,-2,13),(x,-2,15.1),2.4,'bakelite',r2=2.8)
    line('handset handle',[(-7,-2,14.5),(-5,-2,16),(5,-2,16),(7,-2,14.5)],.85,'bakelite')
    for x in (-7,7):box('cradle',(x,-2,11.5),(3,3,2),'iron',.4)
    # crank on right side; cord has actual curled geometry, not painted on the case.
    line('magneto crank',[(10,0,6),(12,0,6),(12,0,9),(14,0,9)],.35,'iron')
    cyl('crank grip',(14,-1.3,9),(14,1.3,9),.6,'bakelite')
    line('handset cord',[(9+cos(k*.8)*.5,-4+sin(k*.8)*.5,13-k*.085) for k in range(110)],.14,'rubber')
    for x in (-5,5):cyl('line binding post',(x,3,11),(x,3,12),.55,'brass')
    for x in (-8,8):box('strap loop',(x,-6.7,7),(2,.5,2),'brass',.2)
    line('carrying strap',[(-10,1,7),(-13,0,2),(-9,-5,1),(10,-7,1),(13,0,7),(10,1,7)],.55,'leather')
    # Canon Ø is on the UNDERSIDE only.
    txt('Ø',(0,0,-.035),2.5,'black',rot=(pi,0,0))
def suitcase(opened=True):
    box('suitcase shell',(0,0,3.5),(34,22,7),'leather',1.3)
    box('inner lining',(0,0,7),(31,19,.7),'canvas',.8)
    if opened:
        box('open upright lid',(0,10.5,16.5),(34,2,22),'leather',1)
        box('lid lining',(0,9.3,16.5),(30,.5,18),'canvas',.7)
        for x in (-12,12):line('lid restraint',[(x,6,7),(x,9,18)],.18,'leather')
    else:box('closed lid',(0,0,8.5),(34,22,4),'leather',1)
    for x in (-11,11):
        box('brass latch',(x,-11.3,5),(2.8,.5,3),'brass',.3)
        for z in (2,8):box('corner reinforcement',(x*1.45,-9,z),(2.2,4,1),'leather',.5)
    line('handle',[(-4,-11.8,5),(-4,-14,5),(4,-14,5),(4,-11.8,5)],.65,'leather')
    if opened:
        for i in range(4):
            x=-10+i*6.8;y=-1+(i%2)*3
            # Tissue around each worn shoe; different low-heeled shoes, no Jerma side-buckle copy.
            box('wrapping paper',(x,y,7.7),(6,13,.2),'paper',.6)
            ell('worn shoe upper',(x,y,9),(4.8,10,3.3),'leather' if i%2 else 'bakelite')
            ell('shoe opening',(x,y+2,10.5),(3,4,.4),'black')
            box('heel',(x,y+3.3,8.7),(3,2,2),'rubber',.5)
def mattress():
    box('striped mattress',(0,0,4),(90,43,8),'ticking',2.4)
    for z in (1,7):line('piping',[(-43,-20,z),(43,-20,z),(43,20,z),(-43,20,z)],.28,'rope',True)
    for x in (-30,-10,10,30):
        for y in (-12,0,12):ell('tuft',(x,y,7.9),(1.4,1.4,.3),'canvas')
    line('dragging rope',[(-44,0,4),(-51,0,2),(-59,3,.3),(-65,2,.3)],.55,'rope')
def amiga():
    box('A1200 integrated keyboard case',(0,0,1.8),(36,19,3.6),'plastic',.7)
    # main block 5 rows, separate numpad and long space bar, keyboard integrated in low sloping case.
    for row in range(5):
        for col in range(13):
            x=-15+col*1.8;y=-7+row*2.1;z=3.2+(y+7)*.09
            box('keycap',(x,y,z),(1.55,1.65,.6),'ivory',.15)
    box('space bar',(-6,-8,3.1),(13,1.4,.6),'ivory',.15)
    for row in range(4):
        for col in range(4):box('numeric keypad',(9+col*1.9,-7+row*2.1,3.4),(1.6,1.7,.6),'ivory',.15)
    for x in range(-15,17):box('rear ventilation',(x,6,3.66),(.38,3,.05),'iron',0)
    box('floppy slot',(18.01,1.5,1.9),(.1,7,.6),'black',.05)
    txt('AMIGA',(10,5,3.8),1.2,'red',rot=(0,0,0))
    box('CRT pedestal',(0,19,2),(12,9,4),'plastic',.9)
    box('CRT casing',(0,20,13),(26,22,21),'plastic',1.6)
    box('CRT bezel',(0,8.6,14),(23,1,17),'ivory',1)
    box('CRT blue screen',(0,7.95,14),(20,.3,14),'screen',1)
    # Deliberate primitive pointer and line plan of a hotel, no invented fake OS paragraphs.
    mesh('screen pointer',[(-7,7.73,18),(-7,7.73,15),(-5,7.73,16)],[(0,1,2)],'white')
    for x in (-4,0,4):line('hotel plan',[(x,7.7,10),(x,7.7,17),(x+3,7.7,17),(x+3,7.7,10)],.065,'white')
    box('shoebox',(26,10,3),(12,20,6),'paper',.2)
    for i in range(8):
        box('floppy disk',(26,4+i*1.5,7),(9,.5,9),'iron',.2)
        box('disk label',(26,3.7+i*1.5,8),(7,.08,4),'paper',.1)

BUILDERS={'pram':pram,'bucket':bucket,'satchel':satchel,'radio_off':radio,'radio_on':lambda:radio(True),'phone':phone,'suitcase':suitcase,'mattress':mattress,'amiga':amiga}
def uv_mesh(o):
    # Make all procedural geometry explicit and freeze modifiers before UV/export.
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    o=bpy.context.object
    key=o.get('rf_mat','iron');tile=TILES.get(key,3)
    uv=o.data.uv_layers.new(name='RF2_material_tiles') if not o.data.uv_layers else o.data.uv_layers.active
    pts=[v.co for v in o.data.vertices];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)]
    for poly in o.data.polygons:
        major=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=major]
        for li in poly.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            u,v=[(co[a]-lo[a])/max(.001,hi[a]-lo[a]) for a in axes]
            uv.data[li].uv=((tile%4+.035+.93*u)/4,(3-tile//4+.035+.93*v)/4)
    return o
def export_obj(coll,dest):
    # UZDoom OBJ coordinates Y-up. Exact conversion inverse: x=X,y=-Z,z=Y.
    rows=['# RF2 original mesh. OBJ Y-up; one packed atlas. Proposed game units.'];vi=1;ti=1
    for o in coll.objects:
        if o.type!='MESH':continue
        rows.append('o '+o.name.replace(' ','_'))
        for v in o.data.vertices:
            p=o.matrix_world@v.co;rows.append(f'v {p.x:.6f} {p.z:.6f} {-p.y:.6f}')
        uv=o.data.uv_layers.active
        for lp in o.data.loops:
            u,v=uv.data[lp.index].uv;rows.append(f'vt {u:.7f} {v:.7f}')
        for poly in o.data.polygons:
            ids=list(poly.loop_indices)
            for k in range(1,len(ids)-1):
                tr=[ids[0],ids[k],ids[k+1]];rows.append('f '+' '.join(f'{vi+o.data.loops[l].vertex_index}/{ti+l}' for l in tr))
        vi+=len(o.data.vertices);ti+=len(o.data.loops)
    dest.write_text('\n'.join(rows)+'\n',encoding='utf8')
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-150,90));cam=bpy.context.object;cam.name='Review camera';cam.data.type='ORTHO';scene.camera=cam
lights=[]
for loc,power,size in [((-50,-80,100),110000,90),((65,-20,60),60000,70),((0,70,90),95000,70)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,(0,0,15));lights.append(o)
metadata=[]
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(BUILDERS)
for name in names:
    if name not in BUILDERS:continue
    COL=bpy.data.collections.new(name);scene.collection.children.link(COL);BUILDERS[name]()
    for o in list(COL.objects):uv_mesh(o)
    for c in scene.collection.children:
        if c.name in BUILDERS:c.hide_render=c!=COL
    bpy.context.view_layer.update()
    coords=[o.matrix_world@v.co for o in COL.objects if o.type=='MESH' for v in o.data.vertices]
    lo=Vector([min(v[k] for v in coords) for k in range(3)]);hi=Vector([max(v[k] for v in coords) for k in range(3)])
    ctr=(lo+hi)/2;span=max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z)
    cam.data.ortho_scale=span*1.4
    render_dir=REN/name;render_dir.mkdir(exist_ok=True)
    record={'name':name,'bounds_min':list(lo),'bounds_max':list(hi),'dimensions_units':list(hi-lo),'anchor':[0,0,0],'front':'-Y','up':'+Z','obj_axes':'X, Z, -Y','ortho_scale':cam.data.ortho_scale,'views':[]}
    # Neutral review front plus 8 azimuth samples from this same master.
    for angle in range(0,360,45):
        a=math.radians(angle);cam.location=ctr+Vector((sin(a)*140,-cos(a)*140,68));point(cam,ctr)
        dst=render_dir/f'view_{angle:03}.png';scene.render.filepath=str(dst);bpy.ops.render.render(write_still=True)
        record['views'].append({'azimuth_degrees':angle,'file':str(dst.relative_to(LOT)).replace('\\','/'),'camera':list(cam.location),'target':list(ctr)})
    export_obj(COL,OUT/f'{name}.obj')
    bpy.ops.object.select_all(action='DESELECT')
    for o in COL.objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/f'{name}.glb'),export_format='GLB',use_selection=True)
    metadata.append(record)
    (OUT/f'{name}.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    print('RF2_MODEL_DONE',name,flush=True)
if metadata:
    atlas.pack();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'RF2_PROPS_MASTER.blend'))
    (OUT/'catalogue.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
print('RF2_GEOMETRY_COMPLETE',flush=True)
