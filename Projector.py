import numpy as np
from Plane import Plane
from Volume import Volume

epsilon = 0.001
class Projector:
    @staticmethod
    def projection(volume: Volume, plane: Plane):

        d_ab = int(round(plane.d_ab))
        d_bc = int(round(plane.d_bc))

        if d_ab <= 0 or d_bc <= 0:
            return np.zeros((max(1, d_ab), max(1, d_bc)), dtype=np.float64)

        E_matrix = np.zeros((d_ab, d_bc), dtype=np.float64)

        y_indices = np.arange(d_ab, dtype=np.float64)[:, np.newaxis]

        a1_grid = plane.pt_a1 + (y_indices + 1) * plane.vec_ab
        a2_grid = plane.pt_a2 + (y_indices + 1) * plane.vec_ac

        grid_vec = a2_grid - a1_grid
        d12_len = np.linalg.norm(grid_vec, axis=1)

        d12_safe = np.where(d12_len < epsilon**3, 1.0, d12_len)
        d12_normalized = grid_vec / d12_safe[:, np.newaxis]

        for y in range(d_ab):
            d12 = d12_len[y]
            steps = int(round(d12))
            if steps < 0:
                continue

            steps_list = np.arange(steps + 1, dtype=np.float64)
            d12_vox_line = a1_grid[y] + steps_list[:, np.newaxis] * d12_normalized[y]

            coords = np.round(d12_vox_line).astype(np.int32)
            pt_x, pt_y, pt_z = coords[:, 0], coords[:, 1], coords[:, 2]

            valid = (
                    (pt_x >= 0) & (pt_x < volume.sx) &
                    (pt_y >= 0) & (pt_y < volume.sy) &
                    (pt_z >= 0) & (pt_z < volume.sz)
            )

            if not np.any(valid):
                continue

            v_vals = volume.data[pt_x[valid], pt_y[valid], pt_z[valid]]

            center_pos = np.round((d_bc / 2.0) - (d12 / 2.0) + steps_list[valid]).astype(np.int32)

            valid_e = (center_pos >= 0) & (center_pos < d_bc)
            E_matrix[y, center_pos[valid_e]] = v_vals[valid_e]

        return E_matrix