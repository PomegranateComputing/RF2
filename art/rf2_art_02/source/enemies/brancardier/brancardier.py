"""BRANCARDIER — final creature source (RED FLAGS 2 MAP01).

Identity: a hospital porter and his wheeled stretcher that are no longer separable. First look:
a huge man in a burst navy service jacket bent over the rear handles of a steel gurney carrying a
strapped, sheeted load. Second look: his hands are bound to the handles with leather restraint
straps, a harness runs from the frame up over his shoulders, and the load under the sheet has the
lumps of a body. Everything about him is mass and momentum: barrel chest, thick neck, head carried
low between raised shoulders, wide stance, heavy boots.

    python brancardier.py preview | family

Runtime contract (sprite prefix BRCD, Scale 0.2, feet and wheels on the floor line):
    A idle | B C D E walk (pushing) | F charge_prep (brace) | G charge (stride 1) | N charge (stride 2)
    O charge_impact | H recovery (charge miss, off balance) | I pain
    J death_1 (porter folds over the handles) | K death_2 (down on the knees, straps torn)
    L death_3 (porter on the floor behind the frame) | M corpse
The stretcher stays upright on its wheels through every state (collision box of the actor).
"""
from __future__ import annotations
import json, math, os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_pipeline"))
import sdfrig as S          # noqa: E402
import humanoid as Hm       # noqa: E402

OUT = HERE.parents[1] / "renders/brancardier"
PREFIX = "BRCD"
PPU = 5.0

(M_SKIN, M_JACKET, M_SHIRT, M_TROUSER, M_BOOT, M_EYE, M_HAIR, M_NAIL, M_LEATHER, M_STEEL, M_RUBBER, M_CANVAS, M_SHEET, M_BRASS, M_SOLE) = range(1, 16)
MATERIALS = {
    M_SKIN: S.Material("skin", (0.62, 0.52, 0.47), rough=0.62, spec=0.16, detail="skin", detail_amp=0.7, sss=0.3),
    M_HAIR: S.Material("hair", (0.12, 0.10, 0.09), rough=0.75, spec=0.15, detail="hair", detail_amp=0.8),
    M_JACKET: S.Material("jacket", (0.13, 0.20, 0.31), rough=0.92, spec=0.04, detail="cloth", albedo2=(0.09, 0.13, 0.20), detail_scale=0.9, detail_amp=0.6),
    M_SHIRT: S.Material("shirt", (0.62, 0.60, 0.54), rough=0.9, spec=0.04, detail="cloth", albedo2=(0.45, 0.43, 0.38), detail_amp=0.5),
    M_TROUSER: S.Material("trousers", (0.16, 0.17, 0.19), rough=0.9, spec=0.05, detail="cloth", albedo2=(0.10, 0.10, 0.12), detail_amp=0.5),
    M_BOOT: S.Material("boot", (0.07, 0.06, 0.06), rough=0.45, spec=0.3, detail="leather", detail_amp=0.5),
    M_SOLE: S.Material("sole", (0.10, 0.09, 0.08), rough=0.85, spec=0.08, detail="rubber"),
    M_EYE: S.Material("eye", (0.05, 0.04, 0.04), rough=0.18, spec=0.5),
    M_NAIL: S.Material("nail", (0.40, 0.33, 0.30), rough=0.35, spec=0.4),
    M_LEATHER: S.Material("leather", (0.22, 0.13, 0.08), rough=0.55, spec=0.3, detail="leather", detail_amp=0.6),
    M_STEEL: S.Material("steel", (0.40, 0.41, 0.43), rough=0.45, spec=0.55, detail="steel", albedo2=(0.36, 0.20, 0.12), detail_scale=1.4, detail_amp=1.0),
    M_RUBBER: S.Material("rubber", (0.09, 0.09, 0.09), rough=0.8, spec=0.1, detail="rubber"),
    M_CANVAS: S.Material("canvas", (0.55, 0.52, 0.44), rough=0.95, spec=0.03, detail="canvas", albedo2=(0.40, 0.37, 0.30), detail_amp=0.6),
    M_SHEET: S.Material("sheet", (0.80, 0.78, 0.71), rough=0.95, spec=0.03, detail="canvas", albedo2=(0.60, 0.57, 0.50), detail_scale=0.8, detail_amp=0.7),
    M_BRASS: S.Material("brass", (0.65, 0.52, 0.28), rough=0.4, spec=0.6),
}

