"""Parametric humanoid builder on top of sdfrig: skeleton, organic body masses,
five-finger hands, feet, head features and reusable pose helpers.

Every creature file builds its own variant (proportions, garments, props, facial
construction) from these parts; nothing here is a final creature by itself.
Units are engine units; a 66-unit figure reads as an adult in MAP01.
"""
from __future__ import annotations
import math
import numpy as np
import sdfrig as S

F32 = np.float32

DEFAULT_PROPS = dict(
    height=66.0, pelvis_z=35.0, spine_len=4.0, chest_len=7.5, neck_len=8.0, head_len=3.5,
    shoulder_y=9.0, clav_z=6.0, upper_arm=13.0, forearm=12.0, hip_y=3.8, thigh=16.5, shin=15.5,
    chest_r=(5.6, 9.2, 8.2), pelvis_r=(5.2, 6.6, 5.0), belly_r=(5.0, 5.8, 4.5),
    upper_arm_r=(2.9, 2.4), forearm_r=(2.5, 1.7), thigh_r=(3.6, 2.7), shin_r=(2.7, 1.9),
    deltoid_r=3.3, neck_r=2.2, trap_r=2.0, scapula_r=(1.6, 2.6, 3.2),
    hand_scale=1.0, foot_len=9.0, foot_w=3.6, foot_h=2.8,
)


# ------------------------------------------------------------- skeleton
def build_skeleton(rig: S.Rig, P):
    rig.bone("root", None, (0, 0, P["pelvis_z"]))
    rig.bone("spine", "root", (0, 0, P["spine_len"]))
    rig.bone("chest", "spine", (0, 0, P["chest_len"]))
    rig.bone("neck", "chest", (0.6, 0, P["neck_len"]))
    rig.bone("head", "neck", (0, 0, P["head_len"]))
    for side, sy in (("l", 1), ("r", -1)):
        rig.bone(f"shoulder_{side}", "chest", (0.0, sy * P["shoulder_y"], P["clav_z"]))
        rig.bone(f"elbow_{side}", f"shoulder_{side}", (0, 0, -P["upper_arm"]))
        rig.bone(f"wrist_{side}", f"elbow_{side}", (0, 0, -P["forearm"]))
        rig.bone(f"hip_{side}", "root", (0, sy * P["hip_y"], -1.0))
        rig.bone(f"knee_{side}", f"hip_{side}", (0, 0, -P["thigh"]))
        rig.bone(f"ankle_{side}", f"knee_{side}", (0, 0, -P["shin"]))


