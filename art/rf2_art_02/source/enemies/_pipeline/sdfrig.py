"""Smooth signed-distance creature rig and sprite renderer (RED FLAGS 2 final enemies).

Creatures are built from smooth-blended SDF primitives attached to a posable
skeleton, rendered by sphere tracing into clean-alpha sprites (8 Doom rotations)
with physically plausible neutral lighting, ambient occlusion, soft shadows and
procedural material detail. No polygon faceting, no sphere joints: limbs are
blended with smooth unions so the body reads as one organic mass.

Conventions (match the existing S1 enemy source): X forward, Y left, Z up, world
units = engine units, floor at Z = 0. Camera looks along +X; rotation 1 shows the
creature facing the camera. Doom stretches sprites 1.2x vertically, so frames are
rendered pre-squashed (PIXEL_STRETCH) unless disabled.
"""
from __future__ import annotations
import math, struct, zlib, json
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from PIL import Image

F32 = np.float32

# ------------------------------------------------------------------ maths
def rot_x(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], F32)

def rot_y(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], F32)

def rot_z(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], F32)

def euler(rx=0.0, ry=0.0, rz=0.0):
    """Z * Y * X order (apply X first)."""
    return rot_z(rz) @ rot_y(ry) @ rot_x(rx)

def look_rot(direction, up=(0, 0, 1)):
    """Rotation whose local +Z axis points along 'direction' (for capsules along an axis)."""
    d = np.asarray(direction, F32); d = d / max(1e-9, np.linalg.norm(d))
    u = np.asarray(up, F32)
    if abs(np.dot(u, d)) > 0.98:
        u = np.array([1, 0, 0], F32)
    x = np.cross(u, d); x /= max(1e-9, np.linalg.norm(x))
    y = np.cross(d, x)
    return np.stack([x, y, d], 1).astype(F32)

def smin(a, b, k):
    """Polynomial smooth minimum (k = blend radius)."""
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * h - k * h * (1.0 - h)

def hash3(p):
    x = np.floor(p).astype(np.int64)
    n = (x[..., 0] * 73856093) ^ (x[..., 1] * 19349663) ^ (x[..., 2] * 83492791)
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return ((n & 0x7fffffff).astype(F32) / F32(0x7fffffff))

def vnoise(p):
    """3D value noise in [0,1], trilinear."""
    i = np.floor(p); f = p - i
    f = f * f * (3 - 2 * f)
    def h(dx, dy, dz):
        return hash3(i + np.array([dx, dy, dz], F32))
    x00 = h(0, 0, 0) * (1 - f[..., 0]) + h(1, 0, 0) * f[..., 0]
    x10 = h(0, 1, 0) * (1 - f[..., 0]) + h(1, 1, 0) * f[..., 0]
    x01 = h(0, 0, 1) * (1 - f[..., 0]) + h(1, 0, 1) * f[..., 0]
    x11 = h(0, 1, 1) * (1 - f[..., 0]) + h(1, 1, 1) * f[..., 0]
    y0 = x00 * (1 - f[..., 1]) + x10 * f[..., 1]
    y1 = x01 * (1 - f[..., 1]) + x11 * f[..., 1]
    return y0 * (1 - f[..., 2]) + y1 * f[..., 2]

def fbm(p, octaves=3, lac=2.1, gain=0.5):
    v = np.zeros(p.shape[:-1], F32); amp = 1.0; s = 1.0; norm = 0.0
    for _ in range(octaves):
        v += amp * vnoise(p * s); norm += amp; amp *= gain; s *= lac
    return v / norm

