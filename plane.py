import numpy as np
epsilon = 0.001
class Plane:
    def __init__(self, points):
        pts = np.asarray(points, dtype=np.float64)
        if pts.shape == (3, 3):
            a, b, c = self.order_triangle_points(pts[0], pts[1], pts[2])
            self.validate_triangle(a, b, c)
            self.a1 = a
            self.a2 = a
            self.b = b
            self.c = c
        elif pts.shape == (4, 3):
            a1, a2, b, c = pts[0], pts[1], pts[2], pts[3]
            self.validate_trapezoid(a1, a2, b, c)
            self.a1 = a1
            self.a2 = a2
            self.b = b
            self.c = c
        else:
            raise ValueError(f"Expected 3 or 4 3D points, got shape {pts.shape}")

        self.d_ab = self.dist(self.a1, self.b)
        self.d_bc = self.dist(self.b, self.c)

        self.v_ab = self.vector(self.a1, self.b) / self.d_ab
        self.v_ac = self.vector(self.a2, self.c) / self.d_ab

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

    def validate_trapezoid(self, a1: np.ndarray, a2: np.ndarray, b: np.ndarray, c: np.ndarray):
        d_a1b = self.dist(a1, b)
        d_a2c = self.dist(a2, c)
        if abs(d_a1b - d_a2c) >= epsilon:
            raise ValueError("Trapezoid legs are not equal:")
        if d_a1b < epsilon:
            raise ValueError("Trapezoid leg distance cannot be zero")

        d_a1a2 = self.dist(a1, a2)
        d_bc = self.dist(b, c)
        if d_a1a2 > d_bc:
            raise ValueError("Top base is larger than bottom base")

        v1 = b - a1
        v2 = c - a1
        normal = np.cross(v1, v2)
        norm_len = np.linalg.norm(normal)
        if norm_len > 0:
            unit_normal = normal / norm_len
            distance_from_plane = abs(np.dot(unit_normal, a2 - a1))
            if distance_from_plane > 0:
                raise ValueError("Points are not coplanar")