"""Review audio derived from credited RF01 recordings; never edits accepted sounds.
48 kHz PCM24; separate proposal paths prevent an unintended global replacement.
"""
from pathlib import Path
import json,hashlib,shutil,math
import numpy as np
import soundfile as sf
from scipy import signal
HERE=Path(__file__).resolve().parent;LOT=HERE.parent
OLD=Path('C:/PROJECTS/RF2_UZDOOM/art/rf2_art_01/audio')
SRC=HERE/'audio';OUT=LOT/'audio_proposal';SR=48000
SRC.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
shutil.copy2(OLD.parent/'CREDITS.md',SRC/'RF01_CREDITS.md')
for p in (OLD/'licenses').glob('*.txt'):shutil.copy2(p,SRC/p.name)
used={};rows=[]
def load(rel):
    p=OLD/rel;dst=SRC/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    used[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
    x,sr=sf.read(p,always_2d=True);x=x.mean(axis=1)
    if sr!=SR:x=signal.resample_poly(x,SR//math.gcd(SR,sr),sr//math.gcd(SR,sr))
    return x
def filt(x,hz,kind):return signal.sosfilt(signal.butter(2,hz,fs=SR,btype=kind,output='sos'),x)
def norm(x,peak):
    x=filt(x,35,'highpass');x-=x.mean();x*=10**(peak/20)/max(1e-9,abs(x).max())
    a=min(32,len(x));b=min(960,len(x));x[:a]*=np.linspace(0,1,a);x[-b:]*=np.linspace(1,0,b)
    return x
def mix(parts):
    n=max(len(x)+int(t*SR) for x,t,g in parts);y=np.zeros(n)
    for x,t,g in parts:i=int(t*SR);y[i:i+len(x)]+=x*g
    return y
def save(name,x,peak,sources,note,event):
    x=norm(x,peak);p=OUT/(name+'.wav');sf.write(p,x,SR,subtype='PCM_24')
    rows.append({'file':p.relative_to(LOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'sample_rate':SR,'bits':24,'channels':1,'duration_seconds':len(x)/SR,'peak_dbfs':float(20*np.log10(max(1e-12,abs(x).max()))),'rms_dbfs':float(20*np.log10(max(1e-12,np.sqrt(np.mean(x*x))))),'clipped_samples':int(np.count_nonzero(abs(x)>=1)),'dc':float(x.mean()),'sources':sources,'edit':note,'suggested_event':event,'audition':'NOT_PERFORMED','integration':'NOT_IN_PK3; proposal only'})
    return x
for i in range(1,4):
    r=f'masters/browning/fire_0{i}.wav';x=load(r)
    # Different spectral balance at unchanged ceiling: compact upper-mid pistol snap.
    low=filt(x,200,'lowpass');high=x-filt(x,1900,'lowpass');y=x-.2*low+.16*high
    save(f'RF2_BROWNING_SHOT_0{i}',y,-2.2,[r],'Compact snap: reduce sub-200 Hz 20%, add 16% above 1.9 kHz; unchanged peak ceiling. Existing recorded source, not a verified Hi-Power recording.',f'rf/browning/fire{i}')
    r=f'masters/fal/shot_0{i}.wav';x=load(r)
    body=filt(filt(x,100,'highpass'),650,'lowpass');y=x+.3*body
    save(f'RF2_FAL_SHOT_0{i}',y,-2.2,[r],'Weight in 100–650 Hz from the recorded body; no synthetic explosion, pitch shift, added long reverb or higher peak ceiling.',f'rf/fal/shot{i}')
for i in range(3):
    for family,material in [('metal','Metal'),('wood','Wood'),('flesh','Soft')]:
        r=f'sources/impact/Audio/impact{material}_medium_00{i}.ogg';x=load(r)
        mech='sources/rpg/Audio/metalClick.ogg';m=load(mech)
        save(f'RF2_MELEE_{family.upper()}_0{i+1}',mix([(x,0,1),(m,.022,.07)]),-5,[r,mech],'Recorded contact plus quiet steel-tool rattle, dry and mono. Material-specific impact for melee; route in future weapon contract.',f'proposal rf/melee/{family}{i+1}')
    cloth='sources/rpg/Audio/cloth2.ogg';knife='sources/rpg/Audio/drawKnife2.ogg'
    a=load(cloth);b=load(knife);rate=1+.04*(i-1)
    a=signal.resample(a,int(len(a)/rate));b=filt(b,3600,'lowpass')
    save(f'RF2_MELEE_SWING_0{i+1}',mix([(a,0,.7),(b,.018,.3)]),-10,[cloth,knife],'Short recorded fabric and tool motion; ±4% timing variations, no voiced exertion.',f'proposal rf/melee/swing{i+1}')
# Quiet intermittent tram-body one-shot, separate from any engine/motor loop.
r='sources/rpg/Audio/creak2.ogg';a=load(r);k='sources/impact/Audio/impactMetal_light_001.ogg';b=load(k)
save('RF2_TRAM_BODY_CREAK',mix([(filt(a,4000,'lowpass'),0,.8),(b,.15,.2)]),-17,[r,k],'Sparse wooden body creak and light metal movement. Schedule locally with silence; not a running tram engine.','proposal rf/paris/tram_body')
(LOT/'audio_proposal'/'manifest.json').write_text(json.dumps({'status':'OWNER_REVIEW_REQUIRED','audition':'NOT_PERFORMED','runtime_integration':'NONE','source_sha256':used,'files':rows},ensure_ascii=False,indent=2),encoding='utf8')
print('Audio proposals:',len(rows),'PCM24/48k mono. No audition claimed.')