# ------------------------------------------------------------- primitives
@dataclass
class Prim:
    kind: str                      # capsule | ellipsoid | rbox | tcapsule | torus | cylinder | cone
    bone: str
    pos: np.ndarray                # local position (bone space)
    rot: np.ndarray                # local rotation matrix (bone space)
    params: tuple
    material: int
    group: str = "body"            # blend group; groups union hard, members blend smoothly
    blend: float = 1.0             # smooth-union radius with previous members of the group
    op: str = "union"              # union | subtract
    # world cache
    wpos: np.ndarray = None
    wrot: np.ndarray = None
    radius: float = 0.0            # bounding sphere radius (world)

    def local_sdf(self, q):
        k = self.kind; P = self.params
        if k == "capsule":            # (half_len, radius) along local z
            hl, r = P
            z = np.clip(q[..., 2], -hl, hl)
            d = q.copy(); d[..., 2] -= z
            return np.linalg.norm(d, axis=-1) - r
        if k == "tcapsule":           # tapered capsule (half_len, r0 at -z, r1 at +z)
            hl, r0, r1 = P
            t = np.clip((q[..., 2] + hl) / (2 * hl), 0, 1)
            z = np.clip(q[..., 2], -hl, hl)
            d = q.copy(); d[..., 2] -= z
            return np.linalg.norm(d, axis=-1) - (r0 + (r1 - r0) * t)
        if k == "ellipsoid":          # (rx, ry, rz)
            r = np.asarray(P, F32)
            k0 = np.linalg.norm(q / r, axis=-1)
            k1 = np.linalg.norm(q / (r * r), axis=-1)
            return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)
        if k == "rbox":               # (hx, hy, hz, round)
            h = np.asarray(P[:3], F32); rr = P[3]
            d = np.abs(q) - h + rr
            return np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(np.max(d, axis=-1), 0) - rr
        if k == "torus":              # (R, r) in local xy plane
            R, r = P
            qxy = np.sqrt(q[..., 0] ** 2 + q[..., 1] ** 2) - R
            return np.sqrt(qxy ** 2 + q[..., 2] ** 2) - r
        if k == "cylinder":           # (half_len, radius, round) along z, rounded edges
            hl, r, rr = P
            dxy = np.sqrt(q[..., 0] ** 2 + q[..., 1] ** 2) - r + rr
            dz = np.abs(q[..., 2]) - hl + rr
            d = np.stack([dxy, dz], -1)
            return np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(np.max(d, axis=-1), 0) - rr
        if k == "cone":               # (half_len, r_base at -z, r_top at +z) sharp-ish cone
            hl, r0, r1 = P
            t = np.clip((q[..., 2] + hl) / (2 * hl), 0, 1)
            rad = r0 + (r1 - r0) * t
            dxy = np.sqrt(q[..., 0] ** 2 + q[..., 1] ** 2) - rad
            dz = np.abs(q[..., 2]) - hl
            return np.maximum(dxy * math.cos(math.atan2(abs(r0 - r1), 2 * hl)), dz)
        raise ValueError(k)

    def bound(self):
        k = self.kind; P = self.params
        if k in ("capsule",):
            return P[0] + P[1]
        if k in ("tcapsule", "cone"):
            return P[0] + max(P[1], P[2])
        if k == "ellipsoid":
            return max(P)
        if k == "rbox":
            return math.sqrt(P[0] ** 2 + P[1] ** 2 + P[2] ** 2)
        if k == "torus":
            return P[0] + P[1]
        if k == "cylinder":
            return math.sqrt(P[0] ** 2 + P[1] ** 2)
        return 1.0


@dataclass
class Material:
    name: str
    albedo: tuple
    rough: float = 0.7
    spec: float = 0.25
    detail: str = "none"          # none | skin | cloth | leather | steel | paper | rubber | canvas | wood
    detail_scale: float = 1.0
    detail_amp: float = 0.3
    albedo2: tuple = None         # secondary tone for patterns
    sss: float = 0.0              # cheap subsurface warm wrap for skin


@dataclass
class Bone:
    name: str
    parent: str | None
    head: np.ndarray               # rest position in parent space
    rest: np.ndarray = field(default_factory=lambda: np.eye(3, dtype=F32))