# ---------------------------------------------------------------- body
def build_body(rig: S.Rig, P, M, skin_arms=True, skin_legs=False):
    """M: dict of material ids: skin, torso, pelvis, arm_upper, arm_lower, leg_upper, leg_lower, shoe."""
    B = P
    cr = B["chest_r"]
    # pelvis / belly / chest as blended organic masses (chest is a rounded slab, not a ball)
    rig.add("ellipsoid", "root", (0.2, 0, 0.0), B["pelvis_r"], M["pelvis"], blend=3.0)
    rig.add("ellipsoid", "spine", (0.6, 0, 1.5), B["belly_r"], M["torso"], blend=3.5)
    rig.add("rbox", "chest", (0.0, 0, 0.6), (cr[0] * 0.78, cr[1] * 0.86, cr[2] * 0.72, min(cr) * 0.75), M["torso"], blend=3.0)
    rig.add("ellipsoid", "chest", (0.6, 0, 3.6), (cr[0] * 0.9, cr[1] * 0.92, cr[2] * 0.55), M["torso"], blend=3.0)   # upper chest plane
    # clavicles and trapezius ridges from the neck base to the shoulder points
    for sy in (1, -1):
        rig.capsule_between("chest", (2.6, sy * 1.0, B["clav_z"] + 0.2), (1.4, sy * (B["shoulder_y"] - 1.2), B["clav_z"] + 0.6), 0.85, M["torso"], r2=1.0, blend=1.6)
        rig.capsule_between("chest", (-0.6, 0, B["clav_z"] + 2.2), (-0.8, sy * (B["shoulder_y"] - 1.6), B["clav_z"] + 0.2), B["trap_r"], M["torso"], r2=B["trap_r"] * 0.8, blend=2.2)
        rig.add("ellipsoid", "chest", (-3.2, sy * 4.0, 2.2), B["scapula_r"], M["torso"], blend=2.4)
        rig.add("ellipsoid", f"shoulder_{'l' if sy > 0 else 'r'}", (0, 0, 0.2), (B["deltoid_r"], B["deltoid_r"] * 0.9, B["deltoid_r"] * 1.1), M["arm_upper"], blend=2.0)
    # neck: explicit column with sternomastoid swell, rising clear of the trapezius
    rig.capsule_between("neck", (0, 0, -2.0), (0.5, 0, B["head_len"] + 1.5), B["neck_r"], M["skin"], r2=B["neck_r"] * 1.08, blend=1.6)
    rig.capsule_between("neck", (1.0, 0, -1.8), (1.1, 0, B["head_len"] - 0.6), B["neck_r"] * 0.55, M["skin"], r2=B["neck_r"] * 0.5, blend=1.2)
    # limbs
    for side in ("l", "r"):
        ua0, ua1 = B["upper_arm_r"]
        fa0, fa1 = B["forearm_r"]
        rig.capsule_between(f"shoulder_{side}", (0, 0, -1.0), (0, 0, -B["upper_arm"] + 0.5), ua0, M["arm_upper"], r2=ua1, blend=2.2)
        rig.add("ellipsoid", f"elbow_{side}", (0, 0, 0), (ua1 * 1.0, ua1 * 0.95, ua1 * 1.15), M["arm_lower"] if skin_arms else M["arm_upper"], blend=2.0)
        rig.capsule_between(f"elbow_{side}", (0, 0, -0.5), (0, 0, -B["forearm"] + 0.3), fa0, M["arm_lower"], r2=fa1, blend=2.0)
        th0, th1 = B["thigh_r"]
        sh0, sh1 = B["shin_r"]
        rig.capsule_between(f"hip_{side}", (0, 0, 1.0), (0, 0, -B["thigh"] + 0.5), th0, M["leg_upper"], r2=th1, blend=2.5)
        rig.add("ellipsoid", f"knee_{side}", (0.3, 0, 0), (th1 * 1.05, th1 * 0.95, th1 * 1.2), M["leg_upper"], blend=2.0)
        rig.capsule_between(f"knee_{side}", (0, 0, -0.5), (0, 0, -B["shin"] + 1.0), sh0, M["leg_lower"], r2=sh1, blend=2.0)
        # foot: rounded shoe from heel to toe (+x), sole 2.8 below the ankle
        fl, fw, fh = B["foot_len"], B["foot_w"], B["foot_h"]
        rig.add("rbox", f"ankle_{side}", (fl * 0.32, 0, -fh * 0.55), (fl * 0.5, fw * 0.5, fh * 0.5, 0.9), M["shoe"], group=f"foot_{side}", blend=1.2)
        rig.add("ellipsoid", f"ankle_{side}", (-1.2, 0, -0.6), (2.2, fw * 0.48, 1.9), M["shoe"], group=f"foot_{side}", blend=1.2)
        rig.add("ellipsoid", f"ankle_{side}", (fl * 0.62, 0, -fh * 0.5), (2.6, fw * 0.46, fh * 0.42), M["shoe"], group=f"foot_{side}", blend=1.5)
        # ankle joins the shin
        rig.add("ellipsoid", f"ankle_{side}", (0, 0, 0.3), (sh1 * 0.9, sh1 * 0.85, 1.6), M["leg_lower"], blend=1.5)


