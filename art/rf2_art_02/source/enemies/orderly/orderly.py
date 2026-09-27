"""ORDERLY — final creature source (RED FLAGS 2 MAP01).

Identity: an institution-derived human remnant. Sainte-Anne service orderly, wasted by the
institution but still built for restraint work: broad trapezius, long arms, big hands. Off-white
cotton service tunic (breast pocket, blank name tab) over blue-de-service trousers, heavy black
shoes, belt with a key ring. Shaved skull, sunken temples, deep sockets with dark wet eyes, and a
leather restraint strap buckled across the mouth (institutional, not gothic). Posture: head thrust
forward, shoulders raised, weight on the balls of the feet, hands half-closed like restraint claws.

    python orderly.py preview        # review sheet (front / 3-4 / side / back + key states)
    python orderly.py family         # all runtime sprites (13 states x 8 rotations) + review sheets

Runtime contract (sprite prefix ORDY, Scale 0.2, feet on the floor line):
    A idle | B C D E walk | F attack_prep | G attack | H attack_recovery | I pain
    J death_1 | K death_2 | L death_3 | M corpse
"""
from __future__ import annotations
import json, math, os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_pipeline"))
import sdfrig as S          # noqa: E402
import humanoid as Hm       # noqa: E402

OUT = HERE.parents[1] / "renders/orderly"
PREFIX = "ORDY"
PPU = 5.0

M_SKIN, M_TUNIC, M_TROUSER, M_SHOE, M_EYE, M_SCALP, M_NAIL, M_LEATHER, M_STEEL, M_TAB, M_SOLE = range(1, 12)
MATERIALS = {
    M_SKIN: S.Material("skin", (0.58, 0.50, 0.47), rough=0.62, spec=0.16, detail="skin", detail_amp=0.7, sss=0.28),
    M_SCALP: S.Material("scalp", (0.50, 0.43, 0.41), rough=0.68, spec=0.12, detail="skin", detail_amp=0.9, sss=0.2),
    M_TUNIC: S.Material("tunic", (0.72, 0.69, 0.60), rough=0.94, spec=0.03, detail="cloth", albedo2=(0.48, 0.45, 0.38), detail_scale=1.0, detail_amp=0.6),
    M_TROUSER: S.Material("trousers", (0.13, 0.20, 0.30), rough=0.9, spec=0.05, detail="cloth", albedo2=(0.09, 0.13, 0.19), detail_scale=1.3, detail_amp=0.5),
    M_SHOE: S.Material("shoe", (0.05, 0.05, 0.05), rough=0.40, spec=0.35, detail="leather", detail_amp=0.4),
    M_SOLE: S.Material("sole", (0.10, 0.09, 0.08), rough=0.85, spec=0.08, detail="rubber"),
    M_EYE: S.Material("eye", (0.05, 0.04, 0.04), rough=0.18, spec=0.5),
    M_NAIL: S.Material("nail", (0.42, 0.34, 0.31), rough=0.35, spec=0.4),
    M_LEATHER: S.Material("leather", (0.20, 0.12, 0.08), rough=0.55, spec=0.30, detail="leather", detail_amp=0.6),
    M_STEEL: S.Material("steel", (0.55, 0.55, 0.57), rough=0.35, spec=0.7, detail="steel", albedo2=(0.36, 0.22, 0.14), detail_amp=0.5),
    M_TAB: S.Material("tab", (0.22, 0.22, 0.25), rough=0.6, spec=0.2),
}

PROPS = dict(Hm.DEFAULT_PROPS)
PROPS.update(height=66.0, pelvis_z=35.5, spine_len=4.0, chest_len=7.5, neck_len=8.6, head_len=3.4,
             shoulder_y=9.4, clav_z=6.0, upper_arm=13.5, forearm=12.5, hip_y=3.6, thigh=17.0, shin=15.5,
             chest_r=(5.4, 8.8, 8.0), pelvis_r=(4.8, 6.0, 4.6), belly_r=(4.0, 5.0, 4.0),
             upper_arm_r=(2.7, 2.2), forearm_r=(2.4, 1.6), thigh_r=(3.3, 2.5), shin_r=(2.5, 1.8),
             deltoid_r=2.7, neck_r=1.95, trap_r=1.9, scapula_r=(1.5, 2.6, 3.0),
             foot_len=9.5, foot_w=3.6, foot_h=2.9)