class Rig:
    def __init__(self):
        self.bones: dict[str, Bone] = {}
        self.prims: list[Prim] = []
        self.materials: dict[int, Material] = {}
        self.order: list[str] = []

    def bone(self, name, parent, head, rest=None):
        self.bones[name] = Bone(name, parent, np.asarray(head, F32), np.eye(3, dtype=F32) if rest is None else rest)
        self.order.append(name)

    def add(self, kind, bone, pos, params, material, rot=None, group="body", blend=1.0, op="union"):
        p = Prim(kind, bone, np.asarray(pos, F32), np.eye(3, dtype=F32) if rot is None else np.asarray(rot, F32), tuple(params), material, group, blend, op)
        self.prims.append(p)
        return p

    def capsule_between(self, bone, a, b, r, material, r2=None, **kw):
        a, b = np.asarray(a, F32), np.asarray(b, F32)
        mid = (a + b) / 2; d = b - a; L = float(np.linalg.norm(d))
        rot = look_rot(d)
        if r2 is None:
            return self.add("capsule", bone, mid, (L / 2, r), material, rot=rot, **kw)
        return self.add("tcapsule", bone, mid, (L / 2, r, r2), material, rot=rot, **kw)

    # ---- forward kinematics -------------------------------------------------
    def world_bones(self, pose):
        """pose: dict bone -> (rx, ry, rz) degrees (+ optional 'root_offset', 'root_rot')."""
        out = {}
        for name in self.order:
            b = self.bones[name]
            local_rot = euler(*pose.get(name, (0, 0, 0)))
            if b.parent is None:
                # every root bone can be placed independently: "<name>_rot" / "<name>_offset"
                RR = np.asarray(pose.get(f"{name}_rot", np.eye(3, dtype=F32)), F32)
                R = RR @ b.rest @ local_rot
                t = np.asarray(pose.get(f"{name}_offset", (0, 0, 0)), F32) + RR @ b.head
            else:
                pR, pt = out[b.parent]
                R = pR @ b.rest @ local_rot
                t = pt + pR @ b.head
            out[name] = (R.astype(F32), t.astype(F32))
        return out

    def place(self, pose, model_rot=None, model_off=(0, 0, 0)):
        wb = self.world_bones(pose)
        M = np.eye(3, dtype=F32) if model_rot is None else np.asarray(model_rot, F32)
        off = np.asarray(model_off, F32)
        for p in self.prims:
            R, t = wb[p.bone]
            p.wrot = (M @ R @ p.rot).astype(F32)
            p.wpos = (M @ (t + R @ p.pos) + off).astype(F32)
            p.radius = p.bound()
        return wb

    # ---- SDF evaluation -----------------------------------------------------
    def sdf(self, pts, want_material=False, min_only=False):
        """pts: (N,3). Returns d (N,) and material id (N,) when requested."""
        n = pts.shape[0]
        INF = F32(1e9)
        groups: dict[str, tuple] = {}
        subtractors: list = []
        # evaluate largest primitives first so culling has a good running minimum
        order = sorted(range(len(self.prims)), key=lambda i: -self.prims[i].radius)
        for i in order:
            p = self.prims[i]
            if p.op == "subtract":
                subtractors.append(p)
                continue
            gd, gm, gcount = groups.get(p.group, (None, None, 0))
            # bounding-sphere lower bound for culling
            lb = np.linalg.norm(pts - p.wpos, axis=-1) - p.radius
            if gd is None:
                sel = None
            else:
                thresh = gd + p.blend + 0.5
                sel = np.nonzero(lb < thresh)[0]
                if sel.size == 0:
                    groups[p.group] = (gd, gm, gcount + 1)
                    continue
                if sel.size > 0.7 * n:
                    sel = None
            sub = pts if sel is None else pts[sel]
            q = (sub - p.wpos) @ p.wrot   # world -> local (rot^T)
            d = p.local_sdf(q).astype(F32)
            if gd is None:
                gd = np.full(n, INF, F32); gm = np.zeros(n, np.int16)
                if sel is None:
                    gd[:] = d; gm[:] = p.material
                else:
                    gd[sel] = d; gm[sel] = p.material
                groups[p.group] = (gd, gm, 1)
                continue
            if sel is None:
                closer = d < gd
                nd = smin(gd, d, p.blend) if p.blend > 0 else np.minimum(gd, d)
                gm = np.where(closer, p.material, gm)
                gd = nd
            else:
                cur = gd[sel]
                nd = smin(cur, d, p.blend) if p.blend > 0 else np.minimum(cur, d)
                gm[sel] = np.where(d < cur, p.material, gm[sel])
                gd[sel] = nd
            groups[p.group] = (gd, gm, gcount + 1)
        # subtractions carve only their own group (eye sockets do not eat the eyeballs)
        for p in subtractors:
            if p.group not in groups:
                continue
            gd, gm, gc = groups[p.group]
            lb = np.linalg.norm(pts - p.wpos, axis=-1) - p.radius - p.blend - 0.5
            sel = np.nonzero(lb < 0)[0]
            if sel.size == 0:
                continue
            q = (pts[sel] - p.wpos) @ p.wrot
            d = p.local_sdf(q).astype(F32)
            k = p.blend
            cur = gd[sel]
            if k > 0:
                h = np.clip(0.5 - 0.5 * (cur + d) / k, 0, 1)
                gd[sel] = (cur + (-d - cur) * h + k * h * (1 - h)).astype(F32)
            else:
                gd[sel] = np.maximum(cur, -d)
            groups[p.group] = (gd, gm, gc)
        total = None; mat = None
        for gd, gm, _ in groups.values():
            if total is None:
                total, mat = gd.copy(), gm.copy()
            else:
                closer = gd < total
                total = np.where(closer, gd, total); mat = np.where(closer, gm, mat)
        if want_material:
            return total, mat
        return total

    def bbox(self, margin=2.0):
        lo = np.array([1e9] * 3, F32); hi = -lo
        for p in self.prims:
            if p.op == "subtract":
                continue
            lo = np.minimum(lo, p.wpos - p.radius); hi = np.maximum(hi, p.wpos + p.radius)
        return lo - margin, hi + margin

    def snap_to_floor(self, pose, model_rot=None, model_off=(0, 0, 0), samples=20000, seed=0):
        """Find the lowest surface point and return the vertical offset that puts it on Z=0."""
        self.place(pose, model_rot, model_off)
        lo, hi = self.bbox(0.5)
        rng = np.random.default_rng(seed)
        # candidate points: dense in the lowest 25% of the bbox
        zmax = lo[2] + 0.25 * (hi[2] - lo[2])
        pts = np.stack([rng.uniform(lo[0], hi[0], samples), rng.uniform(lo[1], hi[1], samples), rng.uniform(lo[2], zmax, samples)], 1).astype(F32)
        d = self.sdf(pts)
        # move each sample to the surface along -gradient approx: use d as vertical offset estimate
        inside = pts[d < 0.5]
        if inside.size == 0:
            return -float(lo[2])
        # refine: for the lowest candidates, march downward until the sdf turns positive
        cand = inside[np.argsort(inside[:, 2])[:400]]
        dz = self.sdf(cand)
        zmin = float(np.min(cand[:, 2] - np.abs(dz)))  # surface is at most |d| below
        return -zmin