# ---------------------------------------------------------------- hands
def add_hand(rig: S.Rig, side, mat_skin, mat_nail=None, curl=0.35, spread=0.15, scale=1.0, thumb_opp=0.5,
             per_finger=None, bone=None, base=(0, 0, 0), rot=None, group=None):
    """Five-finger hand in the wrist bone frame: -z along the fingers, +x is the palm side.
    side: 'l' or 'r' (thumb toward +y for the left hand). curl 0..1, spread 0..1."""
    sy = 1.0 if side == "l" else -1.0
    bone = bone or f"wrist_{side}"
    R = np.eye(3, dtype=F32) if rot is None else np.asarray(rot, F32)
    base = np.asarray(base, F32)
    s = scale
    grp = group or f"hand_{side}"

    def T(p):
        return base + R @ (np.asarray(p, F32) * s)

    def cap(a, b, r0, r1, mat, blend=0.8):
        a, b = T(a), T(b)
        mid = (a + b) / 2; d = b - a; L = float(np.linalg.norm(d))
        rig.add("tcapsule", bone, mid, (L / 2, r0 * s, r1 * s), mat, rot=S.look_rot(d), group=grp, blend=blend * s)

    # palm and wrist
    rig.add("rbox", bone, T((0.0, 0, -3.2)), (0.85 * s, 2.15 * s, 3.1 * s, 0.7 * s), mat_skin, rot=R, group=grp, blend=1.0 * s)
    rig.add("ellipsoid", bone, T((0.0, 0, -0.6)), (1.05 * s, 1.75 * s, 1.5 * s), mat_skin, rot=R, group=grp, blend=1.2 * s)
    # heel of the thumb (thenar) and hypothenar
    rig.add("ellipsoid", bone, T((0.35, sy * 1.5, -2.6)), (0.95 * s, 1.0 * s, 1.7 * s), mat_skin, rot=R, group=grp, blend=1.0 * s)
    rig.add("ellipsoid", bone, T((0.2, -sy * 1.7, -3.6)), (0.8 * s, 0.7 * s, 2.0 * s), mat_skin, rot=R, group=grp, blend=1.0 * s)
    fingers = [  # (y offset, lengths, base radius)
        (1.55, (2.4, 1.45, 1.15), 0.56),   # index
        (0.55, (2.65, 1.6, 1.2), 0.58),    # middle
        (-0.5, (2.4, 1.45, 1.1), 0.54),    # ring
        (-1.5, (1.85, 1.15, 0.95), 0.48),  # little
    ]
    for i, (yo, lens, r0) in enumerate(fingers):
        c = curl if per_finger is None else per_finger[i]
        start = np.array([0.15, sy * yo, -6.2], F32)
        # spread: small yaw outward; flexion: rotate toward +x (palm side)
        sp = spread * (yo) * 9.0
        ang = 0.0
        d = np.array([0.0, 0.0, -1.0], F32)
        rr = r0
        for j, L in enumerate(lens):
            flex = (68, 84, 52)[j] * c
            ang += flex
            a = math.radians(ang); b = math.radians(sp)
            d = np.array([math.sin(a), sy * math.sin(b) * math.cos(a) * 0.3, -math.cos(a)], F32)
            d /= np.linalg.norm(d)
            end = start + d * L
            r1 = rr * (0.9 if j < 2 else 0.8)
            cap(start, end, rr, r1, mat_skin, blend=0.7)
            if j == 2 and mat_nail is not None:
                nail = end - d * 0.45
                rig.add("ellipsoid", bone, T(nail + np.array([-0.45, 0, 0], F32) * 0.0), (0.42 * s, 0.32 * s, 0.5 * s), mat_nail, rot=R @ S.look_rot(d), group=grp, blend=0.2)
            start = end; rr = r1
    # thumb: metacarpal from the palm base, opposed toward the palm
    tbase = np.array([0.35, sy * 2.0, -2.2], F32)
    tdir = np.array([0.55 + 0.5 * thumb_opp, sy * (0.85 - 0.5 * thumb_opp), -0.55], F32); tdir /= np.linalg.norm(tdir)
    p1 = tbase + tdir * 2.4
    cap(tbase, p1, 0.85, 0.66, mat_skin, blend=0.9)
    tc = curl * 0.8
    a1 = math.radians(45 * tc); d2 = np.array([tdir[0] * math.cos(a1) + 0.5 * math.sin(a1), tdir[1] * math.cos(a1), tdir[2] * math.cos(a1) - 0.6 * math.sin(a1)], F32); d2 /= np.linalg.norm(d2)
    p2 = p1 + d2 * 1.9
    cap(p1, p2, 0.66, 0.55, mat_skin, blend=0.6)
    a2 = math.radians(55 * tc); d3 = np.array([d2[0] * math.cos(a2) + 0.6 * math.sin(a2), d2[1] * math.cos(a2), d2[2] * math.cos(a2) - 0.6 * math.sin(a2)], F32); d3 /= np.linalg.norm(d3)
    p3 = p2 + d3 * 1.45
    cap(p2, p3, 0.55, 0.45, mat_skin, blend=0.5)
    if mat_nail is not None:
        rig.add("ellipsoid", bone, T(p3 - d3 * 0.4), (0.4 * s, 0.32 * s, 0.48 * s), mat_nail, rot=R @ S.look_rot(d3), group=grp, blend=0.2)


