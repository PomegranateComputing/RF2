#!/usr/bin/env python3
"""Each door of a map seen working, from the player's height: shut, on its way up, open, on its way down. The door
is moved by the engine's own Door_Raise on its tag (speed 16, as the maps' doors; a lock is not asked for: this is a
view of the mechanism, not of the key), so the leaf, its jambs and its lintel are judged while the leaf moves: the leaf
alone must move.

One camera per door (the first face of each mechanism in the audit, door_audit.py), placed as door_views.py places it.
Usage: python scripts/production/door_motion.py <build.pk3> <out_dir> [--audit build/door_audit.json] [--maps RF01]
                                                [--wads src/maps]
Writes <out_dir>/<MAP>/<door>_{1_fermee,2_en_course,3_ouverte,4_en_fermeture}.png and <out_dir>/<MAP>/mouvement.json
(with the leaf's ceiling height logged at each picture: the proof that it was moving).
"""
import argparse, json, re, shutil, sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import door_audit, door_views, ticcode, devrun  # noqa: E402

PHASES = ['1_fermee', '2_en_course', '3_ouverte', '4_en_fermeture']
ZS = '''version "4.14"
class RFDoorMotionPlayer : RFPlayer
{
    int step, phase, base;
    bool hidden;
    override void PlayerThink()
    {
        static const String LABELS[] = { %(labels)s };
        static const double VX[] = { %(vx)s };
        static const double VY[] = { %(vy)s };
        static const double VA[] = { %(va)s };
        static const double VP[] = { %(vp)s };
        static const int TAG[] = { %(tags)s };
        static const int SEC[] = { %(secs)s };
        static const int TRAVEL[] = { %(travel)s };
        int n = %(n)d;
        if (player != null && Level.maptime >= 180)
        {
            player.cheats |= CF_NOCLIP | CF_GODMODE | CF_NOTARGET;
            player.cmd.buttons = 0;
            player.cmd.forwardmove = 0;
            player.cmd.sidemove = 0;
            if (!hidden)
            {
                hidden = true;
                let it = ThinkerIterator.Create("Actor");
                Actor a;
                while ((a = Actor(it.Next())) != null)
                    if (a != self && (a.bIsMonster || a.bShootable))
                    {
                        a.A_SetRenderStyle(0, STYLE_None);
                        a.bDormant = true;
                    }
            }
            if (step >= n) { if (phase++ == 0) Console.Printf("RF_DEV_UI_DONE"); }
            else
            {
                int t = phase++;
                Vector2 at = (VX[step], VY[step]);
                if (t == 0) SetOrigin((at, Level.PointInSector(at).floorplane.ZAtPoint(at)), false);
                angle = VA[step];
                pitch = VP[step];
                Vel = (0, 0, 0);
                // the leaf rises 2 units a tic (speed 16), waits 150 tics, comes down
                int rise = TRAVEL[step] / 2;
                int shotA = 12, go = 16, shotB = go + rise / 2, shotC = go + rise + 20, shotD = go + rise + 150 + rise / 2;
                if (t == go) Level.ExecuteSpecial(12, self, null, false, TAG[step], 16, 150);
                int which = t == shotA ? 0 : t == shotB ? 1 : t == shotC ? 2 : t == shotD ? 3 : -1;
                if (which >= 0)
                {
                    Sector s = Level.Sectors[SEC[step]];
                    Console.Printf("RF_DOORMOTION label=%%s phase=%%d t=%%d ceiling=%%.1f floor=%%.1f", LABELS[step], which, Level.maptime,
                        s.ceilingplane.ZAtPoint(s.centerspot), s.floorplane.ZAtPoint(s.centerspot));
                    Level.MakeScreenShot();
                }
                if (t >= shotD + 6) { step++; phase = 0; }
            }
        }
        Super.PlayerThink();
    }
}
'''

