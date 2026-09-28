"""Parked old Paris tram adaptation. Source geometry, not a certified vehicle reconstruction.
Requires Opus contract for new physical envelope, walkable floor and door/collision alignment.
"""
import importlib.util,sys,math,json
from pathlib import Path
from mathutils import Vector
import bpy
HERE=Path(__file__).resolve().parent
sys.argv=[__file__,'--','library']
spec=importlib.util.spec_from_file_location('props_lib',HERE/'build_props.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
scene=P.scene;OUT=HERE/'models';REN=HERE/'renders'
COL=bpy.data.collections.new('tram');scene.collection.children.link(COL);P.COL=COL
B=P.box;C=P.cyl;L=P.line
# Physical proposal: 330 x 90 u, floor 30 u, roof 113 u, 68 u internal aisle height.
B('riveted chassis',(0,0,24),(316,70,5),'iron',1)
for y in (-28,28):B('chassis beam',(0,y,20),(294,4,8),'iron',.5)
for x in (-88,88):
    C('axle',(x,-34,12),(x,34,12),2.2,'iron')
    for y in (-30,30):
        C('steel running wheel',(x,y-2,12),(x,y+2,12),12,'iron',n=48)
        inner=1 if y<0 else -1
        C('running flange',(x,y+inner*1.6,12),(x,y+inner*2.6,12),12.7,'iron',n=48)
        C('axle cap',(x,y-3.1,12),(x,y+3.1,12),4.1,'zinc')
        B('bearing box',(x,y,14),(10,7,8),'iron',1)
        for k in range(4):L('laminated leaf spring',[(x-16+32*j/16,y,20+k*.45-4*math.sin(math.pi*j/16)) for j in range(17)],.35,'iron')
for y in (-27,27):
    for x in (-45,45):C('brake pull rod',(x-28,y,15),(x+28,y,15),.55,'iron')
B('passenger floor',(0,0,28.5),(330,84,3),'wood',.3)
for x in range(-156,157,12):B('floor plank seam',(x,0,30.05),(.12,82,.1),'iron',0)
# Center saloon; end platforms left open, retaining railings leave stair apertures clear.
for y in (-42,42):
    B('lower saloon body',(0,y,45),(230,3,30),'green',.6)
    B('cream waist stripe',(0,y*1.006,58),(230,3.1,4),'ivory',.25)
    B('upper clerestory rail',(0,y,102),(234,4,12),'ivory',.6)
    for x in (-116,-78,-39,0,39,78,116):
        B('window mullion',(x,y,80),(3.5,4,42),'wood',.3)
    for x in (-97,-58.5,-19.5,19.5,58.5,97):
        B('lowered sash frame',(x,y,63),(33,3,2),'wood',.3)
    B('long bench seat',(0,y*.76,47),(224,15,3),'wood',.9)
    B('long bench back',(0,y*.90,57),(224,2,18),'wood',.8)
    for x in (-90,-45,0,45,90):
        C('seat leg',(x,y*.64,30),(x,y*.64,46),.8,'iron')
        B('bench slat join',(x,y*.76,48.6),(.16,14,.1),'iron',0)
for x in (-117,117):
    for y in (-32,32):
        B('saloon end panel',(x,y,49),(3,20,38),'green',.4)
        B('saloon end window post',(x,y,80),(3,3,61),'wood',.3)
    B('saloon end lintel',(x,0,102),(4,86,12),'ivory',.5)
    # Two sliding leaves visibly OPEN against the side panels; central aisle remains free.
    for y in (-34,34):B('open sliding door leaf',(x+(1 if x>0 else -1)*2,y,67),(1.5,15,70),'wood',.3)
for x in (-160,160):
    B('curved end apron',(x,0,48),(4,83,36),'green',1.2)
    B('end waist stripe',(x,0,65),(4.3,84,4),'ivory',.5)
    for y in (-40,40):C('platform corner stanchion',(x,y,30),(x,y,106),1.3,'ivory')
    C('brass grab rail',(x,-40,70),(x,40,70),.85,'brass')
    C('controller column',(x*.9,0,30),(x*.9,0,55),3.7,'iron')
    C('controller shaft',(x*.9,0,55),(x*.9,0,61),1,'brass')
    C('controller lever',(x*.9,0,61),(x*.9,9,61),.75,'brass')
    for y in (-42,42):
        # Open end side doors/platform access and three connected steps.
        for j in range(3):B('boarding step',(x*.86,y+(1 if y>0 else -1)*(4+j*3),22-j*7),(34,8,2),'iron',.35)
        C('boarding handrail',(x*.74,y,31),(x*.74,y,94),.85,'brass')
    C('headlamp housing',(x,0,48),(x+(3 if x>0 else -3),0,48),6,'iron')
    C('headlamp frosted glass',(x+(3 if x>0 else -3),0,48),(x+(3.2 if x>0 else -3.2),0,48),5,'ivory')
    C('coupling bar',(x,0,20),(x+(12 if x>0 else -12),0,20),1.8,'iron')
# Arched roof shell covers saloon and both end platforms, with visible thickness.
verts=[]
for x in (-168,168):
    for i in range(25):
        y=-47+94*i/24;z=106+7*math.sqrt(max(0,1-(y/47)**2));verts.append((x,y,z))
faces=[(i,i+1,26+i,25+i) for i in range(24)]
roof=P.mesh('arched zinc roof',verts,faces,'zinc');mo=roof.modifiers.new('sheet thickness','SOLIDIFY');mo.thickness=1.2
for y in (-47,47):C('roof gutter',(-168,y,106),(168,y,106),.7,'iron')
for x in (-85,0,85):B('roof ventilator',(x,0,114),(24,14,4),'green',1)
C('trolley base',(0,0,114),(0,0,120),4.5,'iron')
C('lowered collector pole',(0,0,120),(137,0,133),.9,'iron')
C('collector shoe',(131,0,133),(145,0,133),1.9,'iron')
L('trolley retriever rope',[(142,0,133),(154,0,115),(160,0,75)],.22,'rope')
# Twelve individual period cases with seams, handle and latches; two stacks free the cage seat.
case_positions=[(-92,-31),(-55,-31),(-18,-31),(18,-31),(55,-31),(92,-31),(-92,31),(-55,31),(-18,31),(18,31),(-55,31),(18,31)]
for i,(x,y) in enumerate(case_positions):
    z=50+(14 if i>9 else 0)
    B('abandoned leather suitcase',(x,y,z+6),(26,12,12),'leather',1.2)
    for xx in (x-8,x+8):B('case brass latch',(xx,y-6.2,z+7),(2,.4,2),'brass',.2)
    L('case handle',[(x-4,y,z+12),(x-4,y,z+14),(x+4,y,z+14),(x+4,y,z+12)],.65,'leather')
# Wicker cage on the bench, two schematic hen volumes kept in source only pending a proper animal master.
B('cage wooden base',(78,31,50),(36,18,3),'wood',.5)
for x in range(61,97,4):
    for y in (23,39):C('cage vertical rod',(x,y,51),(x,y,70),.3,'wood',n=8)
for y in range(23,40,4):
    for x in (61,95):C('cage end rod',(x,y,51),(x,y,70),.3,'wood',n=8)
for z in (52,68,71):L('cage horizontal hoop',[(60,22,z),(96,22,z),(96,40,z),(60,40,z)],.45,'wood',True)
for x in range(61,97,4):C('cage top rod',(x,23,71),(x,39,71),.3,'wood',n=8)
# Source cage intentionally empty: do not label two crude ellipsoids as completed animals.
for o in list(COL.objects):P.uv_mesh(o)
P.export_obj(COL,OUT/'tram.obj')
bpy.ops.object.select_all(action='DESELECT')
for o in COL.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'tram.glb'),export_format='GLB',use_selection=True)
records=[]
cam=P.cam;cam.data.ortho_scale=430;scene.render.resolution_x=1280;scene.render.resolution_y=720
for o in P.lights:o.data.energy*=10;o.data.size*=2.8;o.location*=3
for angle in range(0,360,45):
    a=math.radians(angle);cam.location=(math.sin(a)*500,-math.cos(a)*500,245);P.point(cam,(0,0,59))
    d=REN/'tram';d.mkdir(exist_ok=True);p=d/f'view_{angle:03}.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    records.append({'azimuth':angle,'file':p.relative_to(P.LOT).as_posix()})
