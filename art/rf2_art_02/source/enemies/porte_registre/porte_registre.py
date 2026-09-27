"""PORTE-REGISTRE — final creature source (RED FLAGS 2 MAP01).

Identity: the archive made ambulant. A tall, narrow clerk whose torso has been replaced by the
records he carried: a strapped vertical stack of bound registers (cloth boards, laminated page
blocks, dark red spine labels), two columns of files rising past the shoulders so the small grey
head sits in a notch between them, a skirt of hanging manila folders at the hips, thin legs in
grey trousers. Leather archive straps and brass buckles hold everything to the body. Long
ink-stained hands. Pince-nez on a broken nose. The silhouette (rectangular mass, twin towers,
small head, stick legs) is unmistakable from shadow alone.

    python porte_registre.py preview | family

Runtime contract (sprite prefix PREG, Scale 0.2):
    A idle | B C D E walk | F telegraph (register raised overhead) | G release (throw)
    N recovery | H pain | I death_1 | J death_2 | K corpse
Projectile sprite (registry shard, tumbling bound register): PRGS A0, B0.
"""
from __future__ import annotations
import json, math, os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_pipeline"))
import sdfrig as S          # noqa: E402
import humanoid as Hm       # noqa: E402

OUT = HERE.parents[1] / "renders/porte_registre"
PREFIX = "PREG"
PPU = 5.0

(M_SKIN, M_VEST, M_TROUSER, M_SHOE, M_EYE, M_HAIR, M_NAIL, M_LEATHER, M_BRASS, M_PAPER, M_BOOK_G, M_BOOK_T, M_BOOK_B, M_LABEL, M_MANILA, M_STEEL, M_SOLE) = range(1, 18)
MATERIALS = {
    M_SKIN: S.Material("skin", (0.52, 0.50, 0.49), rough=0.6, spec=0.16, detail="skin", detail_amp=0.7, sss=0.15),
    M_HAIR: S.Material("hair", (0.22, 0.20, 0.18), rough=0.75, spec=0.12, detail="hair", detail_amp=0.7),
    M_VEST: S.Material("vest", (0.17, 0.16, 0.18), rough=0.9, spec=0.05, detail="cloth", albedo2=(0.11, 0.10, 0.12), detail_amp=0.5),
    M_TROUSER: S.Material("trousers", (0.31, 0.31, 0.32), rough=0.9, spec=0.05, detail="cloth", albedo2=(0.22, 0.22, 0.23), detail_amp=0.5),
    M_SHOE: S.Material("shoe", (0.06, 0.06, 0.06), rough=0.4, spec=0.35, detail="leather", detail_amp=0.4),
    M_SOLE: S.Material("sole", (0.10, 0.09, 0.08), rough=0.85, spec=0.08, detail="rubber"),
    M_EYE: S.Material("eye", (0.05, 0.04, 0.04), rough=0.18, spec=0.5),
    M_NAIL: S.Material("nail", (0.12, 0.12, 0.15), rough=0.35, spec=0.4),
    M_LEATHER: S.Material("leather", (0.24, 0.14, 0.09), rough=0.55, spec=0.3, detail="leather", detail_amp=0.6),
    M_BRASS: S.Material("brass", (0.66, 0.53, 0.28), rough=0.4, spec=0.6),
    M_STEEL: S.Material("steel", (0.55, 0.55, 0.57), rough=0.35, spec=0.7),
    M_PAPER: S.Material("paper", (0.84, 0.80, 0.70), rough=0.95, spec=0.03, detail="paper", albedo2=(0.66, 0.60, 0.46), detail_scale=1.0, detail_amp=0.7),
    M_BOOK_G: S.Material("book_green", (0.12, 0.19, 0.14), rough=0.85, spec=0.08, detail="cloth", albedo2=(0.08, 0.12, 0.09), detail_scale=1.6, detail_amp=0.4),
    M_BOOK_T: S.Material("book_tan", (0.42, 0.34, 0.22), rough=0.85, spec=0.08, detail="cloth", albedo2=(0.30, 0.24, 0.15), detail_scale=1.6, detail_amp=0.4),
    M_BOOK_B: S.Material("book_blue", (0.21, 0.24, 0.30), rough=0.85, spec=0.08, detail="cloth", albedo2=(0.14, 0.16, 0.21), detail_scale=1.6, detail_amp=0.4),
    M_LABEL: S.Material("label", (0.40, 0.09, 0.10), rough=0.7, spec=0.1),
    M_MANILA: S.Material("manila", (0.72, 0.62, 0.44), rough=0.95, spec=0.03, detail="paper", albedo2=(0.58, 0.48, 0.32), detail_scale=1.2, detail_amp=0.6),
}