def build(curl_l=0.45, curl_r=0.45, spread=0.18, fist_l=False, fist_r=False):
    rig = S.Rig()
    rig.materials = MATERIALS
    P = PROPS
    Hm.build_skeleton(rig, P)
    M = dict(skin=M_SKIN, torso=M_TUNIC, pelvis=M_TUNIC, arm_upper=M_TUNIC, arm_lower=M_SKIN, leg_upper=M_TROUSER, leg_lower=M_TROUSER, shoe=M_SHOE, scalp=M_SCALP, eye=M_EYE)
    Hm.build_body(rig, P, M)
    # throat / open collar (skin showing above the tunic), collar band
    rig.add("ellipsoid", "chest", (3.4, 0, 6.6), (2.0, 2.6, 2.2), M_SKIN, blend=1.4)
    rig.add("torus", "chest", (0.6, 0, 6.9), (3.6, 0.5), M_TUNIC, blend=0.8, rot=S.rot_y(12))
    # tunic hem hanging over the hips, and a soft front placket line
    rig.add("cylinder", "root", (0.3, 0, -2.4), (2.6, 6.9, 0.9), M_TUNIC, blend=1.8)
    rig.add("rbox", "chest", (4.9, 0.0, 1.5), (0.18, 0.35, 6.0, 0.15), M_TUNIC, blend=0.5)
    # breast pocket (left chest, from the creature's point of view) and blank name tab
    rig.add("rbox", "chest", (4.75, 3.1, 3.4), (0.28, 2.0, 2.3, 0.35), M_TUNIC, blend=0.6)
    rig.add("rbox", "chest", (5.0, 3.1, 6.1), (0.12, 1.7, 0.5, 0.1), M_TAB, group="tab", blend=0.0)
    # rolled sleeve cuffs at the elbows
    for side in ("l", "r"):
        rig.add("torus", f"elbow_{side}", (0, 0, 1.2), (2.35, 0.75), M_TUNIC, blend=1.2)
    # belt with buckle, key ring on the right hip
    rig.add("torus", "root", (0.3, 0, 2.6), (6.6, 0.55), M_LEATHER, group="belt", blend=0.3)
    rig.add("rbox", "root", (6.9, 0.0, 2.6), (0.35, 1.1, 0.9, 0.2), M_STEEL, group="belt", blend=0.0)
    rig.add("rbox", "root", (4.6, -5.4, 1.2), (0.25, 0.6, 1.4, 0.2), M_LEATHER, group="keys", blend=0.0)
    rig.add("torus", "root", (4.9, -5.6, -0.6), (1.2, 0.22), M_STEEL, group="keys", blend=0.0, rot=S.rot_x(90))
    for k, (dx, dz) in enumerate(((-0.5, -2.6), (0.2, -2.9), (0.8, -2.4))):
        rig.add("rbox", "root", (4.9 + dx, -5.7, dz), (0.12, 0.3, 1.1, 0.1), M_STEEL, group="keys", blend=0.0, rot=S.rot_x(8 * k - 8))
    # shoe soles
    for side in ("l", "r"):
        rig.add("rbox", f"ankle_{side}", (P["foot_len"] * 0.32, 0, -P["foot_h"] * 0.5 - 1.0), (P["foot_len"] * 0.5, P["foot_w"] * 0.5 + 0.1, 0.55, 0.3), M_SOLE, group=f"foot_{side}", blend=0.4)
    # head: skull, shaved, sunken temples; deep sockets; restraint strap over the mouth
    Hm.build_head(rig, M, skull=(4.4, 4.0, 5.3), brow=1.2, gaunt=0.85, nose=0.95, mouth=False, offset=(1.0, 0, 4.8))
    rig.add("torus", "head", (1.0, 0, 1.9), (3.75, 0.55), M_LEATHER, group="strap", blend=0.0, rot=S.rot_y(-10))
    rig.add("rbox", "head", (-3.0, 0, 2.3), (0.5, 0.9, 0.8, 0.15), M_STEEL, group="strap", blend=0.0)
    rig.add("rbox", "head", (4.85, 0, 1.6), (0.4, 1.7, 0.85, 0.15), M_LEATHER, group="strap", blend=0.0)   # front pad over the mouth
    # hands: big, restraint claws
    Hm.add_hand(rig, "l", M_SKIN, M_NAIL, curl=0.9 if fist_l else curl_l, spread=0.05 if fist_l else spread, scale=1.08)
    Hm.add_hand(rig, "r", M_SKIN, M_NAIL, curl=0.9 if fist_r else curl_r, spread=0.05 if fist_r else spread, scale=1.08)
    return rig


