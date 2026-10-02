#!/usr/bin/env python3
"""Launchers started from C:\\ the way the owner starts them (cmd, another current directory), with -norun: the engine
loads every lump and compiles ZScript, then exits with code 1337. Checks the exit code, the build each launcher
loads (its path and sha256 in the engine's output), no script error, and that the owner's configuration and saves
are untouched (hashes before / after; a lot's own configuration may only change its date line).

Usage: python scripts/production/launcher_check.py <out.json> <launcher.cmd> [...]
One engine at a time: each run holds the engine lock.
"""
import hashlib, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import engine_lock  # noqa: E402


def tree_hash(paths):
    out = {}
    for p in paths:
        p = Path(p)
        files = [p] if p.is_file() else sorted(x for x in p.rglob('*') if x.is_file()) if p.exists() else []
        for f in files:
            out[str(f.relative_to(ROOT))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def main():
    out_json = Path(sys.argv[1])
    launchers = [Path(a).resolve() for a in sys.argv[2:]]
    watched = [ROOT / 'user' / 'uzdoom.ini', ROOT / 'user' / 'savegames', ROOT / 'user' / 'savegames_cumul',
               ROOT / 'user' / 'savegames_art_review']
    before = tree_hash(watched)
    results = []
    for l in launchers:
        text = l.read_text(encoding='utf-8', errors='replace')
        pk3_line = next((x for x in text.splitlines() if x.lower().startswith('rem') and '.pk3' in x), '')
        with engine_lock.hold('opus', f'lanceur {l.name} -norun'):
            t0 = time.time()
            r = subprocess.run(['cmd', '/c', str(l), '-norun', '-stdout'], cwd='C:\\', capture_output=True, text=True,
                               errors='replace', timeout=300)
        log = r.stdout + r.stderr
        if 'adding' not in log.lower():          # a bench launcher sends the engine's output to its own log file
            fresh = [f for f in (ROOT / 'user').glob('logs_*/*.log') if f.stat().st_mtime >= t0 - 1]
            if fresh:
                log += max(fresh, key=lambda f: f.stat().st_mtime).read_text(encoding='utf-8', errors='replace')
        loaded = [x.strip() for x in log.splitlines() if '.pk3' in x.lower() and ('adding' in x.lower() or 'w_' in x.lower() or 'file' in x.lower())]
        errors = [x for x in log.splitlines() if 'Script error' in x or 'error' in x.lower() and ('zscript' in x.lower() or 'fatal' in x.lower())]
        m = re.search(r'(dist\\[\w\\.-]+\.pk3)', pk3_line)
        declared_rel = m.group(1).replace('\\', '/') if m else None
        # None: the launcher names no build in a rem line (the accepted review launcher reads LATEST.txt): see 'loaded'
        right_build = None if not declared_rel else any(declared_rel.lower() in x.replace('\\', '/').lower() for x in loaded)
        results.append(dict(launcher=str(l.relative_to(ROOT)), code=r.returncode, right_build=right_build,
                            ok=r.returncode == 1337 and not errors and right_build is not False,
                            seconds=round(time.time() - t0, 1), declared=pk3_line, loaded=loaded[-3:], errors=errors[:5]))
        print(l.name, r.returncode, 'OK' if results[-1]['ok'] else 'FAIL', loaded[-1:] if loaded else '', flush=True)
    after = tree_hash(watched)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    rec = dict(at=time.strftime('%Y-%m-%d %H:%M'), from_dir='C:\\', results=results, owner_files_changed=changed,
               ok=all(x['ok'] for x in results) and not changed)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('LANCEURS:', 'PASS' if rec['ok'] else 'FAIL', 'fichiers du proprietaire modifies:', changed)
    return 0 if rec['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
