import numpy as np
from Plane import Plane
from Volume import Volume

epsilon = 0.001

class Projector:
    @staticmethod
    def projection(volume: Volume, plane: Plane):

        if plane is None:
            return np.zeros((1, 1), dtype=np.float64)

        if not np.isfinite(plane.d_ab) or not np.isfinite(plane.d_bc):
            raise ValueError("Plane dimensions must be finite")

        d_ab = int(round(plane.d_ab))
        d_bc = int(round(plane.d_bc))

        if d_ab <= 0 or d_bc <= 0:
            return np.zeros(
                (max(1, d_ab), max(1, d_bc)),
                dtype=np.float64,
            )

        E_matrix = np.zeros((d_ab, d_bc), dtype=np.float64)

        y_indices = np.arange(d_ab, dtype=np.float64)[:, np.newaxis]

        with np.errstate(over="ignore", invalid="ignore"):
            a1_grid = plane.pt_a1 + (y_indices + 1) * plane.vec_ab
            a2_grid = plane.pt_a2 + (y_indices + 1) * plane.vec_ac

            grid_vec = a2_grid - a1_grid
            d12_len = np.linalg.norm(grid_vec, axis=1)

        if not np.all(np.isfinite(d12_len)):
            raise ValueError("Plane row lengths must be finite")

        d12_safe = np.where(d12_len < epsilon, 1.0, d12_len)
        d12_normalized = grid_vec / d12_safe[:, np.newaxis]

        steps_per_row = np.rint(d12_len).astype(np.intp)
        max_steps = int(steps_per_row.max(initial=0))
        step_values = np.arange(max_steps + 1, dtype=np.float64)[np.newaxis, :]

        sample_mask = step_values <= steps_per_row[:, np.newaxis]

        with np.errstate(over="ignore", invalid="ignore"):
            points = (
                a1_grid[:, np.newaxis, :]
                + step_values[:, :, np.newaxis]
                * d12_normalized[:, np.newaxis, :]
            )
            rounded_points = np.rint(points)

        valid_samples = (
            sample_mask
            & np.all(np.isfinite(rounded_points), axis=2)
            & (rounded_points[:, :, 0] >= 0)
            & (rounded_points[:, :, 0] < volume.sx)
            & (rounded_points[:, :, 1] >= 0)
            & (rounded_points[:, :, 1] < volume.sy)
            & (rounded_points[:, :, 2] >= 0)
            & (rounded_points[:, :, 2] < volume.sz)
        )

        voxel_indices = np.zeros(rounded_points.shape, dtype=np.intp)
        voxel_indices[valid_samples] = rounded_points[valid_samples].astype(
            np.intp
        )

        with np.errstate(over="ignore", invalid="ignore"):
            rounded_columns = np.rint(
                (d_bc / 2.0)
                - (d12_len[:, np.newaxis] / 2.0)
                + step_values
            )

        valid_output = (
            valid_samples
            & np.isfinite(rounded_columns)
            & (rounded_columns >= 0)
            & (rounded_columns < d_bc)
        )

        column_indices = np.zeros(rounded_columns.shape, dtype=np.intp)
        column_indices[valid_output] = rounded_columns[valid_output].astype(
            np.intp
        )

        last_write_mask = valid_output.copy()
        duplicate_next = (
            valid_output[:, :-1]
            & valid_output[:, 1:]
            & (column_indices[:, :-1] == column_indices[:, 1:])
        )
        last_write_mask[:, :-1] &= ~duplicate_next

        row_indices = np.broadcast_to(
            np.arange(d_ab, dtype=np.intp)[:, np.newaxis],
            valid_output.shape,
        )

        if np.any(last_write_mask):
            E_matrix[
                row_indices[last_write_mask],
                column_indices[last_write_mask],
            ] = volume.data[
                voxel_indices[:, :, 0][last_write_mask],
                voxel_indices[:, :, 1][last_write_mask],
                voxel_indices[:, :, 2][last_write_mask],
            ]

        return E_matrix