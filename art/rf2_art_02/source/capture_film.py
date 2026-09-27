"""Silent visual evidence from actual RF01 combat, using the existing dev harness."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
HERE=Path(__file__).resolve().parent;LOT=HERE.parent;ROOT=LOT.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));import devrun

def main():
    devrun.ROOT=ROOT;devrun.DEV=LOT/'review/engine'
    os.environ['RF_DEV_HIDDEN']='1';pk3=LOT/'review/RF2_ART_02_CANDIDATE.pk3'
    extra=['+rf_dev_ui','0','+rf_dev_autopilot','0','+rf_dev_corpse','0','+rf_dev_weapons','0',
           '+rf_dev_art_combat','1','+rf_dev_film','3','+rf_dev_film_start','12','+rf_dev_film_end','900',
           '+screenshot_quiet','1','+r_drawplayersprites','0','+screenblocks','12']
    status,log,shots=devrun.run(pk3,'candidate_combat_film','RF01',seconds=100,marker='RF_DEV_FILM_DONE',extra=extra,width=1280,height=720)
    assert status.startswith('marker:'),(status,log[-1500:])
    times=[(int(t),float(ms)) for t,ms in re.findall(r'RF_DEV_FILM t=(\d+) ms=([0-9.]+)',log)]
    pngs=sorted(shots.glob('*.png'),key=lambda p:p.stat().st_mtime_ns)
    assert len(times)==len(pngs) and len(times)>250,(len(times),len(pngs))
    frames=[]
    for k,p in enumerate(pngs):
        duration=(times[k+1][1]-times[k][1])/1000 if k+1<len(times) else 3/35
        frames.extend([f"file '{p.as_posix()}'",f'duration {duration:.6f}'])
    frames.append(f"file '{pngs[-1].as_posix()}'")
    concat=LOT/'review/combat_frames.txt';concat.write_text('\n'.join(frames),encoding='utf8')
    movie=LOT/'evidence/combat_RF01.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-vf','fps=35,format=yuv420p','-c:v','libx264','-threads','2','-crf','19','-preset','fast','-an',str(movie)],check=True)
    (LOT/'evidence/combat_RF01.json').write_text(json.dumps({'package_sha256':hashlib.sha256(pk3.read_bytes()).hexdigest(),'status':status,'frames':len(pngs),'sample_every_tics':3,'resolution':[1280,720],'time_source':'RF_DEV_FILM engine millisecond clock','audio':'No audio track; visual enemy review only','scenario':'Existing rf_dev_art_combat, two waves of five enemies, all three families; godmode; not a campaign playthrough'},indent=2),encoding='utf8')
    print('Native RF01 combat film:',movie,flush=True)

if __name__=='__main__':main()