PROPS = dict(Hm.DEFAULT_PROPS)
PROPS.update(height=72.0, pelvis_z=37.0, spine_len=4.5, chest_len=8.0, neck_len=8.0, head_len=3.2,
             shoulder_y=11.0, clav_z=6.5, upper_arm=14.0, forearm=13.0, hip_y=4.6, thigh=17.5, shin=16.0,
             chest_r=(7.2, 11.0, 9.5), pelvis_r=(6.2, 7.6, 5.6), belly_r=(6.4, 7.0, 5.6),
             upper_arm_r=(3.6, 3.0), forearm_r=(3.2, 2.3), thigh_r=(4.4, 3.3), shin_r=(3.4, 2.4),
             deltoid_r=3.6, neck_r=2.9, trap_r=2.8, scapula_r=(2.0, 3.4, 3.8),
             foot_len=10.5, foot_w=4.2, foot_h=3.4)

# stretcher geometry (cart bone space, floor origin, X forward)
RAIL_Z, RAIL_Y = 31.0, 12.5
RAIL_X0, RAIL_X1 = -24.0, 36.0
HANDLE_X = -33.0
WHEEL_R_F, WHEEL_R_R = 5.6, 3.8
AXLE_XF, AXLE_XR = 26.0, -12.0
PORTER_X = -44.0


def add_cart(rig, wheel_phase=0.0, load=True):
    st = M_STEEL
    # side rails, cross bars, handles
    for sy in (1, -1):
        rig.capsule_between("cart", (RAIL_X0, sy * RAIL_Y, RAIL_Z), (RAIL_X1, sy * RAIL_Y, RAIL_Z), 0.95, st, group="frame", blend=0.4)
        rig.capsule_between("cart", (RAIL_X0, sy * RAIL_Y, RAIL_Z), (HANDLE_X, sy * RAIL_Y, RAIL_Z + 1.5), 0.95, st, group="frame", blend=0.4)
        rig.capsule_between("cart", (HANDLE_X, sy * RAIL_Y, RAIL_Z + 1.5), (HANDLE_X - 6.5, sy * RAIL_Y, RAIL_Z + 1.5), 1.25, M_RUBBER, group="frame", blend=0.3)   # grips
        # legs down to the axles, with a lower longitudinal brace
        rig.capsule_between("cart", (AXLE_XF, sy * RAIL_Y, RAIL_Z), (AXLE_XF, sy * RAIL_Y, WHEEL_R_F), 0.85, st, group="frame", blend=0.4)
        rig.capsule_between("cart", (AXLE_XR, sy * RAIL_Y, RAIL_Z), (AXLE_XR, sy * RAIL_Y, WHEEL_R_R), 0.85, st, group="frame", blend=0.4)
        rig.capsule_between("cart", (AXLE_XR, sy * RAIL_Y, 12.0), (AXLE_XF, sy * RAIL_Y, 12.0), 0.7, st, group="frame", blend=0.4)
        rig.capsule_between("cart", (AXLE_XR + 2, sy * RAIL_Y, 12.0), (AXLE_XF - 2, sy * RAIL_Y, RAIL_Z - 1), 0.55, st, group="frame", blend=0.3)   # diagonal brace
    for x in (RAIL_X0, RAIL_X1, AXLE_XF, AXLE_XR):
        rig.capsule_between("cart", (x, -RAIL_Y, RAIL_Z), (x, RAIL_Y, RAIL_Z), 0.85, st, group="frame", blend=0.4)
    # axles and wheels
    for (ax, wr) in ((AXLE_XF, WHEEL_R_F), (AXLE_XR, WHEEL_R_R)):
        rig.capsule_between("cart", (ax, -RAIL_Y - 1.5, wr), (ax, RAIL_Y + 1.5, wr), 0.6, st, group="frame", blend=0.2)
        for sy in (1, -1):
            wy = sy * (RAIL_Y + 1.6)
            rot = S.rot_x(90)   # torus plane -> XZ
            rig.add("torus", "cart", (ax, wy, wr), (wr - 1.15, 1.15), M_RUBBER, group=f"wheel{ax}{sy}", blend=0.0, rot=rot)
            rig.add("cylinder", "cart", (ax, wy, wr), (0.55, wr - 1.9, 0.3), M_STEEL, group=f"wheel{ax}{sy}", blend=0.2, rot=rot)
            rig.add("cylinder", "cart", (ax, wy, wr), (0.9, 1.6, 0.3), M_STEEL, group=f"wheel{ax}{sy}", blend=0.2, rot=rot)
            for k in range(5):
                a = math.radians(wheel_phase + k * 72)
                rig.add("rbox", "cart", (ax, wy, wr), (wr - 1.6, 0.35, 0.5, 0.15), M_STEEL, group=f"wheel{ax}{sy}", blend=0.0, rot=S.rot_y(math.degrees(a)) @ np.eye(3, dtype=np.float32))
            # spoke solid: replace the 5 thin boxes' orientation: rotate about Y is done above (boxes span X)
    # bed: sagging canvas between the rails, sheeted load strapped down
    rig.add("rbox", "cart", ((RAIL_X0 + RAIL_X1) / 2, 0, RAIL_Z - 0.4), ((RAIL_X1 - RAIL_X0) / 2 - 1.0, RAIL_Y - 0.6, 0.8, 0.5), M_CANVAS, group="bed", blend=0.3)
    if load:
        rig.add("rbox", "cart", (5.0, 0, RAIL_Z + 3.2), (25.0, 12.0, 3.0, 2.6), M_SHEET, group="load", blend=3.5)
        rig.add("ellipsoid", "cart", (23.0, 0.5, RAIL_Z + 7.4), (5.8, 5.2, 5.6), M_SHEET, group="load", blend=3.0)      # head lump
        rig.add("ellipsoid", "cart", (7.0, 0, RAIL_Z + 8.2), (12.5, 9.5, 7.0), M_SHEET, group="load", blend=3.5)        # chest lump
        rig.add("ellipsoid", "cart", (-13.0, 1.2, RAIL_Z + 5.6), (7.5, 6.8, 4.6), M_SHEET, group="load", blend=3.0)     # knees / feet
        rig.add("ellipsoid", "cart", (-8.0, -3.5, RAIL_Z + 4.0), (4.0, 3.0, 2.6), M_SHEET, group="load", blend=3.0)
        # sheet edges hanging over the rails
        for sy in (1, -1):
            rig.add("rbox", "cart", (6.0, sy * 12.4, RAIL_Z - 1.6), (22.0, 0.6, 3.2, 0.5), M_SHEET, group="load", blend=1.5)
        # restraint straps over the load (rectangular rings), buckles on the near side
        for x in (14.0, -6.0):
            rig.add("rbox", "cart", (x, 0, RAIL_Z + 3.2), (0.7, 13.6, 7.6, 0.4), M_LEATHER, group=f"strap{x}", blend=0.0)
            rig.add("rbox", "cart", (x, 0, RAIL_Z + 3.2), (1.2, 12.5, 6.6, 0.4), M_LEATHER, group=f"strap{x}", blend=0.0, op="subtract")
            rig.add("rbox", "cart", (x, -13.7, RAIL_Z + 2.0), (0.9, 0.5, 1.2, 0.2), M_BRASS, group="buckles", blend=0.0)