# ------------------------------------------------------------------ poses
def idle():
    return Hm.merge({"root": (0, 2, 0), "spine": (0, 7, 0), "chest": (0, 7, 0), "neck": (0, 10, 0), "head": (0, -8, 0)},
                    Hm.leg(6, 10, 3, out=4, side="l"), Hm.leg(-6, 8, 0, out=4, side="r"),
                    Hm.arm(swing=16, out=12, elbow=28, side="l", wrist=(0, -20, 0)), Hm.arm(swing=14, out=12, elbow=26, side="r", wrist=(0, -20, 0)))


def walk(phase):
    p = Hm.walk(phase, stride=40, lean=14, arm_swing=30, elbow=30, knee_lift=42)
    p["neck"] = (0, 12, 0); p["head"] = (0, -8, math.sin(phase * 2 * math.pi) * 4)
    return p


def attack_prep():
    return Hm.merge({"root": (0, 4, -18), "spine": (0, 6, -8), "chest": (0, 6, -14), "neck": (0, 12, 10), "head": (0, -10, 12)},
                    Hm.leg(22, 24, 4, out=3, side="l"), Hm.leg(-14, 10, 8, out=6, side="r"),
                    Hm.arm(swing=-48, out=34, elbow=96, twist=-20, side="r", wrist=(0, -25, 0)),
                    Hm.arm(swing=26, out=18, elbow=34, side="l", wrist=(0, -30, 0)))


def attack():
    return Hm.merge({"root": (0, 12, 18), "spine": (0, 8, 10), "chest": (0, 8, 16), "neck": (0, 16, -8), "head": (0, -2, -10)},
                    Hm.leg(30, 26, 8, out=3, side="l"), Hm.leg(-30, 4, 14, out=6, side="r"),
                    Hm.arm(swing=78, out=8, elbow=12, twist=10, side="r", wrist=(0, -35, 0)),
                    Hm.arm(swing=-10, out=24, elbow=60, side="l", wrist=(0, -20, 0)))


def attack_recovery():
    return Hm.merge({"root": (0, 6, 8), "spine": (0, 5, 4), "chest": (0, 5, 6), "neck": (0, 10, -4), "head": (0, -6, -4)},
                    Hm.leg(16, 20, 4, out=4, side="l"), Hm.leg(-16, 8, 8, out=5, side="r"),
                    Hm.arm(swing=44, out=10, elbow=36, side="r", wrist=(0, -30, 0)),
                    Hm.arm(swing=8, out=18, elbow=40, side="l", wrist=(0, -20, 0)))


def pain():
    return Hm.merge({"root": (0, -6, -6), "spine": (0, -8, -4), "chest": (0, -10, -6), "neck": (0, -18, 6), "head": (0, -14, 8)},
                    Hm.leg(4, 22, -4, out=6, side="l"), Hm.leg(-8, 14, 2, out=8, side="r"),
                    Hm.arm(swing=34, out=44, elbow=64, side="l", wrist=(0, 10, 0)), Hm.arm(swing=28, out=50, elbow=70, side="r", wrist=(0, 10, 0)))


def death_1():
    return Hm.merge({"root": (0, 16, 6), "spine": (0, 16, 2), "chest": (0, 18, 4), "neck": (0, 20, 0), "head": (0, 10, -6)},
                    Hm.leg(36, 58, -6, out=5, side="l"), Hm.leg(30, 64, -4, out=6, side="r"),
                    Hm.arm(swing=20, out=14, elbow=20, side="l"), Hm.arm(swing=14, out=16, elbow=18, side="r"))


def death_2():
    return Hm.merge({"root": (0, 40, 4), "spine": (0, 16, 0), "chest": (0, 16, 0), "neck": (0, 14, 0), "head": (0, 6, -8)},
                    Hm.leg(46, 70, 20, out=6, side="l"), Hm.leg(38, 76, 24, out=7, side="r"),
                    Hm.arm(swing=92, out=16, elbow=10, side="l", wrist=(0, 20, 0)), Hm.arm(swing=84, out=20, elbow=14, side="r", wrist=(0, 20, 0)))


def death_3():
    p = Hm.merge({"spine": (0, -4, 0), "chest": (0, -6, 0), "neck": (0, -8, 0), "head": (0, 0, 48)},
                 Hm.leg(-4, 8, 30, out=8, side="l"), Hm.leg(6, 14, 34, out=10, side="r"),
                 Hm.arm(swing=120, out=30, elbow=30, side="l", wrist=(0, 30, 0)), Hm.arm(swing=40, out=26, elbow=90, side="r", wrist=(0, 20, 0)))
    p["root_rot"] = Hm.lying(face_down=True, roll=6)
    return p


