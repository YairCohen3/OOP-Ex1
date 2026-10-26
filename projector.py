import numpy as np
from plane import Plane
from volume import Volume

epsilon = 0.001
class Projector:
    @staticmethod
    def projection(volume: Volume, plane: Plane):

        dab = int(round(plane.d_ab))
        dbc = int(round(plane.d_bc))

        if dab <= 0 or dbc <= 0:
            return np.zeros((max(1, dab), max(1, dbc)), dtype=np.float64)

        E = np.zeros((dab, dbc), dtype=np.float64)

        y_indices = np.arange(dab, dtype=np.float64)[:, np.newaxis]

        a1_grid = plane.a1 + (y_indices + 1) * plane.v_ab
        a2_grid = plane.a2 + (y_indices + 1) * plane.v_ac

        diffs = a2_grid - a1_grid
        d12s = np.linalg.norm(diffs, axis=1)

        d12s_safe = np.where(d12s < 1e-5, 1.0, d12s)
        dp_grid = diffs / d12s_safe[:, np.newaxis]

        for y in range(dab):
            d12 = d12s[y]
            steps = int(round(d12))
            if steps < 0:
                continue

            x1 = np.arange(steps + 1, dtype=np.float64)
            p_line = a1_grid[y] + x1[:, np.newaxis] * dp_grid[y]

            coords = np.round(p_line).astype(np.int32)
            ix, iy, iz = coords[:, 0], coords[:, 1], coords[:, 2]

            valid = (
                    (ix >= 0) & (ix < volume.sx) &
                    (iy >= 0) & (iy < volume.sy) &
                    (iz >= 0) & (iz < volume.sz)
            )

            if not np.any(valid):
                continue

            v_vals = volume.data[ix[valid], iy[valid], iz[valid]]

            x_pos = np.round((dbc / 2.0) - (d12 / 2.0) + x1[valid]).astype(np.int32)

            valid_e = (x_pos >= 0) & (x_pos < dbc)
            E[y, x_pos[valid_e]] = v_vals[valid_e]

        return E