def build(curl=0.85, wheel_phase=0.0, straps=True, cart=True):
    rig = S.Rig()
    rig.materials = MATERIALS
    P = PROPS
    rig.bone("cart", None, (0, 0, 0))
    Hm.build_skeleton(rig, P)
    M = dict(skin=M_SKIN, torso=M_JACKET, pelvis=M_TROUSER, arm_upper=M_JACKET, arm_lower=M_JACKET, leg_upper=M_TROUSER, leg_lower=M_TROUSER, shoe=M_BOOT, scalp=M_HAIR, eye=M_EYE)
    Hm.build_body(rig, P, M, skin_arms=False)
    # bull neck and raised shoulders, burst seams showing the undershirt at the shoulders
    rig.add("ellipsoid", "chest", (-0.5, 0, 7.4), (4.5, 8.6, 3.2), M_JACKET, blend=3.0)
    rig.add("ellipsoid", "chest", (3.2, 0, 7.2), (2.4, 3.6, 2.6), M_SKIN, blend=1.6)          # throat
    for sy in (1, -1):
        rig.add("ellipsoid", f"shoulder_{'l' if sy > 0 else 'r'}", (1.2, sy * 0.6, 1.6), (1.8, 1.6, 1.2), M_SHIRT, blend=0.6)   # torn seam
    # forearms bare below the jacket sleeves (rolled), thick wrists
    for side in ("l", "r"):
        rig.capsule_between(f"elbow_{side}", (0, 0, -3.5), (0, 0, -P["forearm"] + 0.3), P["forearm_r"][0] * 0.92, M_SKIN, r2=P["forearm_r"][1] * 1.05, blend=1.4)
        rig.add("torus", f"elbow_{side}", (0, 0, -3.2), (3.1, 0.8), M_JACKET, blend=1.0)
    # wide belt, boot tops, soles
    rig.add("torus", "root", (0.3, 0, 2.2), (7.9, 0.7), M_LEATHER, group="belt", blend=0.3)
    rig.add("rbox", "root", (8.1, 0, 2.2), (0.4, 1.3, 1.0, 0.2), M_BRASS, group="belt", blend=0.0)
    for side in ("l", "r"):
        rig.add("cylinder", f"ankle_{side}", (-0.2, 0, 3.0), (2.8, P["shin_r"][1] * 1.15, 0.5), M_BOOT, group=f"foot_{side}", blend=1.0)
        rig.add("rbox", f"ankle_{side}", (P["foot_len"] * 0.32, 0, -P["foot_h"] * 0.5 - 1.1), (P["foot_len"] * 0.5, P["foot_w"] * 0.5 + 0.1, 0.6, 0.3), M_SOLE, group=f"foot_{side}", blend=0.4)
    # head: heavy brow, broken nose, cropped dark hair, mouth open (breathing hard)
    Hm.build_head(rig, M, skull=(4.7, 4.4, 5.6), brow=1.35, gaunt=0.2, nose=1.15, jaw_open=0.5, mouth=True, offset=(1.0, 0, 4.9))
    rig.add("ellipsoid", "head", (-0.2, 0, 7.2), (4.6, 4.5, 3.2), M_HAIR, group="hair", blend=1.2)     # cropped hair cap
    # hands closed on the grips, bound with restraint straps
    Hm.add_hand(rig, "l", M_SKIN, M_NAIL, curl=curl, spread=0.02, scale=1.15)
    Hm.add_hand(rig, "r", M_SKIN, M_NAIL, curl=curl, spread=0.02, scale=1.15)
    if straps:
        for side in ("l", "r"):
            rig.add("torus", f"wrist_{side}", (0, 0, -4.0), (2.9, 0.6), M_LEATHER, group=f"bind_{side}", blend=0.0, rot=S.rot_x(90))
            rig.add("torus", f"wrist_{side}", (0, 0, -1.0), (2.7, 0.55), M_LEATHER, group=f"bind_{side}", blend=0.0, rot=S.rot_x(90))
    # harness: two leather straps from the frame's rear crossbar up over the shoulders
    for sy in (1, -1):
        rig.capsule_between("chest", (4.0, sy * 5.0, 7.5), (-4.5, sy * 6.5, 2.0), 0.7, M_LEATHER, group="harness", blend=0.0)
        rig.capsule_between("chest", (4.0, sy * 5.0, 7.5), (5.5, sy * 4.0, -6.0), 0.7, M_LEATHER, group="harness", blend=0.0)
    if cart:
        add_cart(rig, wheel_phase=wheel_phase)
    return rig


