#!/usr/bin/env python3
"""Start a process on a separate, invisible Windows desktop (shared-machine etiquette).

Another session may need the interactive desktop undisturbed: a process created on its own
desktop (CreateDesktop) never shows a window there and never takes focus. Output goes to a log
file. Used by devrun.py when RF_DEV_HIDDEN=1, and by hidden_norun.py.
"""
import ctypes, threading
from ctypes import wintypes

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
u32 = ctypes.WinDLL('user32', use_last_error=True)
u32.CreateDesktopW.restype = wintypes.HANDLE
k32.CreateFileW.restype = wintypes.HANDLE
DESKTOP = 'rf2_hidden'


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('nLength', wintypes.DWORD), ('lpSecurityDescriptor', wintypes.LPVOID), ('bInheritHandle', wintypes.BOOL)]


class STARTUPINFO(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('lpReserved', wintypes.LPWSTR), ('lpDesktop', wintypes.LPWSTR),
                ('lpTitle', wintypes.LPWSTR), ('dwX', wintypes.DWORD), ('dwY', wintypes.DWORD),
                ('dwXSize', wintypes.DWORD), ('dwYSize', wintypes.DWORD), ('dwXCountChars', wintypes.DWORD),
                ('dwYCountChars', wintypes.DWORD), ('dwFillAttribute', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                ('wShowWindow', wintypes.WORD), ('cbReserved2', wintypes.WORD), ('lpReserved2', ctypes.c_void_p),
                ('hStdInput', wintypes.HANDLE), ('hStdOutput', wintypes.HANDLE), ('hStdError', wintypes.HANDLE)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [('hProcess', wintypes.HANDLE), ('hThread', wintypes.HANDLE), ('dwProcessId', wintypes.DWORD),
                ('dwThreadId', wintypes.DWORD)]


WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def _capture(desk, hwnd, png):
    """Save a window of the hidden desktop as PNG (its text is drawn, not readable as controls)."""
    g32 = ctypes.WinDLL('gdi32')
    u32.SetThreadDesktop(desk)
    u32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))                   # real pixel size
    r = wintypes.RECT()
    u32.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    if w <= 0 or h <= 0:
        return
    screen = u32.GetDC(None)
    dc = g32.CreateCompatibleDC(screen)
    bmp = g32.CreateCompatibleBitmap(screen, w, h)
    g32.SelectObject(dc, bmp)
    u32.PrintWindow(hwnd, dc, 2)                                             # PW_RENDERFULLCONTENT
    header = (ctypes.c_uint32 * 10)(40, w, (-h) & 0xFFFFFFFF, 1 | (32 << 16), 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    g32.GetDIBits(dc, bmp, 0, h, buf, header, 0)
    g32.DeleteObject(bmp)
    g32.DeleteDC(dc)
    u32.ReleaseDC(None, screen)
    try:
        from PIL import Image
        Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1).convert('RGB').save(str(png))
    except ImportError:
        pass


def _quote(a):
    a = str(a)
    return f'"{a}"' if (' ' in a or not a) else a


class HiddenProcess:
    """Minimal Popen-like handle: poll(), kill(), wait()."""

    def __init__(self, args, log_path, cwd=None):
        self.desk = u32.CreateDesktopW(DESKTOP, None, None, 0, 0x10000000, None)   # GENERIC_ALL
        if not self.desk:
            raise OSError(f'CreateDesktop failed: {ctypes.get_last_error()}')
        sa = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
        self.log = k32.CreateFileW(str(log_path), 0x40000000, 1 | 2, ctypes.byref(sa), 2, 0x80, None)
        si = STARTUPINFO()
        si.cb = ctypes.sizeof(STARTUPINFO)
        si.lpDesktop = DESKTOP
        si.dwFlags = 0x100                                                          # STARTF_USESTDHANDLES
        si.hStdOutput = self.log
        si.hStdError = self.log
        self.pi = PROCESS_INFORMATION()
        cmd = ' '.join(_quote(a) for a in args)
        if not k32.CreateProcessW(None, ctypes.create_unicode_buffer(cmd), None, None, True, 0, None,
                                  None if cwd is None else str(cwd), ctypes.byref(si), ctypes.byref(self.pi)):
            raise OSError(f'CreateProcess failed: {ctypes.get_last_error()}')
        self.returncode = None

    def poll(self):
        if self.returncode is None and k32.WaitForSingleObject(self.pi.hProcess, 0) == 0:
            code = wintypes.DWORD()
            k32.GetExitCodeProcess(self.pi.hProcess, ctypes.byref(code))
            self.returncode = code.value
            self._close()
        return self.returncode

    def wait(self, timeout_s=None):
        k32.WaitForSingleObject(self.pi.hProcess, 0xFFFFFFFF if timeout_s is None else int(timeout_s * 1000))
        return self.poll()

    def fatal_error(self, png=None):
        """True when the engine shows its "Fatal Error" window; the window is saved to `png`."""
        found = []

        def cb(hw, _):
            pid = wintypes.DWORD()
            u32.GetWindowThreadProcessId(hw, ctypes.byref(pid))
            buf = ctypes.create_unicode_buffer(256)
            u32.GetWindowTextW(hw, buf, 256)
            if pid.value == self.pi.dwProcessId and buf.value.startswith('Fatal Error'):
                found.append(hw)
            return True
        if self.desk and self.pi.dwProcessId:
            u32.EnumDesktopWindows(self.desk, WNDENUMPROC(cb), 0)
        if found and png:
            t = threading.Thread(target=_capture, args=(self.desk, found[0], png))
            t.start()
            t.join(10)
        return bool(found)

    def kill(self):
        if self.returncode is None:
            k32.TerminateProcess(self.pi.hProcess, 1)
            k32.WaitForSingleObject(self.pi.hProcess, 5000)
            self.poll()

    def _close(self):
        for h in (self.pi.hProcess, self.pi.hThread, self.log):
            if h:
                k32.CloseHandle(h)
        self.pi.hProcess = self.pi.hThread = self.log = None
        if self.desk:
            u32.CloseDesktop(self.desk)
            self.desk = None
