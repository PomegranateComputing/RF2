"""Placeholder images and sounds for the RF2 arsenal test bench (W03 Manufrance Rapid, W04 Manurhin MR73).

They stand in for Astra's exports until a delivery exists, so that the bench can prove its mechanics: every frame is
a labelled drawing (image name, sequences that use it, tics, event) on the FAL canvas convention (1536x1024), the
pump fore-end really moves, the revolver's cylinder really swings out and shows its six chambers, the chamber layers
line up with the open cylinder. Sounds are short synthetic cues, one per event, at modest level (-6 dBFS for shots):
they make the timing audible, they are not sound design. Nothing here is meant for the campaign.
"""
import math, random, struct, zlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1536, 1024
METAL, METAL_D, WOOD, WOOD_D = (74, 76, 80, 255), (46, 47, 50, 255), (112, 74, 42, 255), (84, 54, 30, 255)
HAND, SLEEVE, BRASS, RED = (206, 170, 140, 255), (20, 20, 22, 255), (196, 160, 70, 255), (150, 34, 30, 255)


def _font(size):
    for name in ('arialbd.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


class Pose:
    """Rotation about a pivot (degrees; positive lifts the muzzle, i.e. counter-clockwise on screen), then translation."""
    def __init__(self, dx=0, dy=0, deg=0, pivot=(1040, 800)):
        self.dx, self.dy, self.a, self.p = dx, dy, math.radians(-deg), pivot     # screen y points down

    def __call__(self, pts):
        px, py = self.p
        c, s = math.cos(self.a), math.sin(self.a)
        out = []
        for x, y in pts:
            x, y = x - px, y - py
            out.append((px + x * c + y * s + self.dx, py - x * s + y * c + self.dy))
        return out


def _bar(p0, p1, width):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * width / 2, (x1 - x0) / L * width / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]