# ---------------------------------------------------------------- shading
def shade(rig: Rig, hit, nrm, mat_id, materials, light):
    """Neutral studio lighting: key + fill + rim + hemispheric ambient, AO and soft shadow."""
    n = nrm
    col = np.zeros((hit.shape[0], 3), F32)
    alb = np.zeros((hit.shape[0], 3), F32); rough = np.ones(hit.shape[0], F32); spec = np.zeros(hit.shape[0], F32); sss = np.zeros(hit.shape[0], F32)
    for mid, m in materials.items():
        sel = mat_id == mid
        if not sel.any():
            continue
        base = np.asarray(m.albedo, F32)[None, :].repeat(int(sel.sum()), 0)
        p = hit[sel]
        if m.detail != "none":
            base, n_sel = apply_detail(m, p, n[sel], base)
            n[sel] = n_sel
        alb[sel] = base; rough[sel] = m.rough; spec[sel] = m.spec; sss[sel] = m.sss
    n = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    key_dir = np.asarray(light["key_dir"], F32); key_dir /= np.linalg.norm(key_dir)
    fill_dir = np.asarray(light["fill_dir"], F32); fill_dir /= np.linalg.norm(fill_dir)
    rim_dir = np.asarray(light["rim_dir"], F32); rim_dir /= np.linalg.norm(rim_dir)
    view = np.asarray(light["view_dir"], F32); view /= np.linalg.norm(view)
    ao = ambient_occlusion(rig, hit, n)
    sh = soft_shadow(rig, hit + n * 0.15, key_dir, light.get("shadow_k", 6.0))
    ndl_key = np.clip(n @ key_dir, 0, 1)
    wrap = np.clip((n @ key_dir + sss * 0.6) / (1 + sss * 0.6), 0, 1)
    ndl_key = ndl_key * (1 - sss) + wrap * sss
    ndl_fill = np.clip(n @ fill_dir, 0, 1)
    ndl_rim = np.clip(n @ rim_dir, 0, 1) ** 2
    hemi = 0.5 + 0.5 * n[:, 2]
    amb = np.asarray(light["ambient"], F32)[None, :] * (0.45 + 0.55 * hemi)[:, None] * ao[:, None]
    h = key_dir - view; h /= np.linalg.norm(h)
    ndh = np.clip(n @ h, 0, 1)
    gloss = 2.0 + (1 - rough) * 60.0
    specular = spec * (ndh ** gloss) * (gloss + 2) / 8 * ndl_key * sh
    col = alb * (np.asarray(light["key"], F32)[None, :] * (ndl_key * sh)[:, None] + np.asarray(light["fill"], F32)[None, :] * ndl_fill[:, None] + np.asarray(light["rim"], F32)[None, :] * ndl_rim[:, None] * ao[:, None] + amb)
    col += (np.asarray(light["key"], F32)[None, :] * specular[:, None])
    # subtle warm subsurface on skin in shadow terminator
    col += alb * (sss * 0.25 * (1 - ndl_key) * ao)[:, None] * np.array([1.0, 0.55, 0.45], F32)[None, :]
    return np.clip(col, 0, 4), n