PROPS = dict(Hm.DEFAULT_PROPS)
PROPS.update(height=78.0, pelvis_z=42.0, spine_len=4.5, chest_len=8.0, neck_len=9.0, head_len=3.2,
             shoulder_y=8.0, clav_z=6.0, upper_arm=15.0, forearm=14.0, hip_y=3.2, thigh=20.0, shin=18.0,
             chest_r=(4.0, 6.5, 7.0), pelvis_r=(3.8, 5.0, 4.2), belly_r=(3.4, 4.2, 3.6),
             upper_arm_r=(2.1, 1.7), forearm_r=(1.9, 1.35), thigh_r=(2.7, 2.1), shin_r=(2.1, 1.5),
             deltoid_r=2.3, neck_r=1.7, trap_r=1.5, scapula_r=(1.2, 2.0, 2.6),
             foot_len=9.0, foot_w=3.2, foot_h=2.6)
BOOK_MATS = [M_BOOK_G, M_BOOK_T, M_BOOK_B, M_BOOK_G, M_BOOK_T]


def add_book(rig, bone, center, hx, hy, hz, yaw, mat, label=False, group="files", rot_extra=None):
    """a bound register: two cloth boards + spine on +X, laminated page block showing on -X and ±Y"""
    R = S.rot_z(yaw) if rot_extra is None else rot_extra @ S.rot_z(yaw)
    c = np.asarray(center, np.float32)
    def off(v):
        return c + R @ np.asarray(v, np.float32)
    rig.add("rbox", bone, off((0, 0, hz - 0.22)), (hx, hy, 0.22, 0.12), mat, rot=R, group=group, blend=0.0)
    rig.add("rbox", bone, off((0, 0, -hz + 0.22)), (hx, hy, 0.22, 0.12), mat, rot=R, group=group, blend=0.0)
    rig.add("rbox", bone, off((hx - 0.35, 0, 0)), (0.35, hy, hz, 0.3), mat, rot=R, group=group, blend=0.0)         # spine (front)
    rig.add("rbox", bone, off((-0.3, 0, 0)), (hx - 0.6, hy - 0.35, hz - 0.35, 0.1), M_PAPER, rot=R, group=group, blend=0.0)  # pages
    if label:
        rig.add("rbox", bone, off((hx + 0.02, 0, 0.1)), (0.08, hy * 0.42, hz * 0.45, 0.05), M_LABEL, rot=R, group="labels", blend=0.0)


def add_stack(rig, rng, bone="chest", z0=-11.5, count=8, hx=5.6, hy=7.6, hz=1.55, x=1.2):
    z = z0
    for i in range(count):
        yaw = rng.uniform(-7, 7)
        dx = rng.uniform(-0.6, 0.6); dy = rng.uniform(-0.9, 0.9)
        add_book(rig, bone, (x + dx, dy, z + hz), hx, hy, hz, yaw, BOOK_MATS[i % 5], label=(i % 3 == 1))
        z += 2 * hz + 0.12
    return z


