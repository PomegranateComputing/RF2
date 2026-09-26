"""Deterministic RF01 audio edit decisions. 48 kHz/24-bit masters; mono PCM16 runtime.
Real CC0 source recordings, short dry edits, no runtime layers or synthetic gunshots.
Human audition is explicitly not asserted by this script's level measurements.
"""
from pathlib import Path
import json,hashlib,math,shutil
import numpy as np
import soundfile as sf
from scipy import signal
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];SR=48000
DL=HERE/'downloads';SOURCES=HERE/'sources';MASTERS=HERE/'masters';OUT=ROOT/'src/sounds'
USED={};ROWS=[]

def load(path):
    path=Path(path);key=path.relative_to(DL).as_posix()
    if (SOURCES/key).exists():path=SOURCES/key
    data,sr=sf.read(path,always_2d=True,dtype='float64')
    # These are stereo location recordings, mono average verified for cancellation.
    mono=data.mean(axis=1)
    if np.max(np.abs(mono))<np.max(np.abs(data))*.2:mono=data[:,0]
    if sr!=SR:mono=signal.resample_poly(mono,SR//math.gcd(sr,SR),sr//math.gcd(sr,SR))
    target=SOURCES/key;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copy2(path,target)
    USED[key]=hashlib.sha256(path.read_bytes()).hexdigest()
    return mono,key

def fade(x,start=.001,end=.04):
    x=x.copy();a=min(len(x),round(start*SR));b=min(len(x),round(end*SR))
    if a:x[:a]*=np.linspace(0,1,a)
    if b:x[-b:]*=np.linspace(1,0,b)**1.5
    return x

def trim(x,db=-48):
    i=np.where(np.abs(x)>10**(db/20))[0]
    return x[max(0,i[0]-240):min(len(x),i[-1]+1440)] if len(i) else x

def hp(x,hz=55):return signal.sosfilt(signal.butter(2,hz,fs=SR,btype='highpass',output='sos'),x)
def lp(x,hz):return signal.sosfilt(signal.butter(2,hz,fs=SR,btype='lowpass',output='sos'),x)

def gun_body(x):
    """Fast feed-forward peak compression; preserves the waveform and natural dry decay.
    A 12 ms release lets the recorded body recover after the very narrow impulse.
    The normal export ceiling still supplies headroom; this is not hard clipping.
    """
    threshold=max(abs(x).max()*.06,1e-8);release=math.exp(-1/(.012*SR))
    env=np.empty(len(x));level=0.
    for i,v in enumerate(abs(x)):
        level=max(float(v),level*release);env[i]=level
    gain=np.minimum(1,(threshold/np.maximum(env,threshold))**.8)
    return x*gain

def mix(parts,seconds=None):
    n=round(seconds*SR) if seconds else max(round(t*SR)+len(x) for x,t,g in parts)
    y=np.zeros(n)
    for x,t,g in parts:
        i=round(t*SR);m=min(n-i,len(x))
        if m>0:y[i:i+m]+=x[:m]*g
    return y

def save(rel,x,peak_db,sources,edit):
    x=hp(x);x=fade(x);x-=np.mean(x)
    p=max(np.max(np.abs(x)),1e-12);gain=10**(peak_db/20)/p;x*=gain
    x=fade(x,.0003,.004)
    dst=OUT/rel;dst.parent.mkdir(parents=True,exist_ok=True);sf.write(dst,x,SR,subtype='PCM_16')
    master=MASTERS/rel;master.parent.mkdir(parents=True,exist_ok=True);sf.write(master,x,SR,subtype='PCM_24')
    ROWS.append(dict(target='src/sounds/'+rel,master=master.relative_to(ROOT).as_posix(),sources=sources,
        edit=edit,format='WAV PCM16 mono 48000 Hz',seconds=round(len(x)/SR,4),peak_dbfs=round(20*np.log10(max(abs(x).max(),1e-12)),2),
        rms_dbfs=round(20*np.log10(np.sqrt(np.mean(x*x))+1e-12),2),edit_gain_db=round(20*np.log10(gain),3),clipped_samples=int(np.sum(abs(x)>=1)),
        audition='NOT_PERFORMED_BY_AGENT'))
    return x

def kpack(kind,name):return load(DL/kind/'Audio'/name)
def basic(rel,kind,name,peak=-12,lowpass=None):
    x,k=kpack(kind,name);x=trim(x)
    if lowpass:x=lp(x,lowpass)
    return save(rel,x,peak,[k],'trim; high-pass DC/rumble; short edge fades; mono; level to hierarchy')

def recorded_shot(path,t,duration):
    x,k=load(DL/'firearms/Prepared SFX Library'/path)
    # Find exact transient within the logged 5 ms onset interval.
    lo=max(0,int((t-.02)*SR));hi=int((t+.03)*SR);seg=x[lo:hi]
    q=np.where(abs(seg)>.018)[0];onset=lo+(q[0] if len(q) else int(.02*SR))
    shot=x[max(0,onset-32):onset+int(duration*SR)]
    return fade(shot,.0002,.065),k

def main():
    SOURCES.mkdir(parents=True,exist_ok=True)
    mech,mk=kpack('rpg','metalClick.ogg');mech=trim(mech)
    for i,t in enumerate([1.405,6.44,10.66],1):
        x,k=recorded_shot('Walther PPQ/X_39P.wav',t,.47)
        x=gun_body(mix([(x,0,1),(mech,.045,.035)],.49))
        save(f'browning/fire_0{i}.wav',x,-2.2,[k,mk],f'Independent 9 mm take at {t}s; 470 ms dry edit + -29 dB metal action at 45 ms; 5:1 peak compression at -24.4 dB relative, instant attack/12 ms release; no pitch shift')
        if i==1:save('browning/fire.wav',x,-2.2,[k,mk],'Compatibility alias of fire_01; existing path remains valid')
    for i,(ta,tb) in enumerate([(1.305,2.61),(6.73,8.015),(1.305,12.785)],1):
        body,bk=recorded_shot('1917/B_24P.wav',ta,.60)
        crack,ck=recorded_shot('SKS/U_19P.wav',tb,.40)
        x=gun_body(mix([(lp(body,3600),0,.75),(hp(crack,1400),0,.75),(mech,.055,.022)],.63))
        save(f'fal/shot_0{i}.wav',x,-1.8,[bk,ck,mk],f'Rifle sound design (not claimed to be FAL recording): .30-06 body take {ta}s + 7.62 SKS transient take {tb}s + short action; 5:1 peak compression at -24.4 dB relative, instant attack/12 ms release')
    for rel,file,db in [('browning/slide.wav','metalLatch.ogg',-15),('browning/dry.wav','metalClick.ogg',-15),
        ('fal/dry.wav','metalClick.ogg',-15),('fal/latch.wav','metalLatch.ogg',-12),('fal/mag_out.wav','drawKnife2.ogg',-13),
        ('fal/mag_in.wav','metalLatch.ogg',-10.5),('fal/seat.wav','bookPlace2.ogg',-12),('fal/action.wav','drawKnife1.ogg',-11),
        ('fal/raise.wav','beltHandle1.ogg',-15),('fal/cloth.wav','cloth2.ogg',-20),('world/paper.wav','bookFlip2.ogg',-17),
        ('world/switch.wav','metalClick.ogg',-14),('world/door.wav','doorOpen_1.ogg',-10),('world/door_close.wav','doorClose_2.ogg',-10),
        ('porte/telegraph.wav','bookOpen.ogg',-11),('porte/throw.wav','bookFlip3.ogg',-11),('items/pickup.wav','beltHandle2.ogg',-17)]:
        basic(rel,'rpg',file,db)
    for i in range(1,4):
        for mat,source,db in [('wood','impactWood_medium',-7),('plaster','impactMining',-7),('metal','impactMetal_medium',-8),('flesh','impactSoft_medium',-9)]:
            basic(f'impact/{mat}_0{i}.wav','impact',f'{source}_{i-1:03}.ogg',db)
        basic(f'orderly/step_0{i}.wav','impact',f'footstep_concrete_{i-1:03}.ogg',-17)
        basic(f'fal/shell_0{i}.wav','impact',f'impactMetal_light_{i-1:03}.ogg',-24,6500)
    basic('world/body_fall.wav','impact','impactSoft_heavy_002.ogg',-10)
    basic('brancardier/frame_hit.wav','impact','impactMetal_heavy_002.ogg',-6.5)
    # Brancardier: actual frame friction and rubber/concrete contacts; no roar bed.
    creak,ck=kpack('rpg','creak2.ogg');step,sk=kpack('impact','footstep_concrete_002.ogg')
    save('brancardier/wheel.wav',mix([(lp(trim(creak),2500),0,.5),(trim(step),.07,.15)],.65),-15,[ck,sk],'short friction creak and wheel contact')
    clank,cl=kpack('impact','impactMetal_medium_003.ogg')
    save('world/winch.wav',mix([(trim(creak),0,.6),(trim(creak),.63,.35),(trim(clank),1.17,.8)],1.65),-13,[ck,cl],'two mechanism creaks, terminating frame engagement; no constant motor buzz')
    # One actor voice per family, natural pitch; unique takes, no monster pitch trick.
    voice=DL/'voices/yelling sounds'
    cues={'orderly': [('penitent_sight','3grunt1'),('penitent_pain','3grunt3'),('penitent_death','3yell11'),('penitent_active','3grunt2'),('penitent_attack','3grunt4')],
          'brancardier':[('invalid_sight','1yell5'),('invalid_pain','1yell2'),('invalid_death','1yell10'),('invalid_active','1yell8'),('brace','1yell4')],
          'porte':[('presence','2yell1'),('pain','2yell3'),('death','2yell10')],
          'viktor':[('pain_01','3grunt5'),('pain_02','3grunt6'),('death','3yell15')]}
    for family,items in cues.items():
        for name,take in items:
            x,k=load(voice/(take+'.wav'));x=lp(hp(trim(x),100),7000)
            if family=='orderly':x=lp(x,3400) # cloth/leather mouth restraint, no pitch change
            db=-8 if family=='viktor' else -7 if 'death' in name else -10
            save(f'{family}/{name}.wav',x,db,[k],'natural human voice; DC/rumble removed, HF softened; mono; no pitch shift')
    # Existing authored ambience retained with independent restrained level changes.
    # Preserve its source BEFORE editing, so repeated exports do not accumulate EQ/gain.
    for name,db in [('hum_loop',-30),('wind_loop',-26),('drip_loop',-24),('room_loop',-36)]:
        p=HERE/'sources/project_world'/(name+'.wav');p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():shutil.copy2(OUT/'world'/(name+'.wav'),p)
        x,sr=sf.read(p);x=signal.resample_poly(x,SR//math.gcd(sr,SR),sr//math.gcd(sr,SR))
        # Preserve the periodic boundary: circular lowpass then one global gain, no edge fades.
        X=np.fft.rfft(x);f=np.fft.rfftfreq(len(x),1/SR);X/=1+(f/4500)**4;x=np.fft.irfft(X,n=len(x))
        x=x/np.max(abs(x))*10**(db/20)
        dst=OUT/'world'/(name+'.wav');sf.write(dst,x,SR,subtype='PCM_16');q=MASTERS/'world'/(name+'.wav');q.parent.mkdir(parents=True,exist_ok=True);sf.write(q,x,SR,subtype='PCM_24')
        ROWS.append(dict(target=dst.relative_to(ROOT).as_posix(),master=q.relative_to(ROOT).as_posix(),sources=[p.relative_to(HERE).as_posix()],edit='retained project ambience; periodic HF EQ; reduced source gain',seconds=len(x)/SR,peak_dbfs=db,rms_dbfs=20*np.log10(np.sqrt(np.mean(x*x))+1e-12),format='WAV PCM16 mono 48000 Hz',clipped_samples=0,audition='NOT_PERFORMED_BY_AGENT'))
    (HERE/'audio_manifest.json').write_text(json.dumps({'sample_rate':SR,'files':ROWS,'source_sha256':USED},indent=2),encoding='utf8')
    print(f'{len(ROWS)} runtime cues and lossless masters; {len(USED)} external sources retained')
if __name__=='__main__':main()
