"""Generate an offline, batch-local animation viewer. No server or network."""
from pathlib import Path
import json
import sys

TEMPLATE = '''<!doctype html>
<html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>__TITLE__ / revue des candidats</title>
<style>
body{margin:24px;background:#161e24;color:#eeeadd;font:16px system-ui}main{max-width:1100px;margin:auto}
h1{font-size:25px}p{line-height:1.55}label{display:inline-block;margin:0 14px 12px 0}select,button,input{font:inherit;padding:7px}
canvas{display:block;background:#dfdfd4;max-width:100%;height:auto;border:1px solid #5d6b70}#info{font:14px monospace}
</style><main><h1>__TITLE__ — revue des candidats</h1>
<p>Prévisualisation 2D des PNG livrés. Statut : OWNER_REVIEW_REQUIRED. Les dimensions, le rendu et le rythme en moteur restent à vérifier par Fable.</p>
<label>Famille <select id="family"></select></label><label>Séquence <select id="sequence"></select></label>
<label>Rotation <select id="rotation"></select></label><label>Fond <select id="background"><option value="#dfdfd4">Clair</option><option value="#172129">Sombre</option><option value="#787c77">Gris</option></select></label>
<label>Vitesse <select id="speed"><option value="1">1×</option><option value="0.5">0,5×</option><option value="0.25">0,25×</option></select></label>
<button id="play">Pause</button><button id="step">Image suivante</button><label><input id="flash" type="checkbox" checked>Flash FAL</label>
<canvas id="view" width="1080" height="720"></canvas><p id="info"></p>
<p>Repère ennemi : origine X fixe et ligne de sol commune. Étirement vertical 1,2 simulé. Les rythmes ennemis de cette page servent uniquement à examiner les poses.</p>
<script>
const data=__DATA__;
const $=id=>document.getElementById(id), canvas=$('view'), ctx=canvas.getContext('2d'), cache=new Map();
let group, seq=[], index=0, playing=true, last=0;
function options(el,values){el.replaceChildren(...values.map(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;return o;}));}
options($('family'),Object.keys(data));
function changeFamily(){group=data[$('family').value];options($('sequence'),Object.keys(group.sequences));options($('rotation'),group.weapon?['0']:['1','2','3','4','5','6','7','8']);$('flash').disabled=!group.weapon;changeSequence();}
function changeSequence(){seq=group.sequences[$('sequence').value];index=0;last=performance.now();draw();}
function getImage(file){if(!cache.has(file)){const im=new Image();im.onload=draw;im.src='../'+file;cache.set(file,im);}return cache.get(file);}
function render(entry){if(!entry)return;const im=getImage(entry.file);if(!im.complete||!im.naturalWidth)return;
if(group.weapon){ctx.drawImage(im,0,0,1080,720);}else{const sx=.2*4.7,sy=.24*4.7;ctx.drawImage(im,540-entry.offset[0]*sx,620-entry.offset[1]*sy,entry.width*sx,entry.height*sy);}}
function draw(){ctx.fillStyle=$('background').value;ctx.fillRect(0,0,1080,720);if(!seq.length)return;
if(!group.weapon){ctx.strokeStyle='#87948b';ctx.beginPath();ctx.moveTo(30,620);ctx.lineTo(1050,620);ctx.stroke();}
const step=seq[index],entry=group.frames[step.state+'_'+$('rotation').value];render(entry);
if(group.weapon&&step.state==='FAL_FIRE'&&$('flash').checked)render(group.flash);
$('info').textContent=(entry?entry.file:'Image absente')+' | '+(index+1)+' / '+seq.length+' | '+step.ms+' ms (proposé)';}
function loop(now){if(playing&&seq.length&&now-last>=seq[index].ms/Number($('speed').value)){index=(index+1)%seq.length;last=now;draw();}requestAnimationFrame(loop);}
$('family').onchange=changeFamily;$('sequence').onchange=changeSequence;$('rotation').onchange=draw;$('background').onchange=draw;$('flash').onchange=draw;
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause':'Lecture';last=performance.now();};
$('step').onclick=()=>{playing=false;$('play').textContent='Lecture';index=(index+1)%seq.length;draw();};
changeFamily();requestAnimationFrame(loop);
</script></main></html>'''

def main():
    batch = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    manifest=json.loads((batch/'manifest.json').read_text(encoding='utf-8'))
    animation=json.loads((batch/'source/animation.json').read_text(encoding='utf-8'))
    data={}
    if 'FAL' in batch.name:
        frames={}
        for state in animation['states']:
            frames[state['state']+'_0']={'file':'runtime/weapons/fal/'+state['file']}
        def sequence(states):
            return [{'state':s['state'],'ms':max(28,round(s['duration_tics_proposal']*1000/35))} for s in states]
        states=animation['states']
        data['FAL']={'weapon':True,'frames':frames,
            'flash':{'file':'runtime/weapons/fal/'+animation['flash']['file']},
            'sequences':{'Repos':[{'state':'FAL_READY','ms':1000}],
                         'Tir':sequence(states[1:4])+[{'state':'FAL_READY','ms':350}],
                         'Recharge à vide':sequence(states[4:])+[{'state':'FAL_READY','ms':500}],
                         'Recharge partielle':sequence(states[4:15]+states[18:])+[{'state':'FAL_READY','ms':500}]}}
    else:
        for family in animation['families']:
            ident=family['id']
            frames={e['state']+'_'+str(e['rotation']):{'file':e['file'],'width':e['width'],'height':e['height'],'offset':e['offset_pixels']}
                    for e in manifest['files'] if e['family_id']==ident and e['kind']=='enemy_sprite'}
            names=[s['name'] for s in family['states']]
            def seq(items, ms=140):
                return [{'state':s,'ms':900 if s=='corpse' else ms} for s in items]
            attacks=[s for s in names if any(x in s for x in ('attack','charge','telegraph','release','recovery'))]
            data[ident.upper()]={'weapon':False,'frames':frames,'sequences':{
                'Repos':seq(['idle'],1000),'Marche':seq([s for s in names if s.startswith('walk')]),
                'Attaque':seq(attacks)+seq(['idle'],450),'Douleur':seq(['pain','idle'],300),
                'Mort':seq(['idle']+[s for s in names if s.startswith('death')]+['corpse'],220)}}
    for group in data.values():
        for entry in list(group['frames'].values())+([group['flash']] if group.get('flash') else []):
            assert (batch/entry['file']).is_file(), entry['file']
    html=TEMPLATE.replace('__TITLE__',batch.name).replace('__DATA__',json.dumps(data,ensure_ascii=False))
    (batch/'evidence/review.html').write_text(html,encoding='utf-8')
    print(batch/'evidence/review.html')

if __name__=='__main__':
    main()
