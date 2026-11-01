import numpy as np
epsilon = 0.001
class Plane:
    def __init__(self, points):
        pts = np.asarray(points, dtype=np.float64)
        if not np.all(np.isfinite(pts)):
            raise ValueError("All point coordinates must be finite")
        if pts.shape == (3, 3):
            a, b, c = self.order_triangle_points(pts[0], pts[1], pts[2])
            self.validate_triangle(a, b, c)
            self.pt_a1 = a
            self.pt_a2 = a
            self.pt_b = b
            self.pt_c = c
        elif pts.shape == (4, 3):
            a1, a2, b, c = pts[0], pts[1], pts[2], pts[3]
            self.validate_trapezoid(a1, a2, b, c)
            self.pt_a1 = a1
            self.pt_a2 = a2
            self.pt_b = b
            self.pt_c = c
        else:
            raise ValueError(f"Expected 3 or 4 3D points, got shape {pts.shape}")

        self.d_ab = self.dist(self.pt_a1, self.pt_b)
        self.d_bc = self.dist(self.pt_b, self.pt_c)
        self.d_ac = self.dist(self.pt_a1, self.pt_c)

        self.vec_ab = self.vector(self.pt_a1, self.pt_b) / self.d_ab
        self.vec_ac = self.vector(self.pt_a2, self.pt_c) / self.d_ac

    @staticmethod
    def vector(p1: np.ndarray, p2: np.ndarray):
        return p2 - p1

    @staticmethod
    def dist(p1: np.ndarray, p2: np.ndarray):
        return float(np.linalg.norm(p2 - p1))

    def order_triangle_points(self, p0: np.ndarray, p1: np.ndarray, p2: np.ndarray):

        if abs(self.dist(p0, p1) - self.dist(p0, p2)) < epsilon:
            return p0, p1, p2
        if abs(self.dist(p1, p0) - self.dist(p1, p2)) < epsilon:
            return p1, p0, p2
        if abs(self.dist(p2, p0) - self.dist(p2, p1)) < epsilon:
            return p2, p0, p1
        return p0, p1, p2

    def validate_triangle(self, a: np.ndarray, b: np.ndarray, c: np.ndarray):
        d_ab = self.dist(a, b)
        d_ac = self.dist(a, c)
        if abs(d_ab - d_ac) >= epsilon:
            raise ValueError("Triangle legs are not equal")
        if d_ab < epsilon:
            raise ValueError("Triangle leg distance cannot be zero.")
        twice_area = np.linalg.norm(np.cross(b - a, c - a))
        altitude = twice_area / d_ab

        if not np.isfinite(altitude) or altitude <= epsilon:
            raise ValueError(
                "Triangle points are collinear or nearly collinear"
            )
    def validate_trapezoid(self, a1: np.ndarray, a2: np.ndarray, b: np.ndarray, c: np.ndarray):
        d_a1b = self.dist(a1, b)
        d_a2c = self.dist(a2, c)
        d_a1a2 = self.dist(a1, a2)
        d_bc = self.dist(b, c)

        if d_a1a2 > d_bc:
            raise ValueError("Top base is larger than bottom base")
        if abs(d_a1b - d_a2c) >= epsilon:
            raise ValueError("Trapezoid legs are not equal")
        if d_a1b < epsilon or d_a2c < epsilon:
            raise ValueError("Trapezoid leg distance cannot be zero")

        v1 = b - a1
        v2 = c - a1
        normal = np.cross(v1, v2)
        norm_len = np.linalg.norm(normal)
        if norm_len > 0:
            unit_normal = normal / norm_len
            distance_from_plane = abs(np.dot(unit_normal, a2 - a1))
            if distance_from_plane > epsilon:
                raise ValueError("Points are not coplanar")
            else:
                pass
        else:
            raise ValueError("Points are not coplanar")