"""Focused revalidation after changing only the seven gunshot WAVs."""
from pathlib import Path
import subprocess,zipfile,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];os.chdir(ROOT);os.environ['RF_DEV_HIDDEN']='1'
def run(args):
    if '--name' in args:
        name=str(args[args.index('--name')+1])
        for parent in ['build/dev/film','build/dev/shots']:
            for n in [name,'film_'+name]:assert (ROOT/parent/n).resolve().is_relative_to(ROOT/parent)
    print('RUN '+' '.join(map(str,args)),flush=True);subprocess.run(list(map(str,args)),check=True)
def main():
    assert (ROOT/'build/pk3_stage').resolve().is_relative_to(ROOT/'build')
    run(['pwsh','-NoProfile','-File','scripts/build.ps1'])
    old=ROOT/'art_pass/base/visual_proof_62202d36.pk3';new=ROOT/'dist/RF2_DEV.pk3'
    a=zipfile.ZipFile(old);b=zipfile.ZipFile(new);assert set(a.namelist())==set(b.namelist())
    changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    expected=['sounds/browning/fire.wav']+[f'sounds/browning/fire_0{i}.wav' for i in range(1,4)]+[f'sounds/fal/shot_0{i}.wav' for i in range(1,4)]
    assert sorted(changed)==sorted(expected),changed
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    (ROOT/'art_pass/evidence/audio_revision.json').write_text(json.dumps({'visual_proof_pk3_sha256':sha(old),'final_pk3_sha256':sha(new),'changed_entries':changed,'all_other_pk3_entries_byte_identical':True,'reason':'More recorded body after the narrow gunshot transient; 5:1 compression, no peak ceiling increase','repeated_engine_proofs':['weapons_final','combat_final','rf01_final'],'retained_identical_visual_proofs':['after_weapons_1080','after_weapons_1440','after_weapons_1610','after_corpses','corpses_final','perf_before','perf_after']},indent=2),encoding='utf8')
    run(['python','art/rf2_art_01/review/verify.py'])
    common=['+screenshot_quiet','1','+r_drawplayersprites','1','+screenblocks','10','+rf_hud_scale','1']
    run(['python','scripts/film.py','--name','weapons_final','--start',10,'--end',430,'--every',2,'+rf_dev_autopilot','0','+rf_dev_weapons','1']+common)
    run(['python','scripts/film.py','--name','combat_final','--end',900,'--every',3,'+rf_dev_autopilot','0','+rf_dev_art_combat','1']+common)
    run(['python','scripts/film.py','--name','rf01_final','--end',1800,'--every',4]+common)
    run(['python','art/rf2_art_01/review/evidence.py'])
    run(['python','art/rf2_art_01/review/report.py'])
    print('FINAL AUDIO REVISION VERIFIED',flush=True)
if __name__=='__main__':main()
