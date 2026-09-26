"""Serial final engine runs, only after the complete render has finished."""
from pathlib import Path
import os,subprocess,time,sys,json
ROOT=Path(__file__).resolve().parents[3]
os.chdir(ROOT);os.environ['RF_DEV_HIDDEN']='1'
def run(args):
    if '--name' in args:
        name=str(args[args.index('--name')+1])
        for parent in ['build/dev/shots','build/dev/film']:
            assert (ROOT/parent/name).resolve().is_relative_to(ROOT/parent)
    print('RUN '+' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True,cwd=ROOT)
def main():
    marker=ROOT/'art/rf2_art_01/enemies/manifest_all.json'
    deadline=time.monotonic()+1800
    while not marker.exists():
        if time.monotonic()>deadline:raise TimeoutError('Complete render manifest not produced')
        time.sleep(5)
    assert len(json.loads(marker.read_text()))==320
    stage=(ROOT/'build/pk3_stage').resolve();assert stage.is_relative_to(ROOT/'build')
    run(['pwsh','-NoProfile','-File','scripts/build.ps1'])
    for script in ['scripts/hidden_norun.py','scripts/check_runtime.py','art/rf2_art_01/review/verify.py']:run(['python',script])
    common=['+screenshot_quiet','1','+r_drawplayersprites','1','+screenblocks','10']
    for name,w,h,hud in [('after_weapons_1080',1920,1080,1),('after_weapons_1440',2560,1440,1),('after_weapons_1610',1920,1200,1.25)]:
        run(['python','scripts/devrun.py','--name',name,'--map','RF01','--width',w,'--height',h,'--seconds',60,'+rf_dev_weapons','1','+rf_hud_scale',hud]+common)
    run(['python','scripts/devrun.py','--name','after_corpses','--map','RF01','--width',1280,'--height',720,'--speed',2,'--marker','RF_DEV_CORPSE_DONE','+rf_dev_corpse','1','+r_drawplayersprites','0','+screenblocks','12','+screenshot_quiet','1'])
    run(['python','scripts/film.py','--name','weapons_final','--start',10,'--end',430,'--every',2,'+rf_dev_autopilot','0','+rf_dev_weapons','1','+rf_hud_scale','1']+common)
    run(['python','scripts/film.py','--name','combat_final','--end',900,'--every',3,'+rf_dev_autopilot','0','+rf_dev_art_combat','1','+rf_hud_scale','1']+common)
    run(['python','scripts/film.py','--name','corpses_final','--start',70,'--end',1261,'--every',3,'+rf_dev_autopilot','0','+rf_dev_corpse','1','+screenshot_quiet','1','+r_drawplayersprites','0','+screenblocks','12'])
    run(['python','scripts/film.py','--name','rf01_final','--end',1800,'--every',4]+common)
    for name,pk3 in [('perf_before','art_pass/base/COMPARISON_844b50f.pk3'),('perf_after','dist/RF2_DEV.pk3')]:
        run(['python','scripts/devrun.py','--pk3',pk3,'--name',name,'--map','RF01','--width',1280,'--height',720,'--marker','RF_DEV_PERF_DONE','+rf_dev_perf','1','+vid_maxfps','0','+rf_hud_scale','1']+common)
    run(['python','art/rf2_art_01/review/evidence.py'])
    run(['python','art/rf2_art_01/review/report.py'])
    print('FINAL CAPTURES AND REPORT COMPLETE',flush=True)
if __name__=='__main__':main()