def add_tower(rig, rng, sy, bone="chest", z0=2.0, count=7, hx=3.4, hy=3.6, hz=1.15, x=-4.6, y=8.6):
    """column of files strapped behind each shoulder (the arms hang in front of it)"""
    z = z0
    for i in range(count):
        yaw = rng.uniform(-9, 9)
        add_book(rig, bone, (x + rng.uniform(-0.4, 0.4), sy * y + rng.uniform(-0.4, 0.4), z + hz), hx, hy, hz, yaw, BOOK_MATS[(i + 2) % 5], label=(i % 2 == 0), group=f"tower{sy}")
        z += 2 * hz + 0.1
    rig.add("rbox", bone, (x, sy * y, z0 + (z - z0) / 2), (hx + 0.5, hy + 0.5, 0.5, 0.2), M_LEATHER, group=f"tstrap{sy}", blend=0.0)
    rig.add("rbox", bone, (x, sy * y, z0 + (z - z0) / 2), (hx - 0.2, hy - 0.2, 0.9, 0.2), M_LEATHER, group=f"tstrap{sy}", blend=0.0, op="subtract")


def add_skirt(rig, rng, bone="root", n=14, radius=7.2, z_top=-1.0, h=7.0):
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.1, 0.1)
        cx, cy = radius * math.cos(a), radius * math.sin(a)
        R = S.rot_z(math.degrees(a)) @ S.rot_y(-9 + rng.uniform(-4, 4))
        mat = M_MANILA if i % 3 else M_PAPER
        rig.add("rbox", bone, (cx, cy, z_top - h / 2), (0.16, 3.1, h / 2, 0.1), mat, rot=R, group="skirt", blend=0.0)
        rig.add("rbox", bone, (cx * 0.97, cy * 0.97, z_top - h / 2 + 0.3), (0.10, 2.9, h / 2 - 0.4, 0.05), M_PAPER, rot=R, group="skirt", blend=0.0)


def add_register_in_hand(rig, side="r"):
    """the register about to be thrown, held against the palm of the right hand"""
    add_book(rig, f"wrist_{side}", (2.2, 0.0, -6.0), 3.0, 4.2, 1.4, 0.0, M_BOOK_G, label=True, group="thrown", rot_extra=S.rot_y(90))


def build(curl=0.35, spread=0.15, held=False, seed=7):
    rng = np.random.default_rng(seed)
    rig = S.Rig()
    rig.materials = MATERIALS
    P = PROPS
    Hm.build_skeleton(rig, P)
    M = dict(skin=M_SKIN, torso=M_VEST, pelvis=M_TROUSER, arm_upper=M_VEST, arm_lower=M_SKIN, leg_upper=M_TROUSER, leg_lower=M_TROUSER, shoe=M_SHOE, scalp=M_HAIR, eye=M_EYE)
    Hm.build_body(rig, P, M)
    # the records: main stack around the torso, two towers past the shoulders, harness straps
    ztop = add_stack(rig, rng)
    for sy in (1, -1):
        add_tower(rig, rng, sy)
    for sy in (1, -1):
        y = sy * 3.4
        rig.add("rbox", "chest", (0.9, y, 4.0), (6.9, 0.55, 15.6, 0.3), M_LEATHER, group=f"hstrap{sy}", blend=0.0)
        rig.add("rbox", "chest", (0.9, y, 4.0), (6.1, 0.9, 14.8, 0.3), M_LEATHER, group=f"hstrap{sy}", blend=0.0, op="subtract")
        rig.add("rbox", "chest", (7.9, y, 1.5), (0.5, 1.0, 1.4, 0.2), M_BRASS, group="buckles", blend=0.0)
        # harness over the shoulders to the towers
        rig.capsule_between("chest", (2.0, y, P["clav_z"] + 5.5), (-0.5, sy * 7.5, P["clav_z"] + 2.0), 0.55, M_LEATHER, group="harness", blend=0.0)
    # belt and hanging-folder skirt
    rig.add("torus", "root", (0.2, 0, 1.5), (6.4, 0.6), M_LEATHER, group="belt", blend=0.2)
    add_skirt(rig, rng)
    # head: grey clerk, hair at the sides and back only, pince-nez, thin mouth
    Hm.build_head(rig, M, skull=(4.2, 3.9, 5.1), brow=0.95, gaunt=0.7, nose=1.05, mouth=True, offset=(0.8, 0, 4.6))
    rig.add("ellipsoid", "head", (-1.4, 0, 3.6), (3.4, 4.3, 3.6), M_HAIR, group="hair", blend=0.8)
    rig.add("ellipsoid", "head", (0.6, 0, 6.4), (4.0, 3.6, 3.4), M_SKIN, group="hair", blend=0.8, op="subtract")     # bald crown
    for s in (1, -1):
        rig.add("torus", "head", (4.9, s * 1.6, 4.95), (1.15, 0.13), M_STEEL, group="specs", blend=0.0, rot=S.rot_y(90))
    rig.capsule_between("head", (4.9, -0.5, 5.2), (4.9, 0.5, 5.2), 0.12, M_STEEL, group="specs", blend=0.0)
    # shoe soles
    for side in ("l", "r"):
        rig.add("rbox", f"ankle_{side}", (P["foot_len"] * 0.32, 0, -P["foot_h"] * 0.5 - 1.0), (P["foot_len"] * 0.5, P["foot_w"] * 0.5 + 0.1, 0.5, 0.3), M_SOLE, group=f"foot_{side}", blend=0.4)
    # long ink-stained hands
    Hm.add_hand(rig, "l", M_SKIN, M_NAIL, curl=curl, spread=spread, scale=1.12)
    Hm.add_hand(rig, "r", M_SKIN, M_NAIL, curl=0.75 if held else curl, spread=0.05 if held else spread, scale=1.12)
    if held:
        add_register_in_hand(rig, "r")
    return rig