def apply_detail(m: Material, p, n, base):
    s = m.detail_scale; amp = m.detail_amp
    if m.detail == "skin":
        v = fbm(p * 1.8 * s, 3) - 0.5
        base = base * (1 + 0.10 * amp * v[:, None] * np.array([1.0, 0.7, 0.6], F32)[None, :])
        n = n + amp * 0.10 * np.stack([fbm(p * 6 * s + 3.1, 2) - 0.5, fbm(p * 6 * s + 7.7, 2) - 0.5, fbm(p * 6 * s + 1.3, 2) - 0.5], 1)
    elif m.detail == "cloth":
        # woven twill (fine), soft folds (coarse normal perturbation) and broad grime areas
        wx = np.sin((p[:, 0] * 1.3 + p[:, 2] * 5.0) * s * 6.0) * np.sin((p[:, 1] * 5.0 - p[:, 2] * 1.1) * s * 6.0)
        g = fbm(p * 0.35 * s + 4.2, 3) - 0.5
        tone2 = np.asarray(m.albedo2 if m.albedo2 else m.albedo, F32)
        base = base * (1 + 0.05 * amp * wx[:, None]) + (tone2[None, :] - base) * np.clip(g * 1.6, 0, 0.45)[:, None] * amp
        # folds: gradient of a coarse noise field, elongated along z (gravity)
        e = 0.35
        q = p * np.array([1.0, 1.0, 0.45], F32)
        f0 = fbm(q * 0.55 * s + 1.7, 2)
        gx = fbm((q + np.array([e, 0, 0], F32)) * 0.55 * s + 1.7, 2) - f0
        gy = fbm((q + np.array([0, e, 0], F32)) * 0.55 * s + 1.7, 2) - f0
        gz = fbm((q + np.array([0, 0, e], F32)) * 0.55 * s + 1.7, 2) - f0
        n = n + amp * 4.5 * np.stack([gx, gy, gz], 1)
        n = n + amp * 0.05 * np.stack([fbm(p * 4 * s + 2.1, 2) - 0.5, fbm(p * 4 * s + 5.7, 2) - 0.5, fbm(p * 4 * s + 9.3, 2) - 0.5], 1)
    elif m.detail == "canvas":
        wx = np.sin(p[:, 0] * s * 9.0) * np.sin(p[:, 1] * s * 9.0) * 0.5 + np.sin(p[:, 2] * s * 9.0) * 0.5
        g = fbm(p * 0.6 * s, 3) - 0.5
        tone2 = np.asarray(m.albedo2 if m.albedo2 else m.albedo, F32)
        base = base * (1 + 0.05 * amp * wx[:, None]) + (tone2[None, :] - base) * np.clip(g * 2.0, 0, 0.7)[:, None] * amp
        n = n + amp * 0.08 * np.stack([fbm(p * 2.5 * s + 2.1, 2) - 0.5, fbm(p * 2.5 * s + 5.7, 2) - 0.5, fbm(p * 2.5 * s + 9.3, 2) - 0.5], 1)
    elif m.detail == "leather":
        g = fbm(p * 5.0 * s, 3) - 0.5
        base = base * (1 + 0.12 * amp * g[:, None])
        n = n + amp * 0.06 * np.stack([fbm(p * 9 * s + 2.1, 2) - 0.5, fbm(p * 9 * s + 5.7, 2) - 0.5, fbm(p * 9 * s + 9.3, 2) - 0.5], 1)
    elif m.detail == "steel":
        g = fbm(p * 3.0 * s, 3) - 0.5
        sc = np.sin(p[:, 2] * 40 * s + fbm(p * 2 * s, 2) * 6) * 0.5
        base = base * (1 + 0.15 * amp * g[:, None] + 0.04 * amp * sc[:, None])
        # rust seeds
        tone2 = np.asarray(m.albedo2 if m.albedo2 else m.albedo, F32)
        r = np.clip((fbm(p * 1.1 * s + 11.0, 3) - 0.62) * 6, 0, 1)
        base = base + (tone2[None, :] - base) * r[:, None] * amp
    elif m.detail == "paper":
        # stacked sheets: fine horizontal lamination lines along z, plus foxing
        lam = np.sin(p[:, 2] * 30 * s) * 0.5 + 0.5
        g = fbm(p * 1.5 * s, 3) - 0.5
        tone2 = np.asarray(m.albedo2 if m.albedo2 else m.albedo, F32)
        base = base * (1 - 0.10 * amp * lam[:, None]) + (tone2[None, :] - base) * np.clip(g * 1.8, 0, 0.6)[:, None] * amp
        n = n + amp * 0.04 * np.stack([np.zeros_like(lam), np.zeros_like(lam), np.sin(p[:, 2] * 30 * s)], 1)
    elif m.detail == "rubber":
        g = fbm(p * 4.0 * s, 2) - 0.5
        base = base * (1 + 0.08 * amp * g[:, None])
    elif m.detail == "wood":
        g = np.sin((p[:, 2] * 2.0 + fbm(p * 0.7 * s, 2) * 4) * s * 4) * 0.5 + 0.5
        tone2 = np.asarray(m.albedo2 if m.albedo2 else m.albedo, F32)
        base = base + (tone2[None, :] - base) * g[:, None] * 0.5 * amp
    elif m.detail == "hair":
        st = np.sin(p[:, 0] * 25 * s + fbm(p * 3 * s, 2) * 8) * 0.5 + 0.5
        base = base * (0.75 + 0.5 * amp * st[:, None])
        n = n + amp * 0.12 * np.stack([fbm(p * 12 * s + 2.1, 2) - 0.5, fbm(p * 12 * s + 5.7, 2) - 0.5, fbm(p * 12 * s + 9.3, 2) - 0.5], 1)
    return np.clip(base, 0, 1).astype(F32), n.astype(F32)


