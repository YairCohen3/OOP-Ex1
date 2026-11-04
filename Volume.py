import numpy as np
import nrrd

class Volume:
    def __init__(self, filepath: str):

        data, header = nrrd.read(filepath)
        self.data = np.asarray(data)

        if self.data.ndim != 3:
            raise ValueError("Expected 3D volumetric data")

        allowed_voxal_dtype = [np.uint8, np.uint16, np.uint32]
        if self.data.dtype not in allowed_voxal_dtype:
            raise ValueError("Matrix data can only be unsigned integer of size 8/16/32 bit")

        self.sx, self.sy, self.sz = self.data.shape

        max_dim = 2 ** 10
        if not (1 <= self.sx < max_dim and 1 <= self.sy < max_dim and 1 <= self.sz < max_dim):
            raise ValueError(f"Volume dimensions {self.data.shape} out of allowed range [1, 1024).")

    def get_voxel(self, p: np.ndarray) :

        x_val = int(round(p[0]))
        y_val = int(round(p[1]))
        z_val = int(round(p[2]))


        if 0 <= x_val < self.sx and 0 <= y_val < self.sy and 0 <= z_val < self.sz:
            return float(self.data[x_val, y_val, z_val])

        return 0.0