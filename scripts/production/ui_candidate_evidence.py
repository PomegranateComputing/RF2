#!/usr/bin/env python3
"""UI evidence of a frozen candidate build: every menu screen, pause, save list, confirmation and death screen
at several window sizes and aspect ratios, plus the two menu navigation tests (Continuer, Nouvelle partie).

Usage: python scripts/production/ui_candidate_evidence.py <candidate folder>
Writes <candidate folder>/evidence/ui/<WxH>/*.png and evidence/ui/navigation.txt
"""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import devrun  # noqa: E402

folder = Path(sys.argv[1]).resolve()
pk3 = next(folder.glob('*.pk3'))
out = folder / 'evidence' / 'ui'
out.mkdir(parents=True, exist_ok=True)
import os
sizes = [] if os.environ.get('RF_UIEV_NAV_ONLY') else ((1920, 1080), (2560, 1440), (2560, 1080), (1440, 1080))
for w, h in sizes:
    dest = out / f'{w}x{h}'
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()
    for name, mapname, mode in (('title', None, '2'), ('game', 'RF01', '1'), ('death', 'RF01', '6')):
        _, _, shots = devrun.run(pk3, f'uiev_{name}', mapname, seconds=90, extra=['+rf_dev_ui', mode], width=w, height=h, quiet=True)
        for i, p in enumerate(sorted(shots.glob('*.png'))):
            shutil.copy(p, dest / f'{name}_{i + 1:02d}.png')
    print(w, h, len(list(dest.glob('*.png'))), 'captures')
lines = []
# A save made by this very build (saves of another pk3 are flagged missing-files and Continuer ignores them):
# RF01 by the autopilot up to waypoint 5, autosaved there, then the process is stopped.
status, text, _ = devrun.run(pk3, 'uiev_nav_save', 'RF01', autopilot=True, seconds=120, speed=4,
                             extra=['+rf_dev_save_at', '5'], marker='RF_DEV_SAVE_REQUESTED', quiet=True)
lines.append(f'save by this build: {status}')
import time; time.sleep(2)
for name, mode in (('continuer', '7'), ('nouvelle_partie', '8')):
    status, text, _ = devrun.run(pk3, f'uiev_nav_{name}', None, seconds=60, marker='RF_DEV_MENU_RESULT', extra=['+rf_dev_ui', mode], width=1920, height=1080, quiet=True)
    result = [l for l in text.splitlines() if l.startswith('RF_DEV_MENU_RESULT')][:1]
    lines.append(f'{name}: {status} {result}')
(out / 'navigation.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