# ------------------------------------------------------------------ poses
def idle():
    return Hm.merge({"root": (0, 2, 0), "spine": (0, 3, 0), "chest": (0, 3, 0), "neck": (0, 8, 0), "head": (0, -6, 0)},
                    Hm.leg(3, 6, 1, out=2, side="l"), Hm.leg(-3, 5, 0, out=2, side="r"),
                    Hm.arm(swing=6, out=14, elbow=14, side="l", wrist=(0, -10, 0)), Hm.arm(swing=4, out=14, elbow=12, side="r", wrist=(0, -10, 0)))


def walk(phase):
    p = Hm.walk(phase, stride=24, lean=6, arm_swing=10, elbow=12, knee_lift=26)
    p["chest"] = (0, 2, math.sin(phase * 2 * math.pi) * 2)
    p["neck"] = (0, 8, 0); p["head"] = (0, -6, 0)
    for side in ("l", "r"):
        p[f"shoulder_{side}"] = (p[f"shoulder_{side}"][0] - (14 if side == "l" else -14) * 0, p[f"shoulder_{side}"][1], 0)
    return p


def telegraph():
    return Hm.merge({"root": (0, -4, 0), "spine": (0, -6, 0), "chest": (0, -8, 0), "neck": (0, -12, 0), "head": (0, -6, 0)},
                    Hm.leg(-8, 12, -4, out=4, side="l"), Hm.leg(10, 16, 4, out=4, side="r"),
                    Hm.arm(swing=165, out=22, elbow=48, side="r", wrist=(0, -30, 0)), Hm.arm(swing=150, out=30, elbow=60, side="l", wrist=(0, -20, 0)))


def release():
    return Hm.merge({"root": (0, 10, 6), "spine": (0, 10, 4), "chest": (0, 12, 6), "neck": (0, 14, 0), "head": (0, -4, 0)},
                    Hm.leg(26, 20, 6, out=3, side="l"), Hm.leg(-26, 8, 16, out=4, side="r"),
                    Hm.arm(swing=92, out=6, elbow=6, side="r", wrist=(0, -40, 0)), Hm.arm(swing=-30, out=30, elbow=50, side="l", wrist=(0, 10, 0)))


def recovery():
    return Hm.merge({"root": (0, 4, 2), "spine": (0, 5, 2), "chest": (0, 5, 2), "neck": (0, 8, 0), "head": (0, -6, 0)},
                    Hm.leg(14, 14, 3, out=3, side="l"), Hm.leg(-12, 8, 6, out=4, side="r"),
                    Hm.arm(swing=40, out=12, elbow=20, side="r", wrist=(0, -20, 0)), Hm.arm(swing=-6, out=20, elbow=30, side="l"))