def normals(rig, hit, eps=0.05):
    e = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], F32) * eps
    n = np.zeros_like(hit)
    for k in range(4):
        n += e[k][None, :] * rig.sdf(hit + e[k][None, :])[:, None]
    return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)


def _field(rig):
    """rig or VoxelSDF -> callable distance field"""
    return rig if callable(rig) and not hasattr(rig, "sdf") else rig.sdf


def ambient_occlusion(rig, hit, n, steps=5, dist=2.4):
    f = _field(rig)
    occ = np.zeros(hit.shape[0], F32); w = 1.0
    for i in range(1, steps + 1):
        h = dist * i / steps
        d = f(hit + n * h)
        # floor plane also occludes
        d = np.minimum(d, hit[:, 2] + n[:, 2] * h)
        occ += w * np.clip(h - d, 0, h) / h
        w *= 0.6
    return np.clip(1 - 0.9 * occ / 2.2, 0.15, 1)


def soft_shadow(rig, origin, ldir, k=6.0, tmax=60.0, steps=18):
    f = _field(rig)
    res = np.ones(origin.shape[0], F32)
    t = np.full(origin.shape[0], 0.2, F32)
    ph = np.full(origin.shape[0], 1e10, F32)
    for _ in range(steps):
        p = origin + ldir[None, :] * t[:, None]
        h = f(p)
        h = np.maximum(h, 1e-3)
        # improved soft shadow estimate (Inigo Quilez)
        y = h * h / (2.0 * ph)
        dd = np.sqrt(np.maximum(h * h - y * y, 0))
        res = np.minimum(res, k * dd / np.maximum(t - y, 1e-3))
        ph = h
        t = t + np.clip(h, 0.15, 3.0)
        if np.all(t > tmax):
            break
    return np.clip(res, 0.25, 1)


# --------------------------------------------------------------- rendering
DEFAULT_LIGHT = {
    "key_dir": (-0.55, 0.45, 0.70), "key": (1.05, 1.0, 0.94),
    "fill_dir": (-0.4, -0.85, 0.15), "fill": (0.28, 0.30, 0.34),
    "rim_dir": (0.7, 0.2, 0.5), "rim": (0.35, 0.38, 0.42),
    "ambient": (0.30, 0.31, 0.33), "view_dir": (1.0, 0.0, 0.0), "shadow_k": 6.0,
}