# ----------------------------------------------------------------- head
def build_head(rig: S.Rig, M, skull=(4.5, 4.1, 5.3), jaw_open=0.0, brow=1.0, gaunt=0.5, sockets=True,
               eyes=True, ears=True, mouth=True, nose=1.0, bone="head", group="head", offset=(0.8, 0, 4.8)):
    """Skull + jaw + brow + nose + cheekbones + eyes. offset = skull centre in the head bone."""
    ox, oy, oz = offset
    sx, sy, sz = skull
    # cranium (scalp) and the face mass in front of it
    rig.add("ellipsoid", bone, (ox - 0.6, oy, oz + 0.8), (sx * 0.98, sy, sz * 0.96), M["scalp"], group=group, blend=1.4)
    rig.add("ellipsoid", bone, (ox + 0.9, oy, oz - 0.6), (sx * 0.80, sy * 0.90, sz * 0.86), M["skin"], group=group, blend=1.6)
    # forehead plane and overhanging brow ridge (the sockets sit under it)
    rig.add("ellipsoid", bone, (ox + sx * 0.62, oy, oz + 2.6), (1.6, sy * 0.78, 1.9), M["skin"], group=group, blend=1.4)
    rig.capsule_between(bone, (ox + sx * 0.86, oy - 2.6, oz + 1.25), (ox + sx * 0.86, oy + 2.6, oz + 1.25), 0.95 * brow, M["skin"], group=group, blend=0.9)
    # mandible: angled box with chin, gaunt cheeks come from a narrower jaw
    jw = sy * (0.80 - 0.18 * gaunt)
    rig.add("rbox", bone, (ox + 1.0, oy, oz - 3.3 - jaw_open * 0.8), (sx * 0.66, jw, 1.35, 1.1), M["skin"], group=group, blend=1.3)
    rig.add("ellipsoid", bone, (ox + sx * 0.78, oy, oz - 4.2 - jaw_open * 1.2), (1.5, 1.6, 1.25), M["skin"], group=group, blend=1.1)
    # cheekbones (zygomatic), hollow cheeks below them
    for s in (1, -1):
        rig.add("ellipsoid", bone, (ox + sx * 0.66, oy + s * 2.75, oz - 0.45), (1.6, 1.15, 1.2), M["skin"], group=group, blend=1.1)
        rig.add("ellipsoid", bone, (ox + sx * 0.72, oy + s * 2.7, oz - 2.3), (1.4, 1.0, 1.1), M["skin"], group=group, blend=0.9 + 0.5 * gaunt, op="subtract")
    # nose: bridge from the brow, tip and alae
    if nose > 0:
        rig.capsule_between(bone, (ox + sx * 0.84, oy, oz + 0.9), (ox + sx * 1.06, oy, oz - 1.7), 0.55 * nose, M["skin"], r2=0.72 * nose, group=group, blend=0.8)
        rig.add("ellipsoid", bone, (ox + sx * 1.02, oy, oz - 1.95), (0.85 * nose, 1.15 * nose, 0.65 * nose), M["skin"], group=group, blend=0.6)
    # eye sockets (deep, under the brow) with recessed eyes and upper lids
    for s in (1, -1):
        ex, ey, ez = ox + sx * 0.84, oy + s * 1.6, oz + 0.35
        if sockets:
            rig.add("ellipsoid", bone, (ex + 0.35, ey, ez - 0.1), (1.2, 1.12, 0.95), M["skin"], group=group, blend=0.5, op="subtract")
        if eyes:
            rig.add("ellipsoid", bone, (ex - 0.85, ey, ez - 0.05), (0.70, 0.70, 0.70), M["eye"], group="eyes", blend=0.0)
            rig.add("ellipsoid", bone, (ex - 0.55, ey, ez + 0.55), (0.75, 1.0, 0.42), M["skin"], group=group, blend=0.35)  # upper lid
    # temples hollow
    for s in (1, -1):
        rig.add("ellipsoid", bone, (ox + 0.8, oy + s * (sy * 0.95), oz + 1.6), (1.4, 0.8, 1.5), M["skin"], group=group, blend=0.8, op="subtract")
    # ears
    if ears:
        for s in (1, -1):
            rig.add("ellipsoid", bone, (ox - 0.9, oy + s * (sy + 0.15), oz - 0.4), (0.75, 0.45, 1.25), M["skin"], group=group, blend=0.5)
    # mouth: closed lips as a shallow slit between two lip rolls
    if mouth:
        rig.add("rbox", bone, (ox + sx * 0.96, oy, oz - 2.95), (0.6, 1.25, 0.16 + jaw_open * 0.9, 0.12), M["skin"], group=group, blend=0.25, op="subtract")


# ---------------------------------------------------------------- poses
def arm(swing=0.0, out=0.0, twist=0.0, elbow=0.0, wrist=(0, 0, 0), side="l"):
    """swing>0 forward, out>0 raises the arm sideways away from the body, elbow>0 bends."""
    sy = 1.0 if side == "l" else -1.0
    return {f"shoulder_{side}": (-sy * out, -swing, twist), f"elbow_{side}": (0, elbow, 0), f"wrist_{side}": tuple(wrist)}