def settle(pose, yaw, **kw):
    """The stretcher stands on its wheels by construction (z=0). Only the porter is floor-snapped:
    his lowest point is measured on a cart-less copy and the root offset corrected, so the cart
    never floats and the feet never sink."""
    porter = build(cart=False, **kw)
    dz = porter.snap_to_floor(pose, S.rot_z(yaw), (0, 0, 0))
    p = dict(pose)
    ro = p.get("root_offset", (0, 0, 0))
    p["root_offset"] = (ro[0], ro[1], ro[2] + dz)
    return p


# ------------------------------------------------------------------ poses
def base(lean=28.0, root_x=PORTER_X, root_z=0.0, crouch=0.0, cart_dx=0.0):
    """porter behind the cart, hands on the grips (solved by IK), stretcher on its wheels"""
    p = {"root": (0, lean * 0.3, 0), "spine": (0, 6 + lean * 0.3, 0), "chest": (0, 8 + lean * 0.4, 0), "neck": (0, lean * 0.5, 0), "head": (0, -lean * 0.6, 0),
         "root_offset": (root_x, 0, root_z - crouch), "cart_offset": (cart_dx, 0, 0)}
    return p


def hands_on_grips(rig, p, cart_dx=0.0):
    for side, sy in (("l", 1), ("r", -1)):
        target = np.array([HANDLE_X - 3.0 + cart_dx, sy * RAIL_Y, RAIL_Z + 1.5], np.float32)
        p, e = Hm.solve_arm(rig, p, side, target, wrist_len=5.5)
    return p


