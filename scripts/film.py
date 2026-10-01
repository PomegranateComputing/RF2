#!/usr/bin/env python3
"""Video with sound of a real RF01 run, from the engine itself (no screen or speaker capture).

The dev handler (rf_dev_film) takes a screenshot every N tics and prints its millisecond clock;
OpenAL Soft's wave writer records the game's mixed sound to a WAV at the same time (devrun
audio_wav). The player's shots (RF_DEV_SHOT, also on the millisecond clock) are matched to the
transients of the recording, which gives the clock offset between pictures and sound. Frames keep
their measured timing in the video (concat durations); the sound is cut from the same clock.

Usage: python scripts/film.py --name e1_baseline --end 900 [--every 2] [--width 1280 --height 720]
Writes build/dev/film/<name>/<name>.mp4, <name>.wav (16-bit, unchanged gain) and film.json.
The run is the autopilot at real speed (timescale 1): sound pacing is real time.
"""
import argparse, json, re, shutil, struct, subprocess, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import devrun  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PK3 = ROOT / 'dist' / 'RF2_DEV.pk3'


def read_wav(path):
    """Float or 16-bit WAV, tolerating the unfinished header of a writer killed mid-run."""
    d = Path(path).read_bytes()
    i, fmt, off = 12, None, None
    while i < len(d) - 8:
        cid, ln = d[i:i + 4], struct.unpack('<I', d[i + 4:i + 8])[0]
        if cid == b'fmt ':
            fmt = struct.unpack('<HHIIHH', d[i + 8:i + 24])
        if cid == b'data':
            off = i + 8
            break
        i += 8 + ln + (ln & 1)
    _, ch, sr, _, align, bits = fmt
    raw = d[off:off + (len(d) - off) // align * align]
    a = np.frombuffer(raw, dtype=np.float32 if bits == 32 else np.int16).astype(np.float64)
    if bits == 16:
        a /= 32768.0
    return a.reshape(-1, ch), sr


def write_wav16(path, a, sr):
    pcm = (np.clip(a, -1.0, 1.0) * 32767.0).astype('<i2')
    ch = a.shape[1]
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', 36 + pcm.nbytes) + b'WAVE')
        f.write(b'fmt ' + struct.pack('<IHHIIHH', 16, 1, ch, sr, sr * ch * 2, ch * 2, 16))
        f.write(b'data' + struct.pack('<I', pcm.nbytes) + pcm.tobytes())


def onsets(a, sr):
    """Sharp rises of the short-term level (1 ms hop): candidate gunshot starts, in seconds."""
    mono = np.abs(a).max(axis=1)
    hop = sr // 1000
    env = mono[:len(mono) // hop * hop].reshape(-1, hop).max(axis=1)
    db = 20 * np.log10(env + 1e-9)
    out, last = [], -1.0
    for k in range(8, len(db)):
        if db[k] > -25 and db[k] - db[k - 8:k].min() > 18 and k / 1000 - last > 0.05:
            out.append(k / 1000.0)
            last = k / 1000.0
    return out


def sync_onset(a, sr, freq=1000.0, dur=0.04):
    """Start (s) of the 40 ms 1 kHz sync tone: peak of a matched filter over the first 10 s."""
    mono = a[:int(10 * sr)].mean(axis=1)
    t = np.arange(int(dur * sr)) / sr
    kernel = np.sin(2 * np.pi * freq * t)
    kc = np.cos(2 * np.pi * freq * t)
    s = np.convolve(mono, kernel[::-1], mode='valid')
    c = np.convolve(mono, kc[::-1], mode='valid')
    mag = np.sqrt(s * s + c * c)
    k = int(np.argmax(mag))
    return k / sr if mag[k] > 0.05 * len(kernel) * 0.25 else None


def align(shot_ms, starts, earliest_ms):
    """Clock offset (s) = audio time - engine ms/1000 that puts the most shots on an onset.

    The sound device opens during engine start-up, before the first frame of the map: the offset
    lies between -earliest_ms/1000 and 0. Outside that window, footsteps and drips would give
    chance matches."""
    if not shot_ms or not starts:
        return None, 0
    shots = np.array(shot_ms) / 1000.0
    st = np.array(starts)
    best, best_n, best_err = None, -1, 1e9
    for o in st:
        for s0 in shots:
            off = o - s0
            if not (-earliest_ms / 1000.0 - 0.05 <= off <= 0.05):
                continue
            d = np.array([np.min(np.abs(st - (s + off))) for s in shots])
            n, err = int((d < 0.015).sum()), float(d[d < 0.015].sum())
            if n > best_n or (n == best_n and err < best_err):
                best, best_n, best_err = off, n, err
    return best, best_n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', required=True)
    ap.add_argument('--map', default='RF01')
    ap.add_argument('--every', type=int, default=2, help='tics between pictures (2 = 17.5 fps)')
    ap.add_argument('--start', type=int, default=36, help='first filmed tic (the sync tone plays at tic 1)')
    ap.add_argument('--end', type=int, default=900)
    ap.add_argument('--width', type=int, default=1280)
    ap.add_argument('--height', type=int, default=720)
    ap.add_argument('--seconds', type=float, default=240)
    ap.add_argument('--pk3', default=str(PK3), help='the build to film (default: the development build)')
    ap.add_argument('--no-autopilot', action='store_true', help='film a scripted development scene instead of the waypoint run')
    ap.add_argument('extra', nargs='*')
    a = ap.parse_args()
    out = devrun.DEV / 'film' / a.name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    raw_wav = out / 'capture_float.wav'
    extra = ['+rf_dev_film', str(a.every), '+rf_dev_film_start', str(a.start), '+rf_dev_film_end', str(a.end)] + a.extra
    status, text, shots = devrun.run(Path(a.pk3), f'film_{a.name}', a.map, autopilot=not a.no_autopilot, seconds=a.seconds,
                                     width=a.width, height=a.height, extra=extra, marker='RF_DEV_FILM_DONE',
                                     audio_wav=raw_wav)
    frames = [(int(t), float(ms)) for t, ms in re.findall(r'RF_DEV_FILM t=(\d+) ms=([\d.]+)', text)]
    shot_ms = [float(ms) for _, ms in re.findall(r'RF_DEV_SHOT t=(\d+) ms=([\d.]+)', text)]
    pngs = sorted(shots.glob('*.png'))
    report = dict(name=a.name, pk3=a.pk3, status=status, frames_requested=len(frames), frames_written=len(pngs), shots=len(shot_ms))
    if len(pngs) != len(frames):
        report['warning'] = 'frame count differs from requests: timing of some frames is approximate'
    audio, sr = read_wav(raw_wav)
    starts = onsets(audio, sr)
    sync = re.search(r'RF_DEV_SYNC t=1 ms=([\d.]+)', text)
    tone = sync_onset(audio, sr)
    if sync and tone is not None:
        offset, matched = tone - float(sync.group(1)) / 1000.0, 'sync tone'
    else:
        offset, matched = align(shot_ms, starts, frames[0][1] if frames else 0)
    report.update(audio_seconds=round(len(audio) / sr, 2), onsets=len(starts), offset_s=offset, shots_matched=matched)
    n = min(len(pngs), len(frames))
    if n < 2 or offset is None:
        report['error'] = 'not enough frames or no shot to align the sound'
        (out / 'film.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report, indent=2))
        return 1
    lines = []
    for k in range(n):
        dur = (frames[k + 1][1] - frames[k][1]) / 1000.0 if k + 1 < n else a.every / 35.0
        lines.append(f"file '{pngs[k].as_posix()}'")
        lines.append(f'duration {dur:.4f}')
    lines.append(f"file '{pngs[n - 1].as_posix()}'")
    (out / 'frames.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    t0 = offset + frames[0][1] / 1000.0
    t1 = offset + frames[n - 1][1] / 1000.0 + a.every / 35.0
    seg = audio[max(0, int(t0 * sr)):int(t1 * sr)]
    peak = float(np.abs(seg).max()) if len(seg) else 0.0
    wav = out / f'{a.name}.wav'
    write_wav16(wav, seg, sr)
    report.update(audio_from_s=round(t0, 3), audio_to_s=round(t1, 3), segment_peak_dbfs=round(20 * np.log10(peak + 1e-12), 1),
                  clipped_samples=int((np.abs(seg) >= 1.0).sum()), gain='unchanged (engine mix, OpenAL wave writer)')
    mp4 = out / f'{a.name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(out / 'frames.txt'), '-i', str(wav),
           '-vf', 'fps=35,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', str(mp4)]
    subprocess.run(cmd, check=True)
    report['video'] = str(mp4)
    (out / 'film.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