# Interior view, front and rear platforms both genuinely modeled.
cam.data.type='PERSP';cam.data.lens=22;cam.location=(-137,0,79);P.point(cam,(115,0,75));scene.render.filepath=str(d/'interior.png');bpy.ops.render.render(write_still=True)
COL.hide_render=True
TRACK=bpy.data.collections.new('track_straight');scene.collection.children.link(TRACK);P.COL=TRACK
for y in (-30,30):
    # Crown at z=0 to coordinate wheel contact. Flange grooves face the track center.
    B('rail foot',(0,y,-3),(256,4,1),'iron',.1)
    B('rail web',(0,y,-1.9),(256,1,2),'iron',.08)
    B('rail running head',(0,y,-.45),(256,2.2,.9),'zinc',.15)
    B('guard lip',(0,y+(-3 if y>0 else 3),-.8),(256,.65,1),'iron',.1)
for x in range(-120,121,24):
    B('buried sleeper',(x,0,-4),(6,82,2),'wood',.25)
    for y in (-30,30):
        B('rail chair',(x,y,-2.4),(8,7,1),'iron',.1)
        for yy in (y-2,y+2):C('rail chair bolt',(x,yy,-2.2),(x,yy,-1.1),.45,'iron',n=8)
for o in list(TRACK.objects):P.uv_mesh(o)
P.export_obj(TRACK,OUT/'track_straight.obj')
bpy.ops.object.select_all(action='DESELECT')
for o in TRACK.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'track_straight.glb'),export_format='GLB',use_selection=True)
cam.data.type='ORTHO';cam.data.ortho_scale=320;cam.location=(170,-200,200);P.point(cam,(0,0,0));scene.render.filepath=str(REN/'track_straight.png');bpy.ops.render.render(write_still=True)
TRACK.hide_render=True;COL.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'RF2_TRAM_MASTER.blend'))
(OUT/'tram_contract_proposal.json').write_text(json.dumps({'status':'SOURCE_REQUIRES_OPUS_CONTRACT','not_runtime_import':True,'source_units':'proposed game units','front':'-X end; +Z up','obj_axes':'X, Z, -Y','body_dimensions':[336,108,133],'floor_z':30,'roof_top_z':113,'wheel_running_radius':12,'flange_radius':12.7,'rail_head_z':0,'rail_centrelines_y':[-30,30],'rail_module_length':256,'flange_recess_depth_min':.7,'origin_world_proposal':[2192,232,0],'current_map_body_dimensions':[352,112,152],'current_map_floor_z':24,'current_collision_reusable':False,'case_count':12,'cage_count':1,'hens_produced':0,'old_man_produced':False,'required_integration':['replace existing solid body slabs','align walkable floor and platform steps','door openings/collision and actor reach','rail grooves below wheel flange','trolley pole and overhead wire strategy'],'views':records,'historical_scope':'Paris interwar tram evocation, not a measured or identified type. Novel requires parked tram in 1940 despite real network removal.'},ensure_ascii=False,indent=2),encoding='utf8')
print('TRAM_SOURCE_COMPLETE; integration and hens/old man remain',flush=True)
