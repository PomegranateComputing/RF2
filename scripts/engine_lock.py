#!/usr/bin/env python3
"""One UZDoom session at a time on this machine, whoever runs it (Opus, Codex): a lock file every runner honours.

Why: the agents share one GPU, and two engines also disturb each other's timing, captures and audio capture.
C:\\PROJECTS\\RF2_MOTEUR.lock names the holder (agent, task, pid of the holding process, start time). A runner
creates it exclusively before starting the engine and deletes it once the engine has exited. A lock whose process is
gone, or older than MAX_AGE, is stale: it is taken over and the takeover is printed.

In Python:   with engine_lock.hold('opus', 'e2e RF04'): ...start and wait for the engine...
Command:     python scripts/engine_lock.py --agent codex --task "apercu RF04" -- <command and its arguments>
             (waits for the lock, runs the command, releases the lock; the command's exit code is returned)
State:       python scripts/engine_lock.py --status
"""
import argparse, contextlib, ctypes, json, os, subprocess, sys, time
from pathlib import Path

LOCK = Path(r'C:\PROJECTS\RF2_MOTEUR.lock')
MAX_AGE = 3 * 3600          # seconds; no single engine session of this project lasts that long
POLL = 2.0


def _alive(pid):
    """True when a process with this pid exists (Windows API; never signals the process)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if os.name != 'nt':
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
    k32.CloseHandle(h)
    return bool(ok) and code.value == 259             # STILL_ACTIVE


def read():
    try:
        return json.loads(LOCK.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


def _stale(info):
    if info is None:
        return True
    return not _alive(info.get('pid')) or time.time() - float(info.get('since', 0)) > MAX_AGE


def acquire(agent, task, wait=6 * 3600, quiet=False):
    info = dict(agent=agent, task=task, pid=os.getpid(), since=time.time(), started=time.strftime('%Y-%m-%d %H:%M:%S'))
    deadline = time.time() + wait
    announced = False
    while True:
        try:
            fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False)
            return info
        except FileExistsError:
            other = read()
            if _stale(other):
                if not quiet:
                    print(f'[engine_lock] verrou perime repris : {other}')
                try:
                    LOCK.unlink()
                except OSError:
                    pass
                continue
            if not announced and not quiet:
                print(f"[engine_lock] moteur occupe par {other.get('agent')} ({other.get('task')}) depuis {other.get('started')} ; attente")
                announced = True
            if time.time() > deadline:
                raise TimeoutError(f'moteur toujours occupe : {other}')
            time.sleep(POLL)


def release(info):
    current = read()
    if current and current.get('pid') == info.get('pid') and current.get('since') == info.get('since'):
        try:
            LOCK.unlink()
        except OSError:
            pass


@contextlib.contextmanager
def hold(agent, task, wait=6 * 3600, quiet=False):
    info = acquire(agent, task, wait, quiet)
    try:
        yield info
    finally:
        release(info)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--agent', default='opus')
    ap.add_argument('--task', default='')
    ap.add_argument('--status', action='store_true')
    ap.add_argument('command', nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if a.status:
        info = read()
        print('libre' if info is None else f"{'PERIME ' if _stale(info) else ''}{info}")
        return 0
    cmd = a.command[1:] if a.command and a.command[0] == '--' else a.command
    if not cmd:
        ap.error('commande manquante (apres --)')
    with hold(a.agent, a.task or ' '.join(cmd)[:80]):
        return subprocess.call(cmd)


if __name__ == '__main__':
    sys.exit(main())