def pain():
    return Hm.merge({"root": (0, -4, -4), "spine": (0, -6, -3), "chest": (0, -8, -5), "neck": (0, -18, 5), "head": (0, -12, 6)},
                    Hm.leg(2, 16, -3, out=5, side="l"), Hm.leg(-6, 12, 0, out=6, side="r"),
                    Hm.arm(swing=28, out=40, elbow=56, side="l", wrist=(0, 10, 0)), Hm.arm(swing=24, out=44, elbow=60, side="r", wrist=(0, 10, 0)))


def death_1():
    return Hm.merge({"root": (0, -8, 4), "spine": (0, -8, 2), "chest": (0, -10, 2), "neck": (0, -10, 0), "head": (0, -16, -6)},
                    Hm.leg(20, 52, -8, out=6, side="l"), Hm.leg(10, 60, -6, out=8, side="r"),
                    Hm.arm(swing=20, out=30, elbow=30, side="l"), Hm.arm(swing=16, out=34, elbow=26, side="r"))


def death_2():
    p = Hm.merge({"spine": (0, 6, 0), "chest": (0, 8, 0), "neck": (0, 10, 0), "head": (0, 6, 20)},
                 Hm.leg(-40, 70, 20, out=10, side="l"), Hm.leg(-30, 60, 24, out=14, side="r"),
                 Hm.arm(swing=40, out=70, elbow=40, side="l", wrist=(0, 20, 0)), Hm.arm(swing=30, out=60, elbow=30, side="r", wrist=(0, 20, 0)))
    p["root_rot"] = Hm.lying(face_down=False, roll=12)
    return p


def corpse():
    p = death_2()
    p["head"] = (0, 8, 40); p["hip_l"] = (-16, 30, 0); p["knee_l"] = (0, 40, 0); p["shoulder_l"] = (-80, -30, 0)
    p["root_rot"] = Hm.lying(face_down=False, roll=18)
    return p


STATES = [
    ("A", "idle", idle, dict()),
    ("B", "walk_1", lambda: walk(0.0), dict()),
    ("C", "walk_2", lambda: walk(0.25), dict()),
    ("D", "walk_3", lambda: walk(0.5), dict()),
    ("E", "walk_4", lambda: walk(0.75), dict()),
    ("F", "telegraph", telegraph, dict(held=True)),
    ("G", "release", release, dict(curl=0.15, spread=0.3)),
    ("N", "recovery", recovery, dict()),
    ("H", "pain", pain, dict(curl=0.2)),
    ("I", "death_1", death_1, dict(curl=0.3)),
    ("J", "death_2", death_2, dict(curl=0.25)),
    ("K", "corpse", corpse, dict(curl=0.2)),
]
ROT_YAW = {r: 180.0 - (r - 1) * 45.0 for r in range(1, 9)}


def build_projectile(tumble=0.0):
    rig = S.Rig(); rig.materials = MATERIALS
    rig.bone("root", None, (0, 0, 6))
    add_book(rig, "root", (0, 0, 0), 3.0, 4.2, 1.4, 0.0, M_BOOK_G, label=True, group="thrown", rot_extra=S.rot_y(tumble) @ S.rot_x(25))
    # loose sheets trailing
    for k in range(3):
        rig.add("rbox", "root", (-2.5 - k * 1.6, (k - 1) * 1.4, 1.2 + k * 0.8), (1.6, 1.1, 0.05, 0.02), M_PAPER, rot=S.rot_y(tumble * 0.5 + k * 25) @ S.rot_x(k * 30), group="sheets", blend=0.0)
    return rig


def render_one(args):
    letter, rot, ppu, out_dir = args
    _, name, pose_fn, kw = next(s for s in STATES if s[0] == letter)
    rig = build(**kw)
    img, ox, oy = S.render(rig, pose_fn(), ROT_YAW[rot], ppu=ppu, ss=2)
    path = Path(out_dir) / f"{PREFIX}{letter}{rot}.png"
    S.save_sprite(img, path, ox, oy)
    return (letter, rot, img.shape[1], img.shape[0], ox, oy)