class VoxelSDF:
    """Coarse trilinear sample of the scene SDF used to accelerate marching, AO and shadows.
    Exact evaluation is still used near surfaces, for normals and for materials."""

    def __init__(self, rig, lo, hi, voxel=1.25, pad=6.0):
        self.lo = (np.asarray(lo, F32) - pad).astype(F32)
        self.v = float(voxel)
        size = (np.asarray(hi, F32) + pad - self.lo) / self.v
        self.n = np.maximum(np.ceil(size).astype(int) + 1, 2)
        gx = self.lo[0] + np.arange(self.n[0]) * self.v
        gy = self.lo[1] + np.arange(self.n[1]) * self.v
        gz = self.lo[2] + np.arange(self.n[2]) * self.v
        X, Y, Z = np.meshgrid(gx, gy, gz, indexing="ij")
        pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).astype(F32)
        vals = np.empty(pts.shape[0], F32)
        for i in range(0, pts.shape[0], 150000):
            vals[i:i + 150000] = rig.sdf(pts[i:i + 150000])
        self.grid = vals.reshape(self.n)

    def __call__(self, p):
        from grid_sample import linear_sample
        c = (p - self.lo[None, :]) / self.v
        d = linear_sample(self.grid, c)
        # outside the padded box the field is at least the distance to the box
        out = np.maximum(np.maximum(-c, c - (self.n[None, :] - 1)), 0) * self.v
        return (d + np.linalg.norm(out, axis=-1)).astype(F32)


def render(rig: Rig, pose, yaw_deg, ppu=6.0, stretch=1.2, ss=2, light=None, floor_snap=True,
           max_steps=110, canvas=None, exposure=1.0, gamma=2.2, extra_off=(0, 0, 0), accel=True, voxel=1.25, lower_clip=-0.5):
    """Orthographic sprite render of the posed rig rotated by yaw about Z.
    Returns (rgba uint8 HxWx4, offset_x, offset_y) with Doom grAb semantics:
    offset_x = pixels from left edge to the origin column, offset_y = pixels from top to the floor line."""
    light = dict(DEFAULT_LIGHT if light is None else light)
    M = rot_z(yaw_deg)
    off = np.asarray(extra_off, F32)
    if floor_snap:
        dz = rig.snap_to_floor(pose, M, off)
        off = off + np.array([0, 0, dz], F32)
    rig.place(pose, M, off)
    lo, hi = rig.bbox(1.5)
    vox = VoxelSDF(rig, lo, hi, voxel) if accel else None
    # screen: x_s = -y_world, y_s(up) = z_world ; camera looks along +X from far -X
    sx0, sx1 = -hi[1], -lo[1]
    sz0, sz1 = max(lo[2], lower_clip), hi[2]
    W = int(math.ceil((sx1 - sx0) * ppu)); H = int(math.ceil((sz1 - sz0) * ppu / stretch))
    if canvas is not None:
        W, H = canvas
        # centre horizontally on origin column, keep floor at bottom
        sx0 = -W / (2 * ppu); sx1 = W / (2 * ppu); sz0 = -0.5; sz1 = sz0 + H * stretch / ppu
    Wr, Hr = W * ss, H * ss
    # rays
    xs = sx0 + (np.arange(Wr) + 0.5) * (sx1 - sx0) / Wr
    zs = sz1 - (np.arange(Hr) + 0.5) * (sz1 - sz0) / Hr
    X, Z = np.meshgrid(xs, zs)
    oy = -X.ravel().astype(F32); oz = Z.ravel().astype(F32)
    N = oy.size
    ox = np.full(N, lo[0] - 2.0, F32)
    origin = np.stack([ox, oy, oz], 1)
    d_dir = np.array([1, 0, 0], F32)
    # cull rays outside the yz bbox
    active = (oy >= lo[1]) & (oy <= hi[1]) & (oz >= lo[2]) & (oz <= hi[2])
    t = np.zeros(N, F32); hitmask = np.zeros(N, bool)
    idx = np.nonzero(active)[0]
    tmax = hi[0] - lo[0] + 4.0
    eps_hit = 0.004 * max(1.0, 6.0 / ppu)
    near = 2.2 * (vox.v if vox else 0.0)
    for _ in range(max_steps):
        if idx.size == 0:
            break
        p = origin[idx] + d_dir[None, :] * t[idx][:, None]
        if vox is not None:
            dg = vox(p)
            far = dg > near
            d = np.empty(idx.size, F32)
            d[far] = dg[far] * 0.8
            if (~far).any():
                d[~far] = rig.sdf(p[~far])
            hit = (~far) & (d < eps_hit)
            hitmask[idx[hit]] = True
            t[idx] += np.where(far, d, np.maximum(d, 0.002) * 0.95)
        else:
            d = rig.sdf(p)
            hit = d < eps_hit
            hitmask[idx[hit]] = True
            t[idx] += np.maximum(d, 0.002) * 0.95
        alive = ~hit & (t[idx] < tmax)
        idx = idx[alive]
    rgba = np.zeros((N, 4), F32)
    hidx = np.nonzero(hitmask)[0]
    if hidx.size:
        hp = origin[hidx] + d_dir[None, :] * t[hidx][:, None]
        _, mat = rig.sdf(hp, want_material=True)
        n = normals(rig, hp, eps=0.04)
        col, n2 = shade(vox if vox is not None else rig, hp, n, mat, rig.materials, light)
        col = col * exposure
        # filmic-ish tone map then gamma
        col = col / (1 + col * 0.15)
        col = np.clip(col, 0, 1) ** (1 / gamma)
        rgba[hidx, :3] = col; rgba[hidx, 3] = 1.0
    img = rgba.reshape(Hr, Wr, 4)
    if ss > 1:
        # premultiplied area average for clean edges
        img[..., :3] *= img[..., 3:4]
        img = img.reshape(H, ss, W, ss, 4).mean(axis=(1, 3))
        a = img[..., 3:4]
        img[..., :3] = np.where(a > 1e-4, img[..., :3] / np.maximum(a, 1e-4), 0)
    out = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    offset_x = int(round((0 - sx0) * ppu))          # origin column (x_s = 0)
    offset_y = int(round((sz1 - 0.0) * ppu / stretch))  # floor line from top
    return out, offset_x, offset_y


