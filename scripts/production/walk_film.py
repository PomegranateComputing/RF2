#!/usr/bin/env python3
"""A short film of one figure walking across a fixed camera, at the game's own speed, on any build (the walk loop of
an enemy family seen in profile: the loop B-C-D-E of the orderly, the next families).

A separate test pk3 (loaded after the build, which is not modified): its player class stands at the camera, out of
reach (no target, god mode); the figure is spawned to one side of the view and sent walking (its See state, A_Chase)
toward an invisible mark on the other side, so that it crosses the picture in profile. A screenshot is taken every
`every` tics; a tic strip in the top-left corner of each picture gives the tic it shows (ticcode.py), and the film is
assembled from the pictures in tic order at 35 / every pictures per second: one second of film is one second of game.
The engine runs slowed (i_timescale, --speed) while filming: saving a picture takes longer than a tic, and at full
speed the engine catches up by running several tics per drawn frame (pictures of the same tic).

Usage: python scripts/production/walk_film.py <build.pk3> <MAP> <Class> <x> <y> <angle> <out_dir>
                                              [--distance 192] [--tics 112] [--every 2] [--size 1280x720]
Writes <out_dir>/<Class>.mp4, the pictures (frame_NNN_tTTTT.png), a strip of the first loop and film.json.
"""
import argparse, hashlib, json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import ticcode  # noqa: E402
import devrun  # noqa: E402