def preview(ppu=PPU):
    OUT.mkdir(parents=True, exist_ok=True)
    imgs, labs = [], []
    rig = build()
    for rot, lab in ((1, "front"), (2, "3/4"), (3, "side"), (5, "back")):
        img, ox, oy = S.render(rig, idle(), ROT_YAW[rot], ppu=ppu, ss=2)
        imgs.append(img); labs.append(f"idle {lab}")
    for letter in ("C", "F", "G", "H", "I", "K"):
        _, name, fn, kw = next(s for s in STATES if s[0] == letter)
        img, ox, oy = S.render(build(**kw), fn(), ROT_YAW[2], ppu=ppu, ss=2)
        imgs.append(img); labs.append(name)
    for t in (0, 90):
        img, ox, oy = S.render(build_projectile(t), {}, 180, ppu=ppu, ss=2, floor_snap=False)
        imgs.append(img); labs.append(f"shard {t}")
    S.review_sheet(imgs, labs, 4, title="PORTE-REGISTRE — preview (neutral light, software render)", path=OUT / "_preview.png")
    print("preview written", OUT / "_preview.png")


def family(ppu=PPU, workers=None):
    from multiprocessing import Pool
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(letter, rot, ppu, str(OUT)) for (letter, _, _, _) in STATES for rot in range(1, 9)]
    workers = workers or max(1, min(12, (os.cpu_count() or 4) - 2))
    with Pool(workers) as pool:
        results = pool.map(render_one, jobs, chunksize=1)
    shards = []
    for letter, t in (("A", 0.0), ("B", 90.0)):
        img, ox, oy = S.render(build_projectile(t), {}, 180, ppu=ppu, ss=2, floor_snap=False)
        oy = img.shape[0] // 2   # projectile: origin at the sprite centre
        S.save_sprite(img, OUT / f"PRGS{letter}0.png", img.shape[1] // 2, oy)
        shards.append({"file": f"PRGS{letter}0.png", "w": img.shape[1], "h": img.shape[0], "grab": [img.shape[1] // 2, oy]})
    manifest = {"prefix": PREFIX, "scale": round(1.0 / ppu, 6), "pixel_stretch_prerendered": 1.2, "ppu": ppu,
                "states": [{"letter": l, "name": n} for (l, n, _, _) in STATES],
                "sprites": [{"file": f"{PREFIX}{l}{r}.png", "w": w, "h": h, "grab": [ox, oy]} for (l, r, w, h, ox, oy) in results],
                "projectile": {"prefix": "PRGS", "sprites": shards}}
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    sheets(ppu)


def sheets(ppu=PPU):
    from PIL import Image
    load = lambda l, r: np.asarray(Image.open(OUT / f"{PREFIX}{l}{r}.png").convert("RGBA"))
    imgs = [load("A", r) for r in (1, 2, 3, 5)] + [load("C", 2), load("F", 2), load("G", 2), load("H", 2), load("J", 2), load("K", 3)]
    labs = ["FRONT", "3/4", "SIDE", "BACK", "MOVEMENT", "TELEGRAPH", "ATTACK", "PAIN", "DEATH", "CORPSE"]
    S.review_sheet(imgs, labs, 5, title="PORTE-REGISTRE — review sheet (neutral light)", path=OUT / "_review_sheet.png")
    rows = []
    for (l, n, _, _) in STATES:
        rows += [load(l, r) for r in range(1, 9)]
    S.review_sheet(rows, [f"{l}{r}" for (l, _, _, _) in STATES for r in range(1, 9)], 8, cell=(170, 220), title="PORTE-REGISTRE — all states x 8 rotations", path=OUT / "_rotations_sheet.png")
    print("sheets written")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "preview":
        preview()
    elif cmd == "family":
        family()
    elif cmd == "sheets":
        sheets()
