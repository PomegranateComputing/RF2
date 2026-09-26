"""Native FAL composition and poses recovered from the project legacy."""
import numpy as np
import rigcomp as rc
PAD_L, PAD_T, PAD_R, PAD_B = 512, 256, 384, 512
W0, H0 = 1536, 1024
def P(x, y):
    return (x + PAD_L, y + PAD_T)
def compose(L, spec):
    """spec: dict layer -> transform dict(angle, scale, tx, ty, pivot) or None to hide;
    'group' transform applies to every visible layer (rifle + hands move together)."""
    H, W = next(iter(L.values())).shape[:2]
    canvas = np.zeros((H, W, 4), np.float32)
    grp = spec.get("group", {})
    order = ["body", "mag", "housing", "knob", "arm_r", "arm_l", "arm_l2", "flash"]
    for name in order:
        t = spec.get(name, {})
        if t is None or (name not in spec and name in ("arm_l2",)):
            continue
        src = L[t.get("use", name)]
        layer = src
        if "warp" in t:
            layer = rc.warp_layer(layer, t["warp"][0], t["warp"][1])
        piv = t.get("pivot", (0, 0))
        layer = rc.transform_layer(layer, t.get("angle", 0.0), t.get("scale", 1.0), t.get("tx", 0.0), t.get("ty", 0.0), piv)
        if grp:
            layer = rc.transform_layer(layer, grp.get("angle", 0.0), grp.get("scale", 1.0), grp.get("tx", 0.0), grp.get("ty", 0.0), grp.get("pivot", (0, 0)))
        rc.over(canvas, layer)
    return canvas


EL = P(-200, 1170)      # left elbow pivot (off-screen)
WR = P(470, 560)        # left wrist
SH = P(1600, 700)       # shoulder/stock pivot for muzzle rise
HT = (0.958, 0.287)     # charging handle travel (rearward, toward the shooter)


def arm_l(angle=0.0, tx=0.0, ty=0.0, pivot=None, scale=1.0):
    return {"angle": angle, "tx": tx, "ty": ty, "pivot": pivot or EL, "scale": scale}


def mag_t(tx=0.0, ty=0.0, angle=0.0, pivot=None, use="mag"):
    return {"tx": tx, "ty": ty, "angle": angle, "pivot": pivot or P(730, 700), "use": use}


def frame_specs():
    """Complete family. Each entry: (state, spec, duration_tics, event)."""
    F = []
    def add(state, spec, tics, event=""):
        F.append((state, spec, tics, event))
    ready = {"body": {}, "mag": mag_t(), "housing": {}, "knob": {}, "arm_r": {}, "arm_l": arm_l(), "flash": None}
    add("FAL_READY", ready, 1, "idle loop; A_WeaponReady")
    # fire cycle: whole assembly kicks back and up (stock pivot), flash forward of the muzzle
    add("FAL_FIRE", {**ready, "flash": {}, "group": {"tx": 6, "ty": 14, "angle": -0.8, "pivot": SH}}, 2, "rf2s1/fal/shot_01; A_GunFlash; case ejection particle")
    add("FAL_RECOIL_MAX", {**ready, "group": {"tx": 14, "ty": 36, "angle": -2.2, "pivot": SH}}, 2, "peak recoil; A_WeaponOffset optional on top")
    add("FAL_RECOVERY", {**ready, "group": {"tx": 5, "ty": 12, "angle": -0.6, "pivot": SH}}, 2, "return to READY")
    # reload: support hand leaves the handguard, comes down and closes round the magazine (vertical grasp
    # pose), rocks it forward out of the well, carries it down, returns with a fresh one, seats it,
    # then reaches up to the charging handle (empty reload) and returns to the handguard.
    MP = P(676, 500)   # magazine front-top corner: the rocking pivot (front lug)
    def carry(tx, ty, ang, fresh=False):
        m = mag_t(tx, ty, ang, MP, use="mag_fresh" if fresh else "mag")
        return {"mag": m, "arm_l": None, "arm_l2": {"tx": tx, "ty": ty, "angle": ang, "pivot": MP}}
    add("FAL_RELOAD_01_HAND_LEAVES_FOREND", {**ready, "arm_l": arm_l(4.0, 8, 4)}, 4, "rf2s1/fal/cloth")
    add("FAL_RELOAD_02_REACH_MAG", {**ready, "arm_l": arm_l(12.0, 30, 30)}, 4, "hand opens toward the magazine")
    add("FAL_RELOAD_03_GRAB_MAG", {**ready, **carry(0, 0, 0)}, 3, "hand closes on the magazine body")
    add("FAL_RELOAD_04_MAG_RELEASE", {**ready, **carry(0, 5, 2.5)}, 3, "rf2s1/fal/latch; catch pressed, rear of magazine drops")
    add("FAL_RELOAD_05_MAG_ROTATE_OUT", {**ready, **carry(-6, 40, 14.0)}, 3, "rf2s1/fal/mag_out; magazine rocks forward, out of the well")
    add("FAL_RELOAD_06_MAG_CLEAR", {**ready, **carry(-70, 250, 26.0)}, 4, "magazine clear of the rifle, carried down and away")
    add("FAL_RELOAD_07_NEW_MAG_ENTER", {**ready, **carry(-40, 190, 18.0, fresh=True)}, 4, "fresh magazine rises from below the frame, brass visible at the lips")
    add("FAL_RELOAD_08_NEW_MAG_ALIGN", {**ready, **carry(-8, 58, 12.0, fresh=True)}, 3, "front lug presented to the well, magazine tilted")
    add("FAL_RELOAD_09_MAG_INSERT", {**ready, **carry(-2, 14, 5.0, fresh=True)}, 3, "rf2s1/fal/mag_in; lug in, magazine rocking rearward")
    add("FAL_RELOAD_10_MAG_LOCK", {**ready, **carry(0, -2, 0.0)}, 3, "rf2s1/fal/seat; catch clicks (ammunition commit point)")
    add("FAL_RELOAD_11_HAND_TRANSITION", {**ready, "arm_l": arm_l(9.0, 30, -60)}, 3, "hand releases magazine, rises along the receiver")
    add("FAL_RELOAD_12_CHARGE_START", {**ready, "arm_l": arm_l(4.5, 96, -84)}, 3, "fingers close on the charging handle")
    add("FAL_RELOAD_13_CHARGE_REAR", {**ready, "arm_l": arm_l(4.5, 96 + HT[0] * 118, -84 + HT[1] * 118), "knob": {"tx": HT[0] * 118, "ty": HT[1] * 118}}, 3, "rf2s1/fal/action; handle at the rear of its travel, bolt back")
    add("FAL_RELOAD_14_CHARGE_RELEASE", {**ready, "arm_l": arm_l(4.5, 96 + HT[0] * 30, -84 + HT[1] * 30), "knob": {"tx": HT[0] * 12, "ty": HT[1] * 12}}, 2, "handle released, bolt slams home")
    add("FAL_RELOAD_15_HAND_RETURN", {**ready, "arm_l": arm_l(2.0, 30, -10)}, 3, "rf2s1/fal/cloth; support hand comes back to the handguard")
    add("FAL_RELOAD_16_READY", ready, 1, "READY (same drawing as FAL_READY)")
    return F