def leg(flex=0.0, knee=0.0, ankle=0.0, out=0.0, side="l"):
    """flex>0 thigh forward, knee>0 bends back, ankle>0 toes down."""
    sy = 1.0 if side == "l" else -1.0
    return {f"hip_{side}": (-sy * out, -flex, 0), f"knee_{side}": (0, knee, 0), f"ankle_{side}": (0, -ankle, 0)}


def merge(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out


def walk(phase, stride=32.0, lean=8.0, bob=0.0, arm_swing=22.0, elbow=25.0, knee_lift=38.0):
    """Four-phase driven walk: phase 0 = left contact, 0.25 = left passing, 0.5 = right contact, 0.75 = right passing."""
    t = phase * 2 * math.pi
    fl = math.sin(t) * stride / 2 * 1.0          # left thigh flex (forward positive)
    fr = math.sin(t + math.pi) * stride / 2
    kl = max(0.0, -math.cos(t)) * knee_lift + 6   # knee bends on the swing-through
    kr = max(0.0, -math.cos(t + math.pi)) * knee_lift + 6
    # positive Y rotation = forward tilt. Hunch lives in spine/chest; root carries only a little whole-body lean.
    pose = merge(
        {"root": (0, lean * 0.4, 0), "spine": (0, 2 + lean * 0.3, 0), "chest": (0, 3 + lean * 0.3, math.sin(t) * 4), "neck": (0, lean * 0.5, 0), "head": (0, -lean * 0.3, -math.sin(t) * 3)},
        leg(fl, kl, ankle=math.sin(t) * 6, side="l"), leg(fr, kr, ankle=math.sin(t + math.pi) * 6, side="r"),
        arm(swing=math.sin(t + math.pi) * arm_swing + 6, out=6, elbow=elbow + max(0, math.sin(t + math.pi)) * 18, side="l"),
        arm(swing=math.sin(t) * arm_swing + 6, out=6, elbow=elbow + max(0, math.sin(t)) * 18, side="r"),
    )
    pose["root_offset"] = (0, 0, bob * math.cos(2 * t))
    return pose


def stand(lean=6.0):
    return merge({"root": (0, lean * 0.3, 0), "spine": (0, 2 + lean * 0.35, 0), "chest": (0, lean * 0.35, 0), "neck": (0, lean * 0.6, 0), "head": (0, -lean * 0.4, 0)},
                 leg(4, 8, 2, out=3, side="l"), leg(-4, 6, 0, out=3, side="r"),
                 arm(swing=10, out=8, elbow=22, side="l"), arm(swing=8, out=8, elbow=20, side="r"))


def solve_arm(rig, pose, side, target, iters=80, wrist_len=6.5):
    """Numerical 3-angle IK: sets shoulder (out, swing, twist) and elbow bend so the wrist bone
    tip (wrist + wrist_len along the hand) reaches target (world). Keeps whatever else is in pose."""
    target = np.asarray(target, np.float32)
    keys = [f"shoulder_{side}", f"elbow_{side}"]
    sy = 1.0 if side == "l" else -1.0
    cur = list(pose.get(keys[0], (0, 0, 0))) + [pose.get(keys[1], (0, 0, 0))[1]]

    def err(v):
        p = dict(pose)
        p[keys[0]] = (v[0], v[1], v[2])
        p[keys[1]] = (0, v[3], 0)
        wb = rig.world_bones(p)
        R, t = wb[f"wrist_{side}"]
        tip = t + R @ np.array([0, 0, -wrist_len], np.float32)
        return float(np.sum((tip - target) ** 2))

    best = err(cur)
    step = 25.0
    for _ in range(iters):
        improved = False
        for k in range(4):
            for d in (step, -step):
                trial = list(cur); trial[k] += d
                if k == 3:
                    trial[3] = float(np.clip(trial[3], 0, 150))
                e = err(trial)
                if e < best - 1e-4:
                    best, cur, improved = e, trial, True
        if not improved:
            step *= 0.5
            if step < 0.25:
                break
    pose = dict(pose)
    pose[keys[0]] = (cur[0], cur[1], cur[2])
    pose[keys[1]] = (0, cur[3], 0)
    return pose, math.sqrt(best)


def lying(face_down=True, roll=0.0, turn=0.0):
    """Rotation that lays the figure on the floor along +x. Combine with a floor snap."""
    R = S.rot_y(90.0 if face_down else -90.0)
    R = S.rot_z(turn) @ S.rot_x(roll) @ R
    return R