# the tic strip of view_check_pk3.py: the tic a picture was drawn at, read back by ticcode.py
STRIP = '''
class RFMotionTicStrip : EventHandler
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
    ap.add_argument('out')
    ap.add_argument('--audit', default=str(ROOT / 'build' / 'door_audit.json'))
    ap.add_argument('--wads', default=str(ROOT / 'src' / 'maps'))
    ap.add_argument('--maps', default='')
    a = ap.parse_args()
    recs = json.loads(Path(a.audit).read_text(encoding='utf-8'))
    names = {n.strip().upper() for n in a.maps.split(',') if n.strip()}
    db = door_audit.texture_db()
    out = Path(a.out)
    for mp in sorted({r['map'] for r in recs}):
        if names and mp not in names:
            continue
        m = door_audit.Map(mp, dict(door_audit.lumps(Path(a.wads) / f'{mp}.wad'))['TEXTMAP'].decode('utf-8', 'replace'), db, {})
        doors_ = {}
        for r in recs:
            if r['map'] != mp or r['kind'] != 'mechanism' or r['sector'] in doors_:
                continue
            tag = m.SE[r['sector']].get('id', 0)
            cam, d = door_views.camera(m, r, 25)
            if not tag or cam is None:
                continue
            doors_[r['sector']] = dict(label=f"porte_s{r['sector']}_tag{tag}_{r['tex']}_{r['W']:g}x{r['H']:g}", cam=cam, tag=tag,
                                       travel=max(8, int(r['H']) - 4), rec=r)
        if not doors_:
            continue
        todo = list(doors_.values())
        got = {}
        mdir = out / mp
        mdir.mkdir(parents=True, exist_ok=True)
        for attempt in range(4):
            if not todo:
                break
            zs = ZS % dict(labels=', '.join('"%s"' % d['label'] for d in todo), vx=', '.join(str(float(d['cam'][0])) for d in todo),
                           vy=', '.join(str(float(d['cam'][1])) for d in todo), va=', '.join(str(float(d['cam'][3])) for d in todo),
                           vp=', '.join(str(float(d['cam'][4])) for d in todo), tags=', '.join(str(d['tag']) for d in todo),
                           secs=', '.join(str(d['rec']['sector']) for d in todo), travel=', '.join(str(d['travel']) for d in todo), n=len(todo))
            probe = Path(tempfile.gettempdir()) / f'door_motion_{mp}.pk3'
            with zipfile.ZipFile(probe, 'w') as z:
                z.writestr('ZSCRIPT.doormotion', zs + STRIP)
                z.writestr('MAPINFO', 'gameinfo\n{\n    PlayerClasses = "RFDoorMotionPlayer"\n    AddEventHandlers = "RFMotionTicStrip"\n}\n')
            status, text, shots = devrun.run(Path(a.pk3).resolve(), f'dm_{out.name}_{mp}'[:60], mp, seconds=90 + 12 * len(todo), width=1280,
                                             height=720, marker='RF_DEV_UI_DONE', extra=['-file', str(probe)])
            by_tic = {}
            for p in sorted(shots.glob('*.png')):
                t = ticcode.read(p)
                if t is not None:
                    by_tic.setdefault(t, p)
            for label, ph, t, ceil, floor in re.findall(r'RF_DOORMOTION label=(\S+) phase=(\d) t=(\d+) ceiling=([-\d.]+) floor=([-\d.]+)', text):
                p = by_tic.get(int(t))
                if p is not None:
                    dst = mdir / f'{label}_{PHASES[int(ph)]}.png'
                    shutil.copy2(p, dst)
                    got.setdefault(label, {})[PHASES[int(ph)]] = dict(tic=int(t), opening=float(ceil) - float(floor), file=dst.name)
            todo = [d for d in doors_.values() if len(got.get(d['label'], {})) < 4]
        rows = []
        for d in doors_.values():
            g = got.get(d['label'], {})
            op = [g.get(ph, {}).get('opening') for ph in PHASES]
            moved = len(g) == 4 and op[0] == 0 and 0 < op[1] < op[2] and 0 < op[3] < op[2]
            rows.append(dict(door=d['label'], tag=d['tag'], sector=d['rec']['sector'], pictures=len(g), opening=op, moved=moved))
        (mdir / 'mouvement.json').write_text(json.dumps(rows, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f"{mp}: {len(rows)} portes, {sum(r['moved'] for r in rows)} vues dans leurs quatre etats (fermee, en course, ouverte, en fermeture)", flush=True)


if __name__ == '__main__':
    main()
