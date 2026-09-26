"""Project native premultiplied-alpha compositor (Pillow/numpy only)."""
import math
import numpy as np
from PIL import Image
def load_rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0


def save_rgba(arr, path):
    a = np.clip(arr, 0, 1)
    Image.fromarray((a * 255 + 0.5).astype(np.uint8), "RGBA").save(path, optimize=False)


def premul(rgba):
    out = rgba.copy()
    out[..., :3] *= out[..., 3:4]
    return out


def unpremul(p):
    out = p.copy()
    a = np.maximum(out[..., 3:4], 1e-6)
    out[..., :3] = np.where(out[..., 3:4] > 1e-6, out[..., :3] / a, 0)
    out[..., 3] = np.clip(out[..., 3], 0, 1)
    out[..., :3] = np.clip(out[..., :3], 0, 1)
    return out


def over(dst_p, src_p):
    """Premultiplied over-compositing, in place on dst."""
    a = src_p[..., 3:4]
    dst_p *= (1 - a)
    dst_p += src_p
    return dst_p


def pad_canvas(rgba, pad_l, pad_t, pad_r, pad_b):
    h, w = rgba.shape[:2]
    out = np.zeros((h + pad_t + pad_b, w + pad_l + pad_r, 4), np.float32)
    out[pad_t:pad_t + h, pad_l:pad_l + w] = rgba
    return out


def affine_params(angle_deg, scale, tx, ty, pivot):
    """PIL affine data (output->input) for: rotate & scale about pivot, then translate."""
    th = math.radians(angle_deg)
    c, s = math.cos(th), math.sin(th)
    px, py = pivot
    a = c / scale
    b = s / scale
    d = -s / scale
    e = c / scale
    ox, oy = px + tx, py + ty
    cx = px - (a * ox + b * oy)
    cy = py - (d * ox + e * oy)
    return (a, b, cx, d, e, cy)


def transform_layer(layer_p, angle=0.0, scale=1.0, tx=0.0, ty=0.0, pivot=(0, 0)):
    """Transform a premultiplied RGBA float layer. Returns a new premultiplied array."""
    if angle == 0 and scale == 1 and tx == 0 and ty == 0:
        return layer_p.copy()
    h, w = layer_p.shape[:2]
    out = np.zeros_like(layer_p)
    if abs(angle) < 1e-9 and abs(scale - 1) < 1e-9 and float(tx).is_integer() and float(ty).is_integer():
        itx, ity = int(tx), int(ty)
        src = layer_p[max(0, -ity):h - max(0, ity), max(0, -itx):w - max(0, itx)]
        out[max(0, ity):max(0, ity) + src.shape[0], max(0, itx):max(0, itx) + src.shape[1]] = src
        return out
    data = affine_params(angle, scale, tx, ty, pivot)
    for ch in range(4):
        im = Image.fromarray(np.ascontiguousarray(layer_p[..., ch]), mode="F")
        im = im.transform((w, h), Image.AFFINE, data, resample=Image.BICUBIC)
        out[..., ch] = np.asarray(im, dtype=np.float32)
    out[..., 3] = np.clip(out[..., 3], 0, 1)
    out[..., :3] = np.clip(out[..., :3], 0, out[..., 3:4])
    return out