def _ellipse(c, rx, ry, n=28):
    return [(c[0] + rx * math.cos(2 * math.pi * k / n), c[1] + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _plate(d, lines):
    d.rectangle((40, 876, 900, 1012), fill=(0, 0, 0, 170))
    d.text((56, 884), lines[0], font=_font(34), fill=(255, 210, 90, 255))
    for i, line in enumerate(lines[1:4]):
        d.text((56, 928 + 26 * i), line, font=_font(22), fill=(235, 235, 235, 255))


def _flash(d, at, size=1.0):
    x, y = at
    pts = []
    for k in range(16):
        r = (95 if k % 2 == 0 else 38) * size
        a = 2 * math.pi * k / 16
        pts.append((x + r * math.cos(a) * 1.3, y + r * math.sin(a)))
    d.polygon(pts, fill=(255, 190, 70, 235))
    d.polygon(_ellipse(at, 34 * size, 26 * size), fill=(255, 245, 200, 255))


# ------------------------------------------------------------------ W03 Manufrance Rapid (pump)
RAPID_POSES = {
    'READY_00': Pose(), 'FIRE_00': Pose(0, -30, 3), 'RECOIL_00': Pose(0, -18, 2), 'RECOIL_01': Pose(0, -5, 0.5),
    'PUMP_00': Pose(), 'PUMP_01': Pose(0, 6, -1), 'PUMP_02': Pose(0, 4, -0.5), 'PUMP_03': Pose(),
    'RELOAD_00': Pose(-40, 50, -10), 'RELOAD_01': Pose(-90, 110, -20),
    'SHELL_00': Pose(-90, 110, -20), 'SHELL_01': Pose(-90, 110, -20), 'SHELL_02': Pose(-90, 110, -20),
}
RAPID_PUMP = {'PUMP_01': 105, 'PUMP_02': 60}          # fore-end travel toward the receiver, px
RAPID_MUZZLE = (372, 246)


def draw_rapid(name):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == 'FLASH_00':
        _flash(d, RAPID_POSES['FIRE_00']([RAPID_MUZZLE])[0], 1.25)
        return im
    T = RAPID_POSES[name]
    M, R = RAPID_MUZZLE, (900, 560)
    t0, t1 = (430, 300), (860, 600)
    along = ((t1[0] - t0[0]), (t1[1] - t0[1]))
    L = math.hypot(*along)
    u = (along[0] / L, along[1] / L)
    travel = RAPID_PUMP.get(name, 0)
    f0 = _lerp(t0, t1, 0.30); f1 = _lerp(t0, t1, 0.54)
    f0 = (f0[0] + u[0] * travel, f0[1] + u[1] * travel); f1 = (f1[0] + u[0] * travel, f1[1] + u[1] * travel)
    fc = _lerp(f0, f1, 0.5)
    d.polygon(T([(1060, 600), (1536, 770), (1536, 1024), (1210, 1024), (1040, 740)]), fill=WOOD)           # stock
    d.polygon(T(_bar(t0, t1, 22)), fill=METAL_D)                                                            # tube
    d.polygon(T(_bar(M, R, 26)), fill=METAL)                                                                # barrel
    d.polygon(T([(850, 495), (1085, 598), (1062, 735), (826, 642)]), fill=METAL)                            # receiver
    if name.startswith(('RELOAD', 'SHELL')):
        d.polygon(T([(900, 650), (1010, 690), (1000, 712), (890, 672)]), fill=(10, 10, 10, 255))            # loading port
    d.polygon(T([(1000, 690), (1092, 722), (1082, 862), (1012, 842)]), fill=WOOD_D)                         # grip
    d.polygon(T(_bar(f0, f1, 50)), fill=WOOD)                                                               # fore-end
    for k in range(6):                                                                                      # grooves
        g = _bar(_lerp(f0, f1, 0.12 + 0.14 * k), _lerp(f0, f1, 0.13 + 0.14 * k), 44)
        d.line(T([g[0], g[3]]), fill=WOOD_D, width=4)
    # right hand on the grip, sleeve to the bottom-right edge
    d.polygon(T([(1000, 800), (1130, 830), (1330, 1024), (880, 1024)]), fill=SLEEVE)
    d.polygon(T(_ellipse((1046, 790), 62, 50)), fill=HAND)
    # left hand: on the fore-end, or bringing a shell to the port
    if name.startswith('SHELL'):
        hand = {'SHELL_00': (860, 760), 'SHELL_01': (930, 712), 'SHELL_02': (820, 800)}[name]
        d.polygon(T([(hand[0] - 50, hand[1] + 10), (hand[0] + 40, hand[1] + 40), (430, 1024), (0, 1024), (0, 930)]), fill=SLEEVE)
        if name != 'SHELL_02':
            depth = 0 if name == 'SHELL_00' else 40
            s0 = (hand[0] + 20 + depth, hand[1] - 50 + depth * 0.4)
            d.polygon(T(_bar(s0, (s0[0] + 70, s0[1] + 28), 26)), fill=RED)
            d.polygon(T(_bar((s0[0] + 70, s0[1] + 28), (s0[0] + 88, s0[1] + 35), 28)), fill=BRASS)
        d.polygon(T(_ellipse(hand, 56, 44)), fill=HAND)
    else:
        d.polygon(T([(fc[0] - 50, fc[1] + 20), (fc[0] + 40, fc[1] + 48), (420, 1024), (0, 1024), (0, 900)]), fill=SLEEVE)
        d.polygon(T(_ellipse((fc[0], fc[1] + 18), 58, 44)), fill=HAND)
    return im


# ------------------------------------------------------------------ W04 Manurhin MR73 (revolver)
MR_POSES = {
    'READY_00': Pose(0, 0, 0, (1000, 800)), 'DRY_00': Pose(0, 3, 0, (1000, 800)),
    'FIRE_00': Pose(0, -28, 6, (1000, 800)), 'RECOIL_00': Pose(0, -38, 9, (1000, 800)), 'RECOIL_01': Pose(0, -10, 3, (1000, 800)),
    'OPEN_00': Pose(-10, 20, -8, (1000, 800)), 'OPEN_01': Pose(-30, 40, -16, (1000, 800)), 'OPEN_02': Pose(-50, 60, -25, (1000, 800)),
    'EJECT_00': Pose(-20, 10, 40, (1000, 800)), 'EJECT_01': Pose(-30, 30, 30, (1000, 800)),
    'LOAD_00': Pose(-50, 60, -25, (1000, 800)), 'LOAD_01': Pose(-50, 60, -25, (1000, 800)),
    'CLOSE_00': Pose(-40, 50, -20, (1000, 800)), 'CLOSE_01': Pose(-15, 20, -8, (1000, 800)),
}
MR_MUZZLE = (548, 466)
MR_OPEN = {'OPEN_01': 0.5, 'OPEN_02': 1.0, 'EJECT_00': 1.0, 'EJECT_01': 1.0, 'LOAD_00': 1.0, 'LOAD_01': 1.0}
MR_FACE = (660, 700)       # centre of the open cylinder face (canvas), identical in LOAD_00, LOAD_01 and the layers
MR_RING, MR_CHAMBER = 54, 19


def chamber_pos(n):
    a = math.radians(90 + 60 * (n - 1))
    return (MR_FACE[0] + MR_RING * math.cos(a), MR_FACE[1] - MR_RING * math.sin(a))


def draw_mr73(name):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == 'FLASH_00':
        _flash(d, MR_POSES['FIRE_00']([MR_MUZZLE])[0], 0.9)
        return im
    if name.startswith('CHAMBER_'):
        n = int(name.split('_')[1])
        c = chamber_pos(n)
        d.polygon(_ellipse(c, MR_CHAMBER - 2, MR_CHAMBER - 2), fill=BRASS)
        d.polygon(_ellipse(c, 6, 6), fill=(150, 120, 60, 255))
        d.text((c[0] - 8, c[1] - 12), str(n), font=_font(18), fill=(40, 30, 10, 255))
        return im
    T = MR_POSES[name]
    open_t = MR_OPEN.get(name, 0.0)
    d.polygon(T([(930, 620), (1012, 648), (1062, 862), (960, 866)]), fill=WOOD)                              # grip
    d.polygon(T([(760, 518), (935, 560), (962, 652), (782, 640)]), fill=METAL)                               # frame
    d.polygon(T(_bar((770, 548), MR_MUZZLE, 34)), fill=METAL)                                                 # barrel
    d.polygon(T(_bar((770, 526), (560, 452), 10)), fill=METAL_D)                                              # rib
    if open_t < 1.0:
        cc = _lerp((846, 590), (760, 680), open_t)
        d.polygon(T(_bar((cc[0] - 70, cc[1] - 18), (cc[0] + 70, cc[1] + 18), 88)), fill=METAL_D)             # cylinder
        for k in range(3):
            d.line(T([(cc[0] - 55, cc[1] - 26 + 22 * k), (cc[0] + 55, cc[1] + 2 + 22 * k)]), fill=(30, 30, 32, 255), width=5)
    else:
        d.polygon(T(_bar((770, 600), (700, 660), 16)), fill=METAL_D)                                          # crane
        if name.startswith('LOAD'):
            d.polygon(_ellipse(MR_FACE, 88, 88), fill=METAL_D)                                                # cylinder face
            for n in range(1, 7):
                d.polygon(_ellipse(chamber_pos(n), MR_CHAMBER, MR_CHAMBER), fill=(8, 8, 8, 255))
            d.polygon(_ellipse(MR_FACE, 12, 12), fill=METAL)
        else:
            face = T([(700, 660)])[0]
            d.polygon(_ellipse(face, 80, 80), fill=METAL_D)
            for n in range(6):
                a = math.radians(90 + 60 * n)
                d.polygon(_ellipse((face[0] + 50 * math.cos(a), face[1] - 50 * math.sin(a)), 17, 17), fill=(8, 8, 8, 255))
    if name.startswith('EJECT'):
        fall = 0 if name == 'EJECT_00' else 90
        rnd = random.Random(7)
        for k in range(6):
            x, y = 640 + rnd.randint(-70, 70), 760 + fall + rnd.randint(0, 80)
            d.polygon(_bar((x, y), (x + 14, y + 44), 16), fill=BRASS)
    # hands and sleeves: right hand on the grip; left hand supports, or feeds a round when loading
    d.polygon(T([(960, 820), (1100, 840), (1330, 1024), (860, 1024)]), fill=SLEEVE)
    d.polygon(T(_ellipse((1012, 770), 64, 54)), fill=HAND)
    if name == 'LOAD_01':
        hand = (590, 800)
        d.polygon([(hand[0] - 60, hand[1] + 10), (hand[0] + 40, hand[1] + 50), (420, 1024), (0, 1024), (0, 940)], fill=SLEEVE)
        d.polygon(_ellipse(hand, 58, 46), fill=HAND)
        c = chamber_pos(1)
        d.polygon(_bar((hand[0] + 20, hand[1] - 30), (c[0] - 8, c[1] + 26), 20), fill=BRASS)
    else:
        lh = T([(940, 840)])[0] if not name.startswith(('LOAD', 'OPEN_02', 'EJECT')) else (640, 860)
        d.polygon([(lh[0] - 60, lh[1] + 10), (lh[0] + 40, lh[1] + 50), (460, 1024), (0, 1024), (0, 960)], fill=SLEEVE)
        d.polygon(_ellipse(lh, 58, 44), fill=HAND)
    return im


def make_images(anim, out_root):
    """Every image named by the animation (frames, flash, chamber layers), labelled; returns {image: path}."""
    uses = {}
    for seq, frames in anim['sequences'].items():
        for f in frames:
            label = f"{seq} {f['tics']} t" + (f" [{f['event']}]" if f.get('event') else '')
            uses.setdefault(f['image'], []).append(label)
    uses.setdefault(anim['flash']['image'], []).append(f"flash {anim['flash']['tics']} t")
    for layer in anim.get('chamber_layers', []):
        uses.setdefault(layer, []).append('couche de chambre')
    draw = draw_rapid if anim['kind'] == 'pump' else draw_mr73
    paths = {}
    for image, labels in uses.items():
        im = draw(image)
        if image != anim['flash']['image'] and not image.startswith('CHAMBER_'):
            _plate(ImageDraw.Draw(im), [f"{anim['weapon']} {anim['name'].split(' (')[0]} - IMAGE PROVISOIRE",
                                        f"{image}", '; '.join(labels)[:80], '; '.join(labels)[80:160]])
        rel = anim['file_prefix'] + image + '.png'
        path = Path(out_root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path)
        paths[image] = rel
    return paths


def make_target(path):
    """Paper silhouette target on a board, 160x288 px (40x72 units at scale 4)."""
    im = Image.new('RGBA', (160, 288), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((6, 20, 154, 288), fill=(120, 96, 64, 255))
    d.rectangle((14, 28, 146, 280), fill=(232, 226, 206, 255))
    d.ellipse((58, 34, 102, 82), fill=(40, 40, 40, 255))
    d.polygon([(40, 96), (120, 96), (136, 278), (24, 278)], fill=(40, 40, 40, 255))
    for r, col in ((46, (232, 226, 206, 255)), (38, (40, 40, 40, 255)), (26, (232, 226, 206, 255)), (14, (180, 40, 36, 255))):
        d.ellipse((80 - r, 170 - r, 80 + r, 170 + r), fill=col)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


# ------------------------------------------------------------------ sounds (48 kHz, 16-bit mono)
RATE = 48000


def _wav(path, samples):
    peak = max(1e-9, max(abs(s) for s in samples))
    data = b''.join(struct.pack('<h', int(max(-1, min(1, s)) * 32767)) for s in samples)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', 36 + len(data)) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 1, 1, RATE, RATE * 2, 2, 16))
        f.write(b'data' + struct.pack('<I', len(data)) + data)
    return peak


def _norm(s, dbfs):
    peak = max(1e-9, max(abs(v) for v in s))
    g = 10 ** (dbfs / 20) / peak
    return [v * g for v in s]


def _noise(n, rnd, smooth=1):
    s, acc = [], 0.0
    for _ in range(n):
        acc += (rnd.uniform(-1, 1) - acc) / smooth
        s.append(acc)
    return s


def _click(rnd, ms=6, smooth=2):
    n = int(RATE * ms / 1000)
    return [v * math.exp(-5 * i / n) for i, v in enumerate(_noise(n, rnd, smooth))]


def _mix(length_s, parts):
    out = [0.0] * int(RATE * length_s)
    for at, sig, gain in parts:
        o = int(at * RATE)
        for i, v in enumerate(sig):
            if o + i < len(out):
                out[o + i] += v * gain
    return out


def _tone(freq, ms, decay):
    n = int(RATE * ms / 1000)
    return [math.sin(2 * math.pi * freq * i / RATE) * math.exp(-i / (decay * RATE)) for i in range(n)]


def synth(event, variant, heavy):
    rnd = random.Random(zlib.crc32(f'{event}/{variant}/{heavy}'.encode()))     # hash() of a str varies per process
    if event == 'shot':
        n = int(RATE * (0.9 if heavy else 0.7))
        tau = 0.16 if heavy else 0.09
        body = [v * math.exp(-i / (tau * RATE)) for i, v in enumerate(_noise(n, rnd, 3 if heavy else 1.5))]
        thump = [math.sin(2 * math.pi * (58 if heavy else 90) * i / RATE) * math.exp(-i / (0.08 * RATE)) for i in range(n)]
        ring = _tone(1900 + 150 * variant, 300, 0.05) if not heavy else []
        return _norm(_mix(n / RATE, [(0, body, 1.0), (0, thump, 0.8), (0.004, ring, 0.25)]), -6.0)
    if event in ('pump_back', 'pump_fwd'):
        slide = [v * math.sin(math.pi * i / 2400) for i, v in enumerate(_noise(2400, rnd, 4))]
        parts = [(0, _click(rnd, 7), 1.0), (0.012, slide, 0.35), (0.06, _click(rnd, 9, 1.5), 1.2)] if event == 'pump_back' \
            else [(0, slide, 0.35), (0.05, _click(rnd, 9, 1.5), 1.3), (0.058, _tone(900, 60, 0.02), 0.3)]
        return _norm(_mix(0.2, parts), -10.0)
    if event in ('shell_in', 'round_in'):
        return _norm(_mix(0.15, [(0, _click(rnd, 5), 1.0), (0.02, _tone(2600 + 300 * variant, 80, 0.015), 0.4)]), -16.0)
    if event == 'dry':
        return _norm(_mix(0.12, [(0, _click(rnd, 4, 1.2), 1.0), (0.003, _tone(3200, 40, 0.01), 0.3)]), -14.0)
    if event in ('cloth', 'raise'):
        n = int(RATE * 0.32)
        return _norm([v * math.sin(math.pi * i / n) ** 2 for i, v in enumerate(_noise(n, rnd, 6))], -24.0)
    if event == 'cyl_open':
        return _norm(_mix(0.2, [(0, _click(rnd, 6), 1.0), (0.01, _tone(2400, 120, 0.03), 0.35)]), -14.0)
    if event == 'eject':
        return _norm(_mix(0.5, [(0.02 * k + rnd.uniform(0, 0.03), _tone(3000 + 400 * k, 120, 0.02), 0.5) for k in range(6)]
                          + [(0, _click(rnd, 8), 1.0)]), -14.0)
    if event == 'cyl_close':
        return _norm(_mix(0.15, [(0, _click(rnd, 8, 1.3), 1.0), (0.004, _tone(1800, 80, 0.02), 0.4)]), -12.0)
    return _norm(_click(rnd, 6), -18.0)


def make_sounds(anim, out_root):
    """{logical sound: [relative wav paths]} for every event of the animation."""
    folder = 'sounds/bench/' + ('rapid' if anim['kind'] == 'pump' else 'mr73')
    heavy = anim['kind'] == 'pump'
    result = {}
    for event, variants in anim['sounds'].items():
        rels = []
        for i, v in enumerate(variants):
            rel = f'{folder}/{v}.wav'
            _wav(Path(out_root) / rel, synth(event, i, heavy))
            rels.append(rel)
        result[event] = rels
    return result
