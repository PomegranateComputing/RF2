#!/usr/bin/env python3
"""Run the engine audit of props (prop_audit_pk3.py) on several maps of a build and list what looks wrong:
  FLOTTE   an actor affected by gravity, or standing (not NOGRAVITY), more than 1 u above the floor under its centre;
  ENFONCE  below the floor;
  PORTE_A_FAUX  the floor under its footprint varies by more than 8 u (half on a step, on a kerb, over a pit);
  DANS_LE_MUR   its drawn half width or its radius reaches past the nearest wall line by more than 4 u.
Lamps, invisible markers and things hung on purpose (NOGRAVITY with z above the floor) are listed apart, not as defects.

Usage: python scripts/production/prop_audit_run.py <build.pk3> <out.json> [RF01 RF02 ...]
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import devrun  # noqa: E402


def main():
    pk3, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    maps = sys.argv[3:] or ['RF01', 'RF02', 'RF04', 'RF05', 'RF06']
    probe = Path(tempfile.gettempdir()) / 'rf2_prop_audit.pk3'
    subprocess.run([sys.executable, str(ROOT / 'scripts/production/prop_audit_pk3.py'), str(probe)], check=True, capture_output=True)
    report = {}
    for mp in maps:
        status, text, _ = devrun.run(pk3, f'audit_{mp}', mp, seconds=60, marker='RF_DEV_UI_DONE', extra=['-file', str(probe)])
        rows = []
        for line in text.splitlines():
            if not line.startswith('RF_AUDIT '):
                continue
            d = dict(re.findall(r'(\w+)=(-?[\d.]+|\w+)', line))
            rows.append(dict(cls=d.pop('class', '?'), raw=line, **d))
        findings, hung = [], []
        for r in rows:
            f = lambda k, default=0.0: float(r.get(k, default)) if re.fullmatch(r'-?[\d.]+', str(r.get(k, ''))) else default
            dz, fmin, fmax, wall, vis, rad = f('dz'), f('fmin'), f('fmax'), f('wall', 999), f('vis'), f('r')
            nograv = r.get('nograv') == '1'
            issues = []
            if dz > 1.0 and not nograv:
                issues.append(f'FLOTTE dz={dz:g}')
            if dz < -1.0:
                issues.append(f'ENFONCE dz={dz:g}')
            if fmax - fmin > 8 and not nograv:
                issues.append(f'PORTE_A_FAUX sol {fmin:g}..{fmax:g}')
            reach = max(vis, rad)
            if wall < reach - 4 and r.get('solid') == '1':
                issues.append(f'DANS_LE_MUR mur a {wall:g} u, emprise {reach:g}')
            if issues:
                findings.append(dict(cls=r['cls'], x=r.get('x'), y=r.get('y'), z=r.get('z'), issues=issues, raw=r['raw']))
            elif nograv and dz > 1.0:
                hung.append(dict(cls=r['cls'], x=r.get('x'), y=r.get('y'), dz=dz))
        report[mp] = dict(status=status, actors=len(rows), findings=findings, hung=len(hung))
        print(f'{mp}: {len(rows)} objets, {len(findings)} a regarder, {len(hung)} accroches en hauteur (voulu)', flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