def idle(rig):
    p = Hm.merge(base(26), Hm.leg(6, 12, 2, out=6, side="l"), Hm.leg(-6, 10, 0, out=6, side="r"))
    return hands_on_grips(rig, p)


def walk(rig, phase):
    w = Hm.walk(phase, stride=30, lean=30, arm_swing=0, elbow=20, knee_lift=34)
    p = Hm.merge(base(30, root_z=0), {k: v for k, v in w.items() if k.startswith(("hip_", "knee_", "ankle_"))})
    p["chest"] = (0, 8, math.sin(phase * 2 * math.pi) * 3)
    return hands_on_grips(rig, p)


def charge_prep(rig):
    p = Hm.merge(base(14, root_x=PORTER_X - 4, crouch=4), Hm.leg(24, 40, 2, out=8, side="l"), Hm.leg(-18, 20, 10, out=9, side="r"))
    p["neck"] = (0, 4, 0); p["head"] = (0, 6, 0)
    return hands_on_grips(rig, p)


def charge(rig, stride=1):
    s = 1 if stride == 1 else -1
    p = Hm.merge(base(40, root_x=PORTER_X + 2, crouch=2), Hm.leg(38 * s, 30 if s > 0 else 12, 12, out=6, side="l"), Hm.leg(-38 * s, 12 if s > 0 else 30, 20, out=6, side="r"))
    p["chest"] = (0, 10, 4 * s)
    return hands_on_grips(rig, p)


def charge_impact(rig):
    p = Hm.merge(base(46, root_x=PORTER_X + 3, crouch=3), Hm.leg(30, 16, 24, out=6, side="l"), Hm.leg(-40, 8, 26, out=6, side="r"))
    p["neck"] = (0, 30, 0); p["head"] = (0, -10, 0)
    return hands_on_grips(rig, p)


def recovery(rig):
    p = Hm.merge(base(18, root_x=PORTER_X - 2, crouch=1), Hm.leg(10, 30, -4, out=10, side="l"), Hm.leg(-4, 36, -6, out=11, side="r"))
    p["chest"] = (0, 6, -12); p["neck"] = (0, 6, 10); p["head"] = (0, 4, 8)
    return hands_on_grips(rig, p)


def pain(rig):
    p = Hm.merge(base(6, root_x=PORTER_X - 3), Hm.leg(4, 20, -4, out=8, side="l"), Hm.leg(-8, 16, 0, out=9, side="r"))
    p["chest"] = (0, -6, 6); p["neck"] = (0, -18, 4); p["head"] = (0, -16, 6)
    return hands_on_grips(rig, p)


def death_1(rig):
    p = Hm.merge(base(52, root_x=PORTER_X - 1, crouch=8), Hm.leg(40, 62, -8, out=7, side="l"), Hm.leg(30, 70, -6, out=8, side="r"))
    p["neck"] = (0, 30, 0); p["head"] = (0, 14, -10)
    return hands_on_grips(rig, p)


def death_2(rig):
    p = Hm.merge(base(70, root_x=PORTER_X - 3, crouch=17), Hm.leg(60, 118, 24, out=8, side="l"), Hm.leg(56, 120, 24, out=10, side="r"),
                 Hm.arm(swing=60, out=20, elbow=30, side="l"), Hm.arm(swing=64, out=22, elbow=26, side="r"))
    p["neck"] = (0, 20, 0); p["head"] = (0, 20, -6)
    return p


def death_3(rig):
    p = Hm.merge({"spine": (0, -4, 0), "chest": (0, -6, 0), "neck": (0, -6, 0), "head": (0, 0, -50)},
                 Hm.leg(-2, 10, 30, out=8, side="l"), Hm.leg(8, 22, 34, out=12, side="r"),
                 Hm.arm(swing=110, out=28, elbow=40, side="l", wrist=(0, 30, 0)), Hm.arm(swing=30, out=30, elbow=100, side="r", wrist=(0, 20, 0)))
    p["root_rot"] = Hm.lying(face_down=True, roll=-8, turn=150)
    p["root_offset"] = (PORTER_X - 8, 6, 0)
    return p


def corpse(rig):
    p = death_3(rig)
    p["head"] = (0, 0, -60); p["hip_r"] = (-14, -6, 0); p["knee_r"] = (0, 30, 0)
    return p