def corpse():
    p = Hm.merge({"spine": (0, -6, 0), "chest": (0, -8, 0), "neck": (0, -8, 0), "head": (0, 0, 60)},
                 Hm.leg(-6, 4, 36, out=10, side="l"), Hm.leg(10, 26, 36, out=16, side="r"),
                 Hm.arm(swing=126, out=42, elbow=22, side="l", wrist=(0, 40, 0)), Hm.arm(swing=30, out=34, elbow=110, side="r", wrist=(0, 30, 0)))
    p["root_rot"] = Hm.lying(face_down=True, roll=10)
    return p


STATES = [
    ("A", "idle", idle, dict(curl_l=0.45, curl_r=0.45)),
    ("B", "walk_1", lambda: walk(0.0), dict(curl_l=0.5, curl_r=0.5)),
    ("C", "walk_2", lambda: walk(0.25), dict(curl_l=0.5, curl_r=0.5)),
    ("D", "walk_3", lambda: walk(0.5), dict(curl_l=0.5, curl_r=0.5)),
    ("E", "walk_4", lambda: walk(0.75), dict(curl_l=0.5, curl_r=0.5)),
    ("F", "attack_prep", attack_prep, dict(fist_r=True, curl_l=0.55)),
    ("G", "attack", attack, dict(fist_r=True, curl_l=0.55)),
    ("H", "attack_recovery", attack_recovery, dict(curl_r=0.7, curl_l=0.5)),
    ("I", "pain", pain, dict(curl_l=0.25, curl_r=0.25)),
    ("J", "death_1", death_1, dict(curl_l=0.3, curl_r=0.3)),
    ("K", "death_2", death_2, dict(curl_l=0.2, curl_r=0.2)),
    ("L", "death_3", death_3, dict(curl_l=0.25, curl_r=0.35)),
    ("M", "corpse", corpse, dict(curl_l=0.2, curl_r=0.3)),
]
ROT_YAW = {r: 180.0 - (r - 1) * 45.0 for r in range(1, 9)}


def render_one(args):
    letter, name, rot, ppu, out_dir = args
    letter_, name_, pose_fn, hand_kw = next(s for s in STATES if s[0] == letter)
    rig = build(**hand_kw)
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
    for letter in ("C", "F", "G", "I", "J", "M"):
        _, name, fn, kw = next(s for s in STATES if s[0] == letter)
        img, ox, oy = S.render(build(**kw), fn(), ROT_YAW[2], ppu=ppu, ss=2)
        imgs.append(img); labs.append(name)
    S.review_sheet(imgs, labs, 5, title="ORDERLY — preview (neutral light, software render)", path=OUT / "_preview.png")
    print("preview written", OUT / "_preview.png")


def family(ppu=PPU, workers=None):
    from multiprocessing import Pool
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(letter, name, rot, ppu, str(OUT)) for (letter, name, _, _) in STATES for rot in range(1, 9)]
    workers = workers or max(1, min(12, (os.cpu_count() or 4) - 2))
    with Pool(workers) as pool:
        results = pool.map(render_one, jobs, chunksize=1)
    manifest = {"prefix": PREFIX, "scale": round(1.0 / ppu, 6), "pixel_stretch_prerendered": 1.2, "ppu": ppu,
                "states": [{"letter": l, "name": n} for (l, n, _, _) in STATES],
                "sprites": [{"file": f"{PREFIX}{l}{r}.png", "w": w, "h": h, "grab": [ox, oy]} for (l, r, w, h, ox, oy) in results]}
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    sheets(ppu)


def sheets(ppu=PPU):
    from PIL import Image
    load = lambda l, r: np.asarray(Image.open(OUT / f"{PREFIX}{l}{r}.png").convert("RGBA"))
    imgs = [load("A", r) for r in (1, 2, 3, 5)] + [load("C", 2), load("G", 2), load("I", 2), load("K", 2), load("M", 3)]
    labs = ["FRONT", "3/4", "SIDE", "BACK", "MOVEMENT", "ATTACK", "PAIN", "DEATH", "CORPSE"]
    S.review_sheet(imgs, labs, 5, title="ORDERLY — review sheet (neutral light)", path=OUT / "_review_sheet.png")
    rows = []
    for (l, n, _, _) in STATES:
        rows += [load(l, r) for r in range(1, 9)]
    S.review_sheet(rows, [f"{l}{r}" for (l, _, _, _) in STATES for r in range(1, 9)], 8, cell=(150, 200), title="ORDERLY — all states x 8 rotations", path=OUT / "_rotations_sheet.png")
    print("sheets written")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "preview":
        preview()
    elif cmd == "family":
        family()
    elif cmd == "sheets":
        sheets()