ZS = '''version "4.14"
class RFWalkMark : Actor
{
    Default { Health 1000; Radius 8; Height 56; +SHOOTABLE; +NOGRAVITY; +NODAMAGE; RenderStyle "None"; }
    States { Spawn: TNT1 A -1; Stop; }
}

class RFWalkFilmPlayer : RFPlayer
{
    int phase;
    Actor walker;
    override void PlayerThink()
    {
        if (player != null && Level.maptime >= %(wait)d)
        {
            player.cheats |= CF_NOCLIP | CF_GODMODE | CF_NOTARGET;
            player.cmd.buttons = 0;
            player.cmd.forwardmove = 0;
            player.cmd.sidemove = 0;
            int t = phase++;
            if (t == 0)
            {
                let it = ThinkerIterator.Create("Actor");
                Actor a;
                while ((a = Actor(it.Next())) != null)
                    if (a != self && (a.bIsMonster || a.bShootable)) a.Destroy();
                Vector2 at = (%(x)f, %(y)f);
                double floor = Level.PointInSector(at).floorplane.ZAtPoint(at);
                SetOrigin((at, floor), false);
                angle = %(angle)f;
                pitch = 0;
                Vector2 fwd = Actor.AngleToVector(%(angle)f, %(distance)f);
                Vector2 side = Actor.AngleToVector(%(angle)f - 90, 1);
                Vector2 from = at + fwd - side * %(half)f, to = at + fwd + side * 1200;
                if (%(explicit)d) { from = (%(fx)f, %(fy)f); to = (%(tx)f, %(ty)f); }
                let mark = Spawn("RFWalkMark", (to, Level.PointInSector(to).floorplane.ZAtPoint(to)));
                walker = Spawn("%(cls)s", (from, Level.PointInSector(from).floorplane.ZAtPoint(from)));
                if (walker != null)
                {
                    walker.angle = walker.AngleTo(mark);
                    walker.target = mark;
                    walker.SetStateLabel("See");
                }
                Console.Printf("RF_WALKFILM start t=%%d", Level.maptime);
            }
            angle = %(angle)f;
            pitch = 0;
            Vel = (0, 0, 0);
            if (t >= 2 && t < 2 + %(tics)d && (t - 2) %% %(every)d == 0)
            {
                Console.Printf("RF_WALKFILM frame=%%d t=%%d state=%%d", (t - 2) / %(every)d, Level.maptime,
                               walker != null ? walker.frame : -1);
                Level.MakeScreenShot();
            }
            if (t == 2 + %(tics)d + 4) Console.Printf("RF_DEV_UI_DONE");
        }
        Super.PlayerThink();
    }
}

class RFTicStrip : EventHandler
{
    override void RenderOverlay(RenderEvent e)
    {
        int tic = Level.maptime;
        Screen.Clear(0, 0, 8 * 18 + 4, 12, Color(255, 0, 0, 0));
        Screen.Clear(2, 2, 10, 10, Color(255, 255, 0, 0));
        for (int i = 0; i < 16; i++)
        {
            Color c = (tic >> i) & 1 ? Color(255, 255, 255, 255) : Color(255, 0, 0, 0);
            Screen.Clear(2 + 8 * (i + 1), 2, 10 + 8 * (i + 1), 10, c);
        }
        Screen.Clear(2 + 8 * 17, 2, 10 + 8 * 17, 10, Color(255, 0, 255, 0));
    }
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pk3')
    ap.add_argument('map')
    ap.add_argument('cls')
    ap.add_argument('x', type=float)
    ap.add_argument('y', type=float)
    ap.add_argument('angle', type=float)
    ap.add_argument('out')
    ap.add_argument('--distance', type=float, default=144)
    ap.add_argument('--half', type=float, default=110, help='start this far to the left of the view axis')
    ap.add_argument('--path', default='', help='x0,y0,x1,y1: walk from (x0,y0) toward (x1,y1) (open ground)')
    ap.add_argument('--tics', type=int, default=112)
    ap.add_argument('--every', type=int, default=2)
    ap.add_argument('--wait', type=int, default=230, help='tics before filming (the title card has gone)')
    ap.add_argument('--size', default='1280x720')
    ap.add_argument('--speed', type=float, default=0.15,
                    help='i_timescale: the game slowed so that every filmed tic is drawn (a PNG takes longer than a tic)')
    a = ap.parse_args()
    pk3 = Path(a.pk3).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    name = ('wf_' + re.sub(r'[^A-Za-z0-9_]+', '_', out.name))[:60]
    probe = Path(tempfile.gettempdir()) / f'{name}_probe.pk3'
    fx, fy, tx, ty = (float(v) for v in a.path.split(',')) if a.path else (0, 0, 0, 0)
    zs = ZS % dict(wait=a.wait, x=a.x, y=a.y, angle=a.angle, distance=a.distance, half=a.half, cls=a.cls,
                   explicit=1 if a.path else 0, fx=fx, fy=fy, tx=tx, ty=ty,
                   tics=a.tics, every=a.every)
    with zipfile.ZipFile(probe, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('ZSCRIPT.walkfilm', zs)
        z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFWalkFilmPlayer"\n    AddEventHandlers = "RFTicStrip"\n}\n')
    w, h = (int(v) for v in a.size.split('x'))
    seconds = int((a.wait + a.tics + 60) / (35 * a.speed)) + 30
    # +i_timescale on the command line does not hold (UZDoom 5.0.1): a deferred exec sets it once the game runs
    cfg = Path(tempfile.gettempdir()) / f'{name}_slow.cfg'
    cfg.write_text(f'wait 10; i_timescale {a.speed}\n', encoding='ascii')
    status, text, shots = devrun.run(pk3, name, a.map.upper(), seconds=seconds, width=w, height=h,
                                     marker='RF_DEV_UI_DONE',
                                     extra=['-file', str(probe), '+cl_capfps', '1', '+exec', str(cfg)])
    logged = [(int(i), int(t), s) for i, t, s in re.findall(r'RF_WALKFILM frame=(\d+) t=(\d+) state=(-?\d+)', text)]
    by_tic = {}
    for p in sorted(shots.glob('*.png')):
        t = ticcode.read(p)
        if t is not None:
            by_tic.setdefault(t, p)
    for f in out.glob('frame_*.png'):
        f.unlink()
    rows, kept = [], []
    for i, t, s in logged:
        p = by_tic.get(t)
        if p is not None:
            dst = out / f'frame_{i:03d}_t{t:05d}.png'
            shutil.copy2(p, dst)
            kept.append(dst)
        rows.append(dict(frame=i, tic=t, sprite_frame='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(s)] if s.isdigit() else s, kept=p is not None))
    fps = 35.0 / a.every
    film = out / f'{a.cls}.mp4'
    if kept:
        lst = out / 'frames.txt'
        lst.write_text(''.join(f"file '{p.name}'\nduration {1 / fps:.6f}\n" for p in kept) + f"file '{kept[-1].name}'\n",
                       encoding='utf-8')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst.name,
                        '-vf', 'format=yuv420p', '-r', f'{fps:g}', film.name], cwd=out, check=True)
    report = dict(build=str(pk3), build_sha256=hashlib.sha256(pk3.read_bytes()).hexdigest(), map=a.map.upper(),
                  cls=a.cls, camera=[a.x, a.y, a.angle], distance=a.distance, every_tics=a.every, fps=fps,
                  status=status, frames=rows, film=film.name if kept else None,
                  note='Engine pictures at the tics they show; the film plays one second of game per second.')
    (out / 'film.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{a.cls}: {len(kept)}/{len(logged)} images, {fps:g} i/s -> {film if kept else "pas de film"}')
    return 0 if kept and len(kept) == len(logged) else 1


if __name__ == '__main__':
    sys.exit(main())