STATES = [
    ("A", "idle", lambda r: idle(r), dict(wheel_phase=0)),
    ("B", "walk_1", lambda r: walk(r, 0.0), dict(wheel_phase=0)),
    ("C", "walk_2", lambda r: walk(r, 0.25), dict(wheel_phase=18)),
    ("D", "walk_3", lambda r: walk(r, 0.5), dict(wheel_phase=36)),
    ("E", "walk_4", lambda r: walk(r, 0.75), dict(wheel_phase=54)),
    ("F", "charge_prep", lambda r: charge_prep(r), dict(wheel_phase=0)),
    ("G", "charge_1", lambda r: charge(r, 1), dict(wheel_phase=20)),
    ("N", "charge_2", lambda r: charge(r, 2), dict(wheel_phase=56)),
    ("O", "charge_impact", lambda r: charge_impact(r), dict(wheel_phase=30)),
    ("H", "recovery", lambda r: recovery(r), dict(wheel_phase=10)),
    ("I", "pain", lambda r: pain(r), dict(wheel_phase=0)),
    ("J", "death_1", lambda r: death_1(r), dict(wheel_phase=0)),
    ("K", "death_2", lambda r: death_2(r), dict(wheel_phase=0, straps=False)),
    ("L", "death_3", lambda r: death_3(r), dict(wheel_phase=0, straps=False)),
    ("M", "corpse", lambda r: corpse(r), dict(wheel_phase=0, straps=False)),
]
ROT_YAW = {r: 180.0 - (r - 1) * 45.0 for r in range(1, 9)}


def render_one(args):
    letter, rot, ppu, out_dir = args
    _, name, pose_fn, kw = next(s for s in STATES if s[0] == letter)
    rig = build(**kw)
    pose = settle(pose_fn(rig), ROT_YAW[rot], **kw)
    img, ox, oy = S.render(rig, pose, ROT_YAW[rot], ppu=ppu, ss=2, floor_snap=False)
    path = Path(out_dir) / f"{PREFIX}{letter}{rot}.png"
    S.save_sprite(img, path, ox, oy)
    return (letter, rot, img.shape[1], img.shape[0], ox, oy)


def preview(ppu=PPU):
    OUT.mkdir(parents=True, exist_ok=True)
    imgs, labs = [], []
    rig = build()
    pose = idle(rig)
    for rot, lab in ((1, "front"), (2, "3/4"), (3, "side"), (5, "back")):
        img, ox, oy = S.render(rig, settle(pose, ROT_YAW[rot]), ROT_YAW[rot], ppu=ppu, ss=2, floor_snap=False)
        imgs.append(img); labs.append(f"idle {lab}")
    for letter in ("C", "F", "G", "O", "I", "J", "M"):
        _, name, fn, kw = next(s for s in STATES if s[0] == letter)
        r2 = build(**kw)
        img, ox, oy = S.render(r2, settle(fn(r2), ROT_YAW[2], **kw), ROT_YAW[2], ppu=ppu, ss=2, floor_snap=False)
        imgs.append(img); labs.append(name)
    S.review_sheet(imgs, labs, 4, title="BRANCARDIER — preview (neutral light, software render)", path=OUT / "_preview.png")
    print("preview written", OUT / "_preview.png")


def family(ppu=PPU, workers=None):
    from multiprocessing import Pool
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(letter, rot, ppu, str(OUT)) for (letter, _, _, _) in STATES for rot in range(1, 9)]
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
    imgs = [load("A", r) for r in (1, 2, 3, 5)] + [load("C", 2), load("G", 3), load("O", 2), load("I", 2), load("K", 2), load("M", 3)]
    labs = ["FRONT", "3/4", "SIDE", "BACK", "MOVEMENT", "CHARGE", "IMPACT", "PAIN", "DEATH", "CORPSE"]
    S.review_sheet(imgs, labs, 5, title="BRANCARDIER — review sheet (neutral light)", path=OUT / "_review_sheet.png")
    rows = []
    for (l, n, _, _) in STATES:
        rows += [load(l, r) for r in range(1, 9)]
    S.review_sheet(rows, [f"{l}{r}" for (l, _, _, _) in STATES for r in range(1, 9)], 8, cell=(190, 200), title="BRANCARDIER — all states x 8 rotations", path=OUT / "_rotations_sheet.png")
    print("sheets written")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "preview":
        preview()
    elif cmd == "family":
        family()
    elif cmd == "sheets":
        sheets()
