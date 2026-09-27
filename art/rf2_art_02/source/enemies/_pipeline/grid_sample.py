"""Trilinear nearest-boundary sampling for the native renderer, numpy only."""
import numpy as np

def linear_sample(grid, coords):
    c = np.clip(coords, 0, np.asarray(grid.shape) - 1)
    lo = np.floor(c).astype(np.int64)
    hi = np.minimum(lo + 1, np.asarray(grid.shape) - 1)
    t = c - lo
    result = np.zeros(len(c), dtype=np.float64)
    for x in range(2):
        for y in range(2):
            for z in range(2):
                ix = hi[:, 0] if x else lo[:, 0]
                iy = hi[:, 1] if y else lo[:, 1]
                iz = hi[:, 2] if z else lo[:, 2]
                wx = t[:, 0] if x else 1-t[:, 0]
                wy = t[:, 1] if y else 1-t[:, 1]
                wz = t[:, 2] if z else 1-t[:, 2]
                result += grid[ix, iy, iz] * wx * wy * wz
    return result.astype(grid.dtype)