# ------------------------------------------------------------ PNG + grAb
def save_sprite(rgba, path, offset_x, offset_y):
    """Write a PNG with a Doom grAb chunk (sprite offsets)."""
    im = Image.fromarray(rgba, "RGBA")
    from io import BytesIO
    buf = BytesIO(); im.save(buf, "PNG", optimize=False); data = buf.getvalue()
    # insert grAb after IHDR
    ihdr_end = 8 + 4 + 4 + 13 + 4
    chunk_data = struct.pack(">ii", int(offset_x), int(offset_y))
    chunk = struct.pack(">I", 8) + b"grAb" + chunk_data + struct.pack(">I", zlib.crc32(b"grAb" + chunk_data) & 0xffffffff)
    Path(path).write_bytes(data[:ihdr_end] + chunk + data[ihdr_end:])


def review_sheet(images, labels, cols, cell=None, bg=(88, 88, 90), title=None, path=None, floor_line=True):
    from PIL import ImageDraw, ImageFont
    ims = [Image.fromarray(i, "RGBA") if isinstance(i, np.ndarray) else i for i in images]
    cw = cell[0] if cell else max(i.width for i in ims) + 24
    ch = cell[1] if cell else max(i.height for i in ims) + 40
    rows = int(math.ceil(len(ims) / cols))
    y0 = 36 if title else 0
    sheet = Image.new("RGB", (cols * cw, rows * ch + y0), bg)
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 13); tfont = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default(); tfont = font
    if title:
        d.text((8, 8), title, fill=(235, 235, 235), font=tfont)
    for k, (im, lab) in enumerate(zip(ims, labels)):
        cx, cy = (k % cols) * cw, y0 + (k // cols) * ch
        scale = min((cw - 16) / im.width, (ch - 30) / im.height, 1.0)
        if scale < 1:
            im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
        px = cx + (cw - im.width) // 2; py = cy + (ch - 30 - im.height)
        if floor_line:
            d.line([(cx + 4, py + im.height), (cx + cw - 4, py + im.height)], fill=(60, 60, 62), width=1)
        sheet.paste(im, (px, py), im)
        d.text((cx + 6, cy + ch - 22), lab, fill=(235, 235, 235), font=font)
    if path:
        sheet.save(path)
    return sheet
