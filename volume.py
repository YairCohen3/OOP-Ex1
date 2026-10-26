import numpy as np
import nrrd

class Volume:
    def __init__(self, filepath: str):

        data, header = nrrd.read(filepath)
        self.data = np.asarray(data)

        if self.data.ndim != 3:
            raise ValueError("Expected 3D volumetric data")

        self.sx, self.sy, self.sz = self.data.shape

        max_dim = 2 ** 10
        if not (1 <= self.sx < max_dim and 1 <= self.sy < max_dim and 1 <= self.sz < max_dim):
            raise ValueError(f"Volume dimensions {self.data.shape} out of allowed range [1, 1024).")

    def get_voxel(self, p: np.ndarray) :

        ix = int(round(p[0]))
        iy = int(round(p[1]))
        iz = int(round(p[2]))


        if 0 <= ix < self.sx and 0 <= iy < self.sy and 0 <= iz < self.sz:
            return float(self.data[ix, iy, iz])

        return 0.